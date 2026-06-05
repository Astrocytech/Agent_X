import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
import jsonschema

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


class TestPromotionReleaseCandidateSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_release_candidate.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_release_candidate.schema.json",
            "candidate_id": "rc-001",
            "candidate_hash": "a" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "component_name": "test",
            "roadmap_layer": "layer-1",
            "candidate_type": "IMPLEMENTATION",
            "source_commit": "abc123",
            "changed_files": [],
            "changed_schemas": [],
            "changed_tests": [],
            "required_validations": [],
            "required_approvals": [],
            "required_evidence": [],
            "git_status_summary": {},
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_release_candidate.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_release_candidate.schema.json",
            "candidate_id": "rc-001",
            "candidate_hash": "a" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "component_name": "test",
            "roadmap_layer": "layer-1",
            "candidate_type": "INVALID_TYPE",
            "source_commit": "abc123",
            "changed_files": [],
            "changed_schemas": [],
            "changed_tests": [],
            "required_validations": [],
            "required_approvals": [],
            "required_evidence": [],
            "git_status_summary": {},
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionValidationEvidenceSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_validation_evidence.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_validation_evidence.schema.json",
            "evidence_id": "ev-001",
            "evidence_hash": "b" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "validated_commit": "abc123",
            "validation_started_at": "2026-01-01T00:00:00",
            "validation_completed_at": "2026-01-01T00:01:00",
            "commands": [],
            "compileall_status": "NOT_RUN",
            "compileall_exit_code": None,
            "pytest_status": "NOT_RUN",
            "pytest_exit_code": None,
            "schema_validation_status": "NOT_RUN",
            "schema_validation_exit_code": None,
            "source_mutation_status": "NOT_CHECKED",
            "evidence_files": [],
            "evidence_hashes": [],
            "review_report_refs": [],
            "completion_record_refs": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_validation_evidence.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_validation_evidence.schema.json",
            "evidence_id": "ev-001",
            "evidence_hash": "b" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "validated_commit": "abc123",
            "validation_started_at": "2026-01-01T00:00:00",
            "validation_completed_at": "2026-01-01T00:01:00",
            "commands": [],
            "compileall_status": "INVALID_STATUS",
            "compileall_exit_code": None,
            "pytest_status": "NOT_RUN",
            "pytest_exit_code": None,
            "schema_validation_status": "NOT_RUN",
            "schema_validation_exit_code": None,
            "source_mutation_status": "NOT_CHECKED",
            "evidence_files": [],
            "evidence_hashes": [],
            "review_report_refs": [],
            "completion_record_refs": [],
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionRiskAcceptanceSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_risk_acceptance.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_risk_acceptance.schema.json",
            "risk_acceptance_id": "ra-001",
            "risk_acceptance_hash": "c" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "risks": [],
            "accepted_risks": [],
            "blocking_risks": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_risk_acceptance.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_risk_acceptance.schema.json",
            "risk_acceptance_id": "ra-001",
            "risk_acceptance_hash": "c" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "risks": [
                {"risk_id": "r1", "description": "test", "severity": "INVALID_SEVERITY",
                 "status": "open", "mitigation": "", "accepted": False, "blocking": False},
            ],
            "accepted_risks": [],
            "blocking_risks": [],
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionApprovalReferenceSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_approval_reference.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_approval_reference.schema.json",
            "approval_id": "ap-001",
            "approval_hash": "d" * 64,
            "created_at": "2026-01-01T00:00:00",
            "approved_by": "alice",
            "approval_type": "HUMAN_REVIEW",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "scope": [],
            "approved_commit": "abc123",
            "source": "local",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_approval_reference.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_approval_reference.schema.json",
            "approval_id": "ap-001",
            "approval_hash": "d" * 64,
            "created_at": "2026-01-01T00:00:00",
            "approved_by": "alice",
            "approval_type": "INVALID_TYPE",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "scope": [],
            "approved_commit": "abc123",
            "source": "local",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionGitEvidenceSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_git_evidence.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_git_evidence.schema.json",
            "git_evidence_id": "ge-001",
            "git_evidence_hash": "e" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "working_tree_status": "CLEAN",
            "expected_runtime_artifacts_only": False,
            "changed_files": [],
            "diff_name_only": [],
            "commit_reachable": True,
            "untracked_files": [],
            "forbidden_git_actions_detected": [],
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_git_evidence.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_git_evidence.schema.json",
            "git_evidence_id": "ge-001",
            "git_evidence_hash": "e" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "working_tree_status": "INVALID_STATUS",
            "expected_runtime_artifacts_only": False,
            "changed_files": [],
            "diff_name_only": [],
            "commit_reachable": True,
            "untracked_files": [],
            "forbidden_git_actions_detected": [],
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionGatePolicySchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_gate_policy.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        required = self.schema.get("required", [])
        instance = {}
        for k in required:
            prop = self.schema["properties"].get(k, {})
            instance[k] = self._default_for_type(prop, k)
        jsonschema.validate(instance, self.schema)

    @staticmethod
    def _default_for_type(prop, name=""):
        if "const" in prop:
            return prop["const"]
        if "enum" in prop:
            return prop["enum"][0]
        t = prop.get("type", "")
        if name == "schema_version":
            return "1.0"
        if t == "string":
            return "test"
        if t == "boolean":
            return False
        if t == "integer":
            return 0
        if t == "array":
            return []
        if t == "object":
            return {}
        if "oneOf" in prop:
            for opt in prop["oneOf"]:
                if "type" in opt:
                    val = TestPromotionGatePolicySchema._default_for_type(opt, name)
                    if val is not None:
                        return val
            return None
        return None

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_gate_policy.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_gate_policy.schema.json",
            "policy_id": "p-001",
            "policy_hash": "f" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "AGENTX_PROMOTION_RELEASE_GATE",
            "source_component": "PromotionReleaseGate",
            "require_clean_git_state": "not_a_boolean",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionGateDecisionSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_gate_decision.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_gate_decision.schema.json",
            "decision_id": "gd-001",
            "gate_decision_hash": "g" * 64,
            "idempotency_key": "ik-001",
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision": "PROMOTE",
            "status": "APPROVED",
            "reason": "All checks passed",
            "checks_run": [],
            "passed_checks": [],
            "failed_checks": [],
            "blocking_failures": [],
            "high_issues": [],
            "non_blocking_followups": [],
            "required_approvals_status": "NOT_RUN",
            "validation_status": "NOT_RUN",
            "risk_status": "NOT_RUN",
            "policy_status": "NOT_RUN",
            "patch_evidence_status": "NOT_RUN",
            "tool_evidence_status": "NOT_RUN",
            "git_status": "NOT_RUN",
            "expiry_status": "NOT_RUN",
            "dry_run": False,
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_gate_decision.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_gate_decision.schema.json",
            "decision_id": "gd-001",
            "gate_decision_hash": "g" * 64,
            "idempotency_key": "ik-001",
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision": "INVALID_DECISION",
            "status": "APPROVED",
            "reason": "",
            "checks_run": [],
            "passed_checks": [],
            "failed_checks": [],
            "blocking_failures": [],
            "high_issues": [],
            "non_blocking_followups": [],
            "required_approvals_status": "NOT_RUN",
            "validation_status": "NOT_RUN",
            "risk_status": "NOT_RUN",
            "policy_status": "NOT_RUN",
            "patch_evidence_status": "NOT_RUN",
            "tool_evidence_status": "NOT_RUN",
            "git_status": "NOT_RUN",
            "expiry_status": "NOT_RUN",
            "dry_run": False,
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionExpirySchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_expiry.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_expiry.schema.json",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_type_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_expiry.schema.json",
            "validation_freshness_minutes": "not_an_integer",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionEvidenceManifestSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_evidence_manifest.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_evidence_manifest.schema.json",
            "manifest_id": "manifest-001",
            "manifest_hash": "h" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "gate_decision_hash": "g" * 64,
            "idempotency_key": "ik-001",
            "runtime_artifact_root": ".agentx-init/promotion",
            "evidence_files": [],
            "evidence_file_hashes": [],
            "source_mutation_status": "NOT_CHECKED",
            "hash_status": "NOT_RUN",
            "final_decision": "APPROVED",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_evidence_manifest.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_evidence_manifest.schema.json",
            "manifest_id": "manifest-001",
            "manifest_hash": "h" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "gate_decision_hash": "g" * 64,
            "idempotency_key": "ik-001",
            "runtime_artifact_root": ".agentx-init/promotion",
            "evidence_files": [],
            "evidence_file_hashes": [],
            "source_mutation_status": "INVALID_STATUS",
            "hash_status": "NOT_RUN",
            "final_decision": "APPROVED",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionReviewReportSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_review_report.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_review_report.schema.json",
            "review_report_id": "rr-001",
            "review_report_hash": "i" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "reviewed_commit": "abc123",
            "review_environment": {},
            "commands_run": [],
            "coverage_statuses": {},
            "blockers": [],
            "evidence_manifest_path": ".agentx-init/promotion/promotion_evidence_manifest.json",
            "evidence_manifest_sha256": "j" * 64,
            "final_verdict": "APPROVED",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_review_report.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_type_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_review_report.schema.json",
            "review_report_id": "rr-001",
            "review_report_hash": "i" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "reviewed_commit": "abc123",
            "review_environment": {},
            "commands_run": [],
            "coverage_statuses": {},
            "blockers": [],
            "evidence_manifest_path": ".agentx-init/promotion/promotion_evidence_manifest.json",
            "evidence_manifest_sha256": "j" * 64,
            "final_verdict": "APPROVED",
            "implementation_rating": "not_a_number",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)


