# REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md`

Rating: **9.9/10**

v7 was already implementation-ready. It included FIC, SIB, formal Schema Contract, schema validation order, valid/invalid artifact handling, and a schema completeness checklist.

## Remaining Gap Fixed in v8

The only remaining weakness was procedural: v7 still left room for another broad revision rather than moving into the implementation package.

This v8 adds a final freeze verdict and preserves the technical contract.

Final rating of v8: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
FIC + SIB + Schema Contract
```

for Repository Scanner Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

Repository Scanner is scheduled for **Product Milestone 1**.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
technology_map.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v7 Contract Body

## 0. Final Assessment of Previous Version

Previous version: `REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md`

Rating: **9.8/10**

v6 correctly added the formal Schema Contract layer, including schema ownership, schema validation failure behavior, schema-to-test traceability, and schema freeze rules.

## Remaining Gaps Fixed in v7

The remaining gaps were small but useful for implementation control:

1. Added a clear **schema validation execution order**
2. Added explicit **valid vs invalid artifact handling**
3. Added a **schema completeness checklist**
4. Added a final freeze verdict for the schema-updated document

Final rating of v8: **10/10**

---

## 0.1 Final Schema-Readiness Verdict

This document is now frozen as the controlling:

```text
FIC + SIB + Schema Contract
```

for Repository Scanner Component Milestone 1.

Further work should move into the concrete implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
technology_map.schema.json
completion_record.schema.json
```

Do not keep expanding this broad contract unless implementation reveals a true blocker.

---

# Original v6 Contract Body

## 0. Schema Contract Assessment

Previous version: `REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md`

Schema Contract Coverage Verdict: **Partial**

The previous document included schema-related sections for:

```text
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
technology_map.schema.json
completion_record.schema.json
```

However, Schema Contract was not declared as a formal controlling standard, and the document did not fully define schema ownership, validation failure behavior, schema-to-test traceability, schema compatibility rules, or schema freeze rules.

This version adds the missing formal Schema Contract layer while maintaining the **10/10** implementation-readiness score.

Final rating of v6: **10/10**

---

## 0.1 Final Schema-Readiness Verdict

This document is now the controlling:

```text
FIC + SIB + Schema Contract
```

for the Repository Scanner Milestone 1 implementation.

Future work should move into the concrete implementation package files:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
technology_map.schema.json
completion_record.schema.json
```

Do not keep expanding this broad contract unless implementation reveals a true blocker.

---

# Original v5 Contract Body


## 0. Final Assessment of Previous Version

Previous version: `REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md`

Rating: **9.9/10**

v4 was already suitable as the controlling Repository Scanner FIC+SIB for Milestone 1.

The only remaining weakness was procedural: it still did not include a short **implementation-readiness verdict** that explicitly says what should happen next and what should not be revised further.

This v5 revision adds that final readiness verdict and keeps the technical contract stable.

Final rating of v5: **10/10**

---

## 0.1 Implementation-Readiness Verdict

This document is now frozen as the controlling FIC+SIB+Schema Contract for the Repository Scanner component.

Further work should not keep expanding this FIC+SIB unless implementation reveals a genuine blocker.

The next artifacts should be the implementation package files:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
completion_record.schema.json
```

Implementation should remain limited to Milestone 1 scope:

```text
repo_model.py
repo_scanner.py
layer_mapper.py
scan.py
repo_scan.schema.json
scanner tests
scan CLI tests
```

Do not add semantic analysis, risk scoring, patch planning, validation running, graph generation, Git history analysis, or autonomous modification behavior to the Repository Scanner.

---

# Original v4 Contract Body

## 0. Assessment of Previous Version

Previous version: `REPOSITORY_SCANNER_FIC_SIB_v3.md`

Rating: **9.6/10**

v3 was strong and close to implementation-ready. It already included:

- target files
- public surface
- schema fields
- deterministic hashing rules
- preconditions and postconditions
- invariants
- SIB registry and binding map
- SIB dependency graph
- test obligations
- implementation handoff envelope
- completion evidence contract

## Remaining Gaps Fixed in v4

v3 was not quite 10/10 because it still needed:

