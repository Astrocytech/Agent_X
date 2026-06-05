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
    record_rejection_decision,
    DECISION_REJECTED,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestHumanRejectionDecision:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-rj-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-rj-001",
            reviewer_label="Bob",
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

    def test_record_rejection_decision_creates_valid_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            decision = record_rejection_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Rejected due to policy violation",
                context={},
                repo_root=repo_root,
            )
            assert decision.decision_id.startswith("hdec-")
            assert decision.request_id == request.request_id
            assert decision.reason == "Rejected due to policy violation"
            assert decision.decision_hash is not None

    def test_rejection_has_correct_decision_value(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            decision = record_rejection_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Rejected",
                context={},
                repo_root=repo_root,
            )
            assert decision.decision == DECISION_REJECTED

    def test_rejection_includes_reason(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            reason = "This change is outside the approved scope"
            decision = record_rejection_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason=reason,
                context={},
                repo_root=repo_root,
            )
            assert decision.reason == reason
