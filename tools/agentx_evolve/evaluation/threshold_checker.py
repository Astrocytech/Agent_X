from __future__ import annotations
from agentx_evolve.evaluation.evaluation_models import (
    EvaluationScore, EvaluationThreshold, EvaluationCaseResult, RegressionComparison,
    EVAL_PASS, EVAL_FAIL, EVAL_ERROR,
)
from agentx_evolve.evaluation.evaluation_errors import EVAL_THRESHOLD_FAILED


SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"
ALL_SEVERITIES = [SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL]


def check_thresholds(
    score: EvaluationScore,
    threshold: EvaluationThreshold,
    case_results: list[EvaluationCaseResult],
    regression_comparison: RegressionComparison | None = None,
    severity: str = SEVERITY_MEDIUM,
) -> dict:
    severity = resolve_severity(severity)

    severity_map = {
        SEVERITY_LOW: {"pass_rate_offset": 0.1, "blocked_error_offset": 2},
        SEVERITY_MEDIUM: {"pass_rate_offset": 0.0, "blocked_error_offset": 0},
        SEVERITY_HIGH: {"pass_rate_offset": -0.05, "blocked_error_offset": -1},
        SEVERITY_CRITICAL: {"pass_rate_offset": None, "blocked_error_offset": None},
    }

    result = {
        "threshold_id": threshold.threshold_id,
        "passed": True,
        "checks": [],
        "errors": [],
        "warnings": [],
        "severity": severity,
    }

    if severity == SEVERITY_CRITICAL:
        effective_min_pass_rate = 1.0
        effective_max_blocked = 0
        effective_max_error = 0
    else:
        adj = severity_map[severity]
        effective_min_pass_rate = threshold.minimum_pass_rate - adj["pass_rate_offset"]
        effective_max_blocked = max(0, threshold.maximum_blocked_count - adj["blocked_error_offset"])
        effective_max_error = max(0, threshold.maximum_error_count - adj["blocked_error_offset"])

    if score.pass_rate < effective_min_pass_rate:
        result["passed"] = False
        result["checks"].append({
            "check": "minimum_pass_rate",
            "passed": False,
            "required": effective_min_pass_rate,
            "actual": score.pass_rate,
        })
    else:
        result["checks"].append({"check": "minimum_pass_rate", "passed": True})
    if score.weighted_score < threshold.minimum_weighted_score:
        result["passed"] = False
        result["checks"].append({
            "check": "minimum_weighted_score",
            "passed": False,
            "required": threshold.minimum_weighted_score,
            "actual": score.weighted_score,
        })
    else:
        result["checks"].append({"check": "minimum_weighted_score", "passed": True})
    bc = score.blocked_cases
    if severity in (SEVERITY_HIGH, SEVERITY_CRITICAL) and bc > 0:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_blocked_count",
            "passed": False,
            "required": 0,
            "actual": bc,
        })
    elif bc > effective_max_blocked:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_blocked_count",
            "passed": False,
            "required": effective_max_blocked,
            "actual": bc,
        })
    elif not threshold.allow_blocked_cases and bc > 0:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_blocked_count",
            "passed": False,
            "required": 0,
            "actual": bc,
        })
    else:
        result["checks"].append({"check": "maximum_blocked_count", "passed": True})
    ec = score.error_cases
    if severity in (SEVERITY_HIGH, SEVERITY_CRITICAL) and ec > 0:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_error_count",
            "passed": False,
            "required": 0,
            "actual": ec,
        })
    elif ec > effective_max_error:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_error_count",
            "passed": False,
            "required": effective_max_error,
            "actual": ec,
        })
    elif not threshold.allow_error_cases and ec > 0:
        result["passed"] = False
        result["checks"].append({
            "check": "maximum_error_count",
            "passed": False,
            "required": 0,
            "actual": ec,
        })
    else:
        result["checks"].append({"check": "maximum_error_count", "passed": True})
    if regression_comparison:
        rc = regression_comparison.regression_count
        if rc > threshold.maximum_regression_count:
            result["passed"] = False
            result["checks"].append({
                "check": "maximum_regression_count",
                "passed": False,
                "required": threshold.maximum_regression_count,
                "actual": rc,
            })
        else:
            result["checks"].append({"check": "maximum_regression_count", "passed": True})
    missing = []
    for rid in threshold.required_case_ids:
        if rid not in {r.case_id for r in case_results if r.passed}:
            missing.append(rid)
    if missing:
        result["passed"] = False
        result["checks"].append({
            "check": "required_case_ids",
            "passed": False,
            "missing": missing,
        })
    else:
        result["checks"].append({"check": "required_case_ids", "passed": True})
    if not result["passed"]:
        result["errors"].append(EVAL_THRESHOLD_FAILED)
    return result


def resolve_severity(severity: str) -> str:
    normalized = severity.upper().strip()
    if normalized in ALL_SEVERITIES:
        return normalized
    return SEVERITY_MEDIUM


def check_required_cases(
    case_results: list[EvaluationCaseResult],
    required_case_ids: list[str],
) -> dict:
    passed_ids = {r.case_id for r in case_results if r.passed}
    missing = [cid for cid in required_case_ids if cid not in passed_ids]
    return {
        "passed": len(missing) == 0,
        "missing": missing,
        "total_required": len(required_case_ids),
        "passed_required": len(required_case_ids) - len(missing),
    }
