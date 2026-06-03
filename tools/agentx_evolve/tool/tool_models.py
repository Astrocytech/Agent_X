from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

TS_SUCCESS = "SUCCESS"
TS_PARTIAL = "PARTIAL"
TS_BLOCKED = "BLOCKED"
TS_FAILED = "FAILED"
TS_INVALID = "INVALID"
ALL_TOOL_STATUSES = [TS_SUCCESS, TS_PARTIAL, TS_BLOCKED, TS_FAILED, TS_INVALID]


class ToolStatus(Enum):
    SUCCESS = TS_SUCCESS
    PARTIAL = TS_PARTIAL
    BLOCKED = TS_BLOCKED
    FAILED = TS_FAILED
    INVALID = TS_INVALID


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str = "") -> str:
    if prefix:
        return f"{prefix}-{uuid4().hex}"
    return uuid4().hex


def to_dict(obj: object) -> dict:
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            elif isinstance(val, Enum):
                result[f] = val.value
            else:
                result[f] = val
        return result
    if isinstance(obj, dict):
        return {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in obj]
    return obj


@dataclass
class ToolParameter:
    name: str = ""
    param_type: str = "string"
    description: str = ""
    required: bool = False
    default: Any = None


@dataclass
class ToolDefinition:
    schema_version: str = "1.0"
    schema_id: str = "tool_definition.schema.json"
    tool_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    description: str = ""
    parameters: list[ToolParameter] = field(default_factory=list)
    handler_name: str = ""
    requires_approval: bool = False
    side_effect: str = "read"
    enabled: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ToolCall:
    call_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ToolResult:
    schema_version: str = "1.0"
    schema_id: str = "tool_result.schema.json"
    result_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    status: str = TS_SUCCESS
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    artifact_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def to_simple_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "status": self.status,
            "message": self.message,
            "data": self.data,
            "artifact_refs": self.artifact_refs,
            "warnings": self.warnings,
            "errors": self.errors,
        }
