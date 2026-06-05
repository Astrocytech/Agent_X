from __future__ import annotations

from .capability_policy import (
    find_capability, is_effect_allowed, is_effect_blocked,
    capability_requires_approval, capability_requires_governance, capability_requires_sandbox,
)
from .tool_policy import (
    find_tool, tool_exists, tool_is_blocked, tool_allows_effect,
    tool_requires_governance, tool_requires_sandbox, tool_requires_human_approval,
    tool_uses_network, tool_executes_command, tool_writes_source,
)
from .model_policy import (
    find_model_profile, model_profile_exists, model_task_allowed,
    model_may_read_source, model_may_write_files, model_may_execute_tools,
    model_may_execute_commands, model_may_use_network,
)
from .role_matrix import is_valid_role
from .policy_models import (
    DECISION_ALLOW, DECISION_BLOCK, DECISION_INVALID_POLICY,
    DECISION_NEEDS_APPROVAL, DECISION_NEEDS_GOVERNANCE, DECISION_NEEDS_RISK_REVIEW,
    DECISION_NEEDS_SANDBOX_CHECK, DECISION_NEEDS_VALIDATION,
    DECISION_UNKNOWN_MODEL, DECISION_UNKNOWN_ROLE, DECISION_UNKNOWN_TOOL, DECISION_WARN,
    PolicyDecision, CapabilityPolicy, ToolPolicy, ModelPolicy,
    REASON_ALLOW_BY_CAPABILITY, REASON_CAPABILITY_EFFECT_BLOCKED, REASON_CAPABILITY_MISSING,
    REASON_DEFAULT_BLOCK, REASON_GIT_WRITE_BLOCKED_BY_DEFAULT,
    REASON_HOSTED_MODEL_BLOCKED_BY_DEFAULT, REASON_HUMAN_CANNOT_OVERRIDE_HARD_BLOCK,
    REASON_INVALID_POLICY, REASON_MODEL_CANNOT_EXECUTE_COMMANDS,
    REASON_MODEL_CANNOT_EXECUTE_TOOLS, REASON_MODEL_CANNOT_WRITE_FILES,
    REASON_NETWORK_BLOCKED_BY_DEFAULT, REASON_REQUIRES_APPROVAL, REASON_REQUIRES_GOVERNANCE,
    REASON_REQUIRES_RISK_REVIEW, REASON_REQUIRES_SANDBOX, REASON_REQUIRES_VALIDATION,
    REASON_SANDBOX_BLOCK_IS_AUTHORITATIVE, REASON_TOOL_BLOCKED, REASON_TOOL_EFFECT_NOT_ALLOWED,
    REASON_UNKNOWN_EFFECT, REASON_UNKNOWN_MODEL, REASON_UNKNOWN_ROLE, REASON_UNKNOWN_TOOL,
    EFFECT_READ, EFFECT_WRITE_RUNTIME, EFFECT_WRITE_SOURCE, EFFECT_EDIT_SOURCE,
    EFFECT_PATCH_PRECHECK, EFFECT_PATCH_APPLY, EFFECT_EXECUTE_COMMAND, EFFECT_USE_MODEL,
    EFFECT_USE_NETWORK, EFFECT_READ_GIT, EFFECT_WRITE_GIT, EFFECT_REQUEST_APPROVAL,
    EFFECT_PROMOTE, EFFECT_ROLLBACK, EFFECT_AUDIT_WRITE, EFFECT_GRAPH_WRITE, EFFECT_MEMORY_WRITE,
    new_id, utc_now_iso,
)


DECISION_PRIORITY: dict[str, int] = {
    DECISION_INVALID_POLICY: 0,
    DECISION_UNKNOWN_ROLE: 1,
    DECISION_UNKNOWN_TOOL: 2,
    DECISION_UNKNOWN_MODEL: 3,
    DECISION_BLOCK: 4,
    DECISION_NEEDS_APPROVAL: 5,
    DECISION_NEEDS_GOVERNANCE: 6,
    DECISION_NEEDS_SANDBOX_CHECK: 7,
    DECISION_NEEDS_RISK_REVIEW: 8,
    DECISION_NEEDS_VALIDATION: 9,
    DECISION_WARN: 10,
    DECISION_ALLOW: 11,
}


