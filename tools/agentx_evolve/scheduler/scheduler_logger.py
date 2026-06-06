from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_audit import SchedulerAuditLog

    warnings.warn(
        "scheduler_audit.SchedulerAuditLog is deprecated; use scheduler_logger.SchedulerLogger",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    SchedulerAuditLog = None  # type: ignore

__all__ = [
    "SchedulerLogger",
]


@dataclass
class SchedulerLogger:
    events: list[dict[str, Any]] = field(default_factory=list)

    def log_event(self, event: dict[str, Any]) -> None:
        self.events.append(event)

    def get_events(self, session_id: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e.get("session_id") == session_id]

    def get_recent(self, count: int = 10) -> list[dict[str, Any]]:
        return self.events[-count:]
