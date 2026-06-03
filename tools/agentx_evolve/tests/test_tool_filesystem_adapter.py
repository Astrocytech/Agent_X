from agentx_evolve.tools.tool_models import ToolDefinition


def test_tool_definition_smoke():
    d = ToolDefinition(tool_name="read_file", description="Read a file", trust_tier="TRUST_TIER_0_READ_ONLY")
    assert d.tool_name == "read_file"
    assert d.trust_tier == "TRUST_TIER_0_READ_ONLY"
    assert d.enabled
