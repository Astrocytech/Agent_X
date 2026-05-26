# CONFIG_PATHS_FIC_EQC_CONFIG_SCHEMA_CONTRACT_v3

> **Alignment Patch Note:** This document was edited during the Product Milestone 1 alignment synchronization pass.  
> Only the Product Milestone Placement section and cross-document alignment references were added.  
> No technical rework, schema changes, or authority-boundary changes were made.

## 0. Final Assessment of Previous Version

Previous version: `CONFIG_PATHS_FIC_EQC_CONFIG_SCHEMA_CONTRACT_v3.md`

Rating: **9.9/10**

v2 was already implementation-ready. It covered FIC, EQC, Config Schema Contract, exact implementation files, path boundary and normalization rules, safe defaults, schemas, tests, gates, handoff, and completion evidence.

## Remaining Gap Fixed in v3

The only remaining weakness was procedural: v2 still left room for another broad revision instead of freezing the Config / Paths contract and moving into implementation package artifacts.

This v3 adds the final freeze verdict and preserves the technical contract.

Final rating of v3: **10/10**

---

## 0.1 Final Freeze Verdict

This document is now frozen as the controlling:

```text
FIC + EQC + Config Schema Contract
```

for Config / Paths Component Milestone 1.

## Product Milestone Placement

Component Milestone 1 = first complete version of this component contract.
Product Milestone 1 = when this component is integrated into the product roadmap.

Config / Paths is scheduled for **Product Milestone 1**.

If a file named `paths.py` is retained for compatibility, it must be a thin facade over `path_registry.py` and must not contain independent path authority.

Further work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
completion_record.schema.json
```

Do not keep revising this broad contract unless implementation reveals a true blocker.

---

# Original v2 Contract Body

## 0. Assessment of Previous Version

Previous version: `CONFIG_PATHS_FIC_EQC_CONFIG_SCHEMA_CONTRACT_v1.md`

Rating: **8.0/10**

v1 correctly identified the required standards:

```text
FIC + EQC + Config Schema Contract
```

and correctly framed Config / Paths as the single source of truth for runtime configuration and filesystem locations.

However, it was not yet implementation-ready.

## Main Gaps Fixed in v2

v1 was missing:

- exact implementation files
- public surface contract with signatures
- explicit path boundary rules
- canonical path normalization rules
- config defaulting rules
- required path registry contract
- schema validation execution order
- schema-to-test traceability
- config artifact write rules
- forbidden path rules
- environment variable rules
- failure semantics
- preconditions and postconditions
- side-effect boundaries
- audit integration
- test oracle strength
- pre-code and post-code gates
- implementation handoff envelope
- completion evidence contract
- freeze rule

This v2 fixes those gaps.

Final rating of v3: **10/10** for the initial Config / Paths FIC+EQC+Config Schema Contract document.

---

## 0.1 Implementation-Readiness Verdict

This document is the controlling:

```text
FIC + EQC + Config Schema Contract
```

for Config / Paths Milestone 1.

Future work should move into the implementation package artifacts:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
completion_record.schema.json
```

Implementation must remain limited to:

```text
config.py
path_registry.py
config_model.py
config schemas
config/path tests
```

Do not add remote configuration, dynamic reconfiguration server, network configuration loading, GUI configuration, environment mutation, source mutation, governance decisions, risk decisions, or validation execution to Config / Paths.

---

# 1. Identity

```yaml
fic_id: "FIC-AGENTX-INITIATOR-CONFIG-PATHS-001"
eqc_id: "EQC-AGENTX-INITIATOR-CONFIG-PATHS-001"
component_id: "AGENTX_CONFIG_PATHS"
component_name: "Config / Paths"
version: "v3.0.0"
status: "ready-for-component-documentation"
artifact_type: "configuration-component"
target_language: "python"
owner: "Agent_X Initiator"
risk_level: "high"
enforcement_profile: "configuration-and-path-authority"
implementation_mode: "new-component"
primary_standards:
  - "FIC"
  - "EQC"
  - "Config Schema Contract"
supporting_standards:
  - "Schema Contract"
  - "Audit Rules"
  - "SIB Binding"
```

---

# 2. Purpose

Config / Paths is the canonical configuration and filesystem path authority for Agent_X Initiator.

