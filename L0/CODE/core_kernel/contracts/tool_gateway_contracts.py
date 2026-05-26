"""Seed-owned tool gateway contracts — tool request/result data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolResultStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"
    INVALID_REQUEST = "invalid_request"


class ToolRiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SideEffectClass(Enum):
    READ_ONLY = "read_only"
    MEMORY_WRITE = "memory_write"
    LOCAL_FILE_WRITE = "local_file_write"
    NETWORK_CALL = "network_call"
    EXTERNAL_API_CALL = "external_api_call"
    DATABASE_WRITE = "database_write"
    SHELL_COMMAND = "shell_command"
    SELF_MODIFICATION = "self_modification"


@dataclass
class ToolSpec:
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    risk_level: ToolRiskLevel = ToolRiskLevel.NONE
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY
    requires_approval: bool = False


@dataclass
class ToolCallRequest:
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    run_id: str = ""
    profile_id: str = ""
    trace_id: str = ""
    call_id: str = ""


@dataclass
class ToolCallResponse:
    status: ToolResultStatus = ToolResultStatus.SUCCEEDED
    output: str = ""
    error: str = ""
    blocked_reason: str = ""
    call_id: str = ""


@dataclass
class ToolContract:
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    risk_level: ToolRiskLevel = ToolRiskLevel.NONE
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY
    requires_approval: bool = False


@dataclass
class ToolSideEffect:
    side_effect_class: SideEffectClass = SideEffectClass.READ_ONLY
    target_resource: str = ""
    description: str = ""
