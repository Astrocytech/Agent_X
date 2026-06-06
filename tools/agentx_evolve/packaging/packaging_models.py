from __future__ import annotations
import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_STATUS_READY = "READY"
PACKAGE_STATUS_BUILT = "BUILT"
PACKAGE_STATUS_VALIDATED = "VALIDATED"
PACKAGE_STATUS_BLOCKED = "BLOCKED"
PACKAGE_STATUS_FAILED = "FAILED"
PACKAGE_STATUS_PARTIAL = "PARTIAL"
ALL_PACKAGE_STATUSES = [
    PACKAGE_STATUS_READY, PACKAGE_STATUS_BUILT, PACKAGE_STATUS_VALIDATED,
    PACKAGE_STATUS_BLOCKED, PACKAGE_STATUS_FAILED, PACKAGE_STATUS_PARTIAL,
]

PACKAGE_FORMAT_TAR_GZ = "tar.gz"
PACKAGE_FORMAT_ZIP = "zip"
PACKAGE_FORMAT_DIRECTORY = "directory"
ALL_PACKAGE_FORMATS = [PACKAGE_FORMAT_TAR_GZ, PACKAGE_FORMAT_ZIP, PACKAGE_FORMAT_DIRECTORY]

PACKAGE_MODE_INTERNAL_DEV = "INTERNAL_DEV_BUNDLE"
PACKAGE_MODE_INTERNAL_EVIDENCE = "INTERNAL_EVIDENCE_BUNDLE"
PACKAGE_MODE_SOURCE_ARCHIVE = "SOURCE_ARCHIVE"
PACKAGE_MODE_WHEEL = "WHEEL"
PACKAGE_MODE_SDIST = "SDIST"
PACKAGE_MODE_RELEASE_CANDIDATE = "RELEASE_CANDIDATE_BUNDLE"
PACKAGE_MODE_PUBLIC_RELEASE = "PUBLIC_RELEASE_BUNDLE"
ALL_PACKAGE_MODES = [
    PACKAGE_MODE_INTERNAL_DEV, PACKAGE_MODE_INTERNAL_EVIDENCE,
    PACKAGE_MODE_SOURCE_ARCHIVE, PACKAGE_MODE_WHEEL, PACKAGE_MODE_SDIST,
    PACKAGE_MODE_RELEASE_CANDIDATE, PACKAGE_MODE_PUBLIC_RELEASE,
]

PACKAGE_TYPE_SOURCE_ARCHIVE = "SOURCE_ARCHIVE"
PACKAGE_TYPE_WHEEL = "WHEEL"
PACKAGE_TYPE_SDIST = "SDIST"
PACKAGE_TYPE_INTERNAL_BUNDLE = "INTERNAL_BUNDLE"
ALL_PACKAGE_TYPES = [
    PACKAGE_TYPE_SOURCE_ARCHIVE, PACKAGE_TYPE_WHEEL,
    PACKAGE_TYPE_SDIST, PACKAGE_TYPE_INTERNAL_BUNDLE,
]

REJECTION_SECRET = "SECRET_DETECTED"
REJECTION_RUNTIME_ARTIFACT = "RUNTIME_ARTIFACT"
REJECTION_CACHE = "CACHE_FILE"
REJECTION_ENV_FILE = "ENV_FILE"
REJECTION_UNTRACKED = "UNTRACKED_FILE"
REJECTION_DIRTY_TREE = "DIRTY_WORKING_TREE"
REJECTION_FORBIDDEN_PATH = "FORBIDDEN_PATH"
REJECTION_FORBIDDEN_EXTENSION = "FORBIDDEN_EXTENSION"
REJECTION_SYMLINK_ESCAPE = "SYMLINK_ESCAPE"
REJECTION_ARCHIVE_ESCAPE = "ARCHIVE_ESCAPE"
REJECTION_ABSOLUTE_PATH = "ABSOLUTE_PATH"
REJECTION_PARENT_TRAVERSAL = "PARENT_TRAVERSAL"
REJECTION_DEPENDENCY_UNLOCKED = "DEPENDENCY_UNLOCKED"
REJECTION_SCHEMA_INVALID = "SCHEMA_INVALID"
REJECTION_NETWORK_REQUIRED = "NETWORK_REQUIRED"
REJECTION_PUBLISH_ATTEMPT = "PUBLISH_ATTEMPT"
ALL_REJECTION_CODES = [
    REJECTION_SECRET, REJECTION_RUNTIME_ARTIFACT, REJECTION_CACHE,
    REJECTION_ENV_FILE, REJECTION_UNTRACKED, REJECTION_DIRTY_TREE,
    REJECTION_FORBIDDEN_PATH, REJECTION_FORBIDDEN_EXTENSION,
    REJECTION_SYMLINK_ESCAPE, REJECTION_ARCHIVE_ESCAPE,
    REJECTION_ABSOLUTE_PATH, REJECTION_PARENT_TRAVERSAL,
    REJECTION_DEPENDENCY_UNLOCKED, REJECTION_SCHEMA_INVALID,
    REJECTION_NETWORK_REQUIRED, REJECTION_PUBLISH_ATTEMPT,
]

