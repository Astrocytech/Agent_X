from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

EVIDENCE_PACKET_SCHEMA_VERSION = "adapter.evidence_packet.v1"

TRUST_LEVELS = {
    "trusted_runtime_evidence",
    "trusted_test_result",
    "trusted_command_result",
    "trusted_git_result",
    "untrusted_tool_output",
    "untrusted_document_text",
    "untrusted_model_output",
    "untrusted_retrieval_result",
}

UNTRUSTED_LEVELS = {"untrusted_tool_output", "untrusted_document_text", "untrusted_model_output", "untrusted_retrieval_result"}


@dataclass
class EvidencePacket:
    evidence_id: str = ""
    run_id: str = ""
    source_type: str = ""
    source_adapter: str = ""
    producer_id: str = ""
    schema_version: str = EVIDENCE_PACKET_SCHEMA_VERSION
    payload: dict[str, Any] = field(default_factory=dict)
    payload_hash: str = ""
    trust_level: str = "untrusted_tool_output"
    created_at: str = ""
    replay_status: str = ""
    provenance: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "run_id": self.run_id,
            "source_type": self.source_type,
            "source_adapter": self.source_adapter,
            "producer_id": self.producer_id,
            "schema_version": self.schema_version,
            "payload_hash": self.payload_hash,
            "trust_level": self.trust_level,
            "created_at": self.created_at,
            "replay_status": self.replay_status,
            "provenance": self.provenance,
        }


class EvidenceBridge:
    def normalize(self, source_type: str, source_adapter: str, payload: dict[str, Any],
                  provenance: dict[str, str] | None = None) -> EvidencePacket:
        raw = str(payload)
        payload_hash = sha256(raw.encode("utf-8")).hexdigest()

        trust_level = "untrusted_tool_output"
        if source_type in ("runtime_state", "test_result", "command_result", "git_result"):
            trust_level = f"trusted_{source_type}"

        return EvidencePacket(
            evidence_id=f"ev-{payload_hash[:12]}",
            source_type=source_type,
            source_adapter=source_adapter,
            payload=payload,
            payload_hash=payload_hash,
            trust_level=trust_level,
            provenance=provenance or {},
        )

    def validate(self, packet: EvidencePacket) -> list[str]:
        errors: list[str] = []
        if not packet.payload_hash:
            errors.append("payload_hash is required")
        if not packet.provenance:
            errors.append("provenance is required")
        if packet.source_type not in ("model_output", "tool_output", "mcp_output", "command_output",
                                       "runtime_state", "test_result", "command_result", "git_result"):
            errors.append(f"unknown source_type: {packet.source_type}")
        computed = sha256(str(packet.payload).encode("utf-8")).hexdigest()
        if packet.payload_hash and packet.payload_hash != computed:
            errors.append(f"payload hash mismatch: expected {computed}")
        return errors

    def is_trusted(self, packet: EvidencePacket) -> bool:
        return packet.trust_level not in UNTRUSTED_LEVELS
