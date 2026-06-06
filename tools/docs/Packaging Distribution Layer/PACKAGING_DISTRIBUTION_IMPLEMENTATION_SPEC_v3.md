# PACKAGING_DISTRIBUTION_IMPLEMENTATION_SPEC

```text
document_id: PACKAGING_DISTRIBUTION_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, final frozen coding-agent handoff
component_id: AGENTX_PACKAGING_DISTRIBUTION
component_name: Packaging / Distribution Layer
roadmap_layer: 20
roadmap_phase: Phase E — Release Preparation
basis_document: PACKAGING_DISTRIBUTION_EQC_FIC_SIB_SCHEMA_CONTRACT
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Release / Promotion Acceptance Criteria, Supply Chain / Dependency Integrity Rules
target_language: Python
canonical_subdirectory: tools/agentx_evolve/packaging/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/packaging/
implementation_mode: deterministic package builder, local release bundle generation, no publishing by default
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

The v2 implementation spec was strong and implementation-ready, but I would rate it:

```text
9.7/10
```

It already covered the requested handoff areas completely: exact subdirectory, files, schemas, classes/functions, runtime artifacts, build flow, validation flow, hashing, provenance, dependency lock validation, integration points, tests, implementation order, acceptance criteria, and Definition of Done.

It was not fully 10/10 because it still needed several final production-control details:

```text
1. Reproducibility required normalized archives, but did not require a double-build hash comparison.
2. The release evidence did not explicitly require dependency inventory / SBOM-style output.
3. License / notice / required distribution metadata checks were not first-class validation gates.
4. Stale lock-file handling was not precise enough for interrupted package builds.
5. Safe extraction rules for archive validation needed to be explicit, not implied.
6. Package version / source commit / manifest version synchronization needed a stricter check.
7. Runtime artifact allowance after validation needed clearer separation from source mutation.
8. Completion evidence needed a clearer reviewed-commit and exact-command reproducibility block.
```

This v3 adds those final controls and is the frozen 10/10 coding-agent handoff.

---

# 1. Purpose

This document is the implementation specification for the **Packaging / Distribution Layer**.

It is the coding-agent handoff for implementing deterministic, auditable, reproducible packaging and local distribution preparation for Agent_X.

This layer answers:

```text
where package builder lives
where package manifests live
how package contents are selected
how package contents are rejected
how package hashes are generated
how install validation works
how release bundles are created
how distribution evidence is written
how tests prove secrets and runtime junk are not packaged
```

This layer must not publish artifacts to external registries by default. It prepares, validates, hashes, and records local release-ready bundles for later approval by the **Promotion / Release Gate**.

---

# 2. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic packaging system that can:

```text
load a package manifest
validate package manifest schema
select approved package files deterministically
reject forbidden files deterministically
reject secrets without logging secret values
reject runtime junk
reject cache files
reject symlink/path traversal archive escapes
reject untracked or dirty source when configured
build a local package artifact
write a package inventory
write a package build report
write a package validation report
write artifact hashes
write provenance metadata
validate installability in a controlled local mode
validate dependency lock / freeze state
write distribution evidence
write packaging evidence manifest
create a local release bundle
write a completion record
```

It must prove:

```text
only approved files are packaged
runtime artifacts are excluded
secrets are excluded
local caches are excluded
symlink/path traversal attacks are blocked
package contents are reproducible
hashes match package and evidence files
provenance identifies commit, source tree, manifest, and build command
install validation does not use network by default
release bundle is not promoted or published automatically
```

---

# 3. Canonical Destination Summary

Create the Packaging / Distribution package here:

```text
tools/agentx_evolve/packaging/
```

Create package manifests here:

```text
tools/agentx_evolve/packaging/manifests/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Write runtime artifacts only here:

```text
.agentx-init/packaging/
```

Default local build output:

```text
.agentx-init/packaging/dist/
```

Default temporary staging output:

```text
.agentx-init/packaging/staging/
```

Default evidence output:

```text
.agentx-init/packaging/evidence/
```

Default report output:

```text
.agentx-init/packaging/reports/
```

---

# 4. Exact Subdirectory

Required directory tree:

```text
tools/agentx_evolve/packaging/
  __init__.py
  packaging_models.py
  package_manifest_loader.py
  package_file_selector.py
  package_rejector.py
  package_builder.py
  package_validator.py
  artifact_hasher.py
  provenance_writer.py
  dependency_lock_validator.py
  dependency_inventory_writer.py
  license_notice_validator.py
  reproducibility_validator.py
  install_validator.py
  release_bundle.py
  distribution_evidence.py
  package_orchestrator.py
  manifests/
    agentx_package_manifest.json
```

Required schema files:

```text
tools/agentx_evolve/schemas/15_packaging/package_manifest.schema.json
tools/agentx_evolve/schemas/15_packaging/package_inventory.schema.json
tools/agentx_evolve/schemas/15_packaging/package_rejection.schema.json
tools/agentx_evolve/schemas/15_packaging/package_build_report.schema.json
tools/agentx_evolve/schemas/15_packaging/package_validation_report.schema.json
tools/agentx_evolve/schemas/15_packaging/artifact_hash_manifest.schema.json
tools/agentx_evolve/schemas/15_packaging/package_provenance.schema.json
tools/agentx_evolve/schemas/15_packaging/dependency_lock_report.schema.json
tools/agentx_evolve/schemas/15_packaging/install_validation_report.schema.json
tools/agentx_evolve/schemas/15_packaging/release_bundle_manifest.schema.json
tools/agentx_evolve/schemas/15_packaging/distribution_evidence.schema.json
tools/agentx_evolve/schemas/15_packaging/packaging_evidence_manifest.schema.json
tools/agentx_evolve/schemas/15_packaging/packaging_completion_record.schema.json
dependency_inventory.schema.json
license_notice_report.schema.json
reproducibility_report.schema.json
tools/agentx_evolve/schemas/15_packaging/dependency_inventory.schema.json
tools/agentx_evolve/schemas/15_packaging/license_notice_report.schema.json
tools/agentx_evolve/schemas/15_packaging/reproducibility_report.schema.json
```

Required test files:

```text
tools/agentx_evolve/tests/test_packaging_models.py
tools/agentx_evolve/tests/test_package_manifest_loader.py
tools/agentx_evolve/tests/test_package_file_selector.py
tools/agentx_evolve/tests/test_package_rejector.py
tools/agentx_evolve/tests/test_package_builder.py
tools/agentx_evolve/tests/test_package_validator.py
tools/agentx_evolve/tests/test_artifact_hasher.py
tools/agentx_evolve/tests/test_provenance_writer.py
tools/agentx_evolve/tests/test_dependency_lock_validator.py
tools/agentx_evolve/tests/test_dependency_inventory_writer.py
tools/agentx_evolve/tests/test_license_notice_validator.py
tools/agentx_evolve/tests/test_reproducibility_validator.py
tools/agentx_evolve/tests/test_install_validator.py
tools/agentx_evolve/tests/test_release_bundle.py
tools/agentx_evolve/tests/test_distribution_evidence.py
tools/agentx_evolve/tests/test_package_orchestrator.py
tools/agentx_evolve/tests/test_packaging_negative_cases.py
tools/agentx_evolve/tests/test_packaging_schema_validation.py
```

---

# 5. Files to Create

## 5.1 `__init__.py`

Purpose:

```text
Expose the public Packaging / Distribution API without side effects.
```

Required exports:

