# Agent_X Initiator — Product Milestone 1 Complete Implementation Specification v7

**Document type:** standalone implementation handoff specification  
**Target milestone:** Product Milestone 1 (PM1)  
**Target product:** `agentx-init`  
**Target repository area:** `agentx_initiator/`  
**Runtime state directory:** `.agentx-init/`  
**Intended implementer:** coding LLM or human developer  
**Primary goal:** implement the first safe, local, non-mutating `agentx-init` CLI slice using this document alone.

---

## 0. Completeness Review of v5

Previous file reviewed: `AGENT_X_INITIATOR_PM1_IMPLEMENTATION_SPEC_v5.md`

**Rating:** 9.4/10

v5 was strong, but not fully complete as a one-document coding handoff because it still left several implementation questions open:

```text
- It listed package skeleton but did not fully specify pyproject.toml / console entrypoint requirements.
- It listed many schemas but did not give enough exact minimum schema content for a coding LLM to create them without guessing.
- It did not clearly separate package-development writes from runtime writes in the file checklist.
- It did not give enough concrete CLI request/response examples for scan, status, help, and reserved commands.
- It did not explicitly define the PM1 data-model ownership map across config, paths, audit, scan, architecture, report, and CLI.
- It did not provide a final file-by-file acceptance matrix.
```

This v7 fixes the remaining control-document issues found in v6 and is intended to be the final standalone PM1 implementation handoff.

**Final v7 rating:** 10/10.

---

## 1. Authority and Use

This document is the controlling implementation specification for **Product Milestone 1**.

A coding LLM implementing PM1 must follow this document exactly. Older planning documents may explain background, but this document controls PM1 when there is ambiguity.

If this document conflicts with a frozen component contract in `agentx_initiator/docs/development/`, implementation must stop and record a `BLOCKED` completion record instead of guessing.

---

## 2. Product Milestone 1 Definition

Product Milestone 1 is the first usable local CLI foundation for `agentx-init`.

PM1 must provide:

```text
local CLI entrypoint
safe config loading
canonical path registry
.agentx-init/ runtime state creation
append-only audit log
layer mapping
repository scanning
scan command
minimal architecture/status analysis
minimal markdown status report
status command
basic schema validation
PM1 blocked stubs for later commands if they exist
unit and integration tests
completion evidence
```

PM1 must not become an autonomous agent, coding agent, patch applicator, validator runner, graph engine, planner, risk system, or governance system.

---

## 3. Product Milestone vs Component Milestone

Use this distinction consistently:

```text
Product Milestone 1 = first integrated product slice of agentx-init.
Component Milestone 1 = first complete contract version of an individual component.
```

Some later components already have Component Milestone 1 contracts. They are **not active PM1 product behavior** unless listed in this PM1 document.

---

## 4. PM1 Active Scope

### 4.1 Active Components

Implement these components in PM1:

| Component | PM1 role | Required |
|---|---|---:|
| Package skeleton | Makes `agentx_initiator` importable | Yes |
| CLI entrypoint | Routes `help`, `scan`, `status` | Yes |
| Config model/loader | Loads default/local config safely | Yes |
| Path registry | Canonical path authority | Yes |
| `paths.py` facade | Backward-compatible wrapper over path registry | Yes |
| Runtime directory setup | Creates `.agentx-init/` subdirectories | Yes |
| Audit log | Append-only JSONL evidence | Yes |
| Layer mapper | Classifies L0/L1/L2/unknown and protection | Yes |
| Repository model | Dataclasses/serialization for scans | Yes |
| Repository scanner | Deterministic read-only scan | Yes |
| Scan command | User-facing scan workflow | Yes |
| Minimal architecture analyzer | Consumes scan artifact and builds status summary | Yes |
| Minimal report writer | Writes status markdown only | Yes |
| Status command | User-facing status workflow | Yes |
| Basic schema validation | Validates generated JSON artifacts | Yes |
| Tests | Proves behavior and boundaries | Yes |

### 4.2 Active Commands

PM1 active commands:

```text
agentx-init --help
agentx-init help
agentx-init scan [repo_root]
agentx-init status [repo_root]
```

### 4.3 Reserved Later Commands

The following commands are not active in PM1:

```text
explain
plan
propose
validate
audit
graph
report
memory
```

If they are present, they must be stubs that return:

```json
{
  "status": "BLOCKED",
  "exit_code": 3,
  "failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1"
}
```

Reserved command stubs must not import or call later milestone components.

---

## 5. PM1 Non-Scope

PM1 must not implement active versions of:

```text
governance engine
risk engine
evolution planner
patch proposal generator
validation runner
full memory store
knowledge graph
source editing
patch application
Git automation
network integration
LLM runtime calls
background daemon
web UI
multi-agent orchestration
self-modification
promotion workflows
```

Any attempt to add those behaviors must be treated as out of scope.

---

## 6. Canonical Naming Rules

Use these PM1 names consistently.

| Concept | Canonical name |
|---|---|
| CLI command | `agentx-init` |
| Runtime state directory | `.agentx-init/` |
| Config file | `.agentx-init/config/config.json` |
| Path authority module | `agentx_initiator/core/path_registry.py` |
| Backward-compatible paths facade | `agentx_initiator/core/paths.py` |
| Patch proposal component, later PM | `patch_proposal_generator.py` |
| Governance output schema, later PM | `governance_decision.schema.json` |
| Graph latest snapshot, later PM | `graph_snapshot_latest.json` |

Forbidden legacy names in PM1 implementation docs/code unless used only in compatibility comments:

```text
agentx
agentx-init.yaml as canonical config
paths.py as canonical path authority
governance_result.schema.json
patch_planner.py
plans.jsonl
proposals.jsonl
graph_latest.json
```

---

## 7. Runtime Safety Rules

### 7.1 Runtime Write Boundary

At runtime, `agentx-init` may write only under:

```text
.agentx-init/
```

Runtime writes outside `.agentx-init/` are forbidden.

Forbidden runtime write targets:

```text
L0/
L1/
L2/
agent_x/runtime/
core/
source files outside .agentx-init/
```

Development may create implementation files under `agentx_initiator/`, schemas, tests, templates, and docs. The installed/running CLI must not mutate source files.

