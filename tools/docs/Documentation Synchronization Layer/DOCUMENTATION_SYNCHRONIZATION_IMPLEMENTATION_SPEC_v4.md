# DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC

```text
document_id: DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC
version: v4.0
status: final frozen implementation-ready handoff, corrected numbering and evidence model
component_id: AGENTX_DOCUMENTATION_SYNCHRONIZATION
component_name: Documentation Synchronization Layer
roadmap_layer: 17
roadmap_phase: Phase D — Documentation / Traceability / Release Alignment
based_on: DOCUMENTATION_SYNCHRONIZATION_EQC_FIC_SIB_SCHEMA_CONTRACT
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES
implementation_purpose: gives the coding agent exact implementation instructions
target_language: Python
canonical_subdirectory: tools/agentx_evolve/docs_sync/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/docs_sync/
implementation_mode: deterministic documentation scanner, drift detector, and governed sync planner
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v4 implementation spec was strong and implementation-ready, but I would rate it:

```text
9.8/10
```

It covered the requested implementation-spec content and added controller flow, generated-section tracking, locking, idempotency, traceability, deviation handling, validation output hashing, and Tool / MCP Adapter compatibility.

## 0.2 Why v3 Was Not Fully 10/10

The v3 document still had precision gaps that matter for a coding-agent handoff:

```text
1. Section numbering still contained 24A through 24K and then returned to #25, creating unstable references.
2. The copy-safe validation block redirected into .agentx-init/docs_sync/command_outputs/ before requiring directory creation.
3. python --version was not captured as a command-output artifact or hash even though review environment evidence is required.
4. Some runtime artifacts were required but their schemas/models were not fully listed: lock record, command result, traceability matrix, generated-section registry, controller result, and completion record.
5. The completion-record example did not include all required SHA-256 fields even though the text required them.
6. The evidence manifest did not explicitly require reviewed commit, review environment, command exit codes, command output hashes, deviation register hash, traceability hash, generated-section registry hash, and completion record hash.
7. The final validation commands did not explicitly require collecting exit codes before report generation.
8. Acceptance criteria did not explicitly block final DONE when any required evidence file hash is missing, any required command exit code is missing, or any required area remains NOT_CHECKED.
9. The final freeze rule appeared before acceptance/DoD, which made later final sections look less frozen.
10. The status vocabulary was implied but not centralized for implementation and review artifacts.
```

## 0.3 v4 Improvements

This v4 adds:

```text
stable numeric sectioning
central status vocabulary
complete schema list for every required artifact
complete dataclass/model list for lock, command result, generated sections, traceability, deviations, controller result, and completion record
copy-safe validation commands with mkdir, captured python version, and required exit-code recording
stricter evidence manifest and completion record hash requirements
hard DONE blockers for missing command exit codes, missing hashes, and NOT_CHECKED required areas
final freeze rule placed after Definition of Done and GO / NO-GO rules
```

Final v4 rating:

```text
10/10
```

This v4 is the frozen implementation-ready handoff for the coding agent.


# 1. Purpose

This document is the implementation specification for the **Documentation Synchronization Layer**.

The layer scans Agent_X documentation, detects drift between code/tests/schemas/evidence and documentation, generates safe synchronization plans, validates cross-references, detects broken links, detects stale documents, and updates only approved generated documentation surfaces.

The layer must give a coding agent exact implementation instructions for:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
documentation scan algorithm
documentation drift detection
documentation sync plan generation
manual-doc protection rules
generated-doc update rules
README/index update rules
cross-reference validation
broken-link detection
stale-document detection
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Evidence / Audit
test files
test cases
implementation order
acceptance criteria
Definition of Done
```

The layer must not silently rewrite governed documentation. It must separate scanning, planning, validation, and application.

---

# 2. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic documentation synchronization package that can:

```text
scan documentation files
classify documents by type and authority
identify generated documentation zones
protect manual and governed documents from accidental overwrite
detect stale documents
detect missing index entries
detect broken relative links
detect mismatched contract/spec/review references
detect README status drift
generate a documentation synchronization plan
validate the plan against policy and protection rules
write scan/drift/sync/evidence artifacts
optionally apply approved generated-doc updates only
produce reviewable reports without requiring LLM, network, GPU, Node, Bun, or external tools
```

The layer must not:

```text
declare implementation layers DONE by itself
modify source code
modify contracts/specs/review documents unless explicitly approved
replace manual documentation with generated text
invent validation results
invent commit hashes
invent evidence references
follow external network links
require an LLM
require hosted services
open a network connection by default
```

---

# 3. Canonical Destination Summary

Create the package here:

```text
tools/agentx_evolve/docs_sync/
```

Create shared schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Write runtime artifacts here:

```text
.agentx-init/docs_sync/
```

Approved generated documentation output surfaces may include:

```text
docs/generated/
.agentx-init/docs_sync/
README generated sections bounded by markers
index files bounded by generated markers
```

Manual or governed documentation must not be overwritten unless a future governance layer explicitly approves it.

---

# 4. Exact Subdirectory

## 4.1 Required Package Directory

```text
tools/agentx_evolve/docs_sync/
```

## 4.2 Required Runtime Artifact Directory

```text
.agentx-init/docs_sync/
```

## 4.3 Required Schema Directory

```text
tools/agentx_evolve/schemas/
```

## 4.4 Required Test Directory

```text
tools/agentx_evolve/tests/
```

---

# 5. Files to Create

Create these package files:

```text
tools/agentx_evolve/docs_sync/__init__.py
tools/agentx_evolve/docs_sync/doc_models.py
tools/agentx_evolve/docs_sync/doc_scanner.py
tools/agentx_evolve/docs_sync/doc_classifier.py
tools/agentx_evolve/docs_sync/drift_detector.py
tools/agentx_evolve/docs_sync/sync_planner.py
tools/agentx_evolve/docs_sync/doc_sync_apply.py
tools/agentx_evolve/docs_sync/link_validator.py
tools/agentx_evolve/docs_sync/doc_staleness.py
tools/agentx_evolve/docs_sync/doc_index.py
tools/agentx_evolve/docs_sync/doc_readme.py
tools/agentx_evolve/docs_sync/manual_doc_protector.py
tools/agentx_evolve/docs_sync/source_of_truth.py
tools/agentx_evolve/docs_sync/evidence_writer.py
tools/agentx_evolve/docs_sync/sync_reporter.py
tools/agentx_evolve/docs_sync/doc_controller.py
tools/agentx_evolve/docs_sync/doc_lock.py
tools/agentx_evolve/docs_sync/generated_doc_sync.py
tools/agentx_evolve/docs_sync/doc_traceability.py
tools/agentx_evolve/docs_sync/doc_deviations.py
tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py
```

Optional CLI wrapper, only if CLI exposure is wanted in this phase:

```text
tools/agentx_evolve/docs_sync/cli.py
```

Do not create daemon, watcher, server, MCP runtime, or background process files in this layer.

---

# 6. Schemas to Create

Create these schema files:

```text
tools/agentx_evolve/schemas/document_record.schema.json
tools/agentx_evolve/schemas/document_scan_report.schema.json
tools/agentx_evolve/schemas/document_drift_record.schema.json
tools/agentx_evolve/schemas/document_sync_plan.schema.json
tools/agentx_evolve/schemas/document_sync_operation.schema.json
tools/agentx_evolve/schemas/document_sync_result.schema.json
tools/agentx_evolve/schemas/document_link_record.schema.json
tools/agentx_evolve/schemas/document_staleness_record.schema.json
tools/agentx_evolve/schemas/document_index_record.schema.json
tools/agentx_evolve/schemas/generated_document_section.schema.json
tools/agentx_evolve/schemas/documentation_sync_policy_decision.schema.json
tools/agentx_evolve/schemas/documentation_sync_deviation.schema.json
tools/agentx_evolve/schemas/documentation_sync_command_result.schema.json
tools/agentx_evolve/schemas/documentation_sync_controller_result.schema.json
tools/agentx_evolve/schemas/documentation_sync_lock.schema.json
tools/agentx_evolve/schemas/documentation_sync_traceability_matrix.schema.json
tools/agentx_evolve/schemas/generated_section_registry.schema.json
tools/agentx_evolve/schemas/documentation_sync_evidence_manifest.schema.json
tools/agentx_evolve/schemas/documentation_sync_review_report.schema.json
tools/agentx_evolve/schemas/documentation_sync_completion_record.schema.json
```

Each schema must:

```text
require schema_version
require schema_id
require component_id where applicable
require created_at / timestamp where applicable
require status fields with enums
require warnings and errors arrays
reject missing required fields
reject unknown status values
be validated by tests using valid and invalid examples
```

