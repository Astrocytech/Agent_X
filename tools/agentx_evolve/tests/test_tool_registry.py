import pytest

from agentx_evolve.tools.tool_registry import (
    load_default_tool_registry,
    get_tool_definition,
    register_tool,
    list_enabled_tools,
    list_mcp_exposable_tools,
)
from agentx_evolve.tools.tool_models import ToolDefinition


def test_load_default_registry_has_28_tools():
    registry = load_default_tool_registry()
    assert len(registry.tools) == 28


def test_load_default_registry_minimal_keys():
    registry = load_default_tool_registry()
    for t in registry.tools:
        assert t.tool_name
        assert t.description
        assert t.trust_tier
        assert t.allowed_roles


def test_get_tool_definition_found():
    registry = load_default_tool_registry()
    td = get_tool_definition(registry, "agentx_scan")
    assert td is not None
    assert td.tool_name == "agentx_scan"


def test_get_tool_definition_not_found():
    registry = load_default_tool_registry()
    td = get_tool_definition(registry, "nonexistent_tool")
    assert td is None


def test_get_tool_definition_case_sensitive():
    registry = load_default_tool_registry()
    assert get_tool_definition(registry, "AGENTX_SCAN") is None


def test_register_tool_adds():
    registry = load_default_tool_registry()
    td = ToolDefinition(tool_name="custom_tool", description="test")
    register_tool(registry, td)
    assert get_tool_definition(registry, "custom_tool") is not None
    assert len(registry.tools) == 29


def test_register_tool_rejects_duplicate_name():
    registry = load_default_tool_registry()
    td = ToolDefinition(tool_name="agentx_scan", description="dupe")
    with pytest.raises(ValueError, match="Duplicate tool name"):
        register_tool(registry, td)


def test_list_enabled_tools_returns_enabled_only():
    registry = load_default_tool_registry()
    names = [t.tool_name for t in list_enabled_tools(registry)]
    assert len(names) == 22
    assert "agentx_scan" in names
    assert "read_file_guarded" in names
    assert "git_create_branch" not in names


def test_list_mcp_exposable_excludes_blocked():
    registry = load_default_tool_registry()
    exposed = list_mcp_exposable_tools(registry)
    for t in exposed:
        assert t.enabled
        assert not t.writes_source
        assert not t.runs_subprocess
        assert not t.uses_network
        assert t.trust_tier not in ("TRUST_TIER_4_GIT_WRITE", "TRUST_TIER_5_NETWORK_OR_EXTERNAL", "TRUST_TIER_6_BLOCKED")
