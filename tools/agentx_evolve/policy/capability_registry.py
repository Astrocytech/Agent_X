from __future__ import annotations
from agentx_evolve.policy.policy_models import (
    CapabilityRegistry, ToolCapability, CapabilityDefinition, PolicyRule,
    RULE_ALLOW, RULE_DENY, RULE_REQUIRE_APPROVAL,
    new_id, utc_now_iso,
)


class CapabilityRegistryError(RuntimeError):
    pass


class CapabilityRegistryImpl:
    def __init__(self, registry: CapabilityRegistry | None = None):
        self._registry = registry or CapabilityRegistry(
            registry_id=new_id("registry"),
            timestamp=utc_now_iso(),
        )

    @property
    def registry(self) -> CapabilityRegistry:
        return self._registry

    def register_tool(self, tool: ToolCapability) -> ToolCapability:
        if not tool.tool_name:
            raise CapabilityRegistryError("Tool must have a name")
        if not tool.capabilities:
            raise CapabilityRegistryError(
                f"Tool '{tool.tool_name}' must define at least one capability"
            )
        self._registry.register_tool(tool)
        return tool

    def get_tool(self, tool_name: str) -> ToolCapability | None:
        if not tool_name:
            return None
        return self._registry.get_tool(tool_name)

    def get_tool_required(self, tool_name: str) -> ToolCapability:
        tool = self.get_tool(tool_name)
        if tool is None:
            raise CapabilityRegistryError(f"Unknown tool: {tool_name}")
        return tool

    def remove_tool(self, tool_name: str) -> bool:
        return self._registry.remove_tool(tool_name)

    def list_tools(self) -> list[ToolCapability]:
        return self._registry.list_tools()

    def list_enabled_tools(self) -> list[ToolCapability]:
        return self._registry.list_enabled_tools()

    def tool_count(self) -> int:
        return len(self._registry.tools)

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._registry.tools

    def enable_tool(self, tool_name: str) -> ToolCapability:
        tool = self.get_tool_required(tool_name)
        tool.enabled = True
        return tool

    def disable_tool(self, tool_name: str) -> ToolCapability:
        tool = self.get_tool_required(tool_name)
        tool.enabled = False
        return tool

    def add_global_rule(self, rule: PolicyRule) -> PolicyRule:
        if not rule.rule_id:
            rule.rule_id = new_id("rule")
        if not rule.timestamp:
            rule.timestamp = utc_now_iso()
        self._registry.global_rules.append(rule)
        return rule

    def remove_global_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self._registry.global_rules):
            if r.rule_id == rule_id:
                self._registry.global_rules.pop(i)
                return True
        return False

    def find_rules_by_operation(self, operation: str) -> list[PolicyRule]:
        return [
            r for r in self._registry.global_rules
            if r.operation == operation or r.operation == "*"
        ]

    def register_default_tools(self) -> list[ToolCapability]:
        defaults = _default_tools()
        for tool in defaults:
            tool.timestamp = utc_now_iso()
            self.register_tool(tool)
        return defaults


def _default_tools() -> list[ToolCapability]:
    return [
        ToolCapability(
            tool_name="safe_read_file",
            description="Read a file through the security sandbox",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-read-file",
                    name="file_read",
                    description="Read file contents",
                    allowed_operations=["READ"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="safe_write_file",
            description="Write a file through the security sandbox",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-write-file",
                    name="file_write",
                    description="Write file contents",
                    allowed_operations=["WRITE"],
                    side_effect_level="write",
                ),
            ],
            side_effect_level="write",
            requires_approval=True,
        ),
        ToolCapability(
            tool_name="safe_exact_edit",
            description="Edit a file via exact text replacement",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-edit-file",
                    name="file_edit",
                    description="Replace exact text in a file",
                    allowed_operations=["EDIT"],
                    side_effect_level="write",
                ),
            ],
            side_effect_level="write",
            requires_approval=True,
        ),
        ToolCapability(
            tool_name="check_subprocess_allowed",
            description="Check if a subprocess command is allowed",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-subprocess-check",
                    name="subprocess_check",
                    description="Validate subprocess command against policy",
                    allowed_operations=["EXECUTE"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="check_network_allowed",
            description="Check if a network request is allowed",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-network-check",
                    name="network_check",
                    description="Validate network target against policy",
                    allowed_operations=["NETWORK"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="apply_patch",
            description="Apply a governed source-code patch",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-patch-apply",
                    name="patch_apply",
                    description="Apply UPDATE/CREATE/DELETE patch",
                    allowed_operations=["EDIT", "WRITE", "DELETE"],
                    side_effect_level="write",
                ),
            ],
            side_effect_level="write",
            requires_approval=True,
        ),
        ToolCapability(
            tool_name="rollback_session",
            description="Roll back a governed implementation session",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-rollback",
                    name="session_rollback",
                    description="Restore files from rollback snapshots",
                    allowed_operations=["WRITE"],
                    side_effect_level="destructive",
                ),
            ],
            side_effect_level="destructive",
            requires_approval=True,
        ),
        ToolCapability(
            tool_name="validate_session",
            description="Run validation commands for a session",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-validate",
                    name="session_validate",
                    description="Execute allowlisted validation commands",
                    allowed_operations=["EXECUTE"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="git_diff_guard",
            description="Read-only git diff inspection",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-git-diff",
                    name="git_diff",
                    description="Run git diff commands (read-only)",
                    allowed_operations=["EXECUTE"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="check_path_boundary",
            description="Check whether a path is within the repository boundary",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-path-boundary",
                    name="path_boundary_check",
                    description="Validate path against repository boundary rules",
                    allowed_operations=["READ"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
        ToolCapability(
            tool_name="weather_fixture_read",
            description="Read deterministic weather fixture data for umbrella recommendation",
            capabilities=[
                CapabilityDefinition(
                    capability_id="cap-weather-fixture-read",
                    name="weather.fixture.read",
                    description="Read fixture-based weather data (deterministic, no network, no secrets)",
                    allowed_operations=["READ"],
                    side_effect_level="read",
                ),
            ],
            side_effect_level="read",
        ),
    ]


class EngineCapabilityRegistry:
    def __init__(self):
        self._impl = CapabilityRegistryImpl()
        self._impl.register_default_tools()

    @property
    def impl(self) -> CapabilityRegistryImpl:
        return self._impl

    @property
    def registry(self) -> CapabilityRegistry:
        return self._impl.registry
