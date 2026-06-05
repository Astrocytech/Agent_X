import pytest

from agentx_evolve.tools.invalid_tool import handle_invalid_tool
from agentx_evolve.tools.tool_models import ToolResult


def test_handle_invalid_tool_returns_tool_result():
    result = handle_invalid_tool({"tool_name": "nonexistent"})
    assert isinstance(result, ToolResult)


def test_tool_not_found():
    result = handle_invalid_tool({"tool_name": "nonexistent"})
    assert result.status == "INVALID"
    assert result.failure_class == "TOOL_NOT_FOUND"
    assert "nonexistent" in result.message or "not found" in result.message.lower()


def test_tool_not_found_no_name():
    result = handle_invalid_tool({"tool_name": ""})
    assert result.failure_class in ("TOOL_NOT_FOUND", "TOOL_SCHEMA_INVALID")


def test_tool_not_found_missing_name():
    result = handle_invalid_tool({})
    assert result.failure_class == "TOOL_SCHEMA_INVALID"


def test_schema_invalid():
    result = handle_invalid_tool({"tool_name": "agentx_scan", "validation_error": "missing required field 'action'"})
    assert result.failure_class == "TOOL_NOT_FOUND"
    assert "Unknown" in result.message or "not found" in result.message.lower()


def test_schema_invalid_missing_validation():
    result = handle_invalid_tool({"tool_name": "agentx_scan"})
    assert result.status == "INVALID"


def test_tool_name_is_none():
    result = handle_invalid_tool({"tool_name": None})
    assert result.failure_class == "TOOL_SCHEMA_INVALID"
    assert result.status == "INVALID"


def test_none_input():
    result = handle_invalid_tool(None)
    assert result.status == "INVALID"
    assert result.failure_class == "TOOL_SCHEMA_INVALID"


def test_result_has_timestamp():
    result = handle_invalid_tool({"tool_name": "nonexistent"})
    assert result.timestamp
    assert "T" in result.timestamp
