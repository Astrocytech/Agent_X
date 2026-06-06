import json
from pathlib import Path

import pytest

from agentx_evolve.packaging.package_manifest_loader import load_package_manifest, validate_package_manifest
from agentx_evolve.packaging.packaging_models import PackageManifest


class TestLoadManifest:
    def test_load_manifest_valid(self, tmp_path: Path):
        data = {
            "package_name": "myapp",
            "package_version": "1.0.0",
            "source_root": "src",
            "manifest_id": "m_001",
        }
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps(data))
        manifest = load_package_manifest(path)
        assert manifest.package_name == "myapp"
        assert manifest.package_version == "1.0.0"
        assert manifest.source_root == "src"
        assert manifest.manifest_id == "m_001"
        assert manifest.errors == []

    def test_load_manifest_missing_required_field(self, tmp_path: Path):
        data = {"source_root": "src"}
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps(data))
        manifest = load_package_manifest(path)
        assert len(manifest.errors) > 0
        assert any("package_name" in e for e in manifest.errors)

    def test_load_manifest_invalid_json(self, tmp_path: Path):
        path = tmp_path / "manifest.json"
        path.write_text("{invalid json}")
        manifest = load_package_manifest(path)
        assert len(manifest.errors) > 0
        assert any("Invalid JSON" in e for e in manifest.errors)

    def test_load_manifest_not_a_dict(self, tmp_path: Path):
        path = tmp_path / "manifest.json"
        path.write_text(json.dumps(["not", "a", "dict"]))
        manifest = load_package_manifest(path)
        assert len(manifest.errors) > 0

    def test_load_manifest_file_not_found(self, tmp_path: Path):
        manifest = load_package_manifest(tmp_path / "nonexistent.json")
        assert len(manifest.errors) > 0


class TestValidateManifest:
    def test_validate_manifest_valid(self):
        m = PackageManifest(package_name="x", package_version="1.0")
        errors = validate_package_manifest(m)
        assert errors == []

    def test_validate_manifest_bad_format(self):
        m = PackageManifest(default_package_format="exe")
        errors = validate_package_manifest(m)
        assert any("default_package_format" in e for e in errors)

    def test_validate_manifest_bad_output_root(self):
        m = PackageManifest(build_output_root="/tmp/outside")
        errors = validate_package_manifest(m)
        assert any("build_output_root" in e for e in errors)

    def test_validate_manifest_empty_required_files(self):
        m = PackageManifest(required_files=[])
        errors = validate_package_manifest(m)
        assert any("README" in e for e in errors)
        assert any("Makefile" in e for e in errors)

    def test_validate_manifest_with_schema_path(self, tmp_path: Path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text(json.dumps({"type": "object"}))
        m = PackageManifest()
        errors = validate_package_manifest(m, schema_path=schema_path)
        assert errors == []

    def test_validate_manifest_schema_not_found(self, tmp_path: Path):
        m = PackageManifest()
        errors = validate_package_manifest(m, schema_path=tmp_path / "missing.json")
        assert any("Schema file not found" in e for e in errors)

    def test_validate_manifest_schema_invalid_json(self, tmp_path: Path):
        schema_path = tmp_path / "schema.json"
        schema_path.write_text("not json")
        m = PackageManifest()
        errors = validate_package_manifest(m, schema_path=schema_path)
        assert any("not valid JSON" in e for e in errors)
