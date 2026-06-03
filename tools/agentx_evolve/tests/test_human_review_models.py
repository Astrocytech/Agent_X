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
    HumanRejectionDecision,
    HumanDeferralDecision,
    HumanClarificationRequest,
    HumanApprovalRevocation,
    HumanReviewValidationResult,
    HumanReviewQueue,
    HumanReviewAuditEvent,
    HumanReviewEvidenceManifest,
    HumanReviewCompletionRecord,
    DECISION_REQUESTED,
    DECISION_APPROVED,
    DECISION_REJECTED,
    DECISION_DEFERRED,
    DECISION_NEEDS_CLARIFICATION,
    DECISION_REVOKED,
    DECISION_EXPIRED,
    DECISION_INVALID,
    ALL_DECISIONS,
    VALIDATION_VALID,
    VALIDATION_INVALID,
    VALIDATION_EXPIRED,
    VALIDATION_REVOKED,
    VALIDATION_OUT_OF_SCOPE,
    VALIDATION_MISSING,
    VALIDATION_FORGED_OR_UNTRUSTED,
    VALIDATION_STALE,
    VALIDATION_REPLAYED,
    VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH,
    VALIDATION_BLOCKED,
    ALL_VALIDATION_STATUSES,
    REQ_PENDING,
    REQ_APPROVED,
    REQ_REJECTED,
    REQ_DEFERRED,
    REQ_NEEDS_CLARIFICATION,
    REQ_CLOSED,
    REQ_EXPIRED,
    REQ_REVOKED,
    REQ_INVALID,
    ALL_REQUEST_STATUSES,
    SCOPE_ACTION,
    SCOPE_TOOL_CALL,
    SCOPE_PATCH_SESSION,
    SCOPE_FILE_PATH,
    SCOPE_COMMIT,
    SCOPE_PROMOTION,
    SCOPE_SESSION,
    ALL_SCOPE_TYPES,
    AUTH_LOCAL_CONFIG,
    AUTH_MANUAL_RECORD,
    AUTH_SIGNED_RECORD,
    AUTH_EXTERNAL_ASSERTION,
    AUTH_UNKNOWN,
    ALL_AUTH_METHODS,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    ALL_RISK_LEVELS,
    SOURCE_COMPONENT,
    SCHEMA_VERSION,
    utc_now_iso,
    new_id,
    to_dict,
    sha256_dict,
    sha256_file,
    redact_sensitive_fields,
    load_queue,
    enqueue_request,
    resolve_request,
    create_review_request,
    validate_review_request,
    record_approval_decision,
    record_rejection_decision,
    record_deferral_decision,
    record_clarification_request,
    lookup_approval,
    validate_approval,
    check_expiry,
    revoke_approval,
    is_revoked,
    check_reviewer_authorization,
    check_separation_of_duties,
    check_non_overridable_blocks,
    write_audit_event,
    write_evidence_manifest,
    write_review_report,
    write_completion_record,
    write_integrity_record,
)
from agentx_evolve.human_review.review_models import canonical_hash_payload


