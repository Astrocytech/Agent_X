from __future__ import annotations

from typing import Any

__all__ = [
    "TaskLoader",
]


class TaskLoader:
    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}

    def load(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    def list_pending(self) -> list[dict[str, Any]]:
        return [t for t in self._tasks.values() if t.get("status") == "PENDING"]
