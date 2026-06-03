from __future__ import annotations
import json
from pathlib import Path
from agentx_evolve.policy.policy_models import (
    CapabilityRegistry, ToolCapability, CapabilityDefinition,
    PolicyRule, PolicyEnforcementResult,
    to_dict, new_id, utc_now_iso,
)
from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl


class PolicyLoader:
    @staticmethod
    def load_registry_from_dict(data: dict) -> CapabilityRegistry:
        tools = {}
        for tool_data in data.get("tools", []):
            tool = _tool_from_dict(tool_data)
            tools[tool.tool_name] = tool

        global_rules = []
        for rule_data in data.get("global_rules", []):
            global_rules.append(_rule_from_dict(rule_data))

        return CapabilityRegistry(
            registry_id=data.get("registry_id", new_id("registry")),
            timestamp=data.get("timestamp", utc_now_iso()),
            tools=tools,
            global_rules=global_rules,
        )

    @staticmethod
    def load_registry_from_json(path: str | Path) -> CapabilityRegistry:
        path = Path(path)
        data = json.loads(path.read_text())
        return PolicyLoader.load_registry_from_dict(data)

    @staticmethod
    def dump_registry_to_dict(registry: CapabilityRegistry) -> dict:
        return registry.to_dict()

    @staticmethod
    def dump_registry_to_json(
        registry: CapabilityRegistry,
        path: str | Path,
        indent: int = 2,
    ) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(registry.to_dict(), indent=indent, default=str)
        )
        return path

    @staticmethod
    def load_impl_from_dict(
        data: dict,
    ) -> CapabilityRegistryImpl:
        registry = PolicyLoader.load_registry_from_dict(data)
        return CapabilityRegistryImpl(registry)

    @staticmethod
    def load_impl_from_json(
        path: str | Path,
    ) -> CapabilityRegistryImpl:
        registry = PolicyLoader.load_registry_from_json(path)
        return CapabilityRegistryImpl(registry)


def _tool_from_dict(data: dict) -> ToolCapability:
    caps = [_cap_from_dict(c) for c in data.get("capabilities", [])]
    rules = [_rule_from_dict(r) for r in data.get("policy_rules", [])]
    return ToolCapability(
        tool_id=data.get("tool_id", ""),
        timestamp=data.get("timestamp", utc_now_iso()),
        tool_name=data.get("tool_name", ""),
        description=data.get("description", ""),
        capabilities=caps,
        policy_rules=rules,
        enabled=data.get("enabled", True),
        requires_approval=data.get("requires_approval", False),
        side_effect_level=data.get("side_effect_level", "read"),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
    )


def _cap_from_dict(data: dict) -> CapabilityDefinition:
    return CapabilityDefinition(
        capability_id=data.get("capability_id", ""),
        timestamp=data.get("timestamp", utc_now_iso()),
        name=data.get("name", ""),
        description=data.get("description", ""),
        allowed_operations=data.get("allowed_operations", ["READ"]),
        side_effect_level=data.get("side_effect_level", "read"),
        requires_approval=data.get("requires_approval", False),
        rate_limit_per_minute=data.get("rate_limit_per_minute", 0),
        enabled=data.get("enabled", True),
        allowed_profiles=data.get("allowed_profiles", ["*"]),
    )


def _rule_from_dict(data: dict) -> PolicyRule:
    return PolicyRule(
        rule_id=data.get("rule_id", ""),
        timestamp=data.get("timestamp", utc_now_iso()),
        effect=data.get("effect", "DENY"),
        operation=data.get("operation", ""),
        target_pattern=data.get("target_pattern", ""),
        reason=data.get("reason", ""),
        priority=data.get("priority", 0),
        conditions=data.get("conditions", {}),
    )
