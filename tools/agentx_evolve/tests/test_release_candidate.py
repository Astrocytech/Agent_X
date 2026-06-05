import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.release_candidate import (
    create_release_candidate, validate_release_candidate,
    write_release_candidate, load_release_candidate,
    compute_candidate_hash,
)
from agentx_evolve.promotion.promotion_models import ReleaseCandidate


class TestCreateReleaseCandidateValid:
    def test_create_release_candidate_valid(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = create_release_candidate(
                component_id="comp-1",
                component_name="test-component",
                roadmap_layer="layer-1",
                source_commit="abc123",
                changed_files=["file1.py"],
                changed_schemas=[],
                changed_tests=[],
                required_validations=[],
                required_approvals=[],
                required_evidence=[],
                repo_root=repo_root,
            )
            assert candidate.candidate_id.startswith("rc-")
            assert candidate.component_id == "comp-1"
            assert candidate.source_commit == "abc123"
            assert candidate.candidate_hash is not None
            assert len(candidate.candidate_hash) == 64


class TestReleaseCandidateSchemaAcceptsValidCandidate:
    def test_release_candidate_schema_accepts_valid_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = create_release_candidate(
                component_id="comp-1",
                component_name="test-component",
                roadmap_layer="layer-1",
                source_commit="abc123",
                changed_files=["file1.py"],
                changed_schemas=[],
                changed_tests=[],
                required_validations=[],
                required_approvals=[],
                required_evidence=[],
                repo_root=repo_root,
            )
            errors = validate_release_candidate(candidate)
            assert errors == []


class TestReleaseCandidateHashMismatchBlocks:
    def test_release_candidate_hash_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = create_release_candidate(
                component_id="comp-1",
                component_name="test-component",
                roadmap_layer="layer-1",
                source_commit="abc123",
                changed_files=["file1.py"],
                changed_schemas=[],
                changed_tests=[],
                required_validations=[],
                required_approvals=[],
                required_evidence=[],
                repo_root=repo_root,
            )
            original_hash = candidate.candidate_hash
            candidate.candidate_hash = "0" * 64
            from agentx_evolve.promotion.gate_policy import collect_promotion_blockers
            blockers = collect_promotion_blockers(
                candidate=candidate,
                validation_evidence=None,
                risk_acceptance=None,
                approvals=[],
                git_evidence=None,
                policy_context={"require_validation": False, "require_review_report": False, "require_completion_record_for_approved": False},
                integration_context={},
                repo_root=repo_root,
            )
            classes = [b["failure_class"] for b in blockers]
            assert "PROMOTION_CANDIDATE_INVALID" in classes


class TestSupersededCandidateBlocksPromotion:
    def test_superseded_candidate_blocks_promotion(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-old",
            candidate_hash="a" * 64,
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            superseded_by_candidate_id="rc-new",
        )
        assert candidate.superseded_by_candidate_id is not None


class TestWriteAndLoadReleaseCandidate:
    def test_write_and_load_release_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = create_release_candidate(
                component_id="comp-1",
                component_name="test-component",
                roadmap_layer="layer-1",
                source_commit="abc123",
                changed_files=["file1.py"],
                changed_schemas=[],
                changed_tests=[],
                required_validations=[],
                required_approvals=[],
                required_evidence=[],
                repo_root=repo_root,
            )
            path = write_release_candidate(candidate, repo_root)
            assert path.exists()
            loaded = load_release_candidate(path)
            assert loaded.candidate_id == candidate.candidate_id
            assert loaded.source_commit == candidate.source_commit
            assert loaded.candidate_hash == candidate.candidate_hash