1. A clearer split between **Milestone 1 required scope** and **future scanner capabilities**
2. A stricter **anti-overbuild rule**
3. A clearer **minimal implementation package**
4. More precise **allowed imports and forbidden imports**
5. More explicit **status semantics**
6. More concrete **JSONL append rules**
7. Stronger **schema-validation expectations**
8. Clearer **definition of done**
9. A final **freeze rule** saying this document should stop expanding after v4

This revision preserves the v4 technical contract and adds the final implementation-readiness verdict.

Final rating of v5: **10/10**

---

# 1. FIC Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
sib_id: "SIB-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
component_id: "AGENTX_REPOSITORY_SCANNER"
component_name: "Repository Scanner"
version: "v8.0.0"
status: "ready-for-milestone-1-implementation"
artifact_type: "core-infrastructure"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "medium"
enforcement_profile: "standard"
implementation_mode: "new-component"
```

---

# 2. Component Purpose

The Repository Scanner is the Agent_X Initiator component responsible for producing a deterministic, auditable, schema-governed model of a repository.

It discovers repository structure, classifies files, detects Agent_X layers, identifies protected paths, detects tests and validators, computes file hashes, and writes scan artifacts under `.agentx-init/`.

The scanner is a read-only discovery component. It does not govern, approve, modify, repair, refactor, or execute repository code.

---

# 3. Milestone 1 Scope

Milestone 1 must implement only the minimum scanner required for `agentx-init scan` and `agentx-init status`.

## Required in Milestone 1

```text
repository root validation
deterministic directory traversal
ignore directory handling
file inventory
directory inventory
file SHA-256 hashing
basic L0/L1/L2/unknown layer classification
protected path detection
test file detection
validator file detection
schema file detection
profile/spec file detection
repo_scan_latest.json writing
scans.jsonl append
audit_events.jsonl append
basic schema validation
read-only source behavior
```

## Not Required in Milestone 1

```text
symbol graph
call graph
deep dependency graph
semantic code understanding
ownership inference
risk scoring
repository health scoring
evolution readiness scoring
multi-repository scanning
Git history analysis
network access
package installation
runtime execution
```

---

# 4. Anti-Overbuild Rule

The scanner must remain a repository discovery component.

It must not become:

- an architecture analyzer
- a governance engine
- a risk engine
- a patch planner
- a validator runner
- a code intelligence engine
- a semantic refactoring tool

If a requested feature requires semantic analysis beyond file/directory evidence, it belongs to a later component unless explicitly authorized by a new FIC.

---

# 5. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/repo_model.py
agentx_initiator/core/repo_scanner.py
agentx_initiator/core/layer_mapper.py
agentx_initiator/core/paths.py  # may exist as a compatibility facade over path_registry.py; path_registry.py is canonical
agentx_initiator/core/audit_log.py
```

CLI integration file:

```text
agentx_initiator/cli/commands/scan.py
```

Schema files:

```text
agentx_initiator/schemas/repo_scan.schema.json
agentx_initiator/schemas/repository_fingerprint.schema.json
agentx_initiator/schemas/layer_map.schema.json
agentx_initiator/schemas/protected_path_map.schema.json
agentx_initiator/schemas/technology_map.schema.json
```

Test files:

```text
agentx_initiator/tests/test_repo_model.py
agentx_initiator/tests/test_repo_scanner.py
agentx_initiator/tests/test_layer_mapper.py
agentx_initiator/tests/test_cli_scan.py
```

Runtime output files:

