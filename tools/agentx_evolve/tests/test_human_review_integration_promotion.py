import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    create_review_request_from_promotion_request,
    validate_approval_for_promotion,
    create_review_request,
    record_approval_decision,
    HumanReviewerIdentity,
    HumanApprovalScope,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestCreateReviewRequestFromPromotionRequest:
    def test_creates_a_request_with_promotion_context(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            promotion_request = {
                "promotion_request_id": "pr-001",
                "requested_by": "promotion-agent",
                "action": "promotion",
                "effect": "promote_artifacts",
                "risk_level": "HIGH",
                "reason": "Promote validated build",
                "artifact_refs": ["artifact-v1.0.tar.gz"],
                "commit_hashes": ["abc123"],
                "session_id": "sess-001",
            }
            validation_summary = {
                "risk_level": "HIGH",
                "reason": "All checks passed",
                "artifact_refs": ["artifact-v1.0.tar.gz"],
                "commit_hashes": ["abc123"],
                "allowed_effects": ["promote_artifacts"],
                "blocked_effects": [],
            }
            request = create_review_request_from_promotion_request(
                promotion_request=promotion_request,
                validation_summary=validation_summary,
                repo_root=repo_root,
            )
            assert request.request_id.startswith("hreq-")
            assert request.promotion_request_id == "pr-001"
            assert request.requested_action == "promotion"


class TestValidateApprovalForPromotion:
    def test_returns_result(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-prv-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="promotion",
                requested_effect="promote_artifacts",
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
            promotion_request = {
                "promotion_request_id": "pr-001",
                "action": "promotion",
                "effect": "promote_artifacts",
                "artifact_refs": ["artifact-v1.0.tar.gz"],
                "commit_hashes": ["abc123"],
                "session_id": "sess-001",
            }
            result = validate_approval_for_promotion(
                promotion_request=promotion_request,
                approval_decision_id=decision.decision_id,
                repo_root=repo_root,
            )
            assert result.allowed is True
