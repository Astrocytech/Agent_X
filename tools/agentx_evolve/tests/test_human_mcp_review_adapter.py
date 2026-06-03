import pytest
from agentx_evolve.human_review.mcp_review_adapter import MCPReviewAdapter


class TestMCPReviewAdapter:
    def test_handle_submit_request(self):
        adapter = MCPReviewAdapter()
        result = adapter.handle_submit_request({"action": "deploy", "reason": "testing"})
        assert "request_id" in result
        assert result["requested_action"] == "deploy"

    def test_handle_get_decision_not_found(self):
        adapter = MCPReviewAdapter()
        result = adapter.handle_get_decision({"request_id": "nonexistent"})
        assert result["decision"] is None

    def test_handle_list_pending(self):
        adapter = MCPReviewAdapter()
        result = adapter.handle_list_pending()
        assert isinstance(result, list)

    def test_submit_then_list(self):
        adapter = MCPReviewAdapter()
        adapter.handle_submit_request({"action": "test", "reason": "r"})
        pending = adapter.handle_list_pending()
        assert len(pending) >= 1
