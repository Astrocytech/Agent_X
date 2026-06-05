import pytest

from agentx_evolve.tools.initiator_tools import (
    agentx_scan,
    agentx_status,
    agentx_plan,
    agentx_propose,
    agentx_validate,
    agentx_report,
    agentx_graph_build,
    agentx_graph_status,
    agentx_graph_query,
)
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
)


INITIATOR_FUNCS = [
    agentx_scan,
    agentx_status,
    agentx_plan,
    agentx_propose,
    agentx_validate,
    agentx_report,
    agentx_graph_build,
    agentx_graph_status,
    agentx_graph_query,
]


def test_each_initiator_returns_tool_result():
    for func in INITIATOR_FUNCS:
        result = func({}, {})
        assert isinstance(result, ToolResult), f"{func.__name__} did not return ToolResult"
        assert result.tool_name == func.__name__
        assert result.source_component == "ToolMCPAdapter"


def test_each_initiator_has_valid_status():
    for func in INITIATOR_FUNCS:
        result = func({}, {})
        assert result.status in (STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED), f"{func.__name__} status: {result.status}"
        assert result.exit_code in (0, 1)


def test_each_initiator_with_tool_call_context():
    tc = ToolCall(tool_call_id="call_test", timestamp="now", source_component="test", tool_name="agentx_scan")
    for func in INITIATOR_FUNCS:
        result = func({}, {"tool_call": tc})
        assert isinstance(result, ToolResult)
        assert result.tool_call_id == "call_test"


def test_initiator_result_has_failure_class_on_error():
    result = agentx_scan({}, {})
    if result.status == STATUS_FAILED:
        assert result.failure_class is not None


def test_initiator_result_has_timestamp():
    result = agentx_scan({}, {})
    assert result.timestamp
    assert "T" in result.timestamp


def test_initiator_result_has_id():
    result = agentx_scan({}, {})
    assert result.tool_result_id.startswith("res_")
