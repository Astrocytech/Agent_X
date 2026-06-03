from pathlib import Path

import pytest

from agentx_evolve.packaging.staging_cleanliness import (
    check_staging_cleanliness,
    clean_staging,
    verify_clean_staging,
)
from agentx_evolve.packaging.packaging_models import (
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_FAIL,
    staging_dir,
)


class TestStagingCleanliness:
    def test_clean_staging_reports_pass(self, tmp_path: Path):
        clean_staging(tmp_path)
        report = check_staging_cleanliness(tmp_path)
        assert report.status == VALIDATION_STATUS_PASS

    def test_stale_staging_entry_detected(self, tmp_path: Path):
        clean_staging(tmp_path)
        stage = staging_dir(tmp_path)
        stale = stage / "stale_artifact"
        stale.write_text("stale")
        report = check_staging_cleanliness(tmp_path)
        assert report.status == VALIDATION_STATUS_FAIL
        assert len(report.stale_staging_entries) >= 1
        assert "stale_artifact" in report.stale_staging_entries[0]

    def test_stale_dist_entry_detected(self, tmp_path: Path):
        clean_staging(tmp_path)
        dist = tmp_path / ".agentx-init" / "packaging" / "dist"
        dist.mkdir(parents=True, exist_ok=True)
        stale_pkg = dist / "old_package.tar.gz"
        stale_pkg.write_text("old")
        report = check_staging_cleanliness(tmp_path)
        assert report.status == VALIDATION_STATUS_FAIL
        assert len(report.stale_dist_entries) >= 1

    def test_expected_staging_id_skipped(self, tmp_path: Path):
        clean_staging(tmp_path)
        stage = staging_dir(tmp_path)
        expected = stage / "expected_staging"
        expected.mkdir(parents=True, exist_ok=True)
        report = check_staging_cleanliness(tmp_path, expected_staging_id="expected_staging")
        assert report.status == VALIDATION_STATUS_PASS

    def test_verify_clean_auto_cleans_stale(self, tmp_path: Path):
        clean_staging(tmp_path)
        stage = staging_dir(tmp_path)
        stale = stage / "stale_artifact"
        stale.write_text("stale")
        report = verify_clean_staging(tmp_path, auto_clean=True)
        assert report.status == VALIDATION_STATUS_PASS
        assert "auto-cleaned" in " ".join(report.issues)

    def test_report_has_correct_schema_id(self, tmp_path: Path):
        clean_staging(tmp_path)
        report = check_staging_cleanliness(tmp_path)
        assert report.schema_id == "package_staging_cleanliness_report.schema.json"

    def test_report_id_generated(self, tmp_path: Path):
        clean_staging(tmp_path)
        report = check_staging_cleanliness(tmp_path)
        assert report.report_id.startswith("stage_clean_")

    def test_clean_staging_removes_directory(self, tmp_path: Path):
        stage = staging_dir(tmp_path)
        stage.mkdir(parents=True, exist_ok=True)
        (stage / "test.txt").write_text("test")
        clean_staging(tmp_path)
        assert stage.exists()
        assert len(list(stage.iterdir())) == 0

    def test_multiple_stale_entries_all_reported(self, tmp_path: Path):
        clean_staging(tmp_path)
        stage = staging_dir(tmp_path)
        for i in range(3):
            (stage / f"stale_{i}").write_text("stale")
        report = check_staging_cleanliness(tmp_path)
        assert report.status == VALIDATION_STATUS_FAIL
        assert len(report.stale_staging_entries) == 3

    def test_dist_does_not_exist_is_clean(self, tmp_path: Path):
        clean_staging(tmp_path)
        report = check_staging_cleanliness(tmp_path)
        assert report.status == VALIDATION_STATUS_PASS