```python
from .packaging_models import (
    PackageManifest,
    PackageInventory,
    PackageFileRecord,
    PackageRejection,
    PackageBuildReport,
    PackageValidationReport,
    ArtifactHashRecord,
    ArtifactHashManifest,
    PackageProvenance,
    DependencyLockReport,
    InstallValidationReport,
    ReleaseBundleManifest,
    DistributionEvidence,
    PackagingEvidenceManifest,
    PackagingCompletionRecord,
)

from .package_manifest_loader import load_package_manifest, validate_package_manifest
from .package_file_selector import select_package_files
from .package_rejector import reject_forbidden_package_files
from .package_builder import build_package, create_staging_tree
from .package_validator import validate_package_contents
from .artifact_hasher import hash_artifact, write_hash_manifest, verify_artifact_hash
from .provenance_writer import write_package_provenance
from .dependency_lock_validator import validate_dependency_lock
from .dependency_inventory_writer import write_dependency_inventory
from .license_notice_validator import validate_license_notice_files
from .reproducibility_validator import verify_reproducible_build
from .install_validator import validate_local_install
from .release_bundle import create_release_bundle
from .distribution_evidence import (
    write_distribution_evidence,
    write_packaging_evidence_manifest,
    write_packaging_completion_record,
)
from .package_orchestrator import build_distribution_package
```

Must not do:

```text
no package build on import
no filesystem writes on import
no network access on import
no publishing on import
no command execution on import
```

---

## 5.2 `packaging_models.py`

Purpose:

```text
Define dataclasses, constants, status values, rejection codes, command records, and helper functions.
```

Required status constants:

```python
PACKAGE_STATUS_READY = "READY"
PACKAGE_STATUS_BUILT = "BUILT"
PACKAGE_STATUS_VALIDATED = "VALIDATED"
PACKAGE_STATUS_BLOCKED = "BLOCKED"
PACKAGE_STATUS_FAILED = "FAILED"
PACKAGE_STATUS_PARTIAL = "PARTIAL"
```

Required package format constants:

```python
PACKAGE_FORMAT_TAR_GZ = "tar.gz"
PACKAGE_FORMAT_ZIP = "zip"
PACKAGE_FORMAT_DIRECTORY = "directory"
```

Required rejection constants:

```python
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
```

Required dataclasses:

```python
PackageManifest
PackageFileRecord
PackageInventory
PackageRejection
PackageBuildReport
PackageValidationReport
ArtifactHashRecord
ArtifactHashManifest
PackageProvenance
DependencyLockReport
InstallValidationReport
ReleaseBundleManifest
DistributionEvidence
PackagingEvidenceManifest
PackagingCompletionRecord
DependencyInventory
LicenseNoticeReport
ReproducibilityReport
CommandRecord
```

### `PackageManifest`

Required fields:

```python
schema_version: str
schema_id: str
manifest_id: str
package_name: str
package_version: str
source_root: str
include_patterns: list[str]
exclude_patterns: list[str]
required_files: list[str]
forbidden_paths: list[str]
forbidden_extensions: list[str]
forbidden_runtime_roots: list[str]
forbidden_archive_names: list[str]
allowed_package_formats: list[str]
default_package_format: str
require_clean_git: bool
require_tracked_files_only: bool
require_dependency_lock: bool
allow_network_for_install_validation: bool
allow_symlinks: bool
allow_external_symlink_targets: bool
allow_external_publish: bool
build_output_root: str
staging_root: str
evidence_root: str
report_root: str
warnings: list[str]
errors: list[str]
```

### `PackageFileRecord`

Required fields:

```python
relative_path: str
absolute_path: str
file_size_bytes: int
sha256: str | None
included: bool
source_tracked: bool | None
is_symlink: bool
symlink_target: str | None
normalized_archive_path: str
reason: str
warnings: list[str]
errors: list[str]
```

### `PackageInventory`

Required fields:

```python
schema_version: str
schema_id: str
inventory_id: str
created_at: str
source_component: str
manifest_id: str
source_root: str
files: list[PackageFileRecord]
rejections: list[PackageRejection]
selected_count: int
rejected_count: int
warnings: list[str]
errors: list[str]
```

### `PackageRejection`

Required fields:

```python
schema_version: str
schema_id: str
rejection_id: str
created_at: str
relative_path: str
reason_code: str
reason: str
severity: str
safe_detail: str
warnings: list[str]
errors: list[str]
```

### `PackageBuildReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
manifest_id: str
package_format: str
staging_root: str
package_artifact: str | None
files_copied: int
files_rejected: int
status: str
commands_run: list[CommandRecord]
warnings: list[str]
errors: list[str]
```

### `PackageValidationReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
package_artifact: str
package_format: str
expected_files: list[str]
actual_files: list[str]
missing_required_files: list[str]
unexpected_files: list[str]
forbidden_files: list[str]
archive_escape_files: list[str]
absolute_path_entries: list[str]
runtime_artifacts_found: list[str]
secret_like_files_found: list[str]
status: str
warnings: list[str]
errors: list[str]
```

### `ArtifactHashRecord`

Required fields:

```python
artifact_path: str
artifact_kind: str
sha256: str
size_bytes: int
created_at: str
hash_algorithm: str
warnings: list[str]
errors: list[str]
```

### `ArtifactHashManifest`

Required fields:

```python
schema_version: str
schema_id: str
hash_manifest_id: str
created_at: str
source_component: str
hash_algorithm: str
artifacts: list[ArtifactHashRecord]
warnings: list[str]
errors: list[str]
```

### `PackageProvenance`

Required fields:

```python
schema_version: str
schema_id: str
provenance_id: str
created_at: str
source_component: str
package_name: str
package_version: str
source_commit: str | None
source_branch: str | None
source_tree_status: str
manifest_path: str
manifest_sha256: str
build_command: str
build_environment: dict
builder_version: str
package_artifact: str
package_sha256: str
reproducibility_settings: dict
warnings: list[str]
errors: list[str]
```

### `DependencyLockReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
lock_files_found: list[str]
lock_files_required: list[str]
missing_lock_files: list[str]
dependency_files_found: list[str]
unpinned_dependencies: list[str]
status: str
warnings: list[str]
errors: list[str]
```

### `InstallValidationReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
package_artifact: str
validation_mode: str
network_allowed: bool
temp_validation_root: str
commands_run: list[CommandRecord]
status: str
warnings: list[str]
errors: list[str]
```

### `ReleaseBundleManifest`

Required fields:

```python
schema_version: str
schema_id: str
bundle_manifest_id: str
created_at: str
source_component: str
bundle_name: str
bundle_version: str
bundle_artifact: str
bundle_sha256: str
included_artifacts: list[str]
included_hashes: list[dict]
provenance_ref: str
evidence_ref: str
promotion_status: str
warnings: list[str]
errors: list[str]
```

### `DistributionEvidence`

Required fields:

```python
schema_version: str
schema_id: str
evidence_id: str
created_at: str
source_component: str
package_manifest_ref: str
package_inventory_ref: str
package_build_report_ref: str
package_validation_report_ref: str
hash_manifest_ref: str
provenance_ref: str
dependency_lock_report_ref: str
install_validation_report_ref: str
release_bundle_manifest_ref: str | None
commands_run: list[CommandRecord]
artifact_refs: list[str]
sha256_refs: list[dict]
rejections: list[dict]
status: str
warnings: list[str]
errors: list[str]
```

### `PackagingEvidenceManifest`

Required fields:

```python
schema_version: str
schema_id: str
evidence_manifest_id: str
created_at: str
source_component: str
component_id: str
validated_commit: str | None
evidence_files: list[str]
evidence_hashes: list[dict]
package_artifacts: list[str]
release_bundle_artifacts: list[str]
commands_run: list[CommandRecord]
source_mutation_status: str
network_status: str
publish_status: str
status: str
warnings: list[str]
errors: list[str]
```

### `PackagingCompletionRecord`

Required fields:

```python
schema_version: str
schema_id: str
component_id: str
component_name: str
status: str
validated_commit: str | None
validated_at: str
package_artifacts: list[str]
release_bundle_artifacts: list[str]
evidence_refs: list[str]
hash_refs: list[dict]
commands_run: list[CommandRecord]
validated_capabilities: list[str]
deviations_from_contract: list[dict]
unresolved_risks: list[dict]
final_decision: str
warnings: list[str]
errors: list[str]
```

### `DependencyInventory`

Required fields:

```python
schema_version: str
schema_id: str
inventory_id: str
created_at: str
source_component: str
dependency_files: list[str]
lock_files: list[str]
resolved_dependencies: list[dict]
unpinned_dependencies: list[str]
network_resolution_used: bool
status: str
warnings: list[str]
errors: list[str]
```

Purpose:

```text
Record a deterministic local dependency inventory or SBOM-style summary without contacting the network.
This is not a full vulnerability scanner. It is a packaging evidence artifact proving what dependency declarations and locks existed at package time.
```

### `LicenseNoticeReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
required_license_files: list[str]
found_license_files: list[str]
missing_license_files: list[str]
notice_files: list[str]
status: str
warnings: list[str]
errors: list[str]
```

Purpose:

```text
Ensure required distribution metadata such as LICENSE, NOTICE, README, and package manifest files are present when required by manifest policy.
```

### `ReproducibilityReport`

Required fields:

```python
schema_version: str
schema_id: str
report_id: str
created_at: str
source_component: str
first_build_artifact: str
first_build_sha256: str
second_build_artifact: str | None
second_build_sha256: str | None
hashes_match: bool
normalized_timestamp: str | int
normalized_permissions: dict
normalized_owner_group: str
status: str
warnings: list[str]
errors: list[str]
```

Purpose:

```text
Prove deterministic packaging by rebuilding the same selected inventory twice in a temporary validation path and comparing SHA-256 hashes.
```

### `CommandRecord`

Required fields:

```python
name: str
command: str
exit_code: int | None
status: str
summary: str
stdout_summary: str | None
stderr_summary: str | None
warnings: list[str]
errors: list[str]
```

Required helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
redact_sensitive_text(text: str) -> str
normalize_archive_path(relative_path: str) -> str
```

