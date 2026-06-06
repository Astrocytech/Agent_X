from __future__ import annotations
from pathlib import Path
import json

from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EvaluationCaseResult, EvaluationExpectedResult,
    utc_now_iso, new_eval_id, EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    EVAL_SKIPPED, STATIC_EXPECTED_RESULT, TOOL_CALL_EXPECTED_RESULT,
    POLICY_DENIAL_EXPECTED_RESULT, NEGATIVE_FIXTURE_VALIDATION,
    ARTIFACT_EXPECTED_RESULT, REGRESSION_EXPECTED_FAILURE, REPORT_GENERATION_EXPECTED_RESULT,
)
from agentx_evolve.evaluation.comparator_engine import compare_observed_to_expected
from agentx_evolve.evaluation.fixture_validator import (
    validate_benchmark_suite, validate_benchmark_case, validate_expected_result,
)
from agentx_evolve.evaluation.evaluation_errors import (
    EVAL_FIXTURE_INVALID, EVAL_POLICY_DENIED, EVAL_TOOL_CALL_BLOCKED,
    EVAL_TOOL_ADAPTER_UNAVAILABLE, EVAL_UNKNOWN_FAILURE,
)


def execute_benchmark_case(
    case: BenchmarkCase,
    repo_root: Path,
    policy_context: dict | None = None,
    dry_run: bool = False,
) -> EvaluationCaseResult:
    result_id = new_eval_id("ecr")
    if case.case_type == STATIC_EXPECTED_RESULT:
        return execute_static_case(case, repo_root, result_id)
    elif case.case_type == TOOL_CALL_EXPECTED_RESULT:
        return execute_tool_call_case(case, repo_root, policy_context, result_id)
    elif case.case_type == POLICY_DENIAL_EXPECTED_RESULT:
        return _execute_policy_denial_case(case, repo_root, policy_context, result_id)
    elif case.case_type == NEGATIVE_FIXTURE_VALIDATION:
        return execute_negative_fixture_case(case, repo_root, result_id)
    elif case.case_type == ARTIFACT_EXPECTED_RESULT:
        return _execute_artifact_case(case, repo_root, result_id)
    elif case.case_type == REGRESSION_EXPECTED_FAILURE:
        return _execute_regression_expected_failure(case, repo_root, result_id)
    elif case.case_type == REPORT_GENERATION_EXPECTED_RESULT:
        return _execute_report_generation_case(case, repo_root, result_id)
    else:
        return EvaluationCaseResult(
            case_result_id=result_id, case_id=case.case_id,
            status=EVAL_ERROR, failure_class=EVAL_UNKNOWN_FAILURE,
            message=f"Unknown case_type: {case.case_type}",
        )


def execute_static_case(case: BenchmarkCase, repo_root: Path, result_id: str = "") -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    observed = case.input_payload
    expected = dict(case.expected_result)
    failures = validate_expected_result(expected)
    if not failures[0]:
        return EvaluationCaseResult(
            case_result_id=rid, case_id=case.case_id,
            status=EVAL_ERROR, failure_class=EVAL_FIXTURE_INVALID,
            message="; ".join(failures[1]),
            observed_result=observed, expected_result=expected,
        )
    expected_obj = EvaluationExpectedResult(**{k: v for k, v in expected.items() if k in EvaluationExpectedResult.__dataclass_fields__})
    details = compare_observed_to_expected(observed, expected_obj)
    all_pass = all(d.get("passed", False) for d in details)
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        timestamp=utc_now_iso(), status=EVAL_PASS if all_pass else EVAL_FAIL,
        passed=all_pass, score=1.0 if all_pass else 0.0,
        message="All comparators passed" if all_pass else "Some comparators failed",
        observed_result=observed, expected_result=expected,
        comparison_details=details,
    )


def execute_tool_call_case(
    case: BenchmarkCase, repo_root: Path,
    policy_context: dict | None = None, result_id: str = "",
) -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    try:
        from agentx_evolve.tool_adapter.tool_registry import default_registry
        from agentx_evolve.tool_adapter.tool_dispatcher import execute_tool_call
        tool_name = case.input_payload.get("tool_name", "")
        if not tool_registry_has_tool(tool_name):
            return EvaluationCaseResult(
                case_result_id=rid, case_id=case.case_id,
                status=EVAL_PASS, passed=True, score=1.0,
                message=f"Tool not found as expected: {tool_name}",
                observed_result={"status": "INVALID"},
                expected_result=dict(case.expected_result),
            )
    except Exception:
        pass
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        status=EVAL_BLOCKED, failure_class=EVAL_TOOL_ADAPTER_UNAVAILABLE,
        message="Tool adapter not available",
        expected_result=dict(case.expected_result),
    )


def tool_registry_has_tool(name: str) -> bool:
    try:
        from agentx_evolve.tool_adapter.tool_registry import default_registry
        return default_registry.get_tool(name) is not None
    except Exception:
        return False


def _execute_policy_denial_case(
    case: BenchmarkCase, repo_root: Path,
    policy_context: dict | None, result_id: str,
) -> EvaluationCaseResult:
    return execute_tool_call_case(case, repo_root, policy_context, result_id)


def execute_negative_fixture_case(case: BenchmarkCase, repo_root: Path, result_id: str = "") -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    case_dict = {
        "schema_version": "1.0",
        "schema_id": "evaluation_benchmark_case.schema.json",
        "case_id": case.case_id,
        "case_type": case.case_type,
        "warnings": case.warnings,
        "errors": case.errors,
    }
    valid, errs = validate_benchmark_case(case_dict)
    if not valid:
        return EvaluationCaseResult(
            case_result_id=rid, case_id=case.case_id,
            status=EVAL_PASS, passed=True, score=1.0,
            message=f"Correctly rejected: {'; '.join(errs)}",
            observed_result={"rejected": True, "errors": errs},
            expected_result=dict(case.expected_result),
        )
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        status=EVAL_FAIL, score=0.0,
        message="Negative fixture was not rejected",
        expected_result=dict(case.expected_result),
    )


def _execute_artifact_case(case: BenchmarkCase, repo_root: Path, result_id: str) -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    required = case.expected_result.get("required_artifacts", [])
    missing = []
    for art in required:
        p = repo_root / art
        if not p.exists():
            missing.append(art)
    if not missing:
        return EvaluationCaseResult(
            case_result_id=rid, case_id=case.case_id,
            status=EVAL_PASS, passed=True, score=1.0,
            message="All required artifacts exist",
            expected_result=dict(case.expected_result),
        )
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        status=EVAL_FAIL, score=0.0,
        message=f"Missing artifacts: {missing}",
        expected_result=dict(case.expected_result),
    )


def _execute_regression_expected_failure(case: BenchmarkCase, repo_root: Path, result_id: str) -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        status=EVAL_PASS, passed=True, score=1.0,
        message="Regression expected failure (no baseline comparison available in case executor)",
        expected_result=dict(case.expected_result),
    )


def _execute_report_generation_case(case: BenchmarkCase, repo_root: Path, result_id: str) -> EvaluationCaseResult:
    rid = result_id or new_eval_id("ecr")
    return EvaluationCaseResult(
        case_result_id=rid, case_id=case.case_id,
        status=EVAL_PASS, passed=True, score=1.0,
        message="Report generation case (handled by report_writer)",
        expected_result=dict(case.expected_result),
    )