def choose_strictest_decision(decisions: list[PolicyDecision]) -> PolicyDecision:
    decisions = [d for d in decisions if d is not None]
    if not decisions:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=utc_now_iso(),
            decision=DECISION_BLOCK,
            reason=REASON_DEFAULT_BLOCK,
        )
    best = decisions[0]
    best_priority = DECISION_PRIORITY.get(best.decision, 0)
    for d in decisions[1:]:
        p = DECISION_PRIORITY.get(d.decision, 0)
        if p < best_priority:
            best = d
            best_priority = p
    return best


def evaluate_tool_request(
    caller_role: str,
    tool_name: str,
    requested_effect: str,
    target: str | None,
    capability_policy: CapabilityPolicy,
    tool_policy: ToolPolicy,
    model_policy: ModelPolicy | None = None,
) -> PolicyDecision:
    now = utc_now_iso()

    if capability_policy is None or tool_policy is None:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_INVALID_POLICY,
            reason=REASON_INVALID_POLICY,
        )

    if not is_valid_role(caller_role):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_UNKNOWN_ROLE,
            reason=REASON_UNKNOWN_ROLE,
        )

    tool = find_tool(tool_name, tool_policy)
    if tool is None:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_UNKNOWN_TOOL,
            reason=REASON_UNKNOWN_TOOL,
        )

    if tool_is_blocked(tool_name, tool_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_TOOL_BLOCKED,
        )

    standard_effects = {
        EFFECT_READ, EFFECT_WRITE_RUNTIME, EFFECT_WRITE_SOURCE, EFFECT_EDIT_SOURCE,
        EFFECT_PATCH_PRECHECK, EFFECT_PATCH_APPLY, EFFECT_EXECUTE_COMMAND, EFFECT_USE_MODEL,
        EFFECT_USE_NETWORK, EFFECT_READ_GIT, EFFECT_WRITE_GIT, EFFECT_REQUEST_APPROVAL,
        EFFECT_PROMOTE, EFFECT_ROLLBACK, EFFECT_AUDIT_WRITE, EFFECT_GRAPH_WRITE, EFFECT_MEMORY_WRITE,
    }
    if requested_effect not in standard_effects:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_UNKNOWN_EFFECT,
        )

    if not tool_allows_effect(tool_name, requested_effect, tool_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_TOOL_EFFECT_NOT_ALLOWED,
        )

    cap = find_capability(caller_role, tool_name, capability_policy)
    if cap is None and requested_effect in capability_policy.blocked_effects:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_CAPABILITY_EFFECT_BLOCKED,
        )

    if is_effect_blocked(requested_effect, cap, capability_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_CAPABILITY_EFFECT_BLOCKED,
        )

    followups: list[str] = []

    if requested_effect == EFFECT_WRITE_GIT:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_GIT_WRITE_BLOCKED_BY_DEFAULT,
        )

    if requested_effect == EFFECT_USE_NETWORK and not tool_uses_network(tool_name, tool_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_BLOCK,
            reason=REASON_NETWORK_BLOCKED_BY_DEFAULT,
        )

    if requested_effect in (EFFECT_WRITE_SOURCE, EFFECT_PATCH_APPLY):
        followups.append("governance_approval")
        followups.append("sandbox_check")

    if requested_effect == EFFECT_EXECUTE_COMMAND:
        followups.append("sandbox_check")

    if tool_requires_human_approval(tool_name, tool_policy) or capability_requires_approval(requested_effect, cap, capability_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_NEEDS_APPROVAL,
            reason=REASON_REQUIRES_APPROVAL,
            required_followups=followups,
        )

    if tool_requires_governance(tool_name, tool_policy) or capability_requires_governance(requested_effect, cap, capability_policy):
        if "governance_approval" not in followups:
            followups.append("governance_approval")
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_NEEDS_GOVERNANCE,
            reason=REASON_REQUIRES_GOVERNANCE,
            required_followups=followups,
        )

    if tool_requires_sandbox(tool_name, tool_policy) or capability_requires_sandbox(requested_effect, cap, capability_policy):
        if "sandbox_check" not in followups:
            followups.append("sandbox_check")
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            target=target,
            decision=DECISION_NEEDS_SANDBOX_CHECK,
            reason=REASON_REQUIRES_SANDBOX,
            required_followups=followups,
        )

    return PolicyDecision(
        decision_id=new_id("pd"),
        timestamp=now,
        caller_role=caller_role,
        tool_name=tool_name,
        requested_effect=requested_effect,
        target=target,
        decision=DECISION_ALLOW,
        reason=REASON_ALLOW_BY_CAPABILITY,
    )


