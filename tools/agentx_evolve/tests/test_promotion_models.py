import os
import sys
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, RiskAcceptance,
    ApprovalReference, GitEvidence, PromotionGatePolicy,
    PromotionGateDecision, PromotionEvidenceManifest,
    PromotionReviewReport, PromotionCompletionRecord,
    canonical_json, sha256_dict, to_dict, redact_sensitive_values,
    ALL_PROMOTION_STATUSES, ALL_PROMOTION_DECISIONS,
    SCHEMA_VERSION,
)


class TestReleaseCandidateDefaults:
    def test_release_candidate_defaults(self):
        obj = ReleaseCandidate()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_release_candidate.schema.json"
        assert obj.candidate_type == "IMPLEMENTATION"
        assert obj.changed_files == []
        assert obj.changed_schemas == []
        assert obj.changed_tests == []
        assert obj.errors == []


class TestValidationEvidenceDefaults:
    def test_validation_evidence_defaults(self):
        obj = ValidationEvidence()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_validation_evidence.schema.json"
        assert obj.compileall_status == "NOT_RUN"
        assert obj.pytest_status == "NOT_RUN"
        assert obj.source_mutation_status == "NOT_CHECKED"


class TestRiskAcceptanceDefaults:
    def test_risk_acceptance_defaults(self):
        obj = RiskAcceptance()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_risk_acceptance.schema.json"
        assert obj.risks == []
        assert obj.accepted_risks == []
        assert obj.blocking_risks == []


class TestApprovalReferenceDefaults:
    def test_approval_reference_defaults(self):
        obj = ApprovalReference()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_approval_reference.schema.json"
        assert obj.approval_type == "HUMAN_REVIEW"
        assert obj.revoked is False
        assert obj.scope == []


class TestGitEvidenceDefaults:
    def test_git_evidence_defaults(self):
        obj = GitEvidence()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_git_evidence.schema.json"
        assert obj.working_tree_status == "UNKNOWN"
        assert obj.commit_reachable is True
        assert obj.forbidden_git_actions_detected == []


class TestPromotionGatePolicyDefaults:
    def test_promotion_gate_policy_defaults(self):
        obj = PromotionGatePolicy()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_gate_policy.schema.json"
        assert obj.component_id == "AGENTX_PROMOTION_RELEASE_GATE"
        assert obj.require_clean_git_state is True


class TestPromotionGateDecisionDefaults:
    def test_promotion_gate_decision_defaults(self):
        obj = PromotionGateDecision()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_gate_decision.schema.json"
        assert obj.decision == "BLOCK"
        assert obj.status == "BLOCKED"
        assert obj.dry_run is False


class TestPromotionEvidenceManifestDefaults:
    def test_promotion_evidence_manifest_defaults(self):
        obj = PromotionEvidenceManifest()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_evidence_manifest.schema.json"
        assert obj.source_mutation_status == "NOT_CHECKED"
        assert obj.hash_status == "NOT_RUN"


class TestPromotionReviewReportDefaults:
    def test_promotion_review_report_defaults(self):
        obj = PromotionReviewReport()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_review_report.schema.json"
        assert obj.final_verdict == "NOT_DONE"
        assert obj.blockers == []


class TestPromotionCompletionRecordDefaults:
    def test_promotion_completion_record_defaults(self):
        obj = PromotionCompletionRecord()
        assert obj.schema_version == SCHEMA_VERSION
        assert obj.schema_id == "promotion_completion_record.schema.json"
        assert obj.decision_status == "APPROVED"
        assert obj.decision == "PROMOTE"
        assert obj.final_decision == "DONE"


class TestCanonicalJsonDeterministic:
    def test_canonical_json_deterministic(self):
        data = {"b": 2, "a": 1}
        j1 = canonical_json(data)
        j2 = canonical_json(data)
        assert j1 == j2
        assert j1 == '{"a":1,"b":2}'


class TestSha256DictDeterministic:
    def test_sha256_dict_deterministic(self):
        data = {"a": 1, "b": 2}
        h1 = sha256_dict(data)
        h2 = sha256_dict(data)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64


class TestToDictSerializesBasic:
    def test_to_dict_serializes_basic(self):
        @dataclass
        class Simple:
            name: str = ""
            value: int = 0

        obj = Simple(name="test", value=42)
        d = to_dict(obj)
        assert d["name"] == "test"
        assert d["value"] == 42


class TestRedactSensitiveValues:
    def test_redact_sensitive_values_hides_secrets(self):
        data = {"password": "s3cr3t", "token": "tok123", "api_key": "key456",
                "private_key": "pk789", "secret": "hidden", "name": "visible"}
        result = redact_sensitive_values(data)
        assert result["name"] == "visible"
        assert result["password"] == "***REDACTED***"
        assert result["token"] == "***REDACTED***"
        assert result["api_key"] == "***REDACTED***"
        assert result["private_key"] == "***REDACTED***"
        assert result["secret"] == "***REDACTED***"


class TestAllPromotionStatuses:
    def test_all_promotion_statuses_has_9_values(self):
        assert len(ALL_PROMOTION_STATUSES) == 9


class TestAllPromotionDecisions:
    def test_all_promotion_decisions_has_9_values(self):
        assert len(ALL_PROMOTION_DECISIONS) == 9
