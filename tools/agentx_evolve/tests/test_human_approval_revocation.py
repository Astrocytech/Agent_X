import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    HumanReviewRequest,
    create_review_request,
    record_approval_decision,
    revoke_approval,
    is_revoked,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestHumanApprovalRevocation:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-rv-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self, reviewer_id="rev-rv-001") -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id=reviewer_id,
            reviewer_label="Frank",
            reviewer_role="admin",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )

    def _make_request(self, repo_root: Path) -> HumanReviewRequest:
        scope = self._make_scope()
        return create_review_request(
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify",
            risk_level=RISK_LEVEL_LOW,
            reason="Test reason",
            scope=scope,
            context={},
            repo_root=repo_root,
        )

    def _make_approval(self, repo_root: Path) -> str:
        request = self._make_request(repo_root)
        reviewer = self._make_reviewer("rev-rv-maker")
        scope = self._make_scope()
        decision = record_approval_decision(
            request_id=request.request_id,
            reviewer=reviewer,
            reason="ok",
            scope=scope,
            expires_at=None,
            no_expiry_reason="no expiry",
            context={},
            repo_root=repo_root,
        )
        return decision.decision_id

    def test_revoke_approval_creates_valid_revocation(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root)
            revoker = self._make_reviewer("rev-rvoker")
            revocation = revoke_approval(decision_id, revoker, "Overturned by admin", repo_root)
            assert revocation.revocation_id.startswith("hrev-")
            assert revocation.approval_decision_id == decision_id
            assert revocation.reason == "Overturned by admin"
            assert revocation.revocation_hash is not None

    def test_is_revoked_returns_true_after_revocation(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root)
            revoker = self._make_reviewer("rev-rvoker-2")
            revoke_approval(decision_id, revoker, "Policy change", repo_root)
            assert is_revoked(decision_id, repo_root) is True

    def test_is_revoked_returns_false_before_revocation(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root)
            assert is_revoked(decision_id, repo_root) is False

    def test_is_revoked_returns_false_for_nonexistent_approval(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            assert is_revoked("nonexistent-id", repo_root) is False