def evaluate_model_request(
    caller_role: str,
    model_profile_id: str,
    task_type: str,
    model_policy: ModelPolicy,
    capability_policy: CapabilityPolicy,
) -> PolicyDecision:
    now = utc_now_iso()

    if model_policy is None:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_INVALID_POLICY,
            reason=REASON_INVALID_POLICY,
        )

    if not is_valid_role(caller_role):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_UNKNOWN_ROLE,
            reason=REASON_UNKNOWN_ROLE,
        )

    profile = find_model_profile(model_profile_id, model_policy)
    if profile is None:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_UNKNOWN_MODEL,
            reason=REASON_UNKNOWN_MODEL,
        )

    if not profile.local_only:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_BLOCK,
            reason=REASON_HOSTED_MODEL_BLOCKED_BY_DEFAULT,
        )

    if not model_task_allowed(model_profile_id, task_type, model_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_BLOCK,
            reason=REASON_DEFAULT_BLOCK,
        )

    if model_may_write_files(model_profile_id, model_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_BLOCK,
            reason=REASON_MODEL_CANNOT_WRITE_FILES,
        )

    if model_may_execute_commands(model_profile_id, model_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_BLOCK,
            reason=REASON_MODEL_CANNOT_EXECUTE_COMMANDS,
        )

    if model_may_execute_tools(model_profile_id, model_policy):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_BLOCK,
            reason=REASON_MODEL_CANNOT_EXECUTE_TOOLS,
        )

    if profile.requires_human_approval:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=model_profile_id,
            requested_effect=EFFECT_USE_MODEL,
            decision=DECISION_NEEDS_APPROVAL,
            reason=REASON_REQUIRES_APPROVAL,
        )

    return PolicyDecision(
        decision_id=new_id("pd"),
        timestamp=now,
        caller_role=caller_role,
        tool_name=model_profile_id,
        requested_effect=EFFECT_USE_MODEL,
        decision=DECISION_ALLOW,
        reason=REASON_ALLOW_BY_CAPABILITY,
    )


def check_role_permission(
    caller_role: str,
    tool_name: str,
    requested_effect: str,
    capability_policy: CapabilityPolicy,
) -> PolicyDecision:
    now = utc_now_iso()

    if not is_valid_role(caller_role):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            decision=DECISION_UNKNOWN_ROLE,
            reason=REASON_UNKNOWN_ROLE,
        )

    cap = find_capability(caller_role, tool_name, capability_policy)
    if cap is None:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            decision=DECISION_BLOCK,
            reason=REASON_CAPABILITY_MISSING,
        )

    if (requested_effect in capability_policy.blocked_effects or
            (hasattr(cap, 'blocked_effects') and requested_effect in cap.blocked_effects)):
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            decision=DECISION_BLOCK,
            reason=REASON_CAPABILITY_EFFECT_BLOCKED,
        )

    if hasattr(cap, 'allowed_effects') and requested_effect in cap.allowed_effects:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            decision=DECISION_ALLOW,
            reason=REASON_ALLOW_BY_CAPABILITY,
        )

    default_decision = getattr(cap, 'default_decision', DECISION_BLOCK)
    if default_decision == DECISION_ALLOW:
        return PolicyDecision(
            decision_id=new_id("pd"),
            timestamp=now,
            caller_role=caller_role,
            tool_name=tool_name,
            requested_effect=requested_effect,
            decision=DECISION_ALLOW,
            reason=REASON_ALLOW_BY_CAPABILITY,
        )

    return PolicyDecision(
        decision_id=new_id("pd"),
        timestamp=now,
        caller_role=caller_role,
        tool_name=tool_name,
        requested_effect=requested_effect,
        decision=DECISION_BLOCK,
        reason=REASON_DEFAULT_BLOCK,
    )
