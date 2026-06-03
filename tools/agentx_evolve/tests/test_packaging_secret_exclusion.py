from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PackageFileRecord,
    REJECTION_SECRET,
)
from agentx_evolve.packaging.secret_exclusion import (
    scan_secrets_in_files,
    verify_no_secrets,
)


class TestScanSecretsInFiles:
    def test_detects_secret_by_filename(self, tmp_path: Path):
        secret_file = tmp_path / "credentials.json"
        secret_file.write_text("{}")
        files = [
            PackageFileRecord(relative_path="credentials.json", absolute_path=str(secret_file)),
            PackageFileRecord(relative_path="README.md", absolute_path=str(tmp_path / "README.md")),
        ]
        (tmp_path / "README.md").write_text("hello")
        rejections = scan_secrets_in_files(files, tmp_path)
        assert len(rejections) == 1
        assert rejections[0].reason_code == REJECTION_SECRET

    def test_detects_secret_by_content(self, tmp_path: Path):
        f = tmp_path / "config.py"
        f.write_text("API_KEY = sk-1234567890123456789012345678901234567890")
        files = [
            PackageFileRecord(relative_path="config.py", absolute_path=str(f)),
        ]
        rejections = scan_secrets_in_files(files, tmp_path)
        assert len(rejections) == 1
        assert rejections[0].reason_code == REJECTION_SECRET

    def test_clean_files_return_empty(self, tmp_path: Path):
        f = tmp_path / "main.py"
        f.write_text("print('hello')")
        files = [
            PackageFileRecord(relative_path="main.py", absolute_path=str(f)),
        ]
        rejections = scan_secrets_in_files(files, tmp_path)
        assert rejections == []

    def test_empty_list(self, tmp_path: Path):
        assert scan_secrets_in_files([], tmp_path) == []


class TestVerifyNoSecrets:
    def test_clean_returns_true(self, tmp_path: Path):
        f = tmp_path / "main.py"
        f.write_text("x = 1")
        files = [PackageFileRecord(relative_path="main.py", absolute_path=str(f))]
        assert verify_no_secrets(files, tmp_path) is True

    def test_with_secret_returns_false(self, tmp_path: Path):
        f = tmp_path / "secret.txt"
        f.write_text("TOKEN = abc123")
        files = [PackageFileRecord(relative_path="secret.txt", absolute_path=str(f))]
        assert verify_no_secrets(files, tmp_path) is False
