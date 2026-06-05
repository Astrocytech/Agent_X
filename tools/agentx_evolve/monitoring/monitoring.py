from __future__ import annotations

import hashlib
import json
import os
import fcntl
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.model.model_models import new_id, to_dict

MN_SCHEMA_VERSION = "1.0"
MN_SCHEMA_ID = "monitoring_audit_event.schema.json"

MN_EVENT_AUDIT = "AUDIT"
MN_EVENT_ERROR = "ERROR"
MN_EVENT_WARN = "WARN"
MN_EVENT_INFO = "INFO"

ALL_EVENT_TYPES = [MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO]


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def append_jsonl(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(canonical_json(data) + "\n")
    return path


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


@dataclass
class AuditEventHash:
    event_hash: str = ""

    @classmethod
    def from_event(cls, event: AuditEvent) -> "AuditEventHash":
        return cls(event_hash=sha256_dict(event.to_dict()))


_MONITORING_DIR = Path(__file__).resolve().parent.parent / ".agentx-init" / "monitoring"


class AuditLog:
    def __init__(self, base_dir: Path | None = None):
        self._events: list[AuditEvent] = []
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

    def log_event(self, event_type: str, session_id: str,
                  component: str, message: str,
                  metadata: dict | None = None,
                  warnings: list[str] | None = None,
                  errors: list[str] | None = None) -> AuditEvent:
        event = AuditEvent(
            event_id=new_id("evt"),
            event_type=event_type,
            session_id=session_id,
            component=component,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
            warnings=warnings or [],
            errors=errors or [],
        )
        self._events.append(event)
        append_jsonl(self.audit_log_path, event.to_dict())
        return event

    def write_latest_event(self, event: AuditEvent) -> Path:
        return write_json_atomic(self.latest_event_path, event.to_dict())

    def load_events_from_disk(self) -> None:
        path = self.audit_log_path
        if path.exists():
            for line in path.read_text().strip().split("\n"):
                line = line.strip()
                if line:
                    data = json.loads(line)
                    self._events.append(AuditEvent(**data))

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
            "events": [
                {**e.to_dict(), "event_hash": sha256_dict(e.to_dict())}
                for e in events
            ],
            "event_count": len(events),
        }

    def last_failure(self, session_id: str) -> AuditEvent | None:
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

    def get_component_events(self, component: str) -> list[AuditEvent]:
        return [e for e in self._audit.list_all() if e.component == component]

    def get_recent_events(self, count: int) -> list[AuditEvent]:
        all_events = self._audit.list_all()
        return all_events[-count:] if count > 0 else []
