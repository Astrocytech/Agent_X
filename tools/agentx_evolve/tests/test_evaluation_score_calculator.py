import pytest
from agentx_evolve.evaluation.score_calculator import (
    calculate_case_score, calculate_run_score, normalize_score,
    calculate_weighted_score,
)
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EvaluationCaseResult, EvaluationScore,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR, EVAL_SKIPPED,
)


def test_calculate_case_score():
    case = BenchmarkCase(case_id="c1", weight=2.0, expected_result={"expected_status": "PASS"})
    result = calculate_case_score(case, {"status": "ok"})
    assert result.case_id == "c1"
    assert result.weight == 2.0
    assert result.expected_result == {"expected_status": "PASS"}


def test_calculate_case_score_zero_weight():
    case = BenchmarkCase(case_id="c1", weight=0.0, expected_result={})
    result = calculate_case_score(case, {})
    assert result.weight == 1.0


def test_calculate_run_score_all_pass():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.total_cases == 2
    assert score.passed_cases == 2
    assert score.failed_cases == 0
    assert score.normalized_score == 1.0
    assert score.weighted_score == 1.0


def test_calculate_run_score_mixed():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0, weight=1.0),
        EvaluationCaseResult(case_id="c3", status=EVAL_BLOCKED, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.total_cases == 3
    assert score.passed_cases == 1
    assert score.failed_cases == 1
    assert score.blocked_cases == 1
    assert score.normalized_score == pytest.approx(1.0 / 3.0)
    assert score.blocked_rate == pytest.approx(1.0 / 3.0)


def test_calculate_run_score_all_skipped():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_SKIPPED, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.skipped_cases == 1
    assert score.pass_rate == 0.0


def test_calculate_run_score_empty():
    score = calculate_run_score([])
    assert score.total_cases == 0
    assert score.normalized_score == 0.0
    assert score.weighted_score == 0.0


def test_calculate_run_score_with_errors():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_ERROR, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.error_cases == 1
    assert score.error_rate == 1.0


def test_calculate_run_score_weighted():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=2.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.weighted_score == pytest.approx(2.0 / 3.0)


def test_normalize_score():
    assert normalize_score(5.0, 10.0) == 0.5
    assert normalize_score(0.0, 10.0) == 0.0
    assert normalize_score(10.0, 10.0) == 1.0


def test_normalize_score_zero_max():
    assert normalize_score(5.0, 0.0) == 0.0


def test_calculate_weighted_score():
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, weight=3.0, score=1.0),
        EvaluationCaseResult(case_id="c2", passed=False, weight=1.0, score=0.0),
    ]
    ws = calculate_weighted_score(results)
    assert ws == pytest.approx(3.0 / 4.0)


def test_calculate_weighted_score_empty():
    assert calculate_weighted_score([]) == 0.0


def test_calculate_weighted_score_all_fail():
    results = [
        EvaluationCaseResult(case_id="c1", passed=False, weight=1.0, score=0.0),
    ]
    assert calculate_weighted_score(results) == 0.0
