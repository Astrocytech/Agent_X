import pytest
from agentx_evolve.git.git_stage import git_stage
from agentx_evolve.git.git_models import GS_BLOCKED

pytestmark = pytest.mark.skip(reason="Requires real git repository")


class TestGitStage:
    def test_returns_blocked(self):
        result = git_stage(repo_root="/tmp", paths=["f.py"])
        assert result.status == GS_BLOCKED
        assert "blocked" in result.message.lower()

    def test_blocked_in_v1(self):
        result = git_stage(repo_root="/tmp", paths=["f.py"])
        assert "v1" in result.message.lower()
        assert len(result.errors) == 1

    def test_returns_git_result(self):
        result = git_stage(repo_root="/tmp", paths=["f.py"])
        assert hasattr(result, "result_id")
        assert result.result_id.startswith("gr-")
        assert result.operation == "STAGE"

    def test_accepts_patch_evidence_id(self):
        result = git_stage(repo_root="/tmp", paths=["f.py"], patch_evidence_id="pe-001")
        assert result.status == GS_BLOCKED

    def test_accepts_empty_paths(self):
        result = git_stage(repo_root="/tmp", paths=[])
        assert result.status == GS_BLOCKED

    def test_accepts_multiple_paths(self):
        result = git_stage(repo_root="/tmp", paths=["a.py", "b.py", "c.py"])
        assert result.status == GS_BLOCKED

    def test_accepts_dry_run(self):
        result = git_stage(repo_root="/tmp", paths=["f.py"], dry_run=True)
        assert result.status == GS_BLOCKED
