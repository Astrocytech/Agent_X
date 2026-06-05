import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.orchestrator_logger import (
    append_session_history,
    write_latest_session,
    append_state_history,
    write_latest_state,
    append_execution_step,
    append_tool_invocation,
    append_model_invocation,
    append_approval_gate_record,
    append_promotion_gate_record,
    append_recovery_action,
    append_evidence_event,
    append_ledger,
    write_latest_ledger,
)
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
    OrchestrationState,
    ExecutionStep,
    ToolInvocationBinding,
    ModelInvocationBinding,
    ApprovalGateRecord,
    PromotionGateRecord,
    RecoveryAction,
    OrchestratorEvidenceEvent,
    RunLedger,
)


def test_append_session_history(tmp_path):
    session = OrchestrationSession(session_id="sess-1", run_id="run-1")
    result = append_session_history(session, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_write_latest_session(tmp_path):
    session = OrchestrationSession(session_id="sess-2", run_id="run-2")
    result = write_latest_session(session, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_state_history(tmp_path):
    state = OrchestrationState(state_id="st-1", session_id="sess-1", run_id="run-1")
    result = append_state_history(state, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_write_latest_state(tmp_path):
    state = OrchestrationState(state_id="st-2", session_id="sess-2", run_id="run-2")
    result = write_latest_state(state, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_execution_step(tmp_path):
    step = ExecutionStep(
        step_id="step-1", plan_id="plan-1", session_id="sess-1",
        run_id="run-1", step_index=0, step_name="test",
        step_type="POLICY", assigned_role="orchestrator",
    )
    r1 = append_execution_step(step, tmp_path)
    assert "path" in r1
    assert "sha256" in r1
    r2 = append_execution_step(step, tmp_path)
    p = Path(r1["path"])
    assert p.exists()
    lines = p.read_text().strip().split("\n")
    assert len(lines) == 2


def test_append_tool_invocation(tmp_path):
    binding = ToolInvocationBinding(
        binding_id="tb-1", step_id="step-1", session_id="sess-1",
        run_id="run-1", tool_name="source_reader",
        caller_role="tool_agent", requested_effect="read",
        arguments_summary="{}",
    )
    result = append_tool_invocation(binding, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_model_invocation(tmp_path):
    binding = ModelInvocationBinding(
        binding_id="mb-1", step_id="step-1", session_id="sess-1",
        run_id="run-1", model_profile_id="default",
        prompt_contract_version="1.0", prompt_binding_id="pb-1",
        caller_role="model_agent", requested_task_type="impl",
    )
    result = append_model_invocation(binding, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_approval_gate_record(tmp_path):
    record = ApprovalGateRecord(
        approval_record_id="ag-1", step_id="step-1",
        session_id="sess-1", run_id="run-1",
        gate_type="APPROVAL", reason="need approval",
        required_approver_role="human",
    )
    result = append_approval_gate_record(record, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_promotion_gate_record(tmp_path):
    record = PromotionGateRecord(
        promotion_record_id="pg-1", session_id="sess-1",
        run_id="run-1", promotion_target="next_layer",
    )
    result = append_promotion_gate_record(record, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_recovery_action(tmp_path):
    action = RecoveryAction(
        recovery_action_id="ra-1", session_id="sess-1",
        run_id="run-1", failure_class="TEST",
    )
    result = append_recovery_action(action, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_evidence_event(tmp_path):
    event = OrchestratorEvidenceEvent(
        event_id="evt-1", session_id="sess-1",
        run_id="run-1", event_type="TEST",
        status="OK", message="test event",
    )
    result = append_evidence_event(event, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_append_ledger(tmp_path):
    ledger = RunLedger(
        ledger_id="ledger-1", session_id="sess-1",
        run_id="run-1", task_id="t-1",
    )
    result = append_ledger(ledger, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()


def test_write_latest_ledger(tmp_path):
    ledger = RunLedger(
        ledger_id="ledger-2", session_id="sess-2",
        run_id="run-2", task_id="t-2",
    )
    result = write_latest_ledger(ledger, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()