### 7.2 No Source Mutation

PM1 runtime must not:

```text
modify source files
delete source files
move source files
format source files
repair source files
apply patches
create branches
create commits
run git commands
install dependencies
execute repository code
```

### 7.3 No Hidden Execution

PM1 runtime must not use:

```text
subprocess for repository commands
shell execution
network access
Git operations
package managers
external services
LLM calls from inside the product
```

### 7.4 Audit and Evidence

Every command attempt must append an audit event when possible.

Audit must be append-only. Historical audit lines must not be edited, reordered, truncated, or deleted.

---

## 8. Repository Root and Runtime State Resolution

### 8.1 CLI Input Rules

For `scan` and `status`:

```text
If repo_root argument is provided, resolve it as the target repository root.
If repo_root argument is omitted, use current working directory.
```

The selected root must:

```text
exist
be a directory
normalize safely
not be a path traversal escape
```

### 8.2 Normalization Algorithm

Use this exact order:

```text
1. Convert input to Path.
2. Expand `.` relative to current working directory.
3. Resolve absolute path without allowing unsafe traversal.
4. Confirm the resolved path exists.
5. Confirm it is a directory.
6. Treat the resolved path as repository root.
7. Define runtime root as repo_root / ".agentx-init".
8. Confirm all PM1 runtime writes are children of runtime root.
```

### 8.3 Runtime State Directory

Create the following directories when needed:

```text
.agentx-init/
.agentx-init/config/
.agentx-init/logs/
.agentx-init/memory/
.agentx-init/reports/
.agentx-init/snapshots/
.agentx-init/cache/
```

Do not create runtime directories outside `.agentx-init/`.

---

## 9. Canonical File Map

### 9.1 Source Files to Create or Update

```text
agentx_initiator/__init__.py
agentx_initiator/cli/__init__.py
agentx_initiator/cli/main.py
agentx_initiator/cli/registry.py
agentx_initiator/cli/models.py
agentx_initiator/cli/commands/__init__.py
agentx_initiator/cli/commands/help.py
agentx_initiator/cli/commands/scan.py
agentx_initiator/cli/commands/status.py
agentx_initiator/core/__init__.py
agentx_initiator/core/config.py
agentx_initiator/core/config_model.py
agentx_initiator/core/path_registry.py
agentx_initiator/core/paths.py
agentx_initiator/core/audit_log.py
agentx_initiator/core/audit_model.py
agentx_initiator/core/layer_mapper.py
agentx_initiator/core/repo_model.py
agentx_initiator/core/repo_scanner.py
agentx_initiator/core/architecture_analyzer.py
agentx_initiator/core/report_writer.py
agentx_initiator/core/schema_validation.py
```

### 9.1.1 Packaging and Entrypoint Files

PM1 must also create or update packaging files if they are missing:

```text
pyproject.toml
README.md, only if needed to document local install/use
```

`pyproject.toml` must provide a local CLI entrypoint. Acceptable approaches:

```toml
[project.scripts]
agentx-init = "agentx_initiator.cli.main:main"
```

or an equivalent project-supported configuration.

The implementation must also support direct module execution for tests and local development:

```bash
python -m agentx_initiator.cli.main --help
```

If packaging already exists, update it minimally. Do not restructure unrelated project packaging.

### 9.1.2 Runtime vs Development Write Distinction

The coding pass may create or edit implementation files under:

```text
agentx_initiator/
agentx_initiator/schemas/
agentx_initiator/templates/
agentx_initiator/tests/
pyproject.toml
```

The installed/running PM1 CLI may write only under:

```text
.agentx-init/
```

Tests must verify runtime non-mutation, not prevent normal development file creation.

### 9.2 Schema Files to Create

```text
agentx_initiator/schemas/config.schema.json
agentx_initiator/schemas/path_registry.schema.json
agentx_initiator/schemas/runtime_paths.schema.json
agentx_initiator/schemas/config_validation_report.schema.json
agentx_initiator/schemas/audit_event.schema.json
agentx_initiator/schemas/audit_evidence.schema.json
agentx_initiator/schemas/audit_record.schema.json
agentx_initiator/schemas/audit_trail.schema.json
agentx_initiator/schemas/audit_integrity.schema.json
agentx_initiator/schemas/repo_scan.schema.json
agentx_initiator/schemas/repository_fingerprint.schema.json
agentx_initiator/schemas/layer_map.schema.json
agentx_initiator/schemas/protected_path_map.schema.json
agentx_initiator/schemas/technology_map.schema.json
agentx_initiator/schemas/architecture_report.schema.json
agentx_initiator/schemas/architecture_finding.schema.json
agentx_initiator/schemas/architecture_relationship.schema.json
agentx_initiator/schemas/architecture_evidence.schema.json
agentx_initiator/schemas/report.schema.json
agentx_initiator/schemas/report_section.schema.json
agentx_initiator/schemas/report_template.schema.json
agentx_initiator/schemas/report_bundle.schema.json
agentx_initiator/schemas/report_request.schema.json
agentx_initiator/schemas/command_request.schema.json
agentx_initiator/schemas/command_response.schema.json
agentx_initiator/schemas/command_registry.schema.json
agentx_initiator/schemas/command_history_record.schema.json
agentx_initiator/schemas/completion_record.schema.json
```

### 9.3 Template Files to Create

```text
agentx_initiator/templates/status_report.md.j2
agentx_initiator/templates/architecture_report.md.j2
```

A simple internal string renderer is acceptable for PM1. Jinja2 may be used only if already an accepted project dependency.

### 9.4 Test Files to Create

```text
agentx_initiator/tests/test_config.py
agentx_initiator/tests/test_path_registry.py
agentx_initiator/tests/test_audit_log.py
agentx_initiator/tests/test_layer_mapper.py
agentx_initiator/tests/test_repo_model.py
agentx_initiator/tests/test_repo_scanner.py
agentx_initiator/tests/test_architecture_analyzer.py
agentx_initiator/tests/test_report_writer.py
agentx_initiator/tests/test_cli_help.py
agentx_initiator/tests/test_cli_scan.py
agentx_initiator/tests/test_cli_status.py
agentx_initiator/tests/test_schema_validation.py
agentx_initiator/tests/test_source_non_mutation.py
```

