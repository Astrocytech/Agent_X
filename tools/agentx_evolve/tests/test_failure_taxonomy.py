import pytest

from agentx_evolve.recovery.failure_taxonomy import (
    REQUIRED_FAILURE_CLASSES,
    DEFAULT_SEVERITY_BY_FAILURE_CLASS,
    is_known_failure_class,
    normalize_failure_class,
    get_failure_severity,
    classify_failure,
    CRITICAL_CLASSES,
)
from agentx_evolve.recovery.failure_models import SEVERITY_CRITICAL, SEVERITY_HIGH


def test_failure_taxonomy_contains_required_classes():
    required = {
        "MODEL_INVALID_OUTPUT", "MODEL_INSUFFICIENT_CONTEXT",
        "PATCH_APPLY_FAILED", "VALIDATION_FAILED", "GOVERNANCE_BLOCKED",
        "RISK_TOO_HIGH", "SOURCE_GUARD_FAILED", "ROLLBACK_FAILED",
        "SCHEMA_VALIDATION_FAILED", "TOOL_FAILURE", "LOCK_CONFLICT",
        "ATOMIC_WRITE_FAILED", "PROMPT_CONTRACT_FAILED", "POLICY_DENIED",
        "UNKNOWN_FAILURE",
    }
    assert required.issubset(REQUIRED_FAILURE_CLASSES)


def test_unknown_failure_maps_to_unknown_failure():
    result = classify_failure({})
    assert result.failure_class == "UNKNOWN_FAILURE"


def test_unknown_failure_requires_human_review():
    result = classify_failure({"failure_class": "UNKNOWN_FAILURE"})
    assert result.requires_human_review is True
    assert result.requires_recovery is True


def test_l0_write_blocked_is_critical():
    sev = get_failure_severity("L0_WRITE_BLOCKED")
    assert sev == SEVERITY_CRITICAL


def test_path_traversal_is_critical():
    sev = get_failure_severity("PATH_TRAVERSAL")
    assert sev == SEVERITY_CRITICAL


def test_model_invalid_output_is_low_or_medium():
    sev = get_failure_severity("MODEL_INVALID_OUTPUT")
    assert sev in ("LOW", "MEDIUM")


def test_required_failure_classes_have_severity():
    for fc in REQUIRED_FAILURE_CLASSES:
        assert fc in DEFAULT_SEVERITY_BY_FAILURE_CLASS, f"{fc} missing severity"
        sev = DEFAULT_SEVERITY_BY_FAILURE_CLASS[fc]
        assert sev in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_is_known_failure_class():
    assert is_known_failure_class("MODEL_INVALID_OUTPUT") is True
    assert is_known_failure_class("UNKNOWN_FAILURE") is True
    assert is_known_failure_class("BOGUS") is False


def test_normalize_failure_class():
    assert normalize_failure_class(None) == "UNKNOWN_FAILURE"
    assert normalize_failure_class("") == "UNKNOWN_FAILURE"
    assert normalize_failure_class("unknown_failure") == "UNKNOWN_FAILURE"
    assert normalize_failure_class("PATH_TRAVERSAL") == "PATH_TRAVERSAL"


def test_malformed_input_none():
    result = classify_failure(None)
    assert result.failure_class == "UNKNOWN_FAILURE"


def test_malformed_input_not_dict():
    result = classify_failure("not a dict")
    assert result.failure_class == "UNKNOWN_FAILURE"


def test_critical_failure_sets_safe_mode():
    result = classify_failure({"failure_class": "ROLLBACK_FAILED"})
    assert result.requires_safe_mode is True
    assert result.severity == SEVERITY_CRITICAL


def test_unknown_failure_with_mutation_unknown_is_critical():
    result = classify_failure({"failure_class": "UNKNOWN_FAILURE", "context": {"mutation_state_unknown": True}})
    assert result.severity == SEVERITY_CRITICAL
