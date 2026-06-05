import pytest

from agentx_evolve.tools.security_tools import (
    read_file_guarded,
    list_files_guarded,
    search_files_guarded,
    write_file_guarded,
    edit_file_guarded,
    patch_precheck_guarded,
    run_allowlisted_command,
)
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_BLOCKED,
)


SECURITY_FUNCS = [
    (read_file_guarded, {"path": "."}),
    (list_files_guarded, {"path": "."}),
    (search_files_guarded, {"path": "."}),
    (write_file_guarded, {"path": "/tmp/test", "content": "test"}),
    (edit_file_guarded, {"path": "/tmp/test", "old_string": "a", "new_string": "b"}),
    (patch_precheck_guarded, {"path": "."}),
    (run_allowlisted_command, {"command": "ls"}),
]


def test_each_security_returns_tool_result():
    for func, args in SECURITY_FUNCS:
        result = func(args, {})
        assert isinstance(result, ToolResult), f"{func.__name__} did not return ToolResult"
        assert result.tool_name == func.__name__


def test_each_security_has_valid_status():
    for func, args in SECURITY_FUNCS:
        result = func(args, {})
        assert result.status in ("SUCCESS", "BLOCKED", "FAILED"), f"{func.__name__} status: {result.status}"
        assert result.exit_code in (0, 1)


def test_each_security_with_tool_call_context():
    tc = ToolCall(tool_call_id="call_sec", tool_name="read_file_guarded")
    for func, args in SECURITY_FUNCS:
        result = func(args, {"tool_call": tc})
        assert result.tool_call_id == "call_sec"


def test_security_blocked_when_sandbox_missing():
    result = read_file_guarded({"path": "/nonexistent"}, {})
    assert result.status in ("BLOCKED", "FAILED")


def test_security_result_has_timestamp():
    result = read_file_guarded({"path": "."}, {})
    assert result.timestamp
    assert "T" in result.timestamp


def test_security_result_has_id():
    result = read_file_guarded({"path": "."}, {})
    assert result.tool_result_id.startswith("res_")
