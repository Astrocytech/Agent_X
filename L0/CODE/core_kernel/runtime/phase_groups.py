"""Canonical phase groups — derived from SEED_PHASE_CONTRACT_V1.

Phase groups: input, interpretation, profile_policy, planning, governance,
execution, memory, evaluation, persistence, output.

Each group has: started, completed, failed/skipped status.
All views are derived from the single-source-of-truth contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core_kernel.contracts.seed_phase_order import (
    PHASE_GROUPS as _CONTRACT_PHASE_GROUPS,
    REQUIRED_GROUPS as _CONTRACT_REQUIRED_GROUPS,
)

PHASE_GROUPS: dict[str, list[str]] = dict(_CONTRACT_PHASE_GROUPS)

GROUP_DISPLAY_NAMES = {
    "input": "Input",
    "interpretation": "Interpretation",
    "profile_policy": "Profile/Policy",
    "planning": "Planning",
    "governance": "Governance",
    "execution": "Execution",
    "memory": "Memory",
    "evaluation": "Evaluation",
    "persistence": "Persistence",
    "output": "Output",
}

REQUIRED_GROUPS: list[str] = list(_CONTRACT_REQUIRED_GROUPS)


def classify_event_phase(event_type: str) -> str:
    for group, events in PHASE_GROUPS.items():
        if event_type in events:
            return group
    return "unknown"


ALL_KNOWN_PHASES: set[str] = set()
for events in PHASE_GROUPS.values():
    ALL_KNOWN_PHASES.update(events)


@dataclass
class PhaseGroupStatus:
    group: str = ""
    started: bool = False
    completed: bool = False
    failed: bool = False
    skipped: bool = False
    reason: str = ""
    events: list[str] = field(default_factory=list)
    first_event_time: str = ""
    last_event_time: str = ""


@dataclass
class PhaseGroupReport:
    groups: dict[str, PhaseGroupStatus] = field(default_factory=dict)
    all_required_completed: bool = False
    missing_groups: list[str] = field(default_factory=list)
    governance_before_execution: bool = False
    persistence_before_output: bool = False
    unknown_phases: list[str] = field(default_factory=list)

    @classmethod
    def from_events(cls, events: list[dict[str, Any]]) -> PhaseGroupReport:
        groups: dict[str, PhaseGroupStatus] = {g: PhaseGroupStatus(group=g) for g in PHASE_GROUPS}
        unknown_phases: list[str] = []

        for event in events:
            phase = event.get("phase", "")
            group_name = classify_event_phase(phase)
            if group_name == "unknown":
                unknown_phases.append(phase)
                continue
            group = groups[group_name]
            group.started = True
            group.events.append(phase)
            if "failed" in phase:
                group.failed = True
                group.reason = event.get("error", event.get("reason", ""))
            if "completed" in phase or phase in ("output_returned",):
                group.completed = True
            if not group.first_event_time:
                group.first_event_time = event.get("timestamp", "")
            group.last_event_time = event.get("timestamp", "")

        missing = [g for g in REQUIRED_GROUPS if not groups[g].started]
        all_completed = all(groups[g].completed for g in REQUIRED_GROUPS if groups[g].started)

        gov_idx = -1
        exec_idx = -1
        for i, event in enumerate(events):
            phase = event.get("phase", "")
            if classify_event_phase(phase) == "governance" and gov_idx == -1:
                gov_idx = i
            if classify_event_phase(phase) == "execution" and exec_idx == -1:
                exec_idx = i

        persist_idx = -1
        output_idx = -1
        for i, event in enumerate(events):
            phase = event.get("phase", "")
            if classify_event_phase(phase) == "persistence":
                persist_idx = i
            if phase == "output_returned":
                output_idx = i

        return cls(
            groups=groups,
            all_required_completed=all_completed,
            missing_groups=missing,
            governance_before_execution=(
                gov_idx < exec_idx if gov_idx != -1 and exec_idx != -1 else False
            ),
            persistence_before_output=(
                persist_idx < output_idx if persist_idx != -1 and output_idx != -1 else False
            ),
            unknown_phases=unknown_phases,
        )
