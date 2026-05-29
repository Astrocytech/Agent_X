"""Decision phases — planning, governance check, approval continuation."""

from core_kernel.memory.memory_recall_result import MemoryRecallResult
from core_kernel.models.planner_decision import PlannerContext
from core_kernel.models.kernel_io import KernelInput
from core_kernel.models.enums.seed_failure_reason import SeedFailureReason
from core_kernel.runtime.seed_turn_record import _RunContext


def run_planning_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input or ctx.profile_error:
        return ctx
    planner_port = ports["planner_port"]
    try:
        memory_recall = MemoryRecallResult(
            status=ctx.memory_recall_status,
            error_type=ctx.memory_recall_error_type,
            record_count=len(ctx.recalled_memory_refs),
            degraded=ctx.memory_error,
            evidence_refs=list(ctx.recalled_memory_refs),
            recalled_items=list(ctx.recalled_memory_items),
        )
        planner_ctx = PlannerContext(
            run_id=ctx.run_id,
            profile_id=inp.profile_id,
            past_lessons=list(ctx.recalled_memory_items),
            memory_recall=memory_recall,
            goal_text=inp.user_goal,
            policy_id=ctx.policy_id,
            task_type=getattr(ctx.task, "task_type", "") if ctx.task else "",
            trace_id=ctx.trace_id,
            evidence_refs=list(ctx.recalled_memory_refs),
        )
        _ = planner_ctx
        planner_ctx_dict = {
            "run_id": ctx.run_id,
            "profile_id": inp.profile_id,
            "past_lessons": list(ctx.recalled_memory_items),
            "goal_text": inp.user_goal,
            "policy_id": ctx.policy_id,
            "trace_id": ctx.trace_id,
        }
        decision = planner_port.make_decision(
            ctx.goal,
            ctx.profile,
            planner_ctx_dict,
        )
        ctx.planner_decision = decision
        emit("planner_decision_made", tool_name=getattr(decision, "tool_name", ""))
        if ctx.memory_error:
            emit(
                "degraded_operation", component="memory_recall", error=ctx.memory_recall_error_type
            )
    except Exception as exc:
        ctx.planner_error = True
        ctx.planner_error_type = type(exc).__name__
        ctx.planner_error_message = str(exc)
        ctx.planner_decision = None
        emit("planner_failed", error=str(exc))
    return ctx


def run_governance_phase(ctx: _RunContext, inp: KernelInput, emit, ports) -> _RunContext:
    if ctx.invalid_input or ctx.profile_error:
        return ctx
    if ctx.planner_decision is None:
        return ctx
    try:
        governance_port = ports["governance_port"]
        decision = ctx.planner_decision
        tool_name = (getattr(decision, "tool_name", None) or getattr(decision, "action", None)) or ""
        arguments = getattr(decision, "arguments", {}) or getattr(decision, "parameters", {})

        gov_action = {
            "tool_name": tool_name,
            "arguments": arguments,
            "profile_id": inp.profile_id,
            "policy_id": ctx.policy_id,
            "run_id": ctx.run_id,
        }
        gov_ctx_dict = {
            "run_id": ctx.run_id,
            "profile_id": inp.profile_id,
            "policy_id": ctx.policy_id,
        }
        gov_decision = governance_port.decide(ctx.profile, gov_action, gov_ctx_dict)
        ctx.governance_decision = gov_decision
        emit(
            "governance_checked",
            allowed=getattr(gov_decision, "allowed", False),
            decision_id=getattr(gov_decision, "decision_id", ""),
            tool_name=tool_name,
        )
    except Exception as exc:
        ctx.governance_error = True
        ctx.governance_error_type = type(exc).__name__
        ctx.governance_error_message = str(exc)
        emit("governance_failed", error=str(exc))
    return ctx


def run_approval_continuation_phase(
    ctx: _RunContext, inp: KernelInput, emit, ports
) -> _RunContext:
    if not ctx.pending_approvals:
        emit("approval_continuation_resolved", skipped="no_pending_approvals")
        return ctx

    continuation = ports.get("continuation_input")
    if continuation is None:
        emit("approval_continuation_resolved", skipped="no_continuation_input")
        return ctx

    decision = getattr(continuation, "approval_decision", "")
    approval_id = getattr(continuation, "approval_id", "")

    if decision == "approved":
        ctx.pending_approvals.clear()
        ctx.approval_continuation_id = approval_id
        ctx.approval_continuation_resolved = True
        emit(
            "approval_continuation_resolved",
            approval_id=approval_id,
            decision="approved",
        )
    elif decision == "denied":
        ctx.pending_approvals.clear()
        ctx.blocked_actions.append(SeedFailureReason.APPROVAL_DENIED.value)
        ctx.tool_output = SeedFailureReason.APPROVAL_DENIED.value
        ctx.approval_continuation_denied = True
        emit(
            "approval_continuation_failed",
            approval_id=approval_id,
            decision="denied",
        )
    else:
        emit(
            "approval_continuation_resolved",
            skipped="unrecognized_decision",
            decision=decision,
        )
    return ctx
