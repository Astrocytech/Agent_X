"""Phase recorder — records seed runtime phase execution metrics.

Critical rules:
- PhaseRecorder is reset per turn (not shared across turns).
- Unknown/noncanonical phase names are rejected at start time.
- Failure phases are recorded with success=False so they don't count as completed.
- validate_all_phases_completed checks the grouped tool outcome rather than requiring tool_gateway_called.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from core_kernel.runtime.phase_groups import ALL_KNOWN_PHASES, PhaseGroupReport
from core_kernel.contracts.seed_phase_order import SEED_PHASE_CONTRACT_V1
from core_kernel.contracts.seed_phase_order import (
    CANONICAL_SEED_PHASES,
    REQUIRED_SEED_PHASES,
)
from core_kernel.models.enums.seed_phase import SeedPhase


@dataclass
class PhaseRecord:
    name: str
    started_at: float
    ended_at: float = 0.0
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""


_REPEATABLE_PHASES = {spec.name for spec in SEED_PHASE_CONTRACT_V1 if spec.repeatable}

_ALLOWED_AFTER_MAP: dict[str, tuple[str, ...]] = {}
_GROUP_RESOLUTIONS: dict[str, set[str]] = {}
_SPEC_GROUP: dict[str, str] = {}
for _spec in SEED_PHASE_CONTRACT_V1:
    _ALLOWED_AFTER_MAP[_spec.name] = _spec.allowed_after
    _SPEC_GROUP[_spec.name] = _spec.group
    if _spec.marks_group_completed or _spec.marks_group_failed or _spec.marks_group_skipped:
        _GROUP_RESOLUTIONS.setdefault(_spec.group, set()).add(_spec.name)


def _resolve_group(phase_name: str) -> str | None:
    return _SPEC_GROUP.get(phase_name)


class PhaseRecorder:
    def __init__(self) -> None:
        self.phases: list[PhaseRecord] = []
        self._current: PhaseRecord | None = None
        self._completed_phases: set[str] = set()
        self._seen_phases: set[str] = set()
        self._phase_order = CANONICAL_SEED_PHASES
        self._required_phases = REQUIRED_SEED_PHASES

    def start_phase(self, name: str) -> None:
        if name not in ALL_KNOWN_PHASES:
            raise ValueError(
                f"Unknown phase '{name}' — not in canonical phase set"
            )
        if name in self._completed_phases and name not in _REPEATABLE_PHASES:
            raise ValueError(f"Phase '{name}' already completed and is not repeatable")
        allowed_after = _ALLOWED_AFTER_MAP.get(name, ())
        if allowed_after:
            satisfied = [p for p in allowed_after if p in self._completed_phases]
            if not satisfied:
                raise ValueError(
                    f"Cannot start phase '{name}' — none of the required prior phases are completed: {allowed_after}"
                )
        if name in self._required_phases:
            idx = self._phase_order.index(name)
            for prior in self._required_phases:
                if self._phase_order.index(prior) >= idx:
                    continue
                if prior in self._completed_phases:
                    continue
                if prior in self._seen_phases:
                    raise ValueError(
                        f"Cannot start phase '{name}' — prior phase '{prior}' was started but not completed"
                    )
        self._current = PhaseRecord(name=name, started_at=time.monotonic())
        self._seen_phases.add(name)
        self._completed_phases.discard(name)

    def end_phase(self, success: bool = True, error: str = "") -> None:
        if self._current is None:
            return
        now = time.monotonic()
        self._current.ended_at = now
        self._current.duration_ms = (now - self._current.started_at) * 1000
        self._current.success = success
        self._current.error = error
        self.phases.append(self._current)
        if success:
            self._completed_phases.add(self._current.name)
        self._current = None

    def _all_recorded_phases(self) -> set[str]:
        recorded = set(self._completed_phases)
        for r in self.phases:
            recorded.add(r.name)
        return recorded

    def validate_all_phases_completed(self) -> list[str]:
        missing: list[str] = []
        recorded = self._all_recorded_phases()

        for p in SeedPhase.required_phases():
            group = _resolve_group(p.value)
            if group and recorded & _GROUP_RESOLUTIONS.get(group, set()):
                continue
            if p.value not in recorded:
                missing.append(p.value)

        tool_outcome = SeedPhase.tool_outcome_group()
        outcome_completed = any(p.value in recorded for p in tool_outcome)
        if not outcome_completed:
            missing.append("<tool_outcome_missing>")

        return sorted(missing)

    def validate_ordered_completion(self) -> list[str]:
        out_of_order: list[str] = []
        seen: set[str] = set()
        for record in self.phases:
            if not record.success:
                continue
            name = record.name
            if name in self._phase_order:
                idx = self._phase_order.index(name)
                prior_required = [
                    p for p in self._required_phases if self._phase_order.index(p) < idx
                ]
                for prior in prior_required:
                    if prior not in seen:
                        out_of_order.append(name)
                        break
            seen.add(name)
        return out_of_order

    def phases_as_events(self) -> list[dict]:
        return [
            {
                "phase": p.name,
                "started_at_monotonic": p.started_at,
                "ended_at_monotonic": p.ended_at,
                "duration_ms": p.duration_ms,
                "success": p.success,
                "error": p.error,
            }
            for p in self.phases
        ]

    def validate_phase_groups(self) -> PhaseGroupReport:
        return PhaseGroupReport.from_events(self.phases_as_events())

    def summary(self) -> dict[str, Any]:
        missing = self.validate_all_phases_completed()
        return {
            "total_phases": len(self.phases),
            "total_duration_ms": sum(p.duration_ms for p in self.phases),
            "all_phases_completed": len(missing) == 0,
            "missing_phases": missing,
            "phases": [
                {
                    "name": p.name,
                    "duration_ms": p.duration_ms,
                    "success": p.success,
                }
                for p in self.phases
            ],
        }

    def reset(self) -> None:
        self.phases.clear()
        self._current = None
        self._completed_phases.clear()
        self._seen_phases.clear()