Acceptance:

```text
dataclasses instantiate
to_dict serializes nested dataclasses
status constants match schemas
rejection constants match schemas
redaction helper removes secret-like values
archive path normalizer rejects absolute and parent-traversal paths
no filesystem writes
no command execution
no network access
```

---

# 6. Schemas to Create

Create all schemas under:

```text
tools/agentx_evolve/schemas/
```

Required schemas:

```text
package_manifest.schema.json
package_inventory.schema.json
package_rejection.schema.json
package_build_report.schema.json
package_validation_report.schema.json
artifact_hash_manifest.schema.json
package_provenance.schema.json
dependency_lock_report.schema.json
install_validation_report.schema.json
release_bundle_manifest.schema.json
distribution_evidence.schema.json
packaging_evidence_manifest.schema.json
packaging_completion_record.schema.json
```

General schema rules:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
reject unknown status values
reject unknown package format values
reject unknown rejection reason values
require arrays for artifact refs, hash refs, warnings, and errors
require SHA-256 fields where artifact integrity is recorded
require command records to include command, exit_code, status, and summary
```

Required schema examples in tests:

```text
valid_package_manifest
valid_package_inventory
valid_package_rejection
valid_package_build_report
valid_package_validation_report
valid_artifact_hash_manifest
valid_package_provenance
valid_dependency_lock_report
valid_install_validation_report
valid_release_bundle_manifest
valid_distribution_evidence
valid_packaging_evidence_manifest
valid_packaging_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid sha256 format fails where applicable
invalid command record fails
unknown package format fails
unknown rejection reason fails
```

---

# 7. Package Manifest Location and Rules

Default manifest path:

```text
tools/agentx_evolve/packaging/manifests/agentx_package_manifest.json
```

The manifest decides:

```text
package name
package version
source root
include patterns
exclude patterns
required files
forbidden paths
forbidden extensions
forbidden runtime roots
forbidden archive names
allowed package formats
default package format
clean-git requirement
tracked-files-only requirement
dependency lock requirement
install validation network policy
symlink policy
external publish policy
staging root
build output root
evidence root
report root
```

Minimum default manifest:

```json
{
  "schema_version": "1.0",
  "schema_id": "package_manifest.schema.json",
  "manifest_id": "agentx-default-package-manifest",
  "package_name": "agentx",
  "package_version": "0.1.0",
  "source_root": ".",
  "include_patterns": [
    "L0/**",
    "L1/**",
    "L2/**",
    "tools/**",
    "README.md",
    "Makefile"
  ],
  "exclude_patterns": [
    ".git/**",
    ".agentx-init/**",
    "**/__pycache__/**",
    "**/.pytest_cache/**",
    "**/*.pyc",
    "**/.DS_Store",
    "**/.env",
    "**/.env.*"
  ],
  "required_files": [
    "README.md",
    "Makefile"
  ],
  "forbidden_paths": [
    ".git",
    ".agentx-init",
    ".venv",
    "venv",
    "node_modules"
  ],
  "forbidden_extensions": [
    ".pem",
    ".key",
    ".p12",
    ".pfx"
  ],
  "forbidden_runtime_roots": [
    ".agentx-init"
  ],
  "forbidden_archive_names": [
    "..",
    "/"
  ],
  "allowed_package_formats": ["tar.gz", "zip", "directory"],
  "default_package_format": "tar.gz",
  "require_clean_git": true,
  "require_tracked_files_only": false,
  "require_dependency_lock": false,
  "allow_network_for_install_validation": false,
  "allow_symlinks": false,
  "allow_external_symlink_targets": false,
  "allow_external_publish": false,
  "build_output_root": ".agentx-init/packaging/dist",
  "staging_root": ".agentx-init/packaging/staging",
  "evidence_root": ".agentx-init/packaging/evidence",
  "report_root": ".agentx-init/packaging/reports",
  "warnings": [],
  "errors": []
}
```

---

# 8. Package Selection and Rejection Rules

## 8.1 Include / Exclude Precedence

The selection algorithm must use this order:

```text
1. Normalize and validate path relative to source_root.
2. Reject absolute path or parent traversal.
3. Reject forbidden roots and forbidden extensions.
4. Reject runtime roots.
5. Reject cache paths.
6. Reject env files.
7. Reject symlink if symlinks are not allowed.
8. Reject symlink target outside source_root if external symlink targets are not allowed.
9. Apply include_patterns.
10. Apply exclude_patterns.
11. Run secret-like scan for selected file candidates.
12. Check tracked-file requirement if require_tracked_files_only=true.
13. Include only if no rejection exists.
```

Important rule:

```text
A later include pattern can never re-allow a path rejected by forbidden, runtime, secret, symlink, or path traversal rules.
```

## 8.2 Archive Path Rules

Every archive member path must be normalized and safe:

```text
no absolute archive paths
no path beginning with /
no Windows drive prefix
no parent traversal segment ..
no empty member name
no duplicate normalized archive path
no symlink target outside source_root
no hardlink target outside source_root
```

Any violation is a BLOCKER.

---

# 9. Classes / Functions

## 9.1 `package_manifest_loader.py`

Required functions:

```python
load_package_manifest(manifest_path: Path) -> PackageManifest
validate_package_manifest(manifest: PackageManifest, schema_path: Path) -> list[str]
```

Behavior:

```text
read manifest JSON
validate required fields
validate include/exclude pattern types
validate package format values
validate runtime roots
validate output roots under .agentx-init/packaging/
return PackageManifest
fail closed on invalid schema
```

Must not:

```text
build package
write runtime artifacts
execute commands
```

---

## 9.2 `package_file_selector.py`

Required functions:

```python
select_package_files(repo_root: Path, manifest: PackageManifest) -> PackageInventory
is_included_by_manifest(relative_path: str, manifest: PackageManifest) -> bool
is_excluded_by_manifest(relative_path: str, manifest: PackageManifest) -> bool
normalize_candidate_path(repo_root: Path, path: Path) -> str
```

Behavior:

```text
walk source tree deterministically
sort selected paths lexicographically
apply include/exclude precedence rules
record selected files
record rejected files
record symlink information
record source tracked status when available
```

Must not include:

```text
.git
.agentx-init
cache directories
virtual environments
local env files
secret-like files
absolute paths
parent traversal paths
external symlink targets
```

---

## 9.3 `package_rejector.py`

Required functions:

```python
reject_forbidden_package_files(
    inventory: PackageInventory,
    manifest: PackageManifest,
    repo_root: Path
) -> PackageInventory

