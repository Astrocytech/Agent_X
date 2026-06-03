import pytest

from agentx_evolve.recovery.safe_mode_triggers import (
    requires_safe_mode,
    get_safe_mode_trigger_type,
    build_safe_mode_trigger,
)
from agentx_evolve.recovery.failure_models import (
    FailureRecord, SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_LOW,
    TRIGGER_ROLLBACK_FAILED, TRIGGER_SOURCE_GUARD_FAILED,
    TRIGGER_UNEXPECTED_FILE_MUTATION, TRIGGER_UNKNOWN_CRITICAL_FAILURE,
)


def _make_failure(failure_class: str, severity: str = "MEDIUM", **kw) -> FailureRecord:
    return FailureRecord(
        failure_id="fail_test",
        failure_class=failure_class,
        severity=severity,
        **kw,
    )


def test_rollback_failed_triggers_safe_mode():
    f = _make_failure("ROLLBACK_FAILED", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_source_guard_failed_triggers_safe_mode():
    f = _make_failure("SOURCE_GUARD_FAILED", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_unexpected_file_mutation_triggers_safe_mode():
    f = _make_failure("UNEXPECTED_FILE_MUTATION", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_l0_write_blocked_triggers_safe_mode():
    f = _make_failure("L0_WRITE_BLOCKED", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_path_traversal_triggers_safe_mode():
    f = _make_failure("PATH_TRAVERSAL", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_symlink_escape_triggers_safe_mode():
    f = _make_failure("SYMLINK_ESCAPE", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_unknown_critical_failure_triggers_safe_mode():
    f = _make_failure("UNKNOWN_FAILURE", SEVERITY_CRITICAL)
    assert requires_safe_mode(f) is True


def test_low_model_failure_does_not_trigger_safe_mode():
    f = _make_failure("MODEL_INVALID_OUTPUT", SEVERITY_LOW, requires_safe_mode=False)
    assert requires_safe_mode(f) is False


def test_build_safe_mode_trigger():
    f = _make_failure("ROLLBACK_FAILED", SEVERITY_CRITICAL)
    t = build_safe_mode_trigger(f, "Rollback failed")
    assert t.trigger_type == TRIGGER_ROLLBACK_FAILED
    assert t.failure_id == "fail_test"
