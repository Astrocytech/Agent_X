from __future__ import annotations

import json
import os
import time
import logging
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_utils import append_jsonl
from agentx_evolve.models.model_models import new_id, utc_now_iso

logger = logging.getLogger(__name__)

LOCK_DIR = ".agentx-init/monitoring/locks"
LOCK_TIMEOUT_SECONDS = 30


def _lock_path(repo_root: Path, resource: str) -> Path:
    return repo_root / LOCK_DIR / f"{resource}.lock"


def acquire_file_lock(
    resource: str,
    repo_root: Path,
    owner: str = "",
    timeout_seconds: int = LOCK_TIMEOUT_SECONDS,
) -> str | None:
    lock_path = _lock_path(repo_root, resource)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_id = new_id("lk")
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            data = {
                "lock_id": lock_id,
                "resource": resource,
                "owner": owner,
                "acquired_at": utc_now_iso(),
                "status": "LOCKED",
            }
            lock_path.write_text(json.dumps(data), encoding="utf-8")
            history = repo_root / ".agentx-init/monitoring" / "lock_history.jsonl"
            append_jsonl(history, data)
            return lock_id
        except FileExistsError:
            try:
                existing = json.loads(lock_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                os.unlink(str(lock_path))
                continue
            time.sleep(0.1)
    return None


def release_file_lock(resource: str, repo_root: Path) -> bool:
    lock_path = _lock_path(repo_root, resource)
    try:
        if lock_path.exists():
            os.unlink(str(lock_path))
            return True
    except OSError:
        pass
    return False


def check_file_lock(resource: str, repo_root: Path) -> bool:
    lock_path = _lock_path(repo_root, resource)
    return lock_path.exists()
