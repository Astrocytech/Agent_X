import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    HumanApprovalDecision,
    HumanReviewRequest,
    create_review_request,
    record_approval_decision,
    check_expiry,
    is_approval_expired,
    mark_expired_approvals,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
    DECISION_APPROVED,
)


class TestHumanApprovalExpiry:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-ex-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-ex-001",
            reviewer_label="Eve",
            reviewer_role="senior_dev",
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

    def _make_approval(self, repo_root: Path, expires_at=None) -> str:
        request = self._make_request(repo_root)
        reviewer = self._make_reviewer()
        scope = self._make_scope()
        decision = record_approval_decision(
            request_id=request.request_id,
            reviewer=reviewer,
            reason="ok",
            scope=scope,
            expires_at=expires_at,
            no_expiry_reason="test" if expires_at is None else None,
            context={},
            repo_root=repo_root,
        )
        return decision.decision_id

    def test_check_expiry_returns_not_expired_for_no_expiry_decision(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root, expires_at=None)
            result = check_expiry(decision_id, repo_root)
            assert result.expired is False

    def test_is_approval_expired_returns_true_for_past_expiry(self):
        decision = HumanApprovalDecision(
            decision_id="d-exp-001",
            request_id="r-001",
            decision=DECISION_APPROVED,
            expires_at="2000-01-01T00:00:00",
        )
        assert is_approval_expired(decision) is True

    def test_is_approval_expired_returns_false_for_future_expiry(self):
        decision = HumanApprovalDecision(
            decision_id="d-noexp-001",
            request_id="r-002",
            decision=DECISION_APPROVED,
            expires_at="2099-12-31T23:59:59",
        )
        assert is_approval_expired(decision) is False

    def test_is_approval_expired_returns_false_when_no_expiry(self):
        decision = HumanApprovalDecision(
            decision_id="d-never-001",
            request_id="r-003",
            decision=DECISION_APPROVED,
            expires_at=None,
        )
        assert is_approval_expired(decision) is False

    def test_check_expiry_returns_expired_for_past_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root, expires_at="2000-01-01T00:00:00")
            result = check_expiry(decision_id, repo_root)
            assert result.expired is True
            assert result.reason == "Past expiry"

    def test_check_expiry_returns_not_expired_for_future_expiry(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision_id = self._make_approval(repo_root, expires_at="2099-12-31T23:59:59")
            result = check_expiry(decision_id, repo_root)
            assert result.expired is False

    def test_mark_expired_approvals_empty_history(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            results = mark_expired_approvals(repo_root)
            assert results == []
