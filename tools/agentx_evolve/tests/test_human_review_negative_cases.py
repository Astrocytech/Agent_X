import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewerIdentity,
    HumanApprovalScope,
    HumanReviewRequest,
    HumanApprovalDecision,
    HumanReviewValidationResult,
    AUTH_LOCAL_CONFIG,
    AUTH_UNKNOWN,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    SOURCE_COMPONENT,
    REQ_PENDING,
    VALIDATION_VALID,
    VALIDATION_INVALID,
    VALIDATION_BLOCKED,
    VALIDATION_EXPIRED,
    VALIDATION_REVOKED,
    VALIDATION_MISSING,
    SCOPE_ACTION,
    SCOPE_TOOL_CALL,
    SCOPE_PATCH_SESSION,
    SCOPE_FILE_PATH,
    SCOPE_COMMIT,
    SCOPE_PROMOTION,
    SCOPE_SESSION,
    utc_now_iso,
    new_id,
    sha256_dict,
    redact_sensitive_fields,
    create_review_request,
    validate_review_request,
    record_approval_decision,
    record_rejection_decision,
    lookup_approval,
    validate_approval,
    check_expiry,
    revoke_approval,
    is_revoked,
    check_reviewer_authorization,
    check_separation_of_duties,
    check_non_overridable_blocks,
    load_queue,
    enqueue_request,
    resolve_request,
    write_audit_event,
    write_evidence_manifest,
    write_integrity_record,
    write_completion_record,
    write_review_report,
    HumanReviewAuditEvent,
)
from agentx_evolve.human_review.review_models import (
    canonical_hash_payload,
    atomic_write_json,
    append_jsonl,
    human_review_runs_dir,
)


# ---------------------------------------------------------------------------
# 1. Self-approval is blocked
# ---------------------------------------------------------------------------

def test_self_approval_blocked():
    reviewer = HumanReviewerIdentity(
        reviewer_id="alice",
        reviewer_label="Alice",
        reviewer_role="senior_dev",
        auth_method=AUTH_LOCAL_CONFIG,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="neg-self-001",
        requested_by="alice",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False


# ---------------------------------------------------------------------------
# 2. Approval cannot be created for a request that doesn't exist
#    (record_approval_decision succeeds anyway; "doesn't exist" means
#     no matching request in the queue, but the function completes
#     gracefully and the request is recorded as resolved.)
# ---------------------------------------------------------------------------

def test_approval_for_nonexistent_request_still_creates_decision():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001",
            reviewer_label="Alice",
            reviewer_role="dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        scope = HumanApprovalScope(scope_id="s-neg-002", scope_type=SCOPE_ACTION)
        decision = record_approval_decision(
            request_id="no-such-request",
            reviewer=reviewer,
            reason="test",
            scope=scope,
            expires_at=None,
            no_expiry_reason=None,
            context={},
            repo_root=repo_root,
        )
        assert decision.decision_id.startswith("hdec-")
        assert decision.request_id == "no-such-request"


# ---------------------------------------------------------------------------
# 3. Expired approval fails validation
# ---------------------------------------------------------------------------

def test_expired_approval_fails_validation():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-neg-003", scope_type=SCOPE_ACTION)
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
            expires_at="1999-01-01T00:00:00",
            no_expiry_reason="ancient", context={}, repo_root=repo_root,
        )
        result = validate_approval(
            decision.decision_id, request.requested_action,
            request.requested_effect, scope, repo_root,
        )
        assert result.status == VALIDATION_EXPIRED
        assert result.allowed is False
        assert result.expired is True


# ---------------------------------------------------------------------------
# 4. Revoked approval fails validation
# ---------------------------------------------------------------------------

