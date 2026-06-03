import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.approval_gate import (
    check_approval_required,
    check_governance_required,
    create_approval_gate_record,
    resolve_approval_gate,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, ApprovalGateRecord
from agentx_evolve.orchestrator.orchestrator_config import (
    STEP_STATUS_PENDING,
    GATE_STATUS_PENDING,
    GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED,
    GATE_STATUS_NOT_REQUIRED,
)


def _make_step(**overrides) -> ExecutionStep:
    params = dict(
        step_id="s-1",
        plan_id="p-1",
        run_id="run-1",
        step_index=0,
        step_name="test_gate",
        step_type="GATE",
        assigned_role="orchestrator",
        status=STEP_STATUS_PENDING,
    )
    params.update(overrides)
    return ExecutionStep(**params)


class TestCheckApprovalRequired:
    def test_check_approval_required_true(self):
        step = _make_step(step_name="approval_gate")
        assert check_approval_required(step) is True

    def test_check_approval_required_false(self):
        step = _make_step(step_name="governance_gate")
        assert check_approval_required(step) is False

    def test_check_approval_required_non_gate(self):
        step = _make_step(step_type="TOOL", step_name="approval_check")
        assert check_approval_required(step) is False


class TestCheckGovernanceRequired:
    def test_check_governance_required_true(self):
        step = _make_step(step_name="governance_gate")
        assert check_governance_required(step) is True

    def test_check_governance_required_false(self):
        step = _make_step(step_name="approval_gate")
        assert check_governance_required(step) is False

    def test_check_governance_required_non_gate(self):
        step = _make_step(step_type="TOOL", step_name="governance_check")
        assert check_governance_required(step) is False


class TestCreateApprovalGateRecord:
    def test_create_approval_gate_record(self):
        step = _make_step()
        record = create_approval_gate_record(step, reason="Need approval")
        assert record.approval_record_id.startswith("ag-")
        assert record.step_id == "s-1"
        assert record.gate_type == "APPROVAL"
        assert record.approval_status == GATE_STATUS_PENDING
        assert "Need approval" in record.reason


class TestResolveApprovalGateApproved:
    def test_resolve_approval_gate_approved(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )
        resolved = resolve_approval_gate(record, GATE_STATUS_APPROVED)
        assert resolved.approval_status == GATE_STATUS_APPROVED
        assert resolved.errors == []


class TestResolveApprovalGateDenied:
    def test_resolve_approval_gate_denied(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )
        resolved = resolve_approval_gate(record, GATE_STATUS_DENIED)
        assert resolved.approval_status == GATE_STATUS_DENIED


class TestResolveApprovalGateRejectsInvalidDecision:
    def test_resolve_approval_gate_rejects_invalid_decision(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )
        resolved = resolve_approval_gate(record, "MAYBE")
        assert resolved.approval_status == GATE_STATUS_DENIED
        assert any("Invalid" in e for e in resolved.errors)


class TestResolveApprovalGateUsesAdapter:
    def test_resolve_approval_gate_uses_adapter(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )
        called = False

        def fake_adapter(**kw):
            nonlocal called
            called = True
            return {"decision": "APPROVED"}

        resolved = resolve_approval_gate(record, GATE_STATUS_APPROVED, fake_adapter)
        assert called
        assert resolved.approval_status == GATE_STATUS_APPROVED

    def test_resolve_approval_gate_adapter_denies(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )

        def denying_adapter(**kw):
            return {"decision": "DENIED", "reason": "vetoed"}

        resolved = resolve_approval_gate(record, GATE_STATUS_APPROVED, denying_adapter)
        assert resolved.approval_status == GATE_STATUS_DENIED
        assert any("vetoed" in e for e in resolved.errors)

    def test_resolve_approval_gate_adapter_error(self):
        record = ApprovalGateRecord(
            approval_record_id="ag-1",
            step_id="s-1",
            run_id="run-1",
            approval_status=GATE_STATUS_PENDING,
        )

        def broken_adapter(**kw):
            raise Exception("adapter blew up")

        resolved = resolve_approval_gate(record, GATE_STATUS_APPROVED, broken_adapter)
        assert resolved.approval_status == GATE_STATUS_DENIED
        assert any("adapter error" in e.lower() for e in resolved.errors)
