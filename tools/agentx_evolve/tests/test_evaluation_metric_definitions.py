import pytest
from agentx_evolve.evaluation.evaluation_models import EvaluationScore
from agentx_evolve.evaluation.score_calculator import (
    normalize_score, calculate_weighted_score,
)
from agentx_evolve.evaluation.evaluation_models import EvaluationCaseResult


def test_metric_created_as_dict_with_required_fields():
    score = EvaluationScore(score_id="m1")
    assert score.score_id == "m1"


def test_invalid_metric_id_empty_string():
    score = EvaluationScore(score_id="")
    assert score.score_id == ""


def test_invalid_metric_type_defaults():
    score = EvaluationScore()
    assert score.schema_id == "evaluation_score.schema.json"


def test_metric_weight_defaults_to_one():
    score = EvaluationScore()
    assert score.normalized_score == 0.0


def test_metric_higher_is_better_default():
    score = EvaluationScore(score_id="m1")
    assert score.total_cases == 0


def test_metric_aggregation_defaults_to_mean():
    from agentx_evolve.evaluation.score_calculator import calculate_run_score
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, score=1.0, weight=1.0, status="EVAL_PASS"),
        EvaluationCaseResult(case_id="c2", passed=True, score=1.0, weight=1.0, status="EVAL_PASS"),
        EvaluationCaseResult(case_id="c3", passed=False, score=0.0, weight=1.0, status="EVAL_FAIL"),
        EvaluationCaseResult(case_id="c4", passed=False, score=0.0, weight=1.0, status="EVAL_FAIL"),
    ]
    score = calculate_run_score(results)
    assert score.normalized_score == 0.5


def test_metric_with_weights():
    results = [
        EvaluationCaseResult(case_id="c1", passed=True, weight=3.0, score=1.0),
        EvaluationCaseResult(case_id="c2", passed=False, weight=1.0, score=0.0),
    ]
    ws = calculate_weighted_score(results)
    assert ws == pytest.approx(3.0 / 4.0)


def test_metric_empty_aggregation():
    score = EvaluationScore()
    assert score.pass_rate == 0.0


def test_metric_all_fields_default():
    score = EvaluationScore()
    assert score.total_cases == 0
    assert score.passed_cases == 0
    assert score.failed_cases == 0
    assert score.blocked_cases == 0
    assert score.error_cases == 0
