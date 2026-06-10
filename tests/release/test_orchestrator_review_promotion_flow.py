import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationTask, OrchestrationSession, ApprovalGateRecord,
    PromotionGateRecord, OrchestratorEvidenceEvent,
    utc_now_iso, new_id, to_dict,
)
from agentx_evolve.orchestrator.orchestrator_config import (
    ORCH_STATUS_CREATED, GATE_STATUS_PENDING, GATE_STATUS_APPROVED,
    GATE_STATUS_DENIED, GATE_TYPE_APPROVAL,
)
from agentx_evolve.orchestrator.promotion_gate import (
    check_promotion_ready, create_promotion_gate_record,
    request_promotion_decision,
)


class TestOrchestratorReviewPromotionFlow:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_orchestrator_can_be_created_with_bounded_goal(self):
        task = OrchestrationTask(
            task_id=new_id("task"), title="Implement bounded feature",
            description="Add input validation to API endpoint",
            risk_level="LOW", requires_human_approval=False,
            requires_promotion_gate=False,
        )
        assert task.task_id.startswith("task-")
        assert task.title == "Implement bounded feature"
        assert task.risk_level == "LOW"

    def test_human_review_can_approve(self):
        gate = ApprovalGateRecord(
            approval_record_id=new_id("app"),
            step_id="step-1", session_id="sess-1", run_id="run-1",
            gate_type=GATE_TYPE_APPROVAL,
            approval_status=GATE_STATUS_APPROVED,
        )
        assert gate.is_resolved()

    def test_human_review_can_reject(self):
        gate = ApprovalGateRecord(
            approval_record_id=new_id("app"),
            step_id="step-1", session_id="sess-1", run_id="run-1",
            gate_type=GATE_TYPE_APPROVAL,
            approval_status=GATE_STATUS_DENIED,
        )
        assert gate.is_resolved()
        assert gate.approval_status == GATE_STATUS_DENIED

    def test_promotion_gate_rejects_without_validation(self):
        record = create_promotion_gate_record("run-1")
        ready, blockers = check_promotion_ready(None, None)
        assert not ready
        assert any("manifest" in b.lower() for b in blockers)

    def test_promotion_gate_with_validation_approves(self):
        record = create_promotion_gate_record("run-1")
        result = request_promotion_decision(record, promotion_gate_fn=None)
        assert result.promotion_status == GATE_STATUS_APPROVED

    def test_orchestrator_records_major_steps(self):
        event = OrchestratorEvidenceEvent(
            event_id=new_id("evt"), session_id="sess-1", run_id="run-1",
            event_type="STEP_COMPLETED", status="DONE",
            message="Step 1 of 3 completed",
        )
        d = to_dict(event)
        assert d["event_type"] == "STEP_COMPLETED"
        assert d["status"] == "DONE"
