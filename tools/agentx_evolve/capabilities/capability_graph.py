from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CAPABILITY_DENIAL_REASONS = {
    "unknown_agent",
    "unknown_capability",
    "wrong_target",
    "missing_validator",
    "missing_evidence",
    "self_modifying",
    "delegation_without_approval",
}


@dataclass
class CapabilityEntry:
    agent_id: str = ""
    capability: str = ""
    target: str = ""
    validator_required: str = ""
    evidence_required: str = ""
    requires_review: bool = False
    can_delegate: bool = False
    can_modify_self: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "capability": self.capability,
            "target": self.target,
            "validator_required": self.validator_required,
            "evidence_required": self.evidence_required,
            "requires_review": self.requires_review,
            "can_delegate": self.can_delegate,
            "can_modify_self": self.can_modify_self,
        }


class MvpCapabilityGraph:
    def __init__(self) -> None:
        self._entries: dict[str, CapabilityEntry] = {}

    def register(self, entry: CapabilityEntry) -> None:
        key = f"{entry.agent_id}:{entry.capability}:{entry.target}"
        self._entries[key] = entry

    def can(self, agent_id: str, capability: str, target: str = "") -> tuple[bool, str]:
        exact = self._entries.get(f"{agent_id}:{capability}:{target}")
        if exact:
            return self._check_entry(exact)

        wild_target = self._entries.get(f"{agent_id}:{capability}:")
        if wild_target:
            return self._check_entry(wild_target)

        if agent_id not in {e.agent_id for e in self._entries.values()}:
            return False, "unknown_agent"

        return False, "unknown_capability"

    def _check_entry(self, entry: CapabilityEntry) -> tuple[bool, str]:
        if entry.can_modify_self:
            return False, "self_modifying"
        if not entry.validator_required:
            return False, "missing_validator"
        if not entry.evidence_required:
            return False, "missing_evidence"
        return True, ""

    def who_can(self, capability: str, target: str = "") -> list[str]:
        result = []
        for key, entry in self._entries.items():
            if entry.capability == capability and (not target or entry.target == target):
                ok, _ = self._check_entry(entry)
                if ok:
                    result.append(entry.agent_id)
        return result

    def required_validator(self, agent_id: str, capability: str, target: str = "") -> str:
        key = f"{agent_id}:{capability}:{target}"
        entry = self._entries.get(key)
        if not entry:
            wild = self._entries.get(f"{agent_id}:{capability}:")
            entry = wild
        return entry.validator_required if entry else ""

    def required_evidence(self, agent_id: str, capability: str, target: str = "") -> str:
        key = f"{agent_id}:{capability}:{target}"
        entry = self._entries.get(key)
        if not entry:
            wild = self._entries.get(f"{agent_id}:{capability}:")
            entry = wild
        return entry.evidence_required if entry else ""

    def to_dict(self) -> dict[str, Any]:
        return {"entries": [e.to_dict() for e in self._entries.values()]}
