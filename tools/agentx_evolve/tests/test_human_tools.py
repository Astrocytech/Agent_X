import pytest

from agentx_evolve.tools.human_tools import ask_human
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_BLOCKED,
    COMMAND_NOT_IMPLEMENTED,
)


def test_ask_human_returns_tool_result():
    result = ask_human({}, {})
    assert isinstance(result, ToolResult)


def test_ask_human_blocked():
    result = ask_human({}, {})
    assert result.status == STATUS_BLOCKED
    assert result.exit_code == 1


def test_ask_human_failure_class():
    result = ask_human({}, {})
    assert result.failure_class == COMMAND_NOT_IMPLEMENTED


def test_ask_human_message():
    result = ask_human({}, {})
    assert "not implemented" in result.message.lower()


def test_ask_human_with_tool_call_context():
    tc = ToolCall(tool_call_id="call_human", tool_name="ask_human")
    result = ask_human({}, {"tool_call": tc})
    assert result.tool_call_id == "call_human"


def test_ask_human_has_timestamp():
    result = ask_human({}, {})
    assert result.timestamp
    assert "T" in result.timestamp


def test_ask_human_has_id():
    result = ask_human({}, {})
    assert result.tool_result_id.startswith("res_")
