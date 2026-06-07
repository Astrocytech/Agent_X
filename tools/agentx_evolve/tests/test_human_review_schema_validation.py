import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import jsonschema
from jsonschema import Draft7Validator

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"

SCHEMA_FILES = [
    "human_review_request.schema.json",
    "human_review_queue.schema.json",
    "human_approval_decision.schema.json",
    "human_rejection_decision.schema.json",
    "human_review_deferral.schema.json",
    "human_clarification_request.schema.json",
    "human_approval_scope.schema.json",
    "human_approval_expiry.schema.json",
    "human_approval_revocation.schema.json",
    "human_reviewer_identity.schema.json",
    "human_review_identity_assurance.schema.json",
    "human_review_quorum.schema.json",
    "human_approval_consumption.schema.json",
    "human_approval_lock.schema.json",
    "human_review_evidence.schema.json",
    "human_review_audit.schema.json",
    "human_review_authorization_policy.schema.json",
    "separation_of_duties_rule.schema.json",
    "human_review_integrity_record.schema.json",
    "approval_invalidation_record.schema.json",
    "human_review_validation_result.schema.json",
    "human_review_evidence_manifest.schema.json",
    "human_review_report.schema.json",
    "human_review_review_report.schema.json",
    "human_review_decision.schema.json",
]


def _load_schema(name):
    path = SCHEMAS_DIR / name
    with open(path) as f:
        return json.load(f)


class TestSchemaDraft7Valid:
    def test_all_schemas_are_valid_draft7(self):
        for fname in SCHEMA_FILES:
            schema = _load_schema(fname)
            Draft7Validator.check_schema(schema)


