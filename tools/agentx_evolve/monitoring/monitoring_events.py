from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from agentx_evolve.models.model_models import new_id, to_dict

MN_SCHEMA_VERSION = "1.0"
MN_SCHEMA_ID = "monitoring_audit_event.schema.json"

MN_EVENT_AUDIT = "AUDIT"
MN_EVENT_ERROR = "ERROR"
MN_EVENT_WARN = "WARN"
MN_EVENT_INFO = "INFO"
MN_EVENT_METRIC = "METRIC"
MN_EVENT_HEALTH = "HEALTH"
MN_EVENT_ALERT = "ALERT"
MN_EVENT_TRACE = "TRACE"
MN_EVENT_STATUS = "STATUS"

ALL_EVENT_TYPES = [
    MN_EVENT_AUDIT, MN_EVENT_ERROR, MN_EVENT_WARN, MN_EVENT_INFO,
    MN_EVENT_METRIC, MN_EVENT_HEALTH, MN_EVENT_ALERT, MN_EVENT_TRACE,
    MN_EVENT_STATUS,
]

ALERT_SEVERITY_CRITICAL = "CRITICAL"
ALERT_SEVERITY_HIGH = "HIGH"
ALERT_SEVERITY_MEDIUM = "MEDIUM"
ALERT_SEVERITY_LOW = "LOW"

HEALTH_STATUS_HEALTHY = "HEALTHY"
HEALTH_STATUS_DEGRADED = "DEGRADED"
HEALTH_STATUS_UNHEALTHY = "UNHEALTHY"
HEALTH_STATUS_UNKNOWN = "UNKNOWN"

STATUS_RUNNING = "RUNNING"
STATUS_DEGRADED = "DEGRADED"
STATUS_STOPPED = "STOPPED"
STATUS_STARTING = "STARTING"

TRACE_STATUS_OK = "OK"
TRACE_STATUS_ERROR = "ERROR"
TRACE_STATUS_TIMEOUT = "TIMEOUT"


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_dict(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MonitoringEvent:
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
class EventHash:
    event_hash: str = ""

    @classmethod
    def from_event(cls, event: MonitoringEvent) -> EventHash:
        return cls(event_hash=sha256_dict(event.to_dict()))


def make_event(
    event_type: str,
    session_id: str,
    component: str,
    message: str,
    metadata: dict | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
) -> MonitoringEvent:
    return MonitoringEvent(
        event_id=new_id("evt"),
        event_type=event_type,
        session_id=session_id,
        component=component,
        message=message,
        timestamp=utc_now_iso(),
        metadata=metadata or {},
        warnings=warnings or [],
        errors=errors or [],
    )


@dataclass
class MetricRecord:
    metric_id: str = ""
    name: str = ""
    value: float = 0.0
    unit: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    component: str = ""

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HealthCheck:
    check_id: str = ""
    name: str = ""
    component: str = ""
    status: str = HEALTH_STATUS_UNKNOWN
    detail: str = ""
    timestamp: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class HealthReport:
    report_id: str = ""
    overall_status: str = HEALTH_STATUS_UNKNOWN
    checks: list[HealthCheck] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "overall_status": self.overall_status,
            "checks": [c.to_dict() for c in self.checks],
            "timestamp": self.timestamp,
        }


@dataclass
class AlertRecord:
    alert_id: str = ""
    rule_name: str = ""
    severity: str = ALERT_SEVERITY_MEDIUM
    message: str = ""
    component: str = ""
    timestamp: str = ""
    metadata: dict | None = None
    acknowledged: bool = False

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class TraceSpan:
    span_id: str = ""
    parent_span_id: str = ""
    trace_id: str = ""
    operation: str = ""
    component: str = ""
    status: str = TRACE_STATUS_OK
    started_at: str = ""
    ended_at: str = ""
    duration_ms: float = 0.0
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class RuntimeStatus:
    component: str = ""
    status: str = STATUS_STARTING
    version: str = ""
    uptime_seconds: float = 0.0
    active_sessions: int = 0
    last_event_timestamp: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return to_dict(self)
