import pytest
from agentx_evolve.evaluation.threshold_checker import (
    check_thresholds, check_required_cases,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationScore, EvaluationThreshold, EvaluationCaseResult, RegressionComparison,
    EVAL_PASS, EVAL_FAIL,
)


def make_score(pass_rate=1.0, weighted_score=1.0, blocked=0, errors=0, total=2):
    return EvaluationScore(
        total_cases=total, passed_cases=int(total * pass_rate),
        pass_rate=pass_rate, weighted_score=weighted_score,
        blocked_cases=blocked, error_cases=errors,
    )


def make_threshold(**overrides):
    params = {
        "threshold_id": "th-1", "minimum_pass_rate": 1.0,
        "minimum_weighted_score": 1.0, "allow_blocked_cases": False,
        "allow_error_cases": False, "maximum_blocked_count": 0,
        "maximum_error_count": 0, "maximum_regression_count": 0,
        "required_case_ids": [],
    }
    params.update(overrides)
    return EvaluationThreshold(**params)


def test_check_thresholds_pass():
    score = make_score()
    th = make_threshold()
    result = check_thresholds(score, th, [])
    assert result["passed"]
    assert len(result["checks"]) > 0


def test_check_thresholds_fail_pass_rate():
    score = make_score(pass_rate=0.5, weighted_score=0.5)
    th = make_threshold(minimum_pass_rate=0.8)
    result = check_thresholds(score, th, [])
    assert not result["passed"]
    assert any(c["check"] == "minimum_pass_rate" and not c["passed"] for c in result["checks"])


def test_check_thresholds_fail_weighted_score():
    score = make_score(weighted_score=0.5)
    th = make_threshold(minimum_weighted_score=0.9)
    result = check_thresholds(score, th, [])
    assert not result["passed"]
    assert any(c["check"] == "minimum_weighted_score" and not c["passed"] for c in result["checks"])


def test_check_thresholds_blocked_cases_exceeded():
    score = make_score(blocked=3)
    th = make_threshold(allow_blocked_cases=True, maximum_blocked_count=1)
    result = check_thresholds(score, th, [])
    assert not result["passed"]
    assert any(c["check"] == "maximum_blocked_count" and not c["passed"] for c in result["checks"])


def test_check_thresholds_blocked_allowed():
    score = make_score(blocked=1)
    th = make_threshold(allow_blocked_cases=True, maximum_blocked_count=2)
    result = check_thresholds(score, th, [])
    checks = {c["check"]: c["passed"] for c in result["checks"]}
    assert checks.get("maximum_blocked_count", True)


def test_check_thresholds_errors_exceeded():
    score = make_score(errors=2)
    th = make_threshold(allow_error_cases=True, maximum_error_count=0)
    result = check_thresholds(score, th, [])
    assert not result["passed"]


def test_check_thresholds_regression_exceeded():
    score = make_score()
    th = make_threshold(maximum_regression_count=0)
    regression = RegressionComparison(regression_count=2, status="REGRESSION_FAIL")
    result = check_thresholds(score, th, [], regression)
    assert not result["passed"]
    assert any(c["check"] == "maximum_regression_count" and not c["passed"] for c in result["checks"])


def test_check_thresholds_no_regression_skip():
    score = make_score()
    th = make_threshold()
    result = check_thresholds(score, th, [])
    assert all(c["check"] != "maximum_regression_count" for c in result["checks"])


def test_check_thresholds_required_case_ids_pass():
    score = make_score()
    th = make_threshold(required_case_ids=["c1", "c2"])
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS),
        EvaluationCaseResult(case_id="c2", passed=True, status=EVAL_PASS),
    ]
    result = check_thresholds(score, th, results)
    checks = {c["check"]: c["passed"] for c in result["checks"]}
    assert checks.get("required_case_ids", True)


def test_check_thresholds_required_case_ids_fail():
    score = make_score()
    th = make_threshold(required_case_ids=["c1", "c2", "c3"])
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS),
    ]
    result = check_thresholds(score, th, results)
    assert not result["passed"]
    assert any(c["check"] == "required_case_ids" and not c["passed"] for c in result["checks"])


def test_check_thresholds_error_code_in_result():
    score = make_score(pass_rate=0.0, weighted_score=0.0)
    th = make_threshold(minimum_pass_rate=1.0)
    result = check_thresholds(score, th, [])
    assert "EVAL_THRESHOLD_FAILED" in result["errors"]


def test_check_required_cases_pass():
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS),
        EvaluationCaseResult(case_id="c2", passed=True, status=EVAL_PASS),
    ]
    result = check_required_cases(results, ["c1", "c2"])
    assert result["passed"]
    assert result["missing"] == []


def test_check_required_cases_fail():
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS),
    ]
    result = check_required_cases(results, ["c1", "c2"])
    assert not result["passed"]
    assert result["missing"] == ["c2"]


def test_check_required_cases_empty_results():
    result = check_required_cases([], ["c1"])
    assert not result["passed"]


def test_check_required_cases_empty_requirements():
    result = check_required_cases([EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS)], [])
    assert result["passed"]


def test_check_required_cases_missing_required():
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, status=EVAL_PASS),
        EvaluationCaseResult(case_id="c2", passed=False, status=EVAL_FAIL),
    ]
    result = check_required_cases(results, ["c1", "c2"])
    assert result["missing"] == ["c2"]