_SCOPE_DEF = {
    "type": "object",
    "properties": {
        "schema_version": {"type": "string"},
        "schema_id": {"type": "string"},
        "scope_id": {"type": "string"},
        "scope_type": {"type": "string"},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "errors": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["schema_version", "schema_id", "scope_id", "scope_type", "warnings", "errors"],
}
_SCOPE_RESOLVER = jsonschema.RefResolver.from_schema(
    {"definitions": {"Scope": _SCOPE_DEF}}
)


class TestHumanReviewRequestSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_request.schema.json")
        _SCOPE_RESOLVER.store["human_review_request.schema.json"] = self.schema
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_request.schema.json",
            "source_component": "HumanReviewApproval",
            "request_id": "hreq-001",
            "created_at": "2026-01-01T00:00:00",
            "requested_by": "user-1",
            "requested_action": "apply_patch",
            "requested_effect": "modify",
            "risk_level": "LOW",
            "reason": "test",
            "scope": {"type": "function", "path": "src/main.py", "description": "Scope of review"},
            "status": "PENDING",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        v = Draft7Validator(self.schema, resolver=_SCOPE_RESOLVER)
        v.validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["request_id"]
        v = Draft7Validator(self.schema, resolver=_SCOPE_RESOLVER)
        errors = list(v.iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["risk_level"] = "INVALID"
        v = Draft7Validator(self.schema, resolver=_SCOPE_RESOLVER)
        errors = list(v.iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewQueueSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_queue.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_queue.schema.json",
            "source_component": "HumanReviewApproval",
            "queue_id": "q-001",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "pending_requests": [],
            "resolved_requests": [],
            "deferred_requests": [],
            "clarification_requests": [],
            "queue_version": 1,
            "queue_hash": "abc",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["queue_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalDecisionSchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_decision.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_decision.schema.json",
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-001",
            "request_id": "r-001",
            "decided_at": "2026-01-01T00:00:00",
            "reviewer": {"reviewer_id": "rev-001"},
            "decision": "APPROVED",
            "reason": "ok",
            "scope": {"scope_id": "s-001"},
            "expires_at": "",
            "no_expiry_reason": "",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "",
            "decision_hash": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["decision_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["decision"] = "BAD_VALUE"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanRejectionDecisionSchema:
    def setup_method(self):
        self.schema = _load_schema("human_rejection_decision.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_rejection_decision.schema.json",
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-002",
            "request_id": "r-001",
            "decided_at": "2026-01-01T00:00:00",
            "reviewer": {"reviewer_id": "rev-001"},
            "decision": "REJECTED",
            "reason": "not needed",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "",
            "decision_hash": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["reason"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewDeferralSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_deferral.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_deferral.schema.json",
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-003",
            "request_id": "r-001",
            "decided_at": "2026-01-01T00:00:00",
            "reviewer": {"reviewer_id": "rev-001"},
            "decision": "DEFERRED",
            "reason": "busy",
            "deferred_until": "2026-12-31T00:00:00",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "",
            "decision_hash": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["deferred_until"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanClarificationRequestSchema:
    def setup_method(self):
        self.schema = _load_schema("human_clarification_request.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_clarification_request.schema.json",
            "source_component": "HumanReviewApproval",
            "clarification_id": "hcla-001",
            "request_id": "r-001",
            "created_at": "2026-01-01T00:00:00",
            "reviewer": {"reviewer_id": "rev-001"},
            "clarification_question": "What does this do?",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "",
            "clarification_hash": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["clarification_question"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalScopeSchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_scope.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_scope.schema.json",
            "scope_id": "s-001",
            "scope_type": "ACTION",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["scope_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["scope_type"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalExpirySchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_expiry.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_expiry.schema.json",
            "source_component": "HumanReviewApproval",
            "expiry_id": "exp-001",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "expired": False,
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["expiry_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalRevocationSchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_revocation.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_revocation.schema.json",
            "source_component": "HumanReviewApproval",
            "revocation_id": "hrev-001",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "revoked_at": "2026-01-01T00:00:00",
            "revoked_by": {"reviewer_id": "rev-002"},
            "reason": "overturned",
            "artifact_refs": [],
            "evidence_refs": [],
            "revocation_hash": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["reason"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewerIdentitySchema:
    def setup_method(self):
        self.schema = _load_schema("human_reviewer_identity.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_reviewer_identity.schema.json",
            "reviewer_id": "rev-001",
            "reviewer_label": "Alice",
            "reviewer_role": "senior_dev",
            "auth_method": "LOCAL_CONFIG",
            "auth_evidence_refs": [],
            "created_at": "2026-01-01T00:00:00",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["reviewer_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["auth_method"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewIdentityAssuranceSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_identity_assurance.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_identity_assurance.schema.json",
            "source_component": "HumanReviewApproval",
            "assurance_id": "ass-001",
            "reviewer_id": "rev-001",
            "reviewer_label": "Alice",
            "reviewer_role": "senior_dev",
            "auth_method": "LOCAL_CONFIG",
            "auth_evidence_refs": [],
            "verified_at": "2026-01-01T00:00:00",
            "verification_status": "VERIFIED",
            "verified_by": "admin-001",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["verification_status"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["verification_status"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewQuorumSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_quorum.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_quorum.schema.json",
            "source_component": "HumanReviewApproval",
            "quorum_id": "qrm-001",
            "request_id": "r-001",
            "required_count": 2,
            "current_count": 1,
            "reviewers": [],
            "status": "PENDING",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["quorum_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["status"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalConsumptionSchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_consumption.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_consumption.schema.json",
            "source_component": "HumanReviewApproval",
            "consumption_id": "csm-001",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "consumer_id": "svc-001",
            "max_uses": 5,
            "current_uses": 0,
            "status": "AVAILABLE",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["consumption_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["status"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanApprovalLockSchema:
    def setup_method(self):
        self.schema = _load_schema("human_approval_lock.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_approval_lock.schema.json",
            "source_component": "HumanReviewApproval",
            "lock_id": "lck-001",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "locked_at": "2026-01-01T00:00:00",
            "locked_by": "svc-001",
            "lock_version": 1,
            "status": "LOCKED",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["lock_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["status"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewEvidenceSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_evidence.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_evidence.schema.json",
            "source_component": "HumanReviewApproval",
            "evidence_id": "ev-001",
            "request_id": "r-001",
            "decision_id": "d-001",
            "event_type": "APPROVED",
            "timestamp": "2026-01-01T00:00:00",
            "artifact_refs": [],
            "evidence_refs": [],
            "payload_hash": "abc",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["evidence_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["event_type"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewAuditSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_audit.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_audit.schema.json",
            "source_component": "HumanReviewApproval",
            "audit_id": "aud-001",
            "timestamp": "2026-01-01T00:00:00",
            "event_type": "REVIEW_STARTED",
            "request_id": "r-001",
            "decision_id": "d-001",
            "validation_id": "",
            "status": "OK",
            "message": "",
            "artifact_refs": [],
            "evidence_refs": [],
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["audit_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewAuthorizationPolicySchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_authorization_policy.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_authorization_policy.schema.json",
            "source_component": "HumanReviewApproval",
            "policy_id": "pol-001",
            "reviewer_role": "senior_dev",
            "allowed_risk_levels": ["LOW", "MEDIUM"],
            "allowed_action_types": ["apply_patch"],
            "requires_quorum": False,
            "quorum_minimum": 1,
            "self_approval_blocked": True,
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["policy_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestSeparationOfDutiesRuleSchema:
    def setup_method(self):
        self.schema = _load_schema("separation_of_duties_rule.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "separation_of_duties_rule.schema.json",
            "source_component": "HumanReviewApproval",
            "rule_id": "sod-001",
            "requester_id": "user-1",
            "reviewer_id": "rev-001",
            "action_type": "apply_patch",
            "status": "ALLOWED",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["rule_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["status"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewIntegrityRecordSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_integrity_record.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_integrity_record.schema.json",
            "source_component": "HumanReviewApproval",
            "record_id": "int-001",
            "prior_record_hash": "",
            "payload_hash": "abc",
            "record_hash": "def",
            "timestamp": "2026-01-01T00:00:00",
            "record_type": "REQUEST",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["record_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["record_type"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestApprovalInvalidationRecordSchema:
    def setup_method(self):
        self.schema = _load_schema("approval_invalidation_record.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "approval_invalidation_record.schema.json",
            "source_component": "HumanReviewApproval",
            "invalidation_id": "inv-001",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "invalidated_at": "2026-01-01T00:00:00",
            "invalidation_reason": "DRIFT_EXPIRY",
            "detail": "Context drifted",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["invalidation_reason"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["invalidation_reason"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewValidationResultSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_validation_result.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_validation_result.schema.json",
            "source_component": "HumanReviewApproval",
            "validation_id": "val-001",
            "validated_at": "2026-01-01T00:00:00",
            "approval_decision_id": "hdec-001",
            "request_id": "r-001",
            "requested_action": "apply_patch",
            "requested_effect": "modify",
            "status": "VALID",
            "reason": "ok",
            "matched_scope": True,
            "expired": False,
            "revoked": False,
            "allowed": True,
            "non_overridable_block_present": False,
            "replay_or_context_mismatch": False,
            "evidence_refs": [],
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["validation_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["status"] = "BAD_VALUE"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewEvidenceManifestSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_evidence_manifest.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_evidence_manifest.schema.json",
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "validated_commit": "abc123",
            "created_at": "2026-01-01T00:00:00",
            "runtime_artifact_root": "",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["component_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewReportSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_report.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_report.schema.json",
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "review_document_id": "rd-001",
            "review_document_version": "1.0",
            "reviewed_commit": "abc",
            "reviewed_at": "2026-01-01T00:00:00",
            "reviewer": "Alice",
            "review_environment": {},
            "working_tree_start_status": "clean",
            "working_tree_end_status": "clean",
            "commands_run": [],
            "coverage_statuses": {},
            "blockers": [],
            "high_issues": [],
            "non_blocking_followups": [],
            "deviation_register": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "implementation_rating": 5,
            "final_verdict": "DONE",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["review_document_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["final_verdict"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestHumanReviewReviewReportSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_review_report.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_review_report.schema.json",
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "review_document_id": "rd-001",
            "review_document_version": "1.0",
            "reviewed_commit": "abc",
            "reviewed_at": "2026-01-01T00:00:00",
            "reviewer": "Alice",
            "review_environment": {},
            "working_tree_start_status": "clean",
            "working_tree_end_status": "clean",
            "commands_run": [],
            "coverage_statuses": {},
            "blockers": [],
            "high_issues": [],
            "non_blocking_followups": [],
            "deviation_register": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "implementation_rating": 5,
            "final_verdict": "DONE",
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["reviewer"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["final_verdict"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0


class TestCompletionRecordSchema:
    pass


class TestHumanReviewDecisionSchema:
    def setup_method(self):
        self.schema = _load_schema("human_review_decision.schema.json")
        self.valid = {
            "schema_version": "1.0",
            "schema_id": "human_review_decision.schema.json",
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-001",
            "request_id": "r-001",
            "decided_at": "2026-01-01T00:00:00",
            "reviewer": {"reviewer_id": "rev-001"},
            "decision": "APPROVED",
            "reason": "ok",
            "scope": {"scope_id": "s-001"},
            "expires_at": None,
            "no_expiry_reason": None,
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": None,
            "decision_hash": None,
            "warnings": [],
            "errors": [],
        }

    def test_valid_instance_passes(self):
        Draft7Validator(self.schema).validate(self.valid)

    def test_missing_required_field_fails(self):
        instance = dict(self.valid)
        del instance["decision_id"]
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0

    def test_invalid_enum_value_fails(self):
        instance = dict(self.valid)
        instance["decision"] = "INVALID"
        errors = list(Draft7Validator(self.schema).iter_errors(instance))
        assert len(errors) > 0
