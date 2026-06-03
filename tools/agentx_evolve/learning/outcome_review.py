from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict


@dataclass
class OutcomeRecord:
    outcome_id: str = ""
    session_id: str = ""
    attempted_task: str = ""
    proposal_type: str = ""
    files_changed: list[str] = field(default_factory=list)
    model_used: str = ""
    validation_outcome: str = ""
    rollback_outcome: str = ""
    failure_reason: str = ""
    successful_strategy: str = ""
    future_recommendation: str = ""
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class OutcomeReview:
    def __init__(self):
        self._records: list[OutcomeRecord] = []

    def record(self, outcome: OutcomeRecord) -> None:
        if not outcome.outcome_id:
            outcome.outcome_id = new_id("or")
        if not outcome.timestamp:
            outcome.timestamp = datetime.now(timezone.utc).isoformat()
        self._records.append(outcome)

    def get_by_session(self, session_id: str) -> list[OutcomeRecord]:
        return [r for r in self._records if r.session_id == session_id]

    def list_all(self) -> list[OutcomeRecord]:
        return list(self._records)

    def get_successful_strategies(self) -> list[OutcomeRecord]:
        return [r for r in self._records if r.successful_strategy]

    def get_failure_patterns(self) -> list[OutcomeRecord]:
        return [r for r in self._records if r.failure_reason]

    def get_recommendations(self) -> list[str]:
        return [r.future_recommendation for r in self._records if r.future_recommendation]


class StrategyMemory:
    def __init__(self):
        self._store: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        self._store[key] = value

    def retrieve(self, key: str) -> Any | None:
        return self._store.get(key)

    def search(self, prefix: str) -> dict[str, Any]:
        return {k: v for k, v in self._store.items() if k.startswith(prefix)}

    def clear(self) -> None:
        self._store.clear()
