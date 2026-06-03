from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    TaskRecord, SchedulerEvent,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_RUNNING,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_EVENT_RUNNING, SCHEDULER_EVENT_RECOVERED,
)
from .task_queue import _queue_store, claim_next_task, get_queue_state
from .session_store import SessionStore
from .lease_manager import LeaseManager
from .crash_recovery import CrashRecovery
from .scheduler_evidence import SchedulerEvidenceWriter


SCHEDULER_ROOT = ".agentx-init/scheduler"
RUNNER_LOCK_FILE = "runner.lock"


def _scheduler_root(repo_root: str | Path) -> Path:
    return Path(repo_root) / SCHEDULER_ROOT


def _evidence_writer(repo_root: str | Path) -> SchedulerEvidenceWriter:
    return SchedulerEvidenceWriter(_scheduler_root(repo_root))


def _write_event(event: SchedulerEvent, repo_root: str | Path) -> None:
    writer = _evidence_writer(repo_root)
    writer._write_json(
        _scheduler_root(repo_root) / "runner_events.jsonl",
        to_dict(event),
    )


def run_next_task(session_id: str, repo_root: str | Path) -> dict:
    root = _scheduler_root(repo_root)
    claim = claim_next_task(session_id, repo_root)
    if not claim.task_id:
        return {"status": "no_task_available", "session_id": session_id}

    event = SchedulerEvent(
        event_id=new_id("evt"),
        event_type=SCHEDULER_EVENT_RUNNING,
        task_id=claim.task_id,
        session_id=session_id,
        claim_id=claim.claim_id,
        lease_id=claim.lease_id,
        details={"action": "run_next_task"},
    )
    _write_event(event, repo_root)

    return {
        "status": "task_claimed",
        "task_id": claim.task_id,
        "claim_id": claim.claim_id,
        "lease_id": claim.lease_id,
        "session_id": session_id,
    }


def run_scheduler_tick(repo_root: str | Path) -> dict:
    root = _scheduler_root(repo_root)
    tick_id = new_id("tick")
    results: dict[str, any] = {"tick_id": tick_id, "actions": []}

    recovery_dir = root / "recovery"
    recovery = CrashRecovery(recovery_dir)

    session_dir = root / "sessions"
    session_store = SessionStore(session_dir)
    active_sessions = session_store.get_active_sessions()
    stale = recovery.recover_stale_sessions(active_sessions)
    if stale:
        for s in stale:
            results["actions"].append({"type": "stale_session_recovered", "session_id": s.get("session_id")})

    lease_dir = root / "leases"
    lease_mgr = LeaseManager(lease_dir)
    expired = lease_mgr.expire_stale_leases()
    if expired:
        recovered = recovery.recover_expired_leases(expired)
        for r in recovered:
            results["actions"].append({"type": "expired_lease_recovered", "lease_id": r.get("lease_id")})

    lock_dir = root / "locks"
    stale_locks = recovery.recover_stale_locks(lock_dir)
    if stale_locks:
        for sl in stale_locks:
            results["actions"].append({"type": "stale_lock_recovered", "lock_name": sl.get("lock_name")})

    store = _queue_store(repo_root)
    tasks, quarantined = store.replay_tasks()
    effective = {}
    for t in sorted(tasks, key=lambda x: (x.append_sequence, x.updated_at or "", x.record_id)):
        effective[t.task_id] = t

    retry_dir = root / "retries"
    from .scheduler_retry import RetryPolicy
    rp = RetryPolicy(retry_dir)
    retryable = rp.get_retryable_tasks(list(effective.values()))
    for t in retryable:
        now = utc_now_iso()
        next_run_at = rp.compute_next_run_at(t.retry_count)
        updated = TaskRecord(
            record_id=new_id("rec"),
            task_id=t.task_id,
            session_id=t.session_id,
            status=SCHEDULER_STATUS_QUEUED,
            priority=t.priority,
            payload_ref=t.payload_ref,
            dependency_ids=t.dependency_ids,
            retry_count=t.retry_count + 1,
            max_retries=t.max_retries,
            next_run_at=next_run_at,
            previous_record_hash=t.task_record_hash,
            append_sequence=t.append_sequence + 1,
            revision=t.revision + 1,
            created_at=t.created_at,
            updated_at=now,
        )
        store.append_task(updated)
        rp.record_retry(t, next_run_at)
        results["actions"].append({"type": "retry_scheduled", "task_id": t.task_id, "next_run_at": next_run_at})

    state = get_queue_state(repo_root)
    results["queue_state"] = {
        "total_tasks": state.total_tasks,
        "by_status": state.by_status,
    }

    return results


def get_queue_summary(repo_root: str | Path) -> dict:
    state = get_queue_state(repo_root)
    store = _queue_store(repo_root)
    tasks, quarantined = store.replay_tasks()
    return {
        "total_tasks": state.total_tasks,
        "by_status": state.by_status,
        "quarantined_count": len(quarantined),
        "snapshot_at": state.snapshot_at,
    }


def is_scheduler_running(repo_root: str | Path) -> bool:
    lock_path = _scheduler_root(repo_root) / RUNNER_LOCK_FILE
    if not lock_path.exists():
        return False
    try:
        import json
        with open(lock_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        from datetime import datetime, timezone
        acquired = datetime.fromisoformat(data.get("acquired_at", "").replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        elapsed = (now - acquired).total_seconds()
        return elapsed < 300
    except (ValueError, TypeError, OSError):
        return False
