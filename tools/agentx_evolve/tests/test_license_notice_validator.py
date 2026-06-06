from pathlib import Path

import pytest

from agentx_evolve.packaging.license_notice_validator import validate_license_notice_files
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_BLOCKED,
)


def _inv_with_files(rel_paths: list[str]) -> PackageInventory:
    records = [PackageFileRecord(relative_path=p, included=True) for p in rel_paths]
    return PackageInventory(files=records)


class TestDetectsRequiredFiles:
    def test_detects_required_files_found(self, tmp_path: Path):
        inv = _inv_with_files(["README.md", "Makefile", "LICENSE"])
        manifest = PackageManifest(required_files=["README.md", "Makefile"])
        report = validate_license_notice_files(tmp_path, manifest, inv)
        assert report.status == VALIDATION_STATUS_PASS
        assert report.required_license_files is not None

    def test_detects_readme_missing(self, tmp_path: Path):
        inv = _inv_with_files(["Makefile"])
        manifest = PackageManifest(required_files=["README.md", "Makefile"])
        report = validate_license_notice_files(tmp_path, manifest, inv)
        assert report.status == VALIDATION_STATUS_BLOCKED

    def test_reports_missing_license(self, tmp_path: Path):
        inv = _inv_with_files(["Makefile"])
        manifest = PackageManifest(required_files=["README.md", "Makefile", "LICENSE"])
        report = validate_license_notice_files(tmp_path, manifest, inv)
        assert "LICENSE" in report.missing_license_files

    def test_finds_notice_files(self, tmp_path: Path):
        inv = _inv_with_files(["README.md", "Makefile", "LICENSE", "NOTICE"])
        manifest = PackageManifest()
        report = validate_license_notice_files(tmp_path, manifest, inv)
        assert len(report.notice_files) > 0
        assert "LICENSE" in report.notice_files
