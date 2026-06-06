from __future__ import annotations
from pathlib import Path
import json

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationBaseline, RegressionComparison,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    REGRESSION_PASS, REGRESSION_FAIL, REGRESSION_BASELINE_MISSING,
    utc_now_iso, new_eval_id,
)


def compare_against_baseline(
    current_run: EvaluationRun,
    baseline_run: EvaluationRun | None = None,
    first_run: bool = False,
) -> RegressionComparison:
    comparison = RegressionComparison(
        comparison_id=new_eval_id("rc"),
        current_run_id=current_run.run_id,
        timestamp=utc_now_iso(),
    )
    if baseline_run is None:
        if first_run:
            comparison.status = REGRESSION_BASELINE_MISSING
            comparison.warnings.append("First-run mode: no baseline to compare against")
            return comparison
        comparison.status = REGRESSION_BASELINE_MISSING
        comparison.errors.append("Baseline is required but missing")
        return comparison
    comparison.baseline_run_id = baseline_run.run_id
    current_by_id = {r.case_id: r for r in current_run.case_results}
    baseline_by_id = {r.case_id: r for r in baseline_run.case_results}
    all_ids = set(current_by_id.keys()) | set(baseline_by_id.keys())
    for cid in all_ids:
        cur = current_by_id.get(cid)
        base = baseline_by_id.get(cid)
        if cur is None and base is not None:
            comparison.new_failures.append(cid)
            comparison.new_blocked_cases.append(cid)
        elif cur is not None and base is None:
            comparison.fixed_failures.append(cid)
        elif cur and base:
            cur_pass = cur.passed
            base_pass = base.passed
            if cur_pass and not base_pass:
                comparison.fixed_failures.append(cid)
                comparison.improvement_count += 1
            elif not cur_pass and base_pass:
                comparison.new_failures.append(cid)
                comparison.regression_count += 1
            elif not cur_pass and not base_pass:
                comparison.unchanged_failures.append(cid)
            elif cur.status == EVAL_BLOCKED and base.status != EVAL_BLOCKED:
                comparison.new_blocked_cases.append(cid)
            elif cur.status == EVAL_ERROR and base.status != EVAL_ERROR:
                comparison.new_error_cases.append(cid)
    current_score = current_run.score_summary
    baseline_score = baseline_run.score_summary
    if current_score and baseline_score:
        cs = current_score.get("normalized_score", 0) or 0
        bs = baseline_score.get("normalized_score", 0) or 0
        comparison.score_delta = cs - bs
        cws = current_score.get("weighted_score", 0) or 0
        bws = baseline_score.get("weighted_score", 0) or 0
        comparison.weighted_score_delta = cws - bws
    if comparison.regression_count > 0:
        comparison.status = REGRESSION_FAIL
    else:
        comparison.status = REGRESSION_PASS
    return comparison


def load_baseline_run(path: Path) -> EvaluationRun:
    if not path.exists():
        raise FileNotFoundError(f"Baseline run not found: {path}")
    data = json.loads(path.read_text())
    return EvaluationRun(**{k: v for k, v in data.items() if k in EvaluationRun.__dataclass_fields__})


def find_new_failures(current: EvaluationRun, baseline: EvaluationRun) -> list[str]:
    comp = compare_against_baseline(current, baseline)
    return comp.new_failures


def find_fixed_failures(current: EvaluationRun, baseline: EvaluationRun) -> list[str]:
    comp = compare_against_baseline(current, baseline)
    return comp.fixed_failures


def calculate_score_delta(current: EvaluationRun, baseline: EvaluationRun) -> dict:
    comp = compare_against_baseline(current, baseline)
    return {
        "score_delta": comp.score_delta,
        "weighted_score_delta": comp.weighted_score_delta,
    }
