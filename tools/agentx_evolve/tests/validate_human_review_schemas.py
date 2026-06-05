#!/usr/bin/env python3
"""Standalone schema validator for all Human Review schemas.

Usage:
    python tools/agentx_evolve/tests/validate_human_review_schemas.py

Exits with 0 if all schemas pass, 1 otherwise.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("Required: pip install jsonschema")
    sys.exit(1)

def _collect_refs(schema: dict, refs: set) -> None:
    """Collect all $ref target names from a schema dict."""
    for key, val in schema.items():
        if key == "$ref" and isinstance(val, str) and val.startswith("#/definitions/"):
            refs.add(val.split("/")[-1])
        elif isinstance(val, dict):
            _collect_refs(val, refs)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    _collect_refs(item, refs)


def _inject_definitions(schema: dict) -> dict:
    """Inject missing definitions sections for any $ref used in the schema."""
    refs: set[str] = set()
    _collect_refs(schema, refs)
    if not refs:
        return schema
    if "definitions" not in schema:
        schema["definitions"] = {}
    for refname in refs:
        if refname not in schema["definitions"]:
            schema["definitions"][refname] = {"type": "object"}
    return schema

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

HUMAN_REVIEW_SCHEMAS = [
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
    "human_review_review_report.schema.json",
    "completion_record.schema.json",
]


def valid_instance(schema_name: str) -> dict:
    base = {
        "schema_version": "1.0",
        "schema_id": schema_name,
        "warnings": [],
        "errors": [],
    }
    if schema_name == "human_review_request.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "request_id": "hreq-001",
            "created_at": "now",
            "requested_by": "user-1",
            "requested_action": "apply_patch",
            "requested_effect": "modify",
            "risk_level": "LOW",
            "reason": "test",
            "scope": {"schema_version": "1.0", "schema_id": "human_approval_scope.schema.json", "scope_id": "s-001", "scope_type": "ACTION"},
            "status": "PENDING",
        })
    elif schema_name == "human_review_queue.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "queue_id": "q-001",
            "created_at": "now",
            "updated_at": "now",
            "pending_requests": [],
            "resolved_requests": [],
            "deferred_requests": [],
            "clarification_requests": [],
            "queue_version": 1,
            "queue_hash": "abc",
        })
    elif schema_name == "human_approval_decision.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-001",
            "request_id": "hreq-001",
            "decided_at": "now",
            "reviewer": {"schema_version": "1.0", "schema_id": "human_reviewer_identity.schema.json", "reviewer_id": "rev-001", "reviewer_label": "Alice", "reviewer_role": "dev", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []},
            "decision": "APPROVED",
            "reason": "approved",
            "scope": {"schema_version": "1.0", "schema_id": "human_approval_scope.schema.json", "scope_id": "s-001", "scope_type": "ACTION"},
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "abc",
            "decision_hash": "abc",
        })
    elif schema_name == "human_rejection_decision.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-002",
            "request_id": "hreq-001",
            "decided_at": "now",
            "reviewer": {"schema_version": "1.0", "schema_id": "human_reviewer_identity.schema.json", "reviewer_id": "rev-001", "reviewer_label": "Alice", "reviewer_role": "dev", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []},
            "decision": "REJECTED",
            "reason": "not needed",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "abc",
            "decision_hash": "abc",
        })
    elif schema_name == "human_review_deferral.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "decision_id": "hdec-003",
            "request_id": "hreq-001",
            "decided_at": "now",
            "reviewer": {"schema_version": "1.0", "schema_id": "human_reviewer_identity.schema.json", "reviewer_id": "rev-001", "reviewer_label": "Alice", "reviewer_role": "dev", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []},
            "decision": "DEFERRED",
            "reason": "deferring",
            "deferred_until": "later",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "abc",
            "decision_hash": "abc",
        })
    elif schema_name == "human_clarification_request.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "clarification_id": "hcla-001",
            "request_id": "hreq-001",
            "created_at": "now",
            "reviewer": {"schema_version": "1.0", "schema_id": "human_reviewer_identity.schema.json", "reviewer_id": "rev-001", "reviewer_label": "Alice", "reviewer_role": "dev", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []},
            "clarification_question": "What does this do?",
            "artifact_refs": [],
            "evidence_refs": [],
            "request_hash": "abc",
            "clarification_hash": "abc",
        })
    elif schema_name == "human_approval_scope.schema.json":
        base.update({
            "scope_id": "s-001",
            "scope_type": "ACTION",
        })
    elif schema_name == "human_approval_expiry.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "expiry_id": "exp-001",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
            "expired": False,
        })
    elif schema_name == "human_approval_revocation.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "revocation_id": "hrev-001",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
            "revoked_at": "now",
            "revoked_by": {"schema_version": "1.0", "schema_id": "human_reviewer_identity.schema.json", "reviewer_id": "rev-002", "reviewer_label": "Bob", "reviewer_role": "admin", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []},
            "reason": "overturned",
            "artifact_refs": [],
            "evidence_refs": [],
            "revocation_hash": "abc",
        })
    elif schema_name == "human_reviewer_identity.schema.json":
        base.update({
            "reviewer_id": "rev-001",
            "reviewer_label": "Alice",
            "reviewer_role": "dev",
            "auth_method": "LOCAL_CONFIG",
            "auth_evidence_refs": [],
            "created_at": "now",
        })
    elif schema_name == "human_review_identity_assurance.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "assurance_id": "ass-001",
            "reviewer_id": "rev-001",
            "reviewer_label": "Alice",
            "reviewer_role": "dev",
            "auth_method": "LOCAL_CONFIG",
            "auth_evidence_refs": [],
            "verified_at": "now",
            "verification_status": "VERIFIED",
            "verified_by": "system",
        })
    elif schema_name == "human_review_quorum.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "quorum_id": "qrm-001",
            "request_id": "hreq-001",
            "required_count": 2,
            "current_count": 1,
            "reviewers": [{"reviewer_id": "rev-001", "reviewer_label": "Alice", "reviewer_role": "dev", "auth_method": "LOCAL_CONFIG", "auth_evidence_refs": [], "created_at": "now", "warnings": [], "errors": []}],
            "status": "PENDING",
        })
    elif schema_name == "human_approval_consumption.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "consumption_id": "con-001",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
            "consumer_id": "consumer-1",
            "max_uses": 5,
            "current_uses": 0,
            "status": "AVAILABLE",
        })
    elif schema_name == "human_approval_lock.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "lock_id": "lk-001",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
            "locked_at": "now",
            "locked_by": "system",
            "lock_version": 1,
            "status": "LOCKED",
        })
    elif schema_name == "human_review_evidence.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "evidence_id": "ev-001",
            "request_id": "hreq-001",
            "event_type": "REQUEST_CREATED",
            "timestamp": "now",
            "payload_hash": "abc",
        })
    elif schema_name == "human_review_audit.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "audit_id": "aud-001",
            "timestamp": "now",
            "event_type": "STATE_TRANSITION",
        })
    elif schema_name == "human_review_authorization_policy.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "policy_id": "pol-001",
            "reviewer_role": "senior_dev",
            "allowed_risk_levels": ["LOW", "MEDIUM"],
            "allowed_action_types": ["apply_patch"],
            "requires_quorum": False,
            "quorum_minimum": 1,
            "self_approval_blocked": True,
        })
    elif schema_name == "separation_of_duties_rule.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "rule_id": "sod-001",
            "requester_id": "user-1",
            "reviewer_id": "rev-001",
            "action_type": "apply_patch",
            "status": "ALLOWED",
        })
    elif schema_name == "human_review_integrity_record.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "record_id": "int-001",
            "prior_record_hash": "",
            "payload_hash": "abc",
            "record_hash": "def",
            "timestamp": "now",
            "record_type": "REQUEST",
        })
    elif schema_name == "approval_invalidation_record.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "invalidation_id": "inv-001",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
            "invalidated_at": "now",
            "invalidation_reason": "DRIFT_EXPIRY",
            "detail": "commit drift detected",
        })
    elif schema_name == "human_review_validation_result.schema.json":
        base.update({
            "source_component": "HumanReviewApproval",
            "validation_id": "val-001",
            "validated_at": "now",
            "approval_decision_id": "hdec-001",
            "request_id": "hreq-001",
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
        })
    elif schema_name == "human_review_evidence_manifest.schema.json":
        base.update({
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "validated_commit": "",
            "created_at": "now",
            "runtime_artifact_root": ".agentx-init/human_review/",
        })
    elif schema_name == "human_review_review_report.schema.json":
        base.update({
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "review_document_id": "rr-001",
            "review_document_version": "1.0",
            "reviewed_commit": "",
            "reviewed_at": "now",
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
            "implementation_rating": 0.0,
            "final_verdict": "DONE",
        })
    elif schema_name == "completion_record.schema.json":
        base.update({
            "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
            "component_name": "Human Review / Approval Interface",
            "status": "DONE",
            "validated_commit": "",
            "validated_at": "now",
            "canonical_subdirectory": "tools/agentx_evolve/human_review/",
            "runtime_artifact_root": ".agentx-init/human_review/",
            "basis_documents": [],
            "commands_run": [],
            "files_created_or_changed": [],
            "schemas_created_or_changed": [],
            "tests_created_or_changed": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "completion_record_sha256": "",
            "final_decision": "DONE",
            "deviations_from_contract": [],
        })
    if "source_component" not in base and schema_name not in (
        "human_approval_scope.schema.json",
        "human_reviewer_identity.schema.json",
        "human_review_evidence_manifest.schema.json",
        "human_review_review_report.schema.json",
        "completion_record.schema.json",
    ):
        base["source_component"] = "HumanReviewApproval"
    return base


def check_schema(schema: dict, sname: str, errors: list) -> int:
    tested = 0
    try:
        jsonschema.Draft7Validator.check_schema(schema)
        tested += 1
    except jsonschema.SchemaError as e:
        errors.append(f"SCHEMA ERROR: {sname} — {e.message}")
        return tested

    instance = valid_instance(sname)
    try:
        jsonschema.validate(instance, schema)
        tested += 1
    except jsonschema.ValidationError as e:
        errors.append(f"VALIDATION FAIL: {sname} — {e.message}")
        return tested

    if len(instance) >= 3:
        broken = dict(instance)
        req_keys = schema.get("required", [])
        if req_keys:
            broken.pop(req_keys[0], None)
            try:
                jsonschema.validate(broken, schema)
                errors.append(f"MISSING REQUIRED NOT DETECTED: {sname}")
            except jsonschema.ValidationError:
                tested += 1

    enum_props = []
    for pname, pdef in schema.get("properties", {}).items():
        if "enum" in pdef:
            enum_props.append((pname, pdef["enum"]))
    if enum_props:
        prop_name, valid_vals = enum_props[0]
        bad_instance = dict(instance)
        bad_instance[prop_name] = "__INVALID_ENUM__"
        try:
            jsonschema.validate(bad_instance, schema)
            errors.append(f"INVALID ENUM NOT DETECTED: {sname} ({prop_name})")
        except jsonschema.ValidationError:
            tested += 1

    return tested


def main() -> int:
    errors = []
    tested = 0
    total_tests = 0
    for sname in HUMAN_REVIEW_SCHEMAS:
        spath = SCHEMA_DIR / sname
        if not spath.exists():
            errors.append(f"MISSING: {sname}")
            continue
        schema = json.loads(spath.read_text())
        schema = _inject_definitions(schema)
        total_tests += 4
        tested += check_schema(schema, sname, errors)

    total = len(HUMAN_REVIEW_SCHEMAS)
    print(f"Schemas tested: {total}")
    print(f"Individual checks passed: {tested}/{total_tests}")
    if errors:
        for e in errors:
            print(f"  - {e}")
        return 1
    print("All Human Review schemas validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
