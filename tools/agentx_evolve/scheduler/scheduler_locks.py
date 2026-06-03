from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SchedulerEvent,
    SCHEDULER_EVENT_LOCK_ACQUIRED, SCHEDULER_EVENT_LOCK_RELEASED,
    SCHEDULER_EVENT_LOCK_STALE,
)
from .lock_manager import LockManager
from .scheduler_evidence import SchedulerEvidenceWriter


LOCK_DIR = ".agentx-init/scheduler/locks"


def _lock_manager(repo_root: str | Path) -> LockManager:
    return LockManager(Path(repo_root) / LOCK_DIR)


def _write_lock_event(
    event_type: str,
    lock_name: str,
    owner_id: str,
    repo_root: str | Path,
    details: dict | None = None,
) -> None:
    event = SchedulerEvent(
        event_id=new_id("evt"),
        event_type=event_type,
        details={"lock_name": lock_name, "owner_id": owner_id, **(details or {})},
    )
    evidence_dir = Path(repo_root) / ".agentx-init/scheduler"
    writer = SchedulerEvidenceWriter(evidence_dir)
    writer._write_json(evidence_dir / "lock_events.jsonl", to_dict(event))


def acquire_scheduler_lock(
    lock_name: str,
    owner_id: str,
    repo_root: str | Path,
) -> dict:
    mgr = _lock_manager(repo_root)
    result = mgr.acquire(lock_name, owner_id)
    _write_lock_event(
        SCHEDULER_EVENT_LOCK_ACQUIRED if result.get("status") == "LOCK_ACQUIRED" else "LOCK_DENIED",
        lock_name,
        owner_id,
        repo_root,
        details={"result_status": result.get("status")},
    )
    return result


def release_scheduler_lock(
    lock_name: str,
    owner_id: str,
    repo_root: str | Path,
) -> dict:
    mgr = _lock_manager(repo_root)
    result = mgr.release(lock_name, owner_id)
    _write_lock_event(
        SCHEDULER_EVENT_LOCK_RELEASED if "RELEASED" in result.get("status", "") else "LOCK_RELEASE_FAILED",
        lock_name,
        owner_id,
        repo_root,
        details={"result_status": result.get("status")},
    )
    return result


def is_locked(lock_name: str, repo_root: str | Path) -> bool:
    mgr = _lock_manager(repo_root)
    return mgr.is_locked(lock_name)


def recover_stale_locks(repo_root: str | Path) -> list[dict]:
    mgr = _lock_manager(repo_root)
    recovered = []
    lock_dir = Path(repo_root) / LOCK_DIR
    for lock_file in sorted(lock_dir.glob("*.lock")):
        if not lock_file.is_file():
            continue
        lock_data = mgr.get_lock_info(lock_file.stem)
        if lock_data is None:
            continue
        if mgr._is_stale(lock_data):
            recovery = mgr._recover_stale_lock(lock_file, lock_data, "recovery")
            recovered.append({
                "lock_name": lock_file.stem,
                "previous_owner": lock_data.get("owner_id", ""),
                "status": "recovered",
            })
            _write_lock_event(
                SCHEDULER_EVENT_LOCK_STALE,
                lock_file.stem,
                "recovery",
                repo_root,
                details={"previous_owner": lock_data.get("owner_id", "")},
            )
    return recovered
