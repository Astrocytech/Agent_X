import json
import re
from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PACKAGE_STATUS_READY, PACKAGE_STATUS_BUILT, PACKAGE_STATUS_VALIDATED,
    PACKAGE_STATUS_BLOCKED, PACKAGE_STATUS_FAILED, PACKAGE_STATUS_PARTIAL,
    ALL_PACKAGE_STATUSES,
    PACKAGE_FORMAT_TAR_GZ, PACKAGE_FORMAT_ZIP, PACKAGE_FORMAT_DIRECTORY,
    ALL_PACKAGE_FORMATS,
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_PARTIAL, VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_BLOCKED, VALIDATION_STATUS_NOT_CHECKED,
    VALIDATION_STATUS_NOT_RUN, VALIDATION_STATUS_NOT_APPLICABLE,
    VALIDATION_STATUS_DEFERRED, ALL_VALIDATION_STATUSES,
    REJECTION_SECRET, REJECTION_RUNTIME_ARTIFACT, REJECTION_CACHE,
    REJECTION_ENV_FILE, REJECTION_UNTRACKED, REJECTION_DIRTY_TREE,
    REJECTION_FORBIDDEN_PATH, REJECTION_FORBIDDEN_EXTENSION,
    REJECTION_SYMLINK_ESCAPE, REJECTION_ARCHIVE_ESCAPE,
    REJECTION_ABSOLUTE_PATH, REJECTION_PARENT_TRAVERSAL,
    REJECTION_DEPENDENCY_UNLOCKED, REJECTION_SCHEMA_INVALID,
    REJECTION_NETWORK_REQUIRED, REJECTION_PUBLISH_ATTEMPT,
    ALL_REJECTION_CODES,
    SEVERITY_BLOCKER, SEVERITY_WARNING, SEVERITY_INFO, ALL_SEVERITIES,
    INSTALL_MODE_ARCHIVE_EXTRACT, INSTALL_MODE_PYTHON_COMPILE,
    INSTALL_MODE_PIP_INSTALL, ALL_INSTALL_MODES,
    PackageManifest, PackageFileRecord, PackageRejection, PackageInventory,
    PackageBuildReport, PackageValidationReport, ArtifactHashRecord,
    ArtifactHashManifest, PackageProvenance, DependencyLockReport,
    DependencyInventory, LicenseNoticeReport, ReproducibilityReport,
    InstallValidationReport, ReleaseBundleManifest, DistributionEvidence,
    PackagingEvidenceManifest, PackagingCompletionRecord, CommandRecord,
    to_dict, new_id, utc_now_iso, canonical_json, sha256_bytes, sha256_file,
    sha256_dict, redact_sensitive_text, normalize_archive_path, is_env_file,
    is_cache_file, is_runtime_artifact, is_secret_file,
    is_forbidden_extension, is_archive_escape, has_secret_like_content,
    SCHEMA_VERSION, SOURCE_COMPONENT, COMPONENT_ID,
)


