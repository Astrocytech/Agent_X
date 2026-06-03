import pytest
from agentx_evolve.git.git_status import git_status


class TestGitInspection:
    def test_git_status(self):
        result = git_status()
        assert result is not None
