from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any
import json

CONTEXT_PACKET_SCHEMA_VERSION = "adapter.context_packet.v1"


@dataclass
class StructuralContext:
    goal_type: str = ""
    task_type: str = ""
    runtime_mode: str = "offline"
    allowed_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    required_contracts: list[str] = field(default_factory=list)
    required_validators: list[str] = field(default_factory=list)
    required_proof_artifacts: list[str] = field(default_factory=list)
    capability_boundaries: list[str] = field(default_factory=list)
    promotion_rules: list[str] = field(default_factory=list)
    tool_policy: dict[str, Any] = field(default_factory=dict)
    model_policy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_type": self.goal_type,
            "task_type": self.task_type,
            "runtime_mode": self.runtime_mode,
            "allowed_actions": self.allowed_actions,
            "forbidden_actions": self.forbidden_actions,
            "required_contracts": self.required_contracts,
            "required_validators": self.required_validators,
            "required_proof_artifacts": self.required_proof_artifacts,
            "capability_boundaries": self.capability_boundaries,
            "promotion_rules": self.promotion_rules,
            "tool_policy": self.tool_policy,
            "model_policy": self.model_policy,
        }


@dataclass
class FactualItem:
    source: str = ""
    content: str = ""
    content_hash: str = ""
    provenance: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    stale: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "content_hash": self.content_hash,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
            "stale": self.stale,
        }


@dataclass
class ContextPacket:
    schema_version: str = CONTEXT_PACKET_SCHEMA_VERSION
    structural: StructuralContext = field(default_factory=StructuralContext)
    factual: list[FactualItem] = field(default_factory=list)
    packet_hash: str = ""

    def __post_init__(self) -> None:
        if not self.packet_hash:
            self.packet_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "structural": self.structural.to_dict(),
            "factual": [f.to_dict() for f in self.factual],
            "packet_hash": self.packet_hash,
        }

    def add_factual(self, item: FactualItem) -> None:
        if not item.provenance:
            raise ValueError("factual item requires provenance")
        if not item.content_hash:
            item.content_hash = sha256(item.content.encode("utf-8")).hexdigest()
        self.factual.append(item)
        self.packet_hash = self._compute_hash()

    def is_replayable(self) -> bool:
        return bool(self.packet_hash)
