from __future__ import annotations
from pathlib import Path
from agentx_evolve.learning.outcome_models import OutcomeEvent
from agentx_evolve.learning.learning_lock import compute_review_key
from agentx_evolve.learning.learning_index import load_learning_review_index, candidate_hash_exists


def test_same_event_produces_same_review_key():
    e1 = OutcomeEvent(event_id="ev-001", outcome_status="SUCCESS", summary="test", evidence_refs=["ev-001"])
    e2 = OutcomeEvent(event_id="ev-001", outcome_status="SUCCESS", summary="test", evidence_refs=["ev-001"])
    assert compute_review_key(e1) == compute_review_key(e2)


def test_same_evidence_produces_same_candidate_hash():
    from agentx_evolve.learning.outcome_models import sha256_text
    assert sha256_text("hello") == sha256_text("hello")
    assert sha256_text("hello") != sha256_text("world")


def test_repeated_review_does_not_duplicate_approved_candidate(tmp_path: Path):
    index = load_learning_review_index(tmp_path)
    assert index.index_id is not None
    assert not index.candidate_hashes


def test_learning_review_index_contains_no_duplicate_hashes():
    from agentx_evolve.learning.outcome_models import LearningReviewIndex
    idx = LearningReviewIndex(index_id="idx-001")
    idx.candidate_hashes = ["a", "b", "c"]
    assert not candidate_hash_exists(idx, "d")
    assert candidate_hash_exists(idx, "a")
