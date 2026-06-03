from __future__ import annotations

from typing import Any, Callable

from agentx_evolve.orchestrator.orchestrator_models import (
    ApprovalGateRecord,
    ExecutionStep,
    utc_now_iso,
    new_id,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
    GATE_STATUS_NOT_REQUIRED,
    GATE_TYPE_APPROVAL,
    GATE_TYPE_GOVERNANCE,
)


def check_approval_required(step: ExecutionStep) -> bool:
    return step.step_type == "GATE" and "approv" in step.step_name.lower()


def check_governance_required(step: ExecutionStep) -> bool:
    return step.step_type == "GATE" and "govern" in step.step_name.lower()


def create_approval_gate_record(
    step: ExecutionStep,
    reason: str = "",
    required_approver_role: str = "human_approver",
) -> ApprovalGateRecord:
    return ApprovalGateRecord(
        approval_record_id=new_id("ag"),
        step_id=step.step_id,
        run_id=step.run_id or "",
        created_at=utc_now_iso(),
        gate_type=GATE_TYPE_APPROVAL,
        reason=reason or f"Approval required for step: {step.step_name}",
        required_approver_role=required_approver_role,
        approval_status=GATE_STATUS_PENDING,
    )


def resolve_approval_gate(
    record: ApprovalGateRecord,
    decision: str,
    human_approval_adapter_fn: Callable | None = None,
) -> ApprovalGateRecord:
    if decision not in (GATE_STATUS_APPROVED, GATE_STATUS_DENIED, GATE_STATUS_NOT_REQUIRED):
        record.approval_status = GATE_STATUS_DENIED
        record.errors.append(f"Invalid approval decision: {decision}")
        return record

    if human_approval_adapter_fn is not None:
        try:
            adapter_result = human_approval_adapter_fn(
                approval_record_id=record.approval_record_id,
                decision=decision,
            )
            if adapter_result.get("decision") == "DENIED":
                record.approval_status = GATE_STATUS_DENIED
                record.errors.append(adapter_result.get("reason", "Approval denied by adapter"))
                return record
        except Exception as e:
            record.approval_status = GATE_STATUS_DENIED
            record.errors.append(f"Approval adapter error: {e}")
            return record

    record.approval_status = decision
    return record