class TestConstants:
    def test_package_status_constants(self):
        assert PACKAGE_STATUS_READY == "READY"
        assert PACKAGE_STATUS_BUILT == "BUILT"
        assert PACKAGE_STATUS_VALIDATED == "VALIDATED"
        assert PACKAGE_STATUS_BLOCKED == "BLOCKED"
        assert PACKAGE_STATUS_FAILED == "FAILED"
        assert PACKAGE_STATUS_PARTIAL == "PARTIAL"
        assert len(ALL_PACKAGE_STATUSES) == 6

    def test_package_format_constants(self):
        assert PACKAGE_FORMAT_TAR_GZ == "tar.gz"
        assert PACKAGE_FORMAT_ZIP == "zip"
        assert PACKAGE_FORMAT_DIRECTORY == "directory"
        assert len(ALL_PACKAGE_FORMATS) == 3

    def test_validation_status_constants(self):
        assert VALIDATION_STATUS_PASS == "PASS"
        assert VALIDATION_STATUS_PARTIAL == "PARTIAL"
        assert VALIDATION_STATUS_FAIL == "FAIL"
        assert VALIDATION_STATUS_BLOCKED == "BLOCKED"
        assert VALIDATION_STATUS_NOT_CHECKED == "NOT CHECKED"
        assert VALIDATION_STATUS_NOT_RUN == "NOT RUN"
        assert VALIDATION_STATUS_NOT_APPLICABLE == "NOT APPLICABLE"
        assert VALIDATION_STATUS_DEFERRED == "DEFERRED SAFELY"
        assert len(ALL_VALIDATION_STATUSES) == 8

    def test_rejection_constants(self):
        assert REJECTION_SECRET == "SECRET_DETECTED"
        assert REJECTION_RUNTIME_ARTIFACT == "RUNTIME_ARTIFACT"
        assert REJECTION_CACHE == "CACHE_FILE"
        assert REJECTION_ENV_FILE == "ENV_FILE"
        assert REJECTION_UNTRACKED == "UNTRACKED_FILE"
        assert REJECTION_DIRTY_TREE == "DIRTY_WORKING_TREE"
        assert REJECTION_FORBIDDEN_PATH == "FORBIDDEN_PATH"
        assert REJECTION_FORBIDDEN_EXTENSION == "FORBIDDEN_EXTENSION"
        assert REJECTION_SYMLINK_ESCAPE == "SYMLINK_ESCAPE"
        assert REJECTION_ARCHIVE_ESCAPE == "ARCHIVE_ESCAPE"
        assert REJECTION_ABSOLUTE_PATH == "ABSOLUTE_PATH"
        assert REJECTION_PARENT_TRAVERSAL == "PARENT_TRAVERSAL"
        assert REJECTION_DEPENDENCY_UNLOCKED == "DEPENDENCY_UNLOCKED"
        assert REJECTION_SCHEMA_INVALID == "SCHEMA_INVALID"
        assert REJECTION_NETWORK_REQUIRED == "NETWORK_REQUIRED"
        assert REJECTION_PUBLISH_ATTEMPT == "PUBLISH_ATTEMPT"
        assert len(ALL_REJECTION_CODES) == 16

    def test_severity_constants(self):
        assert SEVERITY_BLOCKER == "BLOCKER"
        assert SEVERITY_WARNING == "WARNING"
        assert SEVERITY_INFO == "INFO"
        assert len(ALL_SEVERITIES) == 3

    def test_install_mode_constants(self):
        assert INSTALL_MODE_ARCHIVE_EXTRACT == "archive_extract_only"
        assert INSTALL_MODE_PYTHON_COMPILE == "python_compile_only"
        assert INSTALL_MODE_PIP_INSTALL == "local_pip_install_no_deps"
        assert len(ALL_INSTALL_MODES) == 3


class TestPackageManifest:
    def test_default_values(self):
        m = PackageManifest()
        assert m.schema_version == SCHEMA_VERSION
        assert m.schema_id == "package_manifest.schema.json"
        assert m.manifest_id == ""
        assert m.package_name == "agentx"
        assert m.package_version == "0.1.0"
        assert m.source_root == "."
        assert "README.md" in m.include_patterns
        assert ".git/**" in m.exclude_patterns
        assert "README.md" in m.required_files
        assert m.default_package_format == "tar.gz"
        assert m.require_clean_git is True
        assert m.allow_symlinks is False
        assert m.warnings == []
        assert m.errors == []

    def test_custom_values(self):
        m = PackageManifest(package_name="myapp", package_version="2.0.0",
                            manifest_id="m1", errors=["err1"])
        assert m.package_name == "myapp"
        assert m.package_version == "2.0.0"
        assert m.manifest_id == "m1"
        assert m.errors == ["err1"]


class TestPackageFileRecord:
    def test_all_fields(self):
        r = PackageFileRecord(
            relative_path="src/main.py",
            absolute_path="/repo/src/main.py",
            file_size_bytes=1024,
            sha256="a" * 64,
            included=True,
            source_tracked=True,
            is_symlink=False,
            symlink_target=None,
            normalized_archive_path="src/main.py",
            reason="included",
        )
        assert r.relative_path == "src/main.py"
        assert r.absolute_path == "/repo/src/main.py"
        assert r.file_size_bytes == 1024
        assert r.sha256 == "a" * 64
        assert r.included is True
        assert r.source_tracked is True
        assert r.is_symlink is False
        assert r.symlink_target is None
        assert r.normalized_archive_path == "src/main.py"
        assert r.reason == "included"

    def test_defaults(self):
        r = PackageFileRecord()
        assert r.relative_path == ""
        assert r.absolute_path == ""
        assert r.file_size_bytes == 0
        assert r.sha256 is None
        assert r.included is False
        assert r.warnings == []
        assert r.errors == []


