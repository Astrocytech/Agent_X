from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "MonitoringReport",
    "ReportBuilder",
]


@dataclass
class MonitoringReport:
    report_id: str = ""
    created_at: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class ReportBuilder:
    _metrics: dict[str, float]
    _events: list[dict[str, Any]]
    _report_id: str
    _warnings: list[str]
    _errors: list[str]

    def __init__(self, report_id: str = "") -> None:
        self._report_id = report_id
        self._metrics = {}
        self._events = []
        self._warnings = []
        self._errors = []

    def add_metric(self, name: str, value: float) -> ReportBuilder:
        self._metrics[name] = value
        return self

    def add_event(self, event: dict[str, Any]) -> ReportBuilder:
        self._events.append(event)
        return self

    def build(self) -> MonitoringReport:
        return MonitoringReport(
            report_id=self._report_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            metrics=dict(self._metrics),
            events=list(self._events),
            warnings=list(self._warnings),
            errors=list(self._errors),
        )
