from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_BLOCKED,
    STATUS_PARTIAL,
    COMMAND_BLOCKED,
    utc_now_iso,
    new_id,
)


def _blocked_result(tool_call: ToolCall, status: str, message: str) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=status,
        exit_code=1,
        message=message,
        failure_class=COMMAND_BLOCKED,
    )


def _resolve_call(context: dict, name: str) -> ToolCall:
    tc = context.get("tool_call") if isinstance(context, dict) else None
    if not isinstance(tc, ToolCall):
        tc = ToolCall(tool_name=name)
    return tc


def patch_session_status(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "patch_session_status")
    return _blocked_result(tool_call, STATUS_PARTIAL, "Patch session status: Governed Patch Execution layer not yet integrated")


def patch_apply_guarded(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "patch_apply_guarded")
    return _blocked_result(tool_call, STATUS_BLOCKED, "Patch apply blocked: Governed Patch Execution layer not yet authorized Tool Adapter invocation")


def rollback_session(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "rollback_session")
    return _blocked_result(tool_call, STATUS_BLOCKED, "Rollback blocked: Governed Patch Execution layer not yet authorized Tool Adapter invocation")
    return _blocked_result(tool_call, STATUS_BLOCKED, "Rollback blocked: Governed Patch Execution layer not yet authorized Tool Adapter invocation")
