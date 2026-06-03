from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

QS_PENDING = "PENDING"
QS_RUNNING = "RUNNING"
QS_PAUSED = "PAUSED"
QS_COMPLETED = "COMPLETED"
QS_CANCELLED = "CANCELLED"
QS_FAILED = "FAILED"
ALL_QUEUE_STATUSES = [QS_PENDING, QS_RUNNING, QS_PAUSED, QS_COMPLETED, QS_CANCELLED, QS_FAILED]


@dataclass
class TaskQueueItem:
    item_id: str = ""
    session_id: str = ""
    description: str = ""
    status: str = QS_PENDING
    priority: int = 0
    created_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class TaskQueue:
    def __init__(self):
        self._items: dict[str, TaskQueueItem] = {}

    def enqueue(self, session_id: str, description: str,
                priority: int = 0) -> TaskQueueItem:
        item = TaskQueueItem(
            item_id=new_id("tq"),
            session_id=session_id,
            description=description,
            priority=priority,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._items[item.item_id] = item
        return item

    def get(self, item_id: str) -> TaskQueueItem | None:
        return self._items.get(item_id)

    def list_all(self, status: str | None = None) -> list[TaskQueueItem]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return sorted(items, key=lambda x: (-x.priority, x.created_at or ""))

    def update_status(self, item_id: str, status: str) -> bool:
        item = self._items.get(item_id)
        if item is None:
            return False
        item.status = status
        return True

    def remove(self, item_id: str) -> bool:
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False

    def clear_completed(self) -> int:
        before = len(self._items)
        self._items = {k: v for k, v in self._items.items()
                       if v.status not in (QS_COMPLETED, QS_CANCELLED, QS_FAILED)}
        return before - len(self._items)