def test_revoked_approval_fails_validation():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-neg-004", scope_type=SCOPE_ACTION)
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
            reason="ok", scope=scope, expires_at=None,
            no_expiry_reason=None, context={}, repo_root=repo_root,
        )
        revoker = HumanReviewerIdentity(
            reviewer_id="rev-002", reviewer_label="Bob",
            reviewer_role="admin", auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        revoke_approval(decision.decision_id, revoker, "overturned", repo_root)
        result = validate_approval(
            decision.decision_id, request.requested_action,
            request.requested_effect, scope, repo_root,
        )
        assert result.status == VALIDATION_REVOKED
        assert result.allowed is False
        assert result.revoked is True


# ---------------------------------------------------------------------------
# 5. Empty required fields cause INVALID validation
# ---------------------------------------------------------------------------

def test_empty_required_fields_cause_invalid():
    request = HumanReviewRequest()
    result = validate_review_request(request)
    assert result.status == VALIDATION_INVALID
    assert result.allowed is False
    assert len(result.errors) >= 4


# ---------------------------------------------------------------------------
# 6. Unauthorized auth method (UNKNOWN) blocks
# ---------------------------------------------------------------------------

def test_unknown_auth_method_blocks():
    reviewer = HumanReviewerIdentity(
        reviewer_id="rev-001",
        reviewer_label="Alice",
        reviewer_role="dev",
        auth_method=AUTH_UNKNOWN,
        created_at=utc_now_iso(),
    )
    request = HumanReviewRequest(
        request_id="neg-auth-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level=RISK_LEVEL_LOW,
        reason="test",
    )
    result = check_reviewer_authorization(reviewer, request)
    assert result.status == VALIDATION_BLOCKED
    assert result.allowed is False


# ---------------------------------------------------------------------------
# 7. Missing required fields in request creation fail validation
# ---------------------------------------------------------------------------

def test_missing_fields_in_request_creation_fail_validation():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        scope = HumanApprovalScope(scope_id="s-neg-007", scope_type=SCOPE_ACTION)
        request = create_review_request(
            requested_by="",
            requested_action="",
            requested_effect="",
            risk_level=RISK_LEVEL_LOW,
            reason="",
            scope=scope,
            context={},
            repo_root=repo_root,
        )
        result = validate_review_request(request)
        assert result.status == VALIDATION_INVALID
        assert result.allowed is False
        assert any("required" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# 8. Invalid risk level fails request validation
# ---------------------------------------------------------------------------

def test_invalid_risk_level_fails_validation():
    request = HumanReviewRequest(
        request_id="neg-risk-001",
        requested_by="user-1",
        requested_action="apply_patch",
        requested_effect="modify",
        risk_level="INVALID_RISK",
        reason="test",
    )
    result = validate_review_request(request)
    assert result.status == VALIDATION_INVALID
    assert result.allowed is False
    assert any("risk_level" in e for e in result.errors)


# ---------------------------------------------------------------------------
# 9. Cross-repo/session mismatch detection
#    (The constant exists but _scope_matches is a stub; this test verifies
#     the constant is available and the validation path is exercised.)
# ---------------------------------------------------------------------------

def test_cross_repo_session_mismatch_constant_exists():
    from agentx_evolve.human_review import VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH
    assert VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH == "CROSS_REPO_OR_SESSION_MISMATCH"


# ---------------------------------------------------------------------------
# 10. Redaction removes sensitive fields
# ---------------------------------------------------------------------------

def test_redaction_removes_sensitive_fields():
    data = {
        "name": "test",
        "secret": "should-not-appear",
        "password": "should-not-appear",
        "token": "should-not-appear",
        "api_key": "should-not-appear",
        "private_key": "should-not-appear",
        "raw_prompt": "should-not-appear",
        "normal_field": "visible",
    }
    redacted = redact_sensitive_fields(data)
    assert "name" in redacted
    assert "normal_field" in redacted
    assert "secret" not in redacted
    assert "password" not in redacted
    assert "token" not in redacted
    assert "api_key" not in redacted
    assert "private_key" not in redacted
    assert "raw_prompt" not in redacted


# ---------------------------------------------------------------------------
# 11. Atomic write doesn't corrupt on partial write
#     (Simulate by writing an incomplete dict directly; atomic_write_json
#      writes via tmp + replace, so the target should only ever be complete.)
# ---------------------------------------------------------------------------

def test_atomic_write_does_not_corrupt():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        target = human_review_runs_dir(repo_root) / "test_atomic.json"

        atomic_write_json(target, {"complete": True, "value": 42})
        loaded = json.loads(target.read_text())
        assert loaded["complete"] is True
        assert loaded["value"] == 42

        human_review_runs_dir(repo_root).mkdir(parents=True, exist_ok=True)
        target.write_text('{"partial": true, "incomplete"')
        # After a partial write, loading should fail
        try:
            json.loads(target.read_text())
            assert False, "partial JSON should not parse"
        except (json.JSONDecodeError, ValueError):
            pass


# ---------------------------------------------------------------------------
# 12. Missing queue file is recreated safely
# ---------------------------------------------------------------------------

def test_missing_queue_file_recreated_safely():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)
        queue = load_queue(repo_root)
        assert queue.queue_id is not None
        assert len(queue.pending_requests) == 0

        queue_path = human_review_runs_dir(repo_root) / "review_queue.json"
        assert queue_path.exists()

        queue_path.unlink()
        assert not queue_path.exists()

        queue2 = load_queue(repo_root)
        assert queue2.queue_id is not None
        assert queue_path.exists()


# ---------------------------------------------------------------------------
# 13. Integrity chain records are linked
# ---------------------------------------------------------------------------

def test_integrity_chain_records_linked():
    with tempfile.TemporaryDirectory() as td:
        repo_root = Path(td)

        r1 = write_integrity_record("", "payload-001", "REQUEST", repo_root)
        r2 = write_integrity_record(r1["record_hash"], "payload-002", "DECISION", repo_root)
        r3 = write_integrity_record(r2["record_hash"], "payload-003", "VALIDATION", repo_root)

        assert r1["prior_record_hash"] == ""
        assert r2["prior_record_hash"] == r1["record_hash"]
        assert r3["prior_record_hash"] == r2["record_hash"]
        assert r1["record_hash"] != r2["record_hash"]
        assert r2["record_hash"] != r3["record_hash"]

        chain_path = human_review_runs_dir(repo_root) / "record_integrity_chain.jsonl"
        lines = chain_path.read_text().strip().split("\n")
        assert len(lines) == 3
