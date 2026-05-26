"""Seed-owned governance contracts — data models for governance decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


GOVERNANCE_STATES = frozenset({
    "allowed",
    "denied",
    "approval_required",
})

GOVERNANCE_DENIAL_REASONS = frozenset({
    "unknown_tool_denied",
    "tool_not_allowed_by_profile",
    "tool_not_available_in_runtime_mode",
    "forbidden_platform_tool",
    "risk_policy_denied",
    "uncertified_tool_denied",
})

GOVERNANCE_DECISION_STATES = GOVERNANCE_STATES


@dataclass
class GovernanceAction:
    action_type: str = ""
    action_category: str = ""
    action_name: str = ""
    tool_name: str = ""
    tool_group: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"


@dataclass
class PolicyContext:
    profile_id: str = ""
    task_type: str = ""
    goal_text: str = ""
    run_id: str = ""


@dataclass
class PortGovernanceAction:
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    profile_id: str = ""
    policy_id: str = ""
    target_resource: str = ""
    run_id: str = ""


@dataclass
class GovernanceContext:
    run_id: str = ""
    profile_id: str = ""
    policy_id: str = ""
    goal_text: str = ""
    tool_name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    target_resource: str = ""
    evidence_refs: list[str] = field(default_factory=list)


@dataclass
class GovernanceRequest:
    action_category: str = ""
    action_name: str = ""
    profile_id: str = ""
    client_id: str = ""
    run_id: str = ""
    task_id: str = ""
    target: str = ""
    risk_level: str = "low"
    effective_policy_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    action: GovernanceAction | None = None


@dataclass
class GovernanceDecision:
    governance_decision_id: str = ""
    allowed: bool = False
    reason: str = ""
    requires_approval: bool = False
    risk_level: str = "low"
    decision_id: str = ""
    action_type: str = ""
    profile_id: str = ""
    session_id: str = ""
    policy_hash: str = ""
    trace_span_id: str = ""
    policy_refs: list[str] = field(default_factory=list)
    engine_results: list[dict] = field(default_factory=list)
    evaluated_at: str = ""
    run_id: str = ""
    task_id: str = ""
    requested_action: str = ""
    requested_resource: str = ""
    requires_human: bool = False
    policy_ids: list[str] = field(default_factory=list)
    created_at: str = ""
    denial_reason: str = ""


@dataclass(frozen=True)
class RiskAssessment:
    tool_name: str = ""
    tool_args_hash: str = ""
    risk_level: str = ""
    approval_required: bool = False
    matched_rules: tuple[str, ...] = ()
    protected_path_touched: bool = False
    reason: str = ""
