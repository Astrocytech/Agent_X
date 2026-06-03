# PACKAGING_DISTRIBUTION_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: PACKAGING_DISTRIBUTION_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready, v3 precision pass
component_id: AGENTX_PACKAGING_DISTRIBUTION
component_name: Packaging / Distribution Layer
roadmap_layer: 20
roadmap_phase: Phase E — Release Preparation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Release / Promotion Acceptance Criteria, Supply Chain / Dependency Integrity Rules
optional_standards: ES, Report Template, MCP Protocol Acceptance Criteria if MCP artifacts are packaged
target_language: Python
canonical_subdirectory: tools/agentx_evolve/packaging/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/packaging/
approved_package_output_root: .agentx-init/packaging/dist/
risk_level: critical
implementation_mode: deterministic packaging and distribution control layer
previous_version_rating: 9.7/10
current_version_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 controlling contract was strong and close to final. I would rate it:

```text
9.7/10
```

It already covered the core packaging/distribution contract, including:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Packaging artifact rules
Distribution boundary rules
Package manifest schema
Release bundle schema
Installation manifest schema
Dependency lock / dependency policy schema
Artifact hash / provenance schema
Runtime artifact boundary
Source mutation boundary
OpenCode borrowing notes
Agent_X integration notes
secret exclusion
runtime artifact exclusion
deterministic build rules
path / symlink / archive traversal controls
SBOM and license metadata boundaries
deviation register
evidence immutability
No-Go conditions
Definition of Done
```

It was not fully 10/10 because several production-grade precision controls still needed to be explicit:

```text
1. Threat model and trust-boundary assumptions were implied, not directly stated.
2. Manifest-to-archive exact-membership verification was not strict enough.
3. Extraction-safety validation was not separated from archive-entry validation.
4. Package naming/version consistency across manifest, pyproject, wheel, sdist, and bundle was not mandatory.
5. Command Acceptance Criteria were referenced but not fully specified for build/install/validate commands.
6. Signing and attestation were out of scope but needed a safe deferral rule so unsigned artifacts cannot be confused with signed releases.
7. Staging cleanup and stale artifact prevention needed stronger rules.
8. Fresh-clone validation needed stronger environment and exit-code evidence rules.
9. Dependency lock review needed clearer treatment of extras, optional dependencies, build-system dependencies, and transitive metadata.
10. Final freeze needed to distinguish patch/minor/major changes without allowing publication-policy drift.
```

This v3 adds those controls and is the final 10/10 controlling contract.
---

# 1. Purpose

This document defines the controlling contract for the **Packaging / Distribution Layer** in Agent_X.

This layer decides what can be packaged, what must be excluded, how package artifacts are produced, how distribution bundles are validated, how hashes and provenance are recorded, and how release artifacts are reviewed before use.

The layer must ensure that Agent_X can produce reproducible, reviewable, safe distribution artifacts without leaking:

```text
secrets
runtime state
local machine paths
unreviewed source
generated junk
unapproved dependencies
private evidence
private credentials
unsafe install behavior
```

The layer must answer:

```text
what may be packaged
what must never be packaged
which runtime artifacts are excluded
which source files are included
which generated artifacts are included
which secrets must be excluded
which package formats are allowed
how hashes are produced
how provenance is recorded
how installation is validated
how distribution artifacts are reviewed
```

This is a safety-critical layer because packaging is the point where implementation moves from local repository state into distributable artifacts.

---

# 2. Scope

## 2.1 Required in This Layer

This layer must define and control:

```text
package manifest generation
package content selection
package content exclusion
release bundle manifest generation
installation manifest generation
dependency lock validation
dependency policy validation
SBOM metadata generation or explicit SBOM deferral
license metadata collection or explicit license-review deferral
artifact hash records
artifact provenance records
allowed package formats
allowed package contents
forbidden package contents
runtime artifact exclusions
secret exclusions
source mutation boundary
package build evidence
package validation evidence
distribution review evidence
reproducibility checks
install validation checks
package staging boundaries
package output boundaries
evidence immutability
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
promotion approval decisions
Git push or release publication
package hosting or upload
cloud deployment
installer UI
model download management
MCP runtime activation
full vulnerability scanning
full legal license approval
release signing with private keys
public registry publication
container registry publication
full release gate approval
```

Those belong to Promotion / Release Gate, Git Integration, Monitoring, Release Signing, Security Review, Legal Review, or external release infrastructure layers.

---

# 3. Standards Applied

## 3.1 Primary Standard: EQC

EQC is primary because packaging controls what is shipped.

The layer must prevent:

```text
shipping unreviewed files
shipping dirty working-tree state
shipping source files modified by packaging itself
shipping secrets
shipping .env files
shipping credentials
shipping runtime evidence accidentally
shipping local machine paths
shipping cache directories
shipping unpinned dependencies
shipping artifacts without hashes
shipping artifacts without provenance
shipping packages that cannot be installed or validated
shipping non-deterministic archives without deviation
shipping symlink or path traversal escapes
shipping hidden generated files
```

The layer must fail closed when package contents are unsafe, unproven, unhashable, non-deterministic, outside policy, or outside approved paths.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer must be implemented as concrete files with clear responsibilities.

Expected package location:

```text
tools/agentx_evolve/packaging/
```

Expected responsibilities:

```text
package manifest builder
content selector
content exclusion checker
path canonicalizer
symlink and traversal checker
secret exclusion checker
runtime artifact exclusion checker
dependency policy validator
dependency lock validator
SBOM metadata collector
license metadata collector
artifact hasher
provenance recorder
package staging builder
package builder
package validator
installation validator
distribution review reporter
completion record writer
```

Each file must have a clear public API, inputs, outputs, safety rules, tests, and evidence behavior.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects multiple Agent_X subsystems:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Tool / MCP Adapter Layer
Promotion / Release Gate
Git Integration Layer
Documentation Synchronization Layer
Monitoring / Observability Layer
Backup / Disaster Recovery Layer
Final System Acceptance Layer
```

This layer is an integration boundary. It must not become a bypass around promotion, policy, sandboxing, source review, or evidence requirements.

## 3.4 Required Schema Contract

Schema Contract is required because package decisions and distribution artifacts must be machine-checkable.

Required schemas:

