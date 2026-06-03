import json
from pathlib import Path

import jsonschema
import pytest

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def _load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    with open(path) as f:
        return json.load(f)


class TestPackageManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_manifest.schema.json",
            "manifest_id": "m1",
            "package_name": "agentx",
            "package_version": "0.1.0",
            "source_root": ".",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_field_rejects(self):
        schema = _load_schema("package_manifest.schema.json")
        data = {"package_name": "agentx"}
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)

    def test_bad_format_rejects(self):
        schema = _load_schema("package_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_manifest.schema.json",
            "manifest_id": "m1",
            "package_name": "agentx",
            "package_version": "0.1.0",
            "source_root": ".",
            "default_package_format": "exe",
        }
        jsonschema.validate(instance=data, schema=schema)


class TestPackageInventorySchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_inventory.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_inventory.schema.json",
            "inventory_id": "inv1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "manifest_id": "m1",
            "source_root": "/repo",
            "files": [{
                "relative_path": "f.py",
                "absolute_path": "/repo/f.py",
                "file_size_bytes": 100,
                "sha256": "a" * 64,
                "included": True,
            }],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_files_rejects(self):
        schema = _load_schema("package_inventory.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"inventory_id": "inv1"}, schema=schema)


class TestPackageRejectionSchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_rejection.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_rejection.schema.json",
            "rejection_id": "rej1",
            "created_at": "2025-01-01T00:00:00Z",
            "relative_path": ".env",
            "reason_code": "FORBIDDEN_PATH",
            "reason": "Forbidden path",
            "severity": "BLOCKER",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_unknown_reason_code_rejects(self):
        schema = _load_schema("package_rejection.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_rejection.schema.json",
            "rejection_id": "rej1",
            "created_at": "2025-01-01T00:00:00Z",
            "relative_path": ".env",
            "reason_code": "INVALID_CODE",
            "reason": "test",
            "severity": "BLOCKER",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestPackageBuildReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_build_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_build_report.schema.json",
            "report_id": "r1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "manifest_id": "m1",
            "package_format": "tar.gz",
            "staging_root": "/stage",
            "status": "BUILT",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_status_rejects(self):
        schema = _load_schema("package_build_report.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={"status": "INVALID"}, schema=schema)


class TestPackageValidationReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_validation_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_validation_report.schema.json",
            "report_id": "v1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "package_artifact": "/dist/pkg.tar.gz",
            "package_format": "tar.gz",
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_unknown_status_rejects(self):
        schema = _load_schema("package_validation_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_validation_report.schema.json",
            "report_id": "v1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "package_artifact": "/dist/pkg.tar.gz",
            "package_format": "tar.gz",
            "status": "UNKNOWN_STATUS",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestArtifactHashManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("artifact_hash_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "artifact_hash_manifest.schema.json",
            "hash_manifest_id": "hm1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "hash_algorithm": "sha256",
            "artifacts": [{
                "artifact_path": "/dist/pkg.tar.gz",
                "artifact_kind": "tar.gz",
                "sha256": "a" * 64,
                "size_bytes": 100,
                "hash_algorithm": "sha256",
            }],
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_invalid_sha256_rejects(self):
        schema = _load_schema("artifact_hash_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "artifact_hash_manifest.schema.json",
            "hash_manifest_id": "hm1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "hash_algorithm": "sha256",
            "artifacts": [{
                "artifact_path": "/dist/pkg.tar.gz",
                "artifact_kind": "tar.gz",
                "sha256": "not-a-valid-sha256",
                "size_bytes": 100,
                "hash_algorithm": "sha256",
            }],
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestPackageProvenanceSchema:
    def test_valid_accepts(self):
        schema = _load_schema("package_provenance.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "package_provenance.schema.json",
            "provenance_id": "p1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "package_name": "agentx",
            "package_version": "0.1.0",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_sha256_rejects(self):
        schema = _load_schema("package_provenance.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestDependencyLockReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("dependency_lock_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "dependency_lock_report.schema.json",
            "report_id": "dl1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "lock_files_found": [],
            "lock_files_required": [],
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)


class TestInstallValidationReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("install_validation_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "install_validation_report.schema.json",
            "report_id": "iv1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "package_artifact": "/dist/pkg.tar.gz",
            "validation_mode": "archive_extract_only",
            "network_allowed": False,
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_unknown_mode_rejects(self):
        schema = _load_schema("install_validation_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "install_validation_report.schema.json",
            "report_id": "iv1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "package_artifact": "/dist/pkg.tar.gz",
            "validation_mode": "unknown_mode",
            "network_allowed": False,
            "status": "PASS",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=data, schema=schema)


class TestReleaseBundleManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("release_bundle_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "release_bundle_manifest.schema.json",
            "bundle_manifest_id": "bm1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "bundle_name": "release_agentx_0.1.0",
            "bundle_version": "0.1.0",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_hash_rejects(self):
        schema = _load_schema("release_bundle_manifest.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestDistributionEvidenceSchema:
    def test_valid_accepts(self):
        schema = _load_schema("distribution_evidence.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "distribution_evidence.schema.json",
            "evidence_id": "de1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_hash_refs_rejects(self):
        schema = _load_schema("distribution_evidence.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestPackagingEvidenceManifestSchema:
    def test_valid_accepts(self):
        schema = _load_schema("packaging_evidence_manifest.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "packaging_evidence_manifest.schema.json",
            "evidence_manifest_id": "em1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "component_id": "AGENTX_PACKAGING_DISTRIBUTION",
            "validated_commit": "abc123",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_hashes_rejects(self):
        schema = _load_schema("packaging_evidence_manifest.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestPackagingCompletionRecordSchema:
    def test_valid_accepts(self):
        schema = _load_schema("packaging_completion_record.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "packaging_completion_record.schema.json",
            "component_id": "AGENTX_PACKAGING_DISTRIBUTION",
            "component_name": "Packaging / Distribution Layer",
            "status": "PASS",
            "validated_commit": "abc123",
            "validated_at": "2025-01-01T00:00:00Z",
        }
        jsonschema.validate(instance=data, schema=schema)

    def test_missing_final_decision_rejects(self):
        schema = _load_schema("packaging_completion_record.schema.json")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance={}, schema=schema)


class TestDependencyInventorySchema:
    def test_valid_accepts(self):
        schema = _load_schema("dependency_inventory.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "dependency_inventory.schema.json",
            "inventory_id": "di1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)


class TestLicenseNoticeReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("license_notice_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "license_notice_report.schema.json",
            "report_id": "ln1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "required_license_files": ["LICENSE"],
            "found_license_files": [],
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)


class TestReproducibilityReportSchema:
    def test_valid_accepts(self):
        schema = _load_schema("reproducibility_report.schema.json")
        data = {
            "schema_version": "1.0",
            "schema_id": "reproducibility_report.schema.json",
            "report_id": "rp1",
            "created_at": "2025-01-01T00:00:00Z",
            "source_component": "PackagingDistribution",
            "first_build_artifact": "/dist/a.tar.gz",
            "first_build_sha256": "a" * 64,
            "second_build_artifact": "/dist/b.tar.gz",
            "second_build_sha256": "b" * 64,
            "hashes_match": False,
            "status": "PASS",
        }
        jsonschema.validate(instance=data, schema=schema)
