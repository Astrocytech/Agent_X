from __future__ import annotations

import json
import os
import time
from pathlib import Path

from agentx_evolve.patch_execution.patch_models import new_id, utc_now_iso

from agentx_evolve.patch_execution.initiator_patch_compat import InitiatorPatchCompat

LOCK_TYPE_SESSION = "IMPLEMENTATION_SESSION"
LOCK_TYPE_APPLY = "PATCH_APPLY"
LOCK_TYPE_ROLLBACK = "ROLLBACK"
VALID_LOCK_TYPES = {LOCK_TYPE_SESSION, LOCK_TYPE_APPLY, LOCK_TYPE_ROLLBACK}

_LOCK_FILENAMES = {
    LOCK_TYPE_SESSION: "implementation_session.lock",
    LOCK_TYPE_APPLY: "patch_apply.lock",
    LOCK_TYPE_ROLLBACK: "rollback.lock",
}

_LOCK_DIR = ".agentx-init/implementation"

_OWNER_COMPONENT = "GovernedPatchExecution"
_SCHEMA_VERSION = "1.0"
_SCHEMA_ID = "implementation_lock.schema.json"


def _build_lock_payload(
    lock_id: str,
    lock_type: str,
    session_id: str | None,
    repo_root: Path,
) -> dict:
    return {
        "schema_version": _SCHEMA_VERSION,
        "schema_id": _SCHEMA_ID,
        "lock_id": lock_id,
        "session_id": session_id,
        "lock_type": lock_type,
        "owner_component": _OWNER_COMPONENT,
        "created_at": utc_now_iso(),
        "pid": os.getpid(),
        "repo_root": str(repo_root),
        "status": "ACTIVE",
        "warnings": [],
        "errors": [],
    }


def _read_lock(lock_path: Path) -> dict | None:
    try:
        raw = lock_path.read_text(encoding="utf-8")
        return json.loads(raw)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _is_stale(lock: dict, stale_threshold_seconds: int) -> bool:
    created_at = lock.get("created_at")
    if not created_at:
        return True
    try:
        from datetime import datetime, timezone
        created = datetime.fromisoformat(created_at)
        now = datetime.now(timezone.utc)
        return (now - created).total_seconds() > stale_threshold_seconds
    except (ValueError, TypeError):
        return True


def get_lock_path(repo_root: Path, lock_type: str) -> Path:
    if lock_type not in VALID_LOCK_TYPES:
        raise ValueError(f"unknown lock_type: {lock_type!r}")
    filename = _LOCK_FILENAMES[lock_type]
    return repo_root / _LOCK_DIR / filename


def acquire_lock(
    repo_root: Path,
    lock_type: str,
    session_id: str | None = None,
    stale_threshold_seconds: int = 300,
    force: bool = False,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    if lock_type not in VALID_LOCK_TYPES:
        raise ValueError(f"invalid lock_type: {lock_type!r}")

    lock_path = get_lock_path(repo_root, lock_type)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    lock_payload = _build_lock_payload(
        lock_id=new_id("lock"),
        lock_type=lock_type,
        session_id=session_id,
        repo_root=repo_root,
    )
    payload_bytes = json.dumps(lock_payload, indent=2).encode("utf-8")

    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, payload_bytes)
        finally:
            os.close(fd)
        return {"status": "ACQUIRED", "lock": lock_payload}
    except FileExistsError:
        existing = _read_lock(lock_path)
        if existing is None:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                try:
                    os.write(fd, payload_bytes)
                finally:
                    os.close(fd)
                return {"status": "ACQUIRED", "lock": lock_payload}
            except FileExistsError:
                existing = _read_lock(lock_path)
                if existing is None:
                    return {"status": "BLOCKED", "reason": "unreadable lock file", "lock": {}}

        if _is_stale(existing, stale_threshold_seconds):
            if force:
                lock_path.write_text(json.dumps(lock_payload, indent=2), encoding="utf-8")
                return {"status": "ACQUIRED", "lock": lock_payload}
            return {
                "status": "STALE",
                "reason": f"lock is stale (older than {stale_threshold_seconds}s)",
                "lock": existing,
            }

        return {
            "status": "BLOCKED",
            "reason": f"lock held by session {existing.get('session_id')}",
            "lock": existing,
        }


def release_lock(
    repo_root: Path,
    lock_type: str,
    session_id: str | None = None,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    if lock_type not in VALID_LOCK_TYPES:
        raise ValueError(f"invalid lock_type: {lock_type!r}")

    lock_path = get_lock_path(repo_root, lock_type)

    if not lock_path.exists():
        return {"status": "NOT_FOUND", "lock_type": lock_type}

    existing = _read_lock(lock_path)
    if existing is not None and session_id is not None:
        existing_sid = existing.get("session_id")
        if existing_sid is not None and existing_sid != session_id:
            return {
                "status": "BLOCKED",
                "reason": "lock owned by different session",
            }

    try:
        lock_path.unlink()
    except OSError:
        pass

    return {"status": "RELEASED", "lock_type": lock_type}


def check_lock(
    repo_root: Path,
    lock_type: str,
    stale_threshold_seconds: int = 300,
    compat: InitiatorPatchCompat | None = None,
) -> dict:
    if lock_type not in VALID_LOCK_TYPES:
        raise ValueError(f"invalid lock_type: {lock_type!r}")

    lock_path = get_lock_path(repo_root, lock_type)

    if not lock_path.exists():
        return {"status": "FREE"}

    existing = _read_lock(lock_path)
    if existing is None:
        return {"status": "FREE"}

    if _is_stale(existing, stale_threshold_seconds):
        return {"status": "STALE", "lock": existing}

    return {"status": "ACTIVE", "lock": existing}
