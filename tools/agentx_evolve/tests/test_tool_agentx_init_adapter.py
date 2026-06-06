from agentx_evolve.tool.agentx_init_adapter import (
    make_scan_tool, make_status_tool, make_plan_tool, make_propose_tool,
    make_governance_check_tool, make_risk_check_tool, make_validate_tool,
    make_report_tool, make_graph_build_tool, make_graph_status_tool,
    make_graph_query_tool, register_initiator_tools,
)
from agentx_evolve.tool.tool_models import ToolDefinition, ToolCall, TS_SUCCESS


def test_make_scan_tool():
    defn, handler = make_scan_tool()
    assert defn.tool_name == "agentx_scan"
    assert isinstance(defn, ToolDefinition)


def test_make_status_tool():
    defn, handler = make_status_tool()
    assert defn.tool_name == "agentx_status"


def test_make_plan_tool():
    defn, handler = make_plan_tool()
    assert defn.tool_name == "agentx_plan"


def test_make_propose_tool():
    defn, handler = make_propose_tool()
    assert defn.tool_name == "agentx_propose"


def test_make_governance_check_tool():
    defn, handler = make_governance_check_tool()
    assert defn.tool_name == "agentx_governance_check"


def test_make_risk_check_tool():
    defn, handler = make_risk_check_tool()
    assert defn.tool_name == "agentx_risk_check"


def test_make_validate_tool():
    defn, handler = make_validate_tool()
    assert defn.tool_name == "agentx_validate"


def test_make_report_tool():
    defn, handler = make_report_tool()
    assert defn.tool_name == "agentx_report"


def test_make_graph_build_tool():
    defn, handler = make_graph_build_tool()
    assert defn.tool_name == "agentx_graph_build"


def test_make_graph_status_tool():
    defn, handler = make_graph_status_tool()
    assert defn.tool_name == "agentx_graph_status"


def test_make_graph_query_tool():
    defn, handler = make_graph_query_tool()
    assert defn.tool_name == "agentx_graph_query"


def test_default_handler_returns_success():
    _defn, handler = make_scan_tool()
    call = ToolCall(tool_name="agentx_scan", arguments={})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.message == "Scan complete"


def test_default_handler_unknown_tool():
    _defn, handler = make_scan_tool()
    call = ToolCall(tool_name="nonexistent", arguments={})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert "nonexistent" in result.message


class FakeRegistry:
    def __init__(self):
        self.registered = []

    def register(self, defn, handler):
        self.registered.append((defn, handler))


def test_register_initiator_tools():
    registry = FakeRegistry()
    defns = register_initiator_tools(registry)
    assert len(defns) == 11
    assert len(registry.registered) == 11
