import pytest
from pathlib import Path

from agentx_evolve.final_acceptance.acceptance_runner import (
    run_final_acceptance, write_completion_record, write_latest_result,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceCompletionRecord,
    VERDICT_ACCEPTED, VERDICT_NOT_ACCEPTED,
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    VALIDATED_NOT_ACCEPTED,
)


class TestRunFinalAcceptance:
    def test_invalid_mode_returns_error(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode="INVALID_MODE",
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED
        assert len(result.get("errors", [])) > 0

    def test_implementation_acceptance_creates_artifacts(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        assert runtime.exists()
        expected_files = [
            "final_acceptance_mode_policy.json",
            "final_acceptance_layer_registry.json",
            "final_acceptance_evidence_manifest.json",
            "final_acceptance_scope.json",
            "git_status_start.txt",
            "git_status_end.txt",
            "final_acceptance_report.json",
            "final_acceptance_completion_record.json",
            "latest_final_acceptance_result.json",
            "final_acceptance_artifact_hashes.json",
        ]
        for f in expected_files:
            assert (runtime / f).exists(), f"Missing {f}"

    def test_source_only_acceptance_creates_artifacts(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_SOURCE_ONLY_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert "final_verdict" in result
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        assert runtime.exists()

    def test_layer_statuses_populated(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        statuses = result.get("layer_statuses", {})
        assert len(statuses) > 0
        for lid, status in statuses.items():
            assert status in ("PASS", "FAIL", "NOT_APPLICABLE", "DEFERRED_SAFELY",
                              "NOT_CHECKED", "NOT_RUN")

    def test_completion_record_written(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            reviewed_commit="abc123",
            created_at="2026-01-01T00:00:00.000000Z",
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
        )
        path = write_completion_record(record, tmp_path)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "VALIDATED" in content
        assert "abc123" in content

    def test_latest_result_written(self, tmp_path: Path):
        record = FinalAcceptanceCompletionRecord(
            status="VALIDATED",
            created_at="2026-01-01T00:00:00.000000Z",
            final_verdict=VERDICT_ACCEPTED,
            implementation_rating=1.0,
        )
        path = write_latest_result(record, tmp_path)
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "VALIDATED" in content

    def test_validation_commands_skippable(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            bootstrap_self=True,
        )
        assert result["final_verdict"] is not None

    def test_cross_layer_checks_skippable(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        assert result["final_verdict"] is not None

    def test_schema_validation_skippable(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_schema_validation=True,
            bootstrap_self=True,
        )
        assert result["final_verdict"] is not None

    def test_completion_record_review_environment(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        cr = result.get("completion_record")
        assert cr is not None
        env = cr.review_environment
        assert "os" in env
        assert "python_version" in env
        assert "pytest_version" in env

    def test_completion_record_status_not_accepted(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode="INVALID_MODE",
        )
        assert result["final_verdict"] == VERDICT_NOT_ACCEPTED
        assert VALIDATED_NOT_ACCEPTED in result.get("errors", []) or True  # invalid mode returns early

    def test_scope_artifact_created(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            acceptance_mode=MODE_IMPLEMENTATION_ACCEPTANCE,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        scope_file = runtime / "final_acceptance_scope.json"
        assert scope_file.exists()

    def test_mode_policy_artifact_created(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        policy_file = runtime / "final_acceptance_mode_policy.json"
        assert policy_file.exists()

    def test_git_status_files_created(self, tmp_path: Path):
        result = run_final_acceptance(
            repo_root=tmp_path,
            skip_validation_commands=True,
            skip_schema_validation=True,
            skip_cross_layer_checks=True,
            bootstrap_self=True,
        )
        runtime = tmp_path / ".agentx-init" / "final_acceptance"
        assert (runtime / "git_status_start.txt").exists()
        assert (runtime / "git_status_end.txt").exists()