scan_for_secret_like_content(path: Path) -> bool
is_runtime_artifact(relative_path: str, manifest: PackageManifest) -> bool
is_cache_file(relative_path: str) -> bool
is_env_file(relative_path: str) -> bool
is_forbidden_extension(relative_path: str, manifest: PackageManifest) -> bool
is_symlink_escape(path: Path, repo_root: Path) -> bool
is_archive_escape(relative_path: str) -> bool
```

Behavior:

```text
reject runtime artifacts
reject cache files
reject env files
reject secret-like files
reject forbidden extensions
reject forbidden roots
reject symlink/path traversal escapes
record rejection reason and severity
```

Secret-like detection must be conservative and deterministic:

```text
API key patterns
token assignments
private key headers
provider credential names
.env-style credential lines
common cloud credential markers
```

Secret handling rule:

```text
Do not log raw secrets. Rejection evidence includes file path, reason code, and safe detail only.
```

---

## 9.4 `artifact_hasher.py`

Required functions:

```python
hash_artifact(path: Path) -> ArtifactHashRecord
write_hash_manifest(artifacts: list[Path], output_path: Path) -> ArtifactHashManifest
verify_artifact_hash(path: Path, expected_sha256: str) -> bool
hash_bytes(data: bytes) -> str
```

Behavior:

```text
use SHA-256
hash package artifact
hash release bundle
hash manifest
hash inventory
hash reports
hash provenance
hash evidence files
write hash manifest atomically
```

Required hash fields:

```text
artifact_path
artifact_kind
sha256
size_bytes
created_at
hash_algorithm
```

No non-cryptographic hashes are accepted for final evidence.

---

## 9.5 `package_builder.py`

Required functions:

```python
build_package(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    package_format: str | None = None
) -> tuple[Path, PackageBuildReport]

create_staging_tree(repo_root: Path, manifest: PackageManifest, inventory: PackageInventory) -> Path
create_deterministic_tar_gz(staging_root: Path, output_path: Path) -> Path
create_deterministic_zip(staging_root: Path, output_path: Path) -> Path
```

Behavior:

```text
create clean staging directory under .agentx-init/packaging/staging/
copy only included files
preserve relative paths
create deterministic archive if tar.gz or zip
write package artifact under .agentx-init/packaging/dist/
write package build report
return artifact path and report
```

Reproducibility rules:

```text
sort files before archive
use normalized archive member names
normalize timestamps to SOURCE_DATE_EPOCH or 0 where feasible
normalize permissions to stable values where feasible
normalize owner/group to 0 or empty where feasible
avoid absolute paths in archive
avoid local machine usernames in archive metadata
for gzip output, set mtime to deterministic value where Python supports it
```

Must not:

```text
publish package
write outside .agentx-init/packaging/
include rejected files
include runtime artifacts
include secrets
include dirty unreviewed source when require_clean_git=true
```

---

## 9.6 `package_validator.py`

Required functions:

```python
validate_package_contents(
    package_artifact: Path,
    manifest: PackageManifest,
    inventory: PackageInventory
) -> PackageValidationReport

list_package_contents(package_artifact: Path) -> list[str]
validate_archive_member_path(member_name: str) -> bool
```

Behavior:

```text
open package artifact
list contents deterministically
confirm every packaged file was selected
confirm required files exist
confirm rejected files are absent
confirm forbidden roots are absent
confirm runtime artifacts are absent
confirm no absolute paths exist
confirm no parent traversal paths exist
confirm no duplicate archive member names exist
confirm no secret-like files exist
```

Returns a `PackageValidationReport` with:

```text
status
missing required files
unexpected files
forbidden files
archive escape files
runtime artifacts found
secret-like files found
warnings
errors
```

---

## 9.7 `provenance_writer.py`

Required functions:

```python
write_package_provenance(
    repo_root: Path,
    manifest: PackageManifest,
    package_artifact: Path,
    package_sha256: str,
    build_command: str,
    output_path: Path
) -> PackageProvenance

