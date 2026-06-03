from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "MemoryLifecycle",
    "MC_CANDIDATE",
    "MC_ACTIVE",
    "MC_STALE",
    "MC_ARCHIVED",
    "transition",
]

MC_CANDIDATE = "CANDIDATE"
MC_ACTIVE = "ACTIVE"
MC_STALE = "STALE"
MC_ARCHIVED = "ARCHIVED"

_VALID_TRANSITIONS: dict[str, set[str]] = {
    MC_CANDIDATE: {MC_ACTIVE, MC_STALE, MC_ARCHIVED},
    MC_ACTIVE: {MC_STALE, MC_ARCHIVED},
    MC_STALE: {MC_ARCHIVED, MC_ACTIVE},
    MC_ARCHIVED: set(),
}


@dataclass
class MemoryLifecycle:
    memory_id: str = ""
    status: str = MC_CANDIDATE
    warnings: list[str] = field(default_factory=list)

    def transition(self, new_state: str) -> None:
        if new_state not in _VALID_TRANSITIONS.get(self.status, set()):
            raise ValueError(
                f"Invalid MemoryLifecycle transition from {self.status} to {new_state}"
            )
        self.status = new_state


def transition(memory: MemoryLifecycle, new_state: str) -> MemoryLifecycle:
    memory.transition(new_state)
    return memory