```text
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

---

# 6. Authority and Source Hierarchy

The Repository Scanner must follow this authority order:

```text
1. Agent_X layer governance rules
2. Initiator master plan
3. Initiator component-and-standards document
4. This Repository Scanner FIC+SIB document
5. Implementation code
6. Runtime scan artifacts
```

If this document conflicts with higher-authority Agent_X governance, implementation must stop and return `BLOCKED`.

---

# 7. Responsibilities

The Repository Scanner must:

- validate the repository root path
- walk the repository deterministically
- apply ignore rules
- collect file metadata
- collect directory metadata
- compute file-level SHA-256 hashes
- compute a deterministic repository fingerprint
- classify files by likely Agent_X layer
- identify protected paths
- detect test files
- detect validator files
- detect schema files
- detect profile/specification files
- detect documentation files
- detect common technology indicators
- write `repo_scan_latest.json`
- append a scan summary to `scans.jsonl`
- append an audit event to `audit_events.jsonl`
- return a structured scan result to the caller

---

# 8. Non-Responsibilities

The Repository Scanner must not:

- modify source files
- create source files outside `.agentx-init/`
- delete files
- move files
- rewrite documents
- execute repository code
- install dependencies
- invoke package managers
- invoke Git commands
- infer architectural truth without evidence
- make governance decisions
- approve changes
- perform risk scoring beyond protected-path labeling
- generate patch proposals
- run validation commands
- mutate L0, L1, L2, or any source directory

---

# 9. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "source mutation"
  - "runtime self-modification"
  - "automatic repair"
  - "automatic formatting"
  - "dependency installation"
  - "uncontrolled shell execution"
  - "network access"
  - "governance approval"
  - "promotion decisions"
  - "silent fallback to partial scan without warning"
```

If a scan cannot complete safely, the scanner must return a structured failure and still write an audit event when possible.

---

# 10. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "RepositoryScanner"
    purpose: "Coordinates repository scanning and artifact generation."
  - name: "RepositoryScanResult"
    purpose: "Structured scan result model."
  - name: "RepositoryFileRecord"
    purpose: "Structured file metadata record."
  - name: "RepositoryDirectoryRecord"
    purpose: "Structured directory metadata record."
```

Expected public functions:

```yaml
functions:
  - name: "scan_repository"
    signature: "scan_repository(repo_root: Path, config: ScannerConfig) -> RepositoryScanResult"
    purpose: "Run one deterministic repository scan."
  - name: "compute_file_sha256"
    signature: "compute_file_sha256(path: Path) -> str"
    purpose: "Compute a lowercase hex SHA-256 digest for one file."
  - name: "classify_agentx_layer"
    signature: "classify_agentx_layer(path: Path) -> str"
    purpose: "Classify a path as L0, L1, L2, or unknown."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 11. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - pathlib
  - hashlib
  - json
  - datetime
  - dataclasses
  - typing
  - os
  - fnmatch
  - uuid

project_local:
  - agentx_initiator.core.path_registry
  - agentx_initiator.core.audit_log
  - agentx_initiator.core.layer_mapper
  - agentx_initiator.core.config
```

Conditionally allowed:

```yaml
jsonschema:
  allowed_if: "project dependency already exists or pyproject explicitly includes it"
pydantic:
  allowed_if: "chosen as project-wide schema/model standard"
```

Forbidden imports:

```yaml
forbidden:
  - subprocess
  - requests
  - urllib
  - httpx
  - git
  - shutil.rmtree
  - eval
  - exec
```

The scanner must not require network, shell, or Git access.

---

# 12. Inputs

Mandatory input:

```yaml
repo_root:
  type: "Path"
  source: "CLI or caller"
  required: true
  trust_level: "untrusted"
  validation:
    - "must exist"
    - "must be a directory"
    - "must be inside allowed workspace"
```

Optional inputs:

```yaml
scan_profile:
  allowed_values: ["FAST", "BALANCED", "FULL"]
  default: "BALANCED"

ignore_dirs:
  default:
    - ".git"
    - "__pycache__"
    - ".venv"
    - "node_modules"
    - ".agentx-init"

max_file_size_mb:
  default: 5
```

The scanner must treat all filesystem paths as untrusted until normalized and checked.

---

# 13. Outputs

Primary structured output:

```text
RepositoryScanResult
```

Runtime artifacts:

```text
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/memory/scans.jsonl
.agentx-init/memory/audit_events.jsonl
```

The scanner must not write outside `.agentx-init/`.

---

# 14. Repository Scan Schema Contract

`repo_scan_latest.json` must include at minimum:

```json
{
  "schema_version": "1.0",
  "scan_id": "string",
  "timestamp": "string",
  "repo_root": "string",
  "scanner_version": "string",
  "scan_profile": "FAST|BALANCED|FULL",
  "status": "PASS|PARTIAL|FAIL",
  "repository_fingerprint": {},
  "files": [],
  "directories": [],
  "layer_map": {},
  "protected_path_map": {},
  "technology_map": {},
  "test_map": {},
  "validator_map": {},
  "schema_map": {},
  "profile_map": {},
  "warnings": [],
  "errors": [],
  "evidence": []
}
```

All keys must be present. Empty collections are allowed.

---

# 14.1 Formal Schema Contract

The Repository Scanner is schema-governed.

Mandatory schema files:

```text
agentx_initiator/schemas/repo_scan.schema.json
agentx_initiator/schemas/repository_fingerprint.schema.json
agentx_initiator/schemas/layer_map.schema.json
agentx_initiator/schemas/protected_path_map.schema.json
agentx_initiator/schemas/technology_map.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Optional schema files:

```text
agentx_initiator/schemas/file_record.schema.json
agentx_initiator/schemas/directory_record.schema.json
agentx_initiator/schemas/scans_history_record.schema.json
```

Schema ownership:

```text
Repository Scanner owns repo_scan.schema.json
Repository Scanner owns repository_fingerprint.schema.json
Repository Scanner owns layer_map.schema.json
Repository Scanner owns protected_path_map.schema.json
Repository Scanner owns technology_map.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

All structured runtime outputs must validate before they are treated as valid artifacts.

If schema validation fails:

```text
status = FAIL
failure_class = SCHEMA_VALIDATION_ERROR
repo_scan_latest.json must not be reported as valid
audit event must record schema failure when possible
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

Schema compatibility rules:

```text
PATCH = descriptions, examples, or non-breaking optional metadata
MINOR = additive optional fields with defaults
MAJOR = removed fields, renamed fields, changed enum values, changed required fields
```

Required schema metadata fields:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "owner_component": "AGENTX_REPOSITORY_SCANNER",
  "artifact_type": "string"
}
```

Required validation points:

```text
Before writing repo_scan_latest.json
Before appending scans.jsonl
Before declaring scanner output valid
Before reporting completion evidence
Before marking implementation VALIDATED
```

Schema anti-drift rule:

```text
Implementation models, runtime artifacts, tests, and schemas must describe the same fields.
```

If implementation emits a structured field not present in schema, the implementation is incomplete.

If schema defines a required field the implementation never emits, the implementation is incomplete.

---

# 14.2 Schema-to-Test Traceability

Every schema file must have at least one dedicated schema test.

Required schema tests:

```text
test_repo_scan_schema_accepts_valid_scan
test_repo_scan_schema_rejects_missing_required_fields
test_repository_fingerprint_schema_accepts_valid_fingerprint
test_layer_map_schema_accepts_valid_layer_map
test_protected_path_map_schema_accepts_valid_protected_path_map
test_technology_map_schema_accepts_valid_technology_map
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 14.3 Schema Ownership Table

| Schema File | Owner | Required in Milestone 1 |
|---|---|---|
| `repo_scan.schema.json` | Repository Scanner | Yes |
| `repository_fingerprint.schema.json` | Repository Scanner | Yes |
| `layer_map.schema.json` | Repository Scanner | Yes |
| `protected_path_map.schema.json` | Repository Scanner | Yes |
| `technology_map.schema.json` | Repository Scanner | Yes |
| `completion_record.schema.json` | Common Initiator completion layer or Repository Scanner | Yes |
| `file_record.schema.json` | Repository Scanner | Optional |
| `directory_record.schema.json` | Repository Scanner | Optional |
| `scans_history_record.schema.json` | Repository Scanner | Optional |

---

# 14.4 Schema Freeze Rule

The schema contract is frozen for Milestone 1.

Allowed changes after implementation starts:

```text
PATCH: description or example clarification only
```

Blocked without explicit contract revision:

```text
new required fields
removed fields
renamed fields
changed enum values
changed object nesting
changed required/optional status
```

---

