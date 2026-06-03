from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    ExecutionStep,
    TaskPlan,
    ToolInvocationBinding,
    ModelInvocationBinding,
    ApprovalGateRecord,
    utc_now_iso,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    STEP_STATUS_PENDING,
    STEP_STATUS_READY,
    STEP_STATUS_RUNNING,
    STEP_STATUS_BLOCKED,
    STEP_STATUS_FAILED,
    STEP_STATUS_SKIPPED,
    STEP_STATUS_COMPLETED,
    STEP_STATUS_NEEDS_APPROVAL,
    STEP_STATUS_NEEDS_GOVERNANCE,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
    GATE_STATUS_NOT_REQUIRED,
    DECISION_CONTINUE,
    DECISION_BLOCK,
    DECISION_RETRY,
    DECISION_ABORT,
    DECISION_REQUIRE_APPROVAL,
    DECISION_REQUIRE_GOVERNANCE,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_GATE_BLOCKED,
    ORCH_TOOL_BINDING_INVALID,
    ORCH_MODEL_BINDING_INVALID,
    ORCH_POLICY_DENIED,
    ORCH_HUMAN_APPROVAL_MISSING,
    ORCH_FAILURE_UNCLASSIFIED,
)
from agentx_evolve.orchestrator.tool_invoker import invoke_tool_for_step
from agentx_evolve.orchestrator.model_invoker import invoke_model_for_step
from agentx_evolve.orchestrator.approval_gate import (
    check_approval_required,
    check_governance_required,
    create_approval_gate_record,
    resolve_approval_gate,
)


def _check_authority(step: ExecutionStep, binding_context: dict) -> str | None:
    policy_fn = binding_context.get("policy_registry", {}).get("adapter")
    if policy_fn:
        try:
            result = policy_fn(step_id=step.step_id, role=step.assigned_role)
            if result.get("decision") == "BLOCK":
                return result.get("reason", "Policy denied")
        except Exception:
            return "Policy check failed"
    return None


def pre_execution_authority_recheck(
    step: ExecutionStep,
    binding_context: dict,
    session: object | None = None,
) -> str | None:
    authority_error = _check_authority(step, binding_context)
    if authority_error:
        return authority_error

    if session is not None:
        snap_id = getattr(session, "source_snapshot_id", "")
        snap_hash = getattr(session, "source_snapshot_hash", "")
        if snap_id and not snap_hash:
            return "Source snapshot present but hash is empty — TOCTOU risk"

    return None


def execute_step(
    step: ExecutionStep,
    plan: TaskPlan | None,
    binding_context: dict,
    repo_root: Path,
    model_adapter_fn: Callable | None = None,
    tool_adapter_fn: Callable | None = None,
    human_approval_fn: Callable | None = None,
) -> dict:
    step.status = STEP_STATUS_RUNNING
    step.updated_at = utc_now_iso()

    authority_error = _check_authority(step, binding_context)
    if authority_error:
        step.status = STEP_STATUS_BLOCKED
        step.errors.append(authority_error)
        return {"decision": DECISION_BLOCK, "reason": authority_error, "failure_class": ORCH_POLICY_DENIED}

    if step.step_type == "POLICY":
        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "step_type": "POLICY"}

    if step.step_type == "GATE":
        if check_approval_required(step):
            gate_record = create_approval_gate_record(step)
            resolved = resolve_approval_gate(gate_record, GATE_STATUS_APPROVED, human_approval_fn)
            if resolved.approval_status == GATE_STATUS_DENIED:
                step.status = STEP_STATUS_BLOCKED
                step.errors.append("Approval denied")
                return {"decision": DECISION_BLOCK, "reason": "Approval denied", "failure_class": ORCH_GATE_BLOCKED}
            step.status = STEP_STATUS_COMPLETED
            return {"decision": DECISION_CONTINUE, "gate_type": "APPROVAL", "status": resolved.approval_status}

        if check_governance_required(step):
            gate_record = create_approval_gate_record(step)
            gate_record.gate_type = "GOVERNANCE"
            resolved = resolve_approval_gate(gate_record, GATE_STATUS_APPROVED, None)
            if resolved.approval_status == GATE_STATUS_DENIED:
                step.status = STEP_STATUS_BLOCKED
                step.errors.append("Governance denied")
                return {"decision": DECISION_BLOCK, "reason": "Governance denied", "failure_class": ORCH_GATE_BLOCKED}
            step.status = STEP_STATUS_COMPLETED
            return {"decision": DECISION_CONTINUE, "gate_type": "GOVERNANCE", "status": resolved.approval_status}

        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "step_type": "GATE"}

    if step.step_type == "TOOL":
        tool_name = step.step_name.replace("execute_", "")
        binding, result = invoke_tool_for_step(
            step, tool_name, {}, tool_adapter_fn, binding_context,
        )
        if result.get("status") in ("BLOCKED", "FAILED"):
            step.status = STEP_STATUS_FAILED
            step.errors.extend(binding.errors)
            return {
                "decision": DECISION_BLOCK,
                "reason": binding.errors[-1] if binding.errors else "Tool call failed",
                "failure_class": ORCH_TOOL_BINDING_INVALID,
                "binding": binding.to_dict(),
            }
        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "tool_result": result, "binding": binding.to_dict()}

    if step.step_type == "MODEL":
        model_profile = step.step_name.replace("invoke_", "")
        binding, result = invoke_model_for_step(
            step, model_profile or "default", "", model_adapter_fn, binding_context,
        )
        if result.get("status") in ("BLOCKED", "FAILED"):
            step.status = STEP_STATUS_FAILED
            step.errors.extend(binding.errors)
            return {
                "decision": DECISION_BLOCK,
                "reason": binding.errors[-1] if binding.errors else "Model call failed",
                "failure_class": ORCH_MODEL_BINDING_INVALID,
                "binding": binding.to_dict(),
            }
        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "model_result": result, "binding": binding.to_dict()}

    if step.step_type == "PROMOTION":
        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "step_type": "PROMOTION"}

    if step.step_type == "EVIDENCE":
        step.status = STEP_STATUS_COMPLETED
        return {"decision": DECISION_CONTINUE, "step_type": "EVIDENCE"}

    step.status = STEP_STATUS_SKIPPED
    return {"decision": DECISION_CONTINUE, "reason": f"Unknown step type: {step.step_type}"}
