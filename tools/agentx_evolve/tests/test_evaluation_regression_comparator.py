import pytest
import json
from pathlib import Path
from agentx_evolve.evaluation.regression_comparator import (
    compare_against_baseline, load_baseline_run,
    find_new_failures, find_fixed_failures, calculate_score_delta,
)
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationCaseResult, RegressionComparison,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    REGRESSION_PASS, REGRESSION_FAIL, REGRESSION_BASELINE_MISSING,
)


def make_run(run_id="run-1", suite_id="suite-1", results=None, score=None):
    return EvaluationRun(
        run_id=run_id,
        suite_id=suite_id,
        case_results=results or [],
        score_summary=score or {"normalized_score": 1.0, "weighted_score": 1.0, "status": "PASS"},
    )


def test_compare_against_baseline_no_baseline_first_run():
    current = make_run()
    comp = compare_against_baseline(current, first_run=True)
    assert comp.status == REGRESSION_BASELINE_MISSING
    assert "First-run mode" in " ".join(comp.warnings)


def test_compare_against_baseline_no_baseline():
    current = make_run()
    comp = compare_against_baseline(current, first_run=False)
    assert comp.status == REGRESSION_BASELINE_MISSING
    assert len(comp.errors) > 0


def test_compare_against_baseline_no_regression():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert comp.status == REGRESSION_PASS
    assert comp.regression_count == 0


def test_compare_against_baseline_new_failure():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert comp.status == REGRESSION_FAIL
    assert comp.regression_count == 1
    assert "c1" in comp.new_failures


def test_compare_against_baseline_fixed_failure():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert comp.improvement_count == 1
    assert "c1" in comp.fixed_failures


def test_compare_against_baseline_unchanged_failure():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert "c1" in comp.unchanged_failures


def test_compare_against_baseline_new_case_in_current():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_PASS, passed=True, score=1.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert "c2" in comp.fixed_failures or "c2" not in comp.new_failures


def test_compare_against_baseline_case_removed():
    current_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ]
    baseline_results = [
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
        EvaluationCaseResult(case_id="c2", status=EVAL_PASS, passed=True, score=1.0),
    ]
    current = make_run(results=current_results)
    baseline = make_run(run_id="baseline-1", results=baseline_results)
    comp = compare_against_baseline(current, baseline)
    assert "c2" in comp.new_failures or "c2" in comp.new_blocked_cases


def test_compare_against_baseline_score_delta():
    current = make_run(score={"normalized_score": 0.8, "weighted_score": 0.7})
    baseline = make_run(run_id="baseline-1", score={"normalized_score": 1.0, "weighted_score": 0.9})
    comp = compare_against_baseline(current, baseline)
    assert comp.score_delta == pytest.approx(-0.2)
    assert comp.weighted_score_delta == pytest.approx(-0.2)


def test_load_baseline_run(tmp_path):
    data = {"run_id": "bl-1", "suite_id": "s1", "case_results": []}
    p = tmp_path / "baseline.json"
    p.write_text(json.dumps(data))
    run = load_baseline_run(p)
    assert run.run_id == "bl-1"
    assert isinstance(run, EvaluationRun)


def test_load_baseline_run_not_found():
    with pytest.raises(FileNotFoundError):
        load_baseline_run(Path("/missing/baseline.json"))


def test_find_new_failures():
    current = make_run(results=[
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ])
    baseline = make_run(run_id="bl-1", results=[
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ])
    failures = find_new_failures(current, baseline)
    assert "c1" in failures


def test_find_fixed_failures():
    current = make_run(results=[
        EvaluationCaseResult(case_id="c1", status=EVAL_PASS, passed=True, score=1.0),
    ])
    baseline = make_run(run_id="bl-1", results=[
        EvaluationCaseResult(case_id="c1", status=EVAL_FAIL, passed=False, score=0.0),
    ])
    fixed = find_fixed_failures(current, baseline)
    assert "c1" in fixed


def test_calculate_score_delta():
    current = make_run(score={"normalized_score": 0.9, "weighted_score": 0.8})
    baseline = make_run(run_id="bl-1", score={"normalized_score": 0.7, "weighted_score": 0.6})
    delta = calculate_score_delta(current, baseline)
    assert delta["score_delta"] == pytest.approx(0.2)
    assert delta["weighted_score_delta"] == pytest.approx(0.2)
