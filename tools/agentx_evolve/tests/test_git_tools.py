import pytest

from agentx_evolve.tools.git_tools import (
    git_status,
    git_diff,
    git_diff_name_only,
    git_diff_stat,
    git_create_branch,
    git_stage_approved,
    git_commit_approved,
    git_push,
)
from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
)


READ_ONLY_GIT = [
    (git_status, {}),
    (git_diff, {}),
    (git_diff_name_only, {}),
    (git_diff_stat, {}),
]

WRITE_GIT = [
    (git_create_branch, {}),
    (git_stage_approved, {}),
    (git_commit_approved, {}),
    (git_push, {}),
]


def test_each_read_only_git_returns_tool_result():
    for func, args in READ_ONLY_GIT:
        result = func(args, {})
        assert isinstance(result, ToolResult), f"{func.__name__} did not return ToolResult"
        assert result.tool_name == func.__name__


def test_each_read_only_git_valid_status():
    for func, args in READ_ONLY_GIT:
        result = func(args, {})
        assert result.status in (STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED)
        assert result.exit_code in (0, 1)


def test_each_write_git_blocked():
    for func, args in WRITE_GIT:
        result = func(args, {})
        assert result.status == STATUS_BLOCKED
        assert result.exit_code == 1
        assert "blocked" in result.message.lower()


def test_each_git_with_tool_call_context():
    tc = ToolCall(tool_call_id="call_git", tool_name="git_status")
    for func, args in READ_ONLY_GIT + WRITE_GIT:
        result = func(args, {"tool_call": tc})
        assert result.tool_call_id == "call_git"


def test_read_only_git_has_timestamp():
    result = git_status({}, {})
    assert result.timestamp
    assert "T" in result.timestamp


def test_read_only_git_has_id():
    result = git_status({}, {})
    assert result.tool_result_id.startswith("res_")
