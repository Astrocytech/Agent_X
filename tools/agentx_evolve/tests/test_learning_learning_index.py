import json
from pathlib import Path

from agentx_evolve.learning.learning_index import (
    load_learning_review_index, update_learning_review_index,
    candidate_hash_exists, record_candidate_hash,
)
from agentx_evolve.learning.outcome_models import (
    LearningReviewIndex, OutcomeReviewReport, MemoryCandidate,
)


def test_load_learning_review_index_not_exist(tmp_path):
    index = load_learning_review_index(tmp_path)
    assert index.index_id.startswith("idx-")
    assert index.created_at
    assert index.review_keys == []


def test_load_learning_review_index_valid(tmp_path):
    index_dir = tmp_path / ".agentx-init" / "learning"
    index_dir.mkdir(parents=True)
    data = {
        "index_id": "idx-abc",
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
        "review_keys": ["r1"],
    }
    (index_dir / "learning_review_index.json").write_text(json.dumps(data))
    index = load_learning_review_index(tmp_path)
    assert index.index_id == "idx-abc"
    assert index.review_keys == ["r1"]


def test_load_learning_review_index_corrupt(tmp_path):
    index_dir = tmp_path / ".agentx-init" / "learning"
    index_dir.mkdir(parents=True)
    (index_dir / "learning_review_index.json").write_text("not json")
    index = load_learning_review_index(tmp_path)
    assert index.warnings == ["Corrupt index file, created new index"]
    assert index.errors == ["Failed to parse existing index"]


def test_update_learning_review_index_new_review(tmp_path):
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    report = OutcomeReviewReport(
        report_id="rpt-1", review_id="rev-1", memory_candidates=[],
    )
    result = update_learning_review_index(index, report, tmp_path)
    assert "rev-1" in result.review_keys
    assert ".agentx-init/learning/latest_learning_report.json" in result.latest_report_refs


def test_update_learning_review_index_with_candidates(tmp_path):
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    candidate = {"hash_of_candidate_text": "abc123", "status": "APPROVED"}
    report = OutcomeReviewReport(
        report_id="rpt-1", review_id="rev-1",
        memory_candidates=[candidate],
    )
    result = update_learning_review_index(index, report, tmp_path)
    assert "abc123" in result.candidate_hashes
    assert "abc123" in result.approved_candidate_hashes


def test_update_learning_review_index_blocked_candidate(tmp_path):
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    candidate = {"hash_of_candidate_text": "abc123", "status": "BLOCKED"}
    report = OutcomeReviewReport(report_id="rpt-1", review_id="rev-1", memory_candidates=[candidate])
    result = update_learning_review_index(index, report, tmp_path)
    assert "abc123" in result.blocked_candidate_hashes


def test_candidate_hash_exists():
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1", candidate_hashes=["abc"])
    assert candidate_hash_exists(index, "abc") is True
    assert candidate_hash_exists(index, "xyz") is False


def test_record_candidate_hash_approved():
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    candidate = MemoryCandidate(hash_of_candidate_text="h1", status="APPROVED")
    result = record_candidate_hash(index, candidate)
    assert "h1" in result.candidate_hashes
    assert "h1" in result.approved_candidate_hashes


def test_record_candidate_hash_blocked():
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    candidate = MemoryCandidate(hash_of_candidate_text="h1", status="REJECTED")
    result = record_candidate_hash(index, candidate)
    assert "h1" in result.blocked_candidate_hashes


def test_record_candidate_hash_no_hash():
    index = LearningReviewIndex(index_id="idx-1", created_at="t1", updated_at="t1")
    candidate = MemoryCandidate(hash_of_candidate_text=None, status="APPROVED")
    result = record_candidate_hash(index, candidate)
    assert result.candidate_hashes == []