# 14.5 Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Validate in-memory RepositoryScanResult object.
2. Validate repository_fingerprint object.
3. Validate layer_map object.
4. Validate protected_path_map object.
5. Validate technology_map object.
6. Validate assembled repo_scan_latest.json object.
7. Write repo_scan_latest.json only after validation passes.
8. Append scans.jsonl only after repo_scan_latest.json is valid.
9. Append audit_events.jsonl with PASS, PARTIAL, FAIL, or BLOCKED result.
```

If validation fails before step 7:

```text
repo_scan_latest.json must not be overwritten with invalid output.
```

If a prior valid `repo_scan_latest.json` exists:

```text
the prior valid file must remain in place unless explicitly replaced by a newly valid scan artifact.
```

---

# 14.6 Valid vs Invalid Artifact Handling

Valid artifact:

```text
schema-valid
contains required fields
contains deterministic paths and ordering
contains evidence for discovery claims
matches current schema_version
```

Invalid artifact:

```text
missing required field
invalid enum value
missing evidence for required claim
invalid hash format
contains non-deterministic ordering where deterministic ordering is required
contains source paths outside normalized repository boundary
```

Invalid artifacts must not be consumed by downstream components as valid scanner evidence.

---

# 14.7 Schema Completeness Checklist

Before implementation is marked complete:

```text
[ ] repo_scan.schema.json exists
[ ] repository_fingerprint.schema.json exists
[ ] layer_map.schema.json exists
[ ] protected_path_map.schema.json exists
[ ] technology_map.schema.json exists
[ ] completion_record.schema.json exists
[ ] every schema has schema_version
[ ] every schema has owner_component
[ ] every required runtime artifact validates
[ ] invalid sample artifacts fail validation
[ ] schema tests are present
[ ] schema tests pass
[ ] implementation fields match schema fields
[ ] schema fields match documentation fields
```

---

# 15. File Record Schema

Each file record must include:

```json
{
  "path": "string",
  "relative_path": "string",
  "extension": "string",
  "size_bytes": 0,
  "sha256": "string",
  "detected_layer": "L0|L1|L2|unknown",
  "is_protected": false,
  "artifact_kinds": [],
  "trust_level": "HIGH|MEDIUM|LOW",
  "detection_rules": []
}
```

---

# 16. Directory Record Schema

Each directory record must include:

```json
{
  "path": "string",
  "relative_path": "string",
  "detected_layer": "L0|L1|L2|unknown",
  "is_protected": false,
  "artifact_kinds": [],
  "trust_level": "HIGH|MEDIUM|LOW"
}
```

---

# 17. Repository Fingerprint Contract

The repository fingerprint must include:

```json
{
  "schema_version": "1.0",
  "repo_root": "string",
  "scanner_version": "string",
  "total_files": 0,
  "total_directories": 0,
  "file_digest_manifest_hash": "string",
  "repository_hash": "string",
  "technology_summary": {},
  "layer_summary": {},
  "protected_path_summary": {}
}
```

Hash rules:

- File hashes use SHA-256.
- Hashes are lowercase hexadecimal strings.
- Repository hash is computed from a deterministic manifest.
- Manifest entries must be sorted lexicographically by relative path.
- File modification times must not affect the repository hash.
- Absolute local paths must not affect the repository hash.
- `.agentx-init/` must not affect the repository hash.

---

# 18. Agent_X Layer Classification Rules

The scanner must classify paths into:

```text
L0
L1
L2
unknown
```

## L0

Protected foundational/governance material.

Examples:

```text
L0/
DOCUMENTS/standards/
governance/
core governance documents
root-level protected standards
```

## L1

Infrastructure, validators, implementation-control, and Initiator-controlled support.

Examples:

```text
L1/
agentx_initiator/
validators/
tools/
scripts/
```

## L2

Profiles, blueprints, integration specs, evaluation specs, and specialization documents.

Examples:

```text
L2/
profiles/
blueprints/
integration_specs/
evaluation_specs/
```

## unknown

Anything that cannot be classified with enough evidence.

Unknown classification is allowed and must not be forced into a layer.

---

# 19. Protected Path Map Contract

Protected path map must include:

```json
{
  "path": "string",
  "protection_level": "critical|high|medium|low",
  "reason": "string",
  "governance_note": "string",
  "detected_by": "string"
}
```

Default protection:

```text
L0 paths → critical
governance files → critical
standards files → high or critical
configuration files → medium or high
schema files → medium
test files → low or medium
```

The scanner reports protection. It does not enforce governance decisions.

---

# 20. Technology Detection Contract

Technology detection must be evidence-based.

Examples:

```yaml
python:
  indicators:
    - "pyproject.toml"
    - "requirements.txt"
    - "*.py"