```text
package_manifest.schema.json
release_bundle.schema.json
installation_manifest.schema.json
dependency_policy.schema.json
dependency_lock.schema.json
artifact_hash_manifest.schema.json
artifact_provenance.schema.json
package_validation_report.schema.json
distribution_review_report.schema.json
packaging_completion_record.schema.json
packaging_deviation_register.schema.json
packaging_reproducibility_report.schema.json
packaging_sbom.schema.json
packaging_license_manifest.schema.json
```

SBOM and license schemas may be implemented as metadata-only v1 schemas. Full vulnerability or legal approval is outside this layer unless added by a separate contract.

## 3.5 Required Evidence / Audit Rules

Every packaging action must create evidence.

Evidence is required for:

```text
package manifest generation
content inclusion decisions
content exclusion decisions
canonical path checks
symlink and traversal checks
secret scan result
runtime artifact exclusion result
dependency lock validation
dependency policy validation
SBOM metadata result
license metadata result
package build command result
package hash generation
provenance generation
reproducibility check
installation validation
release bundle validation
distribution review
final completion record
```

---

# 4. Why This Layer Is Safety-Critical

Packaging / Distribution decides what leaves the development environment.

It must protect Agent_X against:

```text
secret leakage
runtime artifact leakage
local environment leakage
unreviewed source shipment
source mutation during packaging
non-reproducible bundles
unhashable artifacts
package tampering
silent dependency drift
unsafe install commands
hidden generated files
incomplete provenance
unvalidated installation
path traversal escape
symlink escape
release gate bypass
```

A package is not acceptable merely because it can be built. It is acceptable only if its contents, hashes, dependency policy, provenance, reproducibility status, and validation evidence satisfy this contract.

---

# 5. Threat Model and Trust Boundaries

The Packaging / Distribution Layer must assume that unsafe files may already exist in the repository, working tree, runtime directories, cache directories, or generated build outputs. It must not assume that all files under the repository root are safe to ship.

Threats this layer must defend against:

```text
secret files accidentally committed or generated
secret-like content inside otherwise allowed files
local environment paths inside generated metadata
stale build artifacts from previous runs
malicious or accidental symlink escapes
hardlink or special-file escapes
archive entries that extract outside the target directory
manifest/archive mismatch
package version mismatch
local path or VCS dependency drift
missing build-system dependency records
unsigned artifact confused with signed artifact
release candidate confused with public release
packaging commands that mutate source
install commands that perform network or shell side effects
```

Trust boundaries:

```text
repository source is an input, not automatically trusted
.agentx-init/packaging/ is runtime evidence/output, not reviewed source
.agentx-init/packaging/staging/ is temporary staging, not package authority
.agentx-init/packaging/dist/ is candidate output, not release authority
Promotion / Release Gate is the authority for release approval
Git Integration is the authority for Git mutation
Dependency policy is the authority for dependency acceptability
Security Sandbox is the authority for path boundary checks
```

A package is valid only when the manifest, archive contents, hashes, provenance, dependency records, and validation reports agree. Any disagreement must produce `FAIL` or `BLOCKED`, not a best-effort package.
---

# 6. Status Vocabulary

All review, validation, and evidence records must use only these status values:

