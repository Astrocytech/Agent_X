from __future__ import annotations
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_FAILED,
    new_id, utc_now_iso,
)


def _stub_result(call: ToolCall, message: str) -> ToolResult:
    return ToolResult(
        result_id=new_id("tr"), timestamp=utc_now_iso(),
        tool_name=call.tool_name, status=TS_SUCCESS,
        message=message,
        data={"tool": call.tool_name, "arguments": call.arguments},
    )


def _patch_apply(call: ToolCall) -> ToolResult:
    return _stub_result(call, "Patch applied")


def _patch_rollback(call: ToolCall) -> ToolResult:
    return _stub_result(call, "Patch rolled back")


def _patch_session_status(call: ToolCall) -> ToolResult:
    return _stub_result(call, "Session status retrieved")


def _make_tool(name: str, desc: str, params: list[ToolParameter] | None = None) -> tuple[ToolDefinition, callable]:
    handlers = {
        "patch_apply": _patch_apply,
        "patch_rollback": _patch_rollback,
        "patch_session_status": _patch_session_status,
    }
    h = handlers.get(name, _stub_result)
    defn = ToolDefinition(
        tool_id=new_id("td"), timestamp=utc_now_iso(),
        tool_name=name, description=desc,
        parameters=params or [
            ToolParameter(name="session_id", param_type="string",
                          description="Session identifier", required=False),
        ],
        handler_name=f"patch_execution_adapter.{name}",
        side_effect="write",
        requires_approval=True,
    )
    return defn, h


def make_patch_apply_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("patch_apply", "Apply a patch in a session")


def make_patch_rollback_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("patch_rollback", "Rollback a session's changes")


def make_patch_session_status_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("patch_session_status", "Get session status")


def register_patch_tools(registry) -> list[ToolDefinition]:
    makers = [make_patch_apply_tool, make_patch_rollback_tool, make_patch_session_status_tool]
    defns = []
    for maker in makers:
        defn, handler = maker()
        registry.register(defn, handler)
        defns.append(defn)
    return defns
