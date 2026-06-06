from pathlib import Path
from agentx_evolve.patch.git_diff_guard import GitDiffGuard


class TestGitDiffGuard:
    def test_init(self):
        guard = GitDiffGuard(Path("/tmp"))
        assert guard._repo_root == Path("/tmp").resolve()

    def test_get_diff_empty_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        diff = guard.get_diff()
        assert diff == ""

    def test_get_diff_name_only_empty_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        files = guard.get_diff_name_only()
        assert files == []

    def test_get_diff_stat_empty_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        stat = guard.get_diff_stat()
        assert stat == ""

    def test_get_diff_for_file_empty_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        diff = guard.get_diff_for_file("test.py")
        assert diff == ""

    def test_has_changes_false_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        assert guard.has_changes() is False

    def test_verify_only_expected_files_changed_false_in_nonexistent_dir(self):
        guard = GitDiffGuard(Path("/nonexistent_repo_xyz"))
        ok, unexpected = guard.verify_only_expected_files_changed({"a.py"})
        assert ok is True
        assert unexpected == []
