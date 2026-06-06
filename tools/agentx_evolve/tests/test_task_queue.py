import json
from pathlib import Path

import pytest

from scheduler.task_queue import (
    enqueue_task, get_queue_state, claim_next_task, claim_task,
    evaluate_dependencies, create_task, validate_task,
)
from scheduler.scheduler_models import (
    TaskRecord, new_id, utc_now_iso,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_BLOCKED,
)


def test_enqueue_task_creates_record(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_QUEUED,
    )
    state = enqueue_task(task, tmp_path)
    assert state.total_tasks >= 1


def test_enqueue_task_appends_to_jsonl(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
    )
    enqueue_task(task, tmp_path)
    history = tmp_path / ".agentx-init" / "scheduler" / "queue" / "task_history.jsonl"
    assert history.exists()
    lines = history.read_text().strip().split("\n")
    assert len(lines) >= 1
    data = json.loads(lines[-1])
    assert data["task_id"] == "t1"


def test_get_queue_state_returns_snapshot(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
    )
    enqueue_task(task, tmp_path)
    state = get_queue_state(tmp_path)
    assert state.total_tasks >= 1


def test_claim_next_task_returns_pending_task(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(task)

    from scheduler.session_store import SessionStore
    from scheduler.scheduler_models import SessionRecord
    session_store = SessionStore(tmp_path / ".agentx-init" / "scheduler" / "sessions")
    session = SessionRecord(record_id=new_id("sr"), session_id="s1")
    session_store.append_session(session)

    claim = claim_next_task("s1", tmp_path)
    assert claim.task_id == "t1"


def test_claim_next_task_skips_blocked_tasks(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_BLOCKED,
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(task)

    from scheduler.session_store import SessionStore
    from scheduler.scheduler_models import SessionRecord
    session_store = SessionStore(tmp_path / ".agentx-init" / "scheduler" / "sessions")
    session = SessionRecord(record_id=new_id("sr"), session_id="s1")
    session_store.append_session(session)

    claim = claim_next_task("s1", tmp_path)
    assert claim.task_id == ""


def test_claim_next_task_returns_none_when_empty(tmp_path: Path):
    claim = claim_next_task("empty_session", tmp_path)
    assert claim.task_id == ""


def test_claim_task_creates_claim(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(task)

    claim = claim_task("t1", "s1", tmp_path)
    assert claim.task_id == "t1"
    assert claim.lease_id != ""


def test_claim_task_blocks_duplicate_claim(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(task)

    claim_task("t1", "s1", tmp_path)
    second = claim_task("t1", "s1", tmp_path)
    assert second.lease_id == ""


def test_claim_next_respects_dependencies(tmp_path: Path):
    from scheduler.queue_store import QueueStore
    from scheduler.session_store import SessionStore
    from scheduler.scheduler_models import SessionRecord
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    store = QueueStore(store_dir)
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        dependency_ids=["dep1"],
    )
    store.append_task(task)
    session_store = SessionStore(tmp_path / ".agentx-init" / "scheduler" / "sessions")
    session = SessionRecord(record_id=new_id("sr"), session_id="s1")
    session_store.append_session(session)

    claim = claim_next_task("s1", tmp_path)
    assert claim.task_id == ""


def test_evaluate_dependencies_returns_satisfied(tmp_path: Path):
    dep = TaskRecord(
        record_id=new_id("tr"), task_id="dep1", session_id="s1",
        status=SCHEDULER_STATUS_COMPLETED,
    )
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        dependency_ids=["dep1"],
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(dep)
    store.append_task(task)

    resolutions = evaluate_dependencies("t1", tmp_path)
    assert len(resolutions) == 1
    assert resolutions[0].satisfied is True


def test_evaluate_dependencies_returns_blocked(tmp_path: Path):
    task = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        dependency_ids=["nonexistent"],
    )
    store_dir = tmp_path / ".agentx-init" / "scheduler" / "queue"
    store_dir.mkdir(parents=True, exist_ok=True)
    from scheduler.queue_store import QueueStore
    store = QueueStore(store_dir)
    store.append_task(task)

    resolutions = evaluate_dependencies("t1", tmp_path)
    assert len(resolutions) == 1
    assert resolutions[0].satisfied is False


def test_create_task_returns_record():
    task = create_task({"task_id": "t1", "session_id": "s1"})
    assert task.task_id == "t1"
    assert task.status == SCHEDULER_STATUS_QUEUED


def test_validate_task_valid():
    task = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    errors = validate_task(task)
    assert errors == []
