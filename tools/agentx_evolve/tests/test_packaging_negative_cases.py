from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    VALIDATION_STATUS_FAIL,
    REJECTION_SECRET, REJECTION_CACHE, REJECTION_ENV_FILE,
    REJECTION_FORBIDDEN_EXTENSION, REJECTION_RUNTIME_ARTIFACT,
    SEVERITY_BLOCKER,
)
from agentx_evolve.packaging.package_file_selector import select_package_files
from agentx_evolve.packaging.package_rejector import reject_forbidden_package_files
from agentx_evolve.packaging.package_validator import (
    validate_package_contents, validate_archive_member_path,
)
from agentx_evolve.packaging.package_builder import build_package
from agentx_evolve.packaging.install_validator import validate_local_install


def _make_repo(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


class TestNegativeCases:
    def test_env_file_not_packaged(self, tmp_path: Path):
        _make_repo(tmp_path, {
            "README.md": "# ok",
            ".env": "SECRET=key",
        })
        manifest = PackageManifest(require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert ".env" not in rel_paths

    def test_pycache_not_packaged(self, tmp_path: Path):
        _make_repo(tmp_path, {
            "README.md": "# ok",
            "src/__pycache__/mod.pyc": "",
        })
        manifest = PackageManifest(require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert "src/__pycache__/mod.pyc" not in rel_paths

    def test_secret_file_blocked(self, tmp_path: Path):
        _make_repo(tmp_path, {
            "README.md": "# ok",
            "secret.txt": "API_KEY=sk-1234567890abcdef",
        })
        manifest = PackageManifest(require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        inventory = reject_forbidden_package_files(inventory, manifest, tmp_path)
        assert any(r.reason_code == REJECTION_SECRET for r in inventory.rejections)

    def test_runtime_artifact_blocked(self, tmp_path: Path):
        _make_repo(tmp_path, {
            "README.md": "# ok",
            ".agentx-init/packaging/staging/file.txt": "data",
        })
        manifest = PackageManifest(require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert ".agentx-init/packaging/staging/file.txt" not in rel_paths

    def test_forbidden_extension_blocked(self, tmp_path: Path):
        _make_repo(tmp_path, {
            "README.md": "# ok",
            "key.pem": "PRIVATE KEY DATA",
        })
        manifest = PackageManifest(require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert "key.pem" not in rel_paths

    def test_required_file_missing_blocks(self, tmp_path: Path):
        _make_repo(tmp_path, {"Makefile": "all:"})
        manifest = PackageManifest(required_files=["README.md", "Makefile"], require_clean_git=False)
        inventory = select_package_files(tmp_path, manifest)
        artifact, build_report = build_package(tmp_path, manifest, inventory)
        validation_report = validate_package_contents(artifact, manifest, inventory)
        assert validation_report.status == VALIDATION_STATUS_FAIL
        assert any("README.md" in e for e in validation_report.errors)

    def test_archive_path_traversal_rejected(self):
        assert validate_archive_member_path("../../etc/passwd") is False
        assert validate_archive_member_path("../escape.txt") is False

    def test_symlink_escape_rejected(self, tmp_path: Path):
        target = tmp_path / "outside.txt"
        target.write_text("outside")
        link = tmp_path / "link.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this platform")
        manifest = PackageManifest(allow_symlinks=False, require_clean_git=False)
        records = [
            PackageFileRecord(
                relative_path="link.txt",
                absolute_path=str(link),
                included=True,
                is_symlink=True,
                symlink_target="outside.txt",
            ),
        ]
        inventory = PackageInventory(files=records)
        inventory = reject_forbidden_package_files(inventory, manifest, tmp_path)
        rej_codes = {r.reason_code for r in inventory.rejections}
        assert any("SYMLINK" in rc for rc in rej_codes)

    def test_network_install_blocks_by_default(self, tmp_path: Path):
        import tarfile, gzip
        pkg = tmp_path / "pkg.tar.gz"
        with gzip.GzipFile(str(pkg), "wb", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w|") as tar:
                info = tarfile.TarInfo(name="README.md")
                info.type = tarfile.REGTYPE
                info.size = 3
                tar.addfile(info, fileobj=None)
        manifest = PackageManifest(allow_network_for_install_validation=False)
        report = validate_local_install(pkg, manifest, tmp_path)
        assert report.network_allowed is False
