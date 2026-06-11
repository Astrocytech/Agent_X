from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.lifecycle.state_machine import MvpStateMachine

ACTION_STATES = [
    "DRAFT", "PROPOSED", "VALIDATED", "SIMULATED", "APPROVED",
    "EXECUTED", "OBSERVED", "TESTED", "REVIEWED",
    "PROMOTED", "REJECTED", "ROLLED_BACK", "ARCHIVED",
]

VALID_TRANSITIONS: dict[str, list[str]] = {
    "DRAFT": ["PROPOSED"],
    "PROPOSED": ["VALIDATED"],
    "VALIDATED": ["SIMULATED"],
    "SIMULATED": ["APPROVED"],
    "APPROVED": ["EXECUTED"],
    "EXECUTED": ["OBSERVED", "ROLLED_BACK"],
    "OBSERVED": ["TESTED"],
    "TESTED": ["REVIEWED"],
    "REVIEWED": ["PROMOTED", "REJECTED"],
    "PROMOTED": ["ARCHIVED"],
    "REJECTED": ["ARCHIVED"],
    "ROLLED_BACK": ["ARCHIVED"],
    "ARCHIVED": [],
}

FORBIDDEN_TRANSITIONS: list[tuple[str, str]] = [
    ("DRAFT", "EXECUTED"),
    ("PROPOSED", "EXECUTED"),
    ("VALIDATED", "PROMOTED"),
    ("EXECUTED", "PROMOTED"),
    ("TESTED", "PROMOTED"),
    ("REJECTED", "PROMOTED"),
    ("ROLLED_BACK", "PROMOTED"),
]


@dataclass
class MvpAction:
    action_id: str = ""
    goal_id: str = ""
    profile_id: str = ""
    agent_id: str = ""
    action_type: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    state_machine: MvpStateMachine = field(default_factory=lambda: MvpStateMachine(ACTION_STATES, VALID_TRANSITIONS))

    def __post_init__(self) -> None:
        self.state_machine.reset("DRAFT")

    @property
    def status(self) -> str:
        return self.state_machine.current or "DRAFT"

    def propose(self) -> str:
        return self.state_machine.transition("PROPOSED")

    def validate(self) -> str:
        return self.state_machine.transition("VALIDATED")

    def simulate(self) -> str:
        return self.state_machine.transition("SIMULATED")

    def approve(self) -> str:
        return self.state_machine.transition("APPROVED")

    def execute(self) -> str:
        if self.state_machine.current in ("DRAFT", "PROPOSED"):
            raise ValueError(f"Forbidden transition: {self.state_machine.current} -> EXECUTED")
        return self.state_machine.transition("EXECUTED")

    def observe(self) -> str:
        return self.state_machine.transition("OBSERVED")

    def test(self) -> str:
        return self.state_machine.transition("TESTED")

    def review(self) -> str:
        return self.state_machine.transition("REVIEWED")

    def promote(self) -> str:
        if self.state_machine.current == "REVIEWED":
            return self.state_machine.transition("PROMOTED")
        raise ValueError(f"Cannot promote from {self.state_machine.current}: review required")

    def reject(self) -> str:
        return self.state_machine.transition("REJECTED")

    def rollback(self) -> str:
        return self.state_machine.transition("ROLLED_BACK")

    def archive(self) -> str:
        return self.state_machine.transition("ARCHIVED")

    def is_terminal(self) -> bool:
        return self.state_machine.is_terminal()

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "goal_id": self.goal_id,
            "profile_id": self.profile_id,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "payload": dict(self.payload),
            "state": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpAction:
        action = cls(
            action_id=data.get("action_id", ""),
            goal_id=data.get("goal_id", ""),
            profile_id=data.get("profile_id", ""),
            agent_id=data.get("agent_id", ""),
            action_type=data.get("action_type", ""),
            payload=data.get("payload", {}),
        )
        state = data.get("state", "DRAFT")
        action.state_machine.reset(state)
        return action
