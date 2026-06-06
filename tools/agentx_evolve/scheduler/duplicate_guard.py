from __future__ import annotations
import hashlib
import warnings
from typing import Any

try:
    from agentx_evolve.scheduler.scheduler_locks import (
        acquire_scheduler_lock,
        release_scheduler_lock,
    )

    warnings.warn(
        "scheduler_locks provides lock primitives; duplicate_guard.DuplicateGuard is the dedicated guard",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    pass

__all__ = [
    "DuplicateGuard",
]

_SEEN: set[tuple[str, str]] = set()


class DuplicateGuard:
    def __init__(self) -> None:
        self._seen: dict[str, set[str]] = {}

    def is_duplicate(self, task_id: str, task_hash: str) -> bool:
        seen_hashes = self._seen.get(task_id)
        if seen_hashes is None:
            return False
        return task_hash in seen_hashes

    def mark_seen(self, task_id: str, task_hash: str) -> None:
        if task_id not in self._seen:
            self._seen[task_id] = set()
        self._seen[task_id].add(task_hash)

    @classmethod
    def global_is_duplicate(cls, task_id: str, task_hash: str) -> bool:
        key = (task_id, task_hash)
        return key in _SEEN

    @classmethod
    def global_mark_seen(cls, task_id: str, task_hash: str) -> None:
        _SEEN.add((task_id, task_hash))