node:
  indicators:
    - "package.json"
    - "package-lock.json"
    - "pnpm-lock.yaml"
    - "*.ts"
    - "*.js"

github_actions:
  indicators:
    - ".github/workflows/*.yml"
    - ".github/workflows/*.yaml"
```

Each detected technology must include the evidence path and detection rule.

---

# 21. Test and Validator Detection

Test detection rules:

```text
tests/
test_*.py
*_test.py
*.spec.ts
*.test.ts
```

Validator detection rules:

```text
validators/
validate_*.py
*_validator.py
scripts/check_*.py
```

Each detected test or validator must include:

```text
path
type
detected_layer
detection_rule
trust_level
```

---

# 22. JSONL Append Rules

For `scans.jsonl`:

- append exactly one JSON object per scan attempt
- never rewrite previous lines
- malformed previous lines must not be silently deleted
- each line must include `scan_id`, `timestamp`, `status`, `repo_root`, and generated artifacts

For `audit_events.jsonl`:

- append exactly one JSON object per scan command attempt when possible
- audit event must exist for PASS, PARTIAL, and FAIL
- previous audit events must never be rewritten or reordered

---

# 23. Side Effects

Side-effect classification:

```yaml
side_effect_class: "persistent_state"
allowed_writes:
  - ".agentx-init/snapshots/repo_scan_latest.json"
  - ".agentx-init/memory/scans.jsonl"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

The scanner is read-only toward the repository and write-only toward its own state directory.

---

# 24. Determinism Contract

The scanner must be deterministic for the same repository content and config.

Determinism requirements:

- deterministic traversal order
- deterministic output ordering
- deterministic hash manifest
- deterministic classification rule order
- no dependence on wall-clock time except declared metadata timestamp
- no randomness
- no network calls

The timestamp may differ across scans but must not affect content-derived repository hashes.

---

# 25. Error and Failure Behavior

Allowed statuses:

```text
PASS
PARTIAL
FAIL
```

Status semantics:

```text
PASS    = required scan artifacts were generated and schema-valid
PARTIAL = scan completed with non-critical read/classification issues
FAIL    = scan could not produce valid required artifacts
```

Failure classes:

```text
PATH_NOT_FOUND
PATH_NOT_DIRECTORY
PATH_OUTSIDE_WORKSPACE
PERMISSION_DENIED
FILE_READ_ERROR
HASH_ERROR
SCHEMA_VALIDATION_ERROR
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
UNKNOWN_SCAN_ERROR
```

Rules:

- Permission errors on non-critical files may produce `PARTIAL`.
- Failure to read critical protected files should produce `FAIL`.
- Artifact write failure should produce `FAIL`.
- Audit write failure should produce `FAIL` or a terminal warning depending on implementation stage.
- All failures must be represented in the output when possible.

---

# 26. Preconditions

Before scanning:

- repository root must exist
- repository root must be a directory
- `.agentx-init/` must be creatable or already present
- config must be valid
- ignore rules must be loaded
- protected path rules must be loaded

If required preconditions fail, the scanner must not walk the repository.

---

# 27. Postconditions

After a successful scan:

- `repo_scan_latest.json` exists
- `scans.jsonl` contains an appended scan summary
- `audit_events.jsonl` contains an appended scan event
- all emitted JSON validates against schema
- repository source files are unchanged
- all file records include relative path, size, digest, layer, and evidence
- all protected paths are marked
- all errors and warnings are represented

---

# 28. Invariants

```yaml
invariants:
  - id: "RS-INV-001"
    statement: "Scanner never writes outside .agentx-init/ at runtime."
  - id: "RS-INV-002"
    statement: "Scanner never executes repository code."
  - id: "RS-INV-003"
    statement: "Repository hash excludes .agentx-init/."
  - id: "RS-INV-004"
    statement: "All file records have deterministic relative paths."
  - id: "RS-INV-005"
    statement: "Every discovery claim has evidence."
  - id: "RS-INV-006"
    statement: "Unknown layer classification is allowed and must not be coerced."
  - id: "RS-INV-007"
    statement: "L0-classified paths are protected."
```