# ---------------------------------------------------------------------------
# 1. Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_decision_constants(self):
        assert DECISION_REQUESTED == "REQUESTED"
        assert DECISION_APPROVED == "APPROVED"
        assert DECISION_REJECTED == "REJECTED"
        assert DECISION_DEFERRED == "DEFERRED"
        assert DECISION_NEEDS_CLARIFICATION == "NEEDS_CLARIFICATION"
        assert DECISION_REVOKED == "REVOKED"
        assert DECISION_EXPIRED == "EXPIRED"
        assert DECISION_INVALID == "INVALID"
        assert len(ALL_DECISIONS) == 8

    def test_validation_constants(self):
        assert VALIDATION_VALID == "VALID"
        assert VALIDATION_INVALID == "INVALID"
        assert VALIDATION_EXPIRED == "EXPIRED"
        assert VALIDATION_REVOKED == "REVOKED"
        assert VALIDATION_OUT_OF_SCOPE == "OUT_OF_SCOPE"
        assert VALIDATION_MISSING == "MISSING"
        assert VALIDATION_FORGED_OR_UNTRUSTED == "FORGED_OR_UNTRUSTED"
        assert VALIDATION_STALE == "STALE"
        assert VALIDATION_REPLAYED == "REPLAYED"
        assert VALIDATION_CROSS_REPO_OR_SESSION_MISMATCH == "CROSS_REPO_OR_SESSION_MISMATCH"
        assert VALIDATION_BLOCKED == "BLOCKED"
        assert len(ALL_VALIDATION_STATUSES) == 11

    def test_request_status_constants(self):
        assert REQ_PENDING == "PENDING"
        assert REQ_APPROVED == "APPROVED"
        assert REQ_REJECTED == "REJECTED"
        assert REQ_DEFERRED == "DEFERRED"
        assert REQ_NEEDS_CLARIFICATION == "NEEDS_CLARIFICATION"
        assert REQ_CLOSED == "CLOSED"
        assert REQ_EXPIRED == "EXPIRED"
        assert REQ_REVOKED == "REVOKED"
        assert REQ_INVALID == "INVALID"
        assert len(ALL_REQUEST_STATUSES) == 9

    def test_scope_type_constants(self):
        assert SCOPE_ACTION == "ACTION"
        assert SCOPE_TOOL_CALL == "TOOL_CALL"
        assert SCOPE_PATCH_SESSION == "PATCH_SESSION"
        assert SCOPE_FILE_PATH == "FILE_PATH"
        assert SCOPE_COMMIT == "COMMIT"
        assert SCOPE_PROMOTION == "PROMOTION"
        assert SCOPE_SESSION == "SESSION"
        assert len(ALL_SCOPE_TYPES) == 7

    def test_auth_method_constants(self):
        assert AUTH_LOCAL_CONFIG == "LOCAL_CONFIG"
        assert AUTH_MANUAL_RECORD == "MANUAL_RECORD"
        assert AUTH_SIGNED_RECORD == "SIGNED_RECORD"
        assert AUTH_EXTERNAL_ASSERTION == "EXTERNAL_ASSERTION"
        assert AUTH_UNKNOWN == "UNKNOWN"
        assert len(ALL_AUTH_METHODS) == 5

    def test_risk_level_constants(self):
        assert RISK_LEVEL_LOW == "LOW"
        assert RISK_LEVEL_MEDIUM == "MEDIUM"
        assert RISK_LEVEL_HIGH == "HIGH"
        assert RISK_LEVEL_CRITICAL == "CRITICAL"
        assert len(ALL_RISK_LEVELS) == 4

    def test_component_and_version(self):
        assert SOURCE_COMPONENT == "HumanReviewApproval"
        assert SCHEMA_VERSION == "1.0"


# ---------------------------------------------------------------------------
# 2-3. Dataclass instantiation and serialisation
# ---------------------------------------------------------------------------

