from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

ToolStatus = Literal["success", "failed", "blocked"]


def _generate_record_id() -> str:
    return f"event-tool-requested-{uuid.uuid4().hex[:8]}"


@dataclass(frozen=True)
class ToolRequest:
    schema_version: str = "tool_request_v1"
    run_id: str = ""
    profile_id: str = ""
    policy_id: str = ""
    decision_id: str = ""
    governance_decision_id: str = ""
    planner_decision_id: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "none"
    requires_approval: bool = False
    approval_token: str = ""
    source_phase: str = ""
    capability_id: str = ""
    target_resource: str = ""
    side_effect_type: str = ""
    trace_id: str = ""
    record_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = []
        if not self.run_id:
            missing.append("run_id")
        if not self.profile_id:
            missing.append("profile_id")
        if not self.policy_id:
            missing.append("policy_id")
        if not self.governance_decision_id:
            missing.append("governance_decision_id")
        if not self.tool_name:
            missing.append("tool_name")
        if not self.record_id:
            missing.append("record_id")
        if missing:
            raise ValueError(f"ToolRequest missing required fields: {', '.join(missing)}")


@dataclass(frozen=True)
class ToolResult:
    schema_version: str = "tool_result_v1"
    tool_name: str = ""
    status: ToolStatus = "success"
    output: str = ""
    error: str | None = None
    blocked_reason: str | None = None
    policy_decision_id: str = ""
    trace_id: str = ""
    risk_level: str = "none"
    metadata: dict[str, Any] = field(default_factory=dict)
