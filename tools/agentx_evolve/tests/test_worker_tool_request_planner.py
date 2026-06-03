import pytest
from agentx_evolve.worker.tool_request_planner import plan_tool_requests


class TestPlanToolRequests:
    def test_no_tools(self):
        result = plan_tool_requests({})
        assert result == []

    def test_with_tools(self):
        result = plan_tool_requests({"required_tools": ["read_file", "write_file"]})
        assert len(result) == 2
        assert result[0]["tool"] == "read_file"
        assert result[1]["tool"] == "write_file"
