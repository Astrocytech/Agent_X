import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.recovery_controller import (
    classify_step_failure,
    choose_recovery_action,
    apply_recovery_action,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep
from agentx_evolve.orchestrator.orchestrator_config import (
    RECOVERY_ACTION_NONE,
    RECOVERY_ACTION_RETRY,
    RECOVERY_ACTION_STOP_RUN,
    RECOVERY_ACTION_HUMAN_REVIEW,
    RECOVERY_ACTION_REPLAN,
    RECOVERY_ACTION_ROLLBACK_REQUEST,
    DEFAULT_MAX_RETRIES_PER_STEP,
)


def test_classify_step_failure_known():
    step = ExecutionStep(step_id="s-1")
    result = {"failure_class": "ORCH_DEPENDENCY_MISSING"}
    assert classify_step_failure(step, result) == "ORCH_DEPENDENCY_MISSING"


def test_classify_step_failure_unknown():
    step = ExecutionStep(step_id="s-1")
    result = {"failure_class": "BOGUS"}
    assert classify_step_failure(step, result) == "ORCH_FAILURE_UNCLASSIFIED"


def test_classify_step_failure_empty():
    step = ExecutionStep(step_id="s-1")
    result = {}
    assert classify_step_failure(step, result) == "ORCH_FAILURE_UNCLASSIFIED"


def test_choose_recovery_action_retry():
    assert choose_recovery_action("ORCH_DEPENDENCY_MISSING") == RECOVERY_ACTION_RETRY


def test_choose_recovery_action_stop_run():
    assert choose_recovery_action("ORCH_CONTRACT_INCOMPATIBLE") == RECOVERY_ACTION_STOP_RUN


def test_choose_recovery_action_human_review():
    assert choose_recovery_action("ORCH_GATE_BLOCKED") == RECOVERY_ACTION_HUMAN_REVIEW


def test_choose_recovery_action_none():
    assert choose_recovery_action("ORCH_FAILURE_UNCLASSIFIED") == RECOVERY_ACTION_NONE


def test_choose_recovery_action_unmapped():
    assert choose_recovery_action("BOGUS") == RECOVERY_ACTION_NONE


def test_apply_recovery_action_retry():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", RECOVERY_ACTION_RETRY, retry_count=0)
    assert action.action_status == "RETRYING"
    assert action.recovery_strategy == RECOVERY_ACTION_RETRY
    assert step.status == "PENDING"


def test_apply_recovery_action_retry_exhausted():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", RECOVERY_ACTION_RETRY, retry_count=3, max_retries=3)
    assert action.action_status == "FAILED"
    assert step.status == "FAILED"
    assert "Retry limit exceeded" in step.errors[-1]


def test_apply_recovery_action_none():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_FAILURE_UNCLASSIFIED", RECOVERY_ACTION_NONE)
    assert action.action_status == "FAILED"
    assert step.status == "FAILED"


def test_apply_recovery_action_stop_run():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_CONTRACT_INCOMPATIBLE", RECOVERY_ACTION_STOP_RUN)
    assert action.action_status == "STOPPING"
    assert step.status == "FAILED"


def test_apply_recovery_action_human_review():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_GATE_BLOCKED", RECOVERY_ACTION_HUMAN_REVIEW)
    assert action.action_status == "WAITING_FOR_HUMAN"
    assert step.status == "BLOCKED"


def test_apply_recovery_action_replan():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", RECOVERY_ACTION_REPLAN)
    assert action.action_status == "REPLANNING"
    assert step.status == "PENDING"


def test_apply_recovery_action_rollback():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_PATCH_LAYER_DENIED", RECOVERY_ACTION_ROLLBACK_REQUEST)
    assert action.action_status == "ROLLING_BACK"
    assert step.status == "BLOCKED"


def test_apply_recovery_action_unknown():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_FAILURE_UNCLASSIFIED", "BOGUS_STRATEGY")
    assert action.action_status == "FAILED"
    assert step.status == "FAILED"
    assert "Unknown recovery strategy" in step.errors[-1]


def test_apply_recovery_action_default_max_retries():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", RECOVERY_ACTION_RETRY)
    assert action.max_retries == DEFAULT_MAX_RETRIES_PER_STEP
    assert action.retry_count == 0


def test_apply_recovery_action_creates_valid_id():
    step = ExecutionStep(step_id="s-1", run_id="r-1")
    action = apply_recovery_action(step, "ORCH_DEPENDENCY_MISSING", RECOVERY_ACTION_RETRY)
    assert action.recovery_action_id.startswith("ra-")
    assert action.run_id == "r-1"
    assert action.failure_class == "ORCH_DEPENDENCY_MISSING"
