from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    TaskRecord, SessionRecord,
    SCHEDULER_STATUS_QUEUED, SCHEDULER_STATUS_CLAIMED,
    SCHEDULER_STATUS_RUNNING, SCHEDULER_STATUS_COMPLETED,
    SCHEDULER_STATUS_FAILED, SCHEDULER_STATUS_CANCELLED,
    SCHEDULER_STATUS_BLOCKED, SCHEDULER_STATUS_PENDING_REVIEW,
    SCHEDULER_SESSION_STATUS_ACTIVE, SCHEDULER_SESSION_STATUS_HEARTBEAT,
    SCHEDULER_SESSION_STATUS_CLOSED,
    SCHEDULER_ACTIVE_SESSION_STATUSES,
    SCHEDULER_EVENT_QUEUED, SCHEDULER_EVENT_CLAIMED,
    SCHEDULER_EVENT_RUNNING, SCHEDULER_EVENT_COMPLETED,
    SCHEDULER_EVENT_FAILED, SCHEDULER_EVENT_CANCELLED,
    SCHEDULER_EVENT_BLOCKED, SCHEDULER_EVENT_DEPENDENCY_BLOCKED,
    SCHEDULER_EVENT_POLICY_DENIED, SCHEDULER_EVENT_DEAD_LETTER,
    SCHEDULER_EVENT_RETRY_SCHEDULED, SCHEDULER_EVENT_RECOVERED,
    CENTRAL_STATUS_PASS, CENTRAL_STATUS_FAIL, CENTRAL_STATUS_BLOCKED,
    CENTRAL_STATUS_NOT_CHECKED, CENTRAL_STATUS_NOT_RUN,
)
from .queue_store import QueueStore
from .session_store import SessionStore
from .lock_manager import LockManager
from .lease_manager import LeaseManager
from .scheduler_retry import RetryPolicy
from .crash_recovery import CrashRecovery
from .scheduler_policy import SchedulerPolicy
from .scheduler_engine import SchedulerEngine
from .scheduler_observability import SchedulerObservability
from .scheduler_evidence import SchedulerEvidenceWriter
from .scheduler_validation import (
    validate_task_record, validate_session_record,
    validate_scheduler_event, validate_scheduler_config,
)


