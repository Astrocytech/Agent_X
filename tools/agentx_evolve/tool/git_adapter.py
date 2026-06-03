from __future__ import annotations
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_FAILED,
    new_id, utc_now_iso,
)
from agentx_evolve.git.git_operations import git_status as _git_status, git_diff as _git_diff
from agentx_evolve.git.git_models import GS_SUCCESS


def _result_from_git(call: ToolCall, git_result) -> ToolResult:
    return ToolResult(
        result_id=new_id("tr"), timestamp=utc_now_iso(),
        tool_name=call.tool_name,
        status=TS_SUCCESS if git_result.status == GS_SUCCESS else TS_FAILED,
        message=git_result.message,
        data={
            "operation": git_result.operation,
            "returncode": git_result.returncode,
            "stdout": git_result.stdout[:100000],
            "stderr": git_result.stderr[:50000],
        },
        errors=git_result.errors,
        warnings=git_result.warnings,
    )


def _git_status_handler(call: ToolCall) -> ToolResult:
    repo_path = call.arguments.get("repo_path", ".")
    git_result = _git_status(repo_path=repo_path)
    return _result_from_git(call, git_result)


def _git_diff_handler(call: ToolCall) -> ToolResult:
    target = call.arguments.get("target", "HEAD")
    repo_path = call.arguments.get("repo_path", ".")
    git_result = _git_diff(target=target, repo_path=repo_path)
    return _result_from_git(call, git_result)


def make_git_status_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"), timestamp=utc_now_iso(),
        tool_name="git_status",
        description="Show working tree status (read-only)",
        parameters=[
            ToolParameter(name="repo_path", param_type="string",
                          description="Repository path", required=False, default="."),
        ],
        handler_name="git_adapter.git_status",
        side_effect="read",
    )
    return defn, _git_status_handler


def make_git_diff_tool() -> tuple[ToolDefinition, callable]:
    defn = ToolDefinition(
        tool_id=new_id("td"), timestamp=utc_now_iso(),
        tool_name="git_diff",
        description="Show diff (read-only)",
        parameters=[
            ToolParameter(name="target", param_type="string",
                          description="Diff target (HEAD, --cached, etc.)", required=False, default="HEAD"),
            ToolParameter(name="repo_path", param_type="string",
                          description="Repository path", required=False, default="."),
        ],
        handler_name="git_adapter.git_diff",
        side_effect="read",
    )
    return defn, _git_diff_handler
