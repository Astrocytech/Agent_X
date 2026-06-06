from __future__ import annotations
import warnings
from dataclasses import dataclass, field
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_models import DeadLetterQueue as _DeadLetterQueue

    warnings.warn(
        "scheduler_models.DeadLetterQueue is deprecated; use dead_letter_queue.DeadLetterQueue",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    _DeadLetterQueue = None  # type: ignore

__all__ = [
    "DeadLetterQueue",
]


@dataclass
class DeadLetterQueue:
    items: list[dict[str, Any]] = field(default_factory=list)

    def enqueue(self, item: dict[str, Any], reason: str = "") -> None:
        record = dict(item)
        record["_reason"] = reason
        self.items.append(record)

    def dequeue(self) -> dict[str, Any] | None:
        if not self.items:
            return None
        return self.items.pop(0)

    def list_all(self) -> list[dict[str, Any]]:
        return list(self.items)
