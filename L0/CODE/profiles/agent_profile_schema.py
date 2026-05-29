from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class Profile:
    id: str = ""
    name: str = ""
    role: str = ""
    allowed_tools: list[str] = field(default_factory=list)
    planner_style: str = "direct"
    memory_retrieval: str = "focused"
    evaluation_criteria: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

# Fields that every valid profile MUST have with non-empty values
REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "role",
        "purpose",
        "allowed_tools",
        "stop_conditions",
    }
)

# All known/valid fields for a profile schema (used for unknown-field rejection)
KNOWN_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "role",
        "purpose",
        "required_policy_id",
        "model_policy",
        "allowed_tools",
        "allowed_capabilities",
        "capabilities",
        "forbidden_tools",
        "forbidden_capabilities",
        "default_evaluation_policy",
        "evolution_permissions",
        "allowed_memory_scopes",
        "input_schema",
        "output_schema",
        "risk_policy",
        "approval_policy",
        "stop_conditions",
        "handoff_rules",
        "schema_version",
        "prompt",
        "metadata",
    }
)


@dataclass
class AgentProfileSchema:
    id: str = ""
    name: str = ""
    role: str = ""
    purpose: str = ""
    required_policy_id: str = ""
    model_policy: dict[str, Any] = field(default_factory=dict)
    allowed_tools: list[str] = field(default_factory=list)
    allowed_capabilities: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    forbidden_capabilities: list[str] = field(default_factory=list)
    default_evaluation_policy: str = "strict"
    evolution_permissions: dict[str, bool] = field(default_factory=dict)
    allowed_memory_scopes: dict[str, list[str]] = field(default_factory=dict)
    input_schema: str = ""
    output_schema: str = ""
    risk_policy: str = "conservative"
    approval_policy: str = "approval_required_for_high_risk"
    stop_conditions: list[str] = field(default_factory=list)
    handoff_rules: dict[str, list[str]] = field(default_factory=dict)
    schema_version: int = 1
    prompt: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    REQUIRED_FIELDS: ClassVar[frozenset[str]] = REQUIRED_FIELDS
    KNOWN_FIELDS: ClassVar[frozenset[str]] = KNOWN_FIELDS
