from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


REQUEST_SCHEMA_VERSION = "adapter.model_request.v1"


@dataclass
class ModelRequestSchema:
    schema_version: str = REQUEST_SCHEMA_VERSION
    provider_id: str = ""
    model_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"schema_version": self.schema_version, "provider_id": self.provider_id, "model_id": self.model_id}


@dataclass
class ModelRequest:
    run_id: str = ""
    prompt_contract_id: str = ""
    context_packet_hash: str = ""
    provider_id: str = ""
    model_id: str = ""
    prompt_text: str = ""
    schema_version: str = REQUEST_SCHEMA_VERSION
    capabilities: dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 2048
    temperature: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "prompt_contract_id": self.prompt_contract_id,
            "context_packet_hash": self.context_packet_hash,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "schema_version": self.schema_version,
            "capabilities": self.capabilities,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.run_id:
            errors.append("run_id is required")
        if not self.prompt_contract_id:
            errors.append("prompt_contract_id is required")
        if not self.context_packet_hash:
            errors.append("context_packet_hash is required")
        if not self.provider_id:
            errors.append("provider_id is required")
        if not self.model_id:
            errors.append("model_id is required")
        return errors