SEVERITY_BLOCKER = "BLOCKER"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"
ALL_SEVERITIES = [SEVERITY_BLOCKER, SEVERITY_WARNING, SEVERITY_INFO]

INSTALL_MODE_ARCHIVE_EXTRACT = "archive_extract_only"
INSTALL_MODE_PYTHON_COMPILE = "python_compile_only"
INSTALL_MODE_PIP_INSTALL = "local_pip_install_no_deps"
ALL_INSTALL_MODES = [
    INSTALL_MODE_ARCHIVE_EXTRACT, INSTALL_MODE_PYTHON_COMPILE,
    INSTALL_MODE_PIP_INSTALL,
]

VALIDATION_STATUS_PASS = "PASS"
VALIDATION_STATUS_WARNING = "WARNING"
VALIDATION_STATUS_PARTIAL = "PARTIAL"
VALIDATION_STATUS_FAIL = "FAIL"
VALIDATION_STATUS_BLOCKED = "BLOCKED"
VALIDATION_STATUS_NOT_CHECKED = "NOT CHECKED"
VALIDATION_STATUS_NOT_RUN = "NOT RUN"
VALIDATION_STATUS_NOT_APPLICABLE = "NOT APPLICABLE"
VALIDATION_STATUS_DEFERRED = "DEFERRED SAFELY"
ALL_VALIDATION_STATUSES = [
    VALIDATION_STATUS_PASS, VALIDATION_STATUS_PARTIAL, VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_BLOCKED, VALIDATION_STATUS_NOT_CHECKED,
    VALIDATION_STATUS_NOT_RUN, VALIDATION_STATUS_NOT_APPLICABLE,
    VALIDATION_STATUS_DEFERRED,
]

WORKING_TREE_CLEAN = "CLEAN"
WORKING_TREE_EXPECTED = "EXPECTED_RUNTIME_ARTIFACTS_ONLY"
WORKING_TREE_DIRTY = "DIRTY"
ALL_WORKING_TREE_STATUSES = [WORKING_TREE_CLEAN, WORKING_TREE_EXPECTED, WORKING_TREE_DIRTY]

PACKAGE_NAME = "agentx"
PACKAGE_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0"
SOURCE_COMPONENT = "PackagingDistribution"
COMPONENT_ID = "AGENTX_PACKAGING_DISTRIBUTION"

CANONICAL_SUBDIRECTORY = "tools/agentx_evolve/packaging/"
CANONICAL_SCHEMA_SUBDIRECTORY = "tools/agentx_evolve/schemas/"
CANONICAL_TEST_SUBDIRECTORY = "tools/agentx_evolve/tests/"
RUNTIME_ARTIFACT_ROOT = ".agentx-init/packaging/"

