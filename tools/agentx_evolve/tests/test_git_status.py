from agentx_evolve.git.git_status import git_status
from agentx_evolve.git.git_models import GS_BLOCKED, GS_FAILED, GS_SUCCESS


class TestGitStatus:
    def test_status_in_non_repo_returns_failed_or_blocked(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert result.status in (GS_BLOCKED, GS_FAILED)

    def test_returns_git_result(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert hasattr(result, "result_id")
        assert hasattr(result, "operation")
        assert hasattr(result, "stdout")
        assert hasattr(result, "stderr")

    def test_operation_is_status(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert result.operation == "STATUS"

    def test_returns_data_dict(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert isinstance(result.data, dict)

    def test_data_contains_args(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert "args" in result.data
        assert "cwd" in result.data

    def test_timestamp_set(self, tmp_path):
        result = git_status(repo_root=str(tmp_path))
        assert "T" in result.timestamp

    def test_defaults_to_current_dir(self):
        result = git_status()
        assert result.status in (GS_BLOCKED, GS_FAILED, GS_SUCCESS)