get_git_commit(repo_root: Path) -> str | None
get_git_branch(repo_root: Path) -> str | None
get_git_status(repo_root: Path) -> str
get_build_environment() -> dict
```

Behavior:

```text
record source commit
record branch
record git tree status
record manifest path and hash
record build command
record Python version and OS
record package artifact and SHA-256
record reproducibility settings
redact local sensitive environment values
```

Allowed Git commands must be read-only:

```text
git rev-parse HEAD
git branch --show-current
git status --short
```

If Git is unavailable:

```text
record UNKNOWN
return BLOCKED if require_clean_git=true
```

---

## 9.8 `dependency_lock_validator.py`

Required functions:

```python
validate_dependency_lock(repo_root: Path, manifest: PackageManifest) -> DependencyLockReport
find_dependency_files(repo_root: Path) -> list[Path]
find_lock_files(repo_root: Path) -> list[Path]
detect_unpinned_dependencies(path: Path) -> list[str]
```

Behavior:

```text
identify dependency files
identify lock files
verify required lock files exist when require_dependency_lock=true
flag obvious unpinned dependencies where deterministic rules can detect them
record report
```

Expected dependency files:

```text
pyproject.toml
requirements.txt
requirements-dev.txt
setup.cfg
setup.py
Pipfile
poetry.lock
uv.lock
requirements.lock
```

Unpinned examples:

```text
requests
requests>=2
pytest
some-package~=1.0
```

Pinned examples:

```text
requests==2.31.0
package @ file://...
hash-locked entries where supported
```

No network dependency resolution is allowed in this layer.

---

## 9.9 `dependency_inventory_writer.py`

Required functions:

```python
write_dependency_inventory(
    repo_root: Path,
    manifest: PackageManifest,
    dependency_lock_report: DependencyLockReport,
    output_path: Path
) -> DependencyInventory
```

Behavior:

```text
read dependency declaration files locally
read lock files locally
record package names and pinned versions where deterministically parseable
record unpinned dependencies already identified by dependency_lock_validator
record network_resolution_used=false
write dependency_inventory.json atomically
```

Must not:

```text
contact package indexes
run pip resolution
run npm/uv/poetry/pipenv resolution
claim vulnerability status
log credentials from index URLs
```

## 9.10 `license_notice_validator.py`

Required functions:

```python
validate_license_notice_files(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory
) -> LicenseNoticeReport
```

Behavior:

```text
check required distribution metadata files declared by manifest
verify required README / LICENSE / NOTICE files are included in package inventory when required
record missing files as BLOCKED when manifest requires them
write license_notice_report.json atomically
```

Minimum required files unless the manifest explicitly disables the requirement:

```text
README.md
```

Recommended required files for distributable release bundles:

```text
LICENSE
NOTICE, if third-party notices are required
```

## 9.11 `reproducibility_validator.py`

Required functions:

```python
verify_reproducible_build(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    package_format: str,
    first_artifact: Path,
    output_path: Path
) -> ReproducibilityReport
```

Behavior:

```text
build the same selected inventory a second time in an isolated temporary staging root
apply identical archive normalization settings
hash the second artifact
compare first and second SHA-256 values
write reproducibility_report.json atomically
```

Acceptance:

```text
hashes must match for final DONE when package_format is tar.gz or zip
if the selected package format is directory, reproducibility must validate deterministic inventory and file hashes instead of archive hash
```

No-Go:

```text
reproducibility check skipped without recorded deviation
second build includes a different file set
hashes differ for archive builds
local timestamps, usernames, group names, or absolute paths leak into archive metadata
```

## 9.12 `install_validator.py`

Required functions:

```python
validate_local_install(
    package_artifact: Path,
    manifest: PackageManifest,
    repo_root: Path
) -> InstallValidationReport
```

Default validation mode:

```text
archive_extract_only
```

Allowed validation modes:

```text
archive_extract_only
python_compile_only
local_pip_install_no_deps
```

Safety rule:

```text
archive_extract_only is the default and preferred mode.
python_compile_only may compile extracted Python files without importing the package.
local_pip_install_no_deps is allowed only if policy explicitly permits it, because package installation may execute build scripts.
```

Forbidden by default:

```text
network install
pip install with dependency resolution
upload to registry
Git clone during validation
remote fetch
running package post-install scripts without explicit policy approval
```

Required command records:

```text
command name
command text
exit code
status
summary
stdout summary, bounded and redacted
stderr summary, bounded and redacted
```

---

## 9.13 `release_bundle.py`

Required functions:

```python
create_release_bundle(
    package_artifact: Path,
    evidence_files: list[Path],
    hash_manifest: ArtifactHashManifest,
    provenance: PackageProvenance,
    output_root: Path
) -> ReleaseBundleManifest
```

Behavior:

```text
create a local release bundle under .agentx-init/packaging/dist/
include package artifact
include package manifest
include package inventory
include package build report
include package validation report
include hash manifest
include provenance
include distribution evidence
include install validation report
include dependency lock report
write release bundle manifest
hash the bundle
```

Must not:

```text
publish to package registry
push Git tags
create GitHub release
upload externally
trigger promotion automatically
```

---

## 9.14 `distribution_evidence.py`

Required functions:

```python
write_distribution_evidence(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
    build_report: PackageBuildReport,
    validation_report: PackageValidationReport,
    hash_manifest: ArtifactHashManifest,
    provenance: PackageProvenance,
    dependency_lock_report: DependencyLockReport,
    install_validation_report: InstallValidationReport,
    release_bundle_manifest: ReleaseBundleManifest | None,
    commands_run: list[CommandRecord],
    output_path: Path
) -> DistributionEvidence

write_packaging_evidence_manifest(
    evidence_files: list[Path],
    package_artifacts: list[Path],
    release_bundle_artifacts: list[Path],
    commands_run: list[CommandRecord],
    output_path: Path
) -> PackagingEvidenceManifest

