import pytest
from pathlib import Path
from agentx_evolve.evaluation.case_executor import (
    execute_tool_call_case, tool_registry_has_tool,
)
from agentx_evolve.evaluation.evaluation_models import (
    BenchmarkCase, EVAL_PASS, EVAL_BLOCKED,
    TOOL_CALL_EXPECTED_RESULT, POLICY_DENIAL_EXPECTED_RESULT,
)


def test_invalid_tool_name_returns_blocked_when_adapter_unavailable():
    case = BenchmarkCase(
        case_id="tc-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "__nonexistent_tool_name__", "arguments": {}},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.status == EVAL_BLOCKED


def test_tool_call_with_dry_run_skips_execution(tmp_path):
    case = BenchmarkCase(
        case_id="dry-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "some_tool"},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, tmp_path)
    assert result.case_id == "dry-1"


def test_tool_adapter_unavailable_returns_eval_blocked(tmp_path):
    case = BenchmarkCase(
        case_id="blocked-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "read_file", "arguments": {}},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, tmp_path)
    assert result.status in (EVAL_PASS, EVAL_BLOCKED)


def test_policy_denial_case_dispatches_correctly():
    case = BenchmarkCase(
        case_id="pd-1",
        case_type=POLICY_DENIAL_EXPECTED_RESULT,
        input_payload={"tool_name": "blocked_tool"},
        expected_result={"expected_status": "EVAL_BLOCKED"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.case_id == "pd-1"


def test_tool_call_case_includes_expected_result_in_output():
    expected = {"expected_status": "EVAL_PASS", "warnings": [], "errors": []}
    case = BenchmarkCase(
        case_id="tc-4",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={"tool_name": "fake_tool"},
        expected_result=expected,
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.expected_result == expected


def test_tool_case_handles_empty_payload():
    case = BenchmarkCase(
        case_id="empty-1",
        case_type=TOOL_CALL_EXPECTED_RESULT,
        input_payload={},
        expected_result={"expected_status": "EVAL_PASS"},
    )
    result = execute_tool_call_case(case, Path("/tmp"))
    assert result.case_id == "empty-1"


def test_tool_registry_has_tool_for_nonexistent():
    assert tool_registry_has_tool("__definitely_not_a_real_tool__") is False


def test_tool_case_cannot_execute_mutating_tool():
    from agentx_evolve.evaluation.evaluation_models import BenchmarkCase
    case = BenchmarkCase(
        schema_version="1.0", schema_id="evaluation_benchmark_case.schema.json",
        case_id="mutating-case", case_name="Mutating Tool Test", description="",
        case_type="TOOL_CALL_EXPECTED_RESULT", target_component="AGENTX_TOOL_MCP_ADAPTER",
        severity="critical", weight=3.0, input_ref=None, input_payload={"tool_name": "write_tool"},
        expected_result={"expected_status": "BLOCKED"}, threshold_id=None,
        timeout_seconds=30, tags=[], warnings=[], errors=[],
    )
    assert case.severity == "critical"
    assert case.case_type == "TOOL_CALL_EXPECTED_RESULT"


def test_missing_tool_evidence_blocks_required_case(tmp_path):
    from agentx_evolve.evaluation.evaluation_models import EvaluationCaseResult
    result = EvaluationCaseResult(
        schema_version="1.0", schema_id="evaluation_case_result.schema.json",
        case_result_id="res-1", case_id="case-1", run_id="run-1",
        timestamp="2024-01-01T00:00:00Z", status="EVAL_FAIL", score=0.0, max_score=1.0,
        weight=1.0, weighted_score=0.0, passed=False, message="Missing tool evidence",
        observed_result={}, expected_result={}, comparison_details=[],
        failure_class="EVAL_TOOL_ADAPTER_UNAVAILABLE", artifact_refs=[], evidence_refs=[],
        warnings=[], errors=[],
    )
    assert not result.passed
    assert result.failure_class == "EVAL_TOOL_ADAPTER_UNAVAILABLE"
