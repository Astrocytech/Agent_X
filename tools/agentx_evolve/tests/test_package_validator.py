import io
import tarfile
from pathlib import Path

import pytest

from agentx_evolve.packaging.package_validator import (
    validate_package_contents, list_package_contents,
    validate_archive_member_path,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_FAIL,
)


def _make_tar_gz(path: Path, members: list[str]) -> Path:
    import gzip
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = [m for m in members if not m.startswith("/") and ".." not in m.split("/")]
    escapes = [m for m in members if m not in safe]
    tmpdir = path.parent / f"_tmp_{path.name}"
    tmpdir.mkdir(parents=True, exist_ok=True)
    for m in safe:
        fp = tmpdir / m
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(m)
    with tarfile.open(str(path), "w:gz") as tar:
        for m in safe:
            fp = tmpdir / m
            if fp.exists():
                tar.add(str(fp), arcname=m, recursive=False)
        for m in escapes:
            info = tarfile.TarInfo(name=m)
            info.type = tarfile.REGTYPE
            info.size = len(m.encode())
            tar.addfile(info, io.BytesIO(m.encode()))
    import shutil
    shutil.rmtree(tmpdir)
    return path


def _make_zip(path: Path, members: list[str]) -> Path:
    import zipfile
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as zf:
        for m in members:
            zf.writestr(m, m)
    return path


def _make_dir(path: Path, members: list[str]) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for m in members:
        f = path / m
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(m)
    return path


def _inventory_with(paths: list[str]) -> PackageInventory:
    records = [
        PackageFileRecord(relative_path=p, included=True, normalized_archive_path=p)
        for p in paths
    ]
    return PackageInventory(files=records)


class TestValidateCleanPackage:
    def test_validate_clean_package(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md", "Makefile", "src/main.py"])
        manifest = PackageManifest(required_files=["README.md", "Makefile"])
        inventory = _inventory_with(["README.md", "Makefile", "src/main.py"])
        report = validate_package_contents(pkg, manifest, inventory)
        assert report.status == VALIDATION_STATUS_PASS
        assert report.errors == []


class TestValidateMissingRequiredFile:
    def test_validate_missing_required_file(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["Makefile"])
        manifest = PackageManifest(required_files=["README.md", "Makefile"])
        inventory = _inventory_with(["Makefile"])
        report = validate_package_contents(pkg, manifest, inventory)
        assert report.status == VALIDATION_STATUS_FAIL
        assert any("README.md" in e for e in report.errors)


class TestValidateUnexpectedFile:
    def test_validate_unexpected_file(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md", "Makefile", "unexpected.py"])
        manifest = PackageManifest(required_files=["README.md", "Makefile"])
        inventory = _inventory_with(["README.md", "Makefile"])
        report = validate_package_contents(pkg, manifest, inventory)
        assert report.status == VALIDATION_STATUS_FAIL
        assert any("unexpected" in e.lower() for e in report.errors)


class TestValidateArchiveEscape:
    def test_validate_archive_escape(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md", "../escape.txt"])
        manifest = PackageManifest(required_files=["README.md"])
        inventory = _inventory_with(["README.md"])
        report = validate_package_contents(pkg, manifest, inventory)
        assert report.status == VALIDATION_STATUS_FAIL
        assert len(report.archive_escape_files) > 0


class TestValidateAbsolutePath:
    def test_validate_absolute_path(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md", "/etc/passwd"])
        manifest = PackageManifest(required_files=["README.md"])
        inventory = _inventory_with(["README.md"])
        report = validate_package_contents(pkg, manifest, inventory)
        assert report.status == VALIDATION_STATUS_FAIL
        assert len(report.absolute_path_entries) > 0


class TestListPackageContents:
    def test_list_contents_tar_gz(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["a.py", "b.py"])
        contents = list_package_contents(pkg)
        assert "a.py" in contents
        assert "b.py" in contents

    def test_list_contents_zip(self, tmp_path: Path):
        pkg = _make_zip(tmp_path / "pkg.zip", ["a.py", "b.py"])
        contents = list_package_contents(pkg)
        assert "a.py" in contents
        assert "b.py" in contents

    def test_list_contents_directory(self, tmp_path: Path):
        pkg = _make_dir(tmp_path / "pkg_dir", ["a.py", "b.py"])
        contents = list_package_contents(pkg)
        assert "a.py" in contents
        assert "b.py" in contents

    def test_list_contents_unsupported(self, tmp_path: Path):
        pkg = tmp_path / "pkg.xyz"
        pkg.write_text("data")
        with pytest.raises(ValueError, match="Unsupported"):
            list_package_contents(pkg)


class TestValidateArchiveMemberPath:
    def test_safe_paths_pass(self):
        assert validate_archive_member_path("tools/main.py") is True
        assert validate_archive_member_path("README.md") is True
        assert validate_archive_member_path("src/mod.py") is True

    def test_unsafe_paths_fail(self):
        assert validate_archive_member_path("/etc/passwd") is False
        assert validate_archive_member_path("../escape.txt") is False
        assert validate_archive_member_path("") is False
        assert validate_archive_member_path(".") is False
