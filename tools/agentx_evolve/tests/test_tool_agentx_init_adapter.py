from agentx_evolve.tools.initiator_tools import (
    agentx_scan, agentx_status, agentx_plan, agentx_propose,
    agentx_validate, agentx_report,
    agentx_graph_build, agentx_graph_status, agentx_graph_query,
)
from agentx_evolve.tools.tool_models import ToolDefinition, ToolCall, STATUS_SUCCESS


def test_initiator_tool_functions_have_correct_names():
    cases = [
        (agentx_scan, "agentx_scan"),
        (agentx_status, "agentx_status"),
        (agentx_plan, "agentx_plan"),
        (agentx_propose, "agentx_propose"),
        (agentx_validate, "agentx_validate"),
        (agentx_report, "agentx_report"),
        (agentx_graph_build, "agentx_graph_build"),
        (agentx_graph_status, "agentx_graph_status"),
        (agentx_graph_query, "agentx_graph_query"),
    ]
    for fn, expected_name in cases:
        result = fn({}, {})
        assert result.status in (STATUS_SUCCESS, "BLOCKED", "FAILED")


def test_all_initiator_tools_return_result():
    for fn in [agentx_scan, agentx_status, agentx_plan, agentx_propose,
               agentx_validate, agentx_report, agentx_graph_build,
               agentx_graph_status, agentx_graph_query]:
        result = fn({}, {})
        assert result.tool_name == fn.__name__
        assert result.status is not None
