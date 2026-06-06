from agentx_evolve.recovery.failure_taxonomy import (
    REQUIRED_FAILURE_CLASSES,
    DEFAULT_SEVERITY_BY_FAILURE_CLASS,
    CRITICAL_CLASSES,
    is_known_failure_class,
    normalize_failure_class,
    get_failure_severity,
    classify_failure,
)
from agentx_evolve.recovery.failure_models import SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL


def test_required_failure_classes_is_populated():
    assert len(REQUIRED_FAILURE_CLASSES) > 10
    assert "UNKNOWN_FAILURE" in REQUIRED_FAILURE_CLASSES
    assert "MODEL_INVALID_OUTPUT" in REQUIRED_FAILURE_CLASSES


def test_all_required_classes_have_severity():
    for fc in REQUIRED_FAILURE_CLASSES:
        assert fc in DEFAULT_SEVERITY_BY_FAILURE_CLASS, f"{fc} missing severity"


def test_critical_classes_subset():
    for fc in CRITICAL_CLASSES:
        assert fc in REQUIRED_FAILURE_CLASSES
        assert DEFAULT_SEVERITY_BY_FAILURE_CLASS[fc] == SEVERITY_CRITICAL


def test_is_known_failure_class_known():
    assert is_known_failure_class("MODEL_INVALID_OUTPUT") is True
    assert is_known_failure_class("UNKNOWN_FAILURE") is True
    assert is_known_failure_class("PATH_TRAVERSAL") is True


def test_is_known_failure_class_unknown():
    assert is_known_failure_class("BOGUS_CLASS") is False
    assert is_known_failure_class("") is False


def test_normalize_failure_class_none():
    assert normalize_failure_class(None) == "UNKNOWN_FAILURE"


def test_normalize_failure_class_empty():
    assert normalize_failure_class("") == "UNKNOWN_FAILURE"


def test_normalize_failure_class_strips_and_uppercases():
    assert normalize_failure_class("  model_invalid_output  ") == "MODEL_INVALID_OUTPUT"


def test_normalize_failure_class_replaces_spaces():
    assert normalize_failure_class("patch apply failed") == "PATCH_APPLY_FAILED"


def test_normalize_failure_class_unknown_default():
    assert normalize_failure_class("nonexistent_class") == "UNKNOWN_FAILURE"


def test_get_failure_severity_known_class():
    assert get_failure_severity("MODEL_INVALID_OUTPUT") == SEVERITY_LOW
    assert get_failure_severity("SOURCE_GUARD_FAILED") == SEVERITY_CRITICAL
    assert get_failure_severity("TOOL_FAILURE") == SEVERITY_MEDIUM


def test_get_failure_severity_normalizes_input():
    assert get_failure_severity("  model_invalid_output  ") == SEVERITY_LOW


def test_get_failure_severity_unknown_defaults_high():
    assert get_failure_severity("BOGUS") == SEVERITY_HIGH


def test_get_failure_severity_unknown_with_mutation_context():
    assert get_failure_severity("BOGUS", {"mutation_state_unknown": True}) == SEVERITY_CRITICAL


def test_get_failure_severity_ignores_context_for_known():
    assert get_failure_severity("MODEL_INVALID_OUTPUT", {"mutation_state_unknown": True}) == SEVERITY_LOW


def test_classify_failure_minimal():
    result = classify_failure({})
    assert result.failure_class == "UNKNOWN_FAILURE"
    assert result.severity == SEVERITY_HIGH
    assert result.requires_recovery is True
    assert result.requires_safe_mode is True
    assert result.requires_human_review is True
    assert result.retryable is False


def test_classify_failure_none():
    result = classify_failure(None)
    assert result.failure_class == "UNKNOWN_FAILURE"
    assert result.message == "Malformed failure input: expected dict"


def test_classify_failure_not_dict():
    result = classify_failure("not a dict")
    assert result.failure_class == "UNKNOWN_FAILURE"


def test_classify_failure_known_class():
    result = classify_failure({"failure_class": "MODEL_INVALID_OUTPUT"})
    assert result.failure_class == "MODEL_INVALID_OUTPUT"
    assert result.severity == SEVERITY_LOW
    assert result.retryable is True


def test_classify_failure_critical_class():
    result = classify_failure({"failure_class": "ROLLBACK_FAILED"})
    assert result.severity == SEVERITY_CRITICAL
    assert result.requires_safe_mode is True
    assert result.requires_human_review is True
    assert result.retryable is False


def test_classify_failure_unknown_with_mutation_context():
    result = classify_failure({
        "failure_class": "UNKNOWN_FAILURE",
        "context": {"mutation_state_unknown": True},
    })
    assert result.severity == SEVERITY_CRITICAL


def test_classify_failure_with_source_info():
    result = classify_failure({
        "failure_class": "TOOL_FAILURE",
        "source_component": "TestTool",
        "source_layer": "tool_layer",
        "message": "Tool crashed",
    })
    assert result.source_component == "TestTool"
    assert result.source_layer == "tool_layer"
    assert result.message == "Tool crashed"


def test_classify_failure_with_optional_fields():
    result = classify_failure({
        "failure_class": "MODEL_INVALID_OUTPUT",
        "failure_id": "fail-001",
        "session_id": "session-1",
        "operation": "run_model",
        "details": {"key": "val"},
        "input_artifact_refs": ["ref1"],
        "related_artifact_refs": ["ref2"],
    })
    assert result.failure_id == "fail-001"
    assert result.session_id == "session-1"
    assert result.operation == "run_model"
    assert result.details == {"key": "val"}
    assert result.input_artifact_refs == ["ref1"]
    assert result.related_artifact_refs == ["ref2"]


def test_classify_failure_non_dict_details():
    result = classify_failure({"failure_class": "TOOL_FAILURE", "details": "string"})
    assert result.details == {}


def test_classify_failure_non_list_refs():
    result = classify_failure({
        "failure_class": "TOOL_FAILURE",
        "input_artifact_refs": "not_a_list",
        "related_artifact_refs": None,
    })
    assert result.input_artifact_refs == []
    assert result.related_artifact_refs == []


def test_classify_failure_rollback_classes():
    for fc in ("PATCH_APPLY_FAILED", "SOURCE_GUARD_FAILED", "ROLLBACK_FAILED"):
        result = classify_failure({"failure_class": fc})
        assert result.rollback_required is True, f"{fc} should require rollback"


def test_classify_failure_non_rollback():
    result = classify_failure({"failure_class": "TOOL_FAILURE"})
    assert result.rollback_required is False


def test_critical_severity_map():
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["SOURCE_GUARD_FAILED"] == SEVERITY_CRITICAL
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["ROLLBACK_FAILED"] == SEVERITY_CRITICAL
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["PATH_TRAVERSAL"] == SEVERITY_CRITICAL
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["PATH_OUTSIDE_REPO"] == SEVERITY_CRITICAL
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["SYMLINK_ESCAPE"] == SEVERITY_CRITICAL


def test_low_severity_map():
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["MODEL_INVALID_OUTPUT"] == SEVERITY_LOW
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["MODEL_INSUFFICIENT_CONTEXT"] == SEVERITY_LOW


def test_high_severity_map():
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["PATCH_APPLY_FAILED"] == SEVERITY_HIGH
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["GOVERNANCE_BLOCKED"] == SEVERITY_HIGH
    assert DEFAULT_SEVERITY_BY_FAILURE_CLASS["ATOMIC_WRITE_FAILED"] == SEVERITY_HIGH
