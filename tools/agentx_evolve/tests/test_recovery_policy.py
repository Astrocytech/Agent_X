import pytest

from agentx_evolve.recovery.recovery_policy import select_recovery_actions
from agentx_evolve.recovery.failure_models import (
    FailureRecord, SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_LOW,
    ACTION_RETRY, ACTION_REBUILD_CONTEXT, ACTION_ROLLBACK,
    ACTION_BLOCK_SESSION, ACTION_ENTER_SAFE_MODE,
    ACTION_REQUEST_HUMAN_REVIEW, ACTION_REJECT_OUTPUT,
)
from agentx_evolve.recovery.failure_taxonomy import classify_failure


def _make_failure(failure_class: str, severity: str = "MEDIUM") -> FailureRecord:
    return FailureRecord(
        failure_id="fail_test",
        failure_class=failure_class,
        severity=severity,
        requires_recovery=True,
    )


def test_model_invalid_output_selects_reject_and_retry():
    f = _make_failure("MODEL_INVALID_OUTPUT")
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_REJECT_OUTPUT in types
    assert ACTION_RETRY in types


def test_model_insufficient_context_selects_rebuild_context():
    f = _make_failure("MODEL_INSUFFICIENT_CONTEXT")
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_REBUILD_CONTEXT in types


def test_policy_denied_blocks_session():
    f = _make_failure("POLICY_DENIED", SEVERITY_HIGH)
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_BLOCK_SESSION in types


def test_risk_too_high_requires_human_review():
    f = _make_failure("RISK_TOO_HIGH", SEVERITY_HIGH)
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_REQUEST_HUMAN_REVIEW in types
    assert ACTION_BLOCK_SESSION in types


def test_patch_apply_failed_after_mutation_selects_rollback():
    f = _make_failure("PATCH_APPLY_FAILED", SEVERITY_HIGH)
    actions = select_recovery_actions(f, {"mutation_started": True, "rollback_available": True})
    types = [a.action_type for a in actions]
    assert ACTION_ROLLBACK in types


def test_validation_failed_after_mutation_selects_rollback_or_revalidate():
    f = _make_failure("VALIDATION_FAILED")
    ctx = {"validation_failed_after_mutation": True, "rollback_available": True}
    actions = select_recovery_actions(f, ctx)
    types = [a.action_type for a in actions]
    assert ACTION_ROLLBACK in types


def test_unknown_failure_selects_human_review_and_block():
    f = _make_failure("UNKNOWN_FAILURE", SEVERITY_HIGH)
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_REQUEST_HUMAN_REVIEW in types
    assert ACTION_BLOCK_SESSION in types


def test_secret_redaction_failed_blocks_logging_and_review():
    f = _make_failure("SECRET_REDACTION_FAILED", SEVERITY_CRITICAL)
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_BLOCK_SESSION in types
    assert ACTION_REQUEST_HUMAN_REVIEW in types


def test_critical_failure_always_safe_mode():
    f = _make_failure("PATH_TRAVERSAL", SEVERITY_CRITICAL)
    actions = select_recovery_actions(f)
    types = [a.action_type for a in actions]
    assert ACTION_ENTER_SAFE_MODE in types
    assert ACTION_REQUEST_HUMAN_REVIEW in types
    assert ACTION_BLOCK_SESSION in types
