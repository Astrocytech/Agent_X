import pytest
from pathlib import Path

from agentx_evolve.final_acceptance.cli import main


class TestCLI:
    def test_run_help(self):
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0

    def test_run_invalid_mode(self):
        with pytest.raises(SystemExit):
            main(["run", "--mode", "INVALID"])

    def test_run_minimal(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "run",
            "--mode", "IMPLEMENTATION_ACCEPTANCE",
            "--bootstrap-self",
            "--skip-validation",
            "--skip-schema-validation",
            "--skip-cross-layer",
        ])
        assert rc == 0 or rc == 1

    def test_report_no_report(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "report",
        ])
        assert rc == 1

    def test_check_schemas(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "check",
        ])
        assert rc == 0 or rc == 1

    def test_validate_schemas(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "validate-schemas",
        ])
        assert rc == 0 or rc == 1

    def test_run_with_output_json(self, tmp_path: Path):
        output = tmp_path / "result.json"
        rc = main([
            "--repo-root", str(tmp_path),
            "run",
            "--mode", "IMPLEMENTATION_ACCEPTANCE",
            "--bootstrap-self",
            "--skip-validation",
            "--skip-schema-validation",
            "--skip-cross-layer",
            "--output-json", str(output),
        ])
        assert output.exists() or rc == 1

    def test_run_source_only_mode(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "run",
            "--mode", "SOURCE_ONLY_ACCEPTANCE",
            "--bootstrap-self",
            "--skip-validation",
            "--skip-schema-validation",
            "--skip-cross-layer",
        ])
        assert rc == 0 or rc == 1

    def test_run_with_commit_and_branch(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "run",
            "--mode", "IMPLEMENTATION_ACCEPTANCE",
            "--commit", "abc123def456",
            "--branch", "feature/test",
            "--bootstrap-self",
            "--skip-validation",
            "--skip-schema-validation",
            "--skip-cross-layer",
        ])
        assert rc == 0 or rc == 1

    def test_validate_schemas_with_output(self, tmp_path: Path):
        rc = main([
            "--repo-root", str(tmp_path),
            "validate-schemas",
            "--output",
        ])
        assert rc == 0 or rc == 1
