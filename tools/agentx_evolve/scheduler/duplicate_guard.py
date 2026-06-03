from __future__ import annotations

import json
import logging
from pathlib import Path

from agentx_evolve.scheduler.scheduler_models import (
    TaskRecord,
    utc_now_iso,
    new_id,
    to_dict,
    sha256_bytes,
    canonical_json,
)

logger = logging.getLogger(__name__)

GUARD_INDEX_FILE = "duplicate_index.jsonl"


class DuplicateGuard:
    def __init__(self, guard_dir: str | Path):
        self.guard_dir = Path(guard_dir)
        self.guard_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.guard_dir / GUARD_INDEX_FILE

    def compute_task_fingerprint(self, task: TaskRecord) -> str:
        payload = {
            "task_id": task.task_id,
            "payload_ref": task.payload_ref,
            "dependency_ids": sorted(task.dependency_ids) if task.dependency_ids else [],
            "priority": task.priority,
        }
        return sha256_bytes(canonical_json(payload))

    def is_duplicate(self, task: TaskRecord) -> bool:
        fingerprint = self.compute_task_fingerprint(task)
        existing = self._load_index()
        return fingerprint in existing

    def register_task(self, task: TaskRecord) -> dict:
        fingerprint = self.compute_task_fingerprint(task)
        if self.is_duplicate(task):
            logger.warning("Duplicate task detected: %s (fingerprint: %s)", task.task_id, fingerprint)
            return {"status": "DUPLICATE_DETECTED", "task_id": task.task_id, "fingerprint": fingerprint}
        entry = {
            "fingerprint": fingerprint,
            "task_id": task.task_id,
            "registered_at": utc_now_iso(),
        }
        with open(self._index_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        logger.info("Registered task: %s (fingerprint: %s)", task.task_id, fingerprint)
        return {"status": "REGISTERED", "task_id": task.task_id, "fingerprint": fingerprint}

    def clear(self) -> None:
        if self._index_path.exists():
            self._index_path.unlink()
            logger.info("Duplicate guard index cleared")

    def _load_index(self) -> set[str]:
        if not self._index_path.exists():
            return set()
        fingerprints: set[str] = set()
        with open(self._index_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    fp = data.get("fingerprint")
                    if fp:
                        fingerprints.add(fp)
                except json.JSONDecodeError:
                    continue
        return fingerprints