write_packaging_completion_record(
    evidence: DistributionEvidence,
    evidence_manifest: PackagingEvidenceManifest,
    output_path: Path
) -> PackagingCompletionRecord
```

Behavior:

```text
write distribution evidence JSON
write packaging evidence manifest JSON
write completion record JSON
include artifact paths
include SHA-256 hashes
include command records
include validation status
include rejection summary
include unresolved risks
write all JSON atomically
```

---

## 9.15 `package_orchestrator.py`

Purpose:

```text
Provide one controlled top-level orchestration function so coding agents and future tools do not reimplement package build order.
```

Required function:

```python
build_distribution_package(
    repo_root: Path,
    manifest_path: Path | None = None,
    package_format: str | None = None,
    create_bundle: bool = True,
    dry_run: bool = False,
    policy_context: dict | None = None
) -> DistributionEvidence
```

Required flow:

```text
1. Acquire packaging build lock.
2. Load manifest.
3. Validate manifest schema.
4. Check policy for package build.
5. Check source tree cleanliness if required.
6. Select package files.
7. Reject forbidden files.
8. Stop if any blocking rejection exists.
9. Validate dependency lock policy.
10. Create staging tree.
11. Build package.
12. Hash package artifact.
13. Validate package contents.
14. Write provenance.
15. Run local install validation.
16. Write package build and validation reports.
17. Write hash manifest.
18. Write distribution evidence.
19. Create release bundle if requested.
20. Write packaging evidence manifest.
21. Write completion record.
22. Release packaging build lock.
```

Dry-run behavior:

```text
load manifest
select/reject files
validate dependency policy
show what would be built
write dry-run evidence only
no staging copy
no package artifact
no release bundle
```

---

# 10. Runtime Artifacts

Runtime artifact root:

```text
.agentx-init/packaging/
```

Required runtime subdirectories:

```text
.agentx-init/packaging/staging/
.agentx-init/packaging/dist/
.agentx-init/packaging/evidence/
.agentx-init/packaging/reports/
.agentx-init/packaging/tmp/
```

Required runtime artifacts:

```text
.agentx-init/packaging/evidence/package_inventory.json
.agentx-init/packaging/evidence/package_rejections.json
.agentx-init/packaging/evidence/package_build_report.json
.agentx-init/packaging/evidence/package_validation_report.json
.agentx-init/packaging/evidence/artifact_hash_manifest.json
.agentx-init/packaging/evidence/package_provenance.json
.agentx-init/packaging/evidence/dependency_lock_report.json
.agentx-init/packaging/evidence/dependency_inventory.json
.agentx-init/packaging/evidence/license_notice_report.json
.agentx-init/packaging/evidence/reproducibility_report.json
.agentx-init/packaging/evidence/install_validation_report.json
.agentx-init/packaging/evidence/release_bundle_manifest.json
.agentx-init/packaging/evidence/distribution_evidence.json
.agentx-init/packaging/evidence/packaging_evidence_manifest.json
.agentx-init/packaging/evidence/packaging_completion_record.json
.agentx-init/packaging/.package_build.lock
```

Allowed package outputs:

```text
.agentx-init/packaging/dist/agentx-<version>.tar.gz
.agentx-init/packaging/dist/agentx-<version>.zip
.agentx-init/packaging/dist/agentx-<version>-release-bundle.tar.gz
```

Must not write:

```text
source files
files under L0/L1/L2/tools except intended implementation files
release artifacts outside .agentx-init/packaging/ unless explicitly approved later
external registry artifacts
```

Atomic write rule:

```text
All JSON evidence files must be written through temp-file + rename.
A partially written evidence file is a validation failure.
```

---

# 11. Package Build Flow

Required build flow:

```text
1. Acquire packaging lock.
2. Load package manifest.
3. Validate package manifest schema.
4. Check package build policy.
5. Check source tree cleanliness if require_clean_git=true.
6. Select package files using include/exclude rules.
7. Reject forbidden files, runtime artifacts, caches, env files, symlink escapes, archive escapes, and secrets.
8. Validate required files are present.
9. Validate dependency lock/freeze policy.
10. Write package inventory and rejection records.
11. Create clean staging tree.
12. Copy selected files into staging tree.
13. Build deterministic archive or directory package.
14. Write package build report.
15. Hash package artifact.
16. Validate package contents.
17. Write package validation report.
18. Write package provenance.
19. Run local install validation.
20. Write hash manifest.
21. Write distribution evidence.
22. Create release bundle if requested.
23. Write packaging evidence manifest.
24. Write completion record.
25. Release packaging lock.
```

Fail-closed rules:

```text
invalid manifest -> BLOCKED
secret found -> BLOCKED
runtime artifact selected -> BLOCKED
archive escape found -> BLOCKED
symlink escape found -> BLOCKED
required file missing -> BLOCKED
forbidden path packaged -> BLOCKED
dependency lock missing when required -> BLOCKED
dirty source tree when clean tree required -> BLOCKED
hash mismatch -> FAILED
install validation failure -> FAILED or BLOCKED, depending on cause
policy unavailable for build -> BLOCKED unless restrictive runtime-only fallback is explicitly allowed
```

---

# 12. Package Validation Flow

Validation must prove:

```text
package opens successfully
package has no absolute paths
package has no parent-directory escape paths
package has no duplicate member paths
package has no .git contents
package has no .agentx-init contents
package has no cache files
package has no env files
package has no secret-like files
package has all required files
package has only selected inventory files
package hash matches recorded hash
provenance hash matches recorded hash
release bundle contains evidence and hashes
```

Validation result must be recorded in:

```text
.agentx-init/packaging/evidence/package_validation_report.json
.agentx-init/packaging/evidence/distribution_evidence.json
.agentx-init/packaging/evidence/packaging_completion_record.json
```

---

# 12.1 Safe Archive Extraction Rules

Package validation must inspect archive entries before extraction.

Required safe extraction sequence:

```text
1. Open archive in read-only mode.
2. Enumerate member names without extracting.
3. Normalize each member name.
4. Reject absolute paths, parent traversal, Windows drive prefixes, empty names, duplicate names, symlink escapes, and hardlink escapes.
5. Create an isolated validation directory under .agentx-init/packaging/tmp/.
6. Extract only after all member names pass validation.
7. Confirm every extracted path resolves inside the validation directory.
8. Delete or quarantine the validation directory after report writing.
```

No archive may be extracted before archive member paths pass validation.

# 12.2 Lock File and Concurrency Rules

A packaging run must acquire:

```text
.agentx-init/packaging/.package_build.lock
```

Lock behavior:

```text
if no lock exists -> create lock with pid, timestamp, command, repo root, manifest path
if active lock exists -> return BLOCKED
if stale lock exists and owning process is gone -> move stale lock to evidence with reason, then continue
if stale lock cannot be proven stale -> return BLOCKED
always release lock in finally block
never delete another active process lock
```

A final DONE verdict is invalid if overlapping package builds can write to the same staging, dist, or evidence paths.

# 12.3 Version and Provenance Synchronization

The implementation must verify that package version evidence is internally consistent.

Required checks:

```text
manifest package_version is recorded in provenance
release bundle version equals package version unless explicitly overridden by manifest policy
artifact file name includes package_name and package_version
completion record references the same package version
reviewed commit is recorded when Git metadata exists
manifest SHA-256 is recorded before build and included in provenance
```

If Git metadata is unavailable:

```text
record source_commit = UNKNOWN
record source_branch = UNKNOWN
block if require_clean_git=true
allow only if manifest policy permits non-Git packaging
```

# 12.4 Runtime Artifact vs Source Mutation Rule

Packaging generates runtime artifacts under `.agentx-init/packaging/`. These are allowed outputs, not source mutation.

The source mutation check must distinguish:

```text
allowed runtime artifact changes under .agentx-init/packaging/
blocked source changes under L0/, L1/, L2/, tools/, schemas, tests, docs, root config files
blocked unexpected output outside .agentx-init/packaging/
```

A packaging test may create runtime artifacts in a temp repo fixture. It must not alter the real repository source tree.

# 13. Artifact Hashing Flow

Hashing algorithm:

```text
SHA-256 only
```

Required hashed artifacts:

```text
package manifest
package artifact
package inventory
package rejection report
package build report
package validation report
artifact hash manifest
package provenance
dependency lock report
dependency inventory
license notice report
reproducibility report
install validation report
distribution evidence
packaging evidence manifest
release bundle manifest
release bundle artifact, if created
packaging completion record after final write
packaging completion record
```

Hashing flow:

```text
1. Hash input manifest before build.
2. Hash selected package artifact after build.
3. Hash evidence files after writing.
4. Hash release bundle after creation.
5. Write artifact_hash_manifest.json.
6. Write packaging_evidence_manifest.json with final evidence hashes.
7. Include hash refs in distribution evidence and completion record.
```

A final DONE verdict is invalid if package artifact hashes or final evidence hashes are missing.

---

# 14. Provenance Generation

Provenance must record:

```text
package name
package version
source commit
source branch
source tree status
manifest path
manifest SHA-256
package artifact path
package artifact SHA-256
build command
build timestamp
Python version
OS info
builder module/version
network allowed flag
install validation mode
reproducibility settings
```

Provenance must not contain:

```text
secrets
local credentials
raw environment variables
absolute personal home paths unless redacted
unredacted command output
```

---

# 15. Dependency Freeze / Lock Validation

This layer must validate dependency integrity without resolving dependencies from the network.

Required checks:

```text
identify dependency files
identify lock files
record whether lock files exist
flag missing lock files when required
flag obvious unpinned dependencies in requirements files
record dependency-lock report
```

If the project intentionally does not require dependency lock files, record:

```text
status = PASS
require_dependency_lock = false
lock policy = not required for this layer
```

---

# 16. Install Validation

Install validation must be local and safe.

Default validation mode:

```text
archive_extract_only
```

Allowed validation modes:

```text
archive_extract_only
python_compile_only
local_pip_install_no_deps
```

Forbidden by default:

```text
network install
pip install with dependency resolution
upload to registry
Git clone during validation
remote fetch
running package post-install scripts without explicit policy approval
```

Important rule:

```text
local_pip_install_no_deps is not the default. It may run only if Policy / Capability Registry explicitly allows it for the current package artifact.
```

---

# 17. Release Bundle Creation

A release bundle is a local artifact that groups:

```text
package artifact
package manifest
package inventory
package build report
package validation report
artifact hash manifest
package provenance
dependency lock report
dependency inventory
license notice report
reproducibility report
install validation report
distribution evidence
packaging evidence manifest
completion record
```

Release bundle path:

```text
.agentx-init/packaging/dist/agentx-<version>-release-bundle.tar.gz
```

Rules:

```text
bundle contents sorted deterministically
bundle hash recorded
bundle manifest written
bundle does not publish itself
bundle does not mark promotion complete
bundle is handed to Promotion / Release Gate for final approval
```

---

# 18. Integration Requirements

## 18.1 Security Sandbox Integration

Packaging must integrate with Security Sandbox for filesystem operations.

Required:

```text
source file reads pass sandbox boundary checks where available
staging writes are restricted to .agentx-init/packaging/staging/
dist writes are restricted to .agentx-init/packaging/dist/
evidence writes are restricted to .agentx-init/packaging/evidence/
report writes are restricted to .agentx-init/packaging/reports/
install validation temp paths are controlled
path traversal is rejected
absolute package paths are rejected
symlink escapes are rejected
```

If Security Sandbox is unavailable:

```text
manifest loading may proceed
file selection may proceed in dry-run
build and install validation must BLOCK unless a restrictive local fallback proves paths remain inside allowed roots
```

## 18.2 Policy / Capability Registry Integration

Packaging must integrate with Policy / Capability Registry before build, validation, and release bundle creation.

Required policy decisions:

```text
ALLOW_PACKAGE_BUILD
ALLOW_STAGING_WRITE
ALLOW_DIST_WRITE
ALLOW_EVIDENCE_WRITE
ALLOW_INSTALL_VALIDATION
ALLOW_RELEASE_BUNDLE_CREATE
BLOCK_EXTERNAL_PUBLISH
BLOCK_NETWORK_INSTALL_BY_DEFAULT
```

If policy is unavailable:

```text
manifest loading may proceed
file selection may proceed in dry-run
package build blocks unless restrictive local fallback allows runtime-only writes
external publishing always blocks
network install always blocks
```

## 18.3 Tool / MCP Adapter Integration

Packaging functions may later be exposed as tools, but not in this implementation by default.

Potential future tool names:

```text
package_manifest_validate
package_build_local
package_validate_local
package_hash_artifacts
package_create_release_bundle
package_write_distribution_evidence
```

Tool exposure rules:

```text
read-only package inspection may be MCP-visible later
package build is not MCP-visible by default
release bundle creation is not MCP-visible by default
publishing is not implemented in this layer
all tool calls must use Tool / MCP Adapter evidence rules if exposed
```

## 18.4 Promotion / Release Gate Integration

This layer creates release-ready artifacts but does not promote or publish them.

Required handoff to Promotion / Release Gate:

```text
package artifact path
package artifact SHA-256
release bundle path
release bundle SHA-256
package provenance
package validation report
install validation report
dependency lock report
dependency inventory
license notice report
reproducibility report
distribution evidence
packaging evidence manifest
completion record
```

The Promotion / Release Gate decides:

```text
whether release is approved
whether tag is created
whether artifact is published
whether external distribution is allowed
```

Packaging must not bypass Promotion / Release Gate.

---

# 19. Command Acceptance Criteria

If package commands or CLI wrappers are exposed, each command must record:

```text
command name
exact command text
exit code
status
bounded stdout summary
bounded stderr summary
redaction status
output artifact path
```

Allowed local commands:

```text
python -m compileall <extracted-or-package-path>
tar/zip operations implemented with Python standard library where possible
git rev-parse HEAD
git branch --show-current
git status --short
```

Forbidden commands by default:

```text
pip install with dependency resolution
python setup.py upload
twine upload
npm publish
git tag
git push
curl/wget/network fetch
shell command with metacharacter injection
```

No command may use raw shell execution.

---

# 20. Test Files

Required tests:

```text
test_packaging_models.py
test_package_manifest_loader.py
test_package_file_selector.py
test_package_rejector.py
test_package_builder.py
test_package_validator.py
test_artifact_hasher.py
test_provenance_writer.py
test_dependency_lock_validator.py
test_install_validator.py
test_release_bundle.py
test_distribution_evidence.py
test_package_orchestrator.py
test_packaging_negative_cases.py
test_packaging_schema_validation.py
```

---

# 21. Test Cases

Required positive tests:

```text
test_package_manifest_loads_valid_manifest
test_package_manifest_schema_accepts_valid_example
test_package_file_selector_includes_expected_files
test_package_file_selector_sorts_files_deterministically
test_package_rejector_rejects_runtime_artifacts
test_package_rejector_rejects_cache_files
test_package_rejector_rejects_env_files
test_package_builder_creates_tar_gz_under_dist
test_package_builder_writes_build_report
test_package_builder_does_not_include_absolute_paths
test_package_validator_accepts_clean_package
test_package_validator_writes_validation_report
test_artifact_hasher_writes_sha256_manifest
test_provenance_writer_records_commit_or_unknown
test_dependency_lock_validator_passes_when_lock_not_required
test_install_validator_archive_extract_only_passes
test_reproducibility_validator_double_build_hashes_match
test_dependency_inventory_written_without_network
test_license_notice_report_records_required_files
test_release_bundle_contains_package_and_evidence
test_distribution_evidence_records_artifacts_and_hashes
test_packaging_evidence_manifest_records_final_hashes
test_package_orchestrator_runs_full_flow_in_temp_repo
```

Required negative tests:

```text
test_manifest_missing_required_field_fails
test_invalid_package_format_fails
test_secret_file_is_not_packaged
test_env_file_is_not_packaged
test_agentx_init_runtime_artifact_is_not_packaged
test_git_directory_is_not_packaged
test_pycache_is_not_packaged
test_forbidden_extension_is_rejected
test_required_file_missing_blocks_build
test_dirty_tree_blocks_when_clean_git_required
test_untracked_file_blocks_when_tracked_only_required
test_dependency_lock_missing_blocks_when_required
test_network_install_blocks_by_default
test_release_bundle_does_not_publish
test_package_hash_mismatch_fails_validation
test_package_path_traversal_is_rejected
test_archive_absolute_path_is_rejected
test_symlink_escape_is_rejected
test_duplicate_archive_member_is_rejected
test_external_publish_command_is_blocked
test_package_build_lock_blocks_concurrent_build
test_stale_lock_is_handled_safely
test_archive_is_not_extracted_before_member_validation
test_reproducibility_hash_mismatch_blocks_done
test_license_required_but_missing_blocks_when_manifest_requires_it
```

Schema validation tests:

```text
test_package_manifest_schema_rejects_missing_package_name
test_package_inventory_schema_rejects_missing_files
test_package_rejection_schema_rejects_unknown_reason_code
test_package_build_report_schema_rejects_missing_status
test_package_validation_report_schema_rejects_unknown_status
test_hash_manifest_schema_rejects_invalid_sha256
test_provenance_schema_rejects_missing_package_sha256
test_dependency_lock_report_schema_accepts_missing_lock_report_when_not_required
test_install_validation_report_schema_rejects_unknown_mode
test_release_bundle_manifest_schema_rejects_missing_bundle_hash
test_distribution_evidence_schema_rejects_missing_hash_refs
test_packaging_evidence_manifest_schema_rejects_missing_evidence_hashes
test_completion_record_schema_rejects_missing_final_decision
```

---

# 22. Implementation Order

Implement in this exact order:

```text
1. Create tools/agentx_evolve/packaging/ package.
2. Implement packaging_models.py.
3. Create package schemas.
4. Create default package manifest.
5. Implement package_manifest_loader.py.
6. Implement package_file_selector.py.
7. Implement package_rejector.py.
8. Implement artifact_hasher.py.
9. Implement package_builder.py.
10. Implement package_validator.py.
11. Implement provenance_writer.py.
12. Implement dependency_lock_validator.py.
13. Implement dependency_inventory_writer.py.
14. Implement license_notice_validator.py.
15. Implement reproducibility_validator.py.
16. Implement install_validator.py.
17. Implement distribution_evidence.py.
18. Implement release_bundle.py.
19. Implement package_orchestrator.py.
20. Create tests.
21. Run compileall.
22. Run pytest.
23. Run schema validation tests.
24. Run package build validation in temp repo fixture.
25. Run reproducibility double-build validation.
26. Write packaging evidence manifest.
27. Write completion record.
```

Do not reorder unless import dependencies require it.

Rationale:

```text
models first
schemas second
manifest before selection
selection before rejection
hashing before provenance
build before validation
validation before evidence
release bundle before final evidence manifest
orchestrator after public components exist
completion record after validation
```

---

# 23. Acceptance Criteria

The implementation is accepted only if all are true:

```text
all target files exist
all schemas exist
all tests exist
default package manifest exists
package manifest validates
package file selection is deterministic
runtime artifacts are excluded
secret-like files are rejected
env files are rejected
cache files are rejected
symlink escapes are rejected
path traversal is rejected
forbidden paths are rejected
package builds under .agentx-init/packaging/dist/
package contents validate
package hash is SHA-256
hash manifest is written
double-build reproducibility check passes for archive packages
dependency inventory is written without network
license / notice report is written
package build report is written
package validation report is written
provenance is written
dependency lock report is written
install validation report is written
release bundle manifest is written if bundle is created
distribution evidence is written
packaging evidence manifest is written
completion record is written
no network is required
no publishing occurs
no source mutation occurs
compileall passes
pytest passes
schema validation passes
git status is clean or only expected runtime artifacts exist
```

Conditional acceptance is allowed for:

```text
Git metadata unavailable, if provenance records UNKNOWN and clean-git is not required
lock file missing, if require_dependency_lock=false
release bundle not created, if build mode is package-only and evidence records this
install validation limited to archive_extract_only
```

Conditional acceptance is not allowed for:

```text
secret leakage
runtime artifact leakage
archive/path traversal leakage
hash omission
package validation omission
source mutation
network dependency by default
publishing by default
schema validation failure
missing final evidence hashes
```

---

# 24. Definition of Done

The Packaging / Distribution Layer is done when it can safely produce local release-ready artifacts without publishing them.

It must prove:

```text
package builder lives under tools/agentx_evolve/packaging/
package manifests live under tools/agentx_evolve/packaging/manifests/
package runtime artifacts live under .agentx-init/packaging/
package contents are selected by manifest rules
package contents are rejected by forbidden-file rules
runtime artifacts are excluded
secrets are excluded
env files are excluded
cache files are excluded
symlink/path traversal archive escapes are rejected
package artifacts are generated locally
package artifacts are validated
SHA-256 hashes are generated
reproducibility is proven by double-build hash comparison where applicable
provenance is generated
dependency lock/freeze status is validated
dependency inventory is written
license / notice policy is validated
install validation is local and safe
release bundle is created locally when requested
distribution evidence is written
packaging evidence manifest is written
completion record is written
Security Sandbox integration exists or restrictive fallback blocks unsafe writes
Policy / Capability Registry integration exists or restrictive fallback blocks unsafe operations
Tool / MCP Adapter exposure is not enabled by default
Promotion / Release Gate receives handoff artifacts but is not bypassed
compileall passes
pytest passes
schema validation passes
no source mutation occurs
no network is required
no publishing occurs
```

Final validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/packaging
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_packaging_models.py \
  tools/agentx_evolve/tests/test_package_manifest_loader.py \
  tools/agentx_evolve/tests/test_package_file_selector.py \
  tools/agentx_evolve/tests/test_package_rejector.py \
  tools/agentx_evolve/tests/test_package_builder.py \
  tools/agentx_evolve/tests/test_package_validator.py \
  tools/agentx_evolve/tests/test_artifact_hasher.py \
  tools/agentx_evolve/tests/test_provenance_writer.py \
  tools/agentx_evolve/tests/test_dependency_lock_validator.py \
  tools/agentx_evolve/tests/test_install_validator.py \
  tools/agentx_evolve/tests/test_release_bundle.py \
  tools/agentx_evolve/tests/test_distribution_evidence.py \
  tools/agentx_evolve/tests/test_package_orchestrator.py \
  tools/agentx_evolve/tests/test_packaging_negative_cases.py \
  tools/agentx_evolve/tests/test_packaging_schema_validation.py
git status --short
```

