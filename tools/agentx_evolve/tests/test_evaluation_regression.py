import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.regression_comparator import (
    compare_against_baseline, find_new_failures, find_fixed_failures,
    calculate_score_delta,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationCaseResult,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    REGRESSION_PASS, REGRESSION_FAIL,
)


def make_run(run_id="r1", suite_id="s1", results=None, score=None):
    return EvaluationRun(
        run_id=run_id, suite_id=suite_id,
        case_results=results or [],
        score_summary=score or {"normalized_score": 1.0, "weighted_score": 1.0, "status": "PASS"},
    )


def test_regression_detection_new_failure():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    comp = compare_against_baseline(current, baseline)
    assert comp.status == REGRESSION_FAIL
    assert comp.regression_count == 1


def test_regression_detection_no_change():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    comp = compare_against_baseline(current, baseline)
    assert comp.status == REGRESSION_PASS
    assert comp.regression_count == 0


def test_regression_detection_improvement():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    comp = compare_against_baseline(current, baseline)
    assert comp.improvement_count == 1
    assert "c1" in comp.fixed_failures


def test_regression_detection_unchanged_failure():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    comp = compare_against_baseline(current, baseline)
    assert "c1" in comp.unchanged_failures


def test_regression_with_blocked_status():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_BLOCKED, passed=False, score=0.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    comp = compare_against_baseline(current, baseline)
    assert comp.regression_count == 1
    assert "c1" in comp.new_failures


def test_regression_with_error_status():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_ERROR, passed=False, score=0.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    comp = compare_against_baseline(current, baseline)
    assert comp.regression_count == 1
    assert "c1" in comp.new_failures


def test_find_new_failures_helper():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    failures = find_new_failures(current, baseline)
    assert "c1" in failures


def test_find_fixed_failures_helper():
    current = make_run(results=[EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0)])
    baseline = make_run(run_id="bl", results=[EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0)])
    fixed = find_fixed_failures(current, baseline)
    assert "c1" in fixed


def test_calculate_score_delta_helper():
    current = make_run(score={"normalized_score": 0.5, "weighted_score": 0.4})
    baseline = make_run(run_id="bl", score={"normalized_score": 0.8, "weighted_score": 0.9})
    delta = calculate_score_delta(current, baseline)
    assert delta["score_delta"] == pytest.approx(-0.3)
    assert delta["weighted_score_delta"] == pytest.approx(-0.5)


def test_regression_full_pipeline(tmp_path):
    suite_path = tmp_path / "suite.json"
    suite_path.write_text(json.dumps({
        "suite_id": "s1",
        "case_refs": [],
        "baseline_ref": "baselines/baseline.json",
        "first_run_allowed": True,
        "default_threshold_id": None,
    }))
    baselines_dir = tmp_path / "baselines"
    baselines_dir.mkdir(exist_ok=True)
    baseline_data = {
        "run_id": "bl-1", "suite_id": "s1",
        "case_results": [],
        "score_summary": {"normalized_score": 1.0, "weighted_score": 1.0},
    }
    (baselines_dir / "baseline.json").write_text(json.dumps(baseline_data))
    from agentx_evolve.evaluation.evaluation_runner import run_evaluation
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert run.regression_summary is not None
