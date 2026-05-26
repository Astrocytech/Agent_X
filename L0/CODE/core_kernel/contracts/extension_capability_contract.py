"""Contract for declaring evolved capabilities attached to the seed ABI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


CapabilityType = Literal[
    "planner",
    "governance",
    "tool",
    "memory",
    "evaluation",
    "trace",
    "checkpoint",
    "profile",
    "policy",
    "risk_policy",
    "evidence_writer",
    "orchestrator",
    "controller",
    "manager",
]

RiskClass = Literal[
    "safe_local",
    "read_only",
    "requires_approval",
    "irreversible",
    "forbidden_in_l0",
]


@dataclass(frozen=True)
class ExtensionCapabilityDeclaration:
    capability_id: str
    capability_type: CapabilityType
    attached_port: str
    version: str
    risk_class: RiskClass
    tool_names: tuple[str, ...] = ()
    evidence_required: bool = True
    replay_required: bool = True
    checkpoint_required: bool = True
    rollback_supported: bool = True
    description: str = ""
    proof_commands: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.capability_id:
            errors.append("capability_id is required")
        if not self.attached_port:
            errors.append("attached_port is required")
        if not self.version:
            errors.append("version is required")
        if self.risk_class == "forbidden_in_l0" and self.capability_type != "tool":
            errors.append("forbidden_in_l0 risk is only valid for tool-like capabilities")
        if not self.rollback_supported:
            errors.append("rollback/removal support is required")
        if self.evidence_required is False:
            errors.append("evidence is required for evolved capabilities")
        if self.replay_required is False:
            errors.append("replay is required for evolved capabilities")
        if self.checkpoint_required is False:
            errors.append("checkpointing is required for evolved capabilities")

        return errors
