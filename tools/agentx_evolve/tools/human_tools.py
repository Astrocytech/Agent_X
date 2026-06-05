from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_BLOCKED,
    COMMAND_NOT_IMPLEMENTED,
    utc_now_iso,
    new_id,
)


def ask_human(arguments: dict, context: dict) -> ToolResult:
    tool_call = context.get("tool_call") if isinstance(context, dict) else None
    if not isinstance(tool_call, ToolCall):
        tool_call = ToolCall(tool_name="ask_human")
    return ToolResult(
        tool_result_id=new_id("res_"),
        tool_call_id=tool_call.tool_call_id,
        timestamp=utc_now_iso(),
        source_component="ToolMCPAdapter",
        tool_name=tool_call.tool_name,
        status=STATUS_BLOCKED,
        exit_code=1,
        message="Human review interface is not implemented in this layer.",
        failure_class=COMMAND_NOT_IMPLEMENTED,
    )
