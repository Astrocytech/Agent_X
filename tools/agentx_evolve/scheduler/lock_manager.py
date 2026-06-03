import json
import os
import time
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SCHEDULER_LOCK_STATUS_ACTIVE, SCHEDULER_LOCK_STATUS_STALE,
    SCHEDULER_LOCK_STATUS_RELEASED,
)


LOCK_ACQUIRED = "LOCK_ACQUIRED"
LOCK_DENIED = "SCHEDULER_LOCK_DENIED"
LOCK_STALE_RECOVERED = "LOCK_STALE_RECOVERED"


class LockManager:
    def __init__(self, lock_dir: str | Path, stale_timeout_seconds: int = 600):
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self._stale_timeout = stale_timeout_seconds

    def _lock_path(self, lock_name: str) -> Path:
        return self.lock_dir / f"{lock_name}.lock"

    def acquire(self, lock_name: str, owner_id: str) -> dict:
        lock_path = self._lock_path(lock_name)
        payload = {
            "lock_name": lock_name,
            "owner_id": owner_id,
            "status": SCHEDULER_LOCK_STATUS_ACTIVE,
            "acquired_at": utc_now_iso(),
            "lock_id": new_id("lk"),
        }
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            with os.fdopen(fd, "w") as f:
                json.dump(payload, f, indent=2, default=str)
            return {"status": LOCK_ACQUIRED, "lock_name": lock_name, "owner_id": owner_id, "payload": payload}
        except FileExistsError:
            existing = self._read_lock(lock_path)
            if existing is None:
                return {"status": LOCK_DENIED, "lock_name": lock_name, "reason": "lock_read_error"}
            if self._is_stale(existing):
                recovery = self._recover_stale_lock(lock_path, existing, owner_id)
                if recovery["status"] == LOCK_STALE_RECOVERED:
                    return self.acquire(lock_name, owner_id)
                return {"status": LOCK_DENIED, "lock_name": lock_name, "reason": "stale_lock_recovery_failed"}
            return {"status": LOCK_DENIED, "lock_name": lock_name, "reason": "already_locked", "owner": existing.get("owner_id", "")}

    def release(self, lock_name: str, owner_id: str) -> dict:
        lock_path = self._lock_path(lock_name)
        if not lock_path.exists():
            return {"status": "LOCK_NOT_FOUND", "lock_name": lock_name}
        existing = self._read_lock(lock_path)
        if existing is None:
            return {"status": "LOCK_READ_ERROR", "lock_name": lock_name}
        if existing.get("owner_id") != owner_id:
            return {"status": "LOCK_NOT_OWNER", "lock_name": lock_name, "owner": existing.get("owner_id", "")}
        lock_path.unlink(missing_ok=True)
        return {"status": LOCK_ACQUIRED.replace("ACQUIRED", "RELEASED"), "lock_name": lock_name, "owner_id": owner_id}

    def is_locked(self, lock_name: str) -> bool:
        lock_path = self._lock_path(lock_name)
        if not lock_path.exists():
            return False
        existing = self._read_lock(lock_path)
        if existing is None:
            return False
        if self._is_stale(existing):
            return False
        return existing.get("status") == SCHEDULER_LOCK_STATUS_ACTIVE

    def get_lock_info(self, lock_name: str) -> dict | None:
        lock_path = self._lock_path(lock_name)
        if not lock_path.exists():
            return None
        return self._read_lock(lock_path)

    def _read_lock(self, path: Path) -> dict | None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _is_stale(self, lock_data: dict) -> bool:
        acquired_at = lock_data.get("acquired_at", "")
        if not acquired_at:
            return True
        try:
            from datetime import datetime, timezone
            acquired = datetime.fromisoformat(acquired_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            elapsed = (now - acquired).total_seconds()
            return elapsed > self._stale_timeout
        except (ValueError, TypeError):
            return True

    def _recover_stale_lock(self, lock_path: Path, existing: dict, new_owner: str) -> dict:
        now = utc_now_iso()
        recovery_record = lock_path.with_suffix(".recovery.json")
        recovery_data = {
            "lock_name": lock_path.stem,
            "previous_owner": existing.get("owner_id", ""),
            "new_owner": new_owner,
            "status": SCHEDULER_LOCK_STATUS_STALE,
            "recovered_at": now,
        }
        with open(recovery_record, "w", encoding="utf-8") as f:
            json.dump(recovery_data, f, indent=2, default=str)
        lock_path.unlink(missing_ok=True)
        return {"status": LOCK_STALE_RECOVERED, "lock_name": lock_path.stem, "recovery_record": str(recovery_record)}
