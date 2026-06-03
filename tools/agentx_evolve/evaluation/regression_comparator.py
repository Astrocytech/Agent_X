from __future__ import annotations
from pathlib import Path
import json

from agentx_evolve.evaluation.evaluation_models import (
    EvaluationRun, EvaluationBaseline, RegressionComparison,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    REGRESSION_PASS, REGRESSION_FAIL, REGRESSION_BASELINE_MISSING,
    utc_now_iso, new_eval_id,
)
from agentx_evolve.evaluation.evaluation_errors import (
    EVAL_BASELINE_SCHEMA_INVALID, EVAL_BASELINE_SUITE_MISMATCH,
    EVAL_BASELINE_CASE_MISMATCH, EVAL_BASELINE_VERSION_UNSUPPORTED,
)


def check_baseline_compatibility(
    current_run: EvaluationRun,
    baseline_run: EvaluationRun,
    current_suite_id: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if current_suite_id and baseline_run.suite_id != current_suite_id:
        errors.append(EVAL_BASELINE_SUITE_MISMATCH)
    baseline_schema = getattr(baseline_run, "schema_version", None) or ""
    current_schema = getattr(current_run, "schema_version", None) or ""
    if baseline_schema and current_schema:
        base_parts = [int(p) for p in baseline_schema.split(".")[:2]]
        curr_parts = [int(p) for p in current_schema.split(".")[:2]]
        if curr_parts[0] > base_parts[0]:
            errors.append(EVAL_BASELINE_VERSION_UNSUPPORTED)
    current_case_ids = {r.case_id for r in current_run.case_results}
    baseline_case_ids = {r.case_id for r in baseline_run.case_results}
    missing_in_baseline = current_case_ids - baseline_case_ids
    if missing_in_baseline:
        errors.append(f"{EVAL_BASELINE_CASE_MISMATCH}: cases {sorted(missing_in_baseline)} not in baseline")
    return errors


def compare_against_baseline(
    current_run: EvaluationRun,
    baseline_run: EvaluationRun | None = None,
    first_run: bool = False,
    current_suite_id: str | None = None,
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
    compat_errors = check_baseline_compatibility(current_run, baseline_run, current_suite_id)
    if compat_errors:
        comparison.status = REGRESSION_FAIL
        comparison.errors.extend(compat_errors)
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
