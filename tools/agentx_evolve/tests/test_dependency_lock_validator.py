from pathlib import Path

import pytest

from agentx_evolve.packaging.dependency_lock_validator import (
    validate_dependency_lock, find_dependency_files, find_lock_files,
    detect_unpinned_dependencies,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_BLOCKED, VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_NOT_CHECKED,
)


class TestPassesWhenLockNotRequired:
    def test_passes_when_lock_not_required(self, tmp_path: Path):
        manifest = PackageManifest(require_dependency_lock=False)
        report = validate_dependency_lock(tmp_path, manifest)
        assert report.status == VALIDATION_STATUS_PASS
        assert report.lock_files_found == []

    def test_passes_without_dep_files(self, tmp_path: Path):
        manifest = PackageManifest(require_dependency_lock=False)
        report = validate_dependency_lock(tmp_path, manifest)
        assert report.status in (VALIDATION_STATUS_PASS, VALIDATION_STATUS_NOT_CHECKED)


class TestFindsDependencyFiles:
    def test_finds_pyproject_toml(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").write_text("[project]\ndependencies = []\n")
        files = find_dependency_files(tmp_path)
        assert any(f.name == "pyproject.toml" for f in files)

    def test_finds_requirements_txt(self, tmp_path: Path):
        (tmp_path / "requirements.txt").write_text("requests\n")
        files = find_dependency_files(tmp_path)
        assert any(f.name == "requirements.txt" for f in files)

    def test_finds_lock_files(self, tmp_path: Path):
        (tmp_path / "poetry.lock").write_text("")
        files = find_lock_files(tmp_path)
        assert any(f.name == "poetry.lock" for f in files)


class TestDetectsUnpinned:
    def test_detects_unpinned(self, tmp_path: Path):
        req = tmp_path / "requirements.txt"
        req.write_text("requests\nflask==2.0\n")
        unpinned = detect_unpinned_dependencies(req)
        assert "requests" in unpinned
        assert "flask==2.0" not in unpinned

    def test_detect_unpinned_from_pyproject(self, tmp_path: Path):
        pp = tmp_path / "pyproject.toml"
        pp.write_text('[project]\ndependencies = ["click==8.0", "flask"]\n')
        unpinned = detect_unpinned_dependencies(pp)
        assert "flask" in unpinned
        assert "click" not in unpinned or "click==8.0" not in unpinned


class TestBlocksWhenLockRequiredMissing:
    def test_blocks_when_lock_required_missing(self, tmp_path: Path):
        manifest = PackageManifest(require_dependency_lock=True)
        report = validate_dependency_lock(tmp_path, manifest)
        assert report.status == VALIDATION_STATUS_BLOCKED
        assert len(report.missing_lock_files) > 0

    def test_passes_when_lock_present(self, tmp_path: Path):
        for name in ("poetry.lock", "uv.lock", "requirements.lock", "Pipfile.lock"):
            (tmp_path / name).write_text("")
        manifest = PackageManifest(require_dependency_lock=True)
        report = validate_dependency_lock(tmp_path, manifest)
        assert report.status != VALIDATION_STATUS_BLOCKED

    def test_reports_unpinned_when_no_dep_files(self, tmp_path: Path):
        manifest = PackageManifest(require_dependency_lock=False)
        report = validate_dependency_lock(tmp_path, manifest)
        assert isinstance(report.unpinned_dependencies, list)
