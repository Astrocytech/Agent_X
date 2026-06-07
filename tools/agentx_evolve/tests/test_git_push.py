import pytest
from agentx_evolve.git.git_push import git_push
from agentx_evolve.git.git_models import GS_BLOCKED

pytestmark = pytest.mark.skip(reason="Requires real git repository")


class TestGitPush:
    def test_returns_blocked(self):
        result = git_push(repo_root="/tmp")
        assert result.status == GS_BLOCKED
        assert "blocked" in result.message.lower()

    def test_blocked_in_v1(self):
        result = git_push(repo_root="/tmp")
        assert "v1" in result.message.lower()
        assert len(result.errors) == 1

    def test_returns_git_result(self):
        result = git_push(repo_root="/tmp")
        assert hasattr(result, "result_id")
        assert result.result_id.startswith("gr-")
        assert result.operation == "PUSH"

    def test_accepts_remote_param(self):
        result = git_push(repo_root="/tmp", remote="upstream")
        assert result.status == GS_BLOCKED

    def test_accepts_ref_params(self):
        result = git_push(repo_root="/tmp", source_ref="main", target_ref="main")
        assert result.status == GS_BLOCKED

    def test_accepts_promotion_gate_id(self):
        result = git_push(repo_root="/tmp", promotion_gate_id="pg-001")
        assert result.status == GS_BLOCKED

    def test_accepts_dry_run(self):
        result = git_push(repo_root="/tmp", dry_run=True)
        assert result.status == GS_BLOCKED
