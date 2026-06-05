import json
from pathlib import Path

import pytest

from agentx_evolve.queue.task_queue import (
    TaskQueueItem, TaskQueue, QueueManifest,
    QS_PENDING, QS_RUNNING, QS_PAUSED, QS_COMPLETED, QS_CANCELLED, QS_FAILED,
    ALL_QUEUE_STATUSES,
    TQ_SCHEMA_VERSION, TQ_SCHEMA_ID,
    canonical_json, sha256_dict, write_json_atomic, append_jsonl, queue_runs_dir,
)


class TestConstants:
    def test_tq_schema_version(self):
        assert TQ_SCHEMA_VERSION == "1.0"

    def test_tq_schema_id(self):
        assert TQ_SCHEMA_ID == "task_queue_item.schema.json"

    def test_all_queue_statuses(self):
        assert QS_PENDING in ALL_QUEUE_STATUSES
        assert QS_RUNNING in ALL_QUEUE_STATUSES
        assert QS_PAUSED in ALL_QUEUE_STATUSES
        assert QS_COMPLETED in ALL_QUEUE_STATUSES
        assert QS_CANCELLED in ALL_QUEUE_STATUSES
        assert QS_FAILED in ALL_QUEUE_STATUSES
        assert len(ALL_QUEUE_STATUSES) == 6


class TestCanonicalJsonAndHash:
    def test_canonical_json_sorts_keys(self):
        result = canonical_json({"b": 2, "a": 1})
        assert result == '{"a":1,"b":2}'

    def test_sha256_dict_is_deterministic(self):
        data = {"test": "value", "num": 42}
        assert sha256_dict(data) == sha256_dict(data)

    def test_sha256_dict_different_data(self):
        assert sha256_dict({"a": 1}) != sha256_dict({"a": 2})


class TestTaskQueueItem:
    def test_task_queue_item_defaults(self):
        item = TaskQueueItem()
        assert item.item_id == ""
        assert item.session_id == ""
        assert item.description == ""
        assert item.status == QS_PENDING
        assert item.priority == 0
        assert item.created_at == ""
        assert item.warnings == []
        assert item.errors == []

    def test_task_queue_item_to_dict(self):
        item = TaskQueueItem(item_id="tq_001", session_id="sess_1",
                             description="test", priority=5)
        d = item.to_dict()
        assert d["item_id"] == "tq_001"
        assert d["session_id"] == "sess_1"
        assert d["description"] == "test"
        assert d["priority"] == 5
        assert d["status"] == QS_PENDING

    def test_validate_schema_valid(self):
        data = {
            "schema_version": "1.0",
            "schema_id": "task_queue_item.schema.json",
            "item_id": "tq_abc",
            "session_id": "sess_1",
            "description": "test task",
            "status": "PENDING",
            "priority": 3,
            "created_at": "2025-01-01T00:00:00",
            "warnings": [],
            "errors": [],
        }
        errs = TaskQueueItem.validate_schema(data)
        assert errs == []

    def test_validate_schema_missing_field(self):
        data = {"item_id": "tq_abc"}
        errs = TaskQueueItem.validate_schema(data)
        assert any("schema_version" in e for e in errs)
        assert any("session_id" in e for e in errs)

    def test_validate_schema_bad_status(self):
        data = {
            "schema_version": "1.0",
            "schema_id": "task_queue_item.schema.json",
            "item_id": "tq_abc",
            "session_id": "sess_1",
            "description": "test",
            "status": "INVALID",
            "priority": 0,
            "created_at": "",
            "warnings": [],
            "errors": [],
        }
        errs = TaskQueueItem.validate_schema(data)
        assert any("status" in e for e in errs)

    def test_validate_schema_bad_schema_version(self):
        data = {
            "schema_version": "2.0",
            "schema_id": "task_queue_item.schema.json",
            "item_id": "tq_abc",
            "session_id": "sess_1",
            "description": "test",
            "status": "PENDING",
            "priority": 0,
            "created_at": "",
            "warnings": [],
            "errors": [],
        }
        errs = TaskQueueItem.validate_schema(data)
        assert any("schema_version" in e for e in errs)


