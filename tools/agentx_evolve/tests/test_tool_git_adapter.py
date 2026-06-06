from agentx_evolve.tool.git_adapter import make_git_status_tool, make_git_diff_tool
from agentx_evolve.tool.tool_models import ToolCall, TS_FAILED


def test_make_git_status_tool():
    defn, handler = make_git_status_tool()
    assert defn.tool_name == "git_status"
    assert defn.side_effect == "read"


def test_make_git_diff_tool():
    defn, handler = make_git_diff_tool()
    assert defn.tool_name == "git_diff"
    assert defn.side_effect == "read"


def test_git_status_handler_not_a_repo(tmp_path):
    _defn, handler = make_git_status_tool()
    call = ToolCall(tool_name="git_status", arguments={"repo_path": str(tmp_path)})
    result = handler(call)
    assert result.status == TS_FAILED


def test_git_diff_handler_not_a_repo(tmp_path):
    _defn, handler = make_git_diff_tool()
    call = ToolCall(tool_name="git_diff", arguments={"repo_path": str(tmp_path)})
    result = handler(call)
    assert result.status == TS_FAILED
