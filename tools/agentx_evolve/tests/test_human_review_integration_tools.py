import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    create_review_request_from_tool_call,
    validate_approval_for_tool_call,
    create_review_request,
    record_approval_decision,
    HumanReviewerIdentity,
    HumanApprovalScope,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestCreateReviewRequestFromToolCall:
    def test_creates_a_request_with_tool_call_context(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            tool_call = {
                "tool_call_id": "tc-001",
                "tool_name": "read_file",
                "requested_by": "agent-1",
                "effect": "read_content",
                "risk_level": "LOW",
                "reason": "Need to read file",
                "arguments": {"path": "/tmp/test.txt"},
                "session_id": "sess-001",
            }
            tool_definition = {
                "tool_definition_id": "td-001",
                "effect": "read_content",
                "allowed_effects": ["read_content"],
                "blocked_effects": [],
            }
            request = create_review_request_from_tool_call(
                tool_call=tool_call,
                tool_definition=tool_definition,
                policy_decision=None,
                repo_root=repo_root,
            )
            assert request.request_id.startswith("hreq-")
            assert request.requested_action == "tool:read_file"
            assert request.tool_call_id == "tc-001"


class TestValidateApprovalForToolCall:
    def test_returns_result(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-tv-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="tool:read_file",
                requested_effect="read_content",
                risk_level=RISK_LEVEL_LOW,
                reason="test",
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            reviewer = HumanReviewerIdentity(
                reviewer_id="rev-001",
                reviewer_label="Alice",
                reviewer_role="dev",
                auth_method=AUTH_LOCAL_CONFIG,
                created_at=utc_now_iso(),
            )
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="ok",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            tool_call = {
                "tool_name": "read_file",
                "tool_call_id": "tc-001",
                "effect": "read_content",
                "session_id": "sess-001",
            }
            result = validate_approval_for_tool_call(
                tool_call=tool_call,
                approval_decision_id=decision.decision_id,
                repo_root=repo_root,
            )
            assert result.allowed is True
