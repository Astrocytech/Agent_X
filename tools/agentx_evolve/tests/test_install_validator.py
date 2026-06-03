import tarfile
from pathlib import Path

import pytest

from agentx_evolve.packaging.install_validator import validate_local_install
from agentx_evolve.packaging.packaging_models import (
    PackageManifest,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_FAIL,
)


def _make_tar_gz(path: Path, members: list[str]) -> Path:
    import gzip
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(str(path), "wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w|") as tar:
            for m in members:
                info = tarfile.TarInfo(name=m)
                info.type = tarfile.REGTYPE
                info.size = len(m.encode())
                tar.addfile(info, fileobj=None)
    return path


class TestArchiveExtract:
    def test_archive_extract_only_passes(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md", "src/main.py"])
        manifest = PackageManifest()
        report = validate_local_install(pkg, manifest, tmp_path)
        assert report.status == VALIDATION_STATUS_PASS
        assert report.validation_mode == "archive_extract_only"
        assert report.network_allowed is False

    def test_install_does_not_use_network(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md"])
        manifest = PackageManifest(allow_network_for_install_validation=False)
        report = validate_local_install(pkg, manifest, tmp_path)
        assert report.network_allowed is False

    def test_install_does_not_mutate_source(self, tmp_path: Path):
        pkg = _make_tar_gz(tmp_path / "pkg.tar.gz", ["README.md"])
        manifest = PackageManifest()
        src = tmp_path / "source_state.txt"
        src.write_text("before")
        validate_local_install(pkg, manifest, tmp_path)
        assert src.read_text() == "before"

    def test_invalid_archive_fails(self, tmp_path: Path):
        pkg = tmp_path / "invalid.tar.gz"
        pkg.write_text("not a valid archive")
        manifest = PackageManifest()
        report = validate_local_install(pkg, manifest, tmp_path)
        assert report.status == VALIDATION_STATUS_FAIL