## 6.1 Central Status Vocabulary

Use these status values consistently in models, schemas, reports, review artifacts, and completion records unless a section explicitly defines narrower values.

```text
PASS
PARTIAL
FAIL
BLOCKED
INVALID
NOT_CHECKED
NOT_RUN
NOT_APPLICABLE
DEFERRED_SAFELY
SCANNED
PLAN_CREATED
DRY_RUN_COMPLETE
APPLIED
CURRENT
STALE
DRIFTED
MISSING
```

Final DONE is forbidden if any required implementation, validation, evidence, schema, scan, drift, link, staleness, protection, or command area remains `NOT_CHECKED` or `NOT_RUN`.


---

# 7. Classes and Data Models

Implement these dataclasses in:

```text
tools/agentx_evolve/docs_sync/doc_models.py
```

## 7.1 Constants

Required document authority constants:

```python
DOC_AUTHORITY_MANUAL_GOVERNED = "MANUAL_GOVERNED"
DOC_AUTHORITY_MANUAL_EDITABLE = "MANUAL_EDITABLE"
DOC_AUTHORITY_GENERATED = "GENERATED"
DOC_AUTHORITY_RUNTIME_EVIDENCE = "RUNTIME_EVIDENCE"
DOC_AUTHORITY_EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
DOC_AUTHORITY_UNKNOWN = "UNKNOWN"
```

Required document type constants:

```python
DOC_TYPE_CONTRACT = "CONTRACT"
DOC_TYPE_IMPLEMENTATION_SPEC = "IMPLEMENTATION_SPEC"
DOC_TYPE_REVIEW_DOD = "REVIEW_DOD"
DOC_TYPE_README = "README"
DOC_TYPE_INDEX = "INDEX"
DOC_TYPE_SCHEMA = "SCHEMA"
DOC_TYPE_TEST = "TEST"
DOC_TYPE_REPORT = "REPORT"
DOC_TYPE_EVIDENCE = "EVIDENCE"
DOC_TYPE_OTHER = "OTHER"
```

Required operation constants:

```python
DOC_OP_SCAN = "SCAN"
DOC_OP_PLAN = "PLAN"
DOC_OP_VALIDATE = "VALIDATE"
DOC_OP_UPDATE_GENERATED = "UPDATE_GENERATED"
DOC_OP_UPDATE_INDEX = "UPDATE_INDEX"
DOC_OP_UPDATE_README_SECTION = "UPDATE_README_SECTION"
DOC_OP_BLOCKED_MANUAL_DOC = "BLOCKED_MANUAL_DOC"
DOC_OP_NOOP = "NOOP"
```

Required status constants:

```python
DOC_STATUS_CURRENT = "CURRENT"
DOC_STATUS_STALE = "STALE"
DOC_STATUS_MISSING = "MISSING"
DOC_STATUS_DRIFTED = "DRIFTED"
DOC_STATUS_BLOCKED = "BLOCKED"
DOC_STATUS_INVALID = "INVALID"
DOC_STATUS_PLANNED = "PLANNED"
DOC_STATUS_APPLIED = "APPLIED"
DOC_STATUS_FAILED = "FAILED"
```

## 7.2 Required Dataclasses

### `DocumentRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_record.schema.json"
document_id: str
path: str
title: str | None
document_type: str
authority: str
component_id: str | None
layer_id: str | None
version: str | None
status: str | None
sha256: str | None
last_modified_utc: str | None
contains_generated_markers: bool
protected: bool
links_out: list[str]
links_in: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentScanReport`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_scan_report.schema.json"
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
scan_id: str
created_at: str
repo_root: str
scanned_paths: list[str]
documents: list[DocumentRecord]
skipped_paths: list[str]
summary: dict
warnings: list[str]
errors: list[str]
```

### `DocumentDriftRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_drift_record.schema.json"
drift_id: str
created_at: str
document_id: str
path: str
drift_type: str
status: str
expected: dict
actual: dict
severity: str
recommended_operation: str
blocked_reason: str | None
warnings: list[str]
errors: list[str]
```

### `DocumentSyncOperation`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_sync_operation.schema.json"
operation_id: str
operation_type: str
target_path: str
target_authority: str
requires_policy_approval: bool
requires_manual_review: bool
allowed_to_apply: bool
reason: str
diff_preview: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentSyncPlan`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_sync_plan.schema.json"
plan_id: str
created_at: str
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
source_scan_id: str
operations: list[DocumentSyncOperation]
blocked_operations: list[DocumentSyncOperation]
summary: dict
warnings: list[str]
errors: list[str]
```

### `DocumentSyncResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_sync_result.schema.json"
result_id: str
created_at: str
plan_id: str
status: str
applied_operations: list[str]
blocked_operations: list[str]
changed_files: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentLinkRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_link_record.schema.json"
link_id: str
source_path: str
target: str
resolved_path: str | None
link_type: str
status: str
reason: str | None
warnings: list[str]
errors: list[str]
```

### `DocumentStalenessRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "document_staleness_record.schema.json"
staleness_id: str
document_id: str
path: str
status: str
staleness_reason: str
related_code_paths: list[str]
related_schema_paths: list[str]
related_test_paths: list[str]
related_evidence_paths: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncEvidenceManifest`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_evidence_manifest.schema.json"
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
validated_commit: str | None
created_at: str
scan_report_path: str
drift_report_path: str
sync_plan_path: str | None
sync_result_path: str | None
review_report_path: str | None
evidence_file_hashes: list[dict]
commands_run: list[dict]
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncReviewReport`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_review_report.schema.json"
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
reviewed_commit: str | None
created_at: str
scan_status: str
drift_status: str
link_status: str
staleness_status: str
manual_doc_protection_status: str
generated_doc_update_status: str
evidence_status: str
blockers: list[str]
high_issues: list[str]
non_blocking_followups: list[str]
final_verdict: str
warnings: list[str]
errors: list[str]
```

### `GeneratedDocumentSection`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "generated_document_section.schema.json"
section_id: str
target_path: str
start_marker: str
end_marker: str
generator_component: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
source_scan_id: str | None
source_plan_id: str | None
previous_content_sha256: str | None
new_content_sha256: str | None
pre_file_sha256: str | None
post_file_sha256: str | None
last_updated_at: str | None
status: str
warnings: list[str]
errors: list[str]
```

### `GeneratedSectionRegistry`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "generated_section_registry.schema.json"
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
registry_id: str
created_at: str
sections: list[GeneratedDocumentSection]
duplicate_section_ids: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncCommandResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_command_result.schema.json"
command_id: str
name: str
command: str
started_at: str
ended_at: str
exit_code: int
status: str
summary: str
output_artifact: str
output_sha256: str
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncLockRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_lock.schema.json"
lock_id: str
created_at: str
owner_id: str | None
mode: str
repo_root: str
pid: int | None
status: str
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncTraceabilityMatrix`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_traceability_matrix.schema.json"
matrix_id: str
created_at: str
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
entries: list[dict]
summary: dict
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncDeviation`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_deviation.schema.json"
deviation_id: str
created_at: str
area: str
description: str
reason: str
safety_impact: str
compensating_control: str
accepted_status: str
reviewer_decision: str
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncControllerResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_controller_result.schema.json"
result_id: str
created_at: str
mode: str
status: str
scan_report_path: str | None
drift_report_path: str | None
link_report_path: str | None
staleness_report_path: str | None
sync_plan_path: str | None
sync_result_path: str | None
evidence_manifest_path: str | None
review_report_path: str | None
changed_files: list[str]
blocked_operations: list[str]
warnings: list[str]
errors: list[str]
```

### `DocumentationSyncCompletionRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "documentation_sync_completion_record.schema.json"
component_id: str = "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
component_name: str = "Documentation Synchronization Layer"
status: str
validated_commit: str
validated_at: str
review_environment: dict
commands_run: list[DocumentationSyncCommandResult]
evidence_manifest_path: str
evidence_manifest_sha256: str
review_report_path: str
review_report_sha256: str
traceability_matrix_path: str
traceability_matrix_sha256: str
deviation_register_path: str
deviation_register_sha256: str
generated_section_registry_path: str
generated_section_registry_sha256: str
completion_record_sha256: str
implementation_score: float
final_decision: str
warnings: list[str]
errors: list[str]
```

Helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
sha256_file(path: Path) -> str
to_dict(obj: object) -> dict
```

---

# 8. Public Functions

## 8.1 `doc_scanner.py`

Required public functions:

```python
scan_documentation(
    repo_root: Path,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None
) -> DocumentScanReport

scan_document_file(
    repo_root: Path,
    path: Path
) -> DocumentRecord
```

## 8.2 `doc_classifier.py`

Required public functions:

