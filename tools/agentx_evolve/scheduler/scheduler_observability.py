import json
from pathlib import Path

from .scheduler_models import (
    utc_now_iso, new_id, to_dict,
    SchedulerEvent,
    SCHEDULER_EVENT_QUEUED, SCHEDULER_EVENT_CLAIMED,
    SCHEDULER_EVENT_RUNNING, SCHEDULER_EVENT_COMPLETED,
    SCHEDULER_EVENT_FAILED, SCHEDULER_EVENT_CANCELLED,
    SCHEDULER_EVENT_BLOCKED, SCHEDULER_EVENT_RECOVERED,
    SCHEDULER_EVENT_LOCK_ACQUIRED, SCHEDULER_EVENT_LOCK_RELEASED,
    SCHEDULER_EVENT_LOCK_STALE, SCHEDULER_EVENT_LEASE_ACQUIRED,
    SCHEDULER_EVENT_LEASE_RELEASED, SCHEDULER_EVENT_LEASE_EXPIRED,
    SCHEDULER_EVENT_HEARTBEAT, SCHEDULER_EVENT_SNAPSHOT,
    SCHEDULER_EVENT_CORRUPTION, SCHEDULER_EVENT_QUARANTINE,
    SCHEDULER_EVENT_POLICY_DENIED, SCHEDULER_EVENT_RETRY_SCHEDULED,
    SCHEDULER_EVENT_DEAD_LETTER, SCHEDULER_EVENT_DEPENDENCY_BLOCKED,
    CENTRAL_STATUS_PASS, CENTRAL_STATUS_FAIL,
)


EVENT_LOG_FILE = "event_log.jsonl"
SUMMARY_FILE = "scheduler_summary.json"
HEALTH_FILE = "scheduler_health.json"


class SchedulerObservability:
    def __init__(self, event_dir: str | Path):
        self.event_dir = Path(event_dir)
        self.event_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self.event_dir / EVENT_LOG_FILE

    def record_event(
        self,
        event_type: str,
        task_id: str | None = None,
        session_id: str | None = None,
        claim_id: str | None = None,
        lease_id: str | None = None,
        details: dict | None = None,
    ) -> dict:
        event = SchedulerEvent(
            event_id=new_id("evt"),
            event_type=event_type,
            task_id=task_id,
            session_id=session_id,
            claim_id=claim_id,
            lease_id=lease_id,
            details=details or {},
        )
        line = json.dumps(to_dict(event), sort_keys=True, default=str) + "\n"
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(line)
        return {"event_id": event.event_id, "event_type": event_type}

    def write_summary(self, queue_state: dict, active_sessions: int) -> dict:
        summary = {
            "schema_version": "1.0",
            "summary_id": new_id("sum"),
            "generated_at": utc_now_iso(),
            "queue_state": queue_state,
            "active_sessions": active_sessions,
        }
        path = self.event_dir / SUMMARY_FILE
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        tmp.replace(path)
        return {"path": str(path), "status": "summary_written"}

    def write_health(self, status: str = CENTRAL_STATUS_PASS, checks: dict | None = None) -> dict:
        health = {
            "schema_version": "1.0",
            "health_id": new_id("hlth"),
            "generated_at": utc_now_iso(),
            "status": status,
            "checks": checks or {},
        }
        path = self.event_dir / HEALTH_FILE
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(health, f, indent=2, default=str)
        tmp.replace(path)
        return {"path": str(path), "status": "health_written"}
