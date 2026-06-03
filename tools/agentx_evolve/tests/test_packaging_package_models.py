import pytest
from agentx_evolve.packaging.package_models import PackageInfo, PackageBuildInfo, PackageValidationResult


class TestPackageInfo:
    def test_defaults(self):
        info = PackageInfo()
        assert info.name == ""
        assert info.version == ""
        assert info.sha256 == ""


class TestPackageBuildInfo:
    def test_defaults(self):
        info = PackageBuildInfo()
        assert info.build_id == ""
        assert info.format == "tar.gz"
        assert info.status == ""


class TestPackageValidationResult:
    def test_defaults(self):
        result = PackageValidationResult()
        assert result.validation_id == ""
        assert result.status == "NOT_CHECKED"
        assert result.checks_passed == []
        assert result.checks_failed == []
