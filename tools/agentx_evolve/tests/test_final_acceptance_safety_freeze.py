from pathlib import Path

from agentx_evolve.final_acceptance.safety_freeze import (
    build_safety_freeze_report, write_safety_freeze_report,
)
from agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root,
)


class TestBuildSafetyFreezeReport:
    def test_empty_repo(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        assert "safety_freeze_status" in report
        assert "checks" in report
        assert len(report["checks"]) == 3

    def test_no_git_no_crash(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        source_check = next(c for c in report["checks"] if c["check"] == "source_mutation")
        assert source_check["status"] == "PASS"

    def test_runtime_root_not_exists(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        boundary_check = next(c for c in report["checks"] if c["check"] == "runtime_artifact_boundary")
        assert boundary_check["status"] == "NOT_CHECKED"
        assert "does not exist" in boundary_check["detail"]

    def test_runtime_root_exists_passes(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        report = build_safety_freeze_report(tmp_path)
        boundary_check = next(c for c in report["checks"] if c["check"] == "runtime_artifact_boundary")
        assert boundary_check["status"] == "PASS"
        assert boundary_check["detail"] == "All artifacts under runtime root"

    def test_external_service_check_always_passes(self):
        report = build_safety_freeze_report(Path("/tmp"))
        ext_check = next(c for c in report["checks"] if c["check"] == "external_service_requirements")
        assert ext_check["status"] == "PASS"

    def test_schema_version(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        assert report["schema_version"] == "1.0"

    def test_warnings_and_errors_are_lists(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        assert report["warnings"] == []
        assert report["errors"] == []

    def test_safety_freeze_status_pass_when_all_pass(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        report = build_safety_freeze_report(tmp_path)
        assert report["safety_freeze_status"] == "PASS"

    def test_safety_freeze_status_not_checked_when_no_runtime(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        assert report["safety_freeze_status"] in ("PASS", "NOT_CHECKED")


class TestWriteSafetyFreezeReport:
    def test_writes_file(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        path = write_safety_freeze_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_safety_freeze.json"

    def test_writes_to_runtime_root(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        path = write_safety_freeze_report(report, tmp_path)
        assert runtime_root(tmp_path) in path.parents

    def test_written_json_valid(self, tmp_path: Path):
        report = build_safety_freeze_report(tmp_path)
        write_safety_freeze_report(report, tmp_path)
        import json
        path = runtime_root(tmp_path) / "final_acceptance_safety_freeze.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "safety_freeze_status" in data
        assert "checks" in data