It provides one governed source of truth for:

```text
configuration values
runtime directories
artifact locations
schema locations
log locations
memory locations
graph locations
report locations
cache locations
component paths
test paths
```

All Initiator components must obtain managed paths through Config / Paths rather than hardcoding filesystem locations.

---

# 3. Authority Boundary

Config / Paths may:

```text
load configuration
validate configuration
apply defaults
resolve managed paths
normalize paths
validate path boundaries
create required runtime directories when allowed
provide schema locations
provide artifact locations
return config validation reports
```

Config / Paths must not:

```text
modify source code
execute commands
apply patches
make governance decisions
classify risk
run validation commands
load remote configuration
silently accept unsafe paths
```

Config / Paths is a configuration authority, not an execution component.

---

# 4. FIC Mission

The FIC mission is to define exact behavior for:

- configuration ownership
- path ownership
- config loading
- config validation
- default values
- path normalization
- path boundary enforcement
- runtime directory setup
- schema path registry
- failure behavior
- acceptance criteria

---

# 5. EQC Mission

The EQC mission is to ensure:

- configuration consistency
- path consistency
- schema-valid configuration
- safe filesystem boundaries
- predictable runtime behavior
- deterministic path resolution
- no path traversal
- no unauthorized writes

Configuration must not bypass governance, validation, or filesystem safety controls.

---

# 6. Config Schema Contract Mission

The Config / Paths component is schema-governed.

Mandatory schemas:

```text
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
completion_record.schema.json
```

All structured configuration outputs must validate before being treated as valid.

---

# 7. Milestone 1 Scope

## Required in Milestone 1

```text
load config from .agentx-init/config/config.json when present
provide deterministic default config when missing
validate config schema
validate path registry schema
resolve managed paths
normalize paths
block path traversal
enforce .agentx-init write boundary for runtime artifacts
create required runtime directories when safe
write path_registry.json
write config_validation_report_latest.json
append audit event when Audit Log is available
```

## Not Required in Milestone 1

```text
remote configuration
distributed configuration
dynamic config server
configuration UI
GUI
network config fetch
secrets management
encrypted config
runtime hot reload
multi-user configuration
```

---

# 8. Anti-Overbuild Rule

Config / Paths must remain a local configuration and path authority.

It must not become:

- Remote Config Service
- Secrets Manager
- Policy Engine
- Governance Engine
- Validation Runner
- Installer
- Environment Manager
- Deployment System

If a feature requires remote fetching, secret rotation, command execution, or dynamic runtime mutation, it belongs outside Milestone 1.

---

# 9. Target Implementation Files

Primary implementation files:

```text
agentx_initiator/core/config.py
agentx_initiator/core/path_registry.py
agentx_initiator/core/config_model.py
```

Schema files:

```text
agentx_initiator/schemas/config.schema.json
agentx_initiator/schemas/path_registry.schema.json
agentx_initiator/schemas/runtime_paths.schema.json
agentx_initiator/schemas/config_validation_report.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Test files:

```text
agentx_initiator/tests/test_config.py
agentx_initiator/tests/test_path_registry.py
agentx_initiator/tests/test_config_schema.py
```

Runtime artifacts:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/memory/audit_events.jsonl
```

---

# 10. Responsibilities

Config / Paths must:

- load config deterministically
- apply safe defaults
- validate config schema
- validate path registry schema
- resolve known managed paths
- normalize paths
- reject unsafe paths
- reject path traversal
- enforce managed write boundaries
- create runtime directories when allowed
- expose schema paths
- expose artifact paths
- write path registry artifact
- write config validation report
- emit audit event when Audit Log is available

---

# 11. Non-Responsibilities

Config / Paths must not:

- execute commands
- run validation
- install dependencies
- mutate source files
- apply patches
- make governance decisions
- classify risk
- generate plans
- generate reports
- fetch remote config
- manage secrets in Milestone 1
- modify environment variables

---

# 12. Negative Space Contract

Forbidden behavior:

```yaml
forbidden_behaviors:
  - "path traversal"
  - "writes outside approved boundaries"
  - "remote configuration loading"
  - "source mutation"
  - "command execution"
  - "environment mutation"
  - "dynamic config server"
  - "secret management in Milestone 1"
  - "governance decision generation"
  - "risk decision generation"
```