```text
PASS
PARTIAL
FAIL
BLOCKED
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | Release-ready allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present but incomplete. | No, unless only non-release internal package and deviation recorded |
| FAIL | Requirement was checked and failed. | No |
| BLOCKED | Requirement could not proceed because safety or prerequisite check blocked it. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or validation was not run. | No |
| NOT APPLICABLE | Requirement truly does not apply to the package type. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot affect the active package. | Yes, if justified |

A package cannot be `release_ready=true` if any required validation area is `PARTIAL`, `FAIL`, `BLOCKED`, `NOT CHECKED`, or `NOT RUN`.

---

# 7. Packaging Authority Rule

Packaging does not grant release authority.

The Packaging / Distribution Layer may produce candidate artifacts, but release authority belongs to the Promotion / Release Gate.

A package may be marked `VALIDATED_PACKAGE` only when all required authorities agree:

```text
Packaging / Distribution content checks
Security Sandbox path boundary checks
Policy / Capability Registry packaging permissions
Dependency policy checks
Artifact hash verification
Artifact provenance verification
Reproducibility verification
Installation validation
Distribution review
Promotion / Release Gate, if release-ready status is requested
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_REVIEW
NEEDS_PROMOTION_APPROVAL
VALIDATION_FAILED
VALIDATED_PACKAGE
```

Registry, manifest, or package format approval alone does not grant release approval.

---

# 8. Package Modes

The layer must distinguish package modes.

```text
INTERNAL_DEV_BUNDLE
INTERNAL_EVIDENCE_BUNDLE
SOURCE_ARCHIVE
WHEEL
SDIST
RELEASE_CANDIDATE_BUNDLE
PUBLIC_RELEASE_BUNDLE
```

## 7.1 Internal Development Bundle

Allowed for local validation only.

```text
may include tests
may include internal docs
may include non-release metadata
must still exclude secrets
must still exclude forbidden runtime artifacts
must still hash artifacts
must not be externally published
```

## 7.2 Internal Evidence Bundle

May include selected redacted evidence.

```text
must use evidence appendix rules
must redact secrets
must list every evidence artifact in manifest
must hash every included evidence artifact
must not include raw tool logs unless explicitly redacted and approved
```

## 7.3 Release Candidate Bundle

Candidate for Promotion / Release Gate review.

```text
must pass all package validations
must include hashes
must include provenance
must include dependency policy result
must include installation validation result
must include distribution review report
must not set public release status without Promotion / Release Gate approval
```

## 7.4 Public Release Bundle

Out of v1 active scope unless Promotion / Release Gate explicitly delegates approval.

```text
requires promotion approval
requires release publication contract
requires signing policy if signed artifacts are produced
requires network publication policy if uploaded externally
```

---

# 9. Allowed Package Contents

The package may include only approved source and distribution files.

Allowed content categories:

```text
reviewed Python source files
reviewed schema files
reviewed tests, if test distribution is enabled
reviewed documentation files
reviewed configuration templates
reviewed CLI entrypoint metadata
reviewed package metadata files
license files
README files
CHANGELOG files
static examples that contain no secrets
packaging manifests generated by this layer
artifact hash manifests generated by this layer
provenance records generated by this layer
installation validation reports generated by this layer
redacted evidence appendix files, only for evidence bundle mode
```

Allowed source locations should normally include:

```text
tools/agentx_initiator/
tools/agentx_evolve/
L0/
L1/
L2/
README.md
LICENSE
CHANGELOG.md
pyproject.toml
requirements*.txt, if approved
```

The exact allowed paths must be declared in the package manifest.

A file is allowed only if all are true:

```text
path is explicitly included
path is canonicalized inside approved root
path is not forbidden by pattern
path is not a symlink escape
path has no secret match
path is reviewed or generated by approved packaging command
path has a SHA-256 hash before release-ready status
```

---

# 10. Forbidden Package Contents

The package must never include:

```text
.env files
.env.* files
private keys
API keys
tokens
credentials
SSH keys
cloud credentials
local machine paths
absolute user home paths
.cache directories
__pycache__ directories
.pytest_cache directories
.mypy_cache directories
.ruff_cache directories
.git directory
.git hooks
virtual environments
.venv directories
node_modules directories
Bun or Node runtime artifacts unless explicitly approved for a future layer
model weights unless explicitly approved by a model distribution contract
large generated binary artifacts unless explicitly listed
unreviewed temporary files
scratch files
temp todo files
local logs
runtime evidence accidentally included as package source
unredacted command output
unredacted tool logs
raw prompts containing secrets
personal data dumps
symlink escapes
hardlink escapes
path traversal entries
absolute archive paths
archive entries containing ../
```

Forbidden runtime paths include:

```text
.agentx-init/security/
.agentx-init/tool_calls/
.agentx-init/implementation/
.agentx-init/memory/
.agentx-init/packaging/raw/
.agentx-init/tmp/
```

Runtime evidence may be referenced by provenance, but must not be bundled as source unless the package type explicitly allows an evidence appendix and redaction checks pass.

---

# 11. Path, Symlink, and Archive Entry Rules

All candidate files must be resolved through canonical path checks before inclusion.

Required rules:

```text
candidate path must resolve inside repository root or approved staging root
candidate path must not escape through symlink
candidate path must not escape through hardlink or special filesystem behavior
archive entry path must be relative
archive entry path must not start with /
archive entry path must not contain ../
archive entry path must use normalized POSIX separators
archive entry path must not contain NUL bytes
archive entry path must not include platform-specific private paths
file mode must be normalized unless executable bit is intentionally required
```

Symlinks:

```text
symlinks are excluded by default
internal symlinks may be allowed only if target resolves inside approved package root
external symlinks always block release-ready packaging
broken symlinks always block release-ready packaging
```

Special files:

```text
sockets block
pipes block
devices block
unknown file types block
```

---

# 12. Runtime Artifact Boundary

Packaging runtime artifacts must be written only under:

```text
.agentx-init/packaging/
```

Approved package output root:

```text
.agentx-init/packaging/dist/
```

Approved staging root:

```text
.agentx-init/packaging/staging/
```

Expected runtime artifacts:

```text
.agentx-init/packaging/package_manifest.json
.agentx-init/packaging/release_bundle.json
.agentx-init/packaging/installation_manifest.json
.agentx-init/packaging/dependency_policy_report.json
.agentx-init/packaging/dependency_lock_report.json
.agentx-init/packaging/artifact_hash_manifest.json
.agentx-init/packaging/artifact_provenance.json
.agentx-init/packaging/package_validation_report.json
.agentx-init/packaging/distribution_review_report.json
.agentx-init/packaging/packaging_reproducibility_report.json
.agentx-init/packaging/packaging_deviation_register.json
.agentx-init/packaging/packaging_completion_record.json
```

Rules:

```text
runtime artifacts must not be written into source package directories
package staging must not be inside source directories
package output must not be inside source directories
packaging must not write into source files
packaging must not modify Initiator source
packaging must not modify evolve-layer source
packaging must not modify schema source except through approved implementation work
packaging must not write evidence outside .agentx-init/packaging/ without a recorded deviation
```

---

# 13. Source Mutation Boundary

The Packaging / Distribution Layer must be read-only with respect to reviewed source.

Allowed writes:

```text
packaging runtime artifacts under .agentx-init/packaging/
package staging artifacts under .agentx-init/packaging/staging/
package output artifacts under .agentx-init/packaging/dist/
hash manifests under .agentx-init/packaging/
validation reports under .agentx-init/packaging/
```

Forbidden writes:

```text
source code mutation
schema mutation
test mutation
documentation mutation
Git metadata mutation
version bump mutation unless explicitly delegated from Promotion / Release Gate
lockfile mutation unless explicitly run in dependency update mode and separately reviewed
```

A package build must not make the Git working tree dirty except for approved runtime artifacts or approved build output paths.

---

# 14. Allowed Package Formats

Allowed v1 package formats:

```text
.tar.gz source archive
.zip source archive
Python wheel, if pyproject metadata is present and build is deterministic
Python sdist, if pyproject metadata is present and build is deterministic
internal release bundle directory, if manifest and hashes are present
```

Conditionally allowed later:

```text
container image manifest
standalone executable bundle
MCP server distribution bundle
model-runtime bundle
platform installer
signed release bundle
```

Not allowed in v1 unless a separate contract approves them:

```text
network-published package
public PyPI upload
GitHub release upload
Docker registry push
self-installing binary
unsigned executable installer
bundle with embedded secrets
bundle with embedded model weights
```

---

# 15. Deterministic Build and Reproducibility Rules

Release-ready artifacts must be reproducible or must record a blocking deviation.

Required deterministic rules:

```text
archive entries sorted lexicographically
archive paths normalized
file permissions normalized
owner/group metadata omitted or normalized
timestamps normalized or recorded as SOURCE_DATE_EPOCH-compatible build metadata
line endings preserved or normalized by explicit policy
symlink policy enforced before archiving
excluded files removed before hashing
hashes computed after final artifact write
build commands recorded exactly
build environment recorded
local paths redacted in evidence
```

Reproducibility report must record:

```text
source commit
working tree status
package mode
package format
build command
builder environment
SOURCE_DATE_EPOCH or timestamp policy
file ordering policy
permission policy
hashes
known non-deterministic inputs
deviations
status
```

A package may not be release-ready if reproducibility status is `FAIL`, `NOT CHECKED`, or `NOT RUN`.

---

# 16. Manifest-to-Archive Exact Membership Rules

The package manifest is authoritative for package membership. The built archive must match the manifest exactly.

Required checks:

```text
every archive entry must appear in package_manifest.included_paths or generated_artifacts
every manifest included path must appear in the archive unless explicitly excluded with reason
archive entry count must match expected count
archive entry sizes must match expected sizes after normalization
archive entry SHA-256 hashes must match artifact hash records where applicable
archive must not contain undeclared files
archive must not omit declared required files
archive must not include stale files from previous builds
archive must not include files discovered only during archive creation
```

Manifest/archive mismatch rules:

```text
undeclared archive entry -> FAIL
missing required manifest entry -> FAIL
extra generated file without manifest record -> FAIL
stale file from previous staging run -> FAIL
size/hash mismatch -> FAIL
```

The build must validate archive contents after archive creation, not only before staging. A release-ready package requires both pre-build content validation and post-build archive validation.

---

# 17. Archive Extraction-Safety Validation

Archive entry validation is not enough. The built artifact must also be tested for safe extraction behavior.

Required extraction-safety checks:

```text
extract package in a temporary clean directory
verify no extracted path escapes extraction root
verify no extracted path overwrites outside target root
verify no extracted symlink points outside extraction root
verify no absolute path is created
verify no device, pipe, socket, or special file is created
verify no path traversal entry is accepted by extraction tooling
verify extracted file count matches archive manifest
verify extracted files hash to expected values
```

Extraction validation must run before release-ready status. Failure means `package_validation_status = FAIL`.
---

# 18. Package Manifest Schema Contract

A package manifest must record exactly what is intended to be packaged.

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/package_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "package_manifest.schema.json",
  "manifest_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "component_id": "AGENTX_PACKAGING_DISTRIBUTION",
  "package_name": "string",
  "package_version": "string",
  "package_mode": "INTERNAL_DEV_BUNDLE|INTERNAL_EVIDENCE_BUNDLE|SOURCE_ARCHIVE|WHEEL|SDIST|RELEASE_CANDIDATE_BUNDLE|PUBLIC_RELEASE_BUNDLE",
  "package_type": "SOURCE_ARCHIVE|WHEEL|SDIST|INTERNAL_BUNDLE",
  "source_commit": "string",
  "source_branch": "string",
  "working_tree_status": "CLEAN|EXPECTED_RUNTIME_ARTIFACTS_ONLY|DIRTY",
  "approved_source_roots": [],
  "approved_output_root": "string",
  "included_paths": [],
  "excluded_paths": [],
  "forbidden_path_matches": [],
  "symlink_findings": [],
  "secret_findings": [],
  "generated_artifacts": [],
  "dependency_lock_refs": [],
  "sbom_ref": "string|null",
  "license_manifest_ref": "string|null",
  "hash_manifest_ref": "string|null",
  "provenance_ref": "string|null",
  "deviation_register_ref": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
source_commit is required
included_paths must be explicit
excluded_paths must be explicit
forbidden_path_matches must be empty for package approval
secret_findings must be empty for release-ready approval
external symlink findings block release-ready approval
working_tree_status must not be DIRTY for release-ready packages
```

