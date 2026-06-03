from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

RULE_ALLOW = "ALLOW"
RULE_DENY = "DENY"
RULE_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

ENFORCEMENT_ALLOW = "ALLOW"
ENFORCEMENT_BLOCK = "BLOCK"
ENFORCEMENT_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

SIDE_EFFECT_READ = "read"
SIDE_EFFECT_WRITE = "write"
SIDE_EFFECT_DESTRUCTIVE = "destructive"

OP_READ = "READ"
OP_WRITE = "WRITE"
OP_EDIT = "EDIT"
OP_DELETE = "DELETE"
OP_EXECUTE = "EXECUTE"
OP_NETWORK = "NETWORK"
OP_SUBPROCESS = "SUBPROCESS"


class SideEffectLevel(Enum):
    READ = SIDE_EFFECT_READ
    WRITE = SIDE_EFFECT_WRITE
    DESTRUCTIVE = SIDE_EFFECT_DESTRUCTIVE


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
            if isinstance(val, Path):
                result[f] = str(val)
            elif isinstance(val, list):
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
class PolicyRule:
    rule_id: str = ""
    timestamp: str = ""
    effect: str = RULE_DENY
    operation: str = ""
    target_pattern: str = ""
    reason: str = ""
    priority: int = 0
    conditions: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class CapabilityDefinition:
    schema_version: str = "1.0"
    schema_id: str = "capability_definition.schema.json"
    capability_id: str = ""
    timestamp: str = ""
    name: str = ""
    description: str = ""
    allowed_operations: list[str] = field(default_factory=lambda: [OP_READ])
    side_effect_level: str = SIDE_EFFECT_READ
    requires_approval: bool = False
    rate_limit_per_minute: int = 0
    enabled: bool = True
    allowed_profiles: list[str] = field(default_factory=lambda: ["*"])
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class ToolCapability:
    schema_version: str = "1.0"
    schema_id: str = "tool_capability.schema.json"
    tool_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    description: str = ""
    capabilities: list[CapabilityDefinition] = field(default_factory=list)
    policy_rules: list[PolicyRule] = field(default_factory=list)
    enabled: bool = True
    requires_approval: bool = False
    side_effect_level: str = SIDE_EFFECT_READ
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)

    def get_capability(self, name: str) -> CapabilityDefinition | None:
        for c in self.capabilities:
            if c.name == name:
                return c
        return None

    def get_rule_for_operation(self, operation: str) -> PolicyRule | None:
        for rule in self.policy_rules:
            if rule.operation == operation or rule.operation == "*":
                return rule
        return None


@dataclass
class CapabilityRegistry:
    schema_version: str = "1.0"
    schema_id: str = "capability_registry.schema.json"
    registry_id: str = ""
    timestamp: str = ""
    tools: dict[str, ToolCapability] = field(default_factory=dict)
    global_rules: list[PolicyRule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = to_dict(self)
        d["tools"] = [v.to_dict() for v in self.tools.values()]
        d["global_rules"] = [r.to_dict() for r in self.global_rules]
        return d

    def register_tool(self, tool: ToolCapability) -> ToolCapability:
        self.tools[tool.tool_name] = tool
        return tool

    def get_tool(self, tool_name: str) -> ToolCapability | None:
        return self.tools.get(tool_name)

    def remove_tool(self, tool_name: str) -> bool:
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False

    def list_tools(self) -> list[ToolCapability]:
        return list(self.tools.values())

    def list_enabled_tools(self) -> list[ToolCapability]:
        return [t for t in self.tools.values() if t.enabled]


@dataclass
class PolicyEnforcementResult:
    schema_version: str = "1.0"
    schema_id: str = "policy_enforcement_result.schema.json"
    enforcement_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    operation: str = ""
    decision: str = ENFORCEMENT_BLOCK
    reason: str = ""
    matched_rule_id: str | None = None
    matched_rule_effect: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)