class TestPackageRejection:
    def test_all_fields(self):
        r = PackageRejection(
            rejection_id="rej_abc",
            created_at="2025-01-01T00:00:00.000000Z",
            relative_path=".env",
            reason_code="ENV_FILE",
            reason="Environment file rejected",
            severity=SEVERITY_BLOCKER,
            safe_detail="File is an env file",
        )
        assert r.rejection_id == "rej_abc"
        assert r.relative_path == ".env"
        assert r.reason_code == "ENV_FILE"
        assert r.severity == SEVERITY_BLOCKER

    def test_defaults(self):
        r = PackageRejection()
        assert r.rejection_id == ""
        assert r.severity == SEVERITY_BLOCKER
        assert r.warnings == []


class TestPackageInventory:
    def test_all_fields(self):
        rec = PackageFileRecord(relative_path="f.py", included=True)
        rej = PackageRejection(relative_path=".env", reason_code="ENV_FILE")
        inv = PackageInventory(
            inventory_id="inv_1",
            created_at="now",
            manifest_id="m1",
            source_root="/repo",
            files=[rec],
            rejections=[rej],
            selected_count=1,
            rejected_count=1,
        )
        assert inv.inventory_id == "inv_1"
        assert len(inv.files) == 1
        assert len(inv.rejections) == 1
        assert inv.selected_count == 1
        assert inv.rejected_count == 1

    def test_defaults(self):
        inv = PackageInventory()
        assert inv.schema_version == SCHEMA_VERSION
        assert inv.schema_id == "package_inventory.schema.json"
        assert inv.files == []
        assert inv.rejections == []


class TestPackageBuildReport:
    def test_all_fields(self):
        cmd = CommandRecord(name="build", command="make", exit_code=0, status="PASS", summary="ok")
        r = PackageBuildReport(
            report_id="r1", created_at="now", manifest_id="m1",
            package_format="tar.gz", staging_root="/stage",
            package_artifact="/dist/pkg.tar.gz", files_copied=5,
            files_rejected=0, status=PACKAGE_STATUS_BUILT,
            commands_run=[cmd],
        )
        assert r.report_id == "r1"
        assert r.package_format == "tar.gz"
        assert r.status == PACKAGE_STATUS_BUILT
        assert len(r.commands_run) == 1

    def test_defaults(self):
        r = PackageBuildReport()
        assert r.files_copied == 0
        assert r.files_rejected == 0
        assert r.status == ""


class TestPackageValidationReport:
    def test_all_fields(self):
        r = PackageValidationReport(
            report_id="v1", created_at="now", package_artifact="pkg.tar.gz",
            package_format="tar.gz", status=VALIDATION_STATUS_PASS,
            missing_required_files=["README.md"],
            unexpected_files=["extra.py"],
        )
        assert r.report_id == "v1"
        assert r.status == VALIDATION_STATUS_PASS
        assert "README.md" in r.missing_required_files

    def test_defaults(self):
        r = PackageValidationReport()
        assert r.expected_files == []
        assert r.errors == []


class TestArtifactHashRecord:
    def test_all_fields(self):
        r = ArtifactHashRecord(
            artifact_path="/dist/pkg.tar.gz",
            artifact_kind="tar.gz",
            sha256="a" * 64,
            size_bytes=1000,
            created_at="now",
            hash_algorithm="sha256",
        )
        assert r.artifact_path == "/dist/pkg.tar.gz"
        assert r.artifact_kind == "tar.gz"
        assert r.sha256 == "a" * 64
        assert r.size_bytes == 1000
        assert r.hash_algorithm == "sha256"

    def test_defaults(self):
        r = ArtifactHashRecord()
        assert r.artifact_path == ""
        assert r.sha256 == ""
        assert r.hash_algorithm == "sha256"


