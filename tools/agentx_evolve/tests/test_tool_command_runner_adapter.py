from agentx_evolve.tools.tool_models import ToolDefinition


def test_tool_definition_smoke():
    d = ToolDefinition(tool_name="run_command", description="Execute a command", runs_subprocess=True)
    assert d.tool_name == "run_command"
    assert d.runs_subprocess
    assert d.enabled
