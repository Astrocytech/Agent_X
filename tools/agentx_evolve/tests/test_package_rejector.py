from pathlib import Path

import pytest

from agentx_evolve.packaging.package_rejector import (
    reject_forbidden_package_files, scan_for_secret_like_content,
)
from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord,
    REJECTION_RUNTIME_ARTIFACT, REJECTION_CACHE, REJECTION_ENV_FILE,
    REJECTION_SECRET, REJECTION_FORBIDDEN_EXTENSION,
)


def _inv_with_files(files: list[dict]) -> PackageInventory:
    records = [PackageFileRecord(**f) for f in files]
    return PackageInventory(files=records)


class TestRejectRuntimeArtifacts:
    def test_reject_runtime_artifacts(self, tmp_path: Path):
        inv = _inv_with_files([
            {"relative_path": ".agentx-init/packaging/staging/file.txt", "absolute_path": str(tmp_path / "f")},
            {"relative_path": "src/main.py", "absolute_path": str(tmp_path / "src/main.py")},
        ])
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert len(result.files) == 1
        assert result.files[0].relative_path == "src/main.py"
        assert any(r.reason_code == REJECTION_RUNTIME_ARTIFACT for r in result.rejections)


class TestRejectCacheFiles:
    def test_reject_cache_files(self, tmp_path: Path):
        inv = _inv_with_files([
            {"relative_path": "src/__pycache__/mod.pyc", "absolute_path": str(tmp_path / "mod.pyc")},
            {"relative_path": "src/mod.py", "absolute_path": str(tmp_path / "mod.py")},
        ])
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert len(result.files) == 1
        assert any(r.reason_code == REJECTION_CACHE for r in result.rejections)


class TestRejectEnvFiles:
    def test_reject_env_files(self, tmp_path: Path):
        inv = _inv_with_files([
            {"relative_path": ".env", "absolute_path": str(tmp_path / ".env")},
            {"relative_path": ".env.local", "absolute_path": str(tmp_path / ".env.local")},
            {"relative_path": "README.md", "absolute_path": str(tmp_path / "README.md")},
        ])
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert len(result.files) == 1
        assert any(r.reason_code == REJECTION_ENV_FILE for r in result.rejections)


class TestRejectSecretContent:
    def test_reject_secret_content(self, tmp_path: Path):
        secret_file = tmp_path / "config.py"
        secret_file.write_text("API_KEY=sk-1234")
        inv = _inv_with_files([
            {"relative_path": "config.py", "absolute_path": str(secret_file)},
            {"relative_path": "safe.py", "absolute_path": str(tmp_path / "safe.py")},
        ])
        (tmp_path / "safe.py").write_text("x=1")
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert any(r.reason_code == REJECTION_SECRET for r in result.rejections)


class TestRejectForbiddenExtensions:
    def test_reject_forbidden_extensions(self, tmp_path: Path):
        f = tmp_path / "secret.p12"
        f.write_text("data")
        inv = _inv_with_files([
            {"relative_path": "secret.p12", "absolute_path": str(f)},
        ])
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert len(result.files) == 0
        assert any(r.reason_code in (REJECTION_FORBIDDEN_EXTENSION, REJECTION_SECRET) for r in result.rejections)


class TestScanForSecretLikeContent:
    def test_scan_for_secret_like_content(self, tmp_path: Path):
        f = tmp_path / "secret.txt"
        f.write_text("TOKEN=abc123")
        assert scan_for_secret_like_content(f) is True

    def test_clean_file(self, tmp_path: Path):
        f = tmp_path / "clean.txt"
        f.write_text("print('hello')")
        assert scan_for_secret_like_content(f) is False

    def test_nonexistent_file(self, tmp_path: Path):
        assert scan_for_secret_like_content(tmp_path / "missing.txt") is False


class TestRejectDoesNotLogSecrets:
    def test_reject_does_not_log_secrets(self, tmp_path: Path):
        secret_file = tmp_path / "secret_config.py"
        secret_file.write_text("API_KEY=sk-1234567890abcdef")
        inv = _inv_with_files([
            {"relative_path": "secret_config.py", "absolute_path": str(secret_file)},
        ])
        manifest = PackageManifest()
        result = reject_forbidden_package_files(inv, manifest, tmp_path)
        assert len(result.rejections) == 1
        rejection = result.rejections[0]
        assert "sk-1234567890abcdef" not in rejection.safe_detail
        assert "sk-1234567890abcdef" not in rejection.reason