class TestArtifactHashManifest:
    def test_all_fields(self):
        rec = ArtifactHashRecord(artifact_path="a.tar.gz", sha256="a" * 64, size_bytes=100, artifact_kind="tar.gz")
        m = ArtifactHashManifest(
            hash_manifest_id="hm1", created_at="now",
            hash_algorithm="sha256", artifacts=[rec],
        )
        assert m.hash_manifest_id == "hm1"
        assert len(m.artifacts) == 1
        assert m.hash_algorithm == "sha256"

    def test_defaults(self):
        m = ArtifactHashManifest()
        assert m.schema_version == SCHEMA_VERSION
        assert m.schema_id == "artifact_hash_manifest.schema.json"
        assert m.artifacts == []


class TestPackageProvenance:
    def test_all_fields(self):
        p = PackageProvenance(
            provenance_id="p1", created_at="now", package_name="agentx",
            package_version="0.1.0", source_commit="abc123",
            source_branch="main", source_tree_status="CLEAN",
            manifest_path="/repo/agentx.json", manifest_sha256="a" * 64,
            build_command="make build", build_environment={"os": "linux"},
            builder_version="1.0", package_artifact="/dist/pkg.tar.gz",
            package_sha256="b" * 64,
        )
        assert p.provenance_id == "p1"
        assert p.package_name == "agentx"
        assert p.source_commit == "abc123"
        assert p.build_environment == {"os": "linux"}

    def test_defaults(self):
        p = PackageProvenance()
        assert p.source_commit is None
        assert p.build_environment == {}
        assert p.warnings == []


class TestDependencyLockReport:
    def test_all_fields(self):
        r = DependencyLockReport(
            report_id="dl1", created_at="now",
            lock_files_found=["poetry.lock"],
            missing_lock_files=[],
            dependency_files_found=["pyproject.toml"],
            unpinned_dependencies=["requests"],
            status=VALIDATION_STATUS_PASS,
        )
        assert r.report_id == "dl1"
        assert r.lock_files_found == ["poetry.lock"]
        assert r.status == VALIDATION_STATUS_PASS

    def test_defaults(self):
        r = DependencyLockReport()
        assert r.status == VALIDATION_STATUS_NOT_CHECKED
        assert r.errors == []


class TestDependencyInventory:
    def test_all_fields(self):
        inv = DependencyInventory(
            inventory_id="di1", created_at="now",
            dependency_files=["pyproject.toml"],
            lock_files=["poetry.lock"],
            resolved_dependencies=[{"name": "click", "version_specifier": "==8.0"}],
            unpinned_dependencies=[],
            network_resolution_used=False,
            status=VALIDATION_STATUS_PASS,
        )
        assert inv.inventory_id == "di1"
        assert len(inv.resolved_dependencies) == 1
        assert inv.network_resolution_used is False

    def test_defaults(self):
        inv = DependencyInventory()
        assert inv.network_resolution_used is False
        assert inv.status == VALIDATION_STATUS_PASS


class TestLicenseNoticeReport:
    def test_all_fields(self):
        r = LicenseNoticeReport(
            report_id="ln1", created_at="now",
            required_license_files=["LICENSE"],
            found_license_files=["LICENSE"],
            missing_license_files=[],
            notice_files=[],
            status=VALIDATION_STATUS_PASS,
        )
        assert r.report_id == "ln1"
        assert r.found_license_files == ["LICENSE"]

    def test_defaults(self):
        r = LicenseNoticeReport()
        assert r.status == VALIDATION_STATUS_NOT_CHECKED
        assert r.errors == []


class TestReproducibilityReport:
    def test_all_fields(self):
        r = ReproducibilityReport(
            report_id="rp1", created_at="now",
            first_build_artifact="/dist/first.tar.gz",
            first_build_sha256="a" * 64,
            second_build_artifact="/dist/second.tar.gz",
            second_build_sha256="a" * 64,
            hashes_match=True, status=VALIDATION_STATUS_PASS,
        )
        assert r.report_id == "rp1"
        assert r.hashes_match is True
        assert r.status == VALIDATION_STATUS_PASS

    def test_defaults(self):
        r = ReproducibilityReport()
        assert r.hashes_match is False
        assert r.status == VALIDATION_STATUS_NOT_CHECKED


