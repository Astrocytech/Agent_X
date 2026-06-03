import json
from pathlib import Path

import pytest

from agentx_evolve.scheduler.queue_store import QueueStore
from agentx_evolve.scheduler.scheduler_models import (
    TaskRecord, new_id,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_COMPLETED,
)


@pytest.fixture
def queue_store(tmp_path: Path):
    return QueueStore(tmp_path / "queue")


def test_snapshot_manifest_created(queue_store):
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    state, quarantined = queue_store.build_snapshot()
    assert state.total_tasks == 1
    assert len(quarantined) == 0
    snapshot = queue_store.load_snapshot()
    assert snapshot is not None
    assert snapshot.total_tasks == 1


def test_replay_deterministic_same_state(queue_store):
    t1 = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    t2 = TaskRecord(record_id=new_id("tr"), task_id="t2", session_id="s1")
    queue_store.append_task(t1)
    queue_store.append_task(t2)
    tasks_a, _ = queue_store.replay_tasks()
    tasks_b, _ = queue_store.replay_tasks()
    assert len(tasks_a) == len(tasks_b)
    ids_a = [t.task_id for t in tasks_a]
    ids_b = [t.task_id for t in tasks_b]
    assert ids_a == ids_b


def test_replay_after_corruption_is_safe(queue_store):
    history = queue_store._history_path
    history.parent.mkdir(parents=True, exist_ok=True)
    history.write_text("not valid json\n")
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    tasks, quarantined = queue_store.replay_tasks()
    assert len(tasks) == 1
    assert len(quarantined) >= 1


def test_snapshot_does_not_overwrite_history(queue_store):
    history_path = queue_store._history_path
    snapshot_path = queue_store._snapshot_path
    t = TaskRecord(record_id=new_id("tr"), task_id="t1", session_id="s1")
    queue_store.append_task(t)
    queue_store.build_snapshot()
    assert history_path.exists()
    assert snapshot_path.exists()


def test_replay_over_empty_history_returns_empty(queue_store):
    tasks, quarantined = queue_store.replay_tasks()
    assert tasks == []
    assert quarantined == []