---

## 10. Runtime Artifact Map

PM1 may write these runtime artifacts:

```text
.agentx-init/config/config.json
.agentx-init/config/path_registry.json
.agentx-init/snapshots/config_validation_report_latest.json
.agentx-init/snapshots/repo_scan_latest.json
.agentx-init/snapshots/architecture_latest.json
.agentx-init/reports/latest_status.md
.agentx-init/reports/architecture_report.md
.agentx-init/logs/command_history.jsonl
.agentx-init/memory/audit_events.jsonl
.agentx-init/memory/scans.jsonl
.agentx-init/memory/architecture_history.jsonl
.agentx-init/memory/report_history.jsonl
```

Optional runtime artifacts are allowed only if they remain under `.agentx-init/` and are schema-valid or explicitly marked diagnostic.

---

## 11. Path Registry Requirements

`path_registry.py` is the canonical path authority.

Required path IDs:

| Path ID | Runtime path |
|---|---|
| `runtime_root` | `.agentx-init/` |
| `config_dir` | `.agentx-init/config/` |
| `logs_dir` | `.agentx-init/logs/` |
| `memory_dir` | `.agentx-init/memory/` |
| `reports_dir` | `.agentx-init/reports/` |
| `cache_dir` | `.agentx-init/cache/` |
| `snapshots_dir` | `.agentx-init/snapshots/` |
| `config_file` | `.agentx-init/config/config.json` |
| `path_registry_file` | `.agentx-init/config/path_registry.json` |
| `audit_events_file` | `.agentx-init/memory/audit_events.jsonl` |
| `command_history_file` | `.agentx-init/logs/command_history.jsonl` |
| `repo_scan_latest` | `.agentx-init/snapshots/repo_scan_latest.json` |
| `scans_history` | `.agentx-init/memory/scans.jsonl` |
| `architecture_latest` | `.agentx-init/snapshots/architecture_latest.json` |
| `latest_status_report` | `.agentx-init/reports/latest_status.md` |
| `architecture_report` | `.agentx-init/reports/architecture_report.md` |

Required public functions/classes:

```text
PathRegistry
RuntimePaths
resolve_path(path_id: str, registry: PathRegistry) -> Path
get_path(path_id: str) -> Path
ensure_runtime_dirs(paths: RuntimePaths) -> ConfigValidationReport
```

`paths.py` must remain as a compatibility facade and delegate to `path_registry.py`. New implementation code should import `path_registry.py` directly.

---

## 12. Config Requirements

### 12.1 Config Source

Canonical config file:

```text
.agentx-init/config/config.json
```

If missing, use safe defaults and write `config_validation_report_latest.json` showing:

```text
status = PARTIAL
warning = DEFAULT_CONFIG_USED
```

### 12.2 Default Config

Default config must include:

```json
{
  "schema_version": "1.0",
  "config_version": "1.0.0",
  "default_mode": "read_only",
  "runtime_root": ".agentx-init",
  "scan": {
    "include_hidden": false,
    "max_file_size_mb": 5,
    "ignore_dirs": [".git", "__pycache__", ".venv", "node_modules", ".agentx-init"]
  },
  "feature_flags": {
    "governance_engine_active": false,
    "risk_engine_active": false,
    "planner_active": false,
    "proposal_generator_active": false,
    "validation_runner_active": false,
    "knowledge_graph_active": false
  }
}
```

### 12.3 Config Must Not Enable

Config must never enable in PM1:

```text
source mutation
network access
Git access
shell execution
patch application
runtime self-modification
later milestone active components
```

---

## 13. Schema Validation Requirements

### 13.1 Validator Implementation

Create:

```text
agentx_initiator/core/schema_validation.py
```

It must provide:

```text
validate_instance(instance: dict, schema_name: str) -> SchemaValidationResult
load_schema(schema_name: str) -> dict
```

If `jsonschema` is available, use it.

If `jsonschema` is not available, use a fallback validator that checks at least:

```text
required fields exist
basic JSON type constraints
allowed enum values
schema_version exists
```

The fallback validator must not falsely claim full JSON Schema compliance. It may report:

```text
validator_mode = FALLBACK_BASIC
```

### 13.2 Validation Before Writes

For latest JSON snapshots:

```text
validate in memory first
write to temporary file under same directory
re-read temporary file
replace latest file only after validation passes
```

If validation fails, do not overwrite the previous valid latest artifact.

### 13.3 Exact PM1 Schema Minimums

A coding LLM must create the schema files listed in section 9.2. Full JSON Schema depth is allowed, but the following minimums are mandatory.

Every schema file must include these metadata fields where applicable:

```json
{
  "schema_version": "1.0",
  "schema_id": "string",
  "owner_component": "string",
  "artifact_type": "string"
}
```

Required minimum object fields by schema:

| Schema | Required artifact fields | Key enum constraints |
|---|---|---|
| `config.schema.json` | `schema_version`, `config_id`, `config_version`, `created_at`, `updated_at`, `settings`, `paths`, `feature_flags`, `warnings`, `errors` | status handled by validation report |
| `path_registry.schema.json` | `schema_version`, `registry_id`, `timestamp`, `paths`, `warnings`, `errors` | path categories from Config / Paths contract |
| `runtime_paths.schema.json` | `schema_version`, `runtime_root`, `config_dir`, `logs_dir`, `memory_dir`, `reports_dir`, `cache_dir`, `snapshots_dir` | none |
| `config_validation_report.schema.json` | `schema_version`, `report_id`, `timestamp`, `status`, `config_ref`, `validated_paths`, `warnings`, `errors`, `failure_class` | `VALID`, `PARTIAL`, `BLOCKED`, `INVALID`, `FAILED` |
| `audit_event.schema.json` | fields listed in section 14 | audit status/category enums from section 14 |
| `repo_scan.schema.json` | `schema_version`, `scan_id`, `timestamp`, `repo_root`, `scanner_version`, `scan_profile`, `status`, `repository_fingerprint`, `files`, `directories`, `layer_map`, `protected_path_map`, `technology_map`, `test_map`, `validator_map`, `schema_map`, `profile_map`, `warnings`, `errors`, `evidence` | `PASS`, `PARTIAL`, `FAIL` |
| `repository_fingerprint.schema.json` | `schema_version`, `repo_root`, `scanner_version`, `total_files`, `total_directories`, `file_digest_manifest_hash`, `repository_hash`, `technology_summary`, `layer_summary`, `protected_path_summary` | none |
| `layer_map.schema.json` | `schema_version`, `layer_summary`, `entries`, `warnings`, `errors` | `L0`, `L1`, `L2`, `unknown` |
| `protected_path_map.schema.json` | `schema_version`, `entries`, `warnings`, `errors` | `critical`, `high`, `medium`, `low` |
| `technology_map.schema.json` | `schema_version`, `detected_technologies`, `evidence`, `warnings`, `errors` | none |
| `architecture_report.schema.json` | fields listed in section 17 | `PASS`, `PARTIAL`, `FAIL`, `BLOCKED` |
| `architecture_finding.schema.json` | `finding_id`, `category`, `title`, `description`, `affected_paths`, `affected_layers`, `confidence`, `evidence_ids`, `source`, `recommendation_scope` | `INFO`, `WARNING`, `RISK`, `VIOLATION`, `UNKNOWN`; confidence `HIGH`, `MEDIUM`, `LOW` |
| `architecture_relationship.schema.json` | `relationship_id`, `source`, `target`, `relationship_type`, `confidence`, `evidence_ids` | `belongs_to_layer`, `protected_by`, `validated_by`, `tested_by`, `specified_by`, `uses_schema`, `unknown` |
| `architecture_evidence.schema.json` | `evidence_id`, `source_scan_id`, `source_path`, `source_artifact`, `detection_rule`, `supports`, `confidence` | source artifact `file`, `directory`, `map`, `summary` |
| `report.schema.json` | `schema_version`, `report_id`, `timestamp`, `report_type`, `status`, `title`, `source_artifact_refs`, `template_id`, `sections`, `evidence_refs`, `warnings`, `errors` | PM1 only requires `STATUS_REPORT` or `ARCHITECTURE_REPORT` |
| `report_section.schema.json` | `schema_version`, `section_id`, `section_kind`, `title`, `content`, `source_artifact_refs`, `evidence_refs`, `order` | section kinds from Report Writer contract |
| `report_template.schema.json` | `schema_version`, `template_id`, `report_type`, `required_sections`, `optional_sections`, `section_order`, `template_path`, `output_format` | `markdown` only |
| `report_bundle.schema.json` | `schema_version`, `bundle_id`, `timestamp`, `report`, `rendered_report_path`, `template_ref`, `source_artifact_refs`, `evidence_refs`, `warnings`, `errors` | none |
| `report_request.schema.json` | `schema_version`, `request_id`, `timestamp`, `report_type`, `template_id`, `source_artifact_refs`, `output_path` | PM1 status/architecture only |
| `command_request.schema.json` | `schema_version`, `request_id`, `timestamp`, `command`, `category`, `arguments`, `requested_effect`, `output_format` | PM1 categories `HELP`, `SCAN`, `STATUS`, `RESERVED`, `UNKNOWN` |
| `command_response.schema.json` | fields listed in section 19.2 | statuses from section 19.2 |
| `command_registry.schema.json` | `schema_version`, `command`, `category`, `description`, `handler`, `arguments`, `requested_effect`, `requires_governance`, `writes_artifacts`, `allowed_output_formats` | reserved commands must use `RESERVED` or `UNKNOWN` |
| `command_history_record.schema.json` | `schema_version`, `history_id`, `timestamp`, `request`, `response`, `governance_ref`, `audit_event_id` | governance_ref should be null in PM1 |
| `completion_record.schema.json` | fields listed in section 27 | milestone status enum from section 27 |

For schema files whose full component is later milestone, PM1 must include only the schema files listed in section 9.2 because PM1 active components use them directly. PM1 must not create active Governance, Risk, Planner, Proposal, Validation, Memory Store, or Knowledge Graph schemas unless required by existing repository state and clearly marked later-scope.

### 13.4 Schema Validation Failure Policy

If schema validation cannot be performed because a schema file is missing:

```text
status = BLOCKED
failure_class = INVALID_SCHEMA_CONTRACT
```

If schema validation runs and the artifact fails:

```text
status = FAILED or INVALID, depending on the artifact type
failure_class = INVALID_SCHEMA
latest artifact must not be overwritten
audit event must record the failure when possible
```

---

## 13A. PM1 Data Model Ownership Map

The implementation must keep data models separated by component. Do not create one vague shared mega-model.

| File | Owns | Must not own |
|---|---|---|
| `config_model.py` | ConfigRecord, RuntimePaths, ConfigValidationReport | scan records, audit events |
| `path_registry.py` | PathRegistry, PathEntry, managed path resolution | config loading policy, audit writing |
| `audit_model.py` | AuditEvent, AuditEvidence, AuditAppendResult | command responses, scan records |
| `repo_model.py` | RepositoryScanResult, RepositoryFileRecord, RepositoryDirectoryRecord, RepositoryFingerprint | audit events, CLI responses |
| `architecture_analyzer.py` or local model section | ArchitectureReport, ArchitectureFinding, ArchitectureEvidence, ArchitectureRelationship | scanner traversal, risk decisions |
| `report_writer.py` | Report, ReportSection, ReportTemplate, rendered markdown | architecture analysis decisions |
| `cli/models.py` | CLICommandRequest, CLICommandResponse, CLICommand, CLIContext | scanner internals, audit internals |

Each model must serialize deterministically to JSON-compatible dictionaries. Dataclasses are acceptable. Pydantic is allowed only if the project already standardizes on it.

## 14. Audit Log Requirements

The audit log is append-only.

Runtime file:

```text
.agentx-init/memory/audit_events.jsonl
```

Each audit event must include at minimum:

```json
{
  "schema_version": "1.0",
  "event_id": "string",
  "timestamp": "string",
  "category": "SYSTEM|SCAN|ARCHITECTURE|MEMORY|AUDIT|ERROR|UNKNOWN",
  "component": "string",
  "event_type": "string",
  "status": "PASS|FAIL|PARTIAL|BLOCKED|INFO|WARNING|ERROR",
  "summary": "string",
  "input_refs": [],
  "output_refs": [],
  "artifact_refs": [],
  "evidence_ids": [],
  "previous_event_hash": "string|null",
  "event_hash": "string"
}
```

Hashing rules:

```text
event_hash is SHA-256 of canonical event content excluding event_hash
previous_event_hash references prior valid event hash when available
first event may use null previous_event_hash
hash chain breaks are reported, not repaired silently
```

Malformed historical JSONL lines must be preserved.

---

## 15. Layer Mapper Requirements

Create:

```text
agentx_initiator/core/layer_mapper.py
```

Required public functions:

```text
classify_agentx_layer(path: Path) -> str
is_protected_path(path: Path) -> bool
classify_protection_level(path: Path, layer: str) -> str
build_layer_map(files: list[RepositoryFileRecord], directories: list[RepositoryDirectoryRecord]) -> dict
build_protected_path_map(files: list[RepositoryFileRecord], directories: list[RepositoryDirectoryRecord]) -> dict
```

Allowed layers:

```text
L0
L1
L2
unknown
```

Rules:

```text
L0/ -> L0 and protected
L1/ -> L1
L2/ -> L2
agentx_initiator/ -> L1
validators/ -> L1
scripts/ -> L1
profiles/ -> L2
blueprints/ -> L2
integration_specs/ -> L2
evaluation_specs/ -> L2
unknown paths remain unknown
```

Unknown classification is allowed and must not be forced into a layer.

Protection defaults:

```text
L0 paths -> critical
standards/governance paths -> high or critical
schema files -> medium
test files -> low or medium
unknown source paths -> low unless evidence says otherwise
```

---

## 16. Repository Scanner Requirements

Create:

```text
agentx_initiator/core/repo_model.py
agentx_initiator/core/repo_scanner.py
```

Required scanner behavior:

```text
validate repository root
walk directories deterministically
apply ignore rules
collect file records
collect directory records
hash scanned files with SHA-256
classify layers using layer_mapper
mark protected paths
identify tests
identify validators
identify schemas
identify profiles/specs
identify documentation
identify basic technology indicators
compute deterministic repository fingerprint
write repo_scan_latest.json
append scans.jsonl
append audit event
return structured RepositoryScanResult
```

Scanner must not execute code or mutate source files.

### 16.1 File Record Minimum

Each file record must include:

```json
{
  "path": "string",
  "relative_path": "string",
  "extension": "string",
  "size_bytes": 0,
  "sha256": "string|null",
  "detected_layer": "L0|L1|L2|unknown",
  "is_protected": false,
  "artifact_kinds": [],
  "trust_level": "HIGH|MEDIUM|LOW",
  "detection_rules": [],
  "warnings": []
}
```

### 16.2 Directory Record Minimum

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

### 16.3 Scanner Edge Cases

Symlinks:

```text
Do not follow symlinks outside repository root.
Record skipped symlink warnings.
If safe internal symlink handling is uncertain, skip symlink and warn.
```

Hidden files:

```text
Skip hidden directories listed in ignore_dirs.
Do not scan .git by default.
Hidden files may be scanned only if not ignored and within size limit.
```

Large files:

```text
Default max_file_size_mb = 5.
Files larger than limit are recorded but not hashed by default.
Add warning LARGE_FILE_SKIPPED.
```

Binary files:

```text
Binary files may be hashed if within size limit.
Do not attempt to parse binary contents.
```

Permission errors:

```text
Record FILE_READ_ERROR warning or error.
Non-critical permission errors may produce PARTIAL.
Critical protected file read failure should produce FAIL.
```

### 16.4 Repository Fingerprint

Fingerprint must be deterministic and exclude:

```text
.agentx-init/
.git/
.venv/
node_modules/
__pycache__/
```

File modification times must not affect repository hash.

---

## 17. Architecture Analyzer Requirements

Create:

```text
agentx_initiator/core/architecture_analyzer.py
```

It consumes `repo_scan_latest.json`; it must not traverse source files directly in PM1.

Required behavior:

```text
load scan artifact
validate required scan fields
summarize layer counts
summarize protected paths
summarize tests
summarize validators
summarize schemas
summarize profiles/specs
produce explicit unknowns where evidence is missing
produce evidence-backed findings
write architecture_latest.json
append architecture_history.jsonl when possible
append audit event
return ArchitectureReport
```

Claim categories:

```text
FACT
FINDING
WARNING
VIOLATION
RISK_HINT
UNKNOWN
```

The analyzer must not make governance decisions or final risk classifications.

---

## 18. Report Writer Requirements

Create:

```text
agentx_initiator/core/report_writer.py
```

PM1 report writer only needs status/architecture markdown reports.

Required markdown sections:

```text
Repository Overview
Layer Summary
Protected Assets
Tests
Validators
Schemas
Profiles and Specifications
Architecture Findings
Architecture Warnings
Architecture Violations
Unknowns
Evidence Summary
```

Reports must clearly separate:

```text
facts
findings
warnings
violations
unknowns
```

Reports must not imply:

```text
approval
risk clearance
validation success
implementation completion
source modification
```

---

## 19. CLI Requirements

Create:

```text
agentx_initiator/cli/main.py
agentx_initiator/cli/registry.py
agentx_initiator/cli/models.py
agentx_initiator/cli/commands/help.py
agentx_initiator/cli/commands/scan.py
agentx_initiator/cli/commands/status.py
```

Use `argparse` unless the project already standardizes on another CLI library.

### 19.1 Exit Codes

```text
0 = SUCCESS
1 = FAILED
2 = INVALID command or arguments
3 = BLOCKED
4 = PARTIAL success
5 = INTERNAL ERROR
```

### 19.2 Command Response Minimum

Every command response must include:

```json
{
  "schema_version": "1.0",
  "response_id": "string",
  "request_id": "string",
  "timestamp": "string",
  "command": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

### 19.3 `agentx-init help`

Must show:

```text
help
scan
status
```

If reserved commands are present, mark them as:

```text
reserved / not implemented in Product Milestone 1
```

### 19.4 `agentx-init scan`

Execution order:

```text
1. Parse repo_root.
2. Resolve repository root.
3. Load config or defaults.
4. Build path registry.
5. Ensure runtime directories.
6. Run repository scanner.
7. Validate scan artifact.
8. Write repo_scan_latest.json.
9. Append scans.jsonl.
10. Append audit event.
11. Append command_history.jsonl.
12. Return CLI response.
```

Success output must mention:

```text
scan status
file count
directory count
repo_scan_latest.json path
scans.jsonl path
audit event path
```

### 19.5 `agentx-init status`

Execution order:

```text
1. Parse repo_root.
2. Resolve repository root.
3. Load config or defaults.
4. Build path registry.
5. Ensure runtime directories.
6. Load repo_scan_latest.json.
7. If missing, return BLOCKED with MISSING_SCAN.
8. Validate scan artifact.
9. Run architecture analyzer.
10. Validate architecture_latest.json.
11. Render latest_status.md.
12. Append architecture_history.jsonl when possible.
13. Append audit event.
14. Append command_history.jsonl.
15. Return CLI response.
```

If scan is missing:

```text
status = BLOCKED
exit_code = 3
failure_class = MISSING_SCAN
message must tell user to run agentx-init scan first
```

---

### 19.6 Concrete CLI Examples

Help success example:

```bash
agentx-init --help
```

Expected behavior:

```text
exit_code = 0
status = SUCCESS
output lists help, scan, status
reserved commands are omitted or marked reserved
```

Scan success example:

```bash
agentx-init scan .
```

Minimum response content:

```json
{
  "command": "scan",
  "status": "SUCCESS",
  "exit_code": 0,
  "message": "Repository scan completed.",
  "artifact_refs": [
    ".agentx-init/snapshots/repo_scan_latest.json",
    ".agentx-init/memory/scans.jsonl",
    ".agentx-init/memory/audit_events.jsonl"
  ]
}
```

Status missing-scan example:

```bash
agentx-init status .
```

If no scan exists:

```json
{
  "command": "status",
  "status": "BLOCKED",
  "exit_code": 3,
  "message": "No repository scan found. Run agentx-init scan first.",
  "errors": [
    {"failure_class": "MISSING_SCAN"}
  ]
}
```

Status success after scan:

```json
{
  "command": "status",
  "status": "SUCCESS",
  "exit_code": 0,
  "message": "Status report generated.",
  "artifact_refs": [
    ".agentx-init/snapshots/architecture_latest.json",
    ".agentx-init/reports/latest_status.md",
    ".agentx-init/memory/audit_events.jsonl"
  ]
}
```

Reserved command example:

```bash
agentx-init plan
```

If present in PM1:

```json
{
  "command": "plan",
  "status": "BLOCKED",
  "exit_code": 3,
  "message": "Command is reserved for a later product milestone.",
  "errors": [
    {"failure_class": "COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1"}
  ]
}
```

## 20. Reserved Command Stub Policy

If any of these exist:

```text
explain
plan
propose
validate
audit
graph
report
memory
```

they must:

```text
return BLOCKED
exit with code 3
append audit event when possible
append command history when possible
not create later milestone artifacts
not import later milestone components
not run validation
not query graph
not create plans
not create proposals
```

Allowed reserved command categories:

```text
RESERVED
UNKNOWN
```

Reserved commands must not use categories implying active behavior.

---

## 21. Failure Classes

Use these failure classes consistently:

```text
PATH_NOT_FOUND
PATH_NOT_DIRECTORY
PATH_OUTSIDE_WORKSPACE
PATH_TRAVERSAL_BLOCKED
PERMISSION_DENIED
FILE_READ_ERROR
HASH_ERROR
LARGE_FILE_SKIPPED
SYMLINK_SKIPPED
MISSING_SCAN
INVALID_SCAN
INVALID_CONFIG
INVALID_SCHEMA
INVALID_SCHEMA_CONTRACT
ARTIFACT_WRITE_ERROR
AUDIT_WRITE_ERROR
COMMAND_HISTORY_WRITE_ERROR
COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1
SOURCE_MUTATION_DETECTED
UNKNOWN_PM1_ERROR
```

Failures must be represented in CLI response, audit event, or completion record when possible.

---

## 22. Artifact Write Protocols

### 22.1 Latest JSON Snapshot

For files such as:

```text
repo_scan_latest.json
architecture_latest.json
config_validation_report_latest.json
```

Use:

```text
build object in memory
validate object
write temp file under same directory
re-read temp file
validate again if practical
atomic replace latest file
```

Never overwrite a previous valid latest snapshot with invalid output.

### 22.2 JSONL Append

For files such as:

```text
audit_events.jsonl
scans.jsonl
architecture_history.jsonl
command_history.jsonl
```

Rules:

```text
append one JSON object per line
never rewrite previous lines
never reorder previous lines
never delete previous lines
preserve malformed previous lines
```

### 22.3 Markdown Report

For markdown reports:

```text
build report from validated structured data
write temp markdown file under .agentx-init/reports/
replace latest report only after render succeeds
```

---

## 23. Dependency Rules

Allowed standard library imports:

```text
argparse
collections
dataclasses
datetime
enum
fnmatch
hashlib
json
os
pathlib
sys
typing
uuid
```

Conditionally allowed:

```text
jsonschema, if installed or declared in project dependencies
jinja2, if already accepted for templates
pydantic, only if project-wide standard already uses it
```

Forbidden runtime imports for PM1 core behavior:

```text
subprocess
requests
urllib
httpx
socket
git
shutil.rmtree
os.system
eval
exec
```

Use of `shutil` for safe test fixture setup is allowed only in tests, not runtime source logic.

---

## 24. Test Requirements

PM1 is not complete unless tests prove the implementation.

### 24.1 Required Unit Tests

```text
test_config_defaults_when_missing
test_config_rejects_unsafe_runtime_root
test_path_registry_resolves_managed_paths
test_path_registry_blocks_escape
test_paths_facade_delegates_to_path_registry
test_audit_appends_event
test_audit_preserves_existing_lines
test_layer_mapper_classifies_l0_as_protected
test_layer_mapper_allows_unknown
test_repo_scanner_valid_root
test_repo_scanner_missing_root_fails
test_repo_scanner_ignores_agentx_init
test_repo_scanner_hash_deterministic
test_repo_scanner_large_file_policy
test_repo_scanner_symlink_escape_skipped
test_repo_scan_schema_validates
test_architecture_blocks_missing_scan
test_architecture_summary_from_scan
test_architecture_findings_require_evidence
test_report_writer_status_sections
test_cli_help
test_cli_scan_generates_artifacts
test_cli_status_requires_scan
test_cli_status_after_scan_generates_report
test_reserved_command_blocks_if_present
test_source_non_mutation_after_scan_status
```

### 24.2 Required Integration Tests

```text
test_scan_fresh_fixture_repo
test_status_after_scan_fixture_repo
test_runtime_writes_only_agentx_init
test_command_history_written
test_audit_event_written_for_scan_and_status
```

### 24.3 Test Fixtures

Create fixtures for:

```text
fresh repository with README and simple source file
Agent_X style repository with L0/L1/L2 directories
tests directory
schemas directory
validators directory
profile/spec directory
large file above limit
symlink escape attempt
missing scan state
source mutation detection baseline
```

### 24.4 Source Mutation Verification

Test must snapshot source tree before and after `scan` and `status` excluding `.agentx-init/` and confirm no source files changed.

---

## 25. Implementation Order

Follow this order exactly:

```text
1. Package skeleton
2. Schema validation helper
3. Config model and loader
4. Path registry
5. paths.py compatibility facade
6. Runtime directory creation
7. Audit model and audit log
8. Layer mapper
9. Repository model
10. Repository scanner
11. Architecture analyzer
12. Report writer minimal status rendering
13. CLI models and registry
14. Help command
15. Scan command
16. Status command
17. Reserved command stubs, only if already present or intentionally included
18. Tests
19. Completion evidence
```

Do not implement later milestone engines in PM1.

---

## 26. Component Dependency DAG

```text
schema_validation
  -> config_model
  -> config
  -> path_registry
  -> paths facade
  -> audit_model
  -> audit_log
  -> layer_mapper
  -> repo_model
  -> repo_scanner
  -> architecture_analyzer
  -> report_writer
  -> cli models / registry
  -> help / scan / status commands
