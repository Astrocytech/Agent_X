from __future__ import annotations
from pathlib import Path
from agentx_evolve.learning.outcome_models import (
    LearningReviewIndex, MemoryCandidate, OutcomeReviewReport,
    OUTCOME_SUCCESS, MEMORY_CANDIDATE_NEEDS_HUMAN_REVIEW,
)
from agentx_evolve.learning.learning_index import (
    load_learning_review_index, update_learning_review_index,
    candidate_hash_exists, record_candidate_hash,
)


def test_index_loads_when_absent_by_creating_empty_in_memory_index(tmp_path: Path):
    index = load_learning_review_index(tmp_path)
    assert index.index_id is not None
    assert len(index.review_keys) == 0


def test_index_write_stays_under_runtime_root(tmp_path: Path):
    index = load_learning_review_index(tmp_path)
    report = OutcomeReviewReport(report_id="rpt-001", event_id="ev-001", review_id="rv-001", outcome_status=OUTCOME_SUCCESS)
    updated = update_learning_review_index(index, report, tmp_path)
    assert (tmp_path / ".agentx-init/learning/learning_review_index.json").exists()


def test_duplicate_candidate_hash_is_detected():
    index = LearningReviewIndex(index_id="idx-001")
    index.candidate_hashes = ["abc"]
    assert candidate_hash_exists(index, "abc") is True
    assert candidate_hash_exists(index, "def") is False


def test_repeated_review_does_not_duplicate_approved_candidate(tmp_path: Path):
    index = load_learning_review_index(tmp_path)
    from agentx_evolve.learning.outcome_models import sha256_text
    cand = MemoryCandidate(candidate_id="mc-001", signal_id="sig-001", candidate_text="test", candidate_type="BEHAVIOR_RULE", scope="component", hash_of_candidate_text=sha256_text("test"))
    record_candidate_hash(index, cand)
    assert cand.hash_of_candidate_text in index.candidate_hashes
    record_candidate_hash(index, cand)
    assert index.candidate_hashes.count(cand.hash_of_candidate_text) == 1


def test_corrupt_review_index_blocks_approval(tmp_path: Path):
    p = tmp_path / ".agentx-init/learning/learning_review_index.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("corrupt json")
    index = load_learning_review_index(tmp_path)
    assert len(index.warnings) > 0 or len(index.errors) > 0
