import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    create_review_request_from_policy_decision,
    validate_approval_for_policy_decision,
    create_review_request,
    record_approval_decision,
    HumanReviewerIdentity,
    HumanApprovalScope,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestCreateReviewRequestFromPolicyDecision:
    def test_creates_a_request(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            policy_decision = {
                "requested_by": "user-1",
                "action": "apply_patch",
                "effect": "modify_files",
                "risk_level": "LOW",
                "reason": "Policy allowed",
                "policy_decision_id": "pd-001",
            }
            context = {"session_id": "sess-001", "requester_id": "user-1"}
            request = create_review_request_from_policy_decision(
                policy_decision=policy_decision,
                context=context,
                repo_root=repo_root,
            )
            assert request.request_id.startswith("hreq-")
            assert request.requested_by == "user-1"
            assert request.requested_action == "apply_patch"
            assert request.policy_decision_id == "pd-001"


class TestValidateApprovalForPolicyDecision:
    def test_returns_result(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-pv-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
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
            policy_decision = {
                "action": "apply_patch",
                "effect": "modify",
                "policy_decision_id": "pd-001",
                "scope": {"scope_id": "s-pv-001", "scope_type": "ACTION"},
            }
            result = validate_approval_for_policy_decision(
                policy_decision=policy_decision,
                approval_decision_id=decision.decision_id,
                repo_root=repo_root,
            )
            assert result.allowed is True