class TestPromotionCompletionRecordSchema:
    SCHEMA_PATH = SCHEMAS_DIR / "promotion_completion_record.schema.json"

    @classmethod
    def setup_class(cls):
        with open(cls.SCHEMA_PATH) as f:
            cls.schema = json.loads(f.read())

    def test_valid_instance_passes(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_completion_record.schema.json",
            "completion_record_id": "cr-001",
            "completion_record_hash": "k" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "component_name": "test",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "decision_status": "APPROVED",
            "decision": "PROMOTE",
            "approved_at": "2026-01-01T00:00:00",
            "basis_documents": [],
            "validated_commands": [],
            "validated_evidence": [],
            "release_scope": [],
            "policy_decision_refs": [],
            "approval_refs": [],
            "risk_acceptance_refs": [],
            "git_evidence_refs": [],
            "patch_evidence_refs": [],
            "tool_evidence_refs": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "review_report_path": "",
            "review_report_sha256": "",
            "deviation_register": [],
            "unresolved_risks": [],
            "final_decision": "DONE",
            "warnings": [],
            "errors": [],
        }
        jsonschema.validate(instance, self.schema)

    def test_missing_required_field_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_completion_record.schema.json",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)

    def test_invalid_enum_value_fails(self):
        instance = {
            "schema_version": "1.0",
            "schema_id": "promotion_completion_record.schema.json",
            "completion_record_id": "cr-001",
            "completion_record_hash": "k" * 64,
            "created_at": "2026-01-01T00:00:00",
            "component_id": "comp-1",
            "component_name": "test",
            "candidate_id": "rc-001",
            "source_commit": "abc123",
            "decision_id": "gd-001",
            "decision_status": "INVALID_STATUS",
            "decision": "PROMOTE",
            "approved_at": "2026-01-01T00:00:00",
            "basis_documents": [],
            "validated_commands": [],
            "validated_evidence": [],
            "release_scope": [],
            "policy_decision_refs": [],
            "approval_refs": [],
            "risk_acceptance_refs": [],
            "git_evidence_refs": [],
            "patch_evidence_refs": [],
            "tool_evidence_refs": [],
            "evidence_manifest_path": "",
            "evidence_manifest_sha256": "",
            "review_report_path": "",
            "review_report_sha256": "",
            "deviation_register": [],
            "unresolved_risks": [],
            "final_decision": "DONE",
            "warnings": [],
            "errors": [],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance, self.schema)