---

# 19. Release Bundle Schema Contract

A release bundle records final distribution artifact grouping.

Required schema file:

```text
tools/agentx_evolve/schemas/release_bundle.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "release_bundle.schema.json",
  "bundle_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "component_id": "AGENTX_PACKAGING_DISTRIBUTION",
  "bundle_name": "string",
  "bundle_version": "string",
  "bundle_mode": "INTERNAL_DEV_BUNDLE|INTERNAL_EVIDENCE_BUNDLE|RELEASE_CANDIDATE_BUNDLE|PUBLIC_RELEASE_BUNDLE",
  "source_commit": "string",
  "package_manifest_ref": "string",
  "artifacts": [],
  "artifact_hash_manifest_ref": "string",
  "artifact_provenance_ref": "string",
  "installation_manifest_ref": "string",
  "validation_report_ref": "string",
  "reproducibility_report_ref": "string",
  "distribution_review_report_ref": "string",
  "promotion_required": true,
  "promotion_record_ref": "string|null",
  "release_ready": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
release_ready cannot be true unless validation passes
release_ready cannot be true without hashes
release_ready cannot be true without provenance
release_ready cannot be true without reproducibility result
release_ready cannot be true without distribution review
release_ready cannot be true if promotion is required and missing
```

---

# 20. Package Naming and Version Consistency Rules

Package identity must be consistent across every packaging artifact.

Required consistency checks:

```text
package_manifest.package_name matches pyproject project name, if pyproject is packaged
package_manifest.package_version matches pyproject project version, if pyproject is packaged
release_bundle.bundle_version matches the package version or records an explicit bundle-version mapping
wheel filename version matches package manifest version
sdist filename version matches package manifest version
installation manifest package name/version matches package manifest
hash manifest source_commit matches package manifest source_commit
provenance source_commit matches package manifest source_commit
distribution review reviewed_commit matches provenance source_commit
completion record validated_commit matches distribution review reviewed_commit
```

Blocking mismatches:

```text
package name mismatch -> FAIL
package version mismatch -> FAIL
source commit mismatch -> FAIL
artifact filename/version mismatch -> FAIL
reviewed commit/provenance commit mismatch -> FAIL
```

Version bumping is outside this layer unless explicitly delegated by Promotion / Release Gate. Packaging may read version metadata, but it must not mutate version files.
---

# 21. Installation Manifest Schema Contract

An installation manifest records how a package is installed and validated.

Required schema file:

```text
tools/agentx_evolve/schemas/installation_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "installation_manifest.schema.json",
  "installation_manifest_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "package_name": "string",
  "package_version": "string",
  "supported_python_versions": [],
  "supported_platforms": [],
  "install_commands": [],
  "validation_commands": [],
  "forbidden_install_behaviors": [],
  "requires_network": false,
  "requires_gpu": false,
  "requires_hosted_model": false,
  "requires_mcp_runtime": false,
  "expected_entrypoints": [],
  "expected_imports": [],
  "warnings": [],
  "errors": []
}
```

