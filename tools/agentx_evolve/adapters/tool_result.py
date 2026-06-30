from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from hashlib import sha256
import json


TOOL_CALL_SCHEMA_VERSION = "adapter.tool_call.v1"
TOOL_RESULT_SCHEMA_VERSION = "adapter.tool_result.v1"


@dataclass
class ToolCall:
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    call_id: str = ""
    run_id: str = ""
    action_id: str = ""
    schema_version: str = TOOL_CALL_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "call_id": self.call_id,
            "run_id": self.run_id,
            "action_id": self.action_id,
            "schema_version": self.schema_version,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.tool_name:
            errors.append("tool_name is required")
        if not self.call_id:
            errors.append("call_id is required")
        if not self.run_id:
            errors.append("run_id is required")
        return errors


@dataclass
class ToolResult:
    tool_name: str = ""
    call_id: str = ""
    status: str = "DENIED"
    output: dict[str, Any] = field(default_factory=dict)
    output_text: str = ""
    output_hash: str = ""
    provenance: dict[str, str] = field(default_factory=dict)
    failure_class: str = ""
    failure_reason: str = ""
    schema_version: str = TOOL_RESULT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.output_hash and self.output_text:
            self.output_hash = sha256(self.output_text.encode("utf-8")).hexdigest()
        elif not self.output_hash and self.output:
            raw = json.dumps(self.output, sort_keys=True)
            self.output_hash = sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "call_id": self.call_id,
            "status": self.status,
            "output_hash": self.output_hash,
            "output": self.output,
            "provenance": self.provenance,
            "failure_class": self.failure_class,
            "failure_reason": self.failure_reason,
            "schema_version": self.schema_version,
        }

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.tool_name:
            errors.append("tool_name is required")
        if not self.call_id:
            errors.append("call_id is required")
        if not self.provenance:
            errors.append("provenance is required")
        return errors