class SchedulerDispatcher:
    def __init__(self, runtime_root: str | Path = ".agentx-init/scheduler"):
        self.runtime_root = Path(runtime_root)
        self.engine = SchedulerEngine(str(self.runtime_root))
        self.observability = SchedulerObservability(str(self.runtime_root / "events"))
        self.evidence = SchedulerEvidenceWriter(str(self.runtime_root))
        self._initialized = False

    def initialize(self) -> dict:
        if self._initialized:
            return {"status": "already_initialized"}
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        for subdir in ["queue", "sessions", "locks", "leases", "retries", "recovery", "audit", "events"]:
            (self.runtime_root / subdir).mkdir(parents=True, exist_ok=True)
        self._initialized = True
        return {"status": "initialized", "runtime_root": str(self.runtime_root)}

    def create_task(self, task_id: str, session_id: str, payload_ref: str = "",
                    priority: int = 50, dependency_ids: list[str] | None = None,
                    max_retries: int = 3) -> dict:
        if not self._initialized:
            self.initialize()
        policy = SchedulerPolicy()
        decision = policy.check_create_task("default", session_id)
        if decision.decision == "DENY":
            return {"status": "DENIED", "reason": decision.reason}
        if decision.decision == "BLOCKED":
            return {"status": "BLOCKED", "reason": decision.reason}
        record = TaskRecord(
            record_id=new_id("tr"),
            task_id=task_id,
            session_id=session_id,
            status=SCHEDULER_STATUS_QUEUED,
            priority=priority,
            payload_ref=payload_ref,
            dependency_ids=dependency_ids or [],
            max_retries=max_retries,
        )
        result = self.engine.queue_store.append_task(record)
        self.observability.record_event(
            event_type=SCHEDULER_EVENT_QUEUED,
            task_id=task_id,
            session_id=session_id,
        )
        return {"status": "QUEUED", "task_id": task_id, "record_id": record.record_id}

    def claim_next_task(self, session_id: str) -> dict:
        if not self._initialized:
            self.initialize()
        policy = SchedulerPolicy()
        session = self.engine.get_session(session_id)
        if session is None:
            return {"status": "SESSION_NOT_FOUND", "session_id": session_id}
        if session.status not in SCHEDULER_ACTIVE_SESSION_STATUSES:
            return {"status": "SESSION_NOT_ACTIVE", "session_id": session_id, "session_status": session.status}
        task = self.engine.claim_next(session_id)
        if task is None:
            return {"status": "NO_TASK_AVAILABLE"}
        decision = policy.check_claim_task("default", session_id, task["task_id"])
        if decision.decision == "DENY":
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_POLICY_DENIED,
                task_id=task["task_id"],
                session_id=session_id,
                details={"reason": decision.reason},
            )
            return {"status": "DENIED", "reason": decision.reason}
        if decision.decision == "BLOCKED":
            return {"status": "BLOCKED", "reason": decision.reason}
        self.observability.record_event(
            event_type=SCHEDULER_EVENT_CLAIMED,
            task_id=task["task_id"],
            session_id=session_id,
        )
        return {"status": "CLAIMED", "task_id": task["task_id"], "claim": task}

    def mark_running(self, task_id: str, session_id: str) -> dict:
        result = self.engine.progress_task(task_id, session_id, SCHEDULER_STATUS_RUNNING)
        if result.get("status") == "PROGRESSED":
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_RUNNING,
                task_id=task_id,
                session_id=session_id,
            )
        return result

    def complete_task(self, task_id: str, session_id: str) -> dict:
        result = self.engine.progress_task(task_id, session_id, SCHEDULER_STATUS_COMPLETED)
        if result.get("status") == "PROGRESSED":
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_COMPLETED,
                task_id=task_id,
                session_id=session_id,
            )
        return result

    def fail_task(self, task_id: str, session_id: str, error: str = "") -> dict:
        result = self.engine.progress_task(task_id, session_id, SCHEDULER_STATUS_FAILED)
        if result.get("status") == "PROGRESSED":
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_FAILED,
                task_id=task_id,
                session_id=session_id,
                details={"error": error},
            )
            task = self.engine.get_task(task_id)
            if task:
                retry = self.engine.retry_policy
                sched = retry.should_retry(task)
                if sched["should_retry"]:
                    nra = retry.compute_next_run_at(task.retry_count)
                    retry.record_retry(task, nra)
                    self.observability.record_event(
                        event_type=SCHEDULER_EVENT_RETRY_SCHEDULED,
                        task_id=task_id,
                        session_id=session_id,
                        details={"next_run_at": nra},
                    )
                else:
                    retry.send_to_dead_letter(task, sched["reason"])
                    self.observability.record_event(
                        event_type=SCHEDULER_EVENT_DEAD_LETTER,
                        task_id=task_id,
                        session_id=session_id,
                        details={"reason": sched["reason"]},
                    )
        return result

    def cancel_task(self, task_id: str, session_id: str) -> dict:
        result = self.engine.progress_task(task_id, session_id, SCHEDULER_STATUS_CANCELLED)
        if result.get("status") == "PROGRESSED":
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_CANCELLED,
                task_id=task_id,
                session_id=session_id,
            )
        return result

    def get_task(self, task_id: str) -> TaskRecord | None:
        return self.engine.get_task(task_id)

    def get_queue_state(self) -> dict:
        return self.engine.get_queue_state()

    def get_active_sessions(self) -> list[SessionRecord]:
        return self.engine.get_active_sessions()

    def run_recovery_pass(self) -> dict:
        result = self.engine.run_recovery_pass()
        if result.get("recovered_sessions") or result.get("expired_leases"):
            self.observability.record_event(
                event_type=SCHEDULER_EVENT_RECOVERED,
                details={"recovery_result": result},
            )
        return result

    def finalize_evidence(self, validated_commit: str = "") -> dict:
        return self.evidence.write_all(str(self.runtime_root), validated_commit)


def dispatch_task(dispatcher: SchedulerDispatcher, task_id: str, session_id: str,
                  payload_ref: str = "", priority: int = 50) -> dict:
    return dispatcher.create_task(task_id, session_id, payload_ref, priority)