class TestInstallValidationReport:
    def test_all_fields(self):
        r = InstallValidationReport(
            report_id="iv1", created_at="now",
            package_artifact="/dist/pkg.tar.gz",
            validation_mode=INSTALL_MODE_ARCHIVE_EXTRACT,
            network_allowed=False, temp_validation_root="/tmp/val",
            status=VALIDATION_STATUS_PASS,
        )
        assert r.report_id == "iv1"
        assert r.validation_mode == INSTALL_MODE_ARCHIVE_EXTRACT
        assert r.network_allowed is False

    def test_defaults(self):
        r = InstallValidationReport()
        assert r.validation_mode == INSTALL_MODE_ARCHIVE_EXTRACT
        assert r.network_allowed is False
        assert r.status == VALIDATION_STATUS_NOT_CHECKED


class TestReleaseBundleManifest:
    def test_all_fields(self):
        m = ReleaseBundleManifest(
            bundle_manifest_id="bm1", created_at="now",
            bundle_name="release_agentx_0.1.0", bundle_version="0.1.0",
            bundle_artifact="/bundle", bundle_sha256="a" * 64,
            included_artifacts=["/dist/pkg.tar.gz"],
            provenance_ref="/prov", evidence_ref="/ev",
        )
        assert m.bundle_manifest_id == "bm1"
        assert m.bundle_name == "release_agentx_0.1.0"
        assert m.promotion_status == "NOT_PROMOTED"

    def test_defaults(self):
        m = ReleaseBundleManifest()
        assert m.included_artifacts == []
        assert m.promotion_status == "NOT_PROMOTED"


class TestDistributionEvidence:
    def test_all_fields(self):
        e = DistributionEvidence(
            evidence_id="de1", created_at="now",
            package_manifest_ref="m1", package_inventory_ref="inv1",
            package_build_report_ref="br1", package_validation_report_ref="vr1",
            hash_manifest_ref="hm1", provenance_ref="p1",
            dependency_lock_report_ref="dl1", install_validation_report_ref="iv1",
            artifact_refs=["/dist/pkg.tar.gz"],
            sha256_refs=[{"path": "/dist/pkg.tar.gz", "sha256": "a" * 64}],
            status=VALIDATION_STATUS_PASS,
        )
        assert e.evidence_id == "de1"
        assert e.status == VALIDATION_STATUS_PASS
        assert len(e.artifact_refs) == 1

    def test_defaults(self):
        e = DistributionEvidence()
        assert e.artifact_refs == []
        assert e.sha256_refs == []


class TestPackagingEvidenceManifest:
    def test_all_fields(self):
        m = PackagingEvidenceManifest(
            evidence_manifest_id="em1", created_at="now",
            validated_commit="abc123",
            evidence_files=["/ev/file.json"],
            evidence_hashes=[{"path": "/ev/file.json", "sha256": "a" * 64}],
            package_artifacts=["/dist/pkg.tar.gz"],
            status=VALIDATION_STATUS_PASS,
        )
        assert m.evidence_manifest_id == "em1"
        assert m.validated_commit == "abc123"
        assert m.source_mutation_status == "CLEAN"

    def test_defaults(self):
        m = PackagingEvidenceManifest()
        assert m.component_id == COMPONENT_ID
        assert m.status == VALIDATION_STATUS_PASS


class TestPackagingCompletionRecord:
    def test_all_fields(self):
        c = PackagingCompletionRecord(
            status=VALIDATION_STATUS_PASS,
            validated_commit="abc123",
            validated_at="now",
            package_artifacts=["/dist/pkg.tar.gz"],
            evidence_refs=["/ev/file.json"],
            hash_refs=[{"path": "/ev/file.json", "sha256": "a" * 64}],
            validated_capabilities=["package_build"],
            final_decision=VALIDATION_STATUS_PASS,
        )
        assert c.status == VALIDATION_STATUS_PASS
        assert c.validated_commit == "abc123"
        assert c.final_decision == VALIDATION_STATUS_PASS
        assert c.component_name == "Packaging / Distribution Layer"

    def test_defaults(self):
        c = PackagingCompletionRecord()
        assert c.final_decision == ""
        assert c.status == ""
        assert c.component_id == COMPONENT_ID