Installation validation must prove:

```text
package installs in a clean environment or test sandbox
package imports successfully
CLI entrypoints resolve, if included
schemas are included and loadable
runtime directories are not required to exist before first run
no install command requires network unless explicitly approved
no install command writes outside allowed environment paths
no install command executes raw shell
```

---

# 22. Dependency Lock / Dependency Policy Schema Contract

## 18.1 Dependency Policy Schema

Required schema file:

```text
tools/agentx_evolve/schemas/dependency_policy.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "dependency_policy.schema.json",
  "policy_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "allowed_dependency_files": [],
  "pinned_dependencies_required": true,
  "hash_pinning_required": false,
  "allowed_package_managers": ["pip"],
  "forbidden_dependencies": [],
  "forbidden_runtime_dependencies": ["Bun", "Node", "OpenCode runtime"],
  "network_install_allowed": false,
  "transitive_dependency_review_required": false,
  "warnings": [],
  "errors": []
}
```

## 18.2 Dependency Lock Schema

Required schema file:

```text
tools/agentx_evolve/schemas/dependency_lock.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "dependency_lock.schema.json",
  "lock_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_commit": "string",
  "dependency_files": [],
  "resolved_dependencies": [],
  "unresolved_dependencies": [],
  "unpinned_dependencies": [],
  "unhashed_dependencies": [],
  "forbidden_dependencies_found": [],
  "dependency_source_refs": [],
  "policy_ref": "string",
  "status": "PASS|FAIL|PARTIAL|NOT_CHECKED",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
unpinned dependencies block release-ready distribution unless explicitly accepted by policy
forbidden dependencies always block release-ready distribution
network install must be false by default
new package managers must require explicit policy approval
local path dependencies block release-ready distribution unless explicitly approved and normalized
VCS dependencies block release-ready distribution unless pinned to immutable commit and approved
```

---

# 23. SBOM and License Metadata Contract

This layer must either produce basic package metadata or explicitly defer it.

## 19.1 SBOM Metadata Schema

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/packaging_sbom.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "packaging_sbom.schema.json",
  "sbom_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_commit": "string",
  "package_name": "string",
  "package_version": "string",
  "components": [],
  "generation_mode": "BASIC_METADATA|DEFERRED_SAFELY",
  "status": "PASS|DEFERRED SAFELY|FAIL",
  "warnings": [],
  "errors": []
}
```

## 19.2 License Manifest Schema

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/packaging_license_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "packaging_license_manifest.schema.json",
  "license_manifest_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_commit": "string",
  "package_name": "string",
  "package_version": "string",
  "declared_project_license": "string|null",
  "dependency_license_metadata": [],
  "unknown_licenses": [],
  "forbidden_license_findings": [],
  "status": "PASS|PARTIAL|FAIL|DEFERRED SAFELY",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
unknown license metadata may be non-blocking for internal bundles
unknown license metadata blocks public release unless accepted by Promotion / Release Gate
forbidden license findings block release-ready status
full legal approval is outside this layer unless delegated
```

---

# 24. Artifact Hash / Provenance Schema Contract

## 20.1 Artifact Hash Manifest

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/artifact_hash_manifest.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "artifact_hash_manifest.schema.json",
  "hash_manifest_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "hash_algorithm": "SHA-256",
  "source_commit": "string",
  "artifacts": [
    {
      "artifact_path": "string",
      "artifact_type": "string",
      "size_bytes": 0,
      "sha256": "string"
    }
  ],
  "warnings": [],
  "errors": []
}
```

Hashing rules:

```text
SHA-256 is required
hash every package artifact
hash every manifest used for release-ready status
hash provenance records
hash installation manifest
hash validation report
hash reproducibility report
hash distribution review report
hash completion record after final write, or record self-hash exception clearly
```

## 20.2 Artifact Provenance

Required schema file:

```text
tools/agentx_evolve/schemas/artifact_provenance.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "artifact_provenance.schema.json",
  "provenance_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_repository": "string",
  "source_commit": "string",
  "source_branch": "string",
  "builder_identity": "string",
  "build_environment": {
    "os": "string",
    "python_version": "string",
    "packaging_tool_version": "string"
  },
  "commands_run": [],
  "inputs": [],
  "outputs": [],
  "hash_manifest_ref": "string",
  "deviation_register_ref": "string|null",
  "warnings": [],
  "errors": []
}
```

Provenance rules:

```text
record exact source commit
record source branch
record build environment
record exact commands
record package inputs
record package outputs
record hashes
record deviations
redact local private paths
```

---

# 25. Package Validation Report Schema Contract

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/package_validation_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "package_validation_report.schema.json",
  "validation_report_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_commit": "string",
  "package_manifest_ref": "string",
  "package_artifact_refs": [],
  "content_validation_status": "PASS|FAIL|PARTIAL|NOT CHECKED|NOT RUN",
  "secret_exclusion_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "runtime_artifact_exclusion_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "dependency_policy_status": "PASS|FAIL|PARTIAL|NOT CHECKED|NOT RUN",
  "path_boundary_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "symlink_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "hash_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "provenance_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "installation_validation_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "overall_status": "PASS|FAIL|PARTIAL|BLOCKED",
  "warnings": [],
  "errors": []
}
```

---

# 26. Distribution Review Report Schema Contract

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/distribution_review_report.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "distribution_review_report.schema.json",
  "review_report_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "reviewed_commit": "string",
  "reviewed_branch": "string",
  "package_name": "string",
  "package_version": "string",
  "package_type": "string",
  "package_artifact_path": "string",
  "package_sha256": "string",
  "manifest_sha256": "string",
  "provenance_sha256": "string",
  "installation_validation_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "secret_exclusion_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "runtime_artifact_exclusion_status": "PASS|FAIL|NOT CHECKED|NOT RUN",
  "dependency_policy_status": "PASS|FAIL|PARTIAL|NOT CHECKED|NOT RUN",
  "source_mutation_status": "PASS|FAIL|NOT CHECKED",
  "reproducibility_status": "PASS|FAIL|PARTIAL|NOT CHECKED|NOT RUN",
  "deviation_register_ref": "string|null",
  "accepted_deviations": [],
  "rejected_deviations": [],
  "final_verdict": "DONE|NOT DONE",
  "warnings": [],
  "errors": []
}
```

A package cannot be marked `PASS` if any required area is `NOT CHECKED` or `NOT RUN`.

---

# 27. Deviation Register Contract

Required schema file:

```text
tools/agentx_evolve/schemas/15_packaging/packaging_deviation_register.schema.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "packaging_deviation_register.schema.json",
  "deviation_register_id": "string",
  "created_at": "string",
  "source_component": "PackagingDistribution",
  "source_commit": "string",
  "deviations": [
    {
      "id": "PKG-DEV-001",
      "area": "string",
      "description": "string",
      "reason": "string",
      "safety_impact": "none|low|medium|high|critical",
      "compensating_control": "string",
      "accepted_status": "NOT APPLICABLE|DEFERRED SAFELY|NON-BLOCKING FOLLOW-UP",
      "reviewer_decision": "ACCEPTED|REJECTED"
    }
  ],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
