from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

__all__ = [
    "LearningIdentity",
    "register_learner",
    "authenticate_learner",
]


@dataclass
class LearningIdentity:
    learner_id: str = ""
    learner_type: str = ""
    version: str = ""
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


_REGISTRY: dict[str, LearningIdentity] = {}


def register_learner(
    learner_id: str,
    learner_type: str,
    version: str = "1.0",
    metadata: dict[str, Any] | None = None,
) -> LearningIdentity:
    identity = LearningIdentity(
        learner_id=learner_id,
        learner_type=learner_type,
        version=version,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {},
    )
    _REGISTRY[learner_id] = identity
    return identity


def authenticate_learner(learner_id: str, expected_type: str | None = None) -> LearningIdentity | None:
    identity = _REGISTRY.get(learner_id)
    if identity is None:
        return None
    if expected_type is not None and identity.learner_type != expected_type:
        return None
    return identity
