from __future__ import annotations

import json as _json
import hashlib
from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def _locks_dir(repo_root: Path) -> Path:
    return repo_root / RUNTIME_ARTIFACT_ROOT / "locks"


def acquire_run_lock(
    run_id: str,
    repo_root: Path,
    owner: str = "orchestrator",
) -> bool:
    lock_dir = _locks_dir(repo_root)
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{run_id}.lock"
    if lock_path.exists():
        existing = _json.loads(lock_path.read_text())
        if existing.get("status") == "ACTIVE":
            return False
    lock_data = {
        "run_id": run_id,
        "owner": owner,
        "status": "ACTIVE",
        "acquired_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
    }
    lock_path.write_text(_json.dumps(lock_data, indent=2, sort_keys=True))
    return True


def release_run_lock(run_id: str, repo_root: Path) -> bool:
    lock_path = _locks_dir(repo_root) / f"{run_id}.lock"
    if not lock_path.exists():
        return False
    lock_data = _json.loads(lock_path.read_text())
    lock_data["status"] = "RELEASED"
    lock_data["released_at"] = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    ).isoformat()
    lock_path.write_text(_json.dumps(lock_data, indent=2, sort_keys=True))
    return True


def check_run_lock(run_id: str, repo_root: Path) -> bool:
    lock_path = _locks_dir(repo_root) / f"{run_id}.lock"
    if not lock_path.exists():
        return False
    lock_data = _json.loads(lock_path.read_text())
    return lock_data.get("status") == "ACTIVE"


def compute_idempotency_key(task_data: dict) -> str:
    canonical = {k: v for k, v in sorted(task_data.items()) if k not in ("idempotency_key",)}
    raw = _json.dumps(canonical, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def find_existing_run(idempotency_key: str, repo_root: Path) -> str | None:
    runs_dir = repo_root / RUNTIME_ARTIFACT_ROOT / "runs"
    if not runs_dir.exists():
        return None
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        session_path = run_dir / "orchestration_session.json"
        if not session_path.exists():
            continue
        session_data = _json.loads(session_path.read_text())
        if session_data.get("idempotency_key") == idempotency_key:
            return session_data.get("run_id")
    return None
