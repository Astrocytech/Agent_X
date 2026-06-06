from __future__ import annotations

import json
import os
import fcntl
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_events import (
    MonitoringEvent, EventHash, make_event, sha256_dict,
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
)
from agentx_evolve.monitoring.monitoring_utils import write_json_atomic, append_jsonl
from agentx_evolve.models.model_models import new_id


_MONITORING_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring"


class AuditLog:
    def __init__(self, base_dir: Path | None = None):
        self._events: list[MonitoringEvent] = []
        self._base_dir = Path(base_dir) if base_dir else _MONITORING_DIR
        self._lock_fd: int | None = None
        self.load_events_from_disk()

    @property
    def audit_log_path(self) -> Path:
        return self._base_dir / "audit_log.jsonl"

    @property
    def latest_event_path(self) -> Path:
        return self._base_dir / "latest_audit_event.json"

    def log(self, event_type: str, session_id: str,
            component: str, message: str,
            metadata: dict | None = None) -> MonitoringEvent:
        event = make_event(event_type, session_id, component, message, metadata)
        self._events.append(event)
        return event

    def log_event(self, event_type: str, session_id: str,
                  component: str, message: str,
                  metadata: dict | None = None,
                  warnings: list[str] | None = None,
                  errors: list[str] | None = None) -> MonitoringEvent:
        event = make_event(event_type, session_id, component, message,
                           metadata, warnings, errors)
        self._events.append(event)
        append_jsonl(self.audit_log_path, event.to_dict())
        return event

    def write_latest_event(self, event: MonitoringEvent) -> Path:
        return write_json_atomic(self.latest_event_path, event.to_dict())

    def load_events_from_disk(self) -> None:
        path = self.audit_log_path
        if path.exists():
            for line in path.read_text().strip().split("\n"):
                line = line.strip()
                if line:
                    data = json.loads(line)
                    self._events.append(MonitoringEvent(**data))

    def acquire_audit_lock(self) -> bool:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self._base_dir / "audit.lock"
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._lock_fd = fd
            return True
        except (IOError, OSError):
            return False

    def release_audit_lock(self) -> None:
        if self._lock_fd is not None:
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
                os.close(self._lock_fd)
            except (IOError, OSError):
                pass
            self._lock_fd = None

    def get_by_session(self, session_id: str) -> list[MonitoringEvent]:
        return [e for e in self._events if e.session_id == session_id]

    def get_by_type(self, event_type: str) -> list[MonitoringEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def list_all(self) -> list[MonitoringEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


class SessionInspector:
    def __init__(self, audit_log: AuditLog | None = None):
        self._audit = audit_log or AuditLog()

    @property
    def audit(self) -> AuditLog:
        return self._audit

    def inspect_session(self, session_id: str) -> dict:
        events = self._audit.get_by_session(session_id)
        return {
            "session_id": session_id,
            "events": [
                {**e.to_dict(), "event_hash": sha256_dict(e.to_dict())}
                for e in events
            ],
            "event_count": len(events),
        }

    def last_failure(self, session_id: str) -> MonitoringEvent | None:
        events = self._audit.get_by_session(session_id)
        failures = [e for e in events if "fail" in e.event_type.lower()]
        if failures:
            return failures[-1]
        return None

    def get_session_summary(self, session_id: str) -> dict:
        events = self._audit.get_by_session(session_id)
        type_counts: dict[str, int] = {}
        for e in events:
            type_counts[e.event_type] = type_counts.get(e.event_type, 0) + 1
        error_count = sum(1 for e in events if e.event_type == MN_EVENT_ERROR)
        warn_count = sum(1 for e in events if e.event_type == MN_EVENT_WARN)
        return {
            "session_id": session_id,
            "total_events": len(events),
            "event_type_counts": type_counts,
            "error_count": error_count,
            "warning_count": warn_count,
        }

    def get_component_events(self, component: str) -> list[MonitoringEvent]:
        return [e for e in self._audit.list_all() if e.component == component]

    def get_recent_events(self, count: int) -> list[MonitoringEvent]:
        all_events = self._audit.list_all()
        return all_events[-count:] if count > 0 else []
