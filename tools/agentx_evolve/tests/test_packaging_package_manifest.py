import pytest
from agentx_evolve.packaging.package_manifest import PackageManifest


class TestPackageManifest:
    def test_defaults(self):
        m = PackageManifest()
        assert m.manifest_id == ""
        assert m.files == []

    def test_add_file(self):
        m = PackageManifest()
        m.add_file("src/main.py", "abc")
        assert len(m.files) == 1
        assert m.files[0]["path"] == "src/main.py"

    def test_add_file_dedup(self):
        m = PackageManifest()
        m.add_file("src/main.py", "abc")
        m.add_file("src/main.py", "abc")
        assert len(m.files) == 1

    def test_validate_missing_file(self):
        m = PackageManifest()
        m.add_file("/nonexistent/file.py", "abc")
        result = m.validate()
        assert result["valid"] is False
        assert len(result["missing_files"]) > 0
