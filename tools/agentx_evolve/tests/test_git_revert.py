from agentx_evolve.git.git_revert import git_revert
from agentx_evolve.git.git_models import GS_BLOCKED


class TestGitRevert:
    def test_returns_blocked(self):
        result = git_revert(repo_root="/tmp")
        assert result.status == GS_BLOCKED
        assert "blocked" in result.message.lower()

    def test_blocked_in_v1(self):
        result = git_revert(repo_root="/tmp")
        assert "v1" in result.message.lower()
        assert len(result.errors) == 1

    def test_returns_git_result(self):
        result = git_revert(repo_root="/tmp")
        assert hasattr(result, "result_id")
        assert result.result_id.startswith("gr-")
        assert result.operation == "REVERT"

    def test_accepts_target_commit(self):
        result = git_revert(repo_root="/tmp", target_commit="abc123")
        assert result.status == GS_BLOCKED

    def test_accepts_governance_decision_id(self):
        result = git_revert(repo_root="/tmp", governance_decision_id="gd-001")
        assert result.status == GS_BLOCKED

    def test_accepts_human_approval_id(self):
        result = git_revert(repo_root="/tmp", human_approval_id="ha-001")
        assert result.status == GS_BLOCKED

    def test_accepts_dry_run(self):
        result = git_revert(repo_root="/tmp", dry_run=True)
        assert result.status == GS_BLOCKED
