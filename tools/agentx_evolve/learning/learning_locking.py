from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "LearningLock",
]

try:
    from agentx_evolve.learning.learning_lock import (
        acquire_learning_lock,
        release_learning_lock,
    )
    _HAS_LEGACY = True
except ImportError:
    _HAS_LEGACY = False


@dataclass
class LearningLock:
    lock_id: str = ""
    resource_key: str = ""
    acquired: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def acquire(self, context: dict[str, Any] | None = None) -> bool:
        if _HAS_LEGACY:
            warnings.warn(
                "LearningLock.acquire() delegates to deprecated learning_lock.acquire_learning_lock(). "
                "Use learning_locking directly in new code.",
                DeprecationWarning,
                stacklevel=2,
            )
            record = acquire_learning_lock(self.resource_key, context or {})
            self.acquired = record.status == "ACQUIRED"
            self.lock_id = record.lock_id
            return self.acquired
        self.acquired = True
        return True

    def release(self, context: dict[str, Any] | None = None) -> bool:
        if _HAS_LEGACY and self.lock_id:
            warnings.warn(
                "LearningLock.release() delegates to deprecated learning_lock.release_learning_lock(). "
                "Use learning_locking directly in new code.",
                DeprecationWarning,
                stacklevel=2,
            )
            from agentx_evolve.learning.learning_lock import release_learning_lock
            from agentx_evolve.learning.outcome_models import LearningLockRecord

            record = LearningLockRecord(lock_id=self.lock_id, lock_path="")
            release_learning_lock(record, context or {})
            self.acquired = False
            return True
        self.acquired = False
        return True
