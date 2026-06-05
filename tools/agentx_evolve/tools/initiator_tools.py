from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    STATUS_FAILED,
    COMMAND_NOT_IMPLEMENTED,
    UNKNOWN_TOOL_FAILURE,
    utc_now_iso,
    new_id,
)


def _make_tool_result(tool_call: ToolCall, status: str, message: str, data: dict | None = None, failure_class: str | None = None) -> ToolResult:
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


def _try_call_initiator(action: str, arguments: dict) -> tuple[str, str, dict | None, str | None]:
    try:
        from agentx_initiator import initiator_api as api
        handler = getattr(api, action, None)
        if handler:
            result = handler(**arguments)
            return STATUS_SUCCESS, f"{action} completed", {"result": result}, None
    except ImportError:
        pass
    except Exception as e:
        return STATUS_FAILED, f"{action} failed: {e}", {"error": str(e)}, UNKNOWN_TOOL_FAILURE
    return STATUS_BLOCKED, f"{action} not available", None, COMMAND_NOT_IMPLEMENTED


def _resolve_call(context: dict, name: str) -> ToolCall:
    tc = context.get("tool_call") if isinstance(context, dict) else None
    if not isinstance(tc, ToolCall):
        tc = ToolCall(tool_name=name)
    return tc


def agentx_scan(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_scan")
    status, message, data, fc = _try_call_initiator("scan", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_status(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_status")
    status, message, data, fc = _try_call_initiator("status", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_plan(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_plan")
    status, message, data, fc = _try_call_initiator("plan", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_propose(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_propose")
    status, message, data, fc = _try_call_initiator("propose", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_validate(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_validate")
    status, message, data, fc = _try_call_initiator("validate", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_report(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_report")
    status, message, data, fc = _try_call_initiator("report", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_graph_build(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_graph_build")
    status, message, data, fc = _try_call_initiator("graph_build", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_graph_status(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_graph_status")
    status, message, data, fc = _try_call_initiator("graph_status", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)


def agentx_graph_query(arguments: dict, context: dict) -> ToolResult:
    tool_call = _resolve_call(context, "agentx_graph_query")
    status, message, data, fc = _try_call_initiator("graph_query", arguments)
    return _make_tool_result(tool_call, status, message, data, fc)
