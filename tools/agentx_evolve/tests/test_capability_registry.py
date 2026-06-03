import pytest
import json
from pathlib import Path
from agentx_evolve.policy.policy_models import (
    PolicyRule, CapabilityDefinition, ToolCapability, CapabilityRegistry,
    PolicyEnforcementResult, SideEffectLevel,
    RULE_ALLOW, RULE_DENY, RULE_REQUIRE_APPROVAL,
    ENFORCEMENT_ALLOW, ENFORCEMENT_BLOCK, ENFORCEMENT_REQUIRE_APPROVAL,
    SIDE_EFFECT_READ, SIDE_EFFECT_WRITE, SIDE_EFFECT_DESTRUCTIVE,
    OP_READ, OP_WRITE, OP_EDIT, OP_DELETE, OP_EXECUTE, OP_NETWORK, OP_SUBPROCESS,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.policy.capability_registry import (
    CapabilityRegistryImpl, EngineCapabilityRegistry, CapabilityRegistryError,
)
from agentx_evolve.policy.policy_enforcer import PolicyEnforcer
from agentx_evolve.policy.policy_loader import PolicyLoader


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_tool():
    return ToolCapability(
        tool_id="t1",
        tool_name="test_tool",
        description="A test tool",
        capabilities=[
            CapabilityDefinition(
                capability_id="c1",
                name="read_only",
                description="Read files",
                allowed_operations=[OP_READ],
                side_effect_level=SIDE_EFFECT_READ,
            ),
            CapabilityDefinition(
                capability_id="c2",
                name="write_files",
                description="Write files",
                allowed_operations=[OP_WRITE, OP_EDIT],
                side_effect_level=SIDE_EFFECT_WRITE,
                requires_approval=True,
            ),
        ],
    )


@pytest.fixture
def empty_impl():
    return CapabilityRegistryImpl()


@pytest.fixture
def default_impl():
    return CapabilityRegistryImpl()


@pytest.fixture
def engine_registry():
    return EngineCapabilityRegistry()


@pytest.fixture
def enforcer(engine_registry):
    return PolicyEnforcer(engine_registry.impl)


@pytest.fixture
def tmp_registry_path(tmp_path):
    return tmp_path / "registry.json"


# ---------------------------------------------------------------------------
# PolicyRule tests
# ---------------------------------------------------------------------------

def test_policy_rule_defaults():
    rule = PolicyRule()
    assert rule.effect == RULE_DENY
    assert rule.priority == 0
    assert rule.conditions == {}


def test_policy_rule_custom():
    rule = PolicyRule(
        rule_id="r1", effect=RULE_ALLOW,
        operation=OP_READ, priority=10,
        reason="Allowed for read",
    )
    assert rule.rule_id == "r1"
    assert rule.effect == RULE_ALLOW
    assert rule.priority == 10


def test_policy_rule_to_dict():
    rule = PolicyRule(rule_id="r1", effect=RULE_DENY, operation="WRITE")
    d = rule.to_dict()
    assert d["rule_id"] == "r1"
    assert d["effect"] == RULE_DENY


# ---------------------------------------------------------------------------
# CapabilityDefinition tests
# ---------------------------------------------------------------------------

def test_capability_definition_defaults():
    cap = CapabilityDefinition(name="test_cap")
    assert cap.schema_version == "1.0"
    assert cap.schema_id == "capability_definition.schema.json"
    assert cap.allowed_operations == [OP_READ]
    assert cap.side_effect_level == SIDE_EFFECT_READ
    assert cap.enabled


def test_capability_definition_custom():
    cap = CapabilityDefinition(
        capability_id="cap-write",
        name="write_cap",
        allowed_operations=[OP_WRITE, OP_EDIT, OP_DELETE],
        side_effect_level=SIDE_EFFECT_WRITE,
        requires_approval=True,
    )
    assert cap.requires_approval
    assert cap.side_effect_level == SIDE_EFFECT_WRITE


def test_capability_definition_to_dict():
    cap = CapabilityDefinition(
        name="test", allowed_operations=[OP_READ],
    )
    d = cap.to_dict()
    assert d["name"] == "test"
    assert OP_READ in d["allowed_operations"]


# ---------------------------------------------------------------------------
# ToolCapability tests
# ---------------------------------------------------------------------------

def test_tool_capability_defaults():
    tool = ToolCapability(tool_name="my_tool")
    assert tool.tool_name == "my_tool"
    assert tool.enabled
    assert not tool.requires_approval
    assert tool.capabilities == []


def test_tool_capability_with_capabilities(sample_tool):
    assert len(sample_tool.capabilities) == 2
    assert sample_tool.tool_name == "test_tool"


def test_tool_capability_get_capability_found(sample_tool):
    cap = sample_tool.get_capability("read_only")
    assert cap is not None
    assert cap.name == "read_only"


def test_tool_capability_get_capability_not_found(sample_tool):
    cap = sample_tool.get_capability("nonexistent")
    assert cap is None


def test_tool_capability_get_rule_for_operation(sample_tool):
    sample_tool.policy_rules.append(
        PolicyRule(rule_id="r1", effect=RULE_DENY, operation="WRITE")
    )
    rule = sample_tool.get_rule_for_operation("WRITE")
    assert rule is not None
    assert rule.rule_id == "r1"


def test_tool_capability_get_rule_wildcard(sample_tool):
    sample_tool.policy_rules.append(
        PolicyRule(rule_id="r2", effect=RULE_ALLOW, operation="*")
    )
    rule = sample_tool.get_rule_for_operation("READ")
    assert rule is not None
    assert rule.rule_id == "r2"


def test_tool_capability_get_rule_not_found(sample_tool):
    rule = sample_tool.get_rule_for_operation("DELETE")
    assert rule is None


def test_tool_capability_to_dict(sample_tool):
    d = sample_tool.to_dict()
    assert d["tool_name"] == "test_tool"
    assert len(d["capabilities"]) == 2


# ---------------------------------------------------------------------------
# CapabilityRegistry (dataclass) tests
# ---------------------------------------------------------------------------

def test_capability_registry_defaults():
    reg = CapabilityRegistry()
    assert reg.schema_version == "1.0"
    assert reg.tools == {}
    assert reg.global_rules == []


def test_capability_registry_register_tool():
    reg = CapabilityRegistry()
    tool = ToolCapability(tool_name="tool_a")
    reg.register_tool(tool)
    assert "tool_a" in reg.tools


def test_capability_registry_get_tool():
    reg = CapabilityRegistry()
    reg.register_tool(ToolCapability(tool_name="tool_a"))
    tool = reg.get_tool("tool_a")
    assert tool is not None
    assert tool.tool_name == "tool_a"


def test_capability_registry_get_tool_not_found():
    reg = CapabilityRegistry()
    assert reg.get_tool("nonexistent") is None


def test_capability_registry_remove_tool():
    reg = CapabilityRegistry()
    reg.register_tool(ToolCapability(tool_name="tool_a"))
    assert reg.remove_tool("tool_a")
    assert reg.get_tool("tool_a") is None


def test_capability_registry_remove_nonexistent():
    reg = CapabilityRegistry()
    assert not reg.remove_tool("ghost")


def test_capability_registry_list_tools():
    reg = CapabilityRegistry()
    reg.register_tool(ToolCapability(tool_name="a"))
    reg.register_tool(ToolCapability(tool_name="b"))
    assert len(reg.list_tools()) == 2


def test_capability_registry_list_enabled_tools():
    reg = CapabilityRegistry()
    t1 = ToolCapability(tool_name="a", enabled=True)
    t2 = ToolCapability(tool_name="b", enabled=False)
    reg.register_tool(t1)
    reg.register_tool(t2)
    enabled = reg.list_enabled_tools()
    assert len(enabled) == 1
    assert enabled[0].tool_name == "a"


def test_capability_registry_to_dict():
    reg = CapabilityRegistry(registry_id="reg-1")
    reg.register_tool(ToolCapability(tool_name="x"))
    d = reg.to_dict()
    assert d["registry_id"] == "reg-1"
    assert any(t["tool_name"] == "x" for t in d["tools"])


# ---------------------------------------------------------------------------
# CapabilityRegistryImpl tests
# ---------------------------------------------------------------------------

def test_impl_default_initialization():
    impl = CapabilityRegistryImpl()
    assert impl.tool_count() == 0


def test_impl_register_tool(empty_impl, sample_tool):
    impl = empty_impl
    impl.register_tool(sample_tool)
    assert impl.tool_count() == 1
    assert impl.has_tool("test_tool")


def test_impl_register_tool_no_name(empty_impl):
    tool = ToolCapability(tool_name="")
    with pytest.raises(CapabilityRegistryError, match="must have a name"):
        empty_impl.register_tool(tool)


def test_impl_register_tool_no_capabilities(empty_impl):
    tool = ToolCapability(tool_name="empty_tool", capabilities=[])
    with pytest.raises(CapabilityRegistryError, match="at least one capability"):
        empty_impl.register_tool(tool)


def test_impl_get_tool(empty_impl, sample_tool):
    impl = empty_impl
    impl.register_tool(sample_tool)
    tool = impl.get_tool("test_tool")
    assert tool is not None
    assert tool.tool_name == "test_tool"


def test_impl_get_tool_nonexistent(empty_impl):
    assert empty_impl.get_tool("ghost") is None


def test_impl_get_tool_empty_name(empty_impl):
    assert empty_impl.get_tool("") is None


def test_impl_get_tool_required(empty_impl, sample_tool):
    impl = empty_impl
    impl.register_tool(sample_tool)
    tool = impl.get_tool_required("test_tool")
    assert tool.tool_name == "test_tool"


def test_impl_get_tool_required_not_found(empty_impl):
    with pytest.raises(CapabilityRegistryError, match="Unknown tool"):
        empty_impl.get_tool_required("ghost")


def test_impl_remove_tool(empty_impl, sample_tool):
    impl = empty_impl
    impl.register_tool(sample_tool)
    assert impl.remove_tool("test_tool")
    assert not impl.has_tool("test_tool")


def test_impl_remove_nonexistent(empty_impl):
    assert not empty_impl.remove_tool("ghost")


def test_impl_enable_tool(empty_impl):
    impl = empty_impl
    tool = ToolCapability(tool_name="toggle", enabled=False,
                           capabilities=[CapabilityDefinition(name="c")])
    impl.register_tool(tool)
    impl.enable_tool("toggle")
    assert impl.get_tool("toggle").enabled


def test_impl_disable_tool(empty_impl):
    impl = empty_impl
    tool = ToolCapability(tool_name="toggle", enabled=True,
                           capabilities=[CapabilityDefinition(name="c")])
    impl.register_tool(tool)
    impl.disable_tool("toggle")
    assert not impl.get_tool("toggle").enabled


def test_impl_list_tools(empty_impl):
    impl = empty_impl
    impl.register_tool(ToolCapability(tool_name="a", capabilities=[CapabilityDefinition(name="c1")]))
    impl.register_tool(ToolCapability(tool_name="b", capabilities=[CapabilityDefinition(name="c2")]))
    names = {t.tool_name for t in impl.list_tools()}
    assert names == {"a", "b"}


def test_impl_list_enabled_tools(empty_impl):
    impl = empty_impl
    impl.register_tool(ToolCapability(tool_name="a", enabled=True, capabilities=[CapabilityDefinition(name="c1")]))
    impl.register_tool(ToolCapability(tool_name="b", enabled=False, capabilities=[CapabilityDefinition(name="c2")]))
    assert len(impl.list_enabled_tools()) == 1


def test_impl_global_rules(empty_impl):
    impl = empty_impl
    rule = PolicyRule(effect=RULE_DENY, operation="DELETE")
    impl.add_global_rule(rule)
    assert len(impl.registry.global_rules) == 1
    assert impl.remove_global_rule(rule.rule_id)
    assert len(impl.registry.global_rules) == 0


def test_impl_find_rules_by_operation(empty_impl):
    impl = empty_impl
    impl.add_global_rule(PolicyRule(effect=RULE_DENY, operation="WRITE"))
    impl.add_global_rule(PolicyRule(effect=RULE_ALLOW, operation="*", priority=1))
    found = impl.find_rules_by_operation("WRITE")
    assert len(found) == 2


# ---------------------------------------------------------------------------
# EngineCapabilityRegistry tests
# ---------------------------------------------------------------------------

def test_engine_registry_has_default_tools(engine_registry):
    tools = engine_registry.impl.list_tools()
    names = {t.tool_name for t in tools}
    assert "safe_read_file" in names
    assert "safe_write_file" in names
    assert "apply_patch" in names
    assert "rollback_session" in names
    assert "validate_session" in names
    assert "git_diff_guard" in names
    assert "check_path_boundary" in names
    assert len(tools) >= 8


def test_engine_registry_default_tool_properties(engine_registry):
    tool = engine_registry.impl.get_tool("safe_write_file")
    assert tool is not None
    assert tool.requires_approval
    assert tool.side_effect_level == SIDE_EFFECT_WRITE


def test_engine_registry_rollback_destructive(engine_registry):
    tool = engine_registry.impl.get_tool("rollback_session")
    assert tool is not None
    assert tool.side_effect_level == SIDE_EFFECT_DESTRUCTIVE
    assert tool.requires_approval


def test_engine_registry_read_tools_no_approval(engine_registry):
    for name in ["safe_read_file", "git_diff_guard", "check_path_boundary"]:
        tool = engine_registry.impl.get_tool(name)
        assert tool is not None
        assert not tool.requires_approval


# ---------------------------------------------------------------------------
# PolicyEnforcer tests
# ---------------------------------------------------------------------------

def test_enforcer_enforce_unknown_tool(enforcer):
    result = enforcer.enforce("ghost_tool", "READ")
    assert result.decision == ENFORCEMENT_BLOCK
    assert "not registered" in result.reason


def test_enforcer_enforce_disabled_tool(enforcer, engine_registry):
    engine_registry.impl.disable_tool("safe_read_file")
    result = enforcer.enforce("safe_read_file", "READ")
    assert result.decision == ENFORCEMENT_BLOCK
    assert "disabled" in result.reason


def test_enforcer_enforce_allowed_read(enforcer):
    result = enforcer.enforce("safe_read_file", "READ")
    assert result.decision == ENFORCEMENT_ALLOW


def test_enforcer_enforce_blocked_operation(enforcer):
    result = enforcer.enforce("safe_read_file", "WRITE")
    assert result.decision == ENFORCEMENT_BLOCK


def test_enforcer_enforce_requires_approval(enforcer):
    result = enforcer.enforce("safe_write_file", "WRITE")
    assert result.decision == ENFORCEMENT_REQUIRE_APPROVAL


def test_enforcer_requires_approval_true(enforcer):
    assert enforcer.requires_approval("safe_write_file", "WRITE")


def test_enforcer_requires_approval_false(enforcer):
    assert not enforcer.requires_approval("safe_read_file", "READ")


def test_enforcer_is_allowed_true(enforcer):
    assert enforcer.is_allowed("safe_read_file", "READ")


def test_enforcer_is_allowed_false(enforcer):
    assert not enforcer.is_allowed("safe_read_file", "WRITE")


def test_enforcer_get_side_effect_level(enforcer):
    assert enforcer.get_side_effect_level("safe_read_file") == SIDE_EFFECT_READ
    assert enforcer.get_side_effect_level("safe_write_file") == SIDE_EFFECT_WRITE
    assert enforcer.get_side_effect_level("rollback_session") == SIDE_EFFECT_DESTRUCTIVE


def test_enforcer_get_side_effect_unknown(enforcer):
    assert enforcer.get_side_effect_level("ghost") == "unknown"


def test_enforcer_get_allowed_operations(enforcer):
    ops = enforcer.get_allowed_operations("safe_read_file")
    assert OP_READ in ops


def test_enforcer_get_allowed_operations_unknown(enforcer):
    assert enforcer.get_allowed_operations("ghost") == []


def test_enforcer_enforce_apply_patch_requires_approval(enforcer):
    result = enforcer.enforce("apply_patch", "EDIT")
    assert result.decision == ENFORCEMENT_REQUIRE_APPROVAL


def test_enforcer_enforce_validate_session_allowed(enforcer):
    result = enforcer.enforce("validate_session", "EXECUTE")
    assert result.decision == ENFORCEMENT_ALLOW


def test_enforcer_enforce_check_subprocess_allowed_read(enforcer):
    result = enforcer.enforce("check_subprocess_allowed", "EXECUTE")
    assert result.decision == ENFORCEMENT_ALLOW


def test_enforcer_enforce_git_diff_guard(enforcer):
    result = enforcer.enforce("git_diff_guard", "EXECUTE")
    assert result.decision == ENFORCEMENT_ALLOW


def test_enforcer_enforce_check_path_boundary(enforcer):
    result = enforcer.enforce("check_path_boundary", "READ")
    assert result.decision == ENFORCEMENT_ALLOW


def test_enforcer_enforce_rollback_session_requires_approval(enforcer):
    result = enforcer.enforce("rollback_session", "WRITE")
    assert result.decision == ENFORCEMENT_REQUIRE_APPROVAL


def test_enforcer_enforce_with_global_rule(enforcer):
    enforcer.registry.add_global_rule(
        PolicyRule(rule_id="deny-all-write", effect=RULE_DENY, operation="WRITE", priority=100)
    )
    result = enforcer.enforce("safe_write_file", "WRITE")
    assert result.decision == ENFORCEMENT_BLOCK


def test_enforcer_enforce_with_global_allow_rule(enforcer):
    enforcer.registry.add_global_rule(
        PolicyRule(rule_id="allow-read-all", effect=RULE_ALLOW, operation="*", priority=50)
    )
    result = enforcer.enforce("safe_write_file", "WRITE")
    assert result.decision == ENFORCEMENT_REQUIRE_APPROVAL


def test_enforcer_enforce_with_tool_rule(enforcer):
    tool = enforcer.registry.get_tool("safe_write_file")
    tool.policy_rules.append(
        PolicyRule(rule_id="tool-deny-write", effect=RULE_DENY, operation="WRITE")
    )
    result = enforcer.enforce("safe_write_file", "WRITE")
    assert result.decision == ENFORCEMENT_BLOCK


def test_enforcer_enforce_result_has_rule_info(enforcer):
    enforcer.registry.add_global_rule(
        PolicyRule(rule_id="gr1", effect=RULE_DENY, operation="WRITE", priority=1)
    )
    result = enforcer.enforce("safe_write_file", "WRITE")
    if result.matched_rule_id:
        assert result.matched_rule_id == "gr1"


def test_policy_enforcement_result_defaults():
    result = PolicyEnforcementResult()
    assert result.decision == ENFORCEMENT_BLOCK
    assert result.tool_name == ""


def test_policy_enforcement_result_to_dict():
    result = PolicyEnforcementResult(
        enforcement_id="e1", tool_name="t", operation="READ",
        decision=ENFORCEMENT_ALLOW,
    )
    d = result.to_dict()
    assert d["enforcement_id"] == "e1"
    assert d["decision"] == ENFORCEMENT_ALLOW


def test_enforcer_profile_gating(enforcer):
    result = enforcer.enforce("safe_read_file", "READ", profile_id="restricted")
    assert result.decision == ENFORCEMENT_ALLOW


# ---------------------------------------------------------------------------
# PolicyLoader tests
# ---------------------------------------------------------------------------

def _make_registry_data():
    return {
        "registry_id": "reg-test",
        "timestamp": "2026-01-01T00:00:00",
        "tools": [
            {
                "tool_name": "loader_tool",
                "description": "Loaded from dict",
                "capabilities": [
                    {
                        "name": "loader_cap",
                        "description": "A loaded capability",
                        "allowed_operations": ["READ"],
                        "side_effect_level": "read",
                    }
                ],
                "enabled": True,
                "requires_approval": False,
                "side_effect_level": "read",
            }
        ],
        "global_rules": [
            {
                "rule_id": "global-deny-delete",
                "effect": "DENY",
                "operation": "DELETE",
                "priority": 100,
                "reason": "No delete operations allowed",
            }
        ],
    }


def test_loader_load_from_dict():
    data = _make_registry_data()
    registry = PolicyLoader.load_registry_from_dict(data)
    assert registry.registry_id == "reg-test"
    assert len(registry.tools) == 1
    assert "loader_tool" in registry.tools
    assert len(registry.global_rules) == 1


def test_loader_load_impl_from_dict():
    data = _make_registry_data()
    impl = PolicyLoader.load_impl_from_dict(data)
    assert impl.has_tool("loader_tool")
    assert impl.tool_count() == 1


def test_loader_dump_and_load_json(tmp_registry_path):
    registry = CapabilityRegistry(registry_id="reg-roundtrip")
    registry.register_tool(
        ToolCapability(
            tool_name="rt_tool",
            capabilities=[CapabilityDefinition(name="rt_cap")],
        )
    )
    PolicyLoader.dump_registry_to_json(registry, tmp_registry_path)
    assert tmp_registry_path.exists()
    loaded = PolicyLoader.load_registry_from_json(tmp_registry_path)
    assert loaded.registry_id == "reg-roundtrip"
    assert loaded.get_tool("rt_tool") is not None


def test_loader_dump_registry_to_dict():
    data = _make_registry_data()
    registry = PolicyLoader.load_registry_from_dict(data)
    dumped = PolicyLoader.dump_registry_to_dict(registry)
    assert dumped["registry_id"] == "reg-test"
    assert any(t["tool_name"] == "loader_tool" for t in dumped["tools"])


def test_loader_load_impl_from_json(tmp_registry_path):
    data = _make_registry_data()
    tmp_registry_path.write_text(json.dumps(data))
    impl = PolicyLoader.load_impl_from_json(tmp_registry_path)
    assert impl.has_tool("loader_tool")
    assert impl.tool_count() == 1


def test_loader_preserves_global_rules(tmp_registry_path):
    data = _make_registry_data()
    tmp_registry_path.write_text(json.dumps(data))
    registry = PolicyLoader.load_registry_from_json(tmp_registry_path)
    assert len(registry.global_rules) == 1
    assert registry.global_rules[0].effect == RULE_DENY
    assert registry.global_rules[0].operation == "DELETE"


# ---------------------------------------------------------------------------
# PolicyEnforcementResult schema tests
# ---------------------------------------------------------------------------

def test_enforcement_result_default_decision():
    r = PolicyEnforcementResult()
    assert r.decision == ENFORCEMENT_BLOCK


def test_enforcement_result_all_allow():
    r = PolicyEnforcementResult(
        enforcement_id="e1", tool_name="t", operation="R",
        decision=ENFORCEMENT_ALLOW,
    )
    assert r.decision == ENFORCEMENT_ALLOW


def test_enforcement_result_requires_approval():
    r = PolicyEnforcementResult(
        enforcement_id="e2", tool_name="t", operation="W",
        decision=ENFORCEMENT_REQUIRE_APPROVAL,
    )
    assert r.decision == ENFORCEMENT_REQUIRE_APPROVAL


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_registry_enforcer():
    impl = CapabilityRegistryImpl()
    enforcer = PolicyEnforcer(impl)
    result = enforcer.enforce("anything", "READ")
    assert result.decision == ENFORCEMENT_BLOCK


def test_register_duplicate_tool_overwrites(empty_impl):
    impl = empty_impl
    t1 = ToolCapability(tool_name="dup", capabilities=[CapabilityDefinition(name="c1")])
    t2 = ToolCapability(tool_name="dup", capabilities=[CapabilityDefinition(name="c2")])
    impl.register_tool(t1)
    impl.register_tool(t2)
    assert impl.tool_count() == 1
    assert impl.get_tool("dup").capabilities[0].name == "c2"


def test_default_tools_registration():
    impl = CapabilityRegistryImpl()
    tools = impl.register_default_tools()
    assert len(tools) >= 8


def test_capability_definition_side_effect_enum():
    cap = CapabilityDefinition(
        name="enum_test",
        side_effect_level="write",
    )
    assert cap.side_effect_level == SIDE_EFFECT_WRITE


def test_side_effect_level_enum_values():
    assert SideEffectLevel.READ.value == "read"
    assert SideEffectLevel.WRITE.value == "write"
    assert SideEffectLevel.DESTRUCTIVE.value == "destructive"


def test_helper_new_id():
    nid = new_id("policy")
    assert nid.startswith("policy-")
    assert len(nid) > len("policy-")


def test_helper_utc_now_iso():
    iso = utc_now_iso()
    assert "T" in iso


def test_helper_to_dict_converts_enum():
    class TestEnum:
        VALUE = "test_value"
    obj = TestEnum()
    assert to_dict(obj) == obj


def test_policy_rule_priority_ordering():
    r1 = PolicyRule(rule_id="r1", effect=RULE_ALLOW, operation="*", priority=1)
    r2 = PolicyRule(rule_id="r2", effect=RULE_DENY, operation="*", priority=100)
    rules = [r1, r2]
    highest = max(rules, key=lambda r: r.priority)
    assert highest.rule_id == "r2"


def test_enforcer_result_serialization():
    result = PolicyEnforcementResult(
        enforcement_id="e-serial",
        tool_name="tool",
        operation="READ",
        decision=ENFORCEMENT_ALLOW,
    )
    d = result.to_dict()
    restored = PolicyEnforcementResult(**d)
    assert restored.enforcement_id == "e-serial"
    assert restored.decision == ENFORCEMENT_ALLOW
