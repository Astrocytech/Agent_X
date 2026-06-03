import pytest

from agentx_evolve.recovery.recovery_decider import decide_recovery
from agentx_evolve.recovery.failure_models import (
    FailureRecord, SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_LOW,
    DECISION_RECOVERABLE, DECISION_BLOCKED, DECISION_SAFE_MODE_REQUIRED,
    DECISION_HUMAN_REVIEW_REQUIRED,
)


def _make_failure(failure_class: str, severity: str = "MEDIUM", **kw) -> FailureRecord:
    return FailureRecord(
        failure_id="fail_test",
        failure_class=failure_class,
        severity=severity,
        requires_recovery=kw.pop("requires_recovery", True),
        requires_safe_mode=kw.pop("requires_safe_mode", False),
        requires_human_review=kw.pop("requires_human_review", False),
        retryable=kw.pop("retryable", True),
        rollback_required=kw.pop("rollback_required", False),
        **kw,
    )


def test_critical_failure_blocks_continuation():
    f = _make_failure("ROLLBACK_FAILED", SEVERITY_CRITICAL)
    d = decide_recovery(f)
    assert d.continue_session_allowed is False


def test_recoverable_model_failure_allows_retry():
    f = _make_failure("MODEL_INVALID_OUTPUT", SEVERITY_LOW)
    d = decide_recovery(f)
    assert d.retry_allowed is True
    assert d.decision == DECISION_RECOVERABLE or d.decision == DECISION_HUMAN_REVIEW_REQUIRED


def test_policy_denied_decision_blocked():
    f = _make_failure("POLICY_DENIED", SEVERITY_HIGH, retryable=False)
    d = decide_recovery(f)
    assert d.decision == DECISION_BLOCKED


def test_safe_mode_failure_decision_safe_mode_required():
    f = _make_failure("SOURCE_GUARD_FAILED", SEVERITY_CRITICAL)
    d = decide_recovery(f)
    assert d.decision == DECISION_SAFE_MODE_REQUIRED or d.continue_session_allowed is False


def test_human_review_failure_decision_human_review_required():
    f = _make_failure("UNKNOWN_FAILURE", SEVERITY_HIGH)
    d = decide_recovery(f)
    assert d.human_review_required is True


def test_unknown_failure_does_not_continue_silently():
    f = _make_failure("UNKNOWN_FAILURE", SEVERITY_HIGH)
    d = decide_recovery(f)
    assert d.continue_session_allowed is False
    assert d.human_review_required is True


def test_rollback_failed_sets_rollback_required():
    f = _make_failure("ROLLBACK_FAILED", SEVERITY_CRITICAL, rollback_required=True)
    d = decide_recovery(f)
    assert d.rollback_required is True


def test_model_insufficient_context_decision():
    f = _make_failure("MODEL_INSUFFICIENT_CONTEXT", SEVERITY_LOW)
    d = decide_recovery(f)
    assert d.retry_allowed is True
