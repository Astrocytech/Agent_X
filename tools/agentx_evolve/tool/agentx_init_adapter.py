from __future__ import annotations
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_FAILED,
    new_id, utc_now_iso,
)

_STUB_MESSAGES: dict[str, str] = {
    "agentx_scan": "Scan complete",
    "agentx_status": "Status report generated",
    "agentx_plan": "Plan generated",
    "agentx_propose": "Proposal generated",
    "agentx_governance_check": "Governance check passed",
    "agentx_risk_check": "Risk check passed",
    "agentx_validate": "Validation complete",
    "agentx_report": "Report generated",
    "agentx_graph_build": "Graph built",
    "agentx_graph_status": "Graph status retrieved",
    "agentx_graph_query": "Graph query executed",
}


def _stub_result(call: ToolCall) -> ToolResult:
    message = _STUB_MESSAGES.get(call.tool_name, f"Executed {call.tool_name}")
    return ToolResult(
        result_id=new_id("tr"), timestamp=utc_now_iso(),
        tool_name=call.tool_name, status=TS_SUCCESS,
        message=message,
        data={"tool": call.tool_name, "arguments": call.arguments},
    )


def _make_tool(name: str, desc: str, params: list[ToolParameter] | None = None, handler: callable | None = None) -> tuple[ToolDefinition, callable]:
    h = handler or _stub_result
    defn = ToolDefinition(
        tool_id=new_id("td"), timestamp=utc_now_iso(),
        tool_name=name, description=desc,
        parameters=params or [
            ToolParameter(name="arguments", param_type="object",
                          description="Command arguments", required=False),
        ],
        handler_name=f"agentx_init_adapter.{name}",
        side_effect="read",
    )
    return defn, h


def make_scan_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_scan", "Scan repository structure")


def make_status_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_status", "Show system status")


def make_plan_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_plan", "Generate an evolution plan")


def make_propose_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_propose", "Generate a patch proposal")


def make_governance_check_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_governance_check", "Check governance requirements")


def make_risk_check_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_risk_check", "Check risk level")


def make_validate_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_validate", "Validate a patch proposal")


def make_report_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_report", "Generate session report")


def make_graph_build_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_graph_build", "Build knowledge graph")


def make_graph_status_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_graph_status", "Show knowledge graph status")


def make_graph_query_tool() -> tuple[ToolDefinition, callable]:
    return _make_tool("agentx_graph_query", "Query knowledge graph")


def register_initiator_tools(registry) -> list[ToolDefinition]:
    makers = [
        make_scan_tool, make_status_tool, make_plan_tool,
        make_propose_tool, make_governance_check_tool,
        make_risk_check_tool, make_validate_tool, make_report_tool,
        make_graph_build_tool, make_graph_status_tool, make_graph_query_tool,
    ]
    defns = []
    for maker in makers:
        defn, handler = maker()
        registry.register(defn, handler)
        defns.append(defn)
    return defns
