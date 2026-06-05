import pytest

from agentx_evolve.tools.patch_tools import (
    patch_session_status,
    patch_apply_guarded,
    rollback_session,
)
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_BLOCKED,
    COMMAND_NOT_IMPLEMENTED,
)


PATCH_FUNCS = [
    (patch_session_status, {}),
    (patch_apply_guarded, {}),
    (rollback_session, {}),
]


def test_each_patch_returns_tool_result():
    for func, args in PATCH_FUNCS:
        result = func(args, {})
        assert isinstance(result, ToolResult), f"{func.__name__} did not return ToolResult"
        assert result.tool_name == func.__name__


def test_each_patch_blocked():
    for func, args in PATCH_FUNCS:
        result = func(args, {})
        assert result.status == STATUS_BLOCKED or result.status == "PARTIAL"
        assert result.exit_code == 1
        assert result.failure_class == COMMAND_NOT_IMPLEMENTED


def test_each_patch_with_tool_call_context():
    tc = ToolCall(tool_call_id="call_patch", tool_name="patch_session_status")
    for func, args in PATCH_FUNCS:
        result = func(args, {"tool_call": tc})
        assert result.tool_call_id == "call_patch"


def test_patch_apply_and_rollback_mention_governed():
    result = patch_apply_guarded({}, {})
    assert "Governed Patch Execution" in result.message
    result2 = rollback_session({}, {})
    assert "Governed Patch Execution" in result2.message


def test_patch_session_status_partial_not_critical():
    result = patch_session_status({}, {})
    assert result.failure_class is not None