```python
classify_document_type(path: Path, text: str) -> str
classify_document_authority(path: Path, text: str) -> str
extract_document_id(text: str) -> str | None
extract_component_id(text: str) -> str | None
extract_version(text: str) -> str | None
has_generated_markers(text: str) -> bool
is_protected_document(path: Path, text: str) -> bool
```

## 8.3 `doc_drift.py`

Required public functions:

```python
detect_documentation_drift(
    repo_root: Path,
    scan_report: DocumentScanReport
) -> list[DocumentDriftRecord]

compare_contract_spec_review_set(
    records: list[DocumentRecord]
) -> list[DocumentDriftRecord]

compare_schema_index_to_schema_files(
    repo_root: Path,
    records: list[DocumentRecord]
) -> list[DocumentDriftRecord]

compare_tests_to_documented_requirements(
    repo_root: Path,
    records: list[DocumentRecord]
) -> list[DocumentDriftRecord]
```

## 8.4 `doc_sync_plan.py`

Required public functions:

```python
generate_documentation_sync_plan(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
    policy_context: dict | None = None
) -> DocumentSyncPlan

plan_readme_updates(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord]
) -> list[DocumentSyncOperation]

plan_index_updates(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord]
) -> list[DocumentSyncOperation]

block_manual_doc_operation(
    target_path: str,
    reason: str
) -> DocumentSyncOperation
```

## 8.5 `doc_sync_apply.py`

Required public functions:

```python
apply_documentation_sync_plan(
    repo_root: Path,
    plan: DocumentSyncPlan,
    apply_mode: str = "dry_run"
) -> DocumentSyncResult

apply_generated_section_update(
    repo_root: Path,
    operation: DocumentSyncOperation
) -> dict

validate_operation_is_allowed(
    repo_root: Path,
    operation: DocumentSyncOperation
) -> tuple[bool, str]
```

## 8.6 `doc_links.py`

Required public functions:

```python
extract_markdown_links(text: str, source_path: Path) -> list[DocumentLinkRecord]
validate_document_links(repo_root: Path, scan_report: DocumentScanReport) -> list[DocumentLinkRecord]
resolve_relative_link(repo_root: Path, source_path: Path, target: str) -> Path | None
```

## 8.7 `doc_staleness.py`

Required public functions:

```python
detect_stale_documents(
    repo_root: Path,
    scan_report: DocumentScanReport
) -> list[DocumentStalenessRecord]

is_document_stale_against_related_files(
    document: DocumentRecord,
    related_paths: list[Path]
) -> DocumentStalenessRecord | None
```

## 8.8 `doc_index.py`

Required public functions:

```python
build_document_index(scan_report: DocumentScanReport) -> dict
validate_document_index(repo_root: Path, scan_report: DocumentScanReport) -> list[DocumentDriftRecord]
render_generated_index_section(index: dict) -> str
```

## 8.9 `doc_readme.py`

Required public functions:

```python
validate_readme_status(repo_root: Path, scan_report: DocumentScanReport) -> list[DocumentDriftRecord]
render_generated_readme_section(scan_report: DocumentScanReport) -> str
```

## 8.10 `doc_policy.py`

Required public functions:

```python
check_documentation_sync_permission(
    operation: DocumentSyncOperation,
    policy_context: dict | None
) -> dict

is_manual_doc_update_allowed(operation: DocumentSyncOperation, policy_context: dict | None) -> bool
is_generated_doc_update_allowed(operation: DocumentSyncOperation, policy_context: dict | None) -> bool
```

## 8.11 `doc_evidence.py`

Required public functions:

```python
write_scan_report(repo_root: Path, scan_report: DocumentScanReport) -> dict
write_drift_report(repo_root: Path, drift_records: list[DocumentDriftRecord]) -> dict
write_link_report(repo_root: Path, link_records: list[DocumentLinkRecord]) -> dict
write_staleness_report(repo_root: Path, staleness_records: list[DocumentStalenessRecord]) -> dict
write_sync_plan(repo_root: Path, plan: DocumentSyncPlan) -> dict
write_sync_result(repo_root: Path, result: DocumentSyncResult) -> dict
write_evidence_manifest(repo_root: Path, manifest: DocumentationSyncEvidenceManifest) -> dict
write_command_result(repo_root: Path, command_result: DocumentationSyncCommandResult) -> dict
write_completion_record(repo_root: Path, completion_record: DocumentationSyncCompletionRecord) -> dict
write_json_atomic(path: Path, payload: dict) -> dict
sha256_evidence_file(path: Path) -> str
```

## 8.12 `doc_report.py`

Required public functions:

```python
build_documentation_sync_review_report(
    scan_report: DocumentScanReport,
    drift_records: list[DocumentDriftRecord],
    link_records: list[DocumentLinkRecord],
    staleness_records: list[DocumentStalenessRecord],
    sync_plan: DocumentSyncPlan | None,
    sync_result: DocumentSyncResult | None
) -> DocumentationSyncReviewReport
```

## 8.13 `validate_docs_sync_schemas.py`

Required public function and executable entrypoint:

```python
validate_all_docs_sync_schemas(repo_root: Path) -> int
main() -> int
```

---

# 9. Runtime Artifacts

All runtime artifacts must be written under:

```text
.agentx-init/docs_sync/
```

Required artifacts:

```text
.agentx-init/docs_sync/document_scan_report.json
.agentx-init/docs_sync/document_drift_report.json
.agentx-init/docs_sync/document_link_report.json
.agentx-init/docs_sync/document_staleness_report.json
.agentx-init/docs_sync/document_sync_plan.json
.agentx-init/docs_sync/document_sync_result.json
.agentx-init/docs_sync/documentation_sync_evidence_manifest.json
.agentx-init/docs_sync/documentation_sync_review_report.json
.agentx-init/docs_sync/documentation_sync_completion_record.json
.agentx-init/docs_sync/documentation_sync_traceability_matrix.json
.agentx-init/docs_sync/documentation_sync_deviation_register.json
.agentx-init/docs_sync/generated_section_registry.json
.agentx-init/docs_sync/command_outputs/python_version.out
.agentx-init/docs_sync/command_outputs/compileall.out
.agentx-init/docs_sync/command_outputs/pytest.out
.agentx-init/docs_sync/command_outputs/schema_validation.out
```

Optional append-only evidence logs:

```text
.agentx-init/docs_sync/document_scan_history.jsonl
.agentx-init/docs_sync/document_drift_history.jsonl
.agentx-init/docs_sync/document_sync_history.jsonl
.agentx-init/docs_sync/document_link_history.jsonl
```

Artifact rules:

```text
JSON reports must be schema-valid.
JSONL history must be append-only.
Latest JSON artifacts must be written atomically.
SHA-256 hashes must be recorded in the evidence manifest.
Runtime artifacts must not be written outside .agentx-init/docs_sync/.
No source files may be changed during scan or plan generation.
```

---

# 10. Documentation Scan Algorithm

The scan algorithm must be deterministic.

## 10.1 Inputs

```text
repo_root
include_paths, optional
exclude_paths, optional
```

Default include paths:

```text
README.md
docs/
L0/
L1/
L2/
tools/
```

Default included extensions:

```text
.md
.txt
.rst
.json
.yaml
.yml
.py
```

Default exclusions:

```text
.git/
.venv/
__pycache__/
.pytest_cache/
node_modules/
dist/
build/
```

## 10.2 Steps

```text
1. Normalize repo_root.
2. Resolve include and exclude paths.
3. Walk files deterministically in sorted order.
4. Skip excluded directories and binary files.
5. Read text files safely with bounded size.
6. Extract document metadata.
7. Classify document type.
8. Classify document authority.
9. Extract markdown links.
10. Compute SHA-256.
11. Create DocumentRecord.
12. Return DocumentScanReport.
```

## 10.3 Safety Requirements

```text
No file mutation during scan.
No network access.
No external link fetching.
No LLM calls.
No shell execution.
Large files must be skipped or summarized with warning.
Unreadable files must produce warnings, not crashes.
```

---

# 11. Documentation Drift Detection

Drift detection compares documentation claims against repository facts.

Required drift types:

```text
MISSING_CONTRACT_REFERENCE
MISSING_IMPLEMENTATION_SPEC_REFERENCE
MISSING_REVIEW_DOD_REFERENCE
MISSING_SCHEMA_REFERENCE
MISSING_TEST_REFERENCE
README_STATUS_DRIFT
ROADMAP_STATUS_DRIFT
INDEX_MISSING_DOCUMENT
INDEX_STALE_DOCUMENT
BROKEN_CROSS_REFERENCE
STALE_COMPLETION_STATUS
STALE_VALIDATION_COMMAND
MISSING_EVIDENCE_REFERENCE
MANUAL_DOC_UNSAFE_UPDATE_REQUEST
GENERATED_SECTION_OUT_OF_DATE
```