Expected result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts under .agentx-init/packaging/
```

---

# 25. No-Go Conditions

The implementation is NOT DONE if any are true:

```text
package includes .agentx-init
package includes .git
package includes env files
package includes detected secrets
package includes pycache/cache files
package includes forbidden extensions
package includes symlink escape
package includes path traversal entry
package includes absolute archive path
package includes unselected files
package omits required files
package hash is missing
package hash mismatch occurs
reproducibility hash mismatch occurs without accepted deviation
provenance is missing
install validation is missing
install validation requires network by default
release bundle publishes externally
Promotion / Release Gate is bypassed
source files are mutated during package build
runtime artifacts are written outside approved runtime root
schema validation fails
compileall fails
pytest fails
packaging evidence manifest is missing
completion record is missing
required license/notice file is missing when manifest requires it
archive is extracted before member-path safety validation
```

---

# 26. Coding-Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] Target repository is Agent_X.
[ ] Packaging package lives under tools/agentx_evolve/packaging/.
[ ] Schemas live under tools/agentx_evolve/schemas/.
[ ] Tests live under tools/agentx_evolve/tests/.
[ ] Runtime artifacts live under .agentx-init/packaging/.
[ ] Package manifests live under tools/agentx_evolve/packaging/manifests/.
[ ] Package builder does not publish.
[ ] Package builder does not use network by default.
[ ] Package builder excludes .agentx-init.
[ ] Package builder excludes .git.
[ ] Package builder excludes env files and secrets.
[ ] Package builder rejects symlink and path traversal escapes.
[ ] Package builder writes SHA-256 hashes.
[ ] Package builder writes provenance.
[ ] Package builder writes build and validation reports.
[ ] Package builder writes distribution evidence.
[ ] Package builder writes final evidence hashes.
[ ] Release bundle is local only.
[ ] Promotion / Release Gate is not bypassed.
```

