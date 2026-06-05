import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    HumanReviewRequest,
    load_queue,
    create_review_request,
    record_deferral_decision,
    DECISION_DEFERRED,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    utc_now_iso,
)


class TestHumanReviewDeferral:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-df-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-df-001",
            reviewer_label="Carol",
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

    def test_record_deferral_decision_creates_valid_deferral(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            decision = record_deferral_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Need more time to review",
                deferred_until="2026-12-31T00:00:00",
                context={},
                repo_root=repo_root,
            )
            assert decision.decision_id.startswith("hdec-")
            assert decision.decision == DECISION_DEFERRED
            assert decision.decision_hash is not None

    def test_deferral_includes_deferred_until(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            deferred_until = "2026-06-30T23:59:59"
            decision = record_deferral_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Awaiting additional context",
                deferred_until=deferred_until,
                context={},
                repo_root=repo_root,
            )
            assert decision.deferred_until == deferred_until

    def test_deferral_keeps_request_pending(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            record_deferral_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Deferred",
                deferred_until="2026-12-31T00:00:00",
                context={},
                repo_root=repo_root,
            )
            queue = load_queue(repo_root)
            assert request.request_id in queue.deferred_requests