SECRET_PATTERNS: list[re.Pattern] = [
    re.compile(r"API_KEY\s*=", re.IGNORECASE),
    re.compile(r"SECRET\s*=", re.IGNORECASE),
    re.compile(r"TOKEN\s*=", re.IGNORECASE),
    re.compile(r"PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"PRIVATE\s+KEY", re.IGNORECASE),
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", re.IGNORECASE),
    re.compile(r"aws_access_key_id", re.IGNORECASE),
    re.compile(r"aws_secret_access_key", re.IGNORECASE),
]

FORBIDDEN_ENV_SUFFIXES = [
    ".env", ".env.local", ".env.production", ".env.development",
    ".env.test", ".env.staging",
]

RUNTIME_ARTIFACT_ROOTS = [
    ".agentx-init/security/",
    ".agentx-init/tool_calls/",
    ".agentx-init/implementation/",
    ".agentx-init/memory/",
    ".agentx-init/packaging/raw/",
    ".agentx-init/packaging/staging/",
    ".agentx-init/packaging/dist/",
    ".agentx-init/packaging/evidence/",
    ".agentx-init/packaging/reports/",
    ".agentx-init/packaging/tmp/",
    ".agentx-init/tmp/",
]

CACHE_DIR_PATTERNS = [
    "__pycache__/", ".pytest_cache/", ".mypy_cache/", ".ruff_cache/",
    ".cache/", "node_modules/", ".venv/", "venv/", ".git/",
]


def utc_now_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"


def new_id(prefix: str = "pkg") -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def to_dict(obj: Any) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for f in obj.__dataclass_fields__:
            val = getattr(obj, f)
            if isinstance(val, list):
                result[f] = [to_dict(v) if hasattr(v, "__dataclass_fields__") else v for v in val]
            elif isinstance(val, dict):
                result[f] = {k: to_dict(v) if hasattr(v, "__dataclass_fields__") else v for k, v in val.items()}
            elif hasattr(val, "__dataclass_fields__"):
                result[f] = to_dict(val)
            elif val is not None:
                result[f] = val
        return result
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if v is not None}
    return {}


def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_dict(data: dict) -> str:
    return sha256_bytes(canonical_json(data))


def redact_sensitive_text(text: str) -> str:
    text = re.sub(r"(API_KEY\s*=\s*).*", r"\1***REDACTED***", text, flags=re.IGNORECASE)
    text = re.sub(r"(SECRET\s*=\s*).*", r"\1***REDACTED***", text, flags=re.IGNORECASE)
    text = re.sub(r"(TOKEN\s*=\s*).*", r"\1***REDACTED***", text, flags=re.IGNORECASE)
    text = re.sub(r"(PASSWORD\s*=\s*).*", r"\1***REDACTED***", text, flags=re.IGNORECASE)
    text = re.sub(r"(-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----).*", r"\1\n***REDACTED***", text, flags=re.DOTALL)
    return text