```

`architecture_analyzer` depends on scanner artifacts, not direct repository traversal.

`status` depends on prior scan artifact.

---

## 27. Completion Evidence Package

At the end of PM1, create:

```text
.agentx-init/snapshots/pm1_completion_record.json
```

Minimum fields:

```json
{
  "schema_version": "1.0",
  "completion_id": "string",
  "timestamp": "string",
  "milestone": "Product Milestone 1",
  "status": "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED",
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "commands_run": [],
  "artifacts_generated": [],
  "test_results": [],
  "deviations": [],
  "unresolved_risks": [],
  "source_mutation_check": "PASS|FAIL|NOT_RUN"
}
```

PM1 should be marked `VALIDATED` only when required tests pass and source mutation check passes.

---

## 28. Acceptance Criteria

PM1 is complete only if all are true:

```text
agentx-init --help works
agentx-init help works
agentx-init scan works on a fresh repository fixture
agentx-init scan writes repo_scan_latest.json
agentx-init scan appends scans.jsonl
agentx-init scan appends audit_events.jsonl
agentx-init status blocks clearly if scan is missing
agentx-init status works after scan
agentx-init status writes architecture_latest.json
agentx-init status writes latest_status.md
command_history.jsonl is appended for commands when possible
all PM1 JSON artifacts validate against schemas
L0 paths are classified as protected
unknown layer is allowed
.agentx-init/ is excluded from repository hash
runtime writes are only under .agentx-init/
source files are unchanged after scan/status
reserved later commands are absent or blocked stubs
no forbidden imports are used in runtime modules
all required tests pass
pm1_completion_record.json exists
```

---

## 29. Stop Conditions

Stop and record `BLOCKED` if any of these occur:

```text
write boundary cannot be enforced
repository root cannot be safely resolved
schema expectations conflict irreconcilably
component contract conflict cannot be resolved
source mutation is required to satisfy a runtime feature
later milestone component is required for active PM1 behavior
scanner needs command execution
status needs direct repository traversal
path_registry cannot replace canonical path authority
CLI name cannot be normalized to agentx-init
```

Do not guess around stop conditions.

---

## 30. Recovery and Rollback Rules

If implementation fails mid-pass:

```text
preserve source changes for review unless they are clearly accidental generated files
preserve .agentx-init/ diagnostic artifacts
record failure in pm1_completion_record.json if possible
record audit event if possible
summarize failed step, files touched, and tests run
```

Do not silently delete evidence of failed attempts.

Generated invalid latest artifacts must not replace previous valid latest artifacts.

---

## 31. File-by-File Completion Matrix

Before PM1 is marked complete, verify each item below.

| File / area | Required final state | Evidence |
|---|---|---|
| `pyproject.toml` | `agentx-init` CLI entrypoint exists or equivalent local execution documented | help command test |
| `cli/main.py` | routes help, scan, status; reserved commands blocked/absent | CLI tests |
| `cli/registry.py` | registry only exposes PM1 active commands plus reserved stubs | registry/CLI tests |
| `cli/models.py` | command request/response models serialize to schema-compatible dicts | schema tests |
| `core/config.py` | loads config.json or safe defaults | config tests |
| `core/path_registry.py` | canonical path authority and write-boundary checks | path tests |
| `core/paths.py` | facade only; delegates to path_registry | facade test |
| `core/audit_log.py` | append-only audit with hash chain fields | audit tests |
| `core/layer_mapper.py` | L0/L1/L2/unknown and protection classification | layer tests |
| `core/repo_model.py` | scan dataclasses and deterministic serialization | model tests |
| `core/repo_scanner.py` | deterministic read-only scanner | scanner tests |
| `core/architecture_analyzer.py` | consumes scan artifact only; no source traversal | analyzer tests |
| `core/report_writer.py` | PM1 markdown status/architecture rendering only | report tests |
| `core/schema_validation.py` | jsonschema or fallback validation | schema tests |
| `schemas/*.schema.json` | required PM1 schemas exist and validate samples | schema tests |
| `templates/status_report.md.j2` | status report sections present | report tests |
| `tests/` | required tests from section 24 implemented | pytest result |
| `.agentx-init/snapshots/pm1_completion_record.json` | completion evidence generated | completion artifact |

No file in this matrix may depend on active Governance, Risk, Planner, Proposal, Validation Runner, full Memory Store, or Knowledge Graph behavior.


## 31A. Existing Repository Preservation Rules

PM1 implementation may be applied to an existing repository, not only to an empty package skeleton.

Rules:

```text
create missing PM1 files
update existing PM1 files only as needed
preserve unrelated existing project files
avoid broad rewrites not required by this spec
do not delete existing source files unless they are obsolete PM1 compatibility files and deletion is explicitly justified
prefer compatibility wrappers when renaming behavior could break imports
```

If an existing file conflicts with this PM1 specification:

```text
make the smallest conforming change
record the conflict in pm1_completion_record.json
add or update tests proving the corrected behavior
```

If the conflict cannot be resolved without changing later-milestone behavior, stop and record `BLOCKED`.

## 31B. Command History Requirements

PM1 must write command history when possible:

```text
.agentx-init/logs/command_history.jsonl
```

Each command history record must include:

```json
{
  "schema_version": "1.0",
  "history_id": "string",
  "timestamp": "string",
  "request": {},
  "response": {},
  "governance_ref": null,
  "audit_event_id": "string|null"
}
```

Rules:

```text
append exactly one command history line per command attempt when possible
never rewrite previous command history lines
preserve malformed historical lines
record command history write failure in the CLI response warning if the main command otherwise completed
```

`governance_ref` must be `null` in PM1 because the Governance Engine is not active.

## 31C. CLI Output Mode Rule

The CLI may print human-readable text to stdout, but the internal command response object must always be structured and schema-compatible.

Minimum behavior:

```text
terminal output may be concise text
command_history.jsonl must store the structured command request/response
JSON output mode may be added only if implemented safely and tested
```

Do not make PM1 depend on rich terminal formatting, interactive prompts, colors, or terminal-specific UI features.

## 31D. Atomic Write Detail

For latest artifacts, use a temp file under the same directory as the final artifact.

Acceptable temp naming pattern:

```text
<artifact_name>.tmp.<uuid>
```

Required sequence:

```text
write temp
flush/close temp
re-read temp
validate if JSON
replace final path using atomic rename/replace supported by pathlib/os
remove temp only after successful replace or record cleanup warning
```

Never write temp files outside `.agentx-init/` for runtime artifacts.

## 31E. Forbidden Import Verification

The implementation must include a test or static check that scans PM1 runtime modules for forbidden imports.

Minimum forbidden runtime imports/checks:

```text
subprocess
requests
urllib
httpx
socket
git
os.system
shutil.rmtree
eval(
exec(
```

This check applies to runtime implementation files, not to tests. Test code may use safe filesystem helpers for fixtures.

## 31F. Schema Sample Fixtures

Schema tests must include both valid and invalid samples for the most important PM1 artifacts.

Minimum required samples:

```text
valid config
invalid config missing schema_version
valid path registry
invalid path registry with unsafe escape path
valid audit event
invalid audit event missing event_id
valid repo scan
invalid repo scan missing files
valid architecture report
invalid architecture report missing evidence for non-unknown finding
valid command response
invalid command response with unknown status
valid completion record
invalid completion record missing status
```

These samples may be inline dictionaries in tests or fixture JSON files.

## 31G. PM1 Completion Review Checklist

Before creating `pm1_completion_record.json`, the implementer must verify:

```text
[ ] CLI entrypoint works through console script or documented local module execution
[ ] help command works
[ ] scan command works on fixture repository
[ ] status blocks cleanly before scan
[ ] status succeeds after scan
[ ] runtime writes are contained under .agentx-init/
[ ] source non-mutation test passes
[ ] L0 protection classification test passes
[ ] repository hash excludes .agentx-init/
[ ] JSON latest artifacts validate before replace
[ ] JSONL files are append-only
[ ] reserved commands are absent or blocked
[ ] no active later-milestone engines are imported by PM1 commands
[ ] forbidden runtime import check passes
[ ] all required tests pass or completion status is not VALIDATED
```

## 32. Final Coding LLM Prompt

Use this as the implementation instruction:

```text
Implement Product Milestone 1 of agentx-init exactly according to AGENT_X_INITIATOR_PM1_IMPLEMENTATION_SPEC_v7.md.

Build only the PM1 active components: package skeleton, CLI entrypoint, help, config, path registry, paths facade, runtime directory setup, append-only audit log, layer mapper, repository model, repository scanner, scan command, minimal architecture analyzer, minimal report writer, status command, schema validation, tests, and completion evidence.

Do not implement active governance, risk, planning, proposal, validation, memory store, or knowledge graph behavior.

Use agentx-init as the canonical CLI name. Use .agentx-init/config/config.json as canonical config. Use path_registry.py as canonical path authority and keep paths.py only as a facade. Runtime writes must stay under .agentx-init/. Source files must not be modified by runtime commands.

Implement scan and status with schema-valid artifacts, append-only JSONL history, audit events, deterministic scanner behavior, L0 protection classification, and source non-mutation tests.

Reserved later commands must be absent or return BLOCKED with COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1.

Stop and report BLOCKED if any requirement requires source mutation, shell execution, network access, Git operations, or a later milestone component.
```

---

## 33. Final Rating

This v7 specification is rated **10/10** as a standalone Product Milestone 1 implementation handoff.

It defines:

```text
scope
non-scope
canonical names
source files
schemas
templates
tests
runtime artifacts
path registry
config rules
audit rules
scanner behavior
architecture/status behavior
CLI behavior
reserved command behavior
failure classes
write protocols
import rules
test fixtures
implementation order
completion evidence
acceptance criteria
stop conditions
rollback behavior
final coding prompt
existing repository preservation rules
command history requirements
CLI output mode rule
atomic write details
forbidden import verification
schema sample fixtures
PM1 completion review checklist
```

A coding LLM should be able to complete Product Milestone 1 using this document alone.