class TestDataclassInstantiation:
    def test_human_reviewer_identity_defaults(self):
        obj = HumanReviewerIdentity()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "human_reviewer_identity.schema.json"
        assert obj.auth_method == AUTH_UNKNOWN
        assert obj.auth_evidence_refs == []

    def test_human_approval_scope_defaults(self):
        obj = HumanApprovalScope()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.scope_type == SCOPE_ACTION
        assert obj.file_paths == []

    def test_human_review_request_defaults(self):
        obj = HumanReviewRequest()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.status == REQ_PENDING
        assert obj.source_component == SOURCE_COMPONENT
        assert obj.risk_level == RISK_LEVEL_LOW

    def test_human_approval_decision_defaults(self):
        obj = HumanApprovalDecision()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.decision == DECISION_APPROVED

    def test_human_rejection_decision_defaults(self):
        obj = HumanRejectionDecision()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.decision == DECISION_REJECTED

    def test_human_deferral_decision_defaults(self):
        obj = HumanDeferralDecision()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.decision == DECISION_DEFERRED

    def test_human_clarification_request_defaults(self):
        obj = HumanClarificationRequest()
        assert obj.schema_version == SCHEMA_VERSION

    def test_human_approval_revocation_defaults(self):
        obj = HumanApprovalRevocation()
        assert obj.schema_version == SCHEMA_VERSION

    def test_human_review_validation_result_defaults(self):
        obj = HumanReviewValidationResult()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.status == VALIDATION_INVALID

    def test_human_review_queue_defaults(self):
        obj = HumanReviewQueue()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.queue_version == 1

    def test_human_review_audit_event_defaults(self):
        obj = HumanReviewAuditEvent()
        assert obj.schema_version == SCHEMA_VERSION

    def test_human_review_evidence_manifest_defaults(self):
        obj = HumanReviewEvidenceManifest()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"

    def test_human_review_completion_record_defaults(self):
        obj = HumanReviewCompletionRecord()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"

    def test_to_dict_serialization(self):
        obj = HumanReviewRequest(request_id="test-001", requested_by="alice")
        d = obj.to_dict()
        assert d["request_id"] == "test-001"
        assert d["requested_by"] == "alice"
        assert d["schema_version"] == SCHEMA_VERSION
        assert d["status"] == REQ_PENDING

    def test_to_dict_nested(self):
        scope = HumanApprovalScope(scope_id="s-001")
        req = HumanReviewRequest(request_id="r-001", scope=scope)
        d = req.to_dict()
        assert d["scope"]["scope_id"] == "s-001"
        assert d["scope"]["scope_type"] == SCOPE_ACTION


# ---------------------------------------------------------------------------
# 4-7. Utility functions
# ---------------------------------------------------------------------------

class TestSha256Dict:
    def test_deterministic(self):
        data = {"a": 1, "b": 2}
        h1 = sha256_dict(data)
        h2 = sha256_dict(data)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64

    def test_different_inputs(self):
        h1 = sha256_dict({"a": 1})
        h2 = sha256_dict({"a": 2})
        assert h1 != h2


class TestCanonicalHashPayload:
    def test_removes_hash_fields(self):
        data = {
            "request_hash": "abc",
            "decision_hash": "def",
            "revocation_hash": "ghi",
            "clarification_hash": "jkl",
            "record_hash": "mno",
            "payload_hash": "pqr",
            "name": "test",
        }
        result = canonical_hash_payload(data)
        assert "name" in result
        for key in ("request_hash", "decision_hash", "revocation_hash",
                    "clarification_hash", "record_hash", "payload_hash"):
            assert key not in result

    def test_preserves_other_fields(self):
        data = {"name": "test", "value": 42}
        result = canonical_hash_payload(data)
        assert result == data


class TestRedactSensitiveFields:
    def test_removes_secrets(self):
        data = {"secret": "s3cr3t", "password": "p@ss", "token": "tok",
                "api_key": "key", "private_key": "pk", "raw_prompt": "prompt",
                "name": "visible"}
        result = redact_sensitive_fields(data)
        assert "name" in result
        for key in ("secret", "password", "token", "api_key", "private_key", "raw_prompt"):
            assert key not in result

    def test_case_insensitive(self):
        data = {"Secret": "val", "PASSWORD": "val"}
        result = redact_sensitive_fields(data)
        assert "Secret" not in result
        assert "PASSWORD" not in result


# ---------------------------------------------------------------------------
# 8-10. Review request creation and validation
# ---------------------------------------------------------------------------

