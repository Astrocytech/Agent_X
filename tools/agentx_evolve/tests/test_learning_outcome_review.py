from __future__ import annotations
import json
import os
from pathlib import Path
from agentx_evolve.learning.outcome_review import (
    LearningOutcomeRecord,
    LearningOutcomeReview,
    StrategyMemory,
    canonical_json,
    sha256_dict,
    write_json_atomic,
    append_jsonl,
    to_dict,
)


def _make_outcome(**kwargs) -> LearningOutcomeRecord:
    fields = {
        "outcome_id": "",
        "session_id": "sess-001",
        "attempted_task": "implement_feature_x",
        "proposal_type": "IMPLEMENT_PATCH",
        "files_changed": None,
        "model_used": "small_coder",
        "validation_outcome": "PASS",
        "rollback_outcome": "",
        "failure_reason": "",
        "successful_strategy": "used incremental approach",
        "future_recommendation": "continue incremental approach",
        "created_at": "",
        "outcome_hash": "",
        "tags": None,
        "evidence_refs": None,
        "warnings": None,
        "errors": None,
    }
    fields.update(kwargs)
    if fields["files_changed"] is None:
        fields["files_changed"] = ["src/feature_x.py"]
    if fields["tags"] is None:
        fields["tags"] = ["feature_x", "python"]
    if fields["evidence_refs"] is None:
        fields["evidence_refs"] = ["ev-001"]
    if fields["warnings"] is None:
        fields["warnings"] = []
    if fields["errors"] is None:
        fields["errors"] = []
    return LearningOutcomeRecord(**fields)


class TestRecordOutcome:
    def test_record_outcome_creates_outcome(self):
        review = LearningOutcomeReview()
        outcome = _make_outcome()
        review.record_outcome(outcome)
        assert outcome.outcome_id.startswith("lr-") or outcome.outcome_id == ""
        assert outcome.created_at != ""
        assert outcome.outcome_hash != ""
        d = to_dict(outcome)
        d.pop("outcome_hash", None)
        assert outcome.outcome_hash == sha256_dict(d)
        assert len(review.list_all()) == 1

    def test_outcome_record_defaults(self):
        review = LearningOutcomeReview()
        outcome = LearningOutcomeRecord()
        review.record_outcome(outcome)
        assert outcome.outcome_id.startswith("lr-")
        assert outcome.created_at != ""
        assert outcome.outcome_hash != ""
        assert outcome.schema_version == "1.0"
        assert outcome.schema_id == "learning_outcome_record.schema.json"


class TestGetBySession:
    def test_get_by_session_returns_matching(self):
        review = LearningOutcomeReview()
        review.record_outcome(_make_outcome(session_id="sess-a"))
        review.record_outcome(_make_outcome(session_id="sess-b"))
        review.record_outcome(_make_outcome(session_id="sess-a"))
        assert len(review.get_by_session("sess-a")) == 2
        assert len(review.get_by_session("sess-b")) == 1
        assert len(review.get_by_session("sess-c")) == 0


class TestGetByTag:
    def test_get_by_tag_returns_matching(self):
        review = LearningOutcomeReview()
        review.record_outcome(_make_outcome(tags=["alpha"]))
        review.record_outcome(_make_outcome(tags=["beta"]))
        review.record_outcome(_make_outcome(tags=["alpha", "gamma"]))
        assert len(review.get_by_tag("alpha")) == 2
        assert len(review.get_by_tag("beta")) == 1
        assert len(review.get_by_tag("gamma")) == 1
        assert len(review.get_by_tag("delta")) == 0


class TestGetSuccessfulStrategies:
    def test_get_successful_strategies_returns_only_success(self):
        review = LearningOutcomeReview()
        review.record_outcome(_make_outcome(successful_strategy="strategy A"))
        review.record_outcome(_make_outcome(successful_strategy=""))
        review.record_outcome(_make_outcome(successful_strategy="strategy B"))
        results = review.get_successful_strategies()
        assert len(results) == 2
        assert all(r.successful_strategy for r in results)


class TestGetFailurePatterns:
    def test_get_failure_patterns_returns_only_failures(self):
        review = LearningOutcomeReview()
        review.record_outcome(_make_outcome(failure_reason="timeout error"))
        review.record_outcome(_make_outcome(failure_reason=""))
        review.record_outcome(_make_outcome(failure_reason="validation failed"))
        results = review.get_failure_patterns()
        assert len(results) == 2
        assert all(r.failure_reason for r in results)


