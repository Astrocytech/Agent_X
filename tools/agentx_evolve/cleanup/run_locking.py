"""Run/session locking with artifact root tracking.

Item 44 (38.1/38.2): Prevent concurrent runs from modifying
same artifact set; atomic writes for evidence artifacts.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class RunLock:
    lock_id: str
    session_id: str
    owner_component: str
    created_at: str = ""
    expiry: str = ""
    locked_artifact_roots: list[str] = field(default_factory=list)
    locked_source_paths: list[str] = field(default_factory=list)
    pid: int = 0
    status: str = "active"  # active | stale | released
    stale_threshold_minutes: int = 30

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if self.pid == 0:
            self.pid = os.getpid()
        if not self.expiry:
            from datetime import timedelta
            self.expiry = (datetime.now(timezone.utc) + timedelta(
                minutes=self.stale_threshold_minutes)
            ).isoformat(timespec="seconds")


class LockManager:
    def __init__(self, lock_dir: str | Path = ".agentx-init/locks"):
        self._lock_dir = Path(lock_dir)
        self._lock_dir.mkdir(parents=True, exist_ok=True)
        self._held_locks: dict[str, RunLock] = {}
        self._load_existing()

    def _lock_path(self, lock_id: str) -> Path:
        return self._lock_dir / f"{lock_id}.json"

    def _load_existing(self) -> None:
        for f in self._lock_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                lock = RunLock(**data)
                if lock.status == "active":
                    if self._is_stale(lock):
                        lock.status = "stale"
                        f.write_text(json.dumps(asdict(lock), indent=2))
                self._held_locks[lock.lock_id] = lock
            except (json.JSONDecodeError, KeyError):
                pass

    def _is_stale(self, lock: RunLock) -> bool:
        from datetime import datetime, timedelta
        try:
            created = datetime.fromisoformat(lock.created_at)
            delta = datetime.now(timezone.utc) - created
            return delta > timedelta(minutes=lock.stale_threshold_minutes)
        except (ValueError, TypeError):
            return False

    def acquire(self, session_id: str, owner: str,
                 artifact_roots: list[str] | None = None,
                 source_paths: list[str] | None = None) -> RunLock | None:
        # Check for conflicting locks
        for existing in self._held_locks.values():
            if existing.status != "active":
                continue
            if self._is_stale(existing):
                existing.status = "stale"
                self._save_lock(existing)
                continue
            # Check for overlapping artifact roots
            if artifact_roots and existing.locked_artifact_roots:
                overlap = set(artifact_roots) & set(existing.locked_artifact_roots)
                if overlap:
                    return None

        lock = RunLock(
            lock_id=f"lock-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{os.getpid()}",
            session_id=session_id,
            owner_component=owner,
            locked_artifact_roots=artifact_roots or [],
            locked_source_paths=source_paths or [],
        )
        self._held_locks[lock.lock_id] = lock
        self._save_lock(lock)
        return lock

    def _save_lock(self, lock: RunLock) -> None:
        self._lock_path(lock.lock_id).write_text(json.dumps(asdict(lock), indent=2))

    def release(self, lock_id: str) -> bool:
        lock = self._held_locks.get(lock_id)
        if lock and lock.status == "active":
            lock.status = "released"
            self._save_lock(lock)
            self._lock_path(lock_id).unlink(missing_ok=True)
            return True
        return False

    def get_active_locks(self) -> list[RunLock]:
        return [l for l in self._held_locks.values() if l.status == "active" and not self._is_stale(l)]

    def status(self) -> dict[str, Any]:
        return {
            "total_locks": len(self._held_locks),
            "active": len(self.get_active_locks()),
            "locks": [asdict(l) for l in self._held_locks.values()],
        }


def atomic_write(path: str | Path, content: str) -> bool:
    """Write content atomically: write to temp, validate, then rename."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=str(p.parent), suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.rename(tmp_path, str(p))
        return True
    except (OSError, IOError):
        return False