class TestCommandRecord:
    def test_all_fields(self):
        c = CommandRecord(
            name="test", command="pytest", exit_code=0, status="PASS",
            summary="All tests passed", stdout_summary="OK",
            stderr_summary="",
        )
        assert c.name == "test"
        assert c.command == "pytest"
        assert c.exit_code == 0
        assert c.status == "PASS"
        assert c.stdout_summary == "OK"

    def test_defaults(self):
        c = CommandRecord()
        assert c.name == ""
        assert c.exit_code is None
        assert c.warnings == []


class TestToDict:
    def test_serializes_nested_dataclasses(self):
        rec = PackageFileRecord(relative_path="f.py", included=True, file_size_bytes=100)
        inv = PackageInventory(inventory_id="inv1", files=[rec])
        d = to_dict(inv)
        assert d["inventory_id"] == "inv1"
        assert len(d["files"]) == 1
        assert d["files"][0]["relative_path"] == "f.py"
        assert d["files"][0]["included"] is True

    def test_omits_none_values(self):
        rec = PackageFileRecord(relative_path="f.py", sha256=None)
        d = to_dict(rec)
        assert "sha256" not in d

    def test_serializes_empty_list(self):
        inv = PackageInventory()
        d = to_dict(inv)
        assert "files" in d


class TestNewId:
    def test_generates_unique_ids(self):
        id1 = new_id("pkg")
        id2 = new_id("pkg")
        assert id1 != id2

    def test_prefix(self):
        assert new_id("test").startswith("test_")

    def test_default_prefix(self):
        assert new_id().startswith("pkg_")


class TestUtcNowIso:
    def test_returns_iso_string(self):
        result = utc_now_iso()
        assert result.endswith("Z")
        assert "T" in result


class TestCanonicalJson:
    def test_sorted_output(self):
        result = canonical_json({"b": 2, "a": 1})
        assert result == '{"a":1,"b":2}'


class TestSha256Bytes:
    def test_produces_64_char_hex(self):
        result = sha256_bytes(b"hello")
        assert len(result) == 64
        assert re.match(r"^[a-f0-9]{64}$", result)

    def test_accepts_string(self):
        result = sha256_bytes("hello")
        assert len(result) == 64

    def test_deterministic(self):
        assert sha256_bytes(b"test") == sha256_bytes(b"test")


class TestSha256File:
    def test_correct_hash(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = sha256_file(f)
        assert len(result) == 64
        assert re.match(r"^[a-f0-9]{64}$", result)

    def test_deterministic(self, tmp_path: Path):
        f = tmp_path / "a.txt"
        f.write_text("data")
        assert sha256_file(f) == sha256_file(f)


class TestSha256Dict:
    def test_deterministic_hash(self):
        data = {"key": "value", "num": 42}
        assert sha256_dict(data) == sha256_dict(data)

    def test_different_data(self):
        assert sha256_dict({"a": 1}) != sha256_dict({"a": 2})


class TestRedactSensitiveText:
    def test_redacts_api_key(self):
        result = redact_sensitive_text("API_KEY=sk-1234")
        assert "sk-1234" not in result
        assert "***REDACTED***" in result

    def test_redacts_secret(self):
        result = redact_sensitive_text("SECRET=mysecret")
        assert "mysecret" not in result

    def test_redacts_token(self):
        result = redact_sensitive_text("TOKEN=abc123")
        assert "abc123" not in result

    def test_redacts_password(self):
        result = redact_sensitive_text("PASSWORD=hunter2")
        assert "hunter2" not in result

    def test_redacts_private_key_header(self):
        result = redact_sensitive_text("-----BEGIN PRIVATE KEY-----\nbase64data\n-----END PRIVATE KEY-----")
        assert "***REDACTED***" in result

    def test_redacts_rsa_private_key(self):
        result = redact_sensitive_text("-----BEGIN RSA PRIVATE KEY-----")
        assert "***REDACTED***" in result

    def test_no_false_positive(self):
        result = redact_sensitive_text("normal text without secrets")
        assert result == "normal text without secrets"


class TestNormalizeArchivePath:
    def test_normalizes_backslashes(self):
        assert normalize_archive_path("a\\b\\c") == "a/b/c"

    def test_rejects_absolute(self):
        with pytest.raises(ValueError, match="Absolute"):
            normalize_archive_path("/etc/passwd")

    def test_rejects_parent_traversal(self):
        with pytest.raises(ValueError, match="traversal"):
            normalize_archive_path("a/../../etc")

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="Empty"):
            normalize_archive_path("")

    def test_rejects_dot(self):
        with pytest.raises(ValueError, match="root"):
            normalize_archive_path(".")

    def test_normal_path(self):
        assert normalize_archive_path("tools/main.py") == "tools/main.py"


