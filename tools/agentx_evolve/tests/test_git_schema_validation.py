from agentx_evolve.git.git_models import GitCommand, GitDiff, GitDiffEntry


def test_git_command_defaults():
    cmd = GitCommand()
    assert cmd.command == "git"
    assert cmd.args == []
    assert cmd.repo_path == ""


def test_git_command_custom():
    cmd = GitCommand(command="git", args=["diff", "HEAD"], repo_path="/repo")
    assert cmd.command == "git"
    assert cmd.args == ["diff", "HEAD"]
    assert cmd.repo_path == "/repo"


def test_git_diff_defaults():
    diff = GitDiff()
    assert diff.diff_id == ""
    assert diff.files_changed == 0
    assert diff.entries == []


def test_git_diff_serialization():
    entry = GitDiffEntry(path="src/main.py", change_type="M", additions=5, deletions=3)
    diff = GitDiff(diff_id="diff-001", target="HEAD", entries=[entry], files_changed=1)
    assert diff.diff_id == "diff-001"
    assert diff.target == "HEAD"
    assert len(diff.entries) == 1
    assert diff.entries[0].path == "src/main.py"
    assert diff.entries[0].additions == 5


def test_git_diff_empty_entries():
    diff = GitDiff()
    assert diff.entries == []
    assert diff.files_changed == 0
