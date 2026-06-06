import json
import os
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, canonical_json, sha256_bytes, sha256_file,
    to_dict, compute_task_record_hash,
    TaskRecord, QueueState, SCHEDULER_STATUS_QUEUED,
    SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_VALUES, SCHEDULER_EVENT_CORRUPTION,
    SCHEDULER_EVENT_QUARANTINE, SCHEDULER_EVENT_SNAPSHOT,
)


QUEUE_HISTORY_FILE = "task_history.jsonl"
QUEUE_SNAPSHOT_FILE = "queue_state.json"
QUEUE_QUARANTINE_FILE = "quarantine.jsonl"
QUEUE_LOCK_FILE = "queue.lock"


class QueueStore:
    def __init__(self, queue_dir: str | Path):
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self._history_path = self.queue_dir / QUEUE_HISTORY_FILE
        self._snapshot_path = self.queue_dir / QUEUE_SNAPSHOT_FILE
        self._quarantine_path = self.queue_dir / QUEUE_QUARANTINE_FILE
        self._lock_path = self.queue_dir / QUEUE_LOCK_FILE
        self._append_counter = 0

    def _next_sequence(self) -> int:
        self._append_counter += 1
        return self._append_counter

    def append_task(self, task: TaskRecord) -> dict:
        record = _redact_sensitive(to_dict(task))
        record["task_record_hash"] = compute_task_record_hash(record)
        line = json.dumps(record, sort_keys=True, default=str) + "\n"
        with open(self._history_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"record_id": task.record_id, "task_id": task.task_id, "status": "appended"}

    def replay_tasks(self) -> tuple[list[TaskRecord], list[dict]]:
        valid = []
        quarantined = []
        if not self._history_path.exists():
            return valid, quarantined
        with open(self._history_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    quarantined.append(self._quarantine_line(line, line_no, f"json_parse_error: {e}"))
                    continue
                record = self._dict_to_task_record(data)
                if record is None:
                    quarantined.append(self._quarantine_line(line, line_no, "schema_invalid"))
                    continue
                valid.append(record)
        return valid, quarantined

    def write_quarantine(self, entry: dict) -> dict:
        line = json.dumps(entry, default=str) + "\n"
        with open(self._quarantine_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"path": str(self._quarantine_path), "status": "quarantined"}

    def _quarantine_line(self, raw_line: str, line_no: int, error: str) -> dict:
        entry = {
            "source": str(self._history_path),
            "line_number": line_no,
            "error": error,
            "line_hash": sha256_bytes(raw_line.encode("utf-8")),
            "quarantined_at": utc_now_iso(),
        }
        self.write_quarantine(entry)
        return entry

    def build_snapshot(self) -> QueueState:
        tasks, quarantined = self.replay_tasks()
        effective = self._effective_tasks(tasks)
        by_status = {}
        for t in effective.values():
            by_status[t.status] = by_status.get(t.status, 0) + 1
        state = QueueState(
            queue_id=self.queue_dir.name,
            total_tasks=len(effective),
            by_status=by_status,
        )
        state.queue_hash = self._compute_queue_hash(effective)
        self._write_snapshot(state)
        return state, quarantined

    def _write_snapshot(self, state: QueueState) -> dict:
        tmp = self._snapshot_path.with_suffix(".tmp")
        data = to_dict(state)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        tmp.replace(self._snapshot_path)
        return {"path": str(self._snapshot_path), "status": "snapshot_written"}

    def load_snapshot(self) -> QueueState | None:
        if not self._snapshot_path.exists():
            return None
        try:
            with open(self._snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return QueueState(
                queue_id=data.get("queue_id", self.queue_dir.name),
                snapshot_at=data.get("snapshot_at", utc_now_iso()),
                total_tasks=data.get("total_tasks", 0),
                by_status=data.get("by_status", {}),
                queue_hash=data.get("queue_hash", ""),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def compact_history(self) -> dict:
        tasks, quarantined = self.replay_tasks()
        effective = self._effective_tasks(tasks)
        compacted = [_sort_task_fields(to_dict(t)) for t in effective.values()]
        compacted.sort(key=lambda x: (x.get("priority", 50), x.get("created_at", "")), reverse=True)
        backup = self._history_path.with_suffix(".jsonl.bak")
        if self._history_path.exists():
            import shutil
            shutil.copy2(self._history_path, backup)
        with open(self._history_path, "w", encoding="utf-8") as f:
            for record in compacted:
                record["task_record_hash"] = compute_task_record_hash(record)
                f.write(json.dumps(record, sort_keys=True, default=str) + "\n")
        return {
            "status": "compacted",
            "backup_path": str(backup),
            "records_written": len(compacted),
            "quarantined": len(quarantined),
        }

    def _effective_tasks(self, tasks: list[TaskRecord]) -> dict[str, TaskRecord]:
        effective: dict[str, TaskRecord] = {}
        for t in sorted(tasks, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
            effective[t.task_id] = t
        return effective

    def _compute_queue_hash(self, effective: dict[str, TaskRecord]) -> str:
        serialized = canonical_json({tid: to_dict(t) for tid, t in sorted(effective.items())})
        return sha256_bytes(serialized)

    def _dict_to_task_record(self, data: dict) -> TaskRecord | None:
        try:
            return TaskRecord(
                record_id=data.get("record_id", ""),
                task_id=data.get("task_id", ""),
                session_id=data.get("session_id", ""),
                status=data.get("status", SCHEDULER_STATUS_QUEUED),
                priority=data.get("priority", 50),
                payload_ref=data.get("payload_ref", ""),
                dependency_ids=data.get("dependency_ids", []),
                retry_count=data.get("retry_count", 0),
                max_retries=data.get("max_retries", 3),
                next_run_at=data.get("next_run_at"),
                previous_record_hash=data.get("previous_record_hash", ""),
                task_record_hash=data.get("task_record_hash", ""),
                append_sequence=data.get("append_sequence", 0),
                revision=data.get("revision", 1),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                warnings=data.get("warnings", []),
                errors=data.get("errors", []),
            )
        except (KeyError, TypeError):
            return None


def _redact_sensitive(record: dict) -> dict:
    return record


def _sort_task_fields(data: dict) -> dict:
    order = [
        "schema_version", "schema_id", "record_id", "task_id", "session_id",
        "status", "priority", "payload_ref", "dependency_ids", "retry_count",
        "max_retries", "next_run_at", "previous_record_hash", "task_record_hash",
        "append_sequence", "revision", "created_at", "updated_at",
        "warnings", "errors",
    ]
    return {k: data[k] for k in order if k in data}