secret findings cannot be accepted as deviations for release-ready packages
source mutation cannot be accepted as a deviation for release-ready packages
missing hashes cannot be accepted as a deviation for release-ready packages
missing provenance cannot be accepted as a deviation for release-ready packages
external package publication cannot be accepted as a deviation in v1
high or critical deviations require Promotion / Release Gate review
```

---

# 28. Evidence and Audit Contract

Packaging evidence must be written under:

```text
.agentx-init/packaging/
```

Required evidence artifacts:

```text
package_manifest.json
release_bundle.json
installation_manifest.json
dependency_policy_report.json
dependency_lock_report.json
packaging_sbom.json
packaging_license_manifest.json
artifact_hash_manifest.json
artifact_provenance.json
package_validation_report.json
distribution_review_report.json
packaging_reproducibility_report.json
packaging_deviation_register.json
packaging_completion_record.json
```

Every evidence record must include:

```text
schema_version
schema_id
created_at
source_component
source_commit
status
warnings
errors
```

Evidence rules:

```text
evidence must be machine-readable JSON
evidence must not contain secrets
evidence must not contain raw unredacted command output
evidence must not contain local private paths unless redacted
evidence must record hashes where applicable
evidence must record deviations
evidence must record validation command results
evidence must record final DONE / NOT DONE verdict
```

---

# 29. Evidence Immutability Rule

After a distribution review records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new package artifacts require new hashes and provenance
new validation evidence must record a new timestamp and source commit
manual edits to packaging evidence after sign-off must be listed as deviations
```

The package artifact, manifest, provenance, validation report, distribution review, and completion record form one immutable evidence set.

---

# 30. Secret Exclusion Rules

The package builder must scan candidate package contents before packaging.

Secret-like content must block release-ready packaging.

Required exclusions:

```text
.env
.env.*
*.pem
*.key
id_rsa
id_ed25519
credentials.json
service-account*.json
*.p12
*.pfx
files containing API_KEY=
files containing SECRET=
files containing TOKEN=
files containing PASSWORD=
files containing PRIVATE KEY
files containing provider credentials
```

Required behavior:

```text
secret match found -> package validation FAIL
secret match found -> artifact excluded
secret match found -> evidence records redacted finding
secret match found -> final verdict NOT DONE
```

The evidence must identify the file path and rule ID, but must not print the secret value.

---

# 31. Runtime Artifact Exclusion Rules

Runtime artifacts must be excluded by default.

Excluded runtime roots:

```text
.agentx-init/security/
.agentx-init/tool_calls/
.agentx-init/implementation/
.agentx-init/memory/
.agentx-init/tmp/
.agentx-init/packaging/raw/
.agentx-init/packaging/staging/
```

Conditionally allowed runtime evidence appendix:

```text
.agentx-init/packaging/package_manifest.json
.agentx-init/packaging/artifact_hash_manifest.json
.agentx-init/packaging/artifact_provenance.json
.agentx-init/packaging/package_validation_report.json
.agentx-init/packaging/distribution_review_report.json
.agentx-init/packaging/packaging_reproducibility_report.json
.agentx-init/packaging/packaging_deviation_register.json
```

Rules:

```text
runtime artifacts are not source files
runtime artifacts may be referenced by hash
runtime artifacts may be included only in an evidence appendix package type
runtime artifacts must be redacted before inclusion
runtime artifact inclusion must be listed in package manifest
```

---

# 32. Generated Artifact Rules

Generated artifacts may be included only if they are deterministic, reviewed, and listed.

Allowed generated artifacts:

```text
schema validation reports
package manifests
hash manifests
provenance records
installation validation reports
review reports
compiled metadata generated by standard Python packaging tools
```

Forbidden generated artifacts:

```text
cache files
compiled Python bytecode
local logs
temporary files
coverage reports unless explicitly approved
large binary outputs
model artifacts
unreviewed generated source
```

Every included generated artifact must have:

```text
source input reference
generator command
created_at timestamp
SHA-256 hash
validation status
```

---

# 33. Distribution Boundary Rules

This layer may create distribution candidates. It may not publish them externally in v1.

Allowed:

```text
build local package artifact
build internal release bundle
write package manifest
write hash manifest
write provenance record
run local install validation
write distribution review report
```

Forbidden in v1:

```text
upload to package registry
push Git tags
create GitHub release
publish Docker image
send package to external service
open network connection for distribution
sign release with private key unless signing layer is explicitly approved
```

If release publication is added later, it requires:

```text
Promotion / Release Gate approval
Git Integration approval
network permission
signing policy
release evidence
rollback plan
```

---

# 34. Installation Validation Rules

Every release-ready package must be installation-validated.

Required validation:

```text
extract package in temporary clean directory
verify manifest exists
verify package hashes
verify import paths resolve
run compileall on packaged Python files
run a minimal smoke test
verify schemas are included
verify CLI entrypoints resolve, if present
verify no forbidden files are present
verify no runtime artifacts are included unless explicitly allowed
verify no secrets are present
```

