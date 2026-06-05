import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanApprovalDecision,
    HumanApprovalScope,
    HumanReviewerIdentity,
    check_approval_context_drift,
    invalidate_approval_on_context_drift,
    append_approval_invalidation_record,
    create_review_request,
    record_approval_decision,
    VALIDATION_VALID,
    AUTH_LOCAL_CONFIG,
    RISK_LEVEL_LOW,
    SCOPE_ACTION,
    utc_now_iso,
)


class TestApprovalInvalidation:
    def test_check_approval_context_drift_returns_valid_on_no_drift(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(
                scope_id="s-drift-001",
                scope_type=SCOPE_ACTION,
            )
            decision = HumanApprovalDecision(
                decision_id="d-drift-001",
                request_id="r-drift-001",
                decision="APPROVED",
                decided_at=utc_now_iso(),
                scope=scope,
            )
            current_context = {"session_id": "sess-1", "repo_identity_hash": "abc"}
            result = check_approval_context_drift(decision, current_context, repo_root)
            assert result.status == VALIDATION_VALID
            assert result.allowed is True

    def test_invalidate_approval_on_context_drift_writes_record(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(
                scope_id="s-drift-002",
                scope_type=SCOPE_ACTION,
                repo_identity_hash="repo-a",
            )
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
                reason="approved",
                scope=scope,
                expires_at=None,
                no_expiry_reason=None,
                context={},
                repo_root=repo_root,
            )
            current_context = {"repo_identity_hash": "repo-b"}
            result = invalidate_approval_on_context_drift(
                approval_decision_id=decision.decision_id,
                drift_reason="repo identity mismatch",
                current_context=current_context,
                repo_root=repo_root,
            )
            assert result["approval_decision_id"] == decision.decision_id
            assert "record" in result
            assert result["record"]["approval_decision_id"] == decision.decision_id
            assert result["record"]["reason"] == "repo identity mismatch"
            log_path = repo_root / ".agentx-init" / "human_review" / "approval_invalidation_history.jsonl"
            assert log_path.exists()

    def test_append_approval_invalidation_record_writes_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = append_approval_invalidation_record(
                approval_decision_id="d-inv-001",
                reason="context drift detected",
                context={"session_id": "sess-1"},
                repo_root=repo_root,
            )
            assert record["invalidation_id"].startswith("inv-")
            assert record["approval_decision_id"] == "d-inv-001"
            assert record["reason"] == "context drift detected"
            log_path = repo_root / ".agentx-init" / "human_review" / "approval_invalidation_history.jsonl"
            assert log_path.exists()
            with open(log_path) as f:
                line = f.readline().strip()
                assert "d-inv-001" in line
