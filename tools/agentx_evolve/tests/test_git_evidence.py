import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.git_evidence import (
    validate_git_evidence, verify_git_state_allows_promotion,
    write_git_evidence, load_git_evidence, compute_git_evidence_hash,
)
from agentx_evolve.promotion.promotion_models import (
    GitEvidence, ReleaseCandidate, WT_CLEAN, WT_DIRTY, WT_UNKNOWN,
)


class TestCleanGitEvidencePasses:
    def test_clean_git_evidence_passes(self):
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
            working_tree_status=WT_CLEAN,
            commit_reachable=True,
        )
        errors = validate_git_evidence(evidence, candidate)
        assert errors == []


class TestDirtyGitBlocksWhenCleanRequired:
    def test_dirty_git_blocks_when_clean_required(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = GitEvidence(
            git_evidence_id="ge-002",
            git_evidence_hash="b" * 64,
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            working_tree_status=WT_DIRTY,
            commit_reachable=True,
        )
        errors = verify_git_state_allows_promotion(evidence, candidate, {"require_clean_git_state": True})
        assert len(errors) > 0


class TestUnreachableCommitBlocks:
    def test_unreachable_commit_blocks(self):
        candidate = ReleaseCandidate(
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            component_name="test",
            roadmap_layer="layer-1",
            candidate_hash="a" * 64,
        )
        evidence = GitEvidence(
            git_evidence_id="ge-003",
            git_evidence_hash="b" * 64,
            candidate_id="rc-001",
            source_commit="abc123",
            component_id="comp-1",
            working_tree_status=WT_CLEAN,
            commit_reachable=False,
        )
        errors = verify_git_state_allows_promotion(evidence, candidate, {})
        assert len(errors) > 0


class TestWriteAndLoadGitEvidence:
    def test_write_and_load_git_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            evidence = GitEvidence(
                git_evidence_id="ge-wl-001",
                git_evidence_hash="b" * 64,
                candidate_id="rc-001",
                source_commit="abc123",
                component_id="comp-1",
                working_tree_status=WT_CLEAN,
                commit_reachable=True,
            )
            path = write_git_evidence(evidence, repo_root)
            assert path.exists()
            loaded = load_git_evidence(path)
            assert loaded is not None
            assert loaded.git_evidence_id == evidence.git_evidence_id
            assert loaded.source_commit == evidence.source_commit
