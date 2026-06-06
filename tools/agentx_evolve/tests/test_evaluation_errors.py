import pytest
from agentx_evolve.evaluation.evaluation_errors import (
    EVAL_FIXTURE_INVALID, EVAL_SUITE_NOT_FOUND, EVAL_CASE_NOT_FOUND,
    EVAL_CASE_FAILED, EVAL_THRESHOLD_FAILED, EVAL_REGRESSION_DETECTED,
    EVAL_BASELINE_MISSING, EVAL_BASELINE_INVALID, EVAL_POLICY_DENIED,
    EVAL_TOOL_ADAPTER_UNAVAILABLE, EVAL_TOOL_CALL_BLOCKED,
    EVAL_REPORT_WRITE_FAILED, EVAL_EVIDENCE_WRITE_FAILED,
    EVAL_SOURCE_MUTATION_DETECTED, EVAL_UNKNOWN_FAILURE,
    ALL_EVAL_FAILURE_CLASSES,
)


def test_fixture_invalid():
    assert EVAL_FIXTURE_INVALID == "EVAL_FIXTURE_INVALID"


def test_suite_not_found():
    assert EVAL_SUITE_NOT_FOUND == "EVAL_SUITE_NOT_FOUND"


def test_case_not_found():
    assert EVAL_CASE_NOT_FOUND == "EVAL_CASE_NOT_FOUND"


def test_case_failed():
    assert EVAL_CASE_FAILED == "EVAL_CASE_FAILED"


def test_threshold_failed():
    assert EVAL_THRESHOLD_FAILED == "EVAL_THRESHOLD_FAILED"


def test_regression_detected():
    assert EVAL_REGRESSION_DETECTED == "EVAL_REGRESSION_DETECTED"


def test_baseline_missing():
    assert EVAL_BASELINE_MISSING == "EVAL_BASELINE_MISSING"


def test_baseline_invalid():
    assert EVAL_BASELINE_INVALID == "EVAL_BASELINE_INVALID"


def test_policy_denied():
    assert EVAL_POLICY_DENIED == "EVAL_POLICY_DENIED"


def test_tool_adapter_unavailable():
    assert EVAL_TOOL_ADAPTER_UNAVAILABLE == "EVAL_TOOL_ADAPTER_UNAVAILABLE"


def test_tool_call_blocked():
    assert EVAL_TOOL_CALL_BLOCKED == "EVAL_TOOL_CALL_BLOCKED"


def test_report_write_failed():
    assert EVAL_REPORT_WRITE_FAILED == "EVAL_REPORT_WRITE_FAILED"


def test_evidence_write_failed():
    assert EVAL_EVIDENCE_WRITE_FAILED == "EVAL_EVIDENCE_WRITE_FAILED"


def test_source_mutation_detected():
    assert EVAL_SOURCE_MUTATION_DETECTED == "EVAL_SOURCE_MUTATION_DETECTED"


def test_unknown_failure():
    assert EVAL_UNKNOWN_FAILURE == "EVAL_UNKNOWN_FAILURE"


def test_all_failure_classes():
    assert len(ALL_EVAL_FAILURE_CLASSES) == 15
    assert EVAL_FIXTURE_INVALID in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_SUITE_NOT_FOUND in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_CASE_NOT_FOUND in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_CASE_FAILED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_THRESHOLD_FAILED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_REGRESSION_DETECTED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_BASELINE_MISSING in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_BASELINE_INVALID in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_POLICY_DENIED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_TOOL_ADAPTER_UNAVAILABLE in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_TOOL_CALL_BLOCKED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_REPORT_WRITE_FAILED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_EVIDENCE_WRITE_FAILED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_SOURCE_MUTATION_DETECTED in ALL_EVAL_FAILURE_CLASSES
    assert EVAL_UNKNOWN_FAILURE in ALL_EVAL_FAILURE_CLASSES


def test_all_failure_classes_unique():
    assert len(set(ALL_EVAL_FAILURE_CLASSES)) == len(ALL_EVAL_FAILURE_CLASSES)


def test_all_failure_classes_all_strings():
    for cls in ALL_EVAL_FAILURE_CLASSES:
        assert isinstance(cls, str)
        assert cls == cls.upper()


def test_import_all_via_package():
    from agentx_evolve.evaluation import EVAL_FIXTURE_INVALID, EVAL_SUITE_NOT_FOUND
    assert EVAL_FIXTURE_INVALID == "EVAL_FIXTURE_INVALID"
    assert EVAL_SUITE_NOT_FOUND == "EVAL_SUITE_NOT_FOUND"