class TestStrategyMemory:
    def test_strategy_memory_store_retrieve(self):
        mem = StrategyMemory()
        mem.store("key1", "value1")
        mem.store("key2", {"nested": True})
        assert mem.retrieve("key1") == "value1"
        assert mem.retrieve("key2") == {"nested": True}
        assert mem.retrieve("nonexistent") is None

    def test_strategy_memory_search_prefix(self):
        mem = StrategyMemory()
        mem.store("alpha.one", 1)
        mem.store("alpha.two", 2)
        mem.store("beta.one", 3)
        results = mem.search("alpha.")
        assert results == {"alpha.one": 1, "alpha.two": 2}
        assert len(mem.search("gamma")) == 0


class TestHelpers:
    def test_canonical_json_is_deterministic(self):
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        assert canonical_json(d1) == canonical_json(d2)
        assert canonical_json(d1) == '{"a":1,"b":2}'

    def test_sha256_dict_is_deterministic(self):
        d = {"key": "value"}
        h1 = sha256_dict(d)
        h2 = sha256_dict(d)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64

    def test_to_dict_dataclass(self):
        rec = _make_outcome(outcome_id="test-001", created_at="2026-01-01T00:00:00Z",
                            outcome_hash="abc")
        d = to_dict(rec)
        assert d["outcome_id"] == "test-001"
        assert d["session_id"] == "sess-001"
        assert isinstance(d["files_changed"], list)
        assert isinstance(d["tags"], list)

    def test_write_json_atomic_creates_file(self, tmp_path: Path):
        data = {"key": "value"}
        dest = tmp_path / "test.json"
        result = write_json_atomic(dest, data)
        assert result == dest
        assert dest.exists()
        assert json.loads(dest.read_text()) == data

    def test_append_jsonl_appends(self, tmp_path: Path):
        dest = tmp_path / "test.jsonl"
        append_jsonl(dest, {"a": 1})
        append_jsonl(dest, {"b": 2})
        lines = dest.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0]) == {"a": 1}
        assert json.loads(lines[1]) == {"b": 2}


class TestPersistence:
    def test_write_outcome_history_creates_file(self, tmp_path: Path):
        review = LearningOutcomeReview()
        review.record_outcome(_make_outcome())
        result = review.write_outcome_history(tmp_path)
        expected = tmp_path / ".agentx-init" / "learning" / "outcome_history.json"
        assert result == expected
        assert expected.exists()
        data = json.loads(expected.read_text())
        assert len(data["records"]) == 1
        assert data["records"][0]["session_id"] == "sess-001"

    def test_append_outcome_history_appends(self, tmp_path: Path):
        review = LearningOutcomeReview()
        outcome = _make_outcome()
        review.record_outcome(outcome)
        result = review.append_outcome_history(outcome, tmp_path)
        expected = tmp_path / ".agentx-init" / "learning" / "outcome_history.jsonl"
        assert result == expected
        assert expected.exists()
        lines = expected.read_text().strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["session_id"] == "sess-001"

    def test_strategy_memory_persist_and_load(self, tmp_path: Path):
        mem = StrategyMemory()
        mem.store("strategy.a", "value_a")
        mem.store("strategy.b", "value_b")

        persist_path = mem.persist_memory(tmp_path)
        expected = tmp_path / ".agentx-init" / "learning" / "strategy_memory.json"
        assert persist_path == expected
        assert expected.exists()
        data = json.loads(expected.read_text())
        assert data == {"strategy.a": "value_a", "strategy.b": "value_b"}

        mem2 = StrategyMemory()
        mem2.load_memory(tmp_path)
        assert mem2.retrieve("strategy.a") == "value_a"
        assert mem2.retrieve("strategy.b") == "value_b"
        assert mem2.retrieve("nonexistent") is None

    def test_load_memory_no_file(self, tmp_path: Path):
        mem = StrategyMemory()
        mem.store("existing", "val")
        mem.load_memory(tmp_path)
        assert mem.retrieve("existing") == "val"
        assert len(mem.search("")) == 1


class TestLocking:
    def test_acquire_release_lock(self, tmp_path: Path):
        review = LearningOutcomeReview()
        lock = review.acquire_learning_lock(tmp_path, timeout_seconds=5)
        lock_path = tmp_path / ".agentx-init" / "learning" / ".learning.lock"
        assert lock_path.exists()
        assert lock["acquired"] is True
        review.release_learning_lock(lock, tmp_path)
        assert not lock_path.exists()

    def test_lock_prevents_concurrent_acquire(self, tmp_path: Path):
        review = LearningOutcomeReview()
        lock1 = review.acquire_learning_lock(tmp_path, timeout_seconds=5)
        lock_path = tmp_path / ".agentx-init" / "learning" / ".learning.lock"
        assert lock_path.exists()
        import time
        start = time.monotonic()
        try:
            review.acquire_learning_lock(tmp_path, timeout_seconds=1)
        except TimeoutError:
            pass
        elapsed = time.monotonic() - start
        assert elapsed >= 1.0
        review.release_learning_lock(lock1, tmp_path)
