"""CheckpointRecord — checkpoint contract for turn state persistence."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckpointRecord:
    checkpoint_id: str = ""
    run_id: str = ""
    state: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    timestamp: str = ""

    @classmethod
    def create(cls, run_id: str, state: dict, **kwargs: Any) -> CheckpointRecord:
        return cls(
            checkpoint_id=f"ckpt-{uuid.uuid4().hex[:12]}",
            run_id=run_id,
            state=state,
            **kwargs,
        )
