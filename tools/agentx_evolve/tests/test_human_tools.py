from agentx_evolve.tools.human_tools import (
    request_human_review,
    check_human_review_status,
)
from agentx_evolve.tools.tool_models import (
    STATUS_BLOCKED,
    STATUS_SUCCESS,
    COMMAND_BLOCKED,
)


def test_request_human_review_returns_blocked():
    result = request_human_review({"task": "approve deployment"})
    assert result.status == STATUS_BLOCKED
    assert result.exit_code == 1
    assert result.failure_class == COMMAND_BLOCKED
    assert "Human Review layer" in result.message


def test_request_human_review_with_context():
    result = request_human_review({"task": "review patch"}, {"session_id": "sess-1"})
    assert result.status == STATUS_BLOCKED
    assert result.data["arguments"]["task"] == "review patch"
    assert result.data["context"]["session_id"] == "sess-1"


def test_check_human_review_status_returns_success():
    result = check_human_review_status({})
    assert result.status == STATUS_SUCCESS
    assert result.exit_code == 0
    assert result.data["total_pending"] == 0
    assert result.data["pending_reviews"] == []


def test_check_human_review_status_with_filters():
    result = check_human_review_status({"status": "pending"})
    assert result.status == STATUS_SUCCESS
    assert result.data["total_pending"] == 0
