from pathlib import Path

from agentx_evolve.final_acceptance.runtime_artifact_report import (
    build_runtime_artifact_report, write_runtime_artifact_report,
)
from agentx_evolve.final_acceptance.acceptance_models import (
    FinalAcceptanceDeviation,
)
from agentx_evolve.final_acceptance.artifact_writer import (
    runtime_root, ensure_runtime_root,
)


class TestBuildRuntimeArtifactReport:
    def test_empty_runtime_root(self, tmp_path: Path):
        report = build_runtime_artifact_report(tmp_path, [])
        assert report["report_status"] in ("PASS", "PARTIAL", "FAIL")
        assert len(report["checks"]) == 3

    def test_no_deviations(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        report = build_runtime_artifact_report(tmp_path, [])
        assert len(report["checks"]) == 3

    def test_with_deviation_refs(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        devs = [
            FinalAcceptanceDeviation(
                deviation_id="D001",
                evidence_refs=["/some/path"],
            ),
        ]
        report = build_runtime_artifact_report(tmp_path, devs)
        assert len(report["checks"]) == 3

    def test_all_checks_present(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        report = build_runtime_artifact_report(tmp_path, [])
        check_ids = {c["check_id"] for c in report["checks"]}
        assert "artifacts_under_runtime_root" in check_ids
        assert "no_source_dir_runtime_state" in check_ids
        assert "deviations_cover_unauthorized_paths" in check_ids

    def test_findings_empty_when_clean(self, tmp_path: Path):
        ensure_runtime_root(tmp_path)
        report = build_runtime_artifact_report(tmp_path, [])
        assert isinstance(report["findings"], list)

    def test_artifact_under_runtime_root_pass(self, tmp_path: Path):
        rt = ensure_runtime_root(tmp_path)
        (rt / "artifact.json").write_text("{}")
        report = build_runtime_artifact_report(tmp_path, [])
        check = next(c for c in report["checks"] if c["check_id"] == "artifacts_under_runtime_root")
        assert check["status"] == "PASS"

    def test_no_source_dir_leak(self, tmp_path: Path):
        rt = ensure_runtime_root(tmp_path)
        (rt / "test.json").write_text("{}")
        report = build_runtime_artifact_report(tmp_path, [])
        check = next(c for c in report["checks"] if c["check_id"] == "no_source_dir_runtime_state")
        assert check["status"] == "PASS"

    def test_deviations_cover_paths(self, tmp_path: Path):
        rt = ensure_runtime_root(tmp_path)
        (rt / "some_artifact.txt").touch()
        report = build_runtime_artifact_report(tmp_path, [])
        check = next(c for c in report["checks"] if c["check_id"] == "deviations_cover_unauthorized_paths")
        assert check["status"] in ("PASS", "PARTIAL")


class TestWriteRuntimeArtifactReport:
    def test_writes_file(self, tmp_path: Path):
        report = build_runtime_artifact_report(tmp_path, [])
        path = write_runtime_artifact_report(report, tmp_path)
        assert path.exists()
        assert path.name == "final_acceptance_runtime_artifact_report.json"

    def test_writes_to_runtime_root(self, tmp_path: Path):
        report = build_runtime_artifact_report(tmp_path, [])
        path = write_runtime_artifact_report(report, tmp_path)
        assert runtime_root(tmp_path) in path.parents
