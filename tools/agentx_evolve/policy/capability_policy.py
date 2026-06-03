from __future__ import annotations

from .policy_models import CapabilityEntry, CapabilityPolicy, DECISION_ALLOW


def find_capability(
    role: str,
    tool_name: str,
    capability_policy: CapabilityPolicy,
) -> CapabilityEntry | None:
    for entry in capability_policy.capabilities:
        if entry.role == role and entry.tool_name == tool_name:
            return entry
    return None


def is_effect_allowed(
    effect: str,
    capability: CapabilityEntry,
    capability_policy: CapabilityPolicy,
) -> bool:
    if effect in capability_policy.blocked_effects:
        return False
    if capability is not None and effect in capability.blocked_effects:
        return False
    if capability is not None and effect in capability.allowed_effects:
        return True
    return capability_policy.default_decision == DECISION_ALLOW


def is_effect_blocked(
    effect: str,
    capability: CapabilityEntry | None,
    capability_policy: CapabilityPolicy,
) -> bool:
    if capability is None and effect in capability_policy.blocked_effects:
        return True
    if capability is not None and effect in capability.blocked_effects:
        return True
    return not is_effect_allowed(effect, capability, capability_policy)


def capability_requires_approval(
    effect: str,
    capability: CapabilityEntry,
    capability_policy: CapabilityPolicy,
) -> bool:
    return bool(effect in capability_policy.approval_required_effects or (capability and capability.requires_approval))


def capability_requires_governance(
    effect: str,
    capability: CapabilityEntry,
    capability_policy: CapabilityPolicy,
) -> bool:
    return bool(effect in capability_policy.governance_required_effects or (capability and capability.requires_governance))


def capability_requires_sandbox(
    effect: str,
    capability: CapabilityEntry,
    capability_policy: CapabilityPolicy,
) -> bool:
    return bool(effect in capability_policy.sandbox_required_effects or (capability and capability.requires_sandbox))
