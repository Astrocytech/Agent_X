from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from agentx_evolve.models.model_models import new_id, to_dict

MN_SCHEMA_VERSION = "1.0"
MN_SCHEMA_ID = "monitoring_models.schema.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MetricPoint:
    point_id: str = ""
    name: str = ""
    value: float = 0.0
    unit: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    component: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class EventRecord:
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
class HealthStatus:
    check_id: str = ""
    name: str = ""
    component: str = ""
    status: str = "UNKNOWN"
    detail: str = ""
    timestamp: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class AlertRule:
    name: str = ""
    severity: str = "MEDIUM"
    component: str = ""
    enabled: bool = True
    condition_description: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class TraceSpan:
    span_id: str = ""
    parent_span_id: str = ""
    trace_id: str = ""
    operation: str = ""
    component: str = ""
    status: str = "OK"
    started_at: str = ""
    ended_at: str = ""
    duration_ms: float = 0.0
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return to_dict(self)
