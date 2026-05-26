"""Tool Registry — single canonical registry authority for L0 tools."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

import jsonschema

from tool_gateway.tool_contracts import (
    ToolContract,
    tool_schema_completeness_check,
)


@dataclass
class ToolDescriptor:
    tool_id: str = ""
    name: str = ""
    version: str = ""
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    policy_id: str = ""
    resource_limit_id: str = ""
    evaluation_hook_ids: list[str] = field(default_factory=list)
    allowed_profile_ids: list[str] = field(default_factory=list)
    side_effect_level: str = "read"
    enabled: bool = True


class ToolRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolGovernance:
    tool_id: str
    policy_id: str
    resource_limit_id: str
    evaluation_hook_ids: list[str]
    allowed_profile_ids: list[str]
    side_effect_level: str
    enabled: bool


class ToolStats:
    def __init__(self) -> None:
        self.executions = 0
        self.failures = 0
        self.total_latency_ms = 0.0
        self.last_used: float | None = None

    @property
    def success_rate(self) -> float | None:
        if self.executions == 0:
            return None
        return 1.0 - (self.failures / self.executions)

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.executions if self.executions else 0.0


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolContract] = {}
        self._handlers: dict[str, Callable] = {}
        self._stats: dict[str, ToolStats] = {}
        self._deprecated: set[str] = set()
        self._descriptors: dict[str, ToolDescriptor] = {}

    def register(self, contract: ToolContract, handler: Callable) -> None:
        if not contract.name:
            raise ValueError("Tool must have a name")
        if handler is None:
            raise ValueError("Tool must have a handler")
        issues = tool_schema_completeness_check(contract)
        if issues:
            raise ToolRegistryError(
                f"Cannot register tool '{contract.name}': incomplete contract: {'; '.join(issues)}"
            )
        self._tools[contract.name] = contract
        self._handlers[contract.name] = handler
        self._stats[contract.name] = ToolStats()

    def get_contract(self, name: str) -> ToolContract | None:
        if not name:
            return None
        return self._tools.get(name)

    def get_handler(self, name: str) -> Callable | None:
        if not name:
            return None
        return self._handlers.get(name)

    def list_tools(self) -> list[ToolContract]:
        return list(self._tools.values())

    def enable(self, name: str) -> bool:
        tool = self._tools.get(name)
        if tool:
            tool.enabled = True
            return True
        return False

    def disable(self, name: str) -> bool:
        tool = self._tools.get(name)
        if tool:
            tool.enabled = False
            return True
        return False

    def record_execution(self, name: str, latency_ms: float, success: bool) -> None:
        stats = self._stats.get(name)
        if stats:
            stats.executions += 1
            stats.total_latency_ms += latency_ms
            stats.last_used = time.monotonic()
            if not success:
                stats.failures += 1

    def get_stats(self, name: str) -> ToolStats | None:
        return self._stats.get(name)

    def search_by_risk(self, risk_level: str) -> list[ToolContract]:
        return [t for t in self._tools.values() if t.risk_level.value == risk_level and t.enabled]

    def search_by_tag(self, tag: str) -> list[ToolContract]:
        return [t for t in self._tools.values() if tag in getattr(t, "tags", []) and t.enabled]

    def mark_deprecated(self, name: str, replacement: str | None = None) -> bool:
        if name not in self._tools:
            return False
        self._deprecated.add(name)
        if replacement:
            self._tools[name].metadata = self._tools[name].metadata or {}
            self._tools[name].metadata["deprecated_replacement"] = replacement
        return True

    def is_deprecated(self, name: str) -> bool:
        return name in self._deprecated

    def list_active_tools(self) -> list[ToolContract]:
        return [t for t in self._tools.values() if t.enabled and not self.is_deprecated(t.name)]

    def unregister(self, name: str) -> bool:
        removed = False
        if name in self._tools:
            del self._tools[name]
            removed = True
        if name in self._handlers:
            del self._handlers[name]
        if name in self._stats:
            del self._stats[name]
        if name in self._descriptors:
            del self._descriptors[name]
        self._deprecated.discard(name)
        return removed

    def register_tool(self, descriptor: ToolDescriptor) -> None:
        if descriptor.tool_id in self._descriptors:
            existing = self._descriptors[descriptor.tool_id]
            if existing.enabled:
                raise ToolRegistryError(f"Tool '{descriptor.tool_id}' already registered")
        self._descriptors[descriptor.tool_id] = descriptor

    def get_tool(self, tool_id: str) -> ToolDescriptor:
        if tool_id not in self._descriptors:
            raise ToolRegistryError(f"Unknown tool: {tool_id}")
        return self._descriptors[tool_id]

    def disable_tool(self, tool_id: str, reason: str) -> None:
        if tool_id not in self._descriptors:
            raise ToolRegistryError(f"Unknown tool: {tool_id}")
        desc = self._descriptors[tool_id]
        self._descriptors[tool_id] = ToolDescriptor(
            tool_id=desc.tool_id, name=desc.name, version=desc.version,
            description=desc.description, input_schema=desc.input_schema,
            output_schema=desc.output_schema, policy_id=desc.policy_id,
            resource_limit_id=desc.resource_limit_id, evaluation_hook_ids=desc.evaluation_hook_ids,
            allowed_profile_ids=desc.allowed_profile_ids,
            side_effect_level=desc.side_effect_level, enabled=False,
        )

    def validate_tool_request(self, profile_id: str, tool_id: str, arguments: dict[str, Any]) -> ToolDescriptor:
        desc = self.get_tool(tool_id)
        if not desc.enabled:
            raise ToolRegistryError(f"Tool '{tool_id}' is disabled")
        if "*" not in desc.allowed_profile_ids and profile_id not in desc.allowed_profile_ids:
            raise ToolRegistryError(f"Profile '{profile_id}' not allowed to use tool '{tool_id}'")
        if desc.input_schema:
            try:
                jsonschema.validate(instance=arguments or {}, schema=desc.input_schema)
            except jsonschema.ValidationError as e:
                raise ToolRegistryError(f"Argument validation failed for '{tool_id}': {e.message}")
        return desc

    def update_tool(self, tool_id: str, descriptor: ToolDescriptor) -> None:
        if tool_id not in self._descriptors:
            raise ToolRegistryError(f"Unknown tool: {tool_id}")
        self._descriptors[tool_id] = descriptor

    def register_policy(self, tool_id: str, policy_id: str) -> None:
        desc = self.get_tool(tool_id)
        self._descriptors[tool_id] = ToolDescriptor(
            tool_id=desc.tool_id, name=desc.name, version=desc.version,
            description=desc.description, input_schema=desc.input_schema,
            output_schema=desc.output_schema, policy_id=policy_id,
            resource_limit_id=desc.resource_limit_id, evaluation_hook_ids=list(desc.evaluation_hook_ids),
            allowed_profile_ids=list(desc.allowed_profile_ids),
            side_effect_level=desc.side_effect_level, enabled=desc.enabled,
        )

    def register_resource_limit(self, tool_id: str, resource_limit_id: str) -> None:
        desc = self.get_tool(tool_id)
        self._descriptors[tool_id] = ToolDescriptor(
            tool_id=desc.tool_id, name=desc.name, version=desc.version,
            description=desc.description, input_schema=desc.input_schema,
            output_schema=desc.output_schema, policy_id=desc.policy_id,
            resource_limit_id=resource_limit_id, evaluation_hook_ids=list(desc.evaluation_hook_ids),
            allowed_profile_ids=list(desc.allowed_profile_ids),
            side_effect_level=desc.side_effect_level, enabled=desc.enabled,
        )

    def register_evaluation_hook(self, tool_id: str, hook_id: str) -> None:
        desc = self.get_tool(tool_id)
        new_hooks = list(desc.evaluation_hook_ids)
        if hook_id not in new_hooks:
            new_hooks.append(hook_id)
        self._descriptors[tool_id] = ToolDescriptor(
            tool_id=desc.tool_id, name=desc.name, version=desc.version,
            description=desc.description, input_schema=desc.input_schema,
            output_schema=desc.output_schema, policy_id=desc.policy_id,
            resource_limit_id=desc.resource_limit_id, evaluation_hook_ids=new_hooks,
            allowed_profile_ids=list(desc.allowed_profile_ids),
            side_effect_level=desc.side_effect_level, enabled=desc.enabled,
        )

    def get_governance(self, tool_id: str) -> ToolGovernance:
        desc = self.get_tool(tool_id)
        return ToolGovernance(
            tool_id=desc.tool_id, policy_id=desc.policy_id,
            resource_limit_id=desc.resource_limit_id, evaluation_hook_ids=list(desc.evaluation_hook_ids),
            allowed_profile_ids=list(desc.allowed_profile_ids),
            side_effect_level=desc.side_effect_level, enabled=desc.enabled,
        )

    def list_tools_for_profile(self, profile_id: str) -> list[ToolDescriptor]:
        result = []
        for desc in self._descriptors.values():
            if not desc.enabled:
                continue
            if "*" in desc.allowed_profile_ids or profile_id in desc.allowed_profile_ids:
                result.append(desc)
        return result
