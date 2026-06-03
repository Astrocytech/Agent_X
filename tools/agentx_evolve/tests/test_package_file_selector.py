from pathlib import Path

import pytest

from agentx_evolve.packaging.package_file_selector import (
    select_package_files, normalize_candidate_path,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest,
    PACKAGE_NAME, PACKAGE_VERSION,
)


def _create_repo(repo_root: Path, files: dict[str, str]) -> None:
    for rel_path, content in files.items():
        path = repo_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


class TestSelectIncludesExpectedFiles:
    def test_select_includes_expected_files(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "tools/main.py": "print('hello')",
            "README.md": "# Readme",
            "Makefile": "all:",
        })
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        assert inventory.selected_count >= 3
        rel_paths = {f.relative_path for f in inventory.files}
        assert "tools/main.py" in rel_paths
        assert "README.md" in rel_paths
        assert "Makefile" in rel_paths

    def test_select_sorts_deterministically(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "b.py": "b", "a.py": "a", "c.py": "c",
        })
        manifest = PackageManifest(source_root=".")
        inv1 = select_package_files(tmp_path, manifest)
        inv2 = select_package_files(tmp_path, manifest)
        paths1 = [f.relative_path for f in inv1.files]
        paths2 = [f.relative_path for f in inv2.files]
        assert paths1 == paths2
        assert paths1 == sorted(paths1)

    def test_select_excludes_git(self, tmp_path: Path):
        _create_repo(tmp_path, {
            ".git/config": "[core]",
            "README.md": "# Readme",
        })
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert ".git/config" not in rel_paths

    def test_select_excludes_pycache(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "src/__pycache__/mod.pyc": "",
            "src/mod.py": "code",
        })
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert "src/mod.py" in rel_paths
        assert "src/__pycache__/mod.pyc" not in rel_paths

    def test_select_excludes_env(self, tmp_path: Path):
        _create_repo(tmp_path, {
            ".env": "SECRET=key",
            ".env.local": "TOKEN=t",
            "README.md": "# Readme",
        })
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert ".env" not in rel_paths
        assert ".env.local" not in rel_paths

    def test_select_excludes_runtime_artifacts(self, tmp_path: Path):
        _create_repo(tmp_path, {
            ".agentx-init/packaging/staging/file.txt": "data",
            "README.md": "# Readme",
        })
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        rel_paths = {f.relative_path for f in inventory.files}
        assert ".agentx-init/packaging/staging/file.txt" not in rel_paths

    def test_select_rejects_absolute_paths(self, tmp_path: Path):
        _create_repo(tmp_path, {"README.md": "# Readme"})
        manifest = PackageManifest(source_root=".")
        inventory = select_package_files(tmp_path, manifest)
        for f in inventory.files:
            assert not f.relative_path.startswith("/")


class TestNormalizeCandidatePath:
    def test_normalize_candidate_path(self, tmp_path: Path):
        repo = tmp_path.resolve()
        f = repo / "sub/file.txt"
        f.parent.mkdir(parents=True)
        f.write_text("data")
        result = normalize_candidate_path(repo, f)
        assert result == "sub/file.txt"

    def test_returns_empty_for_outside_path(self, tmp_path: Path):
        repo = tmp_path.resolve()
        outside = tmp_path.parent / "outside.txt"
        outside.write_text("data")
        result = normalize_candidate_path(repo, outside)
        assert result == ""
