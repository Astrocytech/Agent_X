from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from hashlib import sha256
import json


RESPONSE_SCHEMA_VERSION = "adapter.model_response.v1"

STATUS_SUCCESS = "SUCCESS"
STATUS_REFUSAL = "REFUSAL"
STATUS_BLOCKED = "BLOCKED"
STATUS_ERROR = "ERROR"
STATUS_SCHEMA_ERROR = "SCHEMA_ERROR"
STATUS_TIMEOUT = "TIMEOUT"

VALID_STATUSES = {STATUS_SUCCESS, STATUS_REFUSAL, STATUS_BLOCKED, STATUS_ERROR, STATUS_SCHEMA_ERROR, STATUS_TIMEOUT}


@dataclass
class ModelResponseSchema:
    schema_version: str = RESPONSE_SCHEMA_VERSION
    provider_id: str = ""
    model_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"schema_version": self.schema_version, "provider_id": self.provider_id, "model_id": self.model_id}


@dataclass
class ModelResponse:
    provider_id: str = ""
    model_id: str = ""
    status: str = STATUS_BLOCKED
    output_text: str = ""
    output_hash: str = ""
    structured_output: dict[str, Any] | None = None
    failure_class: str = ""
    failure_reason: str = ""
    token_usage: dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0
    schema_version: str = RESPONSE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.output_hash and self.output_text:
            self.output_hash = sha256(self.output_text.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "status": self.status,
            "output_hash": self.output_hash,
            "structured_output": self.structured_output,
            "failure_class": self.failure_class,
            "failure_reason": self.failure_reason,
            "token_usage": self.token_usage,
            "latency_ms": self.latency_ms,
            "schema_version": self.schema_version,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.provider_id:
            errors.append("provider_id is required")
        if not self.model_id:
            errors.append("model_id is required")
        if self.status not in VALID_STATUSES:
            errors.append(f"invalid status: {self.status}")
        if self.status == STATUS_SUCCESS and not self.output_hash:
            errors.append("output_hash required for SUCCESS")
        return errors


def hash_dict(d: dict[str, Any]) -> str:
    raw = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()
