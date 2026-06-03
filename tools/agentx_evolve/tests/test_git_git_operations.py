from agentx_evolve.git.git_operations import (
    _build_git_args, _is_write_operation, _check_forbidden,
    run_git_operation, git_status, git_diff, git_diff_name_only,
    git_diff_stat, git_log, git_knows_repo,
)
from agentx_evolve.git.git_models import (
    GitOperation, GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY,
    GIT_OP_DIFF_STAT, GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH,
    GIT_OP_STAGE, GIT_OP_COMMIT,
    GS_SUCCESS, GS_BLOCKED, GS_FAILED,
)


class TestBuildGitArgs:
    def test_status(self):
        args = _build_git_args(GIT_OP_STATUS)
        assert args == ["git", "status", "--short"]

    def test_diff(self):
        args = _build_git_args(GIT_OP_DIFF, "HEAD")
        assert args == ["git", "diff", "HEAD"]

    def test_diff_no_target(self):
        args = _build_git_args(GIT_OP_DIFF)
        assert args == ["git", "diff"]

    def test_diff_name_only(self):
        args = _build_git_args(GIT_OP_DIFF_NAME_ONLY, "HEAD")
        assert args == ["git", "diff", "--name-only", "HEAD"]

    def test_diff_stat(self):
        args = _build_git_args(GIT_OP_DIFF_STAT)
        assert args == ["git", "diff", "--stat"]

    def test_log(self):
        args = _build_git_args(GIT_OP_LOG)
        assert args == ["git", "log", "--oneline", "-20"]

    def test_show_default(self):
        args = _build_git_args(GIT_OP_SHOW)
        assert args == ["git", "show", "HEAD"]

    def test_show_with_target(self):
        args = _build_git_args(GIT_OP_SHOW, "abc123")
        assert args == ["git", "show", "abc123"]

    def test_branch(self):
        args = _build_git_args(GIT_OP_BRANCH)
        assert args == ["git", "branch", "--list"]


class TestIsWriteOperation:
    def test_read_ops(self):
        assert _is_write_operation(GIT_OP_STATUS) is False
        assert _is_write_operation(GIT_OP_DIFF) is False
        assert _is_write_operation(GIT_OP_SHOW) is False
        assert _is_write_operation(GIT_OP_BRANCH) is False

    def test_write_ops(self):
        assert _is_write_operation(GIT_OP_STAGE) is True
        assert _is_write_operation(GIT_OP_COMMIT) is True
        assert _is_write_operation("PUSH") is True


class TestCheckForbidden:
    def test_allowed(self):
        assert _check_forbidden("HEAD") is None
        assert _check_forbidden("main..feature") is None

    def test_forbidden(self):
        result = _check_forbidden("push")
        assert result is not None
        assert "forbidden" in result

    def test_forbidden_substring(self):
        result = _check_forbidden("origin/feature --push")
        assert result is not None


class TestRunGitOperation:
    def test_write_op_blocked(self):
        op = GitOperation(operation=GIT_OP_STAGE, target="test.txt")
        result = run_git_operation(op)
        assert result.status == GS_BLOCKED
        assert "Write operation" in result.message

    def test_forbidden_target_blocked(self):
        op = GitOperation(operation=GIT_OP_DIFF, target="push")
        result = run_git_operation(op)
        assert result.status == GS_BLOCKED

    def test_git_not_found_in_nonexistent_dir(self):
        op = GitOperation(operation=GIT_OP_STATUS, repo_path="/nonexistent_dir_xyz")
        result = run_git_operation(op)
        assert result.status == GS_FAILED

    def test_valid_read_op_in_current_dir(self):
        import os
        if os.path.isdir(".git"):
            op = GitOperation(operation=GIT_OP_STATUS, repo_path=".")
            result = run_git_operation(op)
            assert result.status in (GS_SUCCESS, GS_FAILED)


class TestGitHelpers:
    def test_git_status_in_nonexistent_dir(self):
        result = git_status(repo_path="/nonexistent_xyz_repo")
        assert result.status == GS_FAILED

    def test_git_diff_in_nonexistent_dir(self):
        result = git_diff(repo_path="/nonexistent_xyz_repo")
        assert result.status == GS_FAILED

    def test_git_diff_name_only_in_nonexistent_dir(self):
        result = git_diff_name_only(repo_path="/nonexistent_xyz_repo")
        assert result.status == GS_FAILED

    def test_git_diff_stat_in_nonexistent_dir(self):
        result = git_diff_stat(repo_path="/nonexistent_xyz_repo")
        assert result.status == GS_FAILED

    def test_git_log_in_nonexistent_dir(self):
        result = git_log(repo_path="/nonexistent_xyz_repo")
        assert result.status == GS_FAILED

    def test_git_knows_repo_false(self):
        assert git_knows_repo("/nonexistent_xyz_repo") is False
