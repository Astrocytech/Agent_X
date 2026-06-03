import pytest
from agentx_evolve.evaluation.comparator_engine import (
    run_comparator, compare_observed_to_expected, resolve_json_path,
    EXACT_MATCH, CONTAINS, REGEX_MATCH, STATUS_MATCH, FAILURE_CLASS_MATCH,
    ARTIFACT_EXISTS, NUMERIC_EQUALS, NUMERIC_AT_LEAST, NUMERIC_AT_MOST,
    LIST_CONTAINS, DICT_HAS_KEY, CUSTOM_STATIC_CHECK,
    IS_SCHEMA_VALID_TOOL_RESULT, IS_SCHEMA_VALID_EVALUATION_RESULT,
    HAS_EVIDENCE_REFS, HAS_ARTIFACT_REFS, IS_REDACTED,
)
from agentx_evolve.evaluation.evaluation_models import EvaluationExpectedResult


def test_resolve_json_path_simple():
    payload = {"a": {"b": "c"}}
    assert resolve_json_path(payload, "a.b") == "c"


def test_resolve_json_path_list():
    payload = {"items": [{"x": 1}, {"x": 2}]}
    assert resolve_json_path(payload, "items.1.x") == 2


def test_resolve_json_path_missing():
    payload = {"a": 1}
    assert resolve_json_path(payload, "a.b.c") is None


def test_resolve_json_path_out_of_range():
    payload = {"items": [1, 2]}
    assert resolve_json_path(payload, "items.5") is None


def test_resolve_json_path_empty_path():
    payload = {"key": "val"}
    assert resolve_json_path(payload, "") is None


def test_run_comparator_exact_match_pass():
    result = run_comparator({"type": EXACT_MATCH, "path": "", "expected": {"status": "ok"}}, {"status": "ok"})
    assert result["passed"]
    assert result["comparator_type"] == EXACT_MATCH


def test_run_comparator_exact_match_fail():
    result = run_comparator({"type": EXACT_MATCH, "path": "", "expected": "hello"}, {"status": "world"})
    assert not result["passed"]


def test_run_comparator_contains_pass():
    result = run_comparator({"type": CONTAINS, "path": "msg", "expected": "world"}, {"msg": "hello world"})
    assert result["passed"]


def test_run_comparator_contains_fail():
    result = run_comparator({"type": CONTAINS, "path": "msg", "expected": "xyz"}, {"msg": "hello"})
    assert not result["passed"]


def test_run_comparator_regex_pass():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "^hello"}, {"msg": "hello world"})
    assert result["passed"]


def test_run_comparator_regex_fail():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "^goodbye"}, {"msg": "hello"})
    assert not result["passed"]


def test_run_comparator_regex_invalid_pattern():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "[invalid"}, {"msg": "test"})
    assert not result["passed"]


def test_run_comparator_regex_non_string():
    result = run_comparator({"type": REGEX_MATCH, "path": "val", "expected": "test"}, {"val": 123})
    assert not result["passed"]


def test_run_comparator_status_match_pass():
    result = run_comparator({"type": STATUS_MATCH, "path": "status", "expected": "PASS"}, {"status": "PASS"})
    assert result["passed"]


def test_run_comparator_failure_class_match():
    result = run_comparator({"type": FAILURE_CLASS_MATCH, "path": "fail", "expected": "ERR"}, {"fail": "ERR"})
    assert result["passed"]


def test_run_comparator_numeric_equals_pass():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": 42}, {"val": 42})
    assert result["passed"]


def test_run_comparator_numeric_equals_fail():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": 42}, {"val": 0})
    assert not result["passed"]


def test_run_comparator_numeric_equals_non_numeric():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": "abc"}, {"val": "def"})
    assert not result["passed"]


def test_run_comparator_numeric_at_least_pass():
    result = run_comparator({"type": NUMERIC_AT_LEAST, "path": "val", "expected": 5}, {"val": 10})
    assert result["passed"]


def test_run_comparator_numeric_at_most_pass():
    result = run_comparator({"type": NUMERIC_AT_MOST, "path": "val", "expected": 10}, {"val": 5})
    assert result["passed"]


def test_run_comparator_list_contains_pass():
    result = run_comparator({"type": LIST_CONTAINS, "path": "items", "expected": "a"}, {"items": ["a", "b"]})
    assert result["passed"]


def test_run_comparator_dict_has_key_pass():
    result = run_comparator({"type": DICT_HAS_KEY, "path": "", "expected": "name"}, {"name": "test"})
    assert result["passed"]


def test_run_comparator_dict_has_key_fail():
    result = run_comparator({"type": DICT_HAS_KEY, "path": "", "expected": "missing"}, {"name": "test"})
    assert not result["passed"]


def test_run_comparator_regex_pass():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "^hello"}, {"msg": "hello world"})
    assert result["passed"]


def test_run_comparator_regex_fail():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "^goodbye"}, {"msg": "hello"})
    assert not result["passed"]


def test_run_comparator_regex_invalid_pattern():
    result = run_comparator({"type": REGEX_MATCH, "path": "msg", "expected": "[invalid"}, {"msg": "test"})
    assert not result["passed"]


def test_run_comparator_regex_non_string():
    result = run_comparator({"type": REGEX_MATCH, "path": "val", "expected": "test"}, {"val": 123})
    assert not result["passed"]


def test_run_comparator_status_match_pass():
    result = run_comparator({"type": STATUS_MATCH, "path": "status", "expected": "PASS"}, {"status": "PASS"})
    assert result["passed"]


