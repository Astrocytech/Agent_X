"""Stop conditions and global safe-mode/kill switch.

Item 50 (42.1/42.2): Conditions that trigger emergency stop,
safe mode, or kill switch across the governance runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class StopLevel(Enum):
    NONE = "none"
    WARN = "warn"
    SAFE_MODE = "safe_mode"
    HARD_STOP = "hard_stop"
    KILL = "kill"


class StopReason(Enum):
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ESCALATION_LIMIT = "escalation_limit"
    REPEATED_FAILURE = "repeated_failure"
    TOO_MANY_RETRIES = "too_many_retries"
    UNAUTHORIZED_COMMAND = "unauthorized_command"
    SECRET_DETECTED = "secret_detected"
    MANUAL_INTERVENTION = "manual_intervention"
    TIMEOUT = "timeout"
    LOCK_CONTENTION = "lock_contention"
    CONFIGURATION_ERROR = "configuration_error"
    TEST_THRESHOLD = "test_threshold"


@dataclass
class StopCondition:
    condition_id: str
    description: str
    level: StopLevel = StopLevel.WARN
    reason: StopReason = StopReason.THRESHOLD_EXCEEDED
    threshold: float = 0.0
    counter: int = 0
    max_count: int = 5
    active: bool = True


class KillSwitch:
    def __init__(self):
        self._conditions: dict[str, StopCondition] = {}
        self._triggered: list[dict] = []
        self._global_safe_mode: bool = False

    def register(self, condition: StopCondition) -> None:
        self._conditions[condition.condition_id] = condition

    def trigger(self, condition_id: str, detail: str = "") -> StopLevel | None:
        cond = self._conditions.get(condition_id)
        if not cond or not cond.active:
            return None
        cond.counter += 1
        entry = {"condition_id": condition_id, "counter": cond.counter,
                 "level": cond.level.value, "detail": detail}
        self._triggered.append(entry)

        if cond.counter >= cond.max_count:
            cond.active = False
            if cond.level in (StopLevel.SAFE_MODE, StopLevel.HARD_STOP):
                self._global_safe_mode = True
            return cond.level

        if cond.level == StopLevel.KILL:
            return StopLevel.KILL
        return cond.level

    def triggered_count(self) -> int:
        return len(self._triggered)

    def is_safe_mode(self) -> bool:
        return self._global_safe_mode

    def enable_safe_mode(self) -> None:
        self._global_safe_mode = True

    def disable_safe_mode(self) -> None:
        self._global_safe_mode = False

    def status(self) -> dict:
        return {
            "safe_mode": self._global_safe_mode,
            "triggered_count": len(self._triggered),
            "active_conditions": sum(1 for c in self._conditions.values() if c.active),
            "conditions": [{"id": cond.condition_id, "level": cond.level.value,
                           "counter": cond.counter, "active": cond.active}
                          for cond in self._conditions.values()],
            "recent_triggered": self._triggered[-10:],
        }


SYSTEM_KILL_SWITCH = KillSwitch()


def RegisterDefaultConditions() -> None:
    SYSTEM_KILL_SWITCH.register(StopCondition(
        "sc-001", "Escalation limit exceeded", StopLevel.HARD_STOP,
        StopReason.ESCALATION_LIMIT, max_count=3))
    SYSTEM_KILL_SWITCH.register(StopCondition(
        "sc-002", "Repeated test failure threshold", StopLevel.SAFE_MODE,
        StopReason.REPEATED_FAILURE, max_count=5))
    SYSTEM_KILL_SWITCH.register(StopCondition(
        "sc-003", "Unauthorized command detected", StopLevel.HARD_STOP,
        StopReason.UNAUTHORIZED_COMMAND, max_count=1))
    SYSTEM_KILL_SWITCH.register(StopCondition(
        "sc-004", "Secret detected in evidence", StopLevel.WARN,
        StopReason.SECRET_DETECTED, max_count=2))
    SYSTEM_KILL_SWITCH.register(StopCondition(
        "sc-005", "Timeout exceeded", StopLevel.KILL,
        StopReason.TIMEOUT, max_count=1))
