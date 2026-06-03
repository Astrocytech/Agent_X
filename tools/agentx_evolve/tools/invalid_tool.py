from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    TOOL_NOT_FOUND,
    TOOL_SCHEMA_INVALID,
    STATUS_INVALID,
    ROLE_UNKNOWN_CALLER,
    utc_now_iso,
    new_id,
)


def handle_invalid_tool(tool_call: ToolCall | dict) -> ToolResult:
    if isinstance(tool_call, dict):
        raw = tool_call
        tool_name = raw.get("tool_name", None)
        caller_role = raw.get("caller_role", ROLE_UNKNOWN_CALLER)
        tool_call_id = raw.get("tool_call_id", None)
    elif isinstance(tool_call, ToolCall):
        raw = None
        tool_name = tool_call.tool_name
        caller_role = tool_call.caller_role
        tool_call_id = tool_call.tool_call_id
    else:
        tool_name = None
        caller_role = ROLE_UNKNOWN_CALLER
        tool_call_id = None

    if tool_name is None or not isinstance(tool_name, str):
        failure_class = TOOL_SCHEMA_INVALID
        reason = "Tool call missing or invalid tool_name"
    else:
        failure_class = TOOL_NOT_FOUND
        reason = f"Unknown tool: {tool_name}"

    result_id = new_id("res_")
    return ToolResult(
        tool_result_id=result_id,
        tool_call_id=tool_call_id or "",
        timestamp=utc_now_iso(),
        source_component="InvalidToolHandler",
        tool_name=tool_name or "",
        status=STATUS_INVALID,
        exit_code=2,
        message=reason,
        data={"tool_name": tool_name, "reason": reason},
        failure_class=failure_class,
        warnings=[reason],
    )
