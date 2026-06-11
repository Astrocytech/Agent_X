from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.runtime.deterministic_clock import MvpDeterministicClock
from agentx_evolve.runtime.randomness import MvpSeededRandomness


@dataclass
class MvpRuntimeContext:
    run_id: str = ""
    goal_id: str = ""
    profile_id: str = ""
    clock: MvpDeterministicClock = field(default_factory=MvpDeterministicClock)
    randomness: MvpSeededRandomness = field(default_factory=MvpSeededRandomness)
    metadata: dict[str, Any] = field(default_factory=dict)

    def initialize(self, goal_text: str = "", profile_id: str = "") -> None:
        rid = self.randomness.next_id("run_")
        self.run_id = rid
        self.goal_id = self.randomness.next_id("goal_")
        self.profile_id = profile_id or "default"
        self.metadata["goal_text"] = goal_text
        self.metadata["started_at"] = self.clock.now_iso()

    def serialize(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal_id": self.goal_id,
            "profile_id": self.profile_id,
            "clock": self.clock.serialize(),
            "randomness": self.randomness.serialize(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def deserialize(cls, data: dict) -> MvpRuntimeContext:
        ctx = cls(
            run_id=data.get("run_id", ""),
            goal_id=data.get("goal_id", ""),
            profile_id=data.get("profile_id", ""),
            clock=MvpDeterministicClock.deserialize(data.get("clock", {})),
            randomness=MvpSeededRandomness.deserialize(data.get("randomness", {})),
            metadata=data.get("metadata", {}),
        )
        return ctx
