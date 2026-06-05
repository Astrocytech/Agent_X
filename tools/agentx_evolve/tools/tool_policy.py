from __future__ import annotations

from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolDefinition,
    ToolPermissionDecision,
    ROLE_UNKNOWN_CALLER,
    TRUST_TIER_6_BLOCKED,
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_NEEDS_GOVERNANCE,
    DECISION_NEEDS_APPROVAL,
    DECISION_NEEDS_SANDBOX_CHECK,
    DECISION_NEEDS_DRY_RUN,
    utc_now_iso,
    new_id,
)


def check_tool_permission(
    tool_call: ToolCall,
    tool_definition: ToolDefinition,
    policy_context: dict,
) -> ToolPermissionDecision:
    decision_id = new_id("pol_")

    if not tool_definition.enabled:
        return _block(decision_id, tool_call, tool_definition, "Tool is disabled")

    if not tool_definition.allowlisted:
        return _block(decision_id, tool_call, tool_definition, "Tool is not allowlisted")

    if tool_call.caller_role == ROLE_UNKNOWN_CALLER:
        return _block(decision_id, tool_call, tool_definition, "Unknown caller role")

    if tool_definition.allowed_roles and tool_call.caller_role not in tool_definition.allowed_roles:
        return _block(decision_id, tool_call, tool_definition, f"Role {tool_call.caller_role} not allowed for this tool")

    if tool_definition.requested_effects and tool_call.requested_effect not in tool_definition.requested_effects:
        return _block(decision_id, tool_call, tool_definition, f"Effect {tool_call.requested_effect} not allowed for this tool")

    if tool_definition.trust_tier == TRUST_TIER_6_BLOCKED:
        return _block(decision_id, tool_call, tool_definition, "Tool is in blocked trust tier")

    if tool_definition.requires_governance and not tool_call.governance_decision_id:
        return _needs(decision_id, tool_call, tool_definition, DECISION_NEEDS_GOVERNANCE, "Governance decision required")

    if tool_definition.requires_human_approval and not tool_call.human_approval_id:
        return _needs(decision_id, tool_call, tool_definition, DECISION_NEEDS_APPROVAL, "Human approval required")

    if tool_definition.requires_dry_run and not tool_call.dry_run:
        return _needs(decision_id, tool_call, tool_definition, DECISION_NEEDS_DRY_RUN, "Dry run required")

    sandbox_decision_id = tool_call.sandbox_decision_id
    if tool_definition.requires_sandbox_check and not sandbox_decision_id:
        return _needs(decision_id, tool_call, tool_definition, DECISION_NEEDS_SANDBOX_CHECK, "Sandbox check required")

    policy_registry_available = policy_context.get("policy_registry_available", False)
    if tool_definition.requires_capability_policy and not policy_registry_available:
        provider_mode = policy_context.get("provider_mode", "local_only")
        if provider_mode == "local_only":
            writes_source = tool_definition.writes_source
            uses_network = tool_definition.uses_network
            runs_subprocess = tool_definition.runs_subprocess
            if writes_source:
                return _block(decision_id, tool_call, tool_definition, "Source write blocked: policy registry unavailable and provider mode is local_only")
            if uses_network:
                return _block(decision_id, tool_call, tool_definition, "Network tool blocked: policy registry unavailable")
            if runs_subprocess:
                return _block(decision_id, tool_call, tool_definition, "Subprocess tool blocked: policy registry unavailable")

    required_checks = []
    missing_checks = []
    if tool_definition.requires_sandbox_check:
        required_checks.append("sandbox")
        if not sandbox_decision_id:
            missing_checks.append("sandbox")
    if tool_definition.requires_governance:
        required_checks.append("governance")
        if not tool_call.governance_decision_id:
            missing_checks.append("governance")
    if tool_definition.requires_human_approval:
        required_checks.append("human_approval")
        if not tool_call.human_approval_id:
            missing_checks.append("human_approval")

    return ToolPermissionDecision(
        decision_id=decision_id,
        timestamp=utc_now_iso(),
        source_component="ToolPolicy",
        tool_name=tool_call.tool_name,
        caller_role=tool_call.caller_role,
        requested_effect=tool_call.requested_effect,
        decision=DECISION_ALLOW,
        reason="All checks passed",
        required_checks=required_checks,
        missing_checks=missing_checks,
    )


def _block(
    decision_id: str,
    tool_call: ToolCall,
    tool_definition: ToolDefinition,
    reason: str,
) -> ToolPermissionDecision:
    return ToolPermissionDecision(
        decision_id=decision_id,
        timestamp=utc_now_iso(),
        source_component="ToolPolicy",
        tool_name=tool_call.tool_name,
        caller_role=tool_call.caller_role,
        requested_effect=tool_call.requested_effect,
        decision=DECISION_BLOCK,
        reason=reason,
    )


def _needs(
    decision_id: str,
    tool_call: ToolCall,
    tool_definition: ToolDefinition,
    decision: str,
    reason: str,
) -> ToolPermissionDecision:
    return ToolPermissionDecision(
        decision_id=decision_id,
        timestamp=utc_now_iso(),
        source_component="ToolPolicy",
        tool_name=tool_call.tool_name,
        caller_role=tool_call.caller_role,
        requested_effect=tool_call.requested_effect,
        decision=decision,
        reason=reason,
    )
