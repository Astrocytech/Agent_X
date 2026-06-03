from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict


@dataclass
class AuditEvent:
    event_id: str = ""
    event_type: str = ""
    session_id: str = ""
    component: str = ""
    message: str = ""
    timestamp: str = ""
    metadata: dict | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class AuditLog:
    def __init__(self):
        self._events: list[AuditEvent] = []

    def log(self, event_type: str, session_id: str,
            component: str, message: str,
            metadata: dict | None = None) -> AuditEvent:
        event = AuditEvent(
            event_id=new_id("evt"),
            event_type=event_type,
            session_id=session_id,
            component=component,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def get_by_session(self, session_id: str) -> list[AuditEvent]:
        return [e for e in self._events if e.session_id == session_id]

    def get_by_type(self, event_type: str) -> list[AuditEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def list_all(self) -> list[AuditEvent]:
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
            "events": [e.to_dict() for e in events],
            "event_count": len(events),
        }

    def last_failure(self, session_id: str) -> AuditEvent | None:
        events = self._audit.get_by_session(session_id)
        failures = [e for e in events if "fail" in e.event_type.lower()]
        if failures:
            return failures[-1]
        return None