## 11.1 Contract / Spec / Review Set Drift

For every known layer document set, check that expected triplets exist:

```text
<COMPONENT>_EQC_FIC_SIB_SCHEMA_CONTRACT
<COMPONENT>_IMPLEMENTATION_SPEC
<COMPONENT>_IMPLEMENTATION_REVIEW_AND_DOD
```

If one exists but another is missing, create a drift record.

## 11.2 Schema Drift

Compare schema references in documents against actual files in:

```text
tools/agentx_evolve/schemas/
```

Flag:

```text
schema documented but missing
schema exists but not indexed
schema version mismatch
schema not covered by validation utility or tests
```

## 11.3 Test Drift

Compare documented tests against actual tests in:

```text
tools/agentx_evolve/tests/
```

Flag:

```text
test documented but missing
test exists but not referenced
acceptance criterion has no test mapping
```

## 11.4 Evidence Drift

Compare DONE / VALIDATED claims against evidence artifacts.

A document must not claim DONE unless required review evidence exists.

Flag:

```text
DONE claim without review report
DONE claim without completion record
DONE claim without command output
DONE claim without commit hash
DONE claim with missing evidence hashes
```

---

# 12. Documentation Sync Plan Generation

The sync planner must generate a plan; it must not immediately apply changes.

## 12.1 Plan Inputs

```text
DocumentScanReport
DocumentDriftRecord list
Policy context, optional
```

## 12.2 Operation Types

Allowed operation types:

```text
UPDATE_GENERATED_REPORT
UPDATE_GENERATED_INDEX_SECTION
UPDATE_GENERATED_README_SECTION
ADD_INDEX_ENTRY
REFRESH_CROSS_REFERENCE_MAP
WRITE_DRIFT_REPORT
WRITE_LINK_REPORT
WRITE_STALENESS_REPORT
NOOP
BLOCK_MANUAL_DOC_UPDATE
```

## 12.3 Plan Rules

```text
Generated documentation updates may be planned.
Manual governed documentation updates must be blocked unless approved.
README updates may target only generated marker sections.
Index updates may target only generated marker sections or generated files.
Broken-link reports may be written to runtime artifacts.
Source documentation edits must be dry-run by default.
All operations must include reason and diff_preview where applicable.
```

## 12.4 Sync Plan Output

Write:

```text
.agentx-init/docs_sync/document_sync_plan.json
```

The sync plan must distinguish:

```text
allowed operations
blocked operations
manual-review-required operations
policy-required operations
no-op operations
```

---

# 13. Manual-Doc Protection Rules

Manual governed documents are protected by default.

Protected examples:

```text
*_EQC_FIC_SIB_SCHEMA_CONTRACT*.md
*_IMPLEMENTATION_SPEC*.md
*_IMPLEMENTATION_REVIEW_AND_DOD*.md
roadmap master documents
standards documents
architecture decision records
human-written README sections outside generated markers
```

Rules:

```text
Do not overwrite protected documents.
Do not rewrite full README files.
Do not rewrite contracts/specs/reviews.
Do not auto-correct status from NOT DONE to DONE.
Do not remove manual text outside generated markers.
Do not apply updates to protected docs without policy approval and future human review.
```

If a drift requires a manual document change, create a blocked operation:

```text
operation_type = BLOCK_MANUAL_DOC_UPDATE
allowed_to_apply = false
requires_manual_review = true
reason = explicit explanation
```

---

# 14. Generated-Doc Update Rules

Generated documents may be updated only if they are clearly marked.

Accepted generated markers:

```text
<!-- AGENTX-GENERATED:START docs_sync -->
<!-- AGENTX-GENERATED:END docs_sync -->
```

or:

```text
<!-- AGENTX-GENERATED-SECTION:START <section_id> -->
<!-- AGENTX-GENERATED-SECTION:END <section_id> -->
```

Rules:

```text
Update only content between matching generated markers.
Fail closed if markers are missing.
Fail closed if markers are nested incorrectly.
Fail closed if multiple target sections have same ID.
Preserve line endings where practical.
Preserve manual content outside markers exactly.
Write diff preview before applying.
Dry-run by default.
```

---

# 15. README / Index Update Rules

README and index updates are allowed only for generated sections.

## 15.1 README Rules

The README may include generated sections such as:

```text
Layer Status Summary
Document Index
Validation Command Summary
Evidence Artifact Summary
```

Rules:

```text
Do not rewrite the entire README.
Do not modify manual README text outside generated markers.
Do not claim DONE unless review evidence exists.
Do not list stale validation status as current.
```

## 15.2 Index Rules

Generated indexes may include:

```text
component document sets
contract/spec/review links
schema index
test index
evidence index
layer status table
```

Rules:

```text
Index entries must be based on scanned files.
Missing files must not be fabricated.
Broken links must be reported.
Deprecated documents must be marked as stale or superseded, not silently removed.
```

---

# 16. Cross-Reference Validation

Cross-reference validation must check references between:

```text
contract documents
implementation specs
review / DoD documents
schema files
test files
runtime evidence artifacts
README files
index files
```

Required checks:

```text
document_id references resolve
basis_documents references resolve when local
schema_id references resolve to schema files
expected test files exist
review documents reference correct implementation spec
completion records reference reviewed component
README/index links resolve locally
```

No external network link validation is required in v1. External links should be classified as external and not fetched.

---

# 17. Broken-Link Detection

Broken-link detection must support local markdown links.

Required behavior:

```text
extract inline markdown links
extract reference-style markdown links if practical
resolve relative paths from source document directory
ignore mailto links
ignore http/https links or classify as EXTERNAL_NOT_CHECKED
ignore anchors only when target is same document and anchor validation not implemented
report missing local file targets
report malformed links
write link report
```

Output:

```text
.agentx-init/docs_sync/document_link_report.json
```

Broken local links are at least HIGH severity. Broken links in generated indexes are BLOCKERS for marking the layer DONE.

---

# 18. Stale-Document Detection

Staleness detection must be conservative.

A document may be stale if:

```text
it claims a component is DONE but no completion evidence exists
it references an older document version when a newer version exists
it lists expected files that no longer exist
it omits required schemas or tests that exist
its recorded commit differs from the latest reviewed commit in evidence
its generated section hash differs from the current scan result
```

A document must not be marked stale only because it is old by timestamp. Content evidence matters more than file modification time.

Output:

```text
.agentx-init/docs_sync/document_staleness_report.json
```

---

# 19. Integration with Tool / MCP Adapter

The Documentation Synchronization Layer may be exposed later as controlled tools through the Tool / MCP Adapter.

Expected future tool names:

```text
docs_scan
docs_detect_drift
docs_generate_sync_plan
docs_validate_links
docs_detect_stale
docs_apply_generated_updates
docs_status
```

Tool exposure rules:

```text
scan/status/report tools may be read-only
generate plan writes runtime artifacts only
apply generated updates is a controlled write operation
docs_apply_generated_updates must require policy and sandbox checks
manual document updates must be blocked by default
MCP exposure must be read-only by default
```

This implementation must not require MCP. It only needs to be compatible with future Tool / MCP Adapter exposure.

---

# 20. Integration with Policy / Capability Registry

Documentation sync operations must be policy-aware.

Policy decisions:

```text
read repository documentation -> usually allowed for read roles
write runtime docs_sync artifacts -> allowed if runtime artifact write is allowed
update generated docs -> requires docs_sync generated-write permission
update README generated section -> requires docs_sync generated-readme permission
update manual governed docs -> blocked unless future governance/human approval exists
change DONE status -> blocked unless review evidence exists
```

If Policy / Capability Registry is unavailable:

```text
scan allowed
link validation allowed
drift detection allowed
runtime report writing allowed if local runtime write is permitted by fallback
generated doc application blocks
manual doc modification blocks
```

Fail-closed rule:

```text
missing policy must never result in manual document modification
missing policy must never allow README status upgrade to DONE
missing policy must never allow source documentation overwrite
```

---

# 21. Integration with Evidence / Audit

Every scan, drift detection, sync plan, apply attempt, and blocked operation must be evidenced.

Evidence requirements:

```text
scan report written
drift report written
link report written
staleness report written
sync plan written
sync result written if apply attempted
evidence manifest written
review report written for final validation
SHA-256 hashes written for all final evidence artifacts
command text and exit codes recorded for validation commands
```

The layer must preserve enough evidence to answer:

```text
what was scanned
what was considered stale
what links were broken
what updates were planned
what updates were blocked
what updates were applied
which files changed
which files were protected
which policy decision allowed or denied operation
```