class TestTaskQueue:
    def test_enqueue_adds_item(self):
        q = TaskQueue()
        item = q.enqueue("sess_1", "test task", priority=3)
        assert item.item_id.startswith("tq")
        assert item.session_id == "sess_1"
        assert item.description == "test task"
        assert item.priority == 3
        assert item.status == QS_PENDING
        assert item.created_at != ""

    def test_get_returns_item(self):
        q = TaskQueue()
        item = q.enqueue("sess_1", "test")
        assert q.get(item.item_id) is item

    def test_get_returns_none(self):
        q = TaskQueue()
        assert q.get("nonexistent") is None

    def test_list_all_returns_sorted(self):
        q = TaskQueue()
        i1 = q.enqueue("sess_1", "low", priority=1)
        i2 = q.enqueue("sess_2", "high", priority=10)
        i3 = q.enqueue("sess_3", "medium", priority=5)
        items = q.list_all()
        assert [i.priority for i in items] == [10, 5, 1]

    def test_list_all_by_status(self):
        q = TaskQueue()
        i1 = q.enqueue("sess_1", "a")
        i2 = q.enqueue("sess_2", "b")
        q.update_status(i2.item_id, QS_RUNNING)
        pending = q.list_all(status=QS_PENDING)
        running = q.list_all(status=QS_RUNNING)
        assert len(pending) == 1
        assert pending[0].item_id == i1.item_id
        assert len(running) == 1
        assert running[0].item_id == i2.item_id

    def test_update_status_changes(self):
        q = TaskQueue()
        item = q.enqueue("sess_1", "test")
        assert item.status == QS_PENDING
        result = q.update_status(item.item_id, QS_RUNNING)
        assert result is True
        assert item.status == QS_RUNNING

    def test_update_status_nonexistent(self):
        q = TaskQueue()
        assert q.update_status("nonexistent", QS_RUNNING) is False

    def test_remove_deletes(self):
        q = TaskQueue()
        item = q.enqueue("sess_1", "test")
        assert q.get(item.item_id) is not None
        assert q.remove(item.item_id) is True
        assert q.get(item.item_id) is None

    def test_remove_nonexistent(self):
        q = TaskQueue()
        assert q.remove("nonexistent") is False

    def test_clear_completed_removes_completed_cancelled_failed(self):
        q = TaskQueue()
        i1 = q.enqueue("sess_1", "pending")
        i2 = q.enqueue("sess_2", "completed")
        i3 = q.enqueue("sess_3", "cancelled")
        i4 = q.enqueue("sess_4", "failed")
        i5 = q.enqueue("sess_5", "running")
        q.update_status(i2.item_id, QS_COMPLETED)
        q.update_status(i3.item_id, QS_CANCELLED)
        q.update_status(i4.item_id, QS_FAILED)
        q.update_status(i5.item_id, QS_RUNNING)
        removed = q.clear_completed()
        assert removed == 3
        assert q.get(i1.item_id) is not None
        assert q.get(i2.item_id) is None
        assert q.get(i3.item_id) is None
        assert q.get(i4.item_id) is None
        assert q.get(i5.item_id) is not None


class TestQueueManifest:
    def test_queue_manifest_defaults(self):
        m = QueueManifest()
        assert m.manifest_id == ""
        assert m.total_items == 0
        assert m.pending == 0
        assert m.running == 0
        assert m.completed == 0
        assert m.failed == 0
        assert m.cancelled == 0
        assert m.paused == 0
        assert m.created_at == ""
        assert m.warnings == []
        assert m.errors == []

    def test_queue_manifest_to_dict(self):
        m = QueueManifest(manifest_id="qm_001", total_items=5, pending=2)
        d = m.to_dict()
        assert d["manifest_id"] == "qm_001"
        assert d["total_items"] == 5
        assert d["pending"] == 2


class TestPersistence:
    def test_write_queue_manifest_creates_file(self, tmp_path: Path):
        q = TaskQueue()
        q.enqueue("sess_1", "test")
        manifest = q.generate_manifest()
        result_path = q.write_queue_manifest(manifest, tmp_path)
        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert data["manifest_id"] == manifest.manifest_id
        assert data["total_items"] == 1

    def test_append_queue_history_appends(self, tmp_path: Path):
        q = TaskQueue()
        item = q.enqueue("sess_1", "test")
        history_path = q.append_queue_history(item, tmp_path)
        assert history_path.exists()
        lines = history_path.read_text().strip().split("\n")
        assert len(lines) >= 1
        last = json.loads(lines[-1])
        assert last["item_id"] == item.item_id

    def test_queue_lock_acquire_release(self, tmp_path: Path):
        q = TaskQueue()
        lock = q.acquire_queue_lock(tmp_path)
        assert lock["acquired"] is True
        q.release_queue_lock(lock, tmp_path)
        lock_path = queue_runs_dir(tmp_path) / ".queue.lock"
        assert not lock_path.exists()

    def test_lock_timeout_raises(self, tmp_path: Path):
        q = TaskQueue()
        lock1 = q.acquire_queue_lock(tmp_path)
        with pytest.raises(TimeoutError):
            q.acquire_queue_lock(tmp_path, timeout_seconds=0)
        q.release_queue_lock(lock1, tmp_path)

    def test_generate_manifest_returns_valid(self):
        q = TaskQueue()
        q.enqueue("sess_1", "a")
        q.enqueue("sess_2", "b")
        q.enqueue("sess_3", "c")
        manifest = q.generate_manifest()
        assert manifest.manifest_id.startswith("qm")
        assert manifest.total_items == 3
        assert manifest.pending == 3
        assert manifest.running == 0
        assert manifest.completed == 0
        assert manifest.failed == 0
        assert manifest.cancelled == 0
        assert manifest.paused == 0
        assert manifest.created_at != ""

    def test_save_to_disk_creates_file(self, tmp_path: Path):
        q = TaskQueue()
        q.enqueue("sess_1", "test")
        path = q.save_to_disk(tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["schema_version"] == TQ_SCHEMA_VERSION
        assert len(data["items"]) == 1

    def test_load_from_disk_restores_state(self, tmp_path: Path):
        q1 = TaskQueue()
        item1 = q1.enqueue("sess_1", "task one", priority=5)
        item2 = q1.enqueue("sess_2", "task two", priority=1)
        q1.update_status(item2.item_id, QS_RUNNING)
        q1.save_to_disk(tmp_path)

        q2 = TaskQueue()
        q2.load_from_disk(tmp_path)
        assert len(q2.list_all()) == 2
        loaded_item1 = q2.get(item1.item_id)
        assert loaded_item1 is not None
        assert loaded_item1.description == "task one"
        assert loaded_item1.priority == 5
        loaded_item2 = q2.get(item2.item_id)
        assert loaded_item2 is not None
        assert loaded_item2.status == QS_RUNNING

    def test_queue_runs_dir(self):
        p = queue_runs_dir(Path("/repo"))
        assert p == Path("/repo/.agentx-init/queue")
