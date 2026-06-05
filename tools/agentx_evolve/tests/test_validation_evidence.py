import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.validation_evidence import (
    validate_validation_evidence, write_validation_evidence,
    load_validation_evidence, verify_command_passed,
    compute_validation_evidence_hash,
)
from agentx_evolve.promotion.promotion_models import (
    ValidationEvidence, ReleaseCandidate, CS_PASS, CS_FAIL, CS_NOT_RUN,
)


class TestValidationEvidenceAcceptsPassingCommands:
    def test_validation_evidence_accepts_passing_commands(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = ValidationEvidence(
            evidence_id="ev-001",
            evidence_hash="b" * 64,
            validated_commit="abc123",
            component_id="comp-1",
            compileall_status=CS_PASS,
            compileall_exit_code=0,
            pytest_status=CS_PASS,
            pytest_exit_code=0,
            schema_validation_status=CS_NOT_RUN,
            schema_validation_exit_code=None,
            commands=[{"name": "compileall", "command": "python -m compileall .", "exit_code": 0, "status": "PASS", "summary": "ok"}],
        )
        errors = validate_validation_evidence(evidence, candidate, 1440)
        assert errors == []


class TestValidationEvidenceRequiresExitCodes:
    def test_validation_evidence_requires_exit_codes(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = ValidationEvidence(
            evidence_id="ev-002",
            evidence_hash="b" * 64,
            validated_commit="abc123",
            component_id="comp-1",
            compileall_status=CS_FAIL,
            compileall_exit_code=None,
        )
        errors = validate_validation_evidence(evidence, candidate, 1440)
        assert len(errors) > 0


class TestFailedValidationBlocksPromotion:
    def test_failed_validation_blocks_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            evidence = ValidationEvidence(
                evidence_id="ev-003",
                evidence_hash="b" * 64,
                validated_commit="abc123",
                component_id="comp-1",
                compileall_status=CS_PASS,
                compileall_exit_code=0,
                pytest_status=CS_FAIL,
                pytest_exit_code=1,
            )
            from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=evidence,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert "PROMOTION_VALIDATION_FAILED" in classes


class TestStaleValidationBlocks:
    def test_stale_validation_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            evidence = ValidationEvidence(
                evidence_id="ev-004",
                evidence_hash="b" * 64,
                validated_commit="abc123",
                component_id="comp-1",
                created_at="2000-01-01T00:00:00",
            )
            from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=evidence,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={
                    "require_validation": False,
                    "require_review_report": False,
                    "require_completion_record_for_approved": False,
                    "validation_freshness_minutes": 0,
                },
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert "PROMOTION_VALIDATION_STALE" in classes


class TestValidationCommitMismatchBlocks:
    def test_validation_commit_mismatch_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = ValidationEvidence(
            evidence_id="ev-005",
            evidence_hash="b" * 64,
            validated_commit="def456",
            component_id="comp-1",
        )
        errors = validate_validation_evidence(evidence, candidate, 1440)
        assert len(errors) > 0


class TestMissingExitCodeBlocks:
    def test_missing_exit_code_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = ValidationEvidence(
            evidence_id="ev-006",
            evidence_hash="b" * 64,
            validated_commit="abc123",
            component_id="comp-1",
            compileall_status=CS_PASS,
            compileall_exit_code=0,
            pytest_status=CS_PASS,
            pytest_exit_code=None,
        )
        errors = validate_validation_evidence(evidence, candidate, 1440)
        assert len(errors) > 0


class TestWriteAndLoadValidationEvidence:
    def test_write_and_load_validation_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            evidence = ValidationEvidence(
                evidence_id="ev-wl-001",
                evidence_hash="b" * 64,
                validated_commit="abc123",
                component_id="comp-1",
            )
            path = write_validation_evidence(evidence, repo_root)
            assert path.exists()
            loaded = load_validation_evidence(path)
            assert loaded.evidence_id == evidence.evidence_id
            assert loaded.validated_commit == evidence.validated_commit