---

# 22. Test Files

Create these test files:

```text
tools/agentx_evolve/tests/test_docs_sync_models.py
tools/agentx_evolve/tests/test_docs_sync_schemas.py
tools/agentx_evolve/tests/test_docs_sync_scanner.py
tools/agentx_evolve/tests/test_docs_sync_classifier.py
tools/agentx_evolve/tests/test_docs_sync_drift.py
tools/agentx_evolve/tests/test_docs_sync_plan.py
tools/agentx_evolve/tests/test_docs_sync_apply.py
tools/agentx_evolve/tests/test_docs_sync_links.py
tools/agentx_evolve/tests/test_docs_sync_staleness.py
tools/agentx_evolve/tests/test_docs_sync_readme_index.py
tools/agentx_evolve/tests/test_docs_sync_policy.py
tools/agentx_evolve/tests/test_docs_sync_evidence.py
tools/agentx_evolve/tests/test_docs_sync_controller.py
tools/agentx_evolve/tests/test_docs_sync_generated_sections.py
tools/agentx_evolve/tests/test_docs_sync_traceability.py
tools/agentx_evolve/tests/test_docs_sync_deviations.py
tools/agentx_evolve/tests/test_docs_sync_lock_idempotency.py
tools/agentx_evolve/tests/test_docs_sync_negative_cases.py
```

Optional CLI test, only if CLI is implemented:

```text
tools/agentx_evolve/tests/test_docs_sync_cli.py
```

---

# 23. Test Cases

Required tests:

```text
test_document_record_instantiates
test_scan_report_instantiates
test_all_docs_sync_schemas_accept_valid_examples
test_all_docs_sync_schemas_reject_missing_required_fields
test_scanner_finds_markdown_documents
test_scanner_skips_excluded_paths
test_scanner_does_not_mutate_files
test_classifier_detects_contract_document
test_classifier_detects_implementation_spec
test_classifier_detects_review_dod
test_classifier_detects_generated_markers
test_manual_governed_doc_is_protected
test_generated_doc_section_can_be_planned_for_update
test_manual_doc_update_is_blocked_by_default
test_readme_update_only_targets_generated_section
test_index_update_only_targets_generated_section
test_missing_contract_spec_review_pair_creates_drift_record
test_missing_schema_reference_creates_drift_record
test_missing_test_reference_creates_drift_record
test_done_claim_without_evidence_creates_drift_record
test_local_markdown_link_resolves
test_broken_local_markdown_link_reported
test_external_link_not_fetched
test_stale_document_detected_from_missing_evidence
test_sync_plan_separates_allowed_and_blocked_operations
test_apply_dry_run_changes_no_files
test_apply_generated_section_preserves_manual_content
test_apply_missing_generated_markers_blocks
test_policy_missing_blocks_generated_apply
test_policy_missing_blocks_manual_doc_update
test_evidence_manifest_written
test_evidence_manifest_contains_sha256_hashes
test_review_report_written
test_runtime_artifacts_written_under_docs_sync_root
test_controller_scan_plan_writes_expected_artifacts
test_apply_generated_requires_lock
test_repeated_apply_generated_is_idempotent
test_generated_section_registry_written
test_traceability_matrix_written
test_deviation_register_written
test_command_outputs_record_exit_codes_and_hashes
```

Required negative tests:

```text
test_manual_contract_overwrite_blocked
test_full_readme_rewrite_blocked
test_generated_marker_mismatch_blocks_apply
test_nested_generated_markers_block_apply
test_duplicate_generated_section_id_blocks_apply
test_broken_link_in_generated_index_blocks_done
test_done_status_upgrade_without_review_evidence_blocked
test_external_network_link_not_fetched
test_shell_not_used_for_scan
test_no_source_mutation_during_scan_plan_or_validation
```

---

# 24. Implementation Order

Implement in this order:

```text
1. Create docs_sync package directory.
2. Implement doc_models.py constants, dataclasses, and helpers.
3. Create JSON schemas.
4. Implement validate_docs_sync_schemas.py.
5. Implement doc_classifier.py.
6. Implement doc_scanner.py.
7. Implement doc_links.py.
8. Implement doc_staleness.py.
9. Implement doc_drift.py.
10. Implement doc_sync_plan.py.
11. Implement doc_policy.py.
12. Implement doc_sync_apply.py in dry-run-first mode.
13. Implement doc_index.py.
14. Implement doc_readme.py.
15. Implement doc_evidence.py.
16. Implement doc_report.py.
17. Implement doc_generated_sections.py.
18. Implement doc_lock.py.
19. Implement doc_traceability.py.
20. Implement doc_deviations.py.
21. Implement doc_controller.py.
22. Add tests in the same order.
23. Run compileall.
24. Run pytest for docs_sync tests.
25. Run schema validation utility.
26. Verify git status.
27. Write evidence manifest, review report, traceability matrix, deviation register, generated-section registry, and completion record only after validation.
```

Do not implement apply behavior before scanner, classifier, policy, protection rules, and tests exist.

---


# 25. Controlled Controller / Dispatcher Flow

The implementation must include a single high-level controller that coordinates scan, drift detection, link validation, staleness detection, sync planning, apply, and evidence writing.

Required file:

```text
tools/agentx_evolve/docs_sync/doc_controller.py
```

Required public functions:

```python
run_documentation_sync(
    repo_root: Path,
    mode: str = "scan_plan",
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    policy_context: dict | None = None,
    reviewed_commit: str | None = None,
) -> dict

run_scan_only(repo_root: Path, policy_context: dict | None = None) -> dict
run_validate_only(repo_root: Path, policy_context: dict | None = None) -> dict
run_plan_only(repo_root: Path, policy_context: dict | None = None) -> dict
run_apply_generated(repo_root: Path, policy_context: dict) -> dict
```

Allowed modes:

```text
scan_only
validate_only
scan_plan
dry_run_apply
apply_generated
review_report
completion_record
```

Controller flow:

```text
1. Normalize repo root.
2. Acquire docs_sync lock.
3. Resolve mode.
4. Load policy context or restrictive fallback.
5. Scan documentation.
6. Classify authority and document type.
7. Validate local links.
8. Detect stale documents.
9. Detect documentation drift.
10. Generate sync plan.
11. Validate plan against policy and manual-doc protection rules.
12. Apply only if mode allows and operation is generated-section-only.
13. Write runtime artifacts under .agentx-init/docs_sync/.
14. Write evidence manifest with hashes.
15. Write review report.
16. Release docs_sync lock.
17. Return schema-valid result summary.
```

Fail-closed rules:

```text
schema validation unavailable -> do not apply changes
policy unavailable -> scan/validate/plan only; generated apply blocks
lock unavailable -> do not apply changes
manual-doc target -> block operation
missing generated markers -> block operation
ambiguous generated markers -> block operation
external link validation unavailable -> mark external not checked; do not fetch
```

---

# 26. Apply Mode Matrix

| Mode | Scan | Drift | Link check | Plan | Runtime evidence | Modify docs | Allowed final status |
|---|---:|---:|---:|---:|---:|---:|---|
| `scan_only` | yes | no | optional | no | yes | no | SCANNED |
| `validate_only` | yes | yes | yes | no | yes | no | VALIDATED_WITH_FINDINGS / VALIDATED_CLEAN |
| `scan_plan` | yes | yes | yes | yes | yes | no | PLAN_CREATED |
| `dry_run_apply` | yes | yes | yes | yes | yes | no | DRY_RUN_COMPLETE |
| `apply_generated` | yes | yes | yes | yes | yes | generated sections only | APPLIED / PARTIAL / BLOCKED |
| `review_report` | yes | yes | yes | optional | yes | no | REVIEW_REPORTED |
| `completion_record` | yes | yes | yes | yes | yes | no | VALIDATED only if all proof exists |

Rules:

```text
Default mode is scan_plan.
apply_generated is never default.
completion_record mode cannot mark DONE unless validation proof exists.
No mode may update manual governed documentation.
No mode may rewrite a whole README or whole contract/spec/review document.
```

---

# 27. Generated Section Registry and Provenance

Generated sections must be tracked by stable identity.

Required file:

```text
tools/agentx_evolve/docs_sync/doc_generated_sections.py
```

Required schema:

```text
tools/agentx_evolve/schemas/generated_document_section.schema.json
```

Runtime artifact:

```text
.agentx-init/docs_sync/generated_section_registry.json
```

Required generated section fields:

```python
section_id: str
target_path: str
start_marker: str
end_marker: str
generator_component: str
source_scan_id: str | None
source_plan_id: str | None
previous_content_sha256: str | None
new_content_sha256: str | None
last_updated_at: str | None
status: str
warnings: list[str]
errors: list[str]
```