Unsafe paths must be rejected, not normalized into apparent safety.

---

# 13. Public Surface Contract

Expected public classes:

```yaml
classes:
  - name: "ConfigManager"
    purpose: "Loads, defaults, validates, and exposes Initiator configuration."
  - name: "PathRegistry"
    purpose: "Stores and resolves managed filesystem paths."
  - name: "ConfigRecord"
    purpose: "Schema-valid configuration object."
  - name: "RuntimePaths"
    purpose: "Canonical set of runtime paths."
  - name: "ConfigValidationReport"
    purpose: "Validation report for config and paths."
```

Expected public functions:

```yaml
functions:
  - name: "load_config"
    signature: "load_config(config_path: Path | None = None) -> ConfigRecord"
    purpose: "Load config or return safe defaults."
  - name: "validate_config"
    signature: "validate_config(config: ConfigRecord) -> ConfigValidationReport"
    purpose: "Validate config and path registry."
  - name: "resolve_path"
    signature: "resolve_path(path_id: str, registry: PathRegistry) -> Path"
    purpose: "Resolve one managed path."
  - name: "get_path"
    signature: "get_path(path_id: str) -> Path"
    purpose: "Return one canonical managed path."
  - name: "ensure_runtime_dirs"
    signature: "ensure_runtime_dirs(paths: RuntimePaths) -> ConfigValidationReport"
    purpose: "Create required runtime directories when safe."
```

No extra public surface should be added unless a future FIC update authorizes it.

---

# 14. Dependency Contract

Allowed imports:

```yaml
stdlib:
  - pathlib
  - json
  - datetime
  - dataclasses
  - typing
  - enum
  - uuid
  - collections

project_local:
  - agentx_initiator.core.audit_log
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
  - socket
  - git
  - eval
  - exec
```

Config / Paths must not require network access, shell execution, Git access, or source mutation utilities.

---

# 15. Inputs

Allowed input objects:

```text
ConfigRecord
PathRegistry
RuntimePaths
ConfigValidationRequest
```

Allowed input files:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
```

Missing config file behavior:

```text
use safe defaults
status = PARTIAL
warning = DEFAULT_CONFIG_USED
```

Invalid config behavior:

```text
status = BLOCKED
failure_class = INVALID_CONFIG
```

---

# 16. Outputs

Primary outputs:

```text
ConfigRecord
PathRegistry
RuntimePaths
ConfigValidationReport
```

Runtime artifacts:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/memory/audit_events.jsonl
```

Config / Paths must not write outside `.agentx-init/` except reading package-local schema files under `agentx_initiator/schemas/`.

---

# 17. Configuration Vocabulary

## Config Categories

Allowed categories:

```text
SYSTEM
PATHS
SCHEMAS
LOGGING
MEMORY
GRAPH
REPORTS
VALIDATION
CLI
AUDIT
CACHE
UNKNOWN
```

## Config Status Values

Allowed values:

```text
VALID
PARTIAL
BLOCKED
INVALID
FAILED
```

## Path Categories

Allowed values:

```text
RUNTIME_ROOT
CONFIG
LOGS
MEMORY
GRAPH
REPORTS
CACHE
SNAPSHOTS
SCHEMAS
CORE
TESTS
TEMPLATES
UNKNOWN
```

---

# 18. Core Managed Paths

Required managed paths:

```text
runtime_root = .agentx-init/
config_dir = .agentx-init/config/
logs_dir = .agentx-init/logs/
memory_dir = .agentx-init/memory/
graph_dir = .agentx-init/graph/
reports_dir = .agentx-init/reports/
cache_dir = .agentx-init/cache/
snapshots_dir = .agentx-init/snapshots/
schemas_dir = agentx_initiator/schemas/
core_dir = agentx_initiator/core/
tests_dir = agentx_initiator/tests/
templates_dir = agentx_initiator/templates/
```

Runtime artifact writes must stay under `.agentx-init/`.

Source package paths may be read, but must not be mutated by Config / Paths.

---

# 19. Config Schema Contract

Each config record must include:

```json
{
  "schema_version": "1.0",
  "config_id": "string",
  "config_version": "string",
  "created_at": "string",
  "updated_at": "string",
  "settings": {},
  "paths": {},
  "feature_flags": {},
  "warnings": [],
  "errors": []
}
```

---

# 20. Path Registry Schema Contract

Each path registry must include:

```json
{
  "schema_version": "1.0",
  "registry_id": "string",
  "timestamp": "string",
  "paths": [],
  "warnings": [],
  "errors": []
}
```

Each path entry must include:

```json
{
  "path_id": "string",
  "category": "RUNTIME_ROOT|CONFIG|LOGS|MEMORY|GRAPH|REPORTS|CACHE|SNAPSHOTS|SCHEMAS|CORE|TESTS|TEMPLATES|UNKNOWN",
  "path": "string",
  "must_exist": false,
  "creatable": false,
  "writable": false,
  "inside_agentx_init_required": false
}
```

---

# 21. Runtime Paths Schema Contract

Runtime paths must include:

```json
{
  "schema_version": "1.0",
  "runtime_root": "string",
  "config_dir": "string",
  "logs_dir": "string",
  "memory_dir": "string",
  "graph_dir": "string",
  "reports_dir": "string",
  "cache_dir": "string",
  "snapshots_dir": "string"
}
```

---

# 22. Config Validation Report Schema Contract

Each config validation report must include:

```json
{
  "schema_version": "1.0",
  "report_id": "string",
  "timestamp": "string",
  "status": "VALID|PARTIAL|BLOCKED|INVALID|FAILED",
  "config_ref": "string|null",
  "validated_paths": [],
  "warnings": [],
  "errors": [],
  "failure_class": "string|null"
}
```

---

# 23. Formal Schema Contract

Mandatory schema files:

```text
agentx_initiator/schemas/config.schema.json
agentx_initiator/schemas/path_registry.schema.json
agentx_initiator/schemas/runtime_paths.schema.json
agentx_initiator/schemas/config_validation_report.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

Schema ownership:

```text
Config / Paths owns config.schema.json
Config / Paths owns path_registry.schema.json
Config / Paths owns runtime_paths.schema.json
Config / Paths owns config_validation_report.schema.json
Common Initiator completion layer may own completion_record.schema.json if shared
```

Schema validation failures:

```text
status = INVALID
failure_class = INVALID_SCHEMA
invalid config must not be treated as valid
completion status cannot be VALIDATED
```

If schema files are missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

No schema validation failure may be downgraded to a warning in Milestone 1.

---

# 24. Schema Validation Execution Order

Schema validation must execute in this order:

```text
1. Load config file if present.
2. If missing, build default ConfigRecord.
3. Validate ConfigRecord.
4. Build RuntimePaths.
5. Validate RuntimePaths.
6. Build PathRegistry.
7. Validate PathRegistry.
8. Validate path boundaries.
9. Build ConfigValidationReport.
10. Validate ConfigValidationReport.
11. Write path_registry.json only after validation passes.
12. Write config_validation_report_latest.json only after validation passes.
13. Append audit event when Audit Log is available.
```

If validation fails before step 11:

```text
path_registry.json must not be overwritten with invalid output.
```

---

# 25. Schema-to-Test Traceability

Required schema tests:

```text
test_config_schema_accepts_valid_config
test_config_schema_rejects_missing_required_fields
test_path_registry_schema_accepts_valid_registry
test_runtime_paths_schema_accepts_valid_runtime_paths
test_config_validation_report_schema_accepts_valid_report
test_completion_record_schema_accepts_valid_completion_record
```

Schema tests must pass before the component is marked VALIDATED.

---

# 26. Path Normalization Rules

All managed paths must be normalized before use.

Rules:

```text
resolve relative paths against repository root
normalize dot segments
reject path traversal attempts
reject paths that escape required boundary
preserve canonical path form in registry
```

Unsafe path examples:

```text
../outside
.agentx-init/../../outside
absolute path outside repository when boundary requires local path
symlink escape if detectable
```

Unsafe paths must be rejected.

---

# 27. Path Boundary Rules

Runtime write paths must stay inside:

```text
.agentx-init/
```

Package-local read paths may point to:

```text
agentx_initiator/schemas/
agentx_initiator/core/
agentx_initiator/tests/
agentx_initiator/templates/
```

Config / Paths must not write to package-local source paths in Milestone 1.

---

# 28. Default Config Rules

If config is missing:

```text
safe defaults must be used
status = PARTIAL
warning = DEFAULT_CONFIG_USED
```

Defaults must include all required managed paths.

Defaults must never authorize:

```text
remote configuration
network access
source mutation
arbitrary command execution
```

---

# 29. Environment Variable Rules

Milestone 1 environment behavior:

```text
environment variables may be read only if explicitly allowlisted
environment variables must not be logged raw
environment variables must not override path boundaries
environment variables must not enable network access
environment variables must not enable source mutation
```

If an environment override is unsafe:

```text
status = BLOCKED
failure_class = UNSAFE_ENVIRONMENT_OVERRIDE
```

---

# 30. Artifact Write Rules

Allowed writes:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/memory/audit_events.jsonl
```

