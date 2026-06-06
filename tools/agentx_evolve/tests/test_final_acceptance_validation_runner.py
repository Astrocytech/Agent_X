import json
import pytest
from pathlib import Path

from tools.agentx_evolve.final_acceptance.validation_runner import (
    run_validation_commands, run_single_validation_command, write_validation_results,
)
from tools.agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceValidationResult, STATUS_PASS, STATUS_FAIL, STATUS_NOT_RUN,
)


class TestRunSingleValidationCommand:
    def test_successful_command(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "echo_test",
            ["/bin/echo", "hello"],
            "echo_output.txt",
        )
        assert result.status == STATUS_PASS
        assert result.exit_code == 0
        out = tmp_path / ".agentx-init" / "final_acceptance" / "echo_output.txt"
        assert out.exists()

    def test_failing_command(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "fail_test",
            ["/bin/false"],
            "fail_output.txt",
        )
        assert result.status == STATUS_FAIL
        assert result.exit_code == 1

    def test_command_not_found(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "bad_cmd",
            ["nonexistent_command_xyz"],
            "bad_output.txt",
        )
        assert result.status == STATUS_FAIL
        assert "not found" in result.summary.lower() or "not found" in str(result.summary)

    def test_output_file_has_sha256(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "echo_test",
            ["/bin/echo", "data"],
            "sha_output.txt",
        )
        assert result.output_sha256 is not None
        assert len(result.output_sha256) == 64

    def test_command_name_preserved(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "my_custom_cmd",
            ["/bin/echo", "test"],
            "out.txt",
        )
        assert result.command_name == "my_custom_cmd"

    def test_timeout_triggers_failure(self, tmp_path: Path):
        result = run_single_validation_command(
            tmp_path, "sleep_cmd",
            ["/bin/sleep", "10"],
            "timeout_output.txt",
            timeout_seconds=1,
        )
        assert result.status == STATUS_FAIL


class TestRunValidationCommands:
    def test_includes_compileall(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=False)
        names = [r.command_name for r in results]
        assert "compileall" in names

    def test_includes_pytest_when_requested(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=True)
        names = [r.command_name for r in results]
        assert "pytest" in names

    def test_pytest_not_run_when_skipped(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=False)
        pytest_results = [r for r in results if r.command_name == "pytest"]
        assert len(pytest_results) == 1
        assert pytest_results[0].status == STATUS_NOT_RUN

    def test_includes_scoped_pytest(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=False)
        names = [r.command_name for r in results]
        assert "pytest_final_acceptance" in names

    def test_returns_three_results(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=False)
        assert len(results) == 3

    def test_returns_three_results_with_full(self, tmp_path: Path):
        results = run_validation_commands(tmp_path, include_full_pytest=True)
        assert len(results) == 3


class TestWriteValidationResults:
    def test_writes_file(self, tmp_path: Path):
        results = [
            FinalAcceptanceValidationResult(
                command_name="test", command_text="test", status=STATUS_PASS,
            )
        ]
        path = write_validation_results(results, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_validation_results.json"

    def test_content(self, tmp_path: Path):
        results = [
            FinalAcceptanceValidationResult(
                command_name="cmd1", command_text="echo hi", status=STATUS_PASS,
                exit_code=0, summary="ok",
            ),
            FinalAcceptanceValidationResult(
                command_name="cmd2", command_text="false", status=STATUS_FAIL,
                exit_code=1, summary="failed",
            ),
        ]
        path = write_validation_results(results, tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_id"] == "final_acceptance_validation_result.schema.json"
        assert len(data["results"]) == 2
        assert data["results"][0]["command_name"] == "cmd1"
        assert data["results"][1]["exit_code"] == 1

    def test_empty_results(self, tmp_path: Path):
        path = write_validation_results([], tmp_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["results"] == []
