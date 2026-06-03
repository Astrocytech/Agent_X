from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
    TOOL_SANDBOX_DENIED,
    TOOL_EXECUTION_FAILED,
    UNKNOWN_TOOL_FAILURE,
    utc_now_iso,
    new_id,
)


def _make_result(tool_call: ToolCall, status: str, message: str, data: dict | None = None, failure_class: str | None = None) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=status,
        exit_code=0 if status == STATUS_SUCCESS else 1,
        message=message,
        data=data or {},
        failure_class=failure_class,
    )


from agentx_evolve.security import safe_read_file, safe_write_file, safe_exact_edit, safe_patch_precheck, check_subprocess_allowed

_SANDBOX_FUNCS = {
    "safe_read_file": safe_read_file,
    "safe_write_file": safe_write_file,
    "safe_exact_edit": safe_exact_edit,
    "safe_patch_precheck": safe_patch_precheck,
    "check_subprocess_allowed": check_subprocess_allowed,
}


def _call_sandbox(func_name: str, *args, **kwargs) -> tuple[str, str, dict | None, str | None]:
    try:
        func = _SANDBOX_FUNCS.get(func_name)
        if func is None:
            return STATUS_BLOCKED, f"Sandbox function {func_name} not found", None, UNKNOWN_TOOL_FAILURE
        result = func(*args, **kwargs)
        return STATUS_SUCCESS, f"{func_name} completed", {"result": str(result)}, None
    except Exception as e:
        return STATUS_BLOCKED, f"Sandbox denied: {e}", {"error": str(e)}, TOOL_SANDBOX_DENIED


def _resolve_call(context: dict, name: str) -> ToolCall:
    tc = context.get("tool_call") if isinstance(context, dict) else None
    if not isinstance(tc, ToolCall):
        tc = ToolCall(tool_name=name)
    return tc


def read_file_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "read_file_guarded")
    path = arguments.get("path", "")
    status, message, data, fc = _call_sandbox("safe_read_file", path)
    return _make_result(tool_call, status, message, data, fc)


def list_files_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "list_files_guarded")
    path = arguments.get("path", ".")
    status, message, data, fc = _call_sandbox("safe_read_file", path)
    return _make_result(tool_call, status, message, data, fc)


def search_files_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "search_files_guarded")
    path = arguments.get("path", ".")
    status, message, data, fc = _call_sandbox("safe_read_file", path)
    return _make_result(tool_call, status, message, data, fc)


def write_file_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "write_file_guarded")
    path = arguments.get("path", "")
    content = arguments.get("content", "")
    status, message, data, fc = _call_sandbox("safe_write_file", path, content)
    return _make_result(tool_call, status, message, data, fc)


def edit_file_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "edit_file_guarded")
    path = arguments.get("path", "")
    old_string = arguments.get("old_string", "")
    new_string = arguments.get("new_string", "")
    status, message, data, fc = _call_sandbox("safe_exact_edit", path, old_string, new_string)
    return _make_result(tool_call, status, message, data, fc)


def patch_precheck_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "patch_precheck_guarded")
    path = arguments.get("path", "")
    status, message, data, fc = _call_sandbox("safe_patch_precheck", path)
    return _make_result(tool_call, status, message, data, fc)


def run_allowlisted_command(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "run_allowlisted_command")
    command = arguments.get("command", "")
    status, message, data, fc = _call_sandbox("check_subprocess_allowed", command)
    return _make_result(tool_call, status, message, data, fc)
