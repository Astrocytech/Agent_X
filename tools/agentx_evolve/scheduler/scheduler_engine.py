from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    TaskRecord, SessionRecord, QueueState,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED,
    SCHEDULER_ACTIVE_SESSION_STATUSES,
    SCHEDULER_VALID_TRANSITIONS,
    compute_task_record_hash, compute_session_record_hash,
    TASK_PRIORITY_LOW, TASK_PRIORITY_MEDIUM, TASK_PRIORITY_HIGH,
    TASK_PRIORITY_CRITICAL,
)
from .queue_store import QueueStore
from .session_store import SessionStore
from .lock_manager import LockManager
from .lease_manager import LeaseManager
from .scheduler_retry import RetryPolicy
from .crash_recovery import CrashRecovery
from .scheduler_policy import SchedulerPolicy


class SchedulerEngine:
    def __init__(self, runtime_root: str | Path):
        self.runtime_root = Path(runtime_root)
        self.queue_store = QueueStore(str(self.runtime_root / "queue"))
        self.session_store = SessionStore(str(self.runtime_root / "sessions"))
        self.lock_manager = LockManager(str(self.runtime_root / "locks"))
        self.lease_manager = LeaseManager(str(self.runtime_root / "leases"))
        self.retry_policy = RetryPolicy(str(self.runtime_root / "retries"))
        self.crash_recovery = CrashRecovery(str(self.runtime_root / "recovery"))
        self.scheduler_policy = SchedulerPolicy()

    def create_session(self, session_id: str, role: str = "default") -> SessionRecord:
        now = utc_now_iso()
        session = SessionRecord(
            record_id=new_id("srec"),
            session_id=session_id,
            role=role,
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )
        self.session_store.append_session(session)
        return session

    def get_session(self, session_id: str) -> SessionRecord | None:
        sessions = self.session_store.get_effective_sessions()
        return sessions.get(session_id)

    def get_active_sessions(self) -> list[SessionRecord]:
        return self.session_store.get_active_sessions()

    def close_session(self, session_id: str) -> dict:
        session = self.session_store.close_session(session_id)
        if session:
            return {"status": "SESSION_CLOSED", "session_id": session_id}
        return {"status": "SESSION_NOT_FOUND", "session_id": session_id}

    def heartbeat_session(self, session_id: str) -> dict:
        session = self.session_store.heartbeat_session(session_id)
        if session:
            return {"status": "HEARTBEAT_RECORDED", "session_id": session_id}
        return {"status": "SESSION_NOT_FOUND", "session_id": session_id}

    def get_task(self, task_id: str) -> TaskRecord | None:
        tasks, _ = self.queue_store.replay_tasks()
        effective = self.queue_store._effective_tasks(tasks)
        return effective.get(task_id)

    def get_queue_state(self) -> dict:
        state, quarantined = self.queue_store.build_snapshot()
        return {
            "total_tasks": state.total_tasks,
            "by_status": state.by_status,
            "queue_hash": state.queue_hash,
            "snapshot_at": state.snapshot_at,
            "quarantined_count": len(quarantined),
        }

    def claim_next(self, session_id: str) -> dict | None:
        tasks, _ = self.queue_store.replay_tasks()
        effective = self.queue_store._effective_tasks(tasks)
        claimable = [
            t for t in effective.values()
            if t.status == SCHEDULER_STATUS_QUEUED
            and self._dependencies_satisfied(t, effective)
            and self._is_eligible_for_claim(t)
        ]
        if not claimable:
            return None
        claimable.sort(key=lambda t: (-t.priority, t.created_at or ""))
        candidate = claimable[0]
        lease_result = self.lease_manager.create_lease(candidate.task_id, session_id)
        if lease_result.get("status") != "LEASE_ACQUIRED":
            return None
        updated = self._update_task_status(candidate, SCHEDULER_STATUS_CLAIMED)
        self.queue_store.append_task(updated)
        result = to_dict(updated)
        result["lease_id"] = lease_result.get("lease_id", "")
        result["claim_id"] = lease_result.get("claim_id", "")
        return result

    def progress_task(self, task_id: str, session_id: str, new_status: str) -> dict:
        task = self.get_task(task_id)
        if task is None:
            return {"status": "TASK_NOT_FOUND", "task_id": task_id}
        if not SchedulerPolicy.validate_transition(task.status, new_status):
            return {
                "status": "INVALID_TRANSITION",
                "task_id": task_id,
                "current_status": task.status,
                "requested_status": new_status,
            }
        updated = self._update_task_status(task, new_status)
        self.queue_store.append_task(updated)
        return {"status": "PROGRESSED", "task_id": task_id, "new_status": new_status}

    def run_recovery_pass(self) -> dict:
        sessions = self.session_store.replay_sessions()
        effective_sessions = self.session_store.get_effective_sessions()
        recovered_sessions = self.crash_recovery.recover_stale_sessions(
            [s for s in effective_sessions.values() if s.status in SCHEDULER_ACTIVE_SESSION_STATUSES]
        )
        for r in recovered_sessions:
            self.session_store.mark_stale(r["session_id"])
        expired = self.lease_manager.expire_stale_leases()
        recovered_leases = self.crash_recovery.recover_expired_leases(expired)
        recovered_locks = self.crash_recovery.recover_stale_locks(Path(str(self.runtime_root)) / "locks")
        return {
            "recovered_sessions": len(recovered_sessions),
            "expired_leases": len(expired),
            "recovered_leases": len(recovered_leases),
            "recovered_locks": len(recovered_locks),
        }

    def _update_task_status(self, task: TaskRecord, new_status: str) -> TaskRecord:
        now = utc_now_iso()
        return TaskRecord(
            record_id=new_id("tr"),
            task_id=task.task_id,
            session_id=task.session_id,
            status=new_status,
            priority=task.priority,
            payload_ref=task.payload_ref,
            dependency_ids=task.dependency_ids,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            next_run_at=task.next_run_at,
            previous_record_hash=task.task_record_hash,
            append_sequence=task.append_sequence + 1,
            revision=task.revision + 1,
            created_at=task.created_at,
            updated_at=now,
        )

    def _dependencies_satisfied(self, task: TaskRecord, effective: dict[str, TaskRecord]) -> bool:
        if not task.dependency_ids:
            return True
        for dep_id in task.dependency_ids:
            dep_task = effective.get(dep_id)
            if dep_task is None:
                return False
            if dep_task.status not in (SCHEDULER_STATUS_COMPLETED, SCHEDULER_STATUS_CANCELLED):
                return False
        return True

    def _is_eligible_for_claim(self, task: TaskRecord) -> bool:
        if task.next_run_at:
            from datetime import datetime, timezone
            try:
                nra = datetime.fromisoformat(task.next_run_at.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                if now < nra:
                    return False
            except (ValueError, TypeError):
                return False
        return True