Forbidden writes:

```text
L0/
L1/
L2/
agentx_initiator/core/
agentx_initiator/schemas/
agentx_initiator/tests/
source files outside .agentx-init/
```

---

# 31. Audit Integration Rules

When Audit Log is available, Config / Paths must emit audit events for:

```text
config loaded
default config used
config validation passed
config validation failed
path registry built
path boundary violation
config artifact write failed
```

Audit failure must not silently hide config validation failure.

---

# 32. Determinism Contract

The same config input and repository root must produce:

```text
same resolved paths
same path registry
same runtime paths
same validation status
same validation errors and warnings
```

Timestamps and generated ids may differ.

---

# 33. Status Semantics

Allowed statuses:

```text
VALID
PARTIAL
BLOCKED
INVALID
FAILED
```

Meaning:

```text
VALID   = config and paths validated successfully
PARTIAL = safe defaults or optional data used
BLOCKED = required schema/path boundary unavailable
INVALID = config or path input is invalid
FAILED  = validation or artifact writing failed unexpectedly
```

---

# 34. Failure Classes

Allowed failure classes:

```text
INVALID_CONFIG
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
MISSING_REQUIRED_PATH
UNSAFE_PATH
PATH_TRAVERSAL
PATH_OUTSIDE_BOUNDARY
UNSAFE_ENVIRONMENT_OVERRIDE
DIRECTORY_CREATE_FAILED
ARTIFACT_WRITE_FAILED
AUDIT_WRITE_FAILED
UNKNOWN_CONFIG_PATHS_ERROR
```

All failures must be represented in output or audit trail when possible.

---

# 35. Preconditions

Before returning managed paths:

- config must be loaded or defaults must be built
- config schema must validate
- runtime paths must validate
- path registry must validate
- requested path id must exist
- boundary rules must pass

If preconditions fail, path must not be returned as valid.

---

# 36. Postconditions

After successful validation:

- ConfigRecord exists
- RuntimePaths exists
- PathRegistry exists
- config_validation_report_latest.json exists
- all runtime paths are normalized
- all write paths stay within approved boundaries
- no source files are changed
- audit event is appended when Audit Log is available

---

# 37. Invariants

```yaml
invariants:
  - id: "CP-INV-001"
    statement: "Config / Paths is the single source of truth for managed paths."
  - id: "CP-INV-002"
    statement: "Runtime write paths stay inside .agentx-init/."
  - id: "CP-INV-003"
    statement: "Path traversal is rejected."
  - id: "CP-INV-004"
    statement: "Config is schema-valid before use."
  - id: "CP-INV-005"
    statement: "Defaults never authorize unsafe behavior."
  - id: "CP-INV-006"
    statement: "Config / Paths never mutates source files."
  - id: "CP-INV-007"
    statement: "Config / Paths never executes commands."
```

---

# 38. Security Contract

Security requirements:

- no network access
- no shell command execution
- no dependency installation
- no source mutation
- no remote config loading
- no unsafe path traversal
- no environment variable logging
- no intentional secret logging
- no path outside approved boundary for runtime writes

---

# 39. Side Effects

Side-effect classification:

```yaml
side_effect_class: "configuration_persistent_state"
allowed_writes:
  - ".agentx-init/config/config.json"
  - ".agentx-init/config/path_registry.json"
  - ".agentx-init/snapshots/config_validation_report_latest.json"
  - ".agentx-init/memory/audit_events.jsonl"
forbidden_writes:
  - "L0/"
  - "L1/"
  - "L2/"
  - "source files outside .agentx-init/"
```

Config / Paths must not mutate governed source files.

---

# 40. SIB Bindings

Consumed by:

```text
Repository Scanner
Architecture Analyzer
Governance Engine
Risk Engine
Evolution Planner
Patch Proposal Generator
Validation Runner
Audit Log
Memory Store
Knowledge Graph
Report Writer
CLI Commands
```

Produces:

```text
ConfigRecord
PathRegistry
RuntimePaths
ConfigValidationReport
```

---

# 41. SIB Registry Entry

```yaml
art_id: "AGENTX::CONFIG_PATHS"
title: "Config / Paths"
type: "production-impl"
language: "python"
layer: 1
file_path: "agentx_initiator/core/config.py"
current_version: "v3.0.0"
status: "active"
canonicalization_tier: "T1"
spec_bindings:
  - doc: "AGENTX::FIC-AGENTX-INITIATOR-CONFIG-PATHS-001"
    binding_type: "GOVERNS"
    binding_strength: "HARD"
```

---

# 42. Test Contract

Required unit tests:

```text
test_load_config_from_file
test_missing_config_uses_safe_defaults
test_validate_config_success
test_invalid_config_rejected
test_resolve_managed_path
test_unknown_path_id_rejected
test_path_traversal_rejected
test_runtime_write_path_outside_agentx_init_rejected
test_path_registry_schema_validates
test_runtime_paths_schema_validates
test_config_validation_report_schema_validates
test_ensure_runtime_dirs_creates_allowed_dirs
test_ensure_runtime_dirs_rejects_source_dirs
```

Required negative tests:

```text
test_absolute_path_outside_boundary_rejected
test_environment_override_cannot_escape_boundary
test_source_path_write_rejected
test_remote_config_rejected
test_command_execution_not_available
```

Required integration tests:

```text
test_repository_scanner_uses_config_paths
test_report_writer_uses_config_paths
test_validation_runner_uses_config_paths
test_cli_uses_config_paths
```

---

# 43. Test Oracle Strength

Minimum oracle levels:

```yaml
path_boundary_enforcement: "O4 invariant"
path_traversal_rejection: "O4 invariant"
schema_validation: "O3 negative"
safe_defaults: "O3 negative"
source_non_mutation: "O4 invariant"
command_non_execution: "O4 invariant"
```

Smoke tests alone are not sufficient.

---

# 44. Acceptance Criteria

Config / Paths is accepted only if:

- config loads from file
- missing config produces safe defaults
- invalid config is rejected
- managed paths resolve deterministically
- path traversal is rejected
- runtime write paths stay inside `.agentx-init/`
- path registry validates
- runtime paths validate
- validation report validates
- required runtime directories can be created safely
- source package paths are not written
- audit event is emitted when available
- all required tests pass
- no forbidden imports or remote config behavior are present

---

# 45. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] target files are listed
[ ] public surface is defined
[ ] config schema is defined
[ ] path registry schema is defined
[ ] runtime paths schema is defined
[ ] validation report schema is defined
[ ] core managed paths are defined
[ ] path normalization rules are defined
[ ] path boundary rules are defined
[ ] default config rules are defined
[ ] environment variable rules are defined
[ ] artifact write rules are defined
[ ] test obligations are defined
[ ] acceptance criteria are binary
```

---

# 46. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] public surface matches FIC
[ ] no extra public symbols are introduced without justification
[ ] no forbidden dependencies are used
[ ] config schema validates
[ ] path registry schema validates
[ ] runtime paths schema validates
[ ] path traversal is rejected
[ ] runtime write paths stay inside .agentx-init/
[ ] safe defaults exist
[ ] source paths are not mutated
[ ] unit tests pass
[ ] integration tests pass
[ ] completion record exists
```

---

# 47. Minimal Implementation Package

Milestone 1 implementation package must include:

```text
TASK_CONTRACT.md
CONFIG_PATHS_FIC_EQC_CONFIG_SCHEMA_CONTRACT_v3.md
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
completion_record.schema.json
implementation_handoff.yaml
completion_record.yaml
```

No coding agent should implement Config / Paths from this document alone without the implementation package.

---

# 48. Implementation Handoff Envelope

```yaml
implementation_handoff:
  fic_id: "FIC-AGENTX-INITIATOR-CONFIG-PATHS-001"
  eqc_id: "EQC-AGENTX-INITIATOR-CONFIG-PATHS-001"
  target_component: "Config / Paths"
  permitted_files:
    - "agentx_initiator/core/config.py"
    - "agentx_initiator/core/path_registry.py"
    - "agentx_initiator/core/config_model.py"
    - "agentx_initiator/schemas/config.schema.json"
    - "agentx_initiator/schemas/path_registry.schema.json"
    - "agentx_initiator/schemas/runtime_paths.schema.json"
    - "agentx_initiator/schemas/config_validation_report.schema.json"
    - "agentx_initiator/tests/test_config.py"
    - "agentx_initiator/tests/test_path_registry.py"
    - "agentx_initiator/tests/test_config_schema.py"
  forbidden_changes:
    - "L0/"
    - "L1/"
    - "L2/"
    - "source files unrelated to config/paths"
  allowed_statuses:
    - "IMPLEMENTED_UNVALIDATED"
    - "VALIDATED"
    - "NO_CHANGE"
    - "BLOCKED"
  stop_conditions:
    - "path boundary enforcement cannot be implemented"
    - "schema validation cannot be enforced"
    - "Config / Paths requires command execution"
    - "Config / Paths requires remote configuration"
    - "Config / Paths requires source mutation"
```

---

# 49. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  fic_id: "FIC-AGENTX-INITIATOR-CONFIG-PATHS-001"
  eqc_id: "EQC-AGENTX-INITIATOR-CONFIG-PATHS-001"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|NO_CHANGE|BLOCKED"
  files_created_or_changed: []
  tests_created_or_changed: []
  schemas_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  deviations_from_fic_eqc_config_schema: []
  unresolved_risks: []
```

The implementation must not be considered complete without evidence.

---

# 50. Residual Risks

Known residual risks:

```yaml
residual_risks:
  - id: "CP-RISK-001"
    description: "Path handling is high-risk because unsafe normalization can allow boundary escape."
    severity: "high"
    mitigation: "Use strict normalization and path traversal tests."
  - id: "CP-RISK-002"
    description: "Defaults can accidentally authorize unsafe behavior."
    severity: "medium"
    mitigation: "Defaults must be safe and conservative."
  - id: "CP-RISK-003"
    description: "Different operating systems may resolve paths differently."
    severity: "medium"
    mitigation: "Use pathlib and deterministic tests for relative/boundary behavior."
```

---

# 51. Definition of Done

Config / Paths Milestone 1 is done when it can:

- load config
- provide safe defaults
- validate config schema
- validate path registry schema
- validate runtime paths schema
- resolve managed paths
- reject unsafe paths
- reject path traversal
- enforce `.agentx-init/` runtime write boundary
- create required runtime directories safely
- write path_registry.json
- write config_validation_report_latest.json
- emit audit event when available
- pass required tests
- avoid source mutation
- avoid command execution
- avoid remote configuration

---

# 52. Freeze Rule

This document is now the controlling Config / Paths FIC+EQC+Config Schema Contract document for Milestone 1.

Do not keep expanding this document unless a true implementation-blocking gap is discovered.

Next artifacts should be:

```text
TASK_CONTRACT.md
IMPLEMENTATION_HANDOFF.yaml
config.schema.json
path_registry.schema.json
runtime_paths.schema.json
config_validation_report.schema.json
completion_record.schema.json
```

---

# 53. Final Success Definition

Config / Paths v1 implementation is successful when it provides a deterministic, schema-valid, governed configuration and path management layer that serves as the single source of truth for Initiator runtime configuration and filesystem locations while enforcing safe path boundaries and avoiding source mutation.

---

# 54. Final Rating

This FIC+EQC+Config Schema Contract document is rated **10/10** for the initial Config / Paths component.

It is ready to be used as the controlling document for the Config / Paths Milestone 1 implementation package.
