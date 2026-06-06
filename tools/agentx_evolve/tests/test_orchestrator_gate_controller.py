import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.gate_controller import (
    check_approval_required,
    check_governance_required,
    create_approval_gate_record,
    resolve_approval_gate,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, ApprovalGateRecord
from agentx_evolve.orchestrator.orchestrator_config import (
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
    GATE_STATUS_NOT_REQUIRED,
)


def _make_step(step_name="approval_gate", step_type="GATE", step_id="s-1", run_id="r-1"):
    return ExecutionStep(step_id=step_id, run_id=run_id, step_name=step_name, step_type=step_type)


def test_check_approval_required_true():
    step = _make_step(step_name="approval_gate")
    assert check_approval_required(step) is True


def test_check_approval_required_false():
    step = _make_step(step_name="tool_call")
    assert check_approval_required(step) is False


def test_check_governance_required_true():
    step = _make_step(step_name="governance_check")
    assert check_governance_required(step) is True


def test_check_governance_required_false():
    step = _make_step(step_name="tool_call")
    assert check_governance_required(step) is False


def test_create_approval_gate_record():
    step = _make_step(step_name="approval_gate", step_id="s-1", run_id="r-1")
    record = create_approval_gate_record(step)
    assert record.step_id == "s-1"
    assert record.run_id == "r-1"
    assert record.gate_type == "APPROVAL"
    assert record.approval_status == GATE_STATUS_PENDING
    assert "approval" in record.reason.lower()


def test_create_approval_gate_record_custom_reason():
    step = _make_step()
    record = create_approval_gate_record(step, reason="Custom reason", required_approver_role="admin")
    assert record.reason == "Custom reason"
    assert record.required_approver_role == "admin"


def test_resolve_approval_gate_approved():
    step = _make_step()
    record = create_approval_gate_record(step)
    result = resolve_approval_gate(record, GATE_STATUS_APPROVED)
    assert result.approval_status == GATE_STATUS_APPROVED


def test_resolve_approval_gate_denied():
    step = _make_step()
    record = create_approval_gate_record(step)
    result = resolve_approval_gate(record, GATE_STATUS_DENIED)
    assert result.approval_status == GATE_STATUS_DENIED


def test_resolve_approval_gate_invalid_decision():
    step = _make_step()
    record = create_approval_gate_record(step)
    result = resolve_approval_gate(record, "INVALID")
    assert result.approval_status == GATE_STATUS_DENIED
    assert "Invalid approval decision" in result.errors[-1]


def test_resolve_approval_gate_with_adapter_denies():
    step = _make_step()
    record = create_approval_gate_record(step)

    def adapter_fn(**kwargs):
        return {"decision": "DENIED", "reason": "Policy violation"}

    result = resolve_approval_gate(record, GATE_STATUS_APPROVED, human_approval_adapter_fn=adapter_fn)
    assert result.approval_status == GATE_STATUS_DENIED


def test_resolve_approval_gate_with_adapter_approves():
    step = _make_step()
    record = create_approval_gate_record(step)

    def adapter_fn(**kwargs):
        return {"decision": "APPROVED"}

    result = resolve_approval_gate(record, GATE_STATUS_APPROVED, human_approval_adapter_fn=adapter_fn)
    assert result.approval_status == GATE_STATUS_APPROVED


def test_resolve_approval_gate_with_adapter_raises():
    step = _make_step()
    record = create_approval_gate_record(step)

    def adapter_fn(**kwargs):
        raise RuntimeError("Adapter crashed")

    result = resolve_approval_gate(record, GATE_STATUS_APPROVED, human_approval_adapter_fn=adapter_fn)
    assert result.approval_status == GATE_STATUS_DENIED
    assert "Approval adapter error" in result.errors[-1]


def test_resolve_approval_gate_not_required():
    step = _make_step()
    record = create_approval_gate_record(step)
    result = resolve_approval_gate(record, GATE_STATUS_NOT_REQUIRED)
    assert result.approval_status == GATE_STATUS_NOT_REQUIRED