class TestIsEnvFile:
    def test_detects_env(self):
        assert is_env_file(".env") is True

    def test_detects_env_local(self):
        assert is_env_file(".env.local") is True

    def test_rejects_normal_file(self):
        assert is_env_file("main.py") is False


class TestIsCacheFile:
    def test_detects_pycache_dir(self):
        assert is_cache_file("src/__pycache__/cache.py") is True

    def test_detects_pyc_file(self):
        assert is_cache_file("module.pyc") is True

    def test_detects_pytest_cache(self):
        assert is_cache_file(".pytest_cache/data") is True

    def test_detects_mypy_cache(self):
        assert is_cache_file(".mypy_cache/data") is True

    def test_rejects_normal(self):
        assert is_cache_file("src/main.py") is False


class TestIsRuntimeArtifact:
    def test_detects_agentx_init(self):
        assert is_runtime_artifact(".agentx-init/packaging/staging/file") is True

    def test_rejects_normal(self):
        assert is_runtime_artifact("src/main.py") is False


class TestIsSecretFile:
    def test_detects_pem(self):
        assert is_secret_file("key.pem") is True

    def test_detects_key(self):
        assert is_secret_file("private.key") is True

    def test_detects_p12(self):
        assert is_secret_file("cert.p12") is True

    def test_detects_pfx(self):
        assert is_secret_file("cert.pfx") is True

    def test_detects_env(self):
        assert is_secret_file(".env") is True

    def test_detects_credentials_json(self):
        assert is_secret_file("credentials.json") is True

    def test_detects_token_in_name(self):
        assert is_secret_file("git-token.txt") is True

    def test_detects_secret_in_name(self):
        assert is_secret_file("my-secret.txt") is True

    def test_detects_service_account(self):
        assert is_secret_file("service-account-sa.json") is True

    def test_rejects_normal(self):
        assert is_secret_file("main.py") is False


class TestIsForbiddenExtension:
    def test_detects_pem(self):
        assert is_forbidden_extension("file.pem") is True

    def test_detects_key(self):
        assert is_forbidden_extension("file.key") is True

    def test_detects_p12(self):
        assert is_forbidden_extension("file.p12") is True

    def test_detects_pfx(self):
        assert is_forbidden_extension("file.pfx") is True

    def test_case_insensitive(self):
        assert is_forbidden_extension("file.PEM") is True

    def test_rejects_normal(self):
        assert is_forbidden_extension("file.py") is False


class TestIsArchiveEscape:
    def test_absolute_path(self):
        assert is_archive_escape("/etc/passwd") is True

    def test_parent_traversal(self):
        assert is_archive_escape("a/../../etc") is True

    def test_empty(self):
        assert is_archive_escape("") is True

    def test_dot(self):
        assert is_archive_escape(".") is True

    def test_normal_path(self):
        assert is_archive_escape("tools/main.py") is False

    def test_backslash_absolute(self):
        assert is_archive_escape("\\etc\\passwd") is True


class TestHasSecretLikeContent:
    def test_detects_api_key(self):
        assert has_secret_like_content("API_KEY=sk-1234") is True

    def test_detects_secret(self):
        assert has_secret_like_content("SECRET=mysecret") is True

    def test_detects_token(self):
        assert has_secret_like_content("TOKEN=abc") is True

    def test_detects_password(self):
        assert has_secret_like_content("PASSWORD=pass") is True

    def test_detects_private_key(self):
        assert has_secret_like_content("-----BEGIN RSA PRIVATE KEY-----") is True

    def test_detects_aws_key(self):
        assert has_secret_like_content("aws_access_key_id=AKIA") is True

    def test_detects_aws_secret(self):
        assert has_secret_like_content("aws_secret_access_key=abc") is True

    def test_clean_text(self):
        assert has_secret_like_content("print('hello')") is False
