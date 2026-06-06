import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone

from .doc_models import (
    DocumentationSyncLockRecord,
    LOCK_MODE_READ,
    LOCK_MODE_WRITE,
    LOCK_STATUS_ACTIVE,
    LOCK_STATUS_STALE,
    LOCK_STATUS_RELEASED,
    LOCK_STATUS_BLOCKED,
    CENTRAL_STATUS_BLOCKED,
    new_id,
    utc_now_iso,
    to_dict,
)

LOCK_PATH = ".agentx-init/docs_sync/docs_sync.lock"
STALE_LOCK_TIMEOUT_SECONDS = 300


def acquire_docs_sync_lock(
    repo_root: Path,
    mode: str,
    owner_id: str | None = None,
) -> dict:
    lock_file = (repo_root / LOCK_PATH).resolve()
    lock_file.parent.mkdir(parents=True, exist_ok=True)

    existing = read_docs_sync_lock(repo_root)
    if existing is not None:
        status = existing.get("status", "")
        if status == LOCK_STATUS_ACTIVE:
            now_utc = utc_now_iso()
            if is_lock_stale(existing, now_utc):
                return {
                    "status": LOCK_STATUS_STALE,
                    "lock": existing,
                    "reason": "stale lock exists",
                }
            if mode == LOCK_MODE_WRITE:
                return {
                    "status": LOCK_STATUS_BLOCKED,
                    "lock": existing,
                    "reason": "active lock exists, write acquisition blocked",
                }
            return {
                "status": LOCK_STATUS_ACTIVE,
                "lock": existing,
                "reason": "concurrent read allowed",
            }

    lock_record = DocumentationSyncLockRecord(
        lock_id=new_id("lock"),
        created_at=utc_now_iso(),
        mode=mode,
        repo_root=str(repo_root),
        owner_id=owner_id,
        pid=os.getpid(),
        status=LOCK_STATUS_ACTIVE,
    )

    lock_data = to_dict(lock_record)
    try:
        with open(lock_file, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2, default=str)
    except OSError as e:
        return {"status": LOCK_STATUS_BLOCKED, "reason": f"failed to write lock: {e}"}

    return {
        "status": LOCK_STATUS_ACTIVE,
        "lock": lock_data,
        "reason": "lock acquired",
    }


def release_docs_sync_lock(repo_root: Path, lock_id: str) -> dict:
    lock_file = (repo_root / LOCK_PATH).resolve()
    existing = read_docs_sync_lock(repo_root)
    if existing is None:
        return {"status": "NOT_FOUND", "reason": "no lock exists"}
    if existing.get("lock_id") != lock_id:
        return {"status": LOCK_STATUS_BLOCKED, "reason": "lock_id mismatch"}
    try:
        lock_file.unlink()
    except OSError as e:
        return {"status": "FAILED", "reason": str(e)}
    return {"status": LOCK_STATUS_RELEASED, "reason": "lock released"}


def read_docs_sync_lock(repo_root: Path) -> dict | None:
    lock_file = (repo_root / LOCK_PATH).resolve()
    if not lock_file.exists():
        return None
    try:
        with open(lock_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def is_lock_stale(
    lock_record: dict,
    now_utc: str | None = None,
) -> bool:
    if now_utc is None:
        now_utc = utc_now_iso()
    created_at = lock_record.get("created_at", "")
    if not created_at:
        return True
    pid = lock_record.get("pid")
    if pid is not None:
        try:
            os.kill(pid, 0)
            return False
        except (OSError, ProcessLookupError):
            return True
    try:
        created_dt = datetime.fromisoformat(created_at)
        now_dt = datetime.fromisoformat(now_utc)
        delta = (now_dt - created_dt).total_seconds()
        return delta > STALE_LOCK_TIMEOUT_SECONDS
    except (ValueError, TypeError):
        return True


def recover_stale_docs_sync_lock(
    repo_root: Path,
    policy_context: dict | None = None,
) -> dict:
    lock_file = (repo_root / LOCK_PATH).resolve()
    existing = read_docs_sync_lock(repo_root)

    if existing is None:
        return {"status": LOCK_STATUS_RELEASED, "reason": "no lock to recover"}

    if not is_lock_stale(existing):
        return {"status": LOCK_STATUS_BLOCKED, "reason": "lock is not stale"}

    try:
        lock_file.unlink()
    except OSError as e:
        return {"status": LOCK_STATUS_BLOCKED, "reason": f"failed to remove stale lock: {e}"}

    return {"status": LOCK_STATUS_RELEASED, "reason": "stale lock recovered"}
