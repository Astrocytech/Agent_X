import tarfile
import zipfile
from pathlib import Path

import pytest

from agentx_evolve.packaging.package_builder import (
    build_package, create_staging_tree,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    PACKAGE_FORMAT_TAR_GZ, PACKAGE_FORMAT_ZIP, PACKAGE_FORMAT_DIRECTORY,
    PACKAGE_STATUS_BUILT, PACKAGE_STATUS_FAILED,
)


def _make_inventory(tmp_path: Path, files: list[str]) -> PackageInventory:
    records = []
    for rel in files:
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"content of {rel}")
        records.append(PackageFileRecord(
            relative_path=rel,
            absolute_path=str(f),
            included=True,
        ))
    return PackageInventory(files=records, selected_count=len(records))


class TestCreateStagingTree:
    def test_create_staging_tree(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".")
        inventory = _make_inventory(tmp_path, ["src/main.py", "README.md"])
        stage = create_staging_tree(tmp_path, manifest, inventory)
        assert stage.exists()
        assert (stage / "src/main.py").exists()
        assert (stage / "README.md").exists()
        content = (stage / "src/main.py").read_text()
        assert content == "content of src/main.py"


class TestBuildTarGz:
    def test_build_tar_gz(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, report = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        assert artifact.exists()
        assert artifact.suffixes == [".tar", ".gz"] or artifact.name.endswith(".tar.gz")
        assert tarfile.is_tarfile(str(artifact))
        assert report.status == PACKAGE_STATUS_BUILT

    def test_no_absolute_paths(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, _ = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        with tarfile.open(str(artifact), "r:gz") as tf:
            for m in tf.getmembers():
                assert not m.name.startswith("/")

    def test_deterministic_ordering(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["b.py", "a.py", "c.py"])
        artifact, _ = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        with tarfile.open(str(artifact), "r:gz") as tf:
            names = [m.name for m in tf.getmembers()]
            assert names == sorted(names)

    def test_no_rejected_files(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        inventory.rejected_count = 2
        inventory.rejections = []
        artifact, report = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        assert report.files_rejected == 2

    def test_build_under_dist(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, _ = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        dist_dir = tmp_path / ".agentx-init" / "packaging" / "dist"
        assert str(artifact.resolve()).startswith(str(dist_dir.resolve()))


class TestBuildZip:
    def test_build_zip(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, report = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_ZIP)
        assert artifact.exists()
        assert artifact.suffix == ".zip"
        assert zipfile.is_zipfile(str(artifact))
        assert report.status == PACKAGE_STATUS_BUILT

    def test_zip_no_absolute_paths(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, _ = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_ZIP)
        with zipfile.ZipFile(str(artifact), "r") as zf:
            for name in zf.namelist():
                assert not name.startswith("/")


class TestBuildDirectory:
    def test_build_directory(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        artifact, report = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_DIRECTORY)
        assert artifact.exists()
        assert artifact.is_dir()
        assert (artifact / "README.md").exists()
        assert report.status == PACKAGE_STATUS_BUILT


class TestBuildReport:
    def test_build_report(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        _, report = build_package(tmp_path, manifest, inventory, package_format=PACKAGE_FORMAT_TAR_GZ)
        assert report.status == PACKAGE_STATUS_BUILT
        assert report.package_artifact is not None
        assert report.files_copied >= 1
        assert report.manifest_id == manifest.manifest_id

    def test_build_report_failed_for_unsupported_format(self, tmp_path: Path):
        manifest = PackageManifest(source_root=".", package_name="testpkg", package_version="1.0")
        inventory = _make_inventory(tmp_path, ["README.md"])
        _, report = build_package(tmp_path, manifest, inventory, package_format="exe")
        assert report.status == PACKAGE_STATUS_FAILED
        assert len(report.errors) > 0
