import pytest
from agentx_evolve.git.git_dispatcher import dispatch_git_command, validate_git_command


class TestDispatchGitCommand:
    def test_validate_allowed_command(self):
        result = validate_git_command("status")
        assert result["command"] == "status"
        assert result["allowed"] is True

    def test_validate_blocked_command(self):
        result = validate_git_command("push")
        assert result["command"] == "push"
        assert result["allowed"] is False


class TestValidateGitCommand:
    def test_validate_with_permanently_blocked(self):
        result = validate_git_command("reset")
        assert "not permitted" in result["reason"]
