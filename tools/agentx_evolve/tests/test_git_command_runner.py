import subprocess
from agentx_evolve.git.git_command_runner import (
    run_git_command, MAX_OUTPUT_BYTES, GIT_TIMEOUT,
)
from agentx_evolve.git.git_models import GS_SUCCESS, GS_FAILED


class TestRunGitCommand:
    def test_runs_simple_command(self):
        result = run_git_command(["echo", "hello"])
        assert result.exit_code == 0
        assert result.stdout == "hello\n"
        assert result.status == GS_SUCCESS

    def test_captures_stderr(self):
        result = run_git_command(["sh", "-c", "echo error >&2; exit 1"])
        assert result.exit_code == 1
        assert result.status == GS_FAILED
        assert result.stderr != ""

    def test_operation_id_and_name_passed(self):
        result = run_git_command(["echo", "test"], operation_id="op-1", operation_name="test_op")
        assert result.operation_id == "op-1"
        assert result.operation_name == "test_op"

    def test_argv_sha256_set(self):
        result = run_git_command(["echo", "hello"])
        assert len(result.argv_sha256) == 64

    def test_duration_ms_set(self):
        result = run_git_command(["echo", "hello"])
        assert result.duration_ms >= 0

    def test_result_id_starts_with_gcr(self):
        result = run_git_command(["echo", "hello"])
        assert result.result_id.startswith("gcr-")

    def test_timestamp_set(self):
        result = run_git_command(["echo", "hello"])
        assert "T" in result.timestamp

    def test_timeout_raises_error(self):
        result = run_git_command(["sleep", "10"], timeout_seconds=0.01)
        assert result.status == GS_FAILED
        assert result.exit_code == -1

    def test_command_not_found(self):
        result = run_git_command(["/nonexistent/binary"])
        assert result.status == GS_FAILED
        assert result.exit_code == -1


class TestGitCommandRunnerConstants:
    def test_max_output_bytes_defined(self):
        assert MAX_OUTPUT_BYTES == 1048576

    def test_git_timeout_defined(self):
        assert GIT_TIMEOUT == 30


class TestGitCommandResult:
    def test_stdout_truncated_above_max(self):
        long_output = "x" * (MAX_OUTPUT_BYTES + 100)
        result = run_git_command(["echo", long_output])
        assert len(result.stdout) <= MAX_OUTPUT_BYTES

    def test_cwd_defaults_to_dot(self):
        import os
        result = run_git_command(["pwd"])
        assert result.exit_code == 0