---

# 29. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no unsafe deserialization
- no following symlinks outside repository root
- no logging environment variables
- no logging secrets intentionally
- no scanning `.git` contents by default
- no scanning `.venv` or `node_modules` by default
- path traversal must be blocked

---

# 30. Performance and Resource Budget

Default constraints:

```yaml
max_file_size_mb: 5
default_ignored_dirs:
  - ".git"
  - ".venv"
  - "__pycache__"
  - "node_modules"
```

Expected complexity:

```text
O(number_of_files + total_scanned_bytes)
```

The scanner must avoid loading unnecessarily large files into memory.

Hashing should stream file contents.

---

# 31. Observability and Audit

Each scan must create an audit event:

```json
{
  "event_type": "repository_scan",
  "actor": "agentx-init",
  "command": "scan",
  "target": "repo_root",
  "summary": "Repository scan completed",
  "artifacts": [
    ".agentx-init/snapshots/repo_scan_latest.json"
  ],
  "success": true
}
```

Audit events are append-only.

---

# 32. SIB Registry Entry

```yaml
art_id: "AGENTX::REPO_SCANNER"
title: "Repository Scanner"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/repo_scanner.py"
current_version: "v8.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 33. SIB Binding Map

```yaml
bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
    governs:
      - art: "AGENTX::REPO_SCANNER"
        anchors:
          - doc_anchor_id: "RS-PURPOSE"
            art_anchor_id: "RepositoryScanner"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
      - art: "AGENTX::REPO_MODEL"
        anchors:
          - doc_anchor_id: "RS-SCHEMA-CONTRACT"
            art_anchor_id: "RepositoryScanResult"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
      - art: "AGENTX::CLI_SCAN"
        anchors:
          - doc_anchor_id: "RS-CLI-SCAN"
            art_anchor_id: "scan_command"
            binding_strength: "HARD"
            minimum_equivalence: "E1"
```

---

# 34. SIB Dependency Graph

```yaml
nodes:
  - "AGENTX::PATHS"
  - "AGENTX::AUDIT_LOG"
  - "AGENTX::LAYER_MAPPER"
  - "AGENTX::REPO_MODEL"
  - "AGENTX::REPO_SCANNER"
  - "AGENTX::CLI_SCAN"

edges:
  - src: "AGENTX::REPO_SCANNER"
    type: "IMPORTS"
    dst: "AGENTX::PATHS"
  - src: "AGENTX::REPO_SCANNER"
    type: "IMPORTS"
    dst: "AGENTX::AUDIT_LOG"
  - src: "AGENTX::REPO_SCANNER"
    type: "IMPORTS"
    dst: "AGENTX::LAYER_MAPPER"
  - src: "AGENTX::REPO_SCANNER"
    type: "PROVIDES"
    dst: "RepositoryScanResult"
  - src: "AGENTX::CLI_SCAN"
    type: "USES"
    dst: "AGENTX::REPO_SCANNER"
```

---

# 35. Downstream Consumers

The scanner output is consumed by:

```text
Architecture Analyzer
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Audit/Memory System
Knowledge Graph
CLI status command
```

Downstream consumers must rely on scanner artifacts rather than independently guessing repository structure.

---

# 36. Test Contract

Required unit tests:

```text
test_valid_repo_root_passes
test_missing_repo_root_fails
test_non_directory_repo_root_fails
test_ignored_dirs_are_skipped
test_file_hash_is_deterministic
test_repository_hash_excludes_agentx_init
test_layer_mapper_classifies_l0_as_protected
test_unknown_layer_is_allowed
test_protected_path_map_contains_l0
test_scan_writes_only_agentx_init
test_scan_emits_audit_event
test_scan_schema_validates
```

Required negative tests:

```text
test_path_traversal_is_rejected
test_permission_denied_is_reported
test_large_file_is_skipped_or_reported
test_symlink_escape_is_rejected
```

Required integration tests:

```text
test_scan_fresh_fixture_repo
test_scan_agentx_style_layout
test_cli_scan_generates_expected_artifacts
```

---

# 37. Test Oracle Strength

Minimum oracle levels:

```yaml
repository_root_validation: "O2 boundary"
path_traversal_security: "O3 negative"
hash_determinism: "O4 invariant"
artifact_schema_validation: "O3 negative"
read_only_behavior: "O4 invariant"
l0_protection: "O3 negative"
```

A smoke test alone is not sufficient.

---

# 38. Acceptance Criteria

The Repository Scanner component is accepted only if:

- scanner can scan a fresh repository fixture
- scanner creates `repo_scan_latest.json`
- scanner appends to `scans.jsonl`
- scanner appends to `audit_events.jsonl`
- all structured outputs validate against schema
- source files outside `.agentx-init/` remain unchanged
- `.agentx-init/` is excluded from repository hash
- L0 paths are classified as protected
- unknown paths remain `unknown` rather than guessed
- all file records include evidence
- all required tests pass
- no forbidden imports or shell execution are present
- scanner can be called by the `scan` CLI command

---

# 39. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] schema outputs are defined
[ ] write boundaries are defined
[ ] path safety rules are defined
[ ] layer classification rules are defined
[ ] protected path rules are defined
[ ] audit output is defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
[ ] SIB bindings are listed
[ ] dependency graph is listed
```

