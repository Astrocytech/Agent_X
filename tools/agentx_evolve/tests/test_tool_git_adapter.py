from agentx_evolve.tools.git_tools import git_status, git_diff
from agentx_evolve.tools.tool_models import STATUS_FAILED


def test_git_status_function():
    result = git_status({}, {})
    assert result.tool_name == "git_status"


def test_git_diff_function():
    result = git_diff({}, {})
    assert result.tool_name == "git_diff"


def test_git_status_not_a_repo(tmp_path):
    result = git_status({"repo_path": str(tmp_path)}, {})
    assert result.status in ("SUCCESS", "BLOCKED", "FAILED")


def test_git_diff_not_a_repo(tmp_path):
    result = git_diff({"repo_path": str(tmp_path)}, {})
    assert result.status in ("SUCCESS", "BLOCKED", "FAILED")
