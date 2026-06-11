from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TRIGGER_INVARIANT_VIOLATION = "invariant_violation"
TRIGGER_SELF_PROMOTION = "unsafe_self_promotion_attempt"
TRIGGER_TOO_MANY_FAILURES = "too_many_repeated_failures"
TRIGGER_MANUAL_STOP = "manual_stop_request"
ALL_TRIGGERS = {TRIGGER_INVARIANT_VIOLATION, TRIGGER_SELF_PROMOTION,
                TRIGGER_TOO_MANY_FAILURES, TRIGGER_MANUAL_STOP}


@dataclass
class SafetyEvent:
    trigger: str = ""
    reason: str = ""
    action_id: str = ""
    run_id: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger": self.trigger,
            "reason": self.reason,
            "action_id": self.action_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
        }


class MvpCircuitBreaker:
    def __init__(self, max_failures: int = 3) -> None:
        self._tripped: bool = False
        self._events: list[SafetyEvent] = []
        self._failure_count: int = 0
        self._max_failures = max_failures

    @property
    def is_tripped(self) -> bool:
        return self._tripped

    def trip(self, trigger: str, reason: str, action_id: str = "",
             run_id: str = "", timestamp: str = "") -> SafetyEvent:
        event = SafetyEvent(
            trigger=trigger, reason=reason,
            action_id=action_id, run_id=run_id, timestamp=timestamp,
        )
        self._events.append(event)
        self._tripped = True
        return event

    def record_failure(self, action_id: str = "", run_id: str = "",
                       timestamp: str = "") -> SafetyEvent | None:
        self._failure_count += 1
        if self._failure_count >= self._max_failures:
            return self.trip(
                trigger=TRIGGER_TOO_MANY_FAILURES,
                reason=f"Too many repeated failures ({self._failure_count})",
                action_id=action_id, run_id=run_id, timestamp=timestamp,
            )
        return None

    def manual_stop(self, reason: str, action_id: str = "",
                    run_id: str = "", timestamp: str = "") -> SafetyEvent:
        return self.trip(
            trigger=TRIGGER_MANUAL_STOP, reason=reason,
            action_id=action_id, run_id=run_id, timestamp=timestamp,
        )

    def reset(self) -> None:
        self._tripped = False
        self._failure_count = 0

    def events(self, trigger: str | None = None) -> list[SafetyEvent]:
        if trigger is None:
            return list(self._events)
        return [e for e in self._events if e.trigger == trigger]
