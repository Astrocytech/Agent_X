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
    lookup_approval,
    DECISION_APPROVED,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    AUTH_LOCAL_CONFIG,
    SCHEMA_VERSION,
    utc_now_iso,
)


class TestHumanApprovalDecision:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-ad-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-ad-001",
            reviewer_label="Alice",
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

    def test_record_approval_decision_creates_valid_decision(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            scope = self._make_scope()
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Approved",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            assert decision.decision == DECISION_APPROVED
            assert decision.request_id == request.request_id
            assert decision.reason == "Approved"

    def test_decision_id_format(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            scope = self._make_scope()
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Approved",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            assert decision.decision_id.startswith("hdec-")
            assert len(decision.decision_id) > len("hdec-")

    def test_decision_hash_is_computed(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            scope = self._make_scope()
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Approved",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            assert decision.decision_hash is not None
            assert len(decision.decision_hash) == 64

    def test_decision_references_existing_request_id(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            scope = self._make_scope()
            decision = record_approval_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Approved",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            looked_up = lookup_approval(decision.decision_id, repo_root)
            assert looked_up is not None
            assert looked_up.request_id == request.request_id
