from agentx_evolve.git.git_branch import git_branch
from agentx_evolve.git.git_models import GS_BLOCKED


class TestGitBranch:
    def test_returns_blocked(self):
        result = git_branch(repo_root="/tmp", new_branch="feature-x")
        assert result.status == GS_BLOCKED
        assert "blocked" in result.message.lower()

    def test_blocked_in_v1(self):
        result = git_branch(repo_root="/tmp", new_branch="feature-x", base_branch="develop")
        assert "v1" in result.message.lower()
        assert len(result.errors) == 1

    def test_returns_git_result(self):
        result = git_branch(repo_root="/tmp", new_branch="feature-x")
        assert hasattr(result, "result_id")
        assert result.result_id.startswith("gr-")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "operation")
        assert result.operation == "BRANCH"

    def test_accepts_governance_decision_id(self):
        result = git_branch(
            repo_root="/tmp", new_branch="feature-x",
            base_branch="main", governance_decision_id="gd-123",
        )
        assert result.status == GS_BLOCKED

    def test_accepts_dry_run_param(self):
        result = git_branch(repo_root="/tmp", new_branch="feature-x", dry_run=True)
        assert result.status == GS_BLOCKED
