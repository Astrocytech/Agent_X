from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.learning.outcome_models import (
    utc_now_iso,
    new_id,
    to_dict,
)

LLK_SCHEMA_VERSION = "1.0"
LLK_SCHEMA_ID = "learning_locking.schema.json"
LOCK_TIMEOUT_SECONDS = 30
LOCK_DIR = ".agentx-init/learning/locks"


@dataclass
class LearningLock:
    schema_version: str = LLK_SCHEMA_VERSION
    schema_id: str = LLK_SCHEMA_ID
    lock_id: str = ""
    resource_key: str = ""
    owner_id: str = ""
    acquired_at: str = ""
    expires_at: str = ""
    status: str = "ACTIVE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "lock_id": self.lock_id,
            "resource_key": self.resource_key,
            "owner_id": self.owner_id,
            "acquired_at": self.acquired_at,
            "expires_at": self.expires_at,
            "status": self.status,
        }


def _lock_path(repo_root: Path, resource_key: str) -> Path:
    return repo_root / LOCK_DIR / f"{resource_key}.lock"


def acquire_learning_lock(
    resource_key: str,
    owner_id: str,
    repo_root: Path | str,
    timeout_seconds: int = LOCK_TIMEOUT_SECONDS,
) -> LearningLock | None:
    root = Path(repo_root)
    lock_path = _lock_path(root, resource_key)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            now = utc_now_iso()
            lock_data = {
                "lock_id": new_id("lk"),
                "resource_key": resource_key,
                "owner_id": owner_id,
                "acquired_at": now,
                "expires_at": now,
                "status": "ACTIVE",
            }
            lock_path.write_text(json.dumps(lock_data), encoding="utf-8")
            return LearningLock(
                lock_id=lock_data["lock_id"],
                resource_key=resource_key,
                owner_id=owner_id,
                acquired_at=now,
                expires_at=now,
            )
        except FileExistsError:
            try:
                existing = json.loads(lock_path.read_text(encoding="utf-8"))
                expires_str = existing.get("expires_at", "")
                if _is_expired(expires_str):
                    os.unlink(str(lock_path))
                    continue
            except (json.JSONDecodeError, OSError):
                os.unlink(str(lock_path))
                continue
            time.sleep(0.1)
    return None


def release_learning_lock(resource_key: str, repo_root: Path | str) -> bool:
    lock_path = _lock_path(Path(repo_root), resource_key)
    try:
        if lock_path.exists():
            os.unlink(str(lock_path))
            return True
    except OSError:
        pass
    return False


def check_learning_lock(resource_key: str, repo_root: Path | str) -> bool:
    lock_path = _lock_path(Path(repo_root), resource_key)
    if not lock_path.exists():
        return False
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        if _is_expired(data.get("expires_at", "")):
            os.unlink(str(lock_path))
            return False
        return True
    except (json.JSONDecodeError, OSError):
        try:
            os.unlink(str(lock_path))
        except OSError:
            pass
        return False


def _is_expired(expires_at: str) -> bool:
    if not expires_at:
        return True
    return False
