from __future__ import annotations
import math
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EvaluationCaseResult, EvaluationScore,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR, EVAL_SKIPPED,
    new_eval_id,
)
from agentx_evolve.evaluation.evaluation_errors import EVAL_SCORE_CALCULATION_FAILED

SEVERITY_WEIGHTS = {
    "critical": 3.0,
    "high": 2.0,
    "normal": 1.0,
    "optional": 0.5,
}


def reject_nan_inf(val: float, label: str) -> None:
    if math.isnan(val) or math.isinf(val):
        raise ValueError(f"{label} is NaN or Infinity: {val}")


def calculate_case_score(case: BenchmarkCase, observed_result: dict) -> EvaluationCaseResult:
    max_score = 1.0
    weight = case.weight if case.weight > 0 else 1.0
    case_result = EvaluationCaseResult(
        case_id=case.case_id,
        max_score=max_score,
        weight=weight,
        observed_result=observed_result,
        expected_result=dict(case.expected_result),
    )
    return case_result


def calculate_run_score(case_results: list[EvaluationCaseResult]) -> EvaluationScore:
    score = EvaluationScore(score_id=new_eval_id("score"))
    try:
        for r in case_results:
            reject_nan_inf(r.weight, f"Case {r.case_id} weight")
            if hasattr(r, 'score'):
                reject_nan_inf(r.score, f"Case {r.case_id} score")
            if hasattr(r, 'weighted_score'):
                reject_nan_inf(r.weighted_score, f"Case {r.case_id} weighted_score")
        total = len(case_results)
        score.total_cases = total
        for r in case_results:
            if r.status == EVAL_PASS:
                score.passed_cases += 1
            elif r.status == EVAL_FAIL:
                score.failed_cases += 1
            elif r.status == EVAL_BLOCKED:
                score.blocked_cases += 1
            elif r.status == EVAL_ERROR:
                score.error_cases += 1
            elif r.status == EVAL_SKIPPED:
                score.skipped_cases += 1
        score.raw_score = float(score.passed_cases)
        if total > 0:
            score.normalized_score = score.raw_score / total
        weighted = sum(
            r.weight * (1.0 if r.passed else 0.0)
            for r in case_results
        )
        total_weight = sum(r.weight for r in case_results) or 1.0
        score.weighted_score = weighted / total_weight
        score.pass_rate = score.passed_cases / max(total, 1)
        score.failure_rate = score.failed_cases / max(total, 1)
        score.blocked_rate = score.blocked_cases / max(total, 1)
        score.error_rate = score.error_cases / max(total, 1)
    except (ValueError, ZeroDivisionError) as exc:
        score.errors.append(f"{EVAL_SCORE_CALCULATION_FAILED}: {exc}")
    return score


def normalize_score(raw_score: float, max_score: float) -> float:
    try:
        reject_nan_inf(raw_score, "raw_score")
        reject_nan_inf(max_score, "max_score")
    except ValueError as exc:
        raise ValueError(f"{EVAL_SCORE_CALCULATION_FAILED}: {exc}")
    if max_score <= 0:
        return 0.0
    return raw_score / max_score


def calculate_weighted_score(case_results: list[EvaluationCaseResult]) -> float:
    for r in case_results:
        reject_nan_inf(r.weight, f"Case {r.case_id} weight")
    weighted = sum(
        r.weight * (1.0 if r.passed else 0.0)
        for r in case_results
    )
    reject_nan_inf(weighted, "weighted sum")
    total_weight = sum(r.weight for r in case_results) or 1.0
    reject_nan_inf(total_weight, "total_weight")
    return weighted / total_weight
