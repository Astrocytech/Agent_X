from agentx_evolve.tool.command_runner_adapter import make_run_command_tool
from agentx_evolve.tool.tool_models import ToolCall, TS_SUCCESS, TS_FAILED


def test_make_run_command_tool():
    defn, handler = make_run_command_tool()
    assert defn.tool_name == "run_allowlisted_command"
    assert defn.requires_approval is True


def test_run_command_success():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["echo", "hello"]})
    result = handler(call)
    assert result.status == TS_SUCCESS
    assert result.data["returncode"] == 0
    assert "hello" in result.data["stdout"]


def test_run_command_blocked_not_allowlisted():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["rm", "-rf", "/"]})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "not allowlisted" in result.message


def test_run_command_empty():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": []})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "Empty command" in result.message


def test_run_command_missing_arg():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "Missing required argument" in result.message


def test_run_command_shell_metachar_blocked():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["echo", "hello", "&&", "rm"]})
    result = handler(call)
    assert result.status == TS_FAILED
    assert "Shell metacharacter" in result.message


def test_run_command_not_found():
    _defn, handler = make_run_command_tool()
    call = ToolCall(tool_name="run_allowlisted_command", arguments={"command": ["nonexistent_cmd_xyz"]})
    result = handler(call)
    assert result.status == TS_FAILED
