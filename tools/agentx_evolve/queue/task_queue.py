from __future__ import annotations
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from agentx_evolve.models.model_models import new_id, to_dict

TQ_SCHEMA_VERSION = "1.0"
TQ_SCHEMA_ID = "task_queue_item.schema.json"

QS_PENDING = "PENDING"
QS_RUNNING = "RUNNING"
QS_PAUSED = "PAUSED"
QS_COMPLETED = "COMPLETED"
QS_CANCELLED = "CANCELLED"
QS_FAILED = "FAILED"
ALL_QUEUE_STATUSES = [QS_PENDING, QS_RUNNING, QS_PAUSED, QS_COMPLETED, QS_CANCELLED, QS_FAILED]

_LOCK_TIMEOUT_SECONDS = 10


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


def queue_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "queue"


@dataclass
class TaskQueueItem:
    item_id: str = ""
    session_id: str = ""
    description: str = ""
    status: str = QS_PENDING
    priority: int = 0
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    @staticmethod
    def validate_schema(data: dict) -> list[str]:
        errors = []
        required = ["schema_version", "schema_id", "item_id", "session_id",
                     "description", "status", "priority", "created_at",
                     "warnings", "errors"]
        for field_name in required:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")
        if "schema_version" in data and data["schema_version"] != TQ_SCHEMA_VERSION:
            errors.append(f"schema_version must be {TQ_SCHEMA_VERSION}")
        if "schema_id" in data and data["schema_id"] != TQ_SCHEMA_ID:
            errors.append(f"schema_id must be {TQ_SCHEMA_ID}")
        if "status" in data and data["status"] not in ALL_QUEUE_STATUSES:
            errors.append(f"status must be one of {ALL_QUEUE_STATUSES}")
        if "priority" in data and not isinstance(data["priority"], int):
            errors.append("priority must be an integer")
        return errors


@dataclass
class QueueManifest:
    manifest_id: str = ""
    total_items: int = 0
    pending: int = 0
    running: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    paused: int = 0
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class TaskQueue:
    def __init__(self):
        self._items: dict[str, TaskQueueItem] = {}

    def enqueue(self, session_id: str, description: str,
                priority: int = 0) -> TaskQueueItem:
        item = TaskQueueItem(
            item_id=new_id("tq"),
            session_id=session_id,
            description=description,
            priority=priority,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._items[item.item_id] = item
        return item

    def get(self, item_id: str) -> TaskQueueItem | None:
        return self._items.get(item_id)

    def list_all(self, status: str | None = None) -> list[TaskQueueItem]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return sorted(items, key=lambda x: (-x.priority, x.created_at or ""))

    def update_status(self, item_id: str, status: str) -> bool:
        item = self._items.get(item_id)
        if item is None:
            return False
        item.status = status
        return True

    def remove(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def clear_completed(self) -> int:
        before = len(self._items)
        self._items = {k: v for k, v in self._items.items()
                       if v.status not in (QS_COMPLETED, QS_CANCELLED, QS_FAILED)}
        return before - len(self._items)

    def _persist_state(self, repo_root: Path) -> None:
        lock = self.acquire_queue_lock(repo_root)
        try:
            self.save_to_disk(repo_root)
            manifest = self.generate_manifest()
            self.write_queue_manifest(manifest, repo_root)
        finally:
            self.release_queue_lock(lock, repo_root)

    def save_to_disk(self, repo_root: Path) -> Path:
        dest = queue_runs_dir(repo_root) / "queue_state.json"
        items_data = [to_dict(item) for item in self._items.values()]
        payload = {
            "schema_version": TQ_SCHEMA_VERSION,
            "schema_id": TQ_SCHEMA_ID,
            "items": items_data,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        return write_json_atomic(dest, payload)

    def load_from_disk(self, repo_root: Path) -> None:
        src = queue_runs_dir(repo_root) / "queue_state.json"
        if not src.exists():
            return
        data = json.loads(src.read_text())
        items_data = data.get("items", [])
        self._items.clear()
        for item_data in items_data:
            item = TaskQueueItem(
                item_id=item_data.get("item_id", ""),
                session_id=item_data.get("session_id", ""),
                description=item_data.get("description", ""),
                status=item_data.get("status", QS_PENDING),
                priority=item_data.get("priority", 0),
                created_at=item_data.get("created_at", ""),
                warnings=item_data.get("warnings", []),
                errors=item_data.get("errors", []),
            )
            self._items[item.item_id] = item

    def write_queue_manifest(self, manifest: QueueManifest, repo_root: Path) -> Path:
        dest = queue_runs_dir(repo_root) / "queue_manifest.json"
        return write_json_atomic(dest, to_dict(manifest))

    def append_queue_history(self, item: TaskQueueItem, repo_root: Path) -> Path:
        dest = queue_runs_dir(repo_root) / "queue_history.jsonl"
        return append_jsonl(dest, to_dict(item))

    def generate_manifest(self) -> QueueManifest:
        all_items = list(self._items.values())
        pending = sum(1 for i in all_items if i.status == QS_PENDING)
        running = sum(1 for i in all_items if i.status == QS_RUNNING)
        completed = sum(1 for i in all_items if i.status == QS_COMPLETED)
        failed = sum(1 for i in all_items if i.status == QS_FAILED)
        cancelled = sum(1 for i in all_items if i.status == QS_CANCELLED)
        paused = sum(1 for i in all_items if i.status == QS_PAUSED)
        return QueueManifest(
            manifest_id=new_id("qm"),
            total_items=len(all_items),
            pending=pending,
            running=running,
            completed=completed,
            failed=failed,
            cancelled=cancelled,
            paused=paused,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def acquire_queue_lock(self, repo_root: Path, timeout_seconds: int = _LOCK_TIMEOUT_SECONDS) -> dict:
        lock_path = queue_runs_dir(repo_root) / ".queue.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return {"acquired": True, "path": str(lock_path)}
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Could not acquire queue lock within {timeout_seconds}s: {lock_path}")
                time.sleep(0.1)

    def release_queue_lock(self, lock: object, repo_root: Path) -> None:
        lock_path = queue_runs_dir(repo_root) / ".queue.lock"
        try:
            lock_path.unlink(missing_ok=True)
        except FileNotFoundError:
            pass
