from __future__ import annotations

from typing import Any


class MvpStateMachine:
    def __init__(self, states: list[str], valid_transitions: dict[str, list[str]]):
        self._states = states
        self._transitions = valid_transitions
        self._current: str | None = None

    @property
    def current(self) -> str | None:
        return self._current

    @property
    def states(self) -> list[str]:
        return list(self._states)

    def reset(self, initial: str) -> None:
        if initial not in self._states:
            raise ValueError(f"Invalid initial state: {initial}")
        self._current = initial

    def can_transition(self, target: str) -> bool:
        if self._current is None:
            return target in self._states
        allowed = self._transitions.get(self._current, [])
        return target in allowed

    def transition(self, target: str) -> str:
        if self._current is None:
            if target not in self._states:
                raise ValueError(f"Cannot start from unknown state: {target}")
            self._current = target
            return self._current
        if not self.can_transition(target):
            raise ValueError(
                f"Invalid transition: {self._current} -> {target} "
                f"(allowed: {self._transitions.get(self._current, [])})"
            )
        self._current = target
        return self._current

    def is_terminal(self) -> bool:
        if self._current is None:
            return False
        return len(self._transitions.get(self._current, [])) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self._current,
            "states": self._states,
        }