def normalize_archive_path(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("/"):
        raise ValueError(f"Absolute archive path rejected: {normalized}")
    if ".." in normalized.split("/"):
        raise ValueError(f"Parent traversal in archive path rejected: {normalized}")
    if normalized == "" or normalized == ".":
        raise ValueError(f"Empty or root archive path rejected: {normalized}")
    parts = [p for p in normalized.split("/") if p and p != "."]
    result = "/".join(parts)
    return result


def write_json_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def write_jsonl_atomic(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "a") as f:
        f.write(canonical_json(data) + "\n")
    tmp.replace(path)
    return path


def is_env_file(relative_path: str) -> bool:
    name = Path(relative_path).name
    for suffix in FORBIDDEN_ENV_SUFFIXES:
        if name == suffix or name.endswith(suffix):
            return True
    return False


def is_cache_file(relative_path: str) -> bool:
    for pattern in CACHE_DIR_PATTERNS:
        if pattern.rstrip("/") in relative_path.split("/"):
            return True
        if pattern.rstrip("/") in relative_path:
            return True
    if relative_path.endswith((".pyc", ".pyo", ".DS_Store")):
        return True
    return False


def is_runtime_artifact(relative_path: str) -> bool:
    for root in RUNTIME_ARTIFACT_ROOTS:
        if relative_path.startswith(root):
            return True
    return False


def is_secret_file(relative_path: str) -> bool:
    name = Path(relative_path).name
    if name in (".env",):
        return True
    if name.endswith((".pem", ".key", ".p12", ".pfx")):
        return True
    if "token" in name.lower() or "secret" in name.lower() or "credential" in name.lower():
        return True
    if name.startswith("service-account") and name.endswith(".json"):
        return True
    if name == "credentials.json":
        return True
    return False


def has_secret_like_content(text: str) -> bool:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return True
    return False


def is_forbidden_extension(relative_path: str) -> bool:
    ext = Path(relative_path).suffix.lower()
    return ext in (".pem", ".key", ".p12", ".pfx")


def is_archive_escape(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("/"):
        return True
    parts = normalized.split("/")
    if ".." in parts:
        return True
    if normalized == "" or normalized == ".":
        return True
    return False


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def packaging_runs_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging"


def staging_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging" / "staging"


def dist_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging" / "dist"


def evidence_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging" / "evidence"


def reports_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging" / "reports"


def tmp_dir(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "packaging" / "tmp"


@dataclass
class PackageManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_manifest.schema.json"
    manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    package_name: str = PACKAGE_NAME
    package_version: str = PACKAGE_VERSION
    package_mode: str = PACKAGE_MODE_INTERNAL_DEV
    package_type: str = PACKAGE_TYPE_INTERNAL_BUNDLE
    source_commit: str | None = None
    source_branch: str | None = None
    working_tree_status: str = WORKING_TREE_CLEAN
    source_root: str = "."
    approved_source_roots: list[str] = field(default_factory=lambda: ["."])
    approved_output_root: str = ".agentx-init/packaging/dist"
    include_patterns: list[str] = field(default_factory=lambda: [
        "L0/**", "L1/**", "L2/**", "tools/**", "README.md", "Makefile",
    ])
    exclude_patterns: list[str] = field(default_factory=lambda: [
        ".git/**", ".agentx-init/**", "**/__pycache__/**",
        "**/.pytest_cache/**", "**/*.pyc", "**/.DS_Store",
        "**/.env", "**/.env.*",
    ])
    required_files: list[str] = field(default_factory=lambda: ["README.md", "Makefile"])
    forbidden_paths: list[str] = field(default_factory=lambda: [
        ".git", ".agentx-init", ".venv", "venv", "node_modules",
    ])
    forbidden_extensions: list[str] = field(default_factory=lambda: [
        ".pem", ".key", ".p12", ".pfx",
    ])
    forbidden_runtime_roots: list[str] = field(default_factory=lambda: [".agentx-init"])
    forbidden_archive_names: list[str] = field(default_factory=lambda: ["..", "/"])
    allowed_package_formats: list[str] = field(default_factory=lambda: [
        "tar.gz", "zip", "directory",
    ])
    default_package_format: str = "tar.gz"
    require_clean_git: bool = True
    require_tracked_files_only: bool = False
    require_dependency_lock: bool = False
    allow_network_for_install_validation: bool = False
    allow_symlinks: bool = False
    allow_external_symlink_targets: bool = False
    allow_external_publish: bool = False
    build_output_root: str = ".agentx-init/packaging/dist"
    staging_root: str = ".agentx-init/packaging/staging"
    evidence_root: str = ".agentx-init/packaging/evidence"
    report_root: str = ".agentx-init/packaging/reports"
    included_paths: list[str] = field(default_factory=list)
    excluded_paths: list[str] = field(default_factory=list)
    forbidden_path_matches: list[str] = field(default_factory=list)
    symlink_findings: list[dict] = field(default_factory=list)
    secret_findings: list[dict] = field(default_factory=list)
    generated_artifacts: list[str] = field(default_factory=list)
    dependency_lock_refs: list[str] = field(default_factory=list)
    sbom_ref: str | None = None
    license_manifest_ref: str | None = None
    hash_manifest_ref: str | None = None
    provenance_ref: str | None = None
    deviation_register_ref: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageFileRecord:
    relative_path: str = ""
    absolute_path: str = ""
    file_size_bytes: int = 0
    sha256: str | None = None
    included: bool = False
    source_tracked: bool | None = None
    is_symlink: bool = False
    symlink_target: str | None = None
    normalized_archive_path: str = ""
    reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageRejection:
    rejection_id: str = ""
    created_at: str = ""
    relative_path: str = ""
    reason_code: str = ""
    reason: str = ""
    severity: str = SEVERITY_BLOCKER
    safe_detail: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageInventory:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_inventory.schema.json"
    inventory_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    manifest_id: str = ""
    source_root: str = ""
    files: list[PackageFileRecord] = field(default_factory=list)
    rejections: list[PackageRejection] = field(default_factory=list)
    selected_count: int = 0
    rejected_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class CommandRecord:
    name: str = ""
    command: str = ""
    exit_code: int | None = None
    status: str = ""
    summary: str = ""
    stdout_summary: str | None = None
    stderr_summary: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageBuildReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_build_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    manifest_id: str = ""
    package_format: str = ""
    staging_root: str = ""
    package_artifact: str | None = None
    files_copied: int = 0
    files_rejected: int = 0
    status: str = ""
    commands_run: list[CommandRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageValidationReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_validation_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    package_artifact: str = ""
    package_format: str = ""
    expected_files: list[str] = field(default_factory=list)
    actual_files: list[str] = field(default_factory=list)
    missing_required_files: list[str] = field(default_factory=list)
    unexpected_files: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    archive_escape_files: list[str] = field(default_factory=list)
    absolute_path_entries: list[str] = field(default_factory=list)
    runtime_artifacts_found: list[str] = field(default_factory=list)
    secret_like_files_found: list[str] = field(default_factory=list)
    status: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ArtifactHashRecord:
    artifact_path: str = ""
    artifact_kind: str = ""
    sha256: str = ""
    size_bytes: int = 0
    created_at: str = ""
    hash_algorithm: str = "sha256"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ArtifactHashManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "artifact_hash_manifest.schema.json"
    hash_manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    hash_algorithm: str = "sha256"
    artifacts: list[ArtifactHashRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackageProvenance:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_provenance.schema.json"
    provenance_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    package_name: str = ""
    package_version: str = ""
    source_commit: str | None = None
    source_branch: str | None = None
    source_tree_status: str = ""
    manifest_path: str = ""
    manifest_sha256: str = ""
    build_command: str = ""
    build_environment: dict = field(default_factory=dict)
    builder_version: str = ""
    package_artifact: str = ""
    package_sha256: str = ""
    reproducibility_settings: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DependencyLockReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "dependency_lock_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    lock_files_found: list[str] = field(default_factory=list)
    lock_files_required: list[str] = field(default_factory=list)
    missing_lock_files: list[str] = field(default_factory=list)
    dependency_files_found: list[str] = field(default_factory=list)
    unpinned_dependencies: list[str] = field(default_factory=list)
    status: str = VALIDATION_STATUS_NOT_CHECKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DependencyInventory:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "dependency_inventory.schema.json"
    inventory_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    dependency_files: list[str] = field(default_factory=list)
    lock_files: list[str] = field(default_factory=list)
    resolved_dependencies: list[dict] = field(default_factory=list)
    unpinned_dependencies: list[str] = field(default_factory=list)
    network_resolution_used: bool = False
    status: str = VALIDATION_STATUS_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LicenseNoticeReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "license_notice_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    required_license_files: list[str] = field(default_factory=list)
    found_license_files: list[str] = field(default_factory=list)
    missing_license_files: list[str] = field(default_factory=list)
    notice_files: list[str] = field(default_factory=list)
    status: str = VALIDATION_STATUS_NOT_CHECKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SbomMetadata:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "packaging_sbom.schema.json"
    sbom_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    source_commit: str = ""
    package_name: str = ""
    package_version: str = ""
    components: list[dict] = field(default_factory=list)
    generation_mode: str = "BASIC_METADATA"
    status: str = VALIDATION_STATUS_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class LicenseManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "packaging_license_manifest.schema.json"
    license_manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    source_commit: str = ""
    package_name: str = ""
    package_version: str = ""
    declared_project_license: str | None = None
    dependency_license_metadata: list[dict] = field(default_factory=list)
    unknown_licenses: list[dict] = field(default_factory=list)
    forbidden_license_findings: list[dict] = field(default_factory=list)
    status: str = VALIDATION_STATUS_NOT_CHECKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DeviationRegister:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "packaging_deviation_register.schema.json"
    deviation_register_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    source_commit: str = ""
    deviations: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ReproducibilityReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "reproducibility_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    first_build_artifact: str = ""
    first_build_sha256: str = ""
    second_build_artifact: str | None = None
    second_build_sha256: str | None = None
    hashes_match: bool = False
    normalized_timestamp: str | int = "0"
    normalized_permissions: dict = field(default_factory=dict)
    normalized_owner_group: str = "0:0"
    status: str = VALIDATION_STATUS_NOT_CHECKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class InstallValidationReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "install_validation_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    package_artifact: str = ""
    validation_mode: str = INSTALL_MODE_ARCHIVE_EXTRACT
    network_allowed: bool = False
    temp_validation_root: str = ""
    commands_run: list[CommandRecord] = field(default_factory=list)
    status: str = VALIDATION_STATUS_NOT_CHECKED
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ReleaseBundleManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "release_bundle_manifest.schema.json"
    bundle_manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    bundle_name: str = ""
    bundle_version: str = ""
    bundle_artifact: str = ""
    bundle_sha256: str = ""
    included_artifacts: list[str] = field(default_factory=list)
    included_hashes: list[dict] = field(default_factory=list)
    provenance_ref: str = ""
    evidence_ref: str = ""
    promotion_status: str = "NOT_PROMOTED"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DistributionEvidence:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "distribution_evidence.schema.json"
    evidence_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    package_manifest_ref: str = ""
    package_inventory_ref: str = ""
    package_build_report_ref: str = ""
    package_validation_report_ref: str = ""
    hash_manifest_ref: str = ""
    provenance_ref: str = ""
    dependency_lock_report_ref: str = ""
    install_validation_report_ref: str = ""
    release_bundle_manifest_ref: str | None = None
    commands_run: list[CommandRecord] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    sha256_refs: list[dict] = field(default_factory=list)
    rejections: list[dict] = field(default_factory=list)
    status: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackagingEvidenceManifest:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "packaging_evidence_manifest.schema.json"
    evidence_manifest_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    component_id: str = COMPONENT_ID
    validated_commit: str | None = None
    evidence_files: list[str] = field(default_factory=list)
    evidence_hashes: list[dict] = field(default_factory=list)
    package_artifacts: list[str] = field(default_factory=list)
    release_bundle_artifacts: list[str] = field(default_factory=list)
    commands_run: list[CommandRecord] = field(default_factory=list)
    source_mutation_status: str = WORKING_TREE_CLEAN
    network_status: str = VALIDATION_STATUS_PASS
    publish_status: str = VALIDATION_STATUS_NOT_APPLICABLE
    status: str = VALIDATION_STATUS_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DistributionReviewReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "distribution_review_report.schema.json"
    review_report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    reviewed_commit: str = ""
    reviewed_branch: str = ""
    package_name: str = ""
    package_version: str = ""
    package_type: str = ""
    package_artifact_path: str = ""
    package_sha256: str = ""
    manifest_sha256: str = ""
    provenance_sha256: str = ""
    installation_validation_status: str = VALIDATION_STATUS_NOT_CHECKED
    secret_exclusion_status: str = VALIDATION_STATUS_NOT_CHECKED
    runtime_artifact_exclusion_status: str = VALIDATION_STATUS_NOT_CHECKED
    dependency_policy_status: str = VALIDATION_STATUS_NOT_CHECKED
    source_mutation_status: str = VALIDATION_STATUS_NOT_CHECKED
    reproducibility_status: str = VALIDATION_STATUS_NOT_CHECKED
    deviation_register_ref: str | None = None
    accepted_deviations: list[str] = field(default_factory=list)
    rejected_deviations: list[str] = field(default_factory=list)
    final_verdict: str = "NOT DONE"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class StagingCleanlinessReport:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "package_staging_cleanliness_report.schema.json"
    report_id: str = ""
    created_at: str = ""
    source_component: str = SOURCE_COMPONENT
    staging_dir: str = ""
    dist_dir: str = ""
    expected_staging_id: str = ""
    stale_staging_entries: list[str] = field(default_factory=list)
    stale_dist_entries: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    status: str = VALIDATION_STATUS_PASS
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PackagingCompletionRecord:
    schema_version: str = SCHEMA_VERSION
    schema_id: str = "packaging_completion_record.schema.json"
    component_id: str = COMPONENT_ID
    component_name: str = "Packaging / Distribution Layer"
    status: str = ""
    validated_commit: str | None = None
    validated_at: str = ""
    package_artifacts: list[str] = field(default_factory=list)
    release_bundle_artifacts: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    hash_refs: list[dict] = field(default_factory=list)
    commands_run: list[CommandRecord] = field(default_factory=list)
    validated_capabilities: list[str] = field(default_factory=list)
    deviations_from_contract: list[dict] = field(default_factory=list)
    unresolved_risks: list[dict] = field(default_factory=list)
    final_decision: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
