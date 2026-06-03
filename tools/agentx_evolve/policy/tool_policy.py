from __future__ import annotations

from .policy_models import ToolEntry, ToolPolicy, TRUST_TIER_6_BLOCKED


def find_tool(tool_name: str, tool_policy: ToolPolicy) -> ToolEntry | None:
    for entry in tool_policy.tools:
        if entry.tool_name == tool_name:
            return entry
    return None


def tool_exists(tool_name: str, tool_policy: ToolPolicy) -> bool:
    return find_tool(tool_name, tool_policy) is not None


def tool_is_blocked(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return True
    return entry.blocked


def tool_allows_effect(tool_name: str, effect: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return effect in entry.requested_effects


def tool_requires_governance(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.requires_governance


def tool_requires_sandbox(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.requires_sandbox


def tool_requires_human_approval(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.requires_human_approval


def tool_uses_network(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.uses_network


def tool_executes_command(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.executes_command


def tool_writes_source(tool_name: str, tool_policy: ToolPolicy) -> bool:
    entry = find_tool(tool_name, tool_policy)
    if entry is None:
        return False
    return entry.writes_source
