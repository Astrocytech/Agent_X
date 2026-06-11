from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from agentx_evolve.io.result_envelope import MvpResultEnvelope, register_record_type

register_record_type("event")


@dataclass
class MvpEvent:
    message_id: str = ""
    event_type: str = ""
    run_id: str = ""
    sender_id: str = ""
    receiver_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def validate(self) -> list[str]:
        issues = []
        if not self.message_id:
            issues.append("message_id required")
        if not self.event_type:
            issues.append("event_type required")
        if not self.run_id:
            issues.append("run_id required")
        if not self.sender_id:
            issues.append("sender_id required")
        return issues

    def to_envelope(self) -> MvpResultEnvelope:
        return MvpResultEnvelope(
            run_id=self.run_id,
            producer_id=self.sender_id,
            consumer_id=self.receiver_id,
            record_type="event",
            status="PASS",
            payload=self.to_dict(),
            created_at=self.created_at,
        )

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "event_type": self.event_type,
            "run_id": self.run_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "payload": self.payload,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpEvent:
        return cls(
            message_id=data.get("message_id", ""),
            event_type=data.get("event_type", ""),
            run_id=data.get("run_id", ""),
            sender_id=data.get("sender_id", ""),
            receiver_id=data.get("receiver_id", ""),
            payload=data.get("payload", {}),
            created_at=data.get("created_at", ""),
        )


class MvpEventBus:
    def __init__(self, log_path: str | Path | None = None) -> None:
        self._log_path = Path(log_path) if log_path else None
        self._subscribers: dict[str, list[Callable[[MvpEvent], None]]] = {}
        self._history: list[MvpEvent] = []

    def publish(self, event: MvpEvent) -> None:
        issues = event.validate()
        if issues:
            raise ValueError(f"Invalid event: {'; '.join(issues)}")
        self._history.append(event)
        self._persist(event)
        for et, subs in self._subscribers.items():
            if et == event.event_type or et == "*":
                for sub in subs:
                    sub(event)

    def subscribe(self, event_type: str, callback: Callable[[MvpEvent], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def history(self, run_id: str | None = None) -> list[MvpEvent]:
        if run_id is None:
            return list(self._history)
        return [e for e in self._history if e.run_id == run_id]

    def _persist(self, event: MvpEvent) -> None:
        if self._log_path is None:
            return
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def replay_log(self, log_path: str | Path | None = None) -> list[MvpEvent]:
        path = self._log_path if log_path is None else Path(log_path)
        if not path or not path.exists():
            return []
        events = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    event = MvpEvent.from_dict(json.loads(line))
                    events.append(event)
                    self._history.append(event)
        return events

    def clear(self) -> None:
        self._history.clear()
        self._subscribers.clear()
