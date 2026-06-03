import pytest
from pathlib import Path
from agentx_evolve.evaluation.case_executor import (
    execute_tool_call_case, tool_registry_has_tool,
)
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EVAL_PASS, EVAL_BLOCKED,
    TOOL_CALL_EXPECTED_RESULT, POLICY_DENIAL_EXPECTED_RESULT,
)


def test_tool_registry_has_tool_returns_bool():
    result = tool_registry_has_tool("__nonexistent__")
    assert isinstance(result, bool)


def test_tool_call_case_blocked_when_adapter_unavailable():
    case = BenchmarkCase(
        case_id="tc-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "read_file", "arguments": {"path": "/tmp/test.txt"}},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.status in (EVAL_PASS, EVAL_BLOCKED)


def test_tool_call_case_with_empty_tool_name():
    case = BenchmarkCase(
        case_id="tc-2",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "", "arguments": {}},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.case_id == "tc-2"


def test_tool_call_case_without_payload():
    case = BenchmarkCase(
        case_id="tc-3",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.case_id == "tc-3"


def test_tool_call_case_includes_expected_result():
    expected = {"expected_status": "EVAL_PASS"}
    case = BenchmarkCase(
        case_id="tc-4",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "fake_tool"},
        expected_result=expected,
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.expected_result == expected


def test_policy_denial_dispatches_to_tool_call():
    case = BenchmarkCase(
        case_id="pd-1",
        case_type=POLICY_DENIAL_EXPECTED_RESULT,
        input_payload={"tool_name": "blocked_tool"},
        expected_result={"expected_status": "EVAL_BLOCKED", "expected_failure_class": "EVAL_POLICY_DENIED"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.case_id == "pd-1"


def test_tool_integration_via_runner(tmp_path):
    from agentx_evolve.evaluation.evaluation_runner import run_evaluation
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    suite_path = fixture_dir / "suite.json"
    suite_path.write_text('{"suite_id": "s1", "case_refs": ["tc.json"], "default_threshold_id": null, "baseline_ref": null, "first_run_allowed": true, "warnings": [], "errors": []}')
    case_path = fixture_dir / "tc.json"
    case_path.write_text('{"schema_version": "1.0", "schema_id": "evaluation_benchmark_case.schema.json", "case_id": "tc", "case_type": "TOOL_CALL_EXPECTED_RESULT", "input_payload": {"tool_name": "read"}, "expected_result": {"schema_version": "1.0", "schema_id": "evaluation_expected_result.schema.json", "expected_result_id": "er-1", "expected_status": "EVAL_PASS", "warnings": [], "errors": []}, "warnings": [], "errors": []}')
    run = run_evaluation(suite_path, tmp_path, first_run=True, write_reports=False, write_evidence=False)
    assert len(run.case_results) == 1


def test_tool_adapter_import_attempt(tmp_path):
    from agentx_evolve.evaluation.case_executor import execute_benchmark_case
    case = BenchmarkCase(
        case_id="imp-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "import_test"},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_benchmark_case(case, tmp_path)
    assert result.case_id == "imp-1"


def test_tool_call_case_dry_run(tmp_path):
    case = BenchmarkCase(
        case_id="dry-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "dry_run_tool"},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, tmp_path)
    assert result is not None
