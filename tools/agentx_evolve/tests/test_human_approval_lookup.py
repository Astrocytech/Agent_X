import os
import sys
import tempfile
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    AUTH_LOCAL_CONFIG,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    VALIDATION_MISSING,
    VALIDATION_VALID,
    utc_now_iso,
    create_review_request,
    record_approval_decision,
)
from agentx_evolve.human_review.approval_lookup import (
    lookup_approval,
    find_active_approval_for_action,
    validate_approval_id,
)
from agentx_evolve.human_review.review_models import human_review_runs_dir


def test_lookup_approval_returns_decision_by_id():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-lkp-001", scope_type=SCOPE_ACTION)
        request = create_review_request(
            requested_by="user-1", requested_action="apply_patch",
            requested_effect="modify", risk_level=RISK_LEVEL_LOW,
            reason="test", scope=scope, context={}, repo_root=repo_root,
        )
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001", reviewer_label="Alice",
            reviewer_role="dev", auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        decision = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        found = lookup_approval(decision.decision_id, repo_root)
        assert found is not None
        assert found.decision_id == decision.decision_id
        assert found.request_id == request.request_id


def test_lookup_approval_returns_none_for_missing_id():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        found = lookup_approval("nonexistent-id", repo_root)
        assert found is None


def test_find_active_approval_for_action_returns_active_approval():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-lkp-002", scope_type=SCOPE_ACTION)
        request = create_review_request(
            requested_by="user-1", requested_action="apply_patch",
            requested_effect="modify", risk_level=RISK_LEVEL_LOW,
            reason="test", scope=scope, context={}, repo_root=repo_root,
        )
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001", reviewer_label="Alice",
            reviewer_role="dev", auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        decision = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        active = find_active_approval_for_action(
            "apply_patch", "modify", {}, repo_root,
        )
        assert active is not None
        assert active.decision_id == decision.decision_id


def test_find_active_approval_for_action_returns_none_when_none_exists():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        active = find_active_approval_for_action(
            "non_existent", "modify", {}, repo_root,
        )
        assert active is None


def test_validate_approval_id_returns_missing_for_none():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        result = validate_approval_id(None, "apply_patch", "modify", {}, repo_root)
        assert result.status == VALIDATION_MISSING
        assert result.allowed is False
