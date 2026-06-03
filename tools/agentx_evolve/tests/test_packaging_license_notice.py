import pytest
from pathlib import Path
from agentx_evolve.packaging.license_notice import detect_license, generate_notice, validate_license


class TestValidateLicense:
    def test_allowed_license(self):
        result = validate_license("MIT")
        assert result["allowed"] is True

    def test_forbidden_license(self):
        result = validate_license("GPL-3.0-only")
        assert result["allowed"] is False
        assert "forbidden" in result["reason"]

    def test_unknown_license(self):
        result = validate_license("Proprietary")
        assert result["allowed"] is False


class TestGenerateNotice:
    def test_empty_deps(self):
        notice = generate_notice([])
        assert "NOTICE" in notice

    def test_with_deps(self):
        deps = [{"name": "requests", "version": "2.28", "license": "Apache-2.0"}]
        notice = generate_notice(deps)
        assert "requests" in notice
        assert "Apache-2.0" in notice


class TestDetectLicense:
    def test_no_license_file(self, tmp_path: Path):
        result = detect_license(tmp_path / "nonexistent")
        assert result["license_file"] is None

    def test_detect_mit(self, tmp_path):
        license_file = tmp_path / "LICENSE"
        license_file.write_text("MIT License")
        result = detect_license(license_file)
        assert result["license_name"] == "MIT"
