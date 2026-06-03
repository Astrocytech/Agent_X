import pytest
from agentx_evolve.git.git_diff import (
    git_diff, git_diff_name_only, git_diff_stat,
    _run_diff_operation,
)
from agentx_evolve.git.git_models import GS_BLOCKED, GS_FAILED, GS_SUCCESS


class TestGitDiff:
    def test_diff_in_non_repo_returns_failed(self, tmp_path):
        result = git_diff(repo_root=str(tmp_path), target="HEAD")
        assert result.status in (GS_BLOCKED, GS_FAILED)

    def test_diff_returns_git_result(self, tmp_path):
        result = git_diff(repo_root=str(tmp_path))
        assert hasattr(result, "result_id")
        assert hasattr(result, "operation")
        assert hasattr(result, "stdout")

    def test_diff_operation_set(self, tmp_path):
        result = git_diff(repo_root=str(tmp_path))
        assert result.operation == "DIFF"


class TestGitDiffNameOnly:
    def test_diff_name_only_in_non_repo(self, tmp_path):
        result = git_diff_name_only(repo_root=str(tmp_path), target="HEAD")
        assert result.status in (GS_BLOCKED, GS_FAILED)

    def test_diff_name_only_returns_git_result(self, tmp_path):
        result = git_diff_name_only(repo_root=str(tmp_path))
        assert hasattr(result, "result_id")
        assert result.operation == "DIFF_NAME_ONLY"


class TestGitDiffStat:
    def test_diff_stat_in_non_repo(self, tmp_path):
        result = git_diff_stat(repo_root=str(tmp_path), target="HEAD")
        assert result.status in (GS_BLOCKED, GS_FAILED)

    def test_diff_stat_returns_git_result(self, tmp_path):
        result = git_diff_stat(repo_root=str(tmp_path))
        assert hasattr(result, "result_id")
        assert result.operation == "DIFF_STAT"


class TestRunDiffOperation:
    def test_returns_blocked_status_for_bad_target(self):
        result = _run_diff_operation("DIFF", "push", "/tmp", ["git", "diff"])
        assert result.status == GS_BLOCKED

    def test_returns_git_result(self):
        result = _run_diff_operation("DIFF", "HEAD", "/tmp", ["git", "diff"])
        assert hasattr(result, "result_id")
        assert hasattr(result, "timestamp")
