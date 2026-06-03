from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
    COMMAND_BLOCKED,
    utc_now_iso,
    new_id,
)


def _blocked_result(tool_call: ToolCall, message: str) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=STATUS_BLOCKED,
        exit_code=1,
        message=message,
        failure_class=COMMAND_BLOCKED,
    )


def _success_result(tool_call: ToolCall, data: dict) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=STATUS_SUCCESS,
        exit_code=0,
        message=f"{tool_call.tool_name} completed",
        data=data,
    )


def _run_git_command(args: list[str]) -> tuple[str, str, dict | None]:
    try:
        import subprocess
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return STATUS_SUCCESS, "OK", {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        return STATUS_FAILED, f"Git command failed: {result.stderr.strip()}", {"stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
    except FileNotFoundError:
        return STATUS_BLOCKED, "Git not found", None
    except Exception as e:
        return STATUS_FAILED, f"Git command error: {e}", None


def _read_only_git(tool_call: ToolCall, args: list[str]) -> ToolResult:
    status, message, data = _run_git_command(args)
    if status == STATUS_SUCCESS:
        return _success_result(tool_call, data or {})
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=status,
        exit_code=1,
        message=message,
        data=data or {},
        failure_class=COMMAND_BLOCKED if status == STATUS_BLOCKED else None,
    )


def _resolve_call(context: dict, name: str) -> ToolCall:
    tc = context.get("tool_call") if isinstance(context, dict) else None
    if not isinstance(tc, ToolCall):
        tc = ToolCall(tool_name=name)
    return tc


def git_status(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_status")
    return _read_only_git(tool_call, ["status", "--short"])


def git_diff(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_diff")
    return _read_only_git(tool_call, ["diff"])


def git_diff_name_only(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_diff_name_only")
    return _read_only_git(tool_call, ["diff", "--name-only"])


def git_diff_stat(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_diff_stat")
    return _read_only_git(tool_call, ["diff", "--stat"])


def git_create_branch(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_create_branch")
    return _blocked_result(tool_call, "Git write tools are blocked in v1")


def git_stage_approved(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_stage_approved")
    return _blocked_result(tool_call, "Git write tools are blocked in v1")


def git_commit_approved(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_commit_approved")
    return _blocked_result(tool_call, "Git write tools are blocked in v1")


def git_push(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "git_push")
    return _blocked_result(tool_call, "Git write tools are blocked in v1")
    return _blocked_result(tool_call, "Git write tools are blocked in v1")
