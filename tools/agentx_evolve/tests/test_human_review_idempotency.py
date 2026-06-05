import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    AUTH_LOCAL_CONFIG,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    utc_now_iso,
    create_review_request,
    record_approval_decision,
)
from agentx_evolve.human_review.approval_decisions import record_approval_decision
from agentx_evolve.human_review.review_models import (
    human_review_runs_dir,
    new_id,
)
import json


def test_create_review_request_with_same_params_creates_distinct_requests():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-idem-001", scope_type=SCOPE_ACTION)
        req1 = create_review_request(
            requested_by="user-1", requested_action="apply_patch",
            requested_effect="modify", risk_level=RISK_LEVEL_LOW,
            reason="test", scope=scope, context={}, repo_root=repo_root,
        )
        req2 = create_review_request(
            requested_by="user-1", requested_action="apply_patch",
            requested_effect="modify", risk_level=RISK_LEVEL_LOW,
            reason="test", scope=scope, context={}, repo_root=repo_root,
        )
        assert req1.request_id != req2.request_id
        assert req1.request_id.startswith("hreq-")
        assert req2.request_id.startswith("hreq-")


def test_same_decision_id_not_written_twice():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-idem-002", scope_type=SCOPE_ACTION)
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
        decision1 = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        decision2 = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        assert decision1.decision_id != decision2.decision_id
        history_path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
        lines = [json.loads(l) for l in history_path.read_text().strip().split("\n") if l.strip()]
        ids = [l["decision_id"] for l in lines]
        assert len(ids) == len(set(ids))


def test_multiple_approvals_for_same_request_are_separate_records():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-idem-003", scope_type=SCOPE_ACTION)
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
        d1 = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        d2 = record_approval_decision(
            request_id=request.request_id, reviewer=reviewer,
            reason="ok", scope=scope,
            expires_at=None, no_expiry_reason=None,
            context={}, repo_root=repo_root,
        )
        assert d1.decision_id != d2.decision_id
        assert d1.request_id == d2.request_id
        history_path = human_review_runs_dir(repo_root) / "approval_decision_history.jsonl"
        lines = [json.loads(l) for l in history_path.read_text().strip().split("\n") if l.strip()]
        ids_for_request = [l["decision_id"] for l in lines if l["request_id"] == request.request_id]
        assert len(ids_for_request) == 2
