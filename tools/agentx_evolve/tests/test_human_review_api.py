import pytest
from agentx_evolve.human_review.review_api import ReviewAPI


class TestReviewAPI:
    def test_submit_request(self):
        api = ReviewAPI()
        result = api.submit_request(action="deploy", reason="testing")
        assert "request_id" in result
        assert result["requested_action"] == "deploy"

    def test_get_decision_no_decision(self):
        api = ReviewAPI()
        result = api.get_decision("req-001")
        assert result["decision"] is None
        assert "No decision found" in result.get("error", "")

    def test_list_pending_empty(self):
        api = ReviewAPI()
        pending = api.list_pending()
        assert pending == []

    def test_submit_and_list(self):
        api = ReviewAPI()
        api.submit_request(action="test", reason="r")
        pending = api.list_pending()
        assert len(pending) == 1
        assert pending[0]["requested_action"] == "test"
