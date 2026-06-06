from __future__ import annotations

import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Iterator

from agentx_evolve.backup.backup_models import (
    LOCK_STATUS_ACQUIRED,
    LOCK_STATUS_RELEASED,
    LOCK_STATUS_STALE,
    LOCK_STATUS_BLOCKED,
    BackupLockRecord,
    locks_dir,
    new_id,
    resolve_repo_root,
    to_dict,
    utc_now_iso,
    write_json_atomic,
)


def _lock_path(repo_root: Path, lock_name: str) -> Path:
    return locks_dir(repo_root) / f"{lock_name}.lock.json"


def _read_lock(repo_root: Path, lock_name: str) -> BackupLockRecord | None:
    path = _lock_path(repo_root, lock_name)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return BackupLockRecord(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None


def _write_lock(repo_root: Path, record: BackupLockRecord) -> Path:
    path = _lock_path(repo_root, record.lock_name)
    return write_json_atomic(path, to_dict(record))


def _is_stale(record: BackupLockRecord) -> bool:
    if record.status != LOCK_STATUS_ACQUIRED:
        return False
    try:
        acquired = datetime.fromisoformat(record.acquired_at)
        now = datetime.now(timezone.utc)
        elapsed = (now - acquired).total_seconds()
        return elapsed > record.stale_after_seconds
    except (ValueError, TypeError):
        return True


def _orig_acquire_backup_lock(
    lock_name: str,
    repo_root: Path | None = None,
    owner_component: str = "BackupDisasterRecovery",
    stale_after_seconds: int = 1800,
    force: bool = False,
) -> BackupLockRecord:
    if repo_root is None:
        repo_root = resolve_repo_root()
    existing = _read_lock(repo_root, lock_name)
    if existing is not None:
        if existing.status == LOCK_STATUS_ACQUIRED:
            if not _is_stale(existing) and not force:
                record = BackupLockRecord(
                    lock_record_id=new_id("lock"),
                    lock_name=lock_name,
                    lock_id=existing.lock_id,
                    acquired_at=existing.acquired_at,
                    stale_after_seconds=stale_after_seconds,
                    owner_component=owner_component,
                    status=LOCK_STATUS_BLOCKED,
                    errors=[f"Lock held by {existing.owner_component} since {existing.acquired_at}"],
                )
                _write_lock(repo_root, record)
                return record
    record = BackupLockRecord(
        lock_record_id=new_id("lock"),
        lock_name=lock_name,
        lock_id=new_id("lid"),
        acquired_at=utc_now_iso(),
        stale_after_seconds=stale_after_seconds,
        owner_component=owner_component,
        status=LOCK_STATUS_ACQUIRED,
    )
    _write_lock(repo_root, record)
    return record


def _orig_release_backup_lock(
    lock_name: str,
    repo_root: Path | None = None,
) -> BackupLockRecord:
    if repo_root is None:
        repo_root = resolve_repo_root()
    existing = _read_lock(repo_root, lock_name)
    if existing is None:
        return BackupLockRecord(
            lock_record_id=new_id("lock"),
            lock_name=lock_name,
            lock_id="",
            acquired_at=utc_now_iso(),
            stale_after_seconds=1800,
            owner_component="unknown",
            status=LOCK_STATUS_RELEASED,
            warnings=[f"Lock {lock_name} not found, recorded as released"],
        )
    record = BackupLockRecord(
        lock_record_id=new_id("lock"),
        lock_name=lock_name,
        lock_id=existing.lock_id,
        acquired_at=existing.acquired_at,
        released_at=utc_now_iso(),
        stale_after_seconds=existing.stale_after_seconds,
        owner_component=existing.owner_component,
        status=LOCK_STATUS_RELEASED,
    )
    _write_lock(repo_root, record)
    return record


def _orig_is_lock_active(
    lock_name: str,
    repo_root: Path | None = None,
) -> bool:
    if repo_root is None:
        repo_root = resolve_repo_root()
    existing = _read_lock(repo_root, lock_name)
    if existing is None:
        return False
    if existing.status != LOCK_STATUS_ACQUIRED:
        return False
    if _is_stale(existing):
        return False
    return True


@contextmanager
def backup_lock(
    lock_name: str,
    repo_root: Path | None = None,
    owner_component: str = "BackupDisasterRecovery",
    stale_after_seconds: int = 1800,
    force: bool = False,
) -> Generator[BackupLockRecord, Any, None]:
    record = _orig_acquire_backup_lock(lock_name, repo_root, owner_component, stale_after_seconds, force)
    try:
        yield record
    finally:
        if record.status == LOCK_STATUS_ACQUIRED:
            _orig_release_backup_lock(lock_name, repo_root)


def list_active_locks(
    repo_root: Path | None = None,
) -> list[BackupLockRecord]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    locks = locks_dir(repo_root)
    if not locks.exists():
        return []
    active: list[BackupLockRecord] = []
    for path in sorted(locks.glob("*.lock.json")):
        try:
            data = json.loads(path.read_text())
            record = BackupLockRecord(**data)
            if record.status == LOCK_STATUS_ACQUIRED and not _is_stale(record):
                active.append(record)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    return active


def clear_all_locks(
    repo_root: Path | None = None,
) -> list[str]:
    if repo_root is None:
        repo_root = resolve_repo_root()
    locks = locks_dir(repo_root)
    if not locks.exists():
        return []
    cleared = []
    for path in sorted(locks.glob("*.lock.json")):
        try:
            data = json.loads(path.read_text())
            record = BackupLockRecord(**data)
            record.status = LOCK_STATUS_RELEASED
            record.released_at = utc_now_iso()
            _write_lock(repo_root, record)
            cleared.append(record.lock_name)
        except (json.JSONDecodeError, TypeError, KeyError):
            path.unlink(missing_ok=True)
            cleared.append(path.stem.replace(".lock", ""))
    return cleared


def acquire_backup_lock(repo_root: Path, lock_name: str, stale_after_seconds: int = 1800) -> dict:
    """SPEC 10.4: Acquire a named backup lock. Returns dict with status."""
    record = _orig_acquire_backup_lock(lock_name, repo_root=repo_root, stale_after_seconds=stale_after_seconds)
    return to_dict(record)


def release_backup_lock(repo_root: Path, lock_id: str) -> dict:
    """SPEC 10.4: Release a backup lock by lock_id. Returns dict."""
    record = _orig_release_backup_lock(lock_id, repo_root=repo_root)
    return to_dict(record)


def is_lock_active(repo_root: Path, lock_name: str) -> bool:
    """SPEC 10.4: Check if a lock is active."""
    return _orig_is_lock_active(lock_name, repo_root=repo_root)