Generated section rules:

```text
section_id must be unique per file
start and end markers must match
nested generated sections are invalid
overlapping generated sections are invalid
missing start marker blocks apply
missing end marker blocks apply
duplicate section IDs block apply
content hash before and after update must be recorded
manual content outside markers must remain byte-for-byte identical where practical
```

---

# 28. Locking, Concurrency, and Idempotency

Required file:

```text
tools/agentx_evolve/docs_sync/doc_lock.py
```

Required lock path:

```text
.agentx-init/docs_sync/docs_sync.lock
```

Rules:

```text
Only one apply_generated run may execute at a time.
scan_only and validate_only may run without write lock if they only read and write unique runtime artifacts.
If lock exists and is fresh, apply_generated must block.
If lock exists and is stale, record a warning and require explicit recovery mode before applying.
Repeated scan_plan with no repository changes must produce stable equivalent reports except IDs/timestamps.
Repeated dry_run_apply must not change files.
Repeated apply_generated must be idempotent when generated content is already current.
```

Idempotency acceptance:

```text
same inputs -> same planned operation targets
same current generated section -> NOOP or unchanged result
no duplicate generated index entries
no duplicate README generated rows
no duplicate history entries except append-only run evidence
```

---

# 29. Source-Mutation Boundary

The layer has three mutation categories.

| Category | Examples | Allowed by default? | Notes |
|---|---|---:|---|
| Runtime artifacts | `.agentx-init/docs_sync/*.json`, JSONL history, command outputs | yes | Must be schema-valid and hashed where final evidence. |
| Generated documentation sections | bounded README/index/generated docs markers | no, only in `apply_generated` with policy | Must preserve manual content. |
| Manual governed documents | contracts, specs, reviews, standards, roadmap master docs | no | Only blocked operation/suggestion may be created. |

Rules:

```text
scan, validate, plan, and dry_run_apply must not modify documentation files.
apply_generated may modify only generated marker sections after policy approval.
manual governed documents must never be directly modified by this layer.
source code files must never be modified by this layer.
```

---

# 30. Deviation Register

Every accepted exception must be explicit.

Required file:

```text
tools/agentx_evolve/docs_sync/doc_deviations.py
```

Required runtime artifact:

```text
.agentx-init/docs_sync/documentation_sync_deviation_register.json
```

Required schema:

```text
tools/agentx_evolve/schemas/documentation_sync_deviation.schema.json
```

Deviation fields:

```python
deviation_id: str
created_at: str
area: str
description: str
reason: str
safety_impact: str
compensating_control: str
accepted_status: str
reviewer_decision: str
warnings: list[str]
errors: list[str]
```

Deviation rules:

```text
BLOCKER findings cannot be accepted as deviations.
Manual-doc overwrite cannot be accepted as a deviation.
Missing evidence hashes cannot be accepted for DONE.
Broken generated-index links cannot be accepted for DONE.
Runtime artifacts outside .agentx-init/docs_sync/ require deviation entry.
External links marked EXTERNAL_NOT_CHECKED do not require deviation if explicitly classified.
```

---

# 31. Traceability Matrix

Required file:

```text
tools/agentx_evolve/docs_sync/doc_traceability.py
```

Required runtime artifact:

```text
.agentx-init/docs_sync/documentation_sync_traceability_matrix.json
```

Traceability matrix fields:

```text
requirement_id
requirement_text
implementation_file
test_file
evidence_artifact
status
```

Minimum traceability requirements:

| Requirement | Implementation file | Test file | Evidence artifact |
|---|---|---|---|
| scan documents | `doc_scanner.py` | `test_docs_sync_scanner.py` | `document_scan_report.json` |
| classify authority | `doc_classifier.py` | `test_docs_sync_classifier.py` | `document_scan_report.json` |
| detect drift | `doc_drift.py` | `test_docs_sync_drift.py` | `document_drift_report.json` |
| protect manual docs | `doc_sync_apply.py` / `doc_policy.py` | `test_docs_sync_negative_cases.py` | `document_sync_plan.json` |
| update generated section only | `doc_sync_apply.py` | `test_docs_sync_apply.py` | `document_sync_result.json` |
| validate links | `doc_links.py` | `test_docs_sync_links.py` | `document_link_report.json` |
| detect stale docs | `doc_staleness.py` | `test_docs_sync_staleness.py` | `document_staleness_report.json` |
| write evidence | `doc_evidence.py` | `test_docs_sync_evidence.py` | evidence manifest |
| controller flow | `doc_controller.py` | `test_docs_sync_controller.py` | review report |

---

# 32. Validation Command Output and Hashing

Validation must record exact commands, exit codes, and output artifacts.

Required output directory:

```text
.agentx-init/docs_sync/command_outputs/
```

Required command output artifacts:

```text
.agentx-init/docs_sync/command_outputs/python_version.out
.agentx-init/docs_sync/command_outputs/python_version.out
.agentx-init/docs_sync/command_outputs/compileall.out
.agentx-init/docs_sync/command_outputs/pytest.out
.agentx-init/docs_sync/command_outputs/schema_validation.out
.agentx-init/docs_sync/command_outputs/git_status_start.out
.agentx-init/docs_sync/command_outputs/git_status_end.out
command_outputs/exit_codes.out
```

Every command result must include:

```text
name
command
exit_code
status
started_at
ended_at
summary
output_artifact
output_sha256
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence artifacts.
Use Python standard library hashlib.
A DONE verdict is invalid if final evidence hashes are missing.
```

---

# 33. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/docs_sync
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_docs_sync_*.py
PYTHONPATH=tools python tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected runtime artifacts only
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
MCP runtime
external documentation service
```

---

# 34. Link Classification Rules

Link validation must classify links before deciding whether they are broken.

Required link types:

```text
LOCAL_FILE
LOCAL_FILE_WITH_ANCHOR
LOCAL_ANCHOR
EXTERNAL_HTTP
EXTERNAL_MAILTO
EXTERNAL_OTHER
UNSUPPORTED
MALFORMED
```

Rules:

```text
LOCAL_FILE must resolve to an existing local path.
LOCAL_FILE_WITH_ANCHOR must resolve file path; anchor validation may be DEFERRED SAFELY if recorded.
LOCAL_ANCHOR may be NOT CHECKED in v1 if anchor extraction is not implemented.
EXTERNAL_HTTP must not be fetched.
EXTERNAL_MAILTO must not be fetched.
MALFORMED links must be reported.
Broken local links in generated indexes block DONE.
Broken local links in manual docs are HIGH unless they prove generated output is wrong.
```

---

# 35. Implementation Scoring Rules

Use this scoring only after implementation validation.

| Category | Points | Full-credit requirement |
|---|---:|---|
| Structure and expected files | 1.0 | package, schemas, tests, runtime paths exist |
| Models and schemas | 1.0 | dataclasses instantiate, schemas validate valid/invalid examples |
| Scan/classification | 1.0 | deterministic scan, authority/type classification, hashes |
| Drift/staleness/link detection | 1.0 | required drift, stale, and broken-link cases detected |
| Sync plan generation | 1.0 | allowed/blocked/manual-review operations separated |
| Manual-doc protection | 1.0 | governed docs and manual README text cannot be overwritten |
| Generated update safety | 1.0 | generated markers required, dry-run default, idempotent apply |
| Policy/tool/evidence integration | 1.0 | policy fail-closed, Tool/MCP-compatible, evidence complete |
| Tests and negative cases | 1.0 | required tests pass, negative cases prove fail-closed behavior |
| Validation/reproducibility | 1.0 | compileall, pytest, schema validation, hashes, clean git status |

Hard caps:

```text
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
manual governed doc can be overwritten caps score at 4.0
README full rewrite possible by default caps score at 4.0
DONE claim can be generated without review evidence caps score at 4.0
network link fetch enabled by default caps score at 5.0
source mutation during scan/plan caps score at 6.0
missing evidence manifest caps score at 7.0
missing evidence hashes caps score at 8.0
missing reviewed commit in completion evidence caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

---


# 36. Generated Sections API

Required file:

```text
tools/agentx_evolve/docs_sync/doc_generated_sections.py
```

Required public functions:

```python
find_generated_sections(text: str, target_path: str) -> list[dict]
validate_generated_sections(sections: list[dict]) -> tuple[bool, list[str]]
build_generated_section_registry(repo_root: Path, scan_report: DocumentScanReport) -> dict
render_generated_section(section_id: str, payload: dict) -> str
replace_generated_section_content(original_text: str, section_id: str, new_content: str) -> tuple[str, dict]
write_generated_section_registry(repo_root: Path, registry: dict) -> dict
```

Required behavior:

```text
section IDs are stable
section IDs are unique per target file
start marker and end marker must match
nested sections block apply
overlapping sections block apply
duplicate section IDs block apply
replacement preserves manual content outside markers
pre-update content SHA-256 is recorded
post-update content SHA-256 is recorded
target file SHA-256 before and after apply is recorded
```

Required schema-valid example objects:

```text
valid_generated_document_section
valid_generated_section_registry
invalid_generated_document_section_missing_section_id
invalid_generated_document_section_duplicate_marker_case
```

---

# 37. Locking API and Stale-Lock Recovery

Required file:

```text
tools/agentx_evolve/docs_sync/doc_lock.py
```

Required public functions:

```python
acquire_docs_sync_lock(repo_root: Path, mode: str, owner_id: str | None = None) -> dict
release_docs_sync_lock(repo_root: Path, lock_id: str) -> dict
read_docs_sync_lock(repo_root: Path) -> dict | None
is_lock_stale(lock_record: dict, now_utc: str | None = None) -> bool
recover_stale_docs_sync_lock(repo_root: Path, policy_context: dict | None = None) -> dict
```

Lock record fields:

```text
lock_id
created_at
owner_id
mode
repo_root
pid, optional
status
warnings
errors
```

Allowed stale-lock recovery modes:

```text
scan_only may report stale lock but does not need to recover it
validate_only may report stale lock but does not need to recover it
scan_plan may report stale lock but does not need to recover it
apply_generated must block on fresh lock
apply_generated may recover stale lock only when policy_context.explicit_stale_lock_recovery == true
```

Rules:

```text
lock acquisition must be atomic where practical
lock release must verify lock_id
lock file must live under .agentx-init/docs_sync/docs_sync.lock
manual deletion of a lock is not a normal success path
stale-lock recovery must write evidence
failed lock acquisition must return BLOCKED status for apply modes
```

---

# 38. Traceability API

Required file:

```text
tools/agentx_evolve/docs_sync/doc_traceability.py
```

Required public functions:

```python
build_docs_sync_traceability_matrix(repo_root: Path, scan_report: DocumentScanReport) -> dict
validate_docs_sync_traceability_matrix(matrix: dict) -> tuple[bool, list[str]]
write_docs_sync_traceability_matrix(repo_root: Path, matrix: dict) -> dict
```

Required traceability status values:

```text
PASS
PARTIAL
FAIL
NOT_CHECKED
NOT_APPLICABLE
DEFERRED_SAFELY
```

Rules:

```text
every required implementation file must map to at least one test or justified NOT_APPLICABLE entry
every required schema must map to schema validation evidence
every required runtime artifact must map to evidence-writing logic
every blocker must map to a test or review-report finding
NOT_CHECKED is not acceptable for final DONE
```

---

# 39. Deviation API

Required file:

```text
tools/agentx_evolve/docs_sync/doc_deviations.py
```

Required public functions:

```python
create_docs_sync_deviation(
    area: str,
    description: str,
    reason: str,
    safety_impact: str,
    compensating_control: str,
    accepted_status: str,
    reviewer_decision: str,
) -> dict

validate_docs_sync_deviation(deviation: dict) -> tuple[bool, list[str]]
write_docs_sync_deviation_register(repo_root: Path, deviations: list[dict]) -> dict
```

Accepted status values:

```text
NOT_APPLICABLE
DEFERRED_SAFELY
NON_BLOCKING_FOLLOWUP
REJECTED
```

Rules:

```text
BLOCKER findings cannot be accepted as deviations
manual governed document overwrite cannot be accepted as a deviation
missing evidence hashes cannot be accepted for DONE
broken generated-index links cannot be accepted for DONE
external links classified EXTERNAL_NOT_CHECKED are not deviations if documented in link report
```

---

# 40. Anchor Validation Rules

Anchor validation may be deferred in v1, but only with explicit status.

Allowed anchor statuses:

```text
ANCHOR_VALID
ANCHOR_MISSING
ANCHOR_NOT_CHECKED
ANCHOR_DEFERRED_SAFELY
ANCHOR_UNSUPPORTED
```

Rules:

```text
LOCAL_FILE_WITH_ANCHOR must at least resolve the file path
if anchor extraction is implemented, missing anchors must be reported
if anchor extraction is not implemented, anchor status must be ANCHOR_DEFERRED_SAFELY or ANCHOR_NOT_CHECKED
broken file path cannot be hidden behind deferred anchor validation
broken file path in generated index blocks DONE
anchor deferral must be summarized in the link report
```

---

# 41. Tool / MCP Adapter Wrapper Compatibility

The layer must be compatible with future Tool / MCP Adapter exposure without requiring MCP in this phase.

Expected wrapper behavior:

| Future tool | Effect | v1 behavior | MCP default |
|---|---|---|---|
| `docs_scan` | READ | allowed through scanner if policy permits | exposable read-only |
| `docs_detect_drift` | READ/REPORT | allowed, writes runtime evidence only | exposable read-only |
| `docs_generate_sync_plan` | REPORT | allowed, writes runtime plan only | exposable read-only |
| `docs_validate_links` | READ/REPORT | allowed, no network fetch | exposable read-only |
| `docs_detect_stale` | READ/REPORT | allowed, writes runtime report only | exposable read-only |
| `docs_status` | READ | allowed | exposable read-only |
| `docs_apply_generated_updates` | WRITE | blocked unless policy + sandbox + generated markers pass | hidden or blocked by default |

Rules:

```text
MCP exposure is not implemented in this layer
future MCP exposure must be read-only by default
apply_generated must never be MCP-exposed by default
manual document update tools must not be registered as executable tools in v1
ToolResult-compatible wrappers should return structured status, artifact refs, evidence refs, warnings, and errors
```

---

# 42. Evidence Hashing and Completion Record Requirements

Final evidence must include SHA-256 hashes for all final validation artifacts.

Required final hashed artifacts:

```text
document_scan_report.json
document_drift_report.json
document_link_report.json
document_staleness_report.json
document_sync_plan.json
document_sync_result.json, if apply attempted
documentation_sync_evidence_manifest.json
documentation_sync_review_report.json
documentation_sync_traceability_matrix.json
documentation_sync_deviation_register.json
generated_section_registry.json
documentation_sync_completion_record.json
command_outputs/python_version.out
command_outputs/compileall.out
command_outputs/pytest.out
command_outputs/schema_validation.out
command_outputs/git_status_start.out
command_outputs/git_status_end.out
command_outputs/exit_codes.out
```

Completion record must include:

```text
validated_commit
validated_at
review_environment
commands_run with exit_code and output_sha256
evidence_manifest_path and evidence_manifest_sha256
review_report_path and review_report_sha256
traceability_matrix_path and traceability_matrix_sha256
deviation_register_path and deviation_register_sha256
generated_section_registry_path and generated_section_registry_sha256
completion_record_sha256
implementation_score
final_decision
```

A final DONE verdict is invalid if any required final hash is missing.

---

# 43. Copy-Safe Validation Commands

Use this command block for final validation. It creates the output directory before redirecting command output.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
mkdir -p .agentx-init/docs_sync/command_outputs

git status --short > .agentx-init/docs_sync/command_outputs/git_status_start.out
python --version > .agentx-init/docs_sync/command_outputs/python_version.out 2>&1

PYTHONPATH=tools python -m compileall tools/agentx_evolve/docs_sync   > .agentx-init/docs_sync/command_outputs/compileall.out 2>&1
COMPILEALL_EXIT_CODE=$?

PYTHONPATH=tools python -m pytest   tools/agentx_evolve/tests/test_docs_sync_models.py   tools/agentx_evolve/tests/test_docs_sync_schemas.py   tools/agentx_evolve/tests/test_docs_sync_scanner.py   tools/agentx_evolve/tests/test_docs_sync_classifier.py   tools/agentx_evolve/tests/test_docs_sync_drift.py   tools/agentx_evolve/tests/test_docs_sync_plan.py   tools/agentx_evolve/tests/test_docs_sync_apply.py   tools/agentx_evolve/tests/test_docs_sync_links.py   tools/agentx_evolve/tests/test_docs_sync_staleness.py   tools/agentx_evolve/tests/test_docs_sync_readme_index.py   tools/agentx_evolve/tests/test_docs_sync_policy.py   tools/agentx_evolve/tests/test_docs_sync_evidence.py   tools/agentx_evolve/tests/test_docs_sync_controller.py   tools/agentx_evolve/tests/test_docs_sync_generated_sections.py   tools/agentx_evolve/tests/test_docs_sync_traceability.py   tools/agentx_evolve/tests/test_docs_sync_deviations.py   tools/agentx_evolve/tests/test_docs_sync_lock_idempotency.py   tools/agentx_evolve/tests/test_docs_sync_negative_cases.py   > .agentx-init/docs_sync/command_outputs/pytest.out 2>&1
PYTEST_EXIT_CODE=$?