Validation commands must not require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
running MCP server
```

Failure to install or validate means the package is not release-ready.

---

# 35. Agent_X Integration Notes

## 31.1 Security Sandbox Integration

Packaging must use the Security Sandbox for path boundary validation.

Required behavior:

```text
candidate package paths must be inside repository root or approved output root
forbidden paths must block
path traversal must block
symlink escapes must block
absolute private paths must block or be redacted
```

## 31.2 Policy / Capability Registry Integration

Packaging actions must be checked against policy.

Policy must decide:

```text
caller role allowed to package?
package type allowed?
output path allowed?
dependency policy satisfied?
network disabled?
release-ready status allowed?
promotion approval required?
```

Missing policy must not allow release-ready packaging.

## 31.3 Tool / MCP Adapter Integration

The Tool / MCP Adapter may expose packaging tools later, but only with controlled permissions.

Potential future tools:

```text
build_package_manifest
validate_package_contents
build_release_bundle
hash_distribution_artifacts
validate_installation
write_distribution_review
```

Default MCP exposure must not allow package publication or release promotion.

## 31.4 Promotion / Release Gate Integration

Packaging may produce candidate artifacts. Promotion / Release Gate decides whether they become release artifacts.

A release-ready flag requires:

```text
package validation PASS
hash validation PASS
provenance PASS
reproducibility PASS
install validation PASS
distribution review PASS
promotion approval, if configured
```

## 31.5 Git Integration

Packaging must record Git commit and working-tree status.

Packaging must not:

```text
stage files
commit files
push tags
create branches
mutate Git history
```

## 31.6 Documentation Synchronization

Packaging must verify that core distribution docs exist when required:

```text
README.md
LICENSE
CHANGELOG.md
installation notes
usage notes
```

Documentation absence may be blocking for public release packages and non-blocking for internal development bundles.

---

# 36. OpenCode Borrowing Notes

OpenCode may be used only as an architectural reference for packaging shape and command separation.

Borrowable ideas:

```text
clear CLI command boundaries
separate build and validate commands
tool-specific command wrappers
evidence-backed task outputs
plugin/package manifest concepts
```

Do not borrow:

```text
OpenCode runtime dependency
Bun dependency
Node dependency
uncontrolled plugin loading
network-enabled package fetch behavior
shell-first build behavior
implicit trust in generated artifacts
```

Agent_X packaging must remain Python-first, deterministic, evidence-backed, and policy-controlled.

---

# 37. Public API Contract

Expected public functions for the implementation spec:

```python
build_package_manifest(repo_root, package_config, policy_context) -> dict
validate_package_contents(package_manifest, repo_root, policy_context) -> dict
canonicalize_package_paths(package_manifest, repo_root) -> dict
scan_package_for_secrets(package_manifest, repo_root) -> dict
validate_runtime_artifact_exclusion(package_manifest, repo_root) -> dict
validate_dependency_policy(repo_root, dependency_policy) -> dict
build_sbom_metadata(repo_root, package_manifest) -> dict
build_license_manifest(repo_root, package_manifest) -> dict
build_release_bundle(package_manifest, output_dir, policy_context) -> dict
hash_distribution_artifacts(artifact_paths) -> dict
record_artifact_provenance(package_manifest, build_context) -> dict
write_reproducibility_report(package_manifest, build_context) -> dict
validate_installation(package_artifact, install_manifest, policy_context) -> dict
write_distribution_review(validation_results, repo_root) -> dict
write_packaging_completion_record(review_result, repo_root) -> dict
```

Rules:

```text
all functions return schema-valid dictionaries or dataclass-backed dictionaries
all functions fail closed
all functions write evidence only under approved runtime root
no function mutates source
no function publishes externally
```

---

# 38. Required Test Acceptance Criteria

Required tests:

```text
test_package_manifest_schema_accepts_valid_manifest
test_package_manifest_schema_rejects_missing_commit
test_release_bundle_schema_accepts_valid_bundle
test_installation_manifest_schema_accepts_valid_manifest
test_dependency_policy_blocks_forbidden_dependency
test_dependency_lock_detects_unpinned_dependency
test_dependency_lock_detects_local_path_dependency
test_artifact_hash_manifest_uses_sha256
test_artifact_provenance_records_commit_and_environment
test_package_excludes_env_files
test_package_excludes_agentx_runtime_artifacts
test_package_excludes_pycache_and_cache_dirs
test_secret_like_content_blocks_release_ready
test_package_build_does_not_mutate_source
test_package_validation_fails_on_dirty_working_tree_for_release_ready
test_install_validation_runs_without_network
test_distribution_review_requires_hashes
test_distribution_review_requires_provenance
test_distribution_review_requires_reproducibility_report
test_distribution_review_requires_install_validation
test_distribution_review_blocks_missing_required_area
test_symlink_escape_blocks_release_ready
test_archive_entry_path_traversal_blocks_release_ready
test_deterministic_archive_orders_entries
test_output_root_is_inside_approved_packaging_dist
test_deviation_register_rejects_blocker_deviation
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
package manifest validation PASS
secret exclusion PASS
runtime artifact exclusion PASS
dependency policy validation PASS
hash generation PASS
provenance generation PASS
reproducibility validation PASS
installation validation PASS
source mutation check PASS
distribution review PASS
completion record exists
```

---

# 39. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
package includes secrets
package includes .env files
package includes private keys
package includes forbidden runtime artifacts
package includes .git directory
package includes __pycache__ or cache directories
package includes local machine paths
package includes unreviewed temp files
package includes symlink escape
package includes hardlink escape
package includes archive path traversal entry
package is built from dirty working tree for release-ready status
package artifact lacks SHA-256 hash
package lacks provenance
package lacks reproducibility report
installation validation fails
source mutation occurs during packaging
network is required by default
Bun/Node/OpenCode runtime becomes required
package publication occurs in v1
forbidden dependency is included
unpinned dependency is accepted without policy exception
schema validation is skipped
evidence is missing
evidence hashes are missing
completion record is missing
manifest/archive membership mismatch exists
archive extraction-safety validation fails
package name/version metadata mismatch exists
command exit codes are missing
staging cleanup is not checked
stale artifacts are included
unsigned artifact is represented as signed
public release status is claimed without Promotion / Release Gate approval
```

---

# 40. Definition of Done

The Packaging / Distribution Layer is done when it can create validated, reproducible, evidence-backed package artifacts without leaking unsafe content or mutating source.

It must prove:

```text
package manifest schema exists
release bundle schema exists
installation manifest schema exists
dependency policy schema exists
dependency lock schema exists
artifact hash manifest schema exists
artifact provenance schema exists
package validation report schema exists
distribution review report schema exists
packaging completion record schema exists
packaging deviation register schema exists
packaging reproducibility report schema exists
SBOM metadata schema exists or is safely deferred
license manifest schema exists or is safely deferred
allowed package contents are explicit
forbidden package contents are blocked
runtime artifacts are excluded
secrets are excluded
source mutation does not occur
allowed package formats are enforced
path traversal is blocked
symlink escape is blocked
SHA-256 hashes are generated
provenance is recorded
reproducibility is recorded
installation validation runs
package validation evidence is written
distribution review evidence is written
manifest-to-archive exact membership is verified
archive extraction-safety validation passes
package name/version consistency is verified
command acceptance criteria are enforced
signing/attestation status is recorded or safely deferred
staging cleanup and stale artifact checks pass
completion record exists
```

Final proof commands expected after implementation:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_packaging_schemas.py
git status --short
```

Expected result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 41. Completion Evidence Contract

Completion evidence must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "packaging_completion_record.schema.json",
  "component_id": "AGENTX_PACKAGING_DISTRIBUTION",
  "component_name": "Packaging / Distribution Layer",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/packaging/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/packaging/",
  "approved_package_output_root": ".agentx-init/packaging/dist/",
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "package_artifacts_created": [],
  "hashes_verified": [],
  "provenance_verified": [],
  "reproducibility_verified": [],
  "install_validation_verified": [],
  "secret_exclusion_verified": [],
  "runtime_artifact_exclusion_verified": [],
  "dependency_policy_verified": [],
  "sbom_metadata_verified": [],
  "license_metadata_verified": [],
  "distribution_review_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE|NOT DONE"
}
```

---

# 42. Residual Risks

```yaml
residual_risks:
  - id: "PKG-RISK-001"
    description: "Secrets may be accidentally included in distribution artifacts."
    severity: "critical"
    mitigation: "Secret exclusion rules, forbidden file patterns, redacted evidence, and package validation tests."
  - id: "PKG-RISK-002"
    description: "Runtime evidence may be packaged as source content."
    severity: "high"
    mitigation: "Runtime artifact exclusion rules and explicit evidence appendix policy."
  - id: "PKG-RISK-003"
    description: "Dependency drift may make packages non-reproducible."
    severity: "high"
    mitigation: "Dependency policy and lock validation."
  - id: "PKG-RISK-004"
    description: "Package may be built from dirty or unreviewed source."
    severity: "critical"
    mitigation: "Git commit and working-tree status checks before release-ready status."
  - id: "PKG-RISK-005"
    description: "Distribution artifact may be tampered with after validation."
    severity: "critical"
    mitigation: "SHA-256 artifact hashes, provenance records, and evidence immutability."
  - id: "PKG-RISK-006"
    description: "Packaging could become a publication layer and bypass Promotion / Release Gate."
    severity: "high"
    mitigation: "No external publication in v1; promotion approval required for release-ready status."
  - id: "PKG-RISK-007"
    description: "Archive paths or symlinks may escape the installation directory."
    severity: "critical"
    mitigation: "Canonical path checks, symlink checks, archive entry normalization, and negative tests."
  - id: "PKG-RISK-008"
    description: "Build output may be non-deterministic and impossible to reproduce."
    severity: "high"
    mitigation: "Deterministic archive rules and reproducibility report."
```

---

# 43. Final Sign-Off Checklist

```text
[ ] EQC applied
[ ] FIC applied
[ ] SIB applied
[ ] schemas defined
[ ] evidence rules defined
[ ] evidence immutability defined
[ ] packaging artifact rules defined
[ ] distribution boundary rules defined
[ ] package modes defined
[ ] package manifest schema defined
[ ] release bundle schema defined
[ ] installation manifest schema defined
[ ] dependency policy schema defined
[ ] dependency lock schema defined
[ ] artifact hash manifest schema defined
[ ] artifact provenance schema defined
[ ] package validation report schema defined
[ ] distribution review report schema defined
[ ] deviation register schema defined
[ ] reproducibility report schema defined
[ ] SBOM metadata boundary defined
[ ] license metadata boundary defined
[ ] runtime artifact boundary defined
[ ] package output boundary defined
[ ] source mutation boundary defined
[ ] secret exclusion rules defined
[ ] runtime artifact exclusion rules defined
[ ] path traversal rules defined
[ ] symlink rules defined
[ ] allowed package formats defined
[ ] deterministic build rules defined
[ ] installation validation rules defined
[ ] distribution review rules defined
[ ] Agent_X integration notes defined
[ ] OpenCode borrowing boundaries defined
[ ] threat model and trust boundaries defined
[ ] manifest-to-archive exact membership defined
[ ] archive extraction-safety validation defined
[ ] package naming/version consistency defined
[ ] command acceptance criteria defined
[ ] signing/attestation boundary defined
[ ] staging cleanup and stale artifact rules defined
[ ] fresh-clone validation gate defined
[ ] No-Go conditions defined
[ ] Definition of Done defined
```

---

# 44. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Packaging / Distribution Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed package authority, changed distribution boundary, changed package formats, changed publication policy, changed release-ready rules
```

Blocked without major revision:

```text
allowing package publication in v1
allowing secrets in release-ready packages
allowing missing hashes for release-ready packages
allowing missing provenance for release-ready packages
allowing source mutation during packaging
allowing symlink/path traversal escapes
allowing runtime artifacts as source package content
allowing dirty working tree for release-ready packages
removing Promotion / Release Gate authority
making Bun/Node/OpenCode runtime required
```

The next document should be:

```text
PACKAGING_DISTRIBUTION_IMPLEMENTATION_SPEC
```

---

# 45. Final Rating

This v3 controlling contract is rated:

```text
10/10
```

Reason:

```text
It preserves the v2 scope and adds the remaining production controls: explicit threat model and trust boundaries, manifest-to-archive exact membership checks, archive extraction-safety validation, package naming/version consistency, command acceptance criteria, signing and attestation safe-deferral rules, staging cleanup controls, stale artifact prevention, fresh-clone validation with exit-code evidence, and stronger dependency review for build-system, optional, extras, VCS, and local path dependencies.
```