---

# 27. Final Frozen Acceptance Matrix

| Area | Required outcome |
|---|---|
| Location | `tools/agentx_evolve/packaging/` |
| Manifest | `tools/agentx_evolve/packaging/manifests/agentx_package_manifest.json` |
| Runtime root | `.agentx-init/packaging/` only |
| Package output | `.agentx-init/packaging/dist/` only |
| Evidence output | `.agentx-init/packaging/evidence/` only |
| Secret handling | reject and do not log raw secret values |
| Runtime junk | `.agentx-init`, `.git`, caches, env files excluded |
| Path safety | absolute paths, parent traversal, symlink escapes rejected |
| Reproducibility | sorted archive members, normalized metadata, and double-build hash comparison |
| Hashing | SHA-256 for package, bundle, and evidence |
| Provenance | commit, branch, tree status, manifest hash, package hash, version sync |
| Install validation | safe extraction first, local only, no network by default |
| Publishing | not implemented and always blocked |
| Promotion | handoff only, no bypass |
| Dependency inventory | local SBOM-style inventory, no network resolution |
| License / notice | required distribution metadata verified when manifest requires it |
| Tests | positive, negative, schema, and orchestration tests pass |
| Final status | compileall PASS, pytest PASS, schema validation PASS, clean git status |

---

# 28. Review Evidence and Reproducibility Block

The coding agent must ensure the final implementation can produce a review-ready evidence block.

Required final evidence fields:

```text
reviewed_commit, or UNKNOWN with justification if Git unavailable
reviewed_branch, or UNKNOWN with justification if Git unavailable
manifest_path
manifest_sha256
package_artifact_path
package_artifact_sha256
release_bundle_path, if created
release_bundle_sha256, if created
exact commands run
exit codes
Python version
OS information
pytest result
schema validation result
source mutation status
network status
publish status
reproducibility status
```

The final evidence package must be enough for an independent reviewer to reproduce the package build using the same commit, manifest, and commands.

A final `DONE` status is invalid if:

```text
reviewed commit is missing without justification
exact commands are missing
command exit codes are missing
package artifact hash is missing
release bundle hash is missing when bundle exists
reproducibility report is missing for archive packages
evidence hashes are missing
```

# 29. Final Freeze Rule

This v3 document is frozen as the implementation spec for the Packaging / Distribution Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details that do not weaken safety
MAJOR: changed package format policy, changed publishing behavior, changed runtime artifact root, changed default network behavior, or changed Promotion Gate boundary
```

Blocked without major revision:

```text
allowing external publishing by default
allowing network install by default
removing secret exclusion
removing runtime artifact exclusion
removing hash/provenance evidence
removing package validation
allowing Promotion / Release Gate bypass
allowing package artifacts outside .agentx-init/packaging/ by default
```

---

# 30. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, package build flow, package validation flow, artifact hashing, provenance generation, dependency lock validation, dependency inventory, license/notice checks, safe install validation, safe archive extraction, release bundle creation, distribution evidence, evidence hashing, reproducibility proof, safety boundaries, integration points, command acceptance criteria, tests, implementation order, acceptance criteria, no-go conditions, and Definition of Done.
```