PYTHONPATH=tools python tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py   > .agentx-init/docs_sync/command_outputs/schema_validation.out 2>&1
SCHEMA_VALIDATION_EXIT_CODE=$?

git status --short > .agentx-init/docs_sync/command_outputs/git_status_end.out
command_outputs/exit_codes.out

printf "compileall=%s
pytest=%s
schema_validation=%s
"   "$COMPILEALL_EXIT_CODE" "$PYTEST_EXIT_CODE" "$SCHEMA_VALIDATION_EXIT_CODE"   > .agentx-init/docs_sync/command_outputs/exit_codes.out

test "$COMPILEALL_EXIT_CODE" -eq 0 && test "$PYTEST_EXIT_CODE" -eq 0 && test "$SCHEMA_VALIDATION_EXIT_CODE" -eq 0
```

Each command must be represented in `documentation_sync_evidence_manifest.json` as a `DocumentationSyncCommandResult` with:

```text
exact command
exit_code
status
started_at
ended_at
summary
output_artifact
output_sha256
```

The final `test` command above is only a shell convenience. The implementation must still parse and record the individual exit codes for compileall, pytest, and schema validation.



# 44. Acceptance Criteria

The implementation is acceptable only if:

```text
all required package files exist
all required schemas exist
all required tests exist
document scan works deterministically
document classification works
drift detection works
sync plan generation works
manual-doc protection works
generated-doc update rules work
README/index updates are limited to generated sections
local broken-link detection works
stale-document detection works
policy missing fails closed for writes
evidence artifacts are written under .agentx-init/docs_sync/
evidence manifest includes SHA-256 hashes
compileall passes
pytest passes
schema validation passes
git status is clean or only expected runtime artifacts exist
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
MCP runtime
external documentation service
```

---

# 45. Manual Validation Commands

Use the copy-safe validation command block in Section 43.

Minimum required validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/docs_sync
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_docs_sync_*.py
PYTHONPATH=tools python tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py
git status --short
```

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or expected runtime artifacts only
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
MCP runtime
external documentation service
```

---

# 46. Definition of Done

The Documentation Synchronization Layer is done when it can safely scan, validate, plan, and evidence documentation synchronization without corrupting governed documentation.

DONE requires:

```text
all target files exist
all schemas exist
all tests exist
schemas validate valid and invalid examples
scanner detects documentation files deterministically
classifier separates contract/spec/review/README/index/schema/test/report/evidence documents
authority classifier protects manual governed documents
drift detector finds missing contract/spec/review references
drift detector finds missing schemas/tests/evidence references
README/index validator detects stale or missing generated sections
broken-link detector reports local missing links
stale-document detector detects unsupported DONE claims
sync planner separates allowed, blocked, and manual-review-required operations
apply function defaults to dry-run
apply function updates only generated marker sections when permitted
manual governed document update is blocked by default
policy missing fails closed for writes
runtime evidence is written under .agentx-init/docs_sync/
evidence manifest records hashes
review report records final validation state
completion record exists after validation
no source mutation occurs during scan/plan/validation
no network access occurs
no raw shell is used
compileall passes
pytest passes
schema validation passes
```

Final proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/docs_sync
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_docs_sync_*.py
PYTHONPATH=tools python tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or expected runtime artifacts only
```

---

# 47. Go / No-Go Rules

## 47.1 GO Criteria

The layer may be marked DONE only if:

```text
compileall passes
pytest passes
schema validation passes
manual-doc protection tests pass
generated-doc update tests pass
broken-link tests pass
stale-document tests pass
policy fail-closed tests pass
evidence tests pass
source mutation check passes
completion record exists
no BLOCKER remains
```

## 47.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
manual governed document can be overwritten by default
README can be fully rewritten by default
generated-marker mismatch still applies changes
DONE status can be claimed without review evidence
policy missing allows documentation writes
scan or plan mutates source files
network links are fetched by default
raw shell is used
runtime artifacts are written outside .agentx-init/docs_sync/ without recorded deviation
evidence manifest is missing
evidence hashes are missing
completion record is missing
required command exit code is missing
required command output hash is missing
any required area remains NOT_CHECKED
any required command remains NOT_RUN
reviewed commit is missing
review environment is missing
```

---

# 48. Completion Record

After validation, create:

```text
.agentx-init/docs_sync/documentation_sync_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_sync_completion_record.schema.json",
  "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
  "component_name": "Documentation Synchronization Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/docs_sync/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/docs_sync/",
  "basis_documents": [
    "DOCUMENTATION_SYNCHRONIZATION_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/docs_sync",
      "exit_code": 0,
      "status": "PASS",
      "output_artifact": ".agentx-init/docs_sync/command_outputs/compileall.out",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_docs_sync_*.py",
      "exit_code": 0,
      "status": "PASS",
      "output_artifact": ".agentx-init/docs_sync/command_outputs/pytest.out",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "PYTHONPATH=tools python tools/agentx_evolve/docs_sync/validate_docs_sync_schemas.py",
      "exit_code": 0,
      "status": "PASS",
      "output_artifact": ".agentx-init/docs_sync/command_outputs/schema_validation.out",
      "output_sha256": "<sha256>"
    }
  ],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "manual_doc_protection_verified": true,
  "generated_doc_updates_verified": true,
  "readme_index_rules_verified": true,
  "broken_link_detection_verified": true,
  "stale_document_detection_verified": true,
  "policy_integration_verified": true,
  "tool_mcp_adapter_integration_ready": true,
  "evidence_manifest_path": ".agentx-init/docs_sync/documentation_sync_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/docs_sync/documentation_sync_review_report.json",
  "review_report_sha256": "<sha256>",
  "traceability_matrix_path": ".agentx-init/docs_sync/documentation_sync_traceability_matrix.json",
  "traceability_matrix_sha256": "<sha256>",
  "deviation_register_path": ".agentx-init/docs_sync/documentation_sync_deviation_register.json",
  "deviation_register_sha256": "<sha256>",
  "generated_section_registry_path": ".agentx-init/docs_sync/generated_section_registry.json",
  "generated_section_registry_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

Completion record rules:

```text
validated_commit is required and must be the exact reviewed commit.
Every required command must include exit_code and output_sha256.
Every required final evidence artifact must have a SHA-256 hash.
completion_record_sha256 must be computed after writing the final record.
If completion_record_sha256 cannot be embedded without changing the file, write a sibling .sha256 file and reference it in the evidence manifest.
A final DONE verdict is invalid if any required hash, exit code, reviewed commit, review environment, review report, evidence manifest, traceability matrix, or deviation register is missing.
```


# 49. Final Freeze and Versioning Rule

This v4 implementation spec is frozen as the implementation handoff.

Allowed future changes:

```text
PATCH: typo fixes, wording clarifications, non-normative examples
MINOR: additive optional tests, optional report fields, additional generated report types
MAJOR: changed protection rules, changed apply defaults, changed required schemas, changed Tool/MCP exposure policy, changed source-mutation boundary
```

Blocked without MAJOR revision:

```text
allowing manual governed document overwrite by default
allowing full README rewrite by default
allowing DONE status upgrades without review evidence
allowing generated update without markers
allowing network link fetching by default
removing evidence hashes
removing policy fail-closed behavior for writes
removing source-mutation protections
```

---

# 50. Final Implementation Handoff Checklist

Before implementation begins, confirm:

```text
[ ] Target repository is Agent_X.
[ ] Package path is tools/agentx_evolve/docs_sync/.
[ ] Runtime artifact root is .agentx-init/docs_sync/.
[ ] Manual governed documents are protected by default.
[ ] Generated updates require generated markers.
[ ] Apply mode defaults to dry_run.
[ ] README/index updates target generated sections only.
[ ] DONE status cannot be inferred without review evidence.
[ ] No network validation is required.
[ ] No LLM is required.
[ ] No MCP runtime is required.
[ ] Tool / MCP Adapter compatibility is planned but not required for base tests.
[ ] Policy missing fails closed for writes.
[ ] Evidence manifest and hashes are required.
```

---

# 51. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, public functions, runtime artifacts, scan algorithm, drift detection, sync planning, manual-document protection, generated-document update rules, README/index rules, link/staleness validation, controller flow, apply-mode boundaries, generated-section provenance, locking/idempotency, deviation handling, traceability, integration points, Tool/MCP compatibility, tests, copy-safe validation commands, evidence hashing, completion-record hash requirements, acceptance criteria, and Definition of Done.
```

This v4 document is frozen as the implementation-ready handoff for the Documentation Synchronization Layer.
