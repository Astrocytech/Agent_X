import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.recovery_manager import (
    classify_step_failure,
    choose_recovery_action,
    apply_recovery_action,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep, RecoveryAction
from agentx_evolve.orchestrator.orchestrator_config import (
    STEP_STATUS_PENDING,
    STEP_STATUS_BLOCKED,
    RECOVERY_ACTION_NONE,
    RECOVERY_ACTION_RETRY,
    RECOVERY_ACTION_STOP_RUN,
    RECOVERY_ACTION_HUMAN_REVIEW,
    RECOVERY_ACTION_ROLLBACK_REQUEST,
    DEFAULT_MAX_RETRIES_PER_STEP,
)
from agentx_evolve.orchestrator.orchestrator_errors import (
    ORCH_GATE_BLOCKED,
    ORCH_TOOL_BINDING_INVALID,
    ORCH_POLICY_DENIED,
    ORCH_PATCH_LAYER_DENIED,
    ORCH_FAILURE_UNCLASSIFIED,
)


def _make_step(**overrides) -> ExecutionStep:
    params = dict(
        step_id="s-1",
        plan_id="p-1",
        run_id="run-1",
        step_index=0,
        step_name="test_step",
        step_type="TOOL",
        assigned_role="tool_agent",
        status=STEP_STATUS_PENDING,
    )
    params.update(overrides)
    return ExecutionStep(**params)


class TestClassifyStepFailureKnown:
    def test_classify_step_failure_known(self):
        step = _make_step()
        result = {"failure_class": ORCH_TOOL_BINDING_INVALID}
        fclass = classify_step_failure(step, result)
        assert fclass == ORCH_TOOL_BINDING_INVALID

    def test_classify_gate_blocked(self):
        step = _make_step()
        result = {"failure_class": ORCH_GATE_BLOCKED}
        fclass = classify_step_failure(step, result)
        assert fclass == ORCH_GATE_BLOCKED


class TestClassifyStepFailureUnknown:
    def test_classify_step_failure_unknown(self):
        step = _make_step()
        result = {"failure_class": "BOGUS_ERROR"}
        fclass = classify_step_failure(step, result)
        assert fclass == ORCH_FAILURE_UNCLASSIFIED

    def test_classify_missing_failure_class(self):
        step = _make_step()
        result = {}
        fclass = classify_step_failure(step, result)
        assert fclass == ORCH_FAILURE_UNCLASSIFIED


class TestChooseRecoveryActionKnown:
    def test_choose_recovery_action_known(self):
        action = choose_recovery_action(ORCH_TOOL_BINDING_INVALID)
        assert action == RECOVERY_ACTION_RETRY

    def test_choose_recovery_human_review(self):
        action = choose_recovery_action(ORCH_GATE_BLOCKED)
        assert action == RECOVERY_ACTION_HUMAN_REVIEW

    def test_choose_recovery_stop_run(self):
        action = choose_recovery_action(ORCH_PATCH_LAYER_DENIED)
        assert action == RECOVERY_ACTION_ROLLBACK_REQUEST


class TestChooseRecoveryActionUnknownDefaultsNone:
    def test_choose_recovery_action_unknown_defaults_none(self):
        action = choose_recovery_action("UNKNOWN_ERROR")
        assert action == RECOVERY_ACTION_NONE

    def test_choose_recovery_missing_defaults_none(self):
        action = choose_recovery_action("")
        assert action == RECOVERY_ACTION_NONE


class TestApplyRecoveryActionRetry:
    def test_apply_recovery_action_retry(self):
        step = _make_step()
        action = apply_recovery_action(step, ORCH_TOOL_BINDING_INVALID, RECOVERY_ACTION_RETRY, retry_count=0)
        assert action.action_status == "RETRYING"
        assert action.recovery_strategy == RECOVERY_ACTION_RETRY
        assert step.status == STEP_STATUS_PENDING


class TestApplyRecoveryActionRetryLimitExceeded:
    def test_apply_recovery_action_retry_limit_exceeded(self):
        step = _make_step()
        action = apply_recovery_action(
            step, ORCH_TOOL_BINDING_INVALID, RECOVERY_ACTION_RETRY,
            retry_count=DEFAULT_MAX_RETRIES_PER_STEP,
        )
        assert action.action_status == "FAILED"
        assert step.status == "FAILED"
        assert "Retry limit exceeded" in step.errors[-1]


class TestApplyRecoveryActionStopRun:
    def test_apply_recovery_action_stop_run(self):
        step = _make_step()
        action = apply_recovery_action(step, "ORCH_CONTRACT_INCOMPATIBLE", RECOVERY_ACTION_STOP_RUN)
        assert action.action_status == "STOPPING"
        assert step.status == "FAILED"
        assert "Stopping run" in step.errors[-1]


class TestApplyRecoveryActionHumanReview:
    def test_apply_recovery_action_human_review(self):
        step = _make_step()
        action = apply_recovery_action(step, ORCH_POLICY_DENIED, RECOVERY_ACTION_HUMAN_REVIEW)
        assert action.action_status == "WAITING_FOR_HUMAN"
        assert step.status == STEP_STATUS_BLOCKED
        assert "human review" in step.errors[-1].lower()


class TestApplyRecoveryActionRollback:
    def test_apply_recovery_action_rollback(self):
        step = _make_step()
        action = apply_recovery_action(step, ORCH_PATCH_LAYER_DENIED, RECOVERY_ACTION_ROLLBACK_REQUEST)
        assert action.action_status == "ROLLING_BACK"
        assert step.status == STEP_STATUS_BLOCKED
        assert "Rollback requested" in step.errors[-1]
