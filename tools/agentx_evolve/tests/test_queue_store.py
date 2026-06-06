import pytest
import json
import tempfile
from pathlib import Path

from scheduler.queue_store import QueueStore
from scheduler.scheduler_models import (
    TaskRecord, new_id,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED,
)


@pytest.fixture
def queue_store():
    with tempfile.TemporaryDirectory() as tmp:
        store = QueueStore(Path(tmp) / "queue")
        yield store


def test_append_and_replay(queue_store):
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    tasks, quarantined = queue_store.replay_tasks()
    assert len(tasks) == 1
    assert len(quarantined) == 0
    assert tasks[0].task_id == "t1"


def test_replay_empty(queue_store):
    tasks, quarantined = queue_store.replay_tasks()
    assert tasks == []
    assert quarantined == []


def test_multiple_tasks(queue_store):
    for i in range(5):
        t = TaskRecord(record_id=new_id("tr"), task_id=f"t{i}", session_id="s1", priority=i * 10)
        queue_store.append_task(t)
    tasks, quarantined = queue_store.replay_tasks()
    assert len(tasks) == 5


def test_build_snapshot(queue_store):
    t1 = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    t2 = TaskRecord(record_id=new_id("tr"), task_id="t2", session_id="s1")
    queue_store.append_task(t1)
    queue_store.append_task(t2)
    state, quarantined = queue_store.build_snapshot()
    assert state.total_tasks == 2
    assert state.by_status.get("QUEUED", 0) == 2
    assert len(quarantined) == 0


def test_effective_latest_wins(queue_store):
    t1 = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1", status=SCHEDULER_STATUS_QUEUED)
    queue_store.append_task(t1)
    t2 = TaskRecord(
        record_id=new_id("tr"), task_id="t1", session_id="s1",
        status=SCHEDULER_STATUS_COMPLETED, revision=2, append_sequence=1,
        previous_record_hash=t1.task_record_hash,
    )
    result = queue_store.append_task(t2)
    tasks, _ = queue_store.replay_tasks()
    effective = queue_store._effective_tasks(tasks)
    assert effective["t1"].status == SCHEDULER_STATUS_COMPLETED


def test_quarantine_malformed(queue_store):
    history_path = queue_store._history_path
    with open(history_path, "a", encoding="utf-8") as f:
        f.write("not valid json\n")
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    tasks, quarantined = queue_store.replay_tasks()
    assert len(tasks) == 1
    assert len(quarantined) >= 1


def test_compact_history(queue_store):
    for i in range(3):
        t = TaskRecord(record_id=new_id("tr"), task_id=f"t{i}", session_id="s1")
        queue_store.append_task(t)
    result = queue_store.compact_history()
    assert result["status"] == "compacted"
    assert result["records_written"] == 3


def test_load_snapshot_after_build(queue_store):
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    queue_store.build_snapshot()
    loaded = queue_store.load_snapshot()
    assert loaded is not None
    assert loaded.total_tasks == 1


def test_snapshot_none_when_missing(queue_store):
    loaded = queue_store.load_snapshot()
    assert loaded is None