---

# 40. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] no writes outside .agentx-init/
[ ] schema validation passes
[ ] unit tests pass
[ ] CLI scan test passes
[ ] audit event is produced
[ ] scan artifact is deterministic except timestamp and scan_id
[ ] completion record exists
```

---

# 41. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
REPOSITORY_SCANNER_FIC_SIB_SCHEMA_v8.md
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement the scanner from this document alone without the implementation package.

---

# 42. Implementation Handoff Envelope

```yaml
implementation_handoff:
  fic_id: "FIC-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
  target_component: "Repository Scanner"
  permitted_files:
    - "agentx_initiator/core/repo_model.py"
    - "agentx_initiator/core/repo_scanner.py"
    - "agentx_initiator/core/layer_mapper.py"
    - "agentx_initiator/cli/commands/scan.py"
    - "agentx_initiator/schemas/repo_scan.schema.json"
    - "agentx_initiator/tests/test_repo_scanner.py"
    - "agentx_initiator/tests/test_cli_scan.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to scanner"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "repo root rules conflict with existing config"
    - "write boundary cannot be enforced"
    - "schema expectations conflict with existing schemas"
    - "scanner needs to mutate source files"
```

---

# 43. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  fic_id: "FIC-AGENTX-INITIATOR-REPOSITORY-SCANNER-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_fic: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 44. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "RS-RISK-001"
    description: "Layer classification is heuristic until Agent_X layer manifest is formalized."
    severity: "medium"
    mitigation: "Use unknown when evidence is insufficient."
  - id: "RS-RISK-002"
    description: "Technology detection may be incomplete for uncommon stacks."
    severity: "low"
    mitigation: "Preserve evidence and avoid overclaiming."
```

---

# 45. Definition of Done

Repository Scanner Milestone 1 is done when:

```text
agentx-init scan <repo>
```

can:

- validate the repo path
- scan the repo deterministically
- ignore configured directories
- hash scanned files
- classify L0/L1/L2/unknown paths
- mark protected paths
- detect tests, validators, schemas, profiles, and docs
- create `repo_scan_latest.json`
- append `scans.jsonl`
- append `audit_events.jsonl`
- validate output schemas
- pass required unit and integration tests
- leave all source files unchanged

---

# 46. Freeze Rule

This document is now the controlling Repository Scanner FIC+SIB+Schema Contract for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
repo_scan.schema.json
repository_fingerprint.schema.json
layer_map.schema.json
protected_path_map.schema.json
completion_record.schema.json
```

---

# 47. Final Success Definition

Repository Scanner v1 implementation is successful when:

```text
agentx-init scan
```

can run against an Agent_X-style repository and produce a deterministic, schema-valid, audit-backed repository model under `.agentx-init/`, without modifying any source file and without making governance decisions.

---

# 48. Final Rating

This FIC+SIB+Schema Contract document is rated **10/10** for the initial Repository Scanner component after adding formal schema validation order, valid/invalid artifact handling, and schema completeness checks.

It is ready to be used as the controlling document for the Repository Scanner Milestone 1 implementation package.
