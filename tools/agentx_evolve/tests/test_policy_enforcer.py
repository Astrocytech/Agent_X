import pytest
from agentx_evolve.policy.policy_models import (
    ToolCapability, CapabilityDefinition, CapabilityRegistry,
    PolicyRule, PolicyEnforcementResult,
    ENFORCEMENT_ALLOW, ENFORCEMENT_BLOCK, ENFORCEMENT_REQUIRE_APPROVAL,
    RULE_ALLOW, RULE_DENY, RULE_REQUIRE_APPROVAL,
    OP_READ, OP_WRITE, OP_EDIT,
)
from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl
from agentx_evolve.policy.policy_enforcer import PolicyEnforcer


class TestPolicyEnforcer:
    def _make_registry(self) -> CapabilityRegistryImpl:
        impl = CapabilityRegistryImpl()
        tool = ToolCapability(
            tool_id="t1",
            tool_name="safe_read",
            description="Read files",
            capabilities=[
                CapabilityDefinition(
                    capability_id="c1", name="read",
                    allowed_operations=[OP_READ],
                ),
            ],
            side_effect_level="read",
        )
        impl.register_tool(tool)
        return impl

    def _make_registry_restricted(self) -> CapabilityRegistryImpl:
        impl = CapabilityRegistryImpl()
        tool = ToolCapability(
            tool_id="t2",
            tool_name="restricted_tool",
            description="Restricted tool",
            capabilities=[
                CapabilityDefinition(
                    capability_id="c2", name="write",
                    allowed_operations=[OP_WRITE],
                    allowed_profiles=["admin"],
                ),
            ],
            side_effect_level="write",
        )
        impl.register_tool(tool)
        return impl

    def test_enforce_unknown_tool_returns_blocked(self):
        enforcer = PolicyEnforcer(self._make_registry())
        result = enforcer.enforce("unknown_tool", OP_READ)
        assert result.decision == ENFORCEMENT_BLOCK
        assert "not registered" in result.reason

    def test_enforce_disabled_tool_returns_blocked(self):
        impl = self._make_registry()
        tool = impl.get_tool("safe_read")
        tool.enabled = False
        enforcer = PolicyEnforcer(impl)
        result = enforcer.enforce("safe_read", OP_READ)
        assert result.decision == ENFORCEMENT_BLOCK
        assert "disabled" in result.reason

    def test_enforce_allowed(self):
        enforcer = PolicyEnforcer(self._make_registry())
        result = enforcer.enforce("safe_read", OP_READ)
        assert result.decision == ENFORCEMENT_ALLOW

    def test_enforce_rule_deny_overrides(self):
        impl = self._make_registry()
        tool = impl.get_tool("safe_read")
        tool.policy_rules.append(PolicyRule(
            rule_id="r1", effect=RULE_DENY, operation=OP_READ,
        ))
        enforcer = PolicyEnforcer(impl)
        result = enforcer.enforce("safe_read", OP_READ)
        assert result.decision == ENFORCEMENT_BLOCK
        assert result.matched_rule_id == "r1"

    def test_enforce_rule_require_approval(self):
        impl = self._make_registry()
        tool = impl.get_tool("safe_read")
        tool.policy_rules.append(PolicyRule(
            rule_id="r2", effect=RULE_REQUIRE_APPROVAL, operation=OP_READ,
        ))
        enforcer = PolicyEnforcer(impl)
        result = enforcer.enforce("safe_read", OP_READ)
        assert result.decision == ENFORCEMENT_REQUIRE_APPROVAL

    def test_enforce_global_rule_blocks(self):
        impl = self._make_registry()
        impl.add_global_rule(PolicyRule(
            rule_id="gr1", effect=RULE_DENY, operation=OP_WRITE,
        ))
        enforcer = PolicyEnforcer(impl)
        result = enforcer.enforce("safe_read", OP_WRITE)
        assert result.decision == ENFORCEMENT_BLOCK

    def test_enforce_no_profile_match_blocks(self):
        enforcer = PolicyEnforcer(self._make_registry_restricted())
        result = enforcer.enforce("restricted_tool", OP_WRITE, profile_id="default")
        assert result.decision == ENFORCEMENT_BLOCK

    def test_requires_approval(self):
        impl = self._make_registry()
        tool = impl.get_tool("safe_read")
        tool.requires_approval = True
        enforcer = PolicyEnforcer(impl)
        assert enforcer.requires_approval("safe_read", OP_READ) is True
        assert enforcer.is_allowed("safe_read", OP_READ) is False

    def test_requires_approval_false(self):
        enforcer = PolicyEnforcer(self._make_registry())
        assert enforcer.requires_approval("safe_read", OP_READ) is False

    def test_is_allowed(self):
        enforcer = PolicyEnforcer(self._make_registry())
        assert enforcer.is_allowed("safe_read", OP_READ) is True

    def test_get_side_effect_level(self):
        enforcer = PolicyEnforcer(self._make_registry())
        assert enforcer.get_side_effect_level("safe_read") == "read"
        assert enforcer.get_side_effect_level("missing") == "unknown"

    def test_get_allowed_operations(self):
        enforcer = PolicyEnforcer(self._make_registry())
        ops = enforcer.get_allowed_operations("safe_read")
        assert OP_READ in ops
        assert enforcer.get_allowed_operations("missing") == []
