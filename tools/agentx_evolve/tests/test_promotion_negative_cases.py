import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.release_candidate import load_release_candidate
from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, ValidationEvidence, GitEvidence,
    FC_CANDIDATE_MISSING,
)


class TestCandidateMissingPath:
    def test_candidate_missing_path(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            path = repo_root / "nonexistent.json"
            import pytest
            with pytest.raises(FileNotFoundError):
                load_release_candidate(path)


class TestValidationWithMissingHash:
    def test_validation_with_missing_hash(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
            schema_id="promotion_release_candidate.schema.json",
        )
        evidence = ValidationEvidence(
            evidence_id="ev-001",
            validated_commit="abc123",
            component_id="comp-1",
        )
        from agentx_evolve.promotion.validation_evidence import validate_validation_evidence
        errors = validate_validation_evidence(evidence, candidate, 1440)
        assert len(errors) > 0
        assert any("evidence_hash" in e for e in errors)


class TestApprovalWithMissingCommit:
    def test_approval_with_missing_commit(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        from agentx_evolve.promotion.promotion_models import ApprovalReference
        from agentx_evolve.promotion.approval_lookup import validate_approval_reference
        approval = ApprovalReference(
            approval_id="ap-001",
            approval_hash="",
            approved_commit="",
            component_id="comp-1",
            source="local",
        )
        errors = validate_approval_reference(approval, candidate)
        assert any("approval_hash" in e for e in errors)


class TestGitEvidenceWithDirtyTreeAndNoPolicy:
    def test_git_evidence_with_dirty_tree_and_no_policy(self):
        from agentx_evolve.promotion.git_evidence import verify_git_state_allows_promotion
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = GitEvidence(
            git_evidence_id="ge-001",
            git_evidence_hash="b" * 64,
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            working_tree_status="DIRTY",
            commit_reachable=True,
        )
        errors = verify_git_state_allows_promotion(evidence, candidate, {"require_clean_git_state": True})
        assert len(errors) > 0
        assert any("dirty" in e.lower() for e in errors)


class TestDispatcherWithNonexistentCandidate:
    def test_dispatcher_with_nonexistent_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            decision = None
            try:
                from agentx_evolve.promotion.gate_decision import create_gate_decision
                decision = create_gate_decision(
                    candidate=None,
                    validation_evidence=None,
                    risk_acceptance=None,
                    approvals=[],
                    git_evidence=None,
                    policy_context={},
                    integration_context={},
                    repo_root=repo_root,
                )
            except Exception:
                pass
            assert decision is not None
            assert decision.status in ("BLOCKED", "FAILED", "INVALID")


class TestNoneCandidateInBlockerCollection:
    def test_none_candidate_in_blocker_collection(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            blockers = collect_promotion_blockers(
                candidate=None,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={},
                integration_context={},
                repo_root=repo_root,
            )
            assert len(blockers) == 1
            assert blockers[0]["failure_class"] == FC_CANDIDATE_MISSING
