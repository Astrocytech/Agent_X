from __future__ import annotations
from pathlib import Path
from typing import Any
import hashlib
import json
import os
import time
from agentx_evolve.learning.outcome_models import (
    OutcomeEvent, LearningLockRecord,
    utc_now_iso, new_id, stable_hash_dict, to_dict,
)

_LOCK_TIMEOUT_SECONDS = 30
_LOCK_DIR = ".agentx-init/learning/locks"


def compute_review_key(event: OutcomeEvent) -> str:
    data = {
        "event_id": event.event_id,
        "run_id": event.run_id or "",
        "task_id": event.task_id or "",
        "commit_before": event.commit_before or "",
        "commit_after": event.commit_after or "",
        "outcome_status": event.outcome_status,
        "evidence_refs": sorted(event.evidence_refs),
    }
    return stable_hash_dict(data)


def _lock_path(review_key: str, repo_root: Path | str) -> Path:
    return Path(repo_root) / _LOCK_DIR / f"{review_key}.lock"


def acquire_learning_lock(review_key: str, context: dict) -> LearningLockRecord:
    repo_root = Path(context.get("repo_root", "."))
    lock_path = _lock_path(review_key, repo_root)
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    timeout = context.get("lock_timeout_seconds", _LOCK_TIMEOUT_SECONDS)
    deadline = time.monotonic() + timeout
    created_at = utc_now_iso()
    lock_id = new_id("lk")

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            lock_data = {
                "lock_id": lock_id,
                "created_at": created_at,
                "review_key": review_key,
                "owner_session_id": context.get("session_id"),
                "expires_at": utc_now_iso(),
            }
            lock_path.write_text(json.dumps(lock_data, separators=(",", ":")), encoding="utf-8")
            return LearningLockRecord(
                lock_id=lock_id,
                created_at=created_at,
                review_key=review_key,
                lock_path=str(lock_path),
                owner_session_id=context.get("session_id"),
                expires_at=created_at,
                status="ACQUIRED",
                evidence_refs=[str(lock_path)],
            )
        except FileExistsError:
            if time.monotonic() >= deadline:
                lock_data = record_stale_lock(lock_path, context)
                return lock_data
            time.sleep(0.1)


def release_learning_lock(lock: LearningLockRecord, context: dict) -> LearningLockRecord:
    lock_path = Path(lock.lock_path)
    try:
        lock_path.unlink(missing_ok=True)
        lock.status = "RELEASED"
    except Exception:
        lock.status = "RELEASE_FAILED"
        lock.errors.append(f"Failed to release lock: {lock_path}")
    return lock


def record_stale_lock(lock_path: Path, context: dict) -> LearningLockRecord:
    lock_id = new_id("lk")
    created_at = utc_now_iso()
    review_key = lock_path.stem
    try:
        existing = json.loads(lock_path.read_text(encoding="utf-8"))
        owner = existing.get("owner_session_id")
    except Exception:
        owner = None
    record = LearningLockRecord(
        lock_id=lock_id,
        created_at=created_at,
        review_key=review_key,
        lock_path=str(lock_path),
        owner_session_id=owner,
        expires_at=created_at,
        status="STALE_LOCK",
        evidence_refs=[str(lock_path)],
        warnings=[f"Stale lock detected: {lock_path}"],
    )
    return record
