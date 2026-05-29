"""Orchestration for the execution phase — tool call, governance gate, result normalization."""

from core_kernel.contracts.tool_gateway_contracts import ToolResultStatus
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.tool_objects import ToolRequest
from core_kernel.runtime.seed_turn_record import _RunContext


def autonomy_level_allows_tool_execution(ctx: _RunContext) -> bool:
    autonomy = getattr(ctx, "autonomy_level", "A1_GUIDED")
    if autonomy == "A0_OBSERVE_ONLY":
        return False
    return True


def classify_side_effect_type(tool_name: str) -> str:
    return "read_only"


def prepare_tool_arguments(tool_name: str, arguments: dict, ctx: _RunContext) -> dict:
    if tool_name == "seed.emit_answer":
        arguments.setdefault("run_id", ctx.run_id)
    return arguments


def infer_target_resource(tool_name: str, arguments: dict) -> str:
    return str(arguments.get("path", arguments.get("filename", "")))


def build_tool_request(
    ctx: _RunContext,
    inp: KernelInput,
    tool_name: str,
    arguments: dict,
    policy_decision_id: str,
    record_id: str,
) -> ToolRequest:
    decision = ctx.planner_decision
    return ToolRequest(
        run_id=ctx.run_id,
        profile_id=inp.profile_id,
        policy_id=ctx.policy_id,
        decision_id=getattr(decision, "task_id", ""),
        governance_decision_id=policy_decision_id,
        planner_decision_id=getattr(decision, "task_id", ""),
        tool_name=tool_name,
        arguments=arguments,
        risk_level=getattr(ctx.governance_decision, "risk_level", "none"),
        requires_approval=getattr(ctx.governance_decision, "requires_approval", False),
        source_phase="tool_requested",
        capability_id=getattr(decision, "action_type", ""),
        target_resource=infer_target_resource(tool_name, arguments),
        side_effect_type=classify_side_effect_type(tool_name),
        trace_id=ctx.trace_id if ctx.trace_id else "",
        record_id=record_id,
        metadata={
            "planner_reasoning": getattr(decision, "reasoning", ""),
            "source_event_id": f"event-tool-requested-{ctx.run_id}",
        },
    )


def normalize_tool_result(ctx: _RunContext, tool_result, emit) -> str:
    status = tool_result.status
    if status in (ToolResultStatus.BLOCKED.value, "blocked"):
        reason = tool_result.blocked_reason or SeedFailureReason.TOOL_BLOCKED.value
        ctx.blocked_actions.append(reason)
        emit("tool_blocked", tool=tool_result.tool_name, reason=reason)
        return f"blocked:{reason}"
    if status in (ToolResultStatus.FAILED.value, "failed"):
        ctx.tool_error = True
        error = tool_result.error or SeedFailureReason.TOOL_FAILED.value
        emit("tool_failed", tool=tool_result.tool_name, error=error)
        return f"failed:{error}"
    if status == ToolResultStatus.INVALID_REQUEST.value:
        reason = tool_result.error or "invalid_request"
        ctx.blocked_actions.append(reason)
        emit("tool_blocked", tool=tool_result.tool_name, reason=reason)
        return f"blocked:{reason}"
    if status == ToolResultStatus.PENDING_APPROVAL.value:
        ctx.pending_approvals.append(SeedFailureReason.APPROVAL_REQUIRED.value)
        emit("tool_pending_approval", tool=tool_result.tool_name)
        return SeedFailureReason.APPROVAL_REQUIRED.value
    emit("tool_succeeded", tool=tool_result.tool_name)
    return str(tool_result.output or "")


def run_tool_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input:
        return ctx
    if not autonomy_level_allows_tool_execution(ctx):
        ctx.blocked_actions.append(SeedFailureReason.GOVERNANCE_DENIED.value)
        ctx.tool_output = SeedFailureReason.GOVERNANCE_DENIED.value
        emit("tool_blocked", reason="A0_OBSERVE_ONLY autonomy level forbids tool execution")
        return ctx
    decision = ctx.planner_decision
    governance_decision = ctx.governance_decision

    if decision is None and ctx.planner_error:
        ctx.tool_output = SeedFailureReason.PLANNER_ERROR.value
        return ctx
    if decision is None:
        ctx.tool_output = SeedFailureReason.NO_DECISION.value
        return ctx

    allowed = getattr(governance_decision, "allowed", False)
    requires_approval = getattr(governance_decision, "requires_approval", False)
    tool_name = getattr(decision, "tool_name", None) or getattr(decision, "action", None) or ""

    if requires_approval:
        ctx.pending_approvals.append(SeedFailureReason.APPROVAL_REQUIRED.value)
        ctx.tool_output = SeedFailureReason.APPROVAL_REQUIRED.value
        emit("governance_pending_approval", reason="requires_approval")
        emit("tool_requested", tool=tool_name)
        emit("tool_pending_approval", tool=tool_name, reason="requires_approval")
        return ctx
    if not allowed:
        ctx.blocked_actions.append(
            getattr(governance_decision, "reason", SeedFailureReason.GOVERNANCE_DENIED.value)
        )
        ctx.tool_output = SeedFailureReason.GOVERNANCE_DENIED.value
        emit("governance_denied", reason=getattr(governance_decision, "reason", "denied"))
        emit("tool_requested", tool=tool_name)
        emit("tool_blocked", tool=tool_name, reason=getattr(governance_decision, "reason", "denied"))
        return ctx

    tool_gateway = ports["tool_gateway_port"]
    if not tool_name:
        ctx.planner_error = True
        ctx.planner_error_type = "missing_tool_name"
        ctx.planner_error_message = "Planner decision missing tool_name"
        ctx.tool_output = SeedFailureReason.PLANNER_ERROR.value
        return ctx

    arguments = dict(getattr(decision, "arguments", {}) or getattr(decision, "parameters", {}))
    arguments = prepare_tool_arguments(tool_name, arguments, ctx)
    policy_decision_id = getattr(governance_decision, "decision_id", "")

    ctx.tool_call_index += 1
    record_id = f"event-tool-requested-{ctx.run_id}-{ctx.tool_call_index}"

    emit("tool_requested", tool=tool_name)

    tool_request = build_tool_request(ctx, inp, tool_name, arguments, policy_decision_id, record_id)

    ctx.tool_request_id = tool_request.record_id
    emit("tool_gateway_called", tool=tool_name, request_id=tool_request.record_id)

    try:
        tool_result = tool_gateway.execute_typed(tool_request)
    except Exception as exc:
        ctx.gateway_error = True
        ctx.gateway_error_type = type(exc).__name__
        ctx.gateway_error_message = str(exc)
        ctx.tool_output = SeedFailureReason.GATEWAY_ERROR.value
        emit("gateway_failed", error=str(exc))
        return ctx

    if tool_result.trace_id and not ctx.trace_id:
        ctx.trace_id = tool_result.trace_id

    ctx.tool_output = normalize_tool_result(ctx, tool_result, emit)
    return ctx
