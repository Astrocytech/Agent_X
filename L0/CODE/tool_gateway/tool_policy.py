from __future__ import annotations

"""Tool Gateway Policy — enforces tool access rules per profile."""


from profiles.agent_profile_schema import AgentProfileSchema  # noqa: E402
from tool_gateway.tool_contracts import ToolRiskLevel  # noqa: E402
from tool_gateway.tool_registry import ToolRegistry  # noqa: E402

__all__ = ["ToolPolicy"]


class ToolPolicy:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def is_allowed(self, tool_name: str, profile: AgentProfileSchema) -> tuple[bool, str]:
        if not tool_name:
            return False, "Tool name cannot be empty"
        if not profile:
            return False, "Profile cannot be None"
        contract = self.registry.get_contract(tool_name)
        if not contract:
            return False, f"Tool not found: {tool_name}"
        if not contract.enabled:
            return False, f"Tool disabled: {tool_name}"
        if contract.transport == "mcp":
            if not contract.metadata.get("server_id"):
                return False, f"MCP tool missing server_id metadata: {tool_name}"
            if contract.metadata.get("requires_schema_validation") is not True:
                return (
                    False,
                    f"MCP tool missing schema-validation requirement: {tool_name}",
                )
            if contract.metadata.get("requires_output_sanitization") is not True:
                return (
                    False,
                    f"MCP tool missing output-sanitization requirement: {tool_name}",
                )
        if profile.forbidden_tools and tool_name in profile.forbidden_tools:
            return False, f"Tool forbidden for profile: {tool_name}"
        allowed_scopes = contract.allowed_scopes or []
        wildcard_scoped = "*" in allowed_scopes
        if profile.allowed_tools and tool_name not in profile.allowed_tools and not wildcard_scoped:
            return False, f"Tool not allowed for profile: {tool_name}"
        profile_id = getattr(profile, "id", "") or getattr(profile, "profile_id", "")
        if allowed_scopes and not wildcard_scoped and profile_id not in allowed_scopes:
            return False, f"Tool scope does not allow profile: {profile_id}"
        return True, ""

    def requires_approval(self, tool_name: str) -> bool:
        contract = self.registry.get_contract(tool_name)
        return contract.requires_approval if contract else False

    def get_risk_level(self, tool_name: str) -> ToolRiskLevel:
        contract = self.registry.get_contract(tool_name)
        if not contract:
            return ToolRiskLevel.CRITICAL
        if contract.transport == "mcp" and contract.risk_level.value in (
            "low",
            "medium",
        ):
            return ToolRiskLevel.HIGH
        return contract.risk_level
