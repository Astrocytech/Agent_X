import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_audit import (
    append_session_history,
    write_latest_session,
    append_state_history,
    write_latest_state,
    append_execution_step,
    append_tool_invocation,
    append_model_invocation,
    append_prompt_binding,
    append_approval_gate_record,
    append_promotion_gate_record,
    append_recovery_action,
    append_evidence_event,
    append_ledger,
    write_latest_ledger,
    append_decision_history,
    append_recovery_history,
    append_gate_history,
    append_audit_history,
    write_latest_step,
    write_latest_result,
    write_latest_run_lock,
    create_evidence_manifest,
    write_evidence_manifest,
    create_review_report,
    write_review_report,
    create_completion_record,
    write_completion_record,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
    OrchestrationState,
    ExecutionStep,
    ToolInvocationBinding,
    ModelInvocationBinding,
    PromptBinding,
    ApprovalGateRecord,
    PromotionGateRecord,
    RecoveryAction,
    OrchestratorEvidenceEvent,
    RunLedger,
    OrchestratorEvidenceManifest,
    OrchestratorReviewReport,
    OrchestratorCompletionRecord,
)
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def test_append_session_history(tmp_path):
    session = OrchestrationSession(session_id="s-1", run_id="r-1")
    result = append_session_history(session, tmp_path)
    assert "path" in result
    assert "sha256" in result
    path = tmp_path / RUNTIME_ARTIFACT_ROOT / "runs" / "r-1" / "orchestration_session.json"
    assert path.exists()


def test_write_latest_session(tmp_path):
    session = OrchestrationSession(session_id="s-1", run_id="r-1")
    result = write_latest_session(session, tmp_path)
    assert "path" in result
    path = tmp_path / RUNTIME_ARTIFACT_ROOT / "latest_orchestration_session.json"
    assert path.exists()


def test_append_state_history(tmp_path):
    state = OrchestrationState(state_id="st-1", run_id="r-1")
    result = append_state_history(state, tmp_path)
    assert "sha256" in result


def test_write_latest_state(tmp_path):
    state = OrchestrationState(state_id="st-1", run_id="r-1")
    result = write_latest_state(state, tmp_path)
    assert "path" in result


def test_append_execution_step(tmp_path):
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    result = append_execution_step(step, tmp_path)
    assert "sha256" in result


def test_append_tool_invocation(tmp_path):
    binding = ToolInvocationBinding(binding_id="tb-1", run_id="r-1")
    result = append_tool_invocation(binding, tmp_path)
    assert "sha256" in result


def test_append_model_invocation(tmp_path):
    binding = ModelInvocationBinding(binding_id="mb-1", run_id="r-1")
    result = append_model_invocation(binding, tmp_path)
    assert "sha256" in result


def test_append_prompt_binding(tmp_path):
    binding = PromptBinding(binding_id="pb-1", run_id="r-1")
    result = append_prompt_binding(binding, tmp_path)
    assert "sha256" in result


def test_append_approval_gate_record(tmp_path):
    record = ApprovalGateRecord(approval_record_id="ag-1", run_id="r-1")
    result = append_approval_gate_record(record, tmp_path)
    assert "sha256" in result


def test_append_promotion_gate_record(tmp_path):
    record = PromotionGateRecord(promotion_record_id="pg-1", run_id="r-1")
    result = append_promotion_gate_record(record, tmp_path)
    assert "sha256" in result


def test_append_recovery_action(tmp_path):
    action = RecoveryAction(recovery_action_id="ra-1", run_id="r-1")
    result = append_recovery_action(action, tmp_path)
    assert "sha256" in result


def test_append_evidence_event(tmp_path):
    event = OrchestratorEvidenceEvent(event_id="evt-1", run_id="r-1")
    result = append_evidence_event(event, tmp_path)
    assert "sha256" in result


def test_append_ledger(tmp_path):
    ledger = RunLedger(ledger_id="l-1", run_id="r-1")
    result = append_ledger(ledger, tmp_path)
    assert "sha256" in result


def test_write_latest_ledger(tmp_path):
    ledger = RunLedger(ledger_id="l-1", run_id="r-1")
    result = write_latest_ledger(ledger, tmp_path)
    assert "path" in result


def test_append_decision_history(tmp_path):
    result = append_decision_history({"decision": "CONTINUE"}, "r-1", tmp_path)
    assert "sha256" in result


def test_append_recovery_history(tmp_path):
    action = RecoveryAction(recovery_action_id="ra-1", run_id="r-1")
    result = append_recovery_history(action, tmp_path)
    assert "sha256" in result


def test_append_gate_history(tmp_path):
    result = append_gate_history({"gate": "approved"}, "r-1", tmp_path)
    assert "sha256" in result


def test_append_audit_history(tmp_path):
    result = append_audit_history({"entry": "test"}, "r-1", tmp_path)
    assert "sha256" in result


def test_write_latest_step(tmp_path):
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    result = write_latest_step(step, tmp_path)
    assert "path" in result


def test_write_latest_result(tmp_path):
    result = write_latest_result({"status": "DONE"}, "r-1", tmp_path)
    assert "path" in result


def test_write_latest_run_lock(tmp_path):
    result = write_latest_run_lock({"status": "ACTIVE"}, "r-1", tmp_path)
    assert "path" in result


def test_create_evidence_manifest():
    manifest = create_evidence_manifest("r-1", "s-1")
    assert manifest.run_id == "r-1"
    assert manifest.session_id == "s-1"
    assert manifest.evidence_files == []
    assert manifest.runtime_artifacts == []
    assert manifest.final_decision == "NOT_DONE"
    assert len(manifest.evidence_manifest_sha256) == 64


def test_create_evidence_manifest_with_files():
    manifest = create_evidence_manifest("r-1", "s-1", evidence_files=["f1"], runtime_artifacts=["a1"])
    assert manifest.evidence_files == ["f1"]
    assert manifest.runtime_artifacts == ["a1"]


def test_write_evidence_manifest(tmp_path):
    manifest = create_evidence_manifest("r-1", "s-1")
    result = write_evidence_manifest(manifest, tmp_path)
    assert "path" in result
    assert result["sha256"] == manifest.evidence_manifest_sha256


def test_create_review_report():
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest)
    assert report.final_verdict == "NOT_DONE"
    assert report.review_report_id.startswith("rr-")
    assert len(report.review_report_sha256) == 64


def test_create_review_report_with_commands():
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest, commands_run=["test", "lint"])
    assert report.commands_run == ["test", "lint"]


def test_write_review_report(tmp_path):
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest)
    result = write_review_report(report, tmp_path, "r-1")
    assert "path" in result
    assert result["sha256"] == report.review_report_sha256


def test_create_completion_record():
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report)
    assert record.status == "DONE"
    assert record.implementation_score == 0.0
    assert len(record.completion_record_sha256) == 64


def test_create_completion_record_custom():
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report, status="FAILED", implementation_score=42.5)
    assert record.status == "FAILED"
    assert record.implementation_score == 42.5


def test_write_completion_record(tmp_path):
    manifest = create_evidence_manifest("r-1", "s-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report)
    result = write_completion_record(record, tmp_path, "r-1")
    assert "path" in result
    assert result["sha256"] == record.completion_record_sha256
