from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_engine import run_scheduler_cycle

    warnings.warn(
        "scheduler_engine.run_scheduler_cycle is deprecated; use scheduler_runner.SchedulerRunner",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    run_scheduler_cycle = None  # type: ignore

__all__ = [
    "SchedulerRunner",
]


@dataclass
class SchedulerRunner:
    _running: bool = False
    cycles: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_running(self) -> bool:
        return self._running

    def run_cycle(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": "cycle_complete",
            "tasks_processed": 0,
        }
        self.cycles.append(result)
        return result

    def stop(self) -> None:
        self._running = False
