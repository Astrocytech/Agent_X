import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.failure_recovery import (
    classify_step_failure,
    choose_recovery_action,
    apply_recovery_action,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, RecoveryAction


def test_classify_step_failure_known():
    step = ExecutionStep(step_id="s-1")
    result = {"failure_class": "ORCH_DEPENDENCY_MISSING"}
    assert classify_step_failure(step, result) == "ORCH_DEPENDENCY_MISSING"


def test_classify_step_failure_unknown():
    step = ExecutionStep(step_id="s-1")
    result = {"failure_class": "BOGUS"}
    assert classify_step_failure(step, result) == "ORCH_FAILURE_UNCLASSIFIED"


def test_classify_step_failure_missing_key():
    step = ExecutionStep(step_id="s-1")
    result = {}
    assert classify_step_failure(step, result) == "ORCH_FAILURE_UNCLASSIFIED"


def test_choose_recovery_action_mapped():
    assert choose_recovery_action("ORCH_DEPENDENCY_MISSING") == "RETRY"


def test_choose_recovery_action_unmapped():
    assert choose_recovery_action("BOGUS") == "NONE"


def test_choose_recovery_action_all_mapped():
    for fc, expected in [
        ("ORCH_DEPENDENCY_MISSING", "RETRY"),
        ("ORCH_CONTRACT_INCOMPATIBLE", "STOP_RUN"),
        ("ORCH_GATE_BLOCKED", "HUMAN_REVIEW"),
        ("ORCH_HUMAN_APPROVAL_MISSING", "HUMAN_REVIEW"),
        ("ORCH_PROMOTION_DENIED", "HUMAN_REVIEW"),
        ("ORCH_BUDGET_EXCEEDED", "STOP_RUN"),
        ("ORCH_EVIDENCE_MISSING", "RETRY"),
        ("ORCH_FAILURE_UNCLASSIFIED", "NONE"),
    ]:
        assert choose_recovery_action(fc) == expected


def test_apply_recovery_action_retry_under_limit():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", "RETRY", retry_count=0, max_retries=3)
    assert action.action_status == "RETRYING"
    assert action.recovery_strategy == "RETRY"
    assert action.retry_count == 0


def test_apply_recovery_action_retry_exceeds_limit():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", "RETRY", retry_count=3, max_retries=3)
    assert action.action_status == "FAILED"
    assert "Retry limit exceeded" in step.errors[-1]


def test_apply_recovery_action_none():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_FAILURE_UNCLASSIFIED", "NONE")
    assert action.action_status == "FAILED"
    assert step.status == "FAILED"


def test_apply_recovery_action_stop_run():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_CONTRACT_INCOMPATIBLE", "STOP_RUN")
    assert action.action_status == "STOPPING"
    assert step.status == "FAILED"


def test_apply_recovery_action_human_review():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_GATE_BLOCKED", "HUMAN_REVIEW")
    assert action.action_status == "WAITING_FOR_HUMAN"
    assert step.status == "BLOCKED"


def test_apply_recovery_action_replan():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", "REPLAN")
    assert action.action_status == "REPLANNING"
    assert step.status == "PENDING"


def test_apply_recovery_action_rollback():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_PATCH_LAYER_DENIED", "ROLLBACK_REQUEST")
    assert action.action_status == "ROLLING_BACK"
    assert step.status == "BLOCKED"


def test_apply_recovery_action_unknown():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_FAILURE_UNCLASSIFIED", "UNKNOWN_STRATEGY")
    assert action.action_status == "FAILED"
    assert step.status == "FAILED"
