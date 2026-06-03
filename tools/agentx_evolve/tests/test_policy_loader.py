import json
import tempfile
from pathlib import Path
from agentx_evolve.policy.policy_loader import PolicyLoader, _tool_from_dict, _cap_from_dict, _rule_from_dict
from agentx_evolve.policy.policy_models import (
    CapabilityRegistry, ToolCapability, CapabilityDefinition, PolicyRule,
    OP_READ, OP_WRITE, RULE_ALLOW, RULE_DENY,
)


class TestToolFromDict:
    def test_minimal(self):
        data = {"tool_name": "test_tool"}
        tool = _tool_from_dict(data)
        assert tool.tool_name == "test_tool"
        assert tool.enabled is True
        assert tool.capabilities == []

    def test_full(self):
        data = {
            "tool_id": "t1",
            "tool_name": "my_tool",
            "description": "A tool",
            "enabled": False,
            "requires_approval": True,
            "side_effect_level": "write",
            "capabilities": [{"name": "cap1", "allowed_operations": ["READ"]}],
            "policy_rules": [{"rule_id": "r1", "effect": "DENY", "operation": "WRITE"}],
        }
        tool = _tool_from_dict(data)
        assert tool.tool_id == "t1"
        assert tool.enabled is False
        assert len(tool.capabilities) == 1
        assert len(tool.policy_rules) == 1


class TestCapFromDict:
    def test_minimal(self):
        cap = _cap_from_dict({"name": "test"})
        assert cap.name == "test"
        assert cap.allowed_operations == ["READ"]

    def test_custom(self):
        cap = _cap_from_dict({
            "name": "write",
            "allowed_operations": ["WRITE"],
            "allowed_profiles": ["admin"],
            "requires_approval": True,
        })
        assert cap.allowed_operations == ["WRITE"]
        assert cap.allowed_profiles == ["admin"]


class TestRuleFromDict:
    def test_minimal(self):
        rule = _rule_from_dict({"rule_id": "r1"})
        assert rule.rule_id == "r1"
        assert rule.effect == "DENY"

    def test_custom(self):
        rule = _rule_from_dict({
            "rule_id": "r2", "effect": "ALLOW", "operation": "READ",
            "priority": 10, "reason": "test reason",
        })
        assert rule.effect == RULE_ALLOW
        assert rule.priority == 10


class TestPolicyLoader:
    def test_load_registry_from_dict_empty(self):
        registry = PolicyLoader.load_registry_from_dict({})
        assert isinstance(registry, CapabilityRegistry)
        assert registry.tools == {}
        assert registry.global_rules == []

    def test_load_registry_from_dict_with_tools(self):
        data = {
            "registry_id": "reg-1",
            "tools": [
                {"tool_name": "tool_a", "capabilities": [{"name": "read", "allowed_operations": ["READ"]}]},
                {"tool_name": "tool_b", "capabilities": [{"name": "write", "allowed_operations": ["WRITE"]}]},
            ],
            "global_rules": [
                {"rule_id": "gr1", "effect": "DENY", "operation": "DELETE"},
            ],
        }
        registry = PolicyLoader.load_registry_from_dict(data)
        assert len(registry.tools) == 2
        assert registry.tools["tool_a"].tool_name == "tool_a"
        assert len(registry.global_rules) == 1

    def test_load_registry_from_json(self):
        data = {"tools": [{"tool_name": "t1", "capabilities": []}]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            registry = PolicyLoader.load_registry_from_json(path)
            assert "t1" in registry.tools
        finally:
            Path(path).unlink()

    def test_dump_registry_to_dict(self):
        registry = PolicyLoader.load_registry_from_dict({
            "tools": [{"tool_name": "dump_tool", "capabilities": [{"name": "c1"}]}],
        })
        dumped = PolicyLoader.dump_registry_to_dict(registry)
        assert "tools" in dumped
        assert "registry_id" in dumped

    def test_dump_registry_to_json(self):
        registry = PolicyLoader.load_registry_from_dict({
            "tools": [{"tool_name": "json_tool", "capabilities": [{"name": "c1"}]}],
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            result = PolicyLoader.dump_registry_to_json(registry, path)
            assert result == path
            assert path.exists()
            loaded = json.loads(path.read_text())
            assert "tools" in loaded

    def test_load_impl_from_dict(self):
        impl = PolicyLoader.load_impl_from_dict({
            "tools": [{"tool_name": "t1", "capabilities": [{"name": "read", "allowed_operations": ["READ"]}]}],
        })
        tool = impl.get_tool("t1")
        assert tool is not None
        assert tool.tool_name == "t1"
