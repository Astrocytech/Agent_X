from __future__ import annotations
import os
import time
from datetime import datetime, timezone
from pathlib import Path


class RunLock:
    def __init__(self, lock_dir: str | Path, run_id: str, stale_seconds: int = 300):
        self._lock_dir = Path(lock_dir)
        self._run_id = run_id
        self._stale_seconds = stale_seconds
        self._lock_file = self._lock_dir / f"{run_id}.lock"
        self._held = False

    def acquire(self) -> bool:
        self._lock_dir.mkdir(parents=True, exist_ok=True)
        if self._lock_file.exists():
            if self._is_stale():
                self._lock_file.write_text(self._stamp())
                self._held = True
                return True
            return False
        self._lock_file.write_text(self._stamp())
        self._held = True
        return True

    def release(self) -> None:
        if self._held and self._lock_file.exists():
            self._lock_file.unlink()
            self._held = False

    def _is_stale(self) -> bool:
        try:
            age = time.time() - self._lock_file.stat().st_mtime
            return age > self._stale_seconds
        except OSError:
            return False

    @staticmethod
    def _stamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def __enter__(self) -> "RunLock":
        self.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self.release()
