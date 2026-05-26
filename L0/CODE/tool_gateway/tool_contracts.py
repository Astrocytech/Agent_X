from __future__ import annotations

"""Tool Contracts module."""


from dataclasses import dataclass, field  # noqa: E402
from enum import Enum  # noqa: E402
from typing import Any, Literal  # noqa: E402

__all__ = [
    "ToolCallRequest",
    "ToolCallResponse",
    "ToolContract",
    "ToolRiskLevel",
    "ToolSpec",
    "ToolResultStatus",
    "ToolSideEffect",
    "SideEffectClass",
    "tool_schema_completeness_check",
]

ToolResultStatus = Literal["success", "failure", "blocked"]


class ToolRiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SideEffectClass(Enum):
    """Eight-way side-effect classification for tool contracts."""

    READ_ONLY = "read_only"
    MEMORY_WRITE = "memory_write"
    LOCAL_FILE_WRITE = "local_file_write"
    NETWORK_CALL = "network_call"
    EXTERNAL_API_CALL = "external_api_call"
    CODE_PATCH = "code_patch"
    SHELL_COMMAND = "shell_command"
    DESTRUCTIVE_ACTION = "destructive_action"


@dataclass
class ToolContract:
    schema_version: str = "tool_contract_v1"
    name: str = ""
    description: str = ""
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    category: str = ""
    requires_approval: bool = False
    allowed_scopes: list[str] = field(default_factory=list)
    timeout_seconds: int = 30
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
    governed: bool = False
    requires_context: bool = False
    required_context_fields: list[str] = field(default_factory=list)
    namespace_scoped: bool = False
    forbidden_profiles: list[str] = field(default_factory=list)
    resource_estimate: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    side_effect_class: str = "read_only"
    permission_scope: str = ""
    rollback_behavior: str = ""
    evidence_required: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.name

    @property
    def side_effect_level(self) -> str:
        risk = self.risk_level
        if hasattr(risk, "value"):
            risk_val = risk.value
        else:
            risk_val = str(risk)
        if risk_val == "critical":
            return "irreversible"
        if risk_val == "high":
            return "unbounded"
        if risk_val == "medium":
            return "bounded"
        return "none"

    @property
    def allowed_profiles(self) -> list[str]:
        return self.allowed_scopes

    @property
    def transport(self) -> str:
        return self.metadata.get("transport", "local")


ToolSpec = ToolContract


@dataclass
class ToolCallRequest:
    schema_version: str = "tool_call_v1"
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    profile_id: str = ""
    run_id: str = ""
    request_id: str = ""
    client_id: str = ""
    namespace_id: str = ""
    actor_id: str = ""
    owner_id: str = ""
    task_id: str = ""
    effective_policy_id: str = ""
    governance_decision_id: str = ""
    planner_decision_id: str = ""
    risk_level: ToolRiskLevel = ToolRiskLevel.NONE
    dry_run: bool = False
    requires_approval: bool = False
    approval_token: str = ""
    source_phase: str = ""
    correlation_id: str = ""
    target_resource: str = ""
    side_effect_type: str = ""
    rollback_plan_id: str = ""
    evidence_id: str = ""
    trace_id: str = ""
    record_id: str = ""


@dataclass
class ToolSideEffect:
    """Record of a side effect produced during tool execution."""

    effect_type: str = ""
    target: str = ""
    description: str = ""
    timestamp: str = ""
    severity: str = "info"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCallResponse:
    schema_version: str = "tool_call_v1"
    tool_name: str = ""
    capability: str = ""
    request_id: str = ""
    success: bool = False
    result: Any = None
    error: str = ""
    input_hash: str = ""
    output_hash: str = ""
    rollback_available: bool = False
    evidence_id: str = ""
    duration_ms: float = 0.0
    status: str = ""
    policy_decision_id: str = ""
    governance_decision_id: str = ""
    started_at: str = ""
    ended_at: str = ""
    artifact_ids: list[str] = field(default_factory=list)
    observation_id: str = ""
    side_effects: list[ToolSideEffect] = field(default_factory=list)
    trace_span_id: str = ""
    resource_usage: dict[str, Any] = field(default_factory=dict)


REQUIRED_SCHEMA_FIELDS = [
    "side_effect_class",
    "risk_level",
    "permission_scope",
    "rollback_behavior",
    "evidence_required",
]


def tool_schema_completeness_check(
    contract: ToolContract,
    trace_collector: list | None = None,
) -> list[str]:
    """Check that a tool contract has all required schema fields populated.
    Returns a list of missing/invalid field descriptions (empty = complete)."""
    issues: list[str] = []
    if not contract.side_effect_class:
        issues.append(f"tool '{contract.name}': missing side_effect_class")
    if contract.risk_level is None:
        issues.append(f"tool '{contract.name}': missing risk_level")
    if not contract.permission_scope:
        issues.append(f"tool '{contract.name}': missing permission_scope")
    if contract.side_effect_class != "read_only" and not contract.rollback_behavior:
        issues.append(f"tool '{contract.name}': missing rollback_behavior")
    if contract.side_effect_class != "read_only" and not contract.evidence_required:
        issues.append(f"tool '{contract.name}': missing evidence_required")

    return issues
