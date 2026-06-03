import pytest
from pathlib import Path
from agentx_evolve.evaluation.case_executor import (
    execute_benchmark_case, execute_static_case, execute_tool_call_case,
    execute_negative_fixture_case, tool_registry_has_tool,
)
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EvaluationCaseResult,
    EVAL_PASS, EVAL_FAIL, EVAL_BLOCKED, EVAL_ERROR,
    STATIC_EXPECTED_RESULT, TOOL_CALL_EXPECTED_RESULT,
    POLICY_DENIAL_EXPECTED_RESULT, NEGATIVE_FIXTURE_VALIDATION,
    ARTIFACT_EXPECTED_RESULT, REGRESSION_EXPECTED_FAILURE,
    REPORT_GENERATION_EXPECTED_RESULT,
)


def test_execute_benchmark_case_unknown_type():
    case = BenchmarkCase(case_id="c1", case_type="UNKNOWN")
    result = execute_benchmark_case(case, Path("/tmp"))
    assert result.status == EVAL_ERROR
    assert "Unknown case_type" in result.message


def _valid_expected(overrides=None):
    base = {
        "schema_version": "1.0",
        "schema_id": "evaluation_expected_result.schema.json",
        "expected_result_id": "er-1",
        "expected_status": "ok",
        "warnings": [],
        "errors": [],
        "comparators": [{"type": "EXACT_MATCH", "path": "status", "expected": "ok"}],
    }
    if overrides:
        base.update(overrides)
    return base


def test_execute_static_case_passes():
    case = BenchmarkCase(
        case_id="c1",
        case_type=STATIC_EXPECTED_RESULT,
        input_payload={"status": "ok"},
        expected_result=_valid_expected(),
    )
    result = execute_static_case(case, Path("/tmp"))
    assert result.status == EVAL_PASS
    assert result.passed
    assert result.score == 1.0


def test_execute_static_case_fails():
    case = BenchmarkCase(
        case_id="c1",
        case_type=STATIC_EXPECTED_RESULT,
        input_payload={"status": "bad"},
        expected_result=_valid_expected(),
    )
    result = execute_static_case(case, Path("/tmp"))
    assert result.status == EVAL_FAIL
    assert not result.passed
    assert result.score == 0.0


def test_execute_static_case_invalid_expected_result():
    case = BenchmarkCase(
        case_id="c1",
        case_type=STATIC_EXPECTED_RESULT,
        input_payload={},
        expected_result={"comparators": [{"type": "BAD_TYPE"}]},
    )
    result = execute_static_case(case, Path("/tmp"))
    assert result.status == EVAL_ERROR
    assert "EVAL_FIXTURE_INVALID" in result.failure_class or "unknown type" in result.message.lower()


def test_execute_tool_call_case_tool_not_found():
    case = BenchmarkCase(
        case_id="c1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "nonexistent_tool_xyz"},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.status in (EVAL_PASS, EVAL_BLOCKED)


def test_tool_registry_has_tool_false():
    assert not tool_registry_has_tool("__nonexistent_tool__")


def test_execute_negative_fixture_case_rejected():
    case = BenchmarkCase(
        case_id="c1",
        case_type="COMPLETELY_INVALID",
        input_payload={"bad_field": "value"},
        expected_result={"expected_status": "EVAL_FAIL"},
    )
    result = execute_negative_fixture_case(case, Path("/tmp"))
    assert result.status == EVAL_PASS


def test_execute_negative_fixture_case_not_rejected():
    case = BenchmarkCase(
        case_id="c1",
        case_type=NEGATIVE_FIXTURE_VALIDATION,
        expected_result={"expected_status": "EVAL_FAIL"},
    )
    result = execute_negative_fixture_case(case, Path("/tmp"))
    assert result.status in (EVAL_PASS, EVAL_FAIL)


def test_execute_artifact_case_passes(tmp_path):
    (tmp_path / "artifact.txt").write_text("data")
    case = BenchmarkCase(
        case_id="c1",
        case_type=ARTIFACT_EXPECTED_RESULT,
        expected_result={"required_artifacts": ["artifact.txt"]},
    )
    from agentx_evolve.evaluation.case_executor import _execute_artifact_case
    result = _execute_artifact_case(case, tmp_path, "")
    assert result.status == EVAL_PASS
    assert result.passed


def test_execute_artifact_case_missing(tmp_path):
    case = BenchmarkCase(
        case_id="c1",
        case_type=ARTIFACT_EXPECTED_RESULT,
        expected_result={"required_artifacts": ["missing.txt"]},
    )
    from agentx_evolve.evaluation.case_executor import _execute_artifact_case
    result = _execute_artifact_case(case, tmp_path, "")
    assert result.status == EVAL_FAIL
    assert not result.passed


def test_execute_regression_expected_failure():
    case = BenchmarkCase(case_id="c1", case_type=REGRESSION_EXPECTED_FAILURE)
    from agentx_evolve.evaluation.case_executor import _execute_regression_expected_failure
    result = _execute_regression_expected_failure(case, Path("/tmp"), "")
    assert result.status == EVAL_PASS


def test_execute_report_generation_case():
    case = BenchmarkCase(case_id="c1", case_type=REPORT_GENERATION_EXPECTED_RESULT)
    from agentx_evolve.evaluation.case_executor import _execute_report_generation_case
    result = _execute_report_generation_case(case, Path("/tmp"), "")
    assert result.status == EVAL_PASS


def test_execute_benchmark_case_static_dispatch():
    case = BenchmarkCase(case_id="c1", case_type=STATIC_EXPECTED_RESULT, input_payload={}, expected_result={"expected_status": "ok", "comparators": [{"type": "EXACT_MATCH", "path": "", "expected": {}}]})
    result = execute_benchmark_case(case, Path("/tmp"))
    assert result.case_id == "c1"


def test_execute_benchmark_case_policy_denial():
    case = BenchmarkCase(case_id="c1", case_type=POLICY_DENIAL_EXPECTED_RESULT)
    result = execute_benchmark_case(case, Path("/tmp"))
    assert result.case_id == "c1"


def test_execute_benchmark_case_negative_dispatch():
    case = BenchmarkCase(case_id="c1", case_type=NEGATIVE_FIXTURE_VALIDATION, expected_result={"expected_status": "EVAL_FAIL"})
    result = execute_benchmark_case(case, Path("/tmp"))
    assert result.case_id == "c1"


def test_execute_benchmark_case_artifact_dispatch(tmp_path):
    (tmp_path / "exists.txt").write_text("data")
    case = BenchmarkCase(case_id="c1", case_type=ARTIFACT_EXPECTED_RESULT, expected_result={"required_artifacts": ["exists.txt"]})
    result = execute_benchmark_case(case, tmp_path)
    assert result.case_id == "c1"
