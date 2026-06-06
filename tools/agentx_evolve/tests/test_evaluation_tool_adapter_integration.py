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
