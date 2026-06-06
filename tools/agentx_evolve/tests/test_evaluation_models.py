import pytest
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkSuite, BenchmarkCase, EvaluationCaseInput, EvaluationExpectedResult,
    EvaluationCaseResult, EvaluationRun, EvaluationScore, EvaluationThreshold,
    RegressionComparison, EvaluationReport, EvaluationBaseline,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR, EVAL_SKIPPED,
    REGRESSION_PASS, REGRESSION_FAIL, REGRESSION_BASELINE_MISSING, REGRESSION_NOT_APPLICABLE,
    THRESHOLD_PASS, THRESHOLD_FAIL,
    ALL_EVAL_STATUSES, ALL_CASE_TYPES, ALL_COMPARATOR_TYPES, ALL_STATIC_CHECKS,
    STATIC_EXPECTED_RESULT, TOOL_CALL_EXPECTED_RESULT, POLICY_DENIAL_EXPECTED_RESULT,
    REGRESSION_EXPECTED_FAILURE, ARTIFACT_EXPECTED_RESULT, REPORT_GENERATION_EXPECTED_RESULT,
    NEGATIVE_FIXTURE_VALIDATION,
    EXACT_MATCH, CONTAINS, REGEX_MATCH, STATUS_MATCH, FAILURE_CLASS_MATCH,
    ARTIFACT_EXISTS, NUMERIC_EQUALS, NUMERIC_AT_LEAST, NUMERIC_AT_MOST,
    LIST_CONTAINS, DICT_HAS_KEY, CUSTOM_STATIC_CHECK,
    IS_SCHEMA_VALID_TOOL_RESULT, IS_SCHEMA_VALID_EVALUATION_RESULT,
    HAS_EVIDENCE_REFS, HAS_ARTIFACT_REFS, IS_REDACTED,
    utc_now_iso, new_eval_id, stable_json_hash, to_dict,
)


def test_eval_status_constants():
    assert EVAL_PASS == "EVAL_PASS"
    assert EVAL_FAIL == "EVAL_FAIL"
    assert EVAL_BLOCKED == "EVAL_BLOCKED"
    assert EVAL_ERROR == "EVAL_ERROR"
    assert EVAL_SKIPPED == "EVAL_SKIPPED"


def test_regression_constants():
    assert REGRESSION_PASS == "REGRESSION_PASS"
    assert REGRESSION_FAIL == "REGRESSION_FAIL"
    assert REGRESSION_BASELINE_MISSING == "REGRESSION_BASELINE_MISSING"
    assert REGRESSION_NOT_APPLICABLE == "REGRESSION_NOT_APPLICABLE"


def test_threshold_constants():
    assert THRESHOLD_PASS == "THRESHOLD_PASS"
    assert THRESHOLD_FAIL == "THRESHOLD_FAIL"


def test_all_eval_statuses():
    assert len(ALL_EVAL_STATUSES) == 11
    assert EVAL_PASS in ALL_EVAL_STATUSES


def test_all_case_types():
    assert len(ALL_CASE_TYPES) == 7
    assert STATIC_EXPECTED_RESULT in ALL_CASE_TYPES


def test_all_comparator_types():
    assert len(ALL_COMPARATOR_TYPES) == 12
    assert EXACT_MATCH in ALL_COMPARATOR_TYPES


def test_all_static_checks():
    assert len(ALL_STATIC_CHECKS) == 5
    assert IS_REDACTED in ALL_STATIC_CHECKS


def test_benchmark_suite_defaults():
    s = BenchmarkSuite()
    assert s.suite_id == ""
    assert s.case_refs == []
    assert s.warnings == []
    assert s.errors == []


def test_benchmark_suite_with_values():
    s = BenchmarkSuite(suite_id="s1", suite_name="Test", case_refs=["a.json"])
    assert s.suite_id == "s1"
    assert len(s.case_refs) == 1


def test_benchmark_case_defaults():
    c = BenchmarkCase()
    assert c.case_id == ""
    assert c.input_payload == {}
    assert c.expected_result == {}
    assert c.severity == "normal"
    assert c.weight == 1.0


def test_benchmark_case_with_values():
    c = BenchmarkCase(case_id="c1", case_type="STATIC_EXPECTED_RESULT", weight=2.0, severity="critical")
    assert c.case_id == "c1"
    assert c.weight == 2.0
    assert c.severity == "critical"


def test_evaluation_case_result_defaults():
    r = EvaluationCaseResult()
    assert r.score == 0.0
    assert not r.passed
    assert r.comparison_details == []


def test_evaluation_case_result_with_values():
    r = EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)
    assert r.passed
    assert r.score == 1.0


def test_evaluation_run_defaults():
    r = EvaluationRun()
    assert r.runner_version == "1.0.0"
    assert r.execution_mode == "OFFLINE_FIXTURE"
    assert r.case_results == []


def test_evaluation_score_defaults():
    s = EvaluationScore()
    assert s.total_cases == 0
    assert s.raw_score == 0.0


def test_evaluation_threshold_defaults():
    t = EvaluationThreshold()
    assert t.minimum_pass_rate == 1.0
    assert t.maximum_error_count == 0


def test_regression_comparison_defaults():
    rc = RegressionComparison()
    assert rc.regression_count == 0
    assert rc.new_failures == []


def test_evaluation_report_defaults():
    r = EvaluationReport()
    assert r.case_summaries == []
    assert r.status == ""


def test_evaluation_baseline_defaults():
    b = EvaluationBaseline()
    assert b.baseline_id == ""
    assert b.case_result_index == {}


def test_utc_now_iso_format():
    now = utc_now_iso()
    assert "T" in now
    assert now.endswith("+00:00") or "+" in now


def test_new_eval_id_format():
    eid = new_eval_id("test")
    assert eid.startswith("test-")
    assert len(eid) > 10


def test_new_eval_id_default_prefix():
    eid = new_eval_id()
    assert eid.startswith("eval-")


def test_stable_json_hash():
    h1 = stable_json_hash({"b": 2, "a": 1})
    h2 = stable_json_hash({"a": 1, "b": 2})
    assert h1 == h2
    assert len(h1) == 64


def test_stable_json_hash_different():
    h1 = stable_json_hash({"a": 1})
    h2 = stable_json_hash({"a": 2})
    assert h1 != h2


def test_to_dict_dataclass():
    case = EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True)
    d = to_dict(case)
    assert d["case_id"] == "c1"
    assert d["status"] == EVAL_PASS


def test_to_dict_nested():
    case = EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True)
    run = EvaluationRun(run_id="r1", case_results=[case])
    d = to_dict(run)
    assert d["run_id"] == "r1"
    assert len(d["case_results"]) == 1
    assert d["case_results"][0]["case_id"] == "c1"


def test_evaluation_case_input_defaults():
    inp = EvaluationCaseInput()
    assert inp.input_id == ""
    assert inp.payload == {}


def test_evaluation_expected_result_defaults():
    er = EvaluationExpectedResult()
    assert er.expected_status == ""
    assert er.comparators == []