class TestReviewRequest:
    def test_create_review_request(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-cr-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify_files",
                risk_level=RISK_LEVEL_LOW,
                reason="Test reason",
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            assert request.request_id.startswith("hreq-")
            assert request.requested_by == "user-1"
            assert request.requested_action == "apply_patch"
            assert request.requested_effect == "modify_files"
            assert request.risk_level == RISK_LEVEL_LOW
            assert request.status == REQ_PENDING
            assert request.request_hash is not None
            assert len(request.request_hash) == 64

    def test_validate_valid_request(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-val-001", scope_type=SCOPE_ACTION)
            request = create_review_request(
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify_files",
                risk_level=RISK_LEVEL_LOW,
                reason="Test reason",
                scope=scope,
                context={},
                repo_root=repo_root,
            )
            result = validate_review_request(request)
            assert result.status == VALIDATION_VALID
            assert result.allowed is True

    def test_validate_invalid_request_missing_fields(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = HumanReviewRequest()
            result = validate_review_request(request)
            assert result.status == VALIDATION_INVALID
            assert result.allowed is False
            assert len(result.errors) > 0


# ---------------------------------------------------------------------------
# 11-14. Record decisions
# ---------------------------------------------------------------------------

class TestRecordDecisions:
    def _make_scope(self) -> HumanApprovalScope:
        return HumanApprovalScope(scope_id="s-dec-001", scope_type=SCOPE_ACTION)

    def _make_reviewer(self) -> HumanReviewerIdentity:
        return HumanReviewerIdentity(
            reviewer_id="rev-001",
            reviewer_label="Alice Reviewer",
            reviewer_role="senior_dev",
            auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )

    def _make_request(self, repo_root: Path) -> HumanReviewRequest:
        scope = self._make_scope()
        return create_review_request(
            requested_by="user-1",
            requested_action="apply_patch",
            requested_effect="modify_files",
            risk_level=RISK_LEVEL_LOW,
            reason="Test reason",
            scope=scope,
            context={},
            repo_root=repo_root,
        )

    def test_record_approval_decision(self):
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
            assert decision.request_id == request.request_id
            assert decision.decision == DECISION_APPROVED
            assert decision.decision_hash is not None
            assert len(decision.decision_hash) == 64

    def test_record_rejection_decision(self):
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
            assert decision.decision_id.startswith("hdec-")
            assert decision.decision == DECISION_REJECTED
            assert decision.decision_hash is not None

    def test_record_deferral_decision(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            decision = record_deferral_decision(
                request_id=request.request_id,
                reviewer=reviewer,
                reason="Deferred",
                deferred_until="2026-12-31T00:00:00",
                context={},
                repo_root=repo_root,
            )
            assert decision.decision_id.startswith("hdec-")
            assert decision.decision == DECISION_DEFERRED
            assert decision.decision_hash is not None
            assert decision.deferred_until == "2026-12-31T00:00:00"

    def test_record_clarification_request(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            request = self._make_request(repo_root)
            reviewer = self._make_reviewer()
            clarification = record_clarification_request(
                request_id=request.request_id,
                reviewer=reviewer,
                question="What does this patch do?",
                context={},
                repo_root=repo_root,
            )
            assert clarification.clarification_id.startswith("hcla-")
            assert clarification.clarification_question == "What does this patch do?"
            assert clarification.clarification_hash is not None


# ---------------------------------------------------------------------------
# 15-16. Lookup approval
# ---------------------------------------------------------------------------

class TestLookupApproval:
    def test_lookup_approval_by_id(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-lk-001", scope_type=SCOPE_ACTION)
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
            looked_up = lookup_approval(decision.decision_id, repo_root)
            assert looked_up is not None
            assert looked_up.decision_id == decision.decision_id
            assert looked_up.request_id == request.request_id

    def test_lookup_nonexistent_approval_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            result = lookup_approval("nonexistent-decision-id", repo_root)
            assert result is None


# ---------------------------------------------------------------------------
# 17. Validate approval against scope (VALID)
# ---------------------------------------------------------------------------

class TestValidateApproval:
    def test_validate_approval_valid(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-vld-001", scope_type=SCOPE_ACTION)
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
            result = validate_approval(
                decision.decision_id, request.requested_action,
                request.requested_effect, scope, repo_root,
            )
            assert result.status == VALIDATION_VALID
            assert result.allowed is True

    def test_validate_expired_approval(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-exp-001", scope_type=SCOPE_ACTION)
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
                expires_at="2000-01-01T00:00:00",
                no_expiry_reason="past", context={}, repo_root=repo_root,
            )
            result = validate_approval(
                decision.decision_id, request.requested_action,
                request.requested_effect, scope, repo_root,
            )
            assert result.status == VALIDATION_EXPIRED
            assert result.allowed is False
            assert result.expired is True

    def test_validate_revoked_approval(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-rev-001", scope_type=SCOPE_ACTION)
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

    def test_validate_missing_approval(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-ms-001", scope_type=SCOPE_ACTION)
            result = validate_approval(
                "no-such-id", "apply_patch", "modify", scope, repo_root,
            )
            assert result.status == VALIDATION_MISSING
            assert result.allowed is False


# ---------------------------------------------------------------------------
# 21. Revoke approval & is_revoked
# ---------------------------------------------------------------------------

class TestRevokeApproval:
    def test_revoke_and_check(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-rvk-001", scope_type=SCOPE_ACTION)
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
            revocation = revoke_approval(decision.decision_id, revoker, "overturned", repo_root)
            assert revocation.revocation_id.startswith("hrev-")
            assert is_revoked(decision.decision_id, repo_root) is True
            assert is_revoked("no-such-id", repo_root) is False


# ---------------------------------------------------------------------------
# 22. Check expiry: no expiry = not expired
# ---------------------------------------------------------------------------

class TestCheckExpiry:
    def test_no_expiry_not_expired(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(scope_id="s-ce-001", scope_type=SCOPE_ACTION)
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
            result = check_expiry(decision.decision_id, repo_root)
            assert result.expired is False


# ---------------------------------------------------------------------------
# 23-25. Reviewer authorization
# ---------------------------------------------------------------------------

class TestReviewerAuthorization:
    def test_different_people_valid(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001", reviewer_label="Alice",
            reviewer_role="senior_dev", auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-001", requested_by="user-1",
            requested_action="apply_patch", requested_effect="modify",
            risk_level=RISK_LEVEL_LOW, reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == "VALID"
        assert result.allowed is True

    def test_self_approval_blocked(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="user-1", reviewer_label="Alice",
            reviewer_role="senior_dev", auth_method=AUTH_LOCAL_CONFIG,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-002", requested_by="user-1",
            requested_action="apply_patch", requested_effect="modify",
            risk_level=RISK_LEVEL_LOW, reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False

    def test_unknown_auth_blocked(self):
        reviewer = HumanReviewerIdentity(
            reviewer_id="rev-001", reviewer_label="Alice",
            reviewer_role="senior_dev", auth_method=AUTH_UNKNOWN,
            created_at=utc_now_iso(),
        )
        request = HumanReviewRequest(
            request_id="r-003", requested_by="user-2",
            requested_action="apply_patch", requested_effect="modify",
            risk_level=RISK_LEVEL_LOW, reason="test",
        )
        result = check_reviewer_authorization(reviewer, request)
        assert result.status == VALIDATION_BLOCKED
        assert result.allowed is False


# ---------------------------------------------------------------------------
# 26-27. Separation of duties
# ---------------------------------------------------------------------------

class TestSeparationOfDuties:
    def test_different_people_returns_true(self):
        assert check_separation_of_duties("user-1", "rev-001") is True

    def test_same_person_returns_false(self):
        assert check_separation_of_duties("alice", "alice") is False


# ---------------------------------------------------------------------------
# 28. Non-overridable blocks
# ---------------------------------------------------------------------------

class TestNonOverridableBlocks:
    def test_all_valid_returns_true(self):
        assert check_non_overridable_blocks(True, True, True) is True

    def test_policy_blocked_returns_false(self):
        assert check_non_overridable_blocks(False, True, True) is False

    def test_sandbox_blocked_returns_false(self):
        assert check_non_overridable_blocks(True, False, True) is False

    def test_schema_invalid_returns_false(self):
        assert check_non_overridable_blocks(True, True, False) is False

    def test_all_blocked_returns_false(self):
        assert check_non_overridable_blocks(False, False, False) is False


# ---------------------------------------------------------------------------
# 29. Write audit event
# ---------------------------------------------------------------------------

class TestWriteAuditEvent:
    def test_write_audit_event(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            event = write_audit_event(
                event_type="REVIEW_STARTED",
                request_id="r-001",
                decision_id="d-001",
                status="OK",
                message="Review initiated",
                repo_root=repo_root,
            )
            assert event.audit_id.startswith("aud-")
            assert event.event_type == "REVIEW_STARTED"
            assert event.status == "OK"
            audit_path = repo_root / ".agentx-init" / "human_review" / "human_review_audit.jsonl"
            assert audit_path.exists()


# ---------------------------------------------------------------------------
# 30. Write evidence manifest
# ---------------------------------------------------------------------------

class TestWriteEvidenceManifest:
    def test_write_evidence_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            manifest = write_evidence_manifest(repo_root, validated_commit="abc123")
            assert manifest.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"
            manifest_path = repo_root / ".agentx-init" / "human_review" / "human_review_evidence_manifest.json"
            assert manifest_path.exists()


# ---------------------------------------------------------------------------
# 31. Write integrity record
# ---------------------------------------------------------------------------

class TestWriteIntegrityRecord:
    def test_write_integrity_record(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = write_integrity_record(
                prior_record_hash="",
                payload_hash="payload-abc",
                record_type="REQUEST",
                repo_root=repo_root,
            )
            assert record["record_id"].startswith("int-")
            assert record["record_hash"] != ""
            assert record["prior_record_hash"] == ""
            assert record["payload_hash"] == "payload-abc"
            assert record["record_type"] == "REQUEST"
            chain_path = repo_root / ".agentx-init" / "human_review" / "record_integrity_chain.jsonl"
            assert chain_path.exists()


# ---------------------------------------------------------------------------
# 32. Queue operations: load, enqueue, resolve
# ---------------------------------------------------------------------------

class TestQueueOperations:
    def test_queue_load_enqueue_resolve(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            queue = load_queue(repo_root)
            assert queue.queue_id.startswith("q-")
            assert len(queue.pending_requests) == 0

            req = HumanReviewRequest(
                request_id="q-test-001",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=RISK_LEVEL_LOW,
                reason="queue test",
                status=REQ_PENDING,
            )
            enqueue_request(req, repo_root)

            queue = load_queue(repo_root)
            ids = [r.request_id for r in queue.pending_requests]
            assert "q-test-001" in ids

            resolve_request("q-test-001", repo_root)
            queue = load_queue(repo_root)
            ids = [r.request_id for r in queue.pending_requests]
            assert "q-test-001" not in ids
            assert "q-test-001" in queue.resolved_requests


# ---------------------------------------------------------------------------
# 33. Write completion record
# ---------------------------------------------------------------------------

class TestWriteCompletionRecord:
    def test_write_completion_record(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = write_completion_record(
                repo_root=repo_root,
                validated_commit="abc123",
                final_decision="DONE",
                files_created=["test_file.py"],
                schemas_created=["test.schema.json"],
                tests_created=["test_test.py"],
            )
            assert record.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"
            assert record.status == "DONE"
            assert record.final_decision == "DONE"
            assert record.validated_commit == "abc123"
            assert "test_file.py" in record.files_created_or_changed
            assert record.completion_record_sha256 != ""


# ---------------------------------------------------------------------------
# 34. Validate approval with scope (scope match case)
# ---------------------------------------------------------------------------

class TestValidateApprovalWithScope:
    def test_validate_approval_with_scope(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            scope = HumanApprovalScope(
                scope_id="s-scp-001",
                scope_type=SCOPE_ACTION,
                action_id="action-001",
            )
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
            result = validate_approval(
                decision.decision_id,
                request.requested_action,
                request.requested_effect,
                scope,
                repo_root,
            )
            assert result.status == VALIDATION_VALID
            assert result.allowed is True
            assert result.matched_scope is True