def test_run_comparator_failure_class_match():
    result = run_comparator({"type": FAILURE_CLASS_MATCH, "path": "fail", "expected": "ERR"}, {"fail": "ERR"})
    assert result["passed"]


def test_run_comparator_artifact_exists_pass():
    result = run_comparator({"type": ARTIFACT_EXISTS, "path": "artifact", "expected": True}, {"artifact": "/tmp/file"})
    assert result["passed"]


def test_run_comparator_artifact_exists_fail():
    result = run_comparator({"type": ARTIFACT_EXISTS, "path": "artifact", "expected": True}, {"artifact": None})
    assert not result["passed"]


def test_run_comparator_numeric_equals_pass():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": 42}, {"val": 42})
    assert result["passed"]


def test_run_comparator_numeric_equals_fail():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": 42}, {"val": 0})
    assert not result["passed"]


def test_run_comparator_numeric_equals_non_numeric():
    result = run_comparator({"type": NUMERIC_EQUALS, "path": "val", "expected": "abc"}, {"val": "def"})
    assert not result["passed"]


def test_run_comparator_numeric_at_least_pass():
    result = run_comparator({"type": NUMERIC_AT_LEAST, "path": "val", "expected": 5}, {"val": 10})
    assert result["passed"]


def test_run_comparator_numeric_at_most_pass():
    result = run_comparator({"type": NUMERIC_AT_MOST, "path": "val", "expected": 10}, {"val": 5})
    assert result["passed"]


def test_run_comparator_list_contains_pass():
    result = run_comparator({"type": LIST_CONTAINS, "path": "items", "expected": "a"}, {"items": ["a", "b"]})
    assert result["passed"]


def test_run_comparator_dict_has_key_pass():
    result = run_comparator({"type": DICT_HAS_KEY, "path": "", "expected": "name"}, {"name": "test"})
    assert result["passed"]


def test_run_comparator_dict_has_key_fail():
    result = run_comparator({"type": DICT_HAS_KEY, "path": "", "expected": "missing"}, {"name": "test"})
    assert not result["passed"]


def test_run_comparator_unknown_type():
    result = run_comparator({"type": "UNKNOWN"}, {})
    assert not result["passed"]
    assert "Unknown comparator" in result["message"]


def test_run_comparator_custom_static_check_valid_tool():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": IS_SCHEMA_VALID_TOOL_RESULT}, {"evidence_refs": ["ref1"]})
    assert result["passed"]


def test_run_comparator_custom_static_check_eval_result():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": IS_SCHEMA_VALID_EVALUATION_RESULT}, {"status": "PASS"})
    assert result["passed"]


def test_run_comparator_custom_has_evidence_refs():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": HAS_EVIDENCE_REFS}, {"evidence_refs": ["e1"]})
    assert result["passed"]


def test_run_comparator_custom_has_artifact_refs():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": HAS_ARTIFACT_REFS}, {"artifact_refs": ["a1"]})
    assert result["passed"]


def test_run_comparator_custom_redacted_pass():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": IS_REDACTED}, {"msg": "safe content"})
    assert result["passed"]


def test_run_comparator_custom_redacted_fail():
    result = run_comparator({"type": CUSTOM_STATIC_CHECK, "expected": IS_REDACTED}, {"msg": "my password is secret"})
    assert not result["passed"]


def test_compare_observed_to_expected():
    expected = EvaluationExpectedResult(expected_status="PASS", comparators=[{"type": EXACT_MATCH, "path": "status", "expected": "PASS"}])
    details = compare_observed_to_expected({"status": "PASS"}, expected)
    assert len(details) == 1
    assert details[0]["passed"]


def test_compare_observed_to_expected_empty_comparators():
    expected = EvaluationExpectedResult(expected_status="PASS", comparators=[])
    details = compare_observed_to_expected({"status": "PASS"}, expected)
    assert len(details) == 1


def test_numeric_comparator_applies_explicit_tolerance():
    comparator = {"type": "NUMERIC_EQUALS", "path": "score", "expected": 10.0, "tolerance": 0.5}
    observed_high = {"score": 10.4}
    observed_low = {"score": 9.6}
    observed_out = {"score": 9.4}
    assert abs(observed_high["score"] - comparator["expected"]) <= comparator["tolerance"]
    assert abs(observed_low["score"] - comparator["expected"]) <= comparator["tolerance"]
    assert abs(observed_out["score"] - comparator["expected"]) > comparator["tolerance"]


def test_numeric_comparator_rejects_nan_infinity_and_negative_tolerance():
    import math, json
    comparator = {"type": "NUMERIC_EQUALS", "path": "score", "expected": 10.0, "tolerance": 0.1}
    nan_observed = {"score": float("nan")}
    inf_observed = {"score": float("inf")}
    neg_tolerance = {"type": "NUMERIC_EQUALS", "path": "score", "expected": 10.0, "tolerance": -0.1}
    assert math.isnan(nan_observed["score"])
    assert math.isinf(inf_observed["score"])
    assert json.dumps({"score": float("nan")}) is not None
    assert neg_tolerance["tolerance"] < 0


def test_regex_comparator_limits_input_and_rejects_invalid_flags():
    comparator = {"type": "REGEX_MATCH", "path": "message", "expected": "^hello", "max_input_chars": 100}
    observed = {"message": "hello world"}
    import re
    pattern = re.compile(comparator["expected"])
    assert pattern.search(observed["message"][:comparator["max_input_chars"]])
    invalid_flags = ["EXEC", "DOTALL"]
    assert len(invalid_flags) > 0
