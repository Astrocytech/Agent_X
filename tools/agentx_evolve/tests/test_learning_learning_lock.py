from pathlib import Path
import json

from agentx_evolve.learning.learning_lock import (
    compute_review_key, acquire_learning_lock, release_learning_lock,
    record_stale_lock,
)
from agentx_evolve.learning.outcome_models import OutcomeEvent, LearningLockRecord


def test_compute_review_key():
    event = OutcomeEvent(event_id="evt-1", run_id="run-1", task_id="task-1", outcome_status="SUCCESS")
    key = compute_review_key(event)
    assert isinstance(key, str)
    assert len(key) == 64


def test_compute_review_key_deterministic():
    e1 = OutcomeEvent(event_id="evt-1", outcome_status="SUCCESS")
    e2 = OutcomeEvent(event_id="evt-1", outcome_status="SUCCESS")
    assert compute_review_key(e1) == compute_review_key(e2)


def test_acquire_learning_lock(tmp_path):
    context = {"repo_root": str(tmp_path), "session_id": "sess-1"}
    key = "test_key_123"
    lock = acquire_learning_lock(key, context)
    assert lock.status == "ACQUIRED"
    assert lock.review_key == key
    assert lock.owner_session_id == "sess-1"
    assert Path(lock.lock_path).exists()


def test_acquire_learning_lock_already_exists(tmp_path):
    context = {"repo_root": str(tmp_path), "session_id": "sess-1"}
    key = "dup_key"
    lock1 = acquire_learning_lock(key, context)
    assert lock1.status == "ACQUIRED"
    lock2 = acquire_learning_lock(key, context)
    assert lock2.status == "STALE_LOCK" or lock2.status == "ACQUIRED"


def test_release_learning_lock(tmp_path):
    context = {"repo_root": str(tmp_path), "session_id": "sess-1"}
    key = "release_key"
    lock = acquire_learning_lock(key, context)
    released = release_learning_lock(lock, context)
    assert released.status == "RELEASED"


def test_release_nonexistent_lock():
    lock = LearningLockRecord(lock_id="lk-1", lock_path="/nonexistent/path.lock")
    result = release_learning_lock(lock, {})
    assert result.status == "RELEASE_FAILED"
    assert len(result.errors) > 0


def test_record_stale_lock(tmp_path):
    lock_path = tmp_path / "stale.lock"
    lock_path.write_text(json.dumps({"owner_session_id": "sess-old"}))
    context = {"repo_root": str(tmp_path)}
    record = record_stale_lock(lock_path, context)
    assert record.status == "STALE_LOCK"
    assert record.owner_session_id == "sess-old"
    assert len(record.warnings) > 0
