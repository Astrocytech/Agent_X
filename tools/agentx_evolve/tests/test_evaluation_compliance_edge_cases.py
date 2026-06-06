import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationCaseResult, EvaluationScore,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
)
from agentx_evolve.evaluation.score_calculator import calculate_run_score
from agentx_evolve.evaluation.threshold_checker import check_thresholds
from agentx_evolve.evaluation.evaluation_models import EvaluationThreshold
from agentx_evolve.evaluation.regression_comparator import compare_against_baseline
from agentx_evolve.evaluation.evaluation_models import EvaluationRun


def test_empty_case_list_produces_zero_score():
    score = calculate_run_score([])
    assert score.total_cases == 0
    assert score.pass_rate == 0.0
    assert score.normalized_score == 0.0


def test_all_blocked_run_produces_zero_pass_rate():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_BLOCKED, passed=False, score=0.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_BLOCKED, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.pass_rate == 0.0
    assert score.blocked_cases == 2


def test_all_error_run_produces_zero_pass_rate():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_ERROR, passed=False, score=0.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_ERROR, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.pass_rate == 0.0
    assert score.error_cases == 2


def test_mix_of_pass_fail_blocked_error_produces_correct_counts():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0, weight=1.0),
        EvaluationCaseResult(case_id="c3", status=EVAL_BLOCKED, passed=False, score=0.0, weight=1.0),
        EvaluationCaseResult(case_id="c4", status=EVAL_ERROR, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.total_cases == 4
    assert score.passed_cases == 1
    assert score.failed_cases == 1
    assert score.blocked_cases == 1
    assert score.error_cases == 1
    assert score.pass_rate == 0.25


def test_very_large_weight_values_handled_correctly():
    results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0, weight=1e6),
        EvaluationCaseResult(case_id="c2", status=EVAL_FAIL, passed=False, score=0.0, weight=1.0),
    ]
    score = calculate_run_score(results)
    assert score.weighted_score == pytest.approx(1e6 / (1e6 + 1.0))


def test_threshold_with_maximum_values_does_not_overflow():
    score = EvaluationScore(
        total_cases=1000, passed_cases=1000, pass_rate=1.0,
        weighted_score=1.0, blocked_cases=0, error_cases=0,
    )
    th = EvaluationThreshold(
        threshold_id="th-max", minimum_pass_rate=1.0, minimum_weighted_score=1.0,
        maximum_blocked_count=1000000, maximum_error_count=1000000,
        maximum_regression_count=1000000,
    )
    result = check_thresholds(score, th, [])
    assert result["passed"]


def test_regression_comparison_with_no_cases():
    current = EvaluationRun(
        run_id="r1", suite_id="s1",
        case_results=[],
        score_summary={"normalized_score": 0.0, "weighted_score": 0.0},
    )
    baseline = EvaluationRun(
        run_id="bl", suite_id="s1",
        case_results=[],
        score_summary={"normalized_score": 0.0, "weighted_score": 0.0},
    )
    comp = compare_against_baseline(current, baseline)
    assert comp.regression_count == 0
    assert comp.new_failures == []
    assert comp.fixed_failures == []
