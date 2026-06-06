from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

__all__ = [
    "LearningLifecycle",
    "LL_CREATED",
    "LL_ACTIVE",
    "LL_ARCHIVED",
]

try:
    from agentx_evolve.learning.outcome_models import (
        LearningLifecycle as _LegacyLifecycle,
        LL_CREATED as _LL_CREATED,
        LL_PENDING_REVIEW as _LL_PENDING_REVIEW,
        LL_APPROVED as _LL_APPROVED,
        LL_ARCHIVED as _LL_ARCHIVED,
        LL_REJECTED as _LL_REJECTED,
        transition as _transition,
    )
    _HAS_OUTCOME_MODELS = True
except ImportError:
    _HAS_OUTCOME_MODELS = False

LL_CREATED = "CREATED"
LL_ACTIVE = "ACTIVE"
LL_ARCHIVED = "ARCHIVED"

_VALID_TRANSITIONS: dict[str, set[str]] = {
    LL_CREATED: {LL_ACTIVE},
    LL_ACTIVE: {LL_ARCHIVED},
    LL_ARCHIVED: set(),
}


@dataclass
class LearningLifecycle:
    candidate_id: str = ""
    status: str = LL_CREATED

    def transition(self, new_status: str) -> None:
        if _HAS_OUTCOME_MODELS:
            warnings.warn(
                "LearningLifecycle delegates to outcome_models.LearningLifecycle. "
                "Use learning_lifecycle directly in new code.",
                DeprecationWarning,
                stacklevel=2,
            )
            _LegacyLifecycle(self.candidate_id, new_status)
            return
        if new_status not in _VALID_TRANSITIONS.get(self.status, set()):
            raise ValueError(
                f"Invalid transition from {self.status} to {new_status}"
            )
        self.status = new_status
