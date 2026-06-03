import pytest
from agentx_evolve.git.git_commit import git_commit
from agentx_evolve.git.git_models import GS_BLOCKED

pytestmark = pytest.mark.skip(reason="Requires real git repository")


class TestGitCommit:
    def test_returns_blocked(self):
        result = git_commit(repo_root="/tmp")
        assert result.status == GS_BLOCKED
        assert "blocked" in result.message.lower()

    def test_blocked_in_v1(self):
        result = git_commit(repo_root="/tmp", message="test commit")
        assert "v1" in result.message.lower()
        assert len(result.errors) == 1

    def test_returns_git_result(self):
        result = git_commit(repo_root="/tmp")
        assert hasattr(result, "result_id")
        assert result.result_id.startswith("gr-")
        assert result.operation == "COMMIT"

    def test_accepts_message_param(self):
        result = git_commit(repo_root="/tmp", message="my message")
        assert result.status == GS_BLOCKED

    def test_accepts_stage_evidence_id(self):
        result = git_commit(repo_root="/tmp", stage_evidence_id="se-001")
        assert result.status == GS_BLOCKED

    def test_accepts_dry_run(self):
        result = git_commit(repo_root="/tmp", dry_run=True)
        assert result.status == GS_BLOCKED
