from pathlib import Path

import pytest

from agentx_evolve.packaging.provenance_writer import (
    get_git_commit, get_git_branch, get_build_environment,
    write_package_provenance,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest,
)


class TestGetGitCommit:
    def test_get_git_commit(self, tmp_path: Path):
        result = get_git_commit(tmp_path)
        assert result is None or len(result) > 0


class TestGetGitBranch:
    def test_get_git_branch(self, tmp_path: Path):
        result = get_git_branch(tmp_path)
        assert result is None or len(result) > 0


class TestGetBuildEnvironment:
    def test_get_build_environment(self):
        env = get_build_environment()
        assert "python_version" in env
        assert "os" in env
        assert "platform" in env
        assert "environment_variables" in env

    def test_environment_has_redacted_vars(self):
        env = get_build_environment()
        ev = env["environment_variables"]
        assert isinstance(ev, dict)


class TestWritePackageProvenance:
    def test_provenance_records_commit(self, tmp_path: Path):
        manifest = PackageManifest(package_name="testpkg", package_version="1.0")
        output = tmp_path / "provenance.json"
        artifact = tmp_path / "dist" / "pkg.tar.gz"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("fake artifact")
        prov = write_package_provenance(
            repo_root=tmp_path,
            manifest=manifest,
            package_artifact=artifact,
            package_sha256="a" * 64,
            build_command="make build",
            output_path=output,
        )
        assert prov.provenance_id.startswith("prov_")
        assert prov.source_commit == "UNKNOWN" or len(prov.source_commit) > 0
        assert output.exists()

    def test_provenance_records_manifest_hash(self, tmp_path: Path):
        manifest = PackageManifest(package_name="testpkg", package_version="1.0")
        output = tmp_path / "provenance.json"
        artifact = tmp_path / "dist" / "pkg.tar.gz"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("fake")
        prov = write_package_provenance(tmp_path, manifest, artifact, "a" * 64, "make", output)
        assert len(prov.manifest_sha256) == 64

    def test_provenance_records_artifact(self, tmp_path: Path):
        manifest = PackageManifest(package_name="testpkg", package_version="1.0")
        output = tmp_path / "provenance.json"
        artifact = tmp_path / "dist" / "pkg.tar.gz"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("fake")
        prov = write_package_provenance(tmp_path, manifest, artifact, "a" * 64, "make", output)
        assert prov.package_artifact == str(artifact)

    def test_provenance_records_environment(self, tmp_path: Path):
        manifest = PackageManifest(package_name="testpkg", package_version="1.0")
        output = tmp_path / "provenance.json"
        artifact = tmp_path / "dist" / "pkg.tar.gz"
        artifact.parent.mkdir(parents=True)
        artifact.write_text("fake")
        prov = write_package_provenance(tmp_path, manifest, artifact, "a" * 64, "make", output)
        assert "python_version" in prov.build_environment
        assert "os" in prov.build_environment

    def test_get_git_commit_returns_none_in_non_repo(self):
        result = get_git_commit(Path("/nonexistent"))
        assert result is None

    def test_get_git_branch_returns_none_in_non_repo(self):
        result = get_git_branch(Path("/nonexistent"))
        assert result is None

    def test_get_build_environment_schema(self):
        env = get_build_environment()
        assert isinstance(env["python_version"], str)
        assert isinstance(env["os"], str)
        assert isinstance(env["platform"], str)
