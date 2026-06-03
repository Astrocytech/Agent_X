# DOCUMENTATION_SYNCHRONIZATION_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: DOCUMENTATION_SYNCHRONIZATION_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready, v4 precision upgrade
component_id: AGENTX_DOCUMENTATION_SYNCHRONIZATION
component_name: Documentation Synchronization Layer
roadmap_layer: 17
roadmap_phase: Phase D — Documentation / Traceability / Drift Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Report Template
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria if exposed through MCP
optional_standards: ES, only for ecosystem placement
risk_level: high
implementation_mode: controlled documentation scan, drift detection, coverage reporting, and governed synchronization
operation_mode: scan/report first; repository writes only for approved generated documentation paths
target_language: Python
canonical_subdirectory: tools/agentx_evolve/docs_sync/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/docs_sync/
previous_version_rating: 9.8/10
contract_rating: 10/10
next_document: DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC
```

---

# 0. v4 Review and Upgrade Summary

The v3 contract was strong and close to final. I would rate v3:

```text
9.8/10
```

It already covered the required contract areas:

```text
EQC
FIC
SIB
Schema Contract
Documentation Scope Contract
Documentation Source-of-Truth Rules
Documentation Drift Rules
Generated-vs-Manual Documentation Rules
Documentation Sync Decision Schema
Documentation Change Record Schema
Documentation Coverage Matrix
Documentation Evidence / Audit Contract
Agent_X integration notes
OpenCode borrowing notes
execution modes
claim taxonomy
lineage / freshness rules
manual proposal contract
review report and completion record contract
locking and idempotency
```

It was not fully 10/10 because several final production-control details still needed to be explicit enough for implementation and later review:

```text
1. It needed a stricter repository scan-scope contract, including include/exclude rules and symlink handling.
2. It needed a stronger document identity rule so duplicate document_id, filename-only matching, and renamed docs cannot create false continuity.
3. It needed an explicit read-only validation mode for CI and review checks.
4. It needed canonical link-resolution rules for relative anchors, generated reports, and external links.
5. It needed stronger tamper-evidence and SHA-256 requirements for histories, reports, proposals, and final evidence.
6. It needed clearer deletion/archival rules so missing documents are not silently removed from indexes.
7. It needed explicit command-proof requirements with command text, exit code, status, output artifact, and hash.
8. It needed safer rules for README/status updates, especially when generated output proposes status text.
9. It needed stricter approval boundaries for repository writes through Tool / MCP Adapter tools.
10. It needed review scoring hard caps to prevent a layer from being rated DONE when evidence is incomplete.
```

This v4 applies those corrections and is the final 10/10 controlling contract for the Documentation Synchronization Layer.
---

# 1. Purpose

This document defines the controlling contract for the **Documentation Synchronization Layer** in the Agent_X self-evolving system.

This layer keeps Agent_X documentation aligned with implementation, schemas, tests, roadmap state, review evidence, and generated reports without silently rewriting governed human-authored documents.

The layer defines:

```text
what documentation may be scanned
what documentation may be generated
what documentation may be synchronized automatically
what documentation requires proposal-only handling
what documentation requires human approval before update
what documentation must never be overwritten automatically
how documentation drift is detected
how generated documentation is separated from manual documentation
how documentation source-of-truth is determined
how documentation sync decisions are recorded
how documentation change records are written
how documentation coverage is measured
how broken references and stale status are reported
how evidence proves that synchronization was safe
```

The layer must prevent documentation from becoming a false source of authority. It must not claim that a feature, layer, tool, schema, test, or roadmap item is complete unless the required evidence exists.

---

# 2. Why This Layer Is Safety-Critical

Documentation Synchronization is safety-critical because Agent_X uses documents as:

```text
architecture contracts
implementation handoffs
coding-agent instructions
schema contracts
review gates
Definition of Done records
roadmap state records
release evidence
future-agent context
```

If documentation becomes stale or inaccurate, later agents may:

```text
implement against the wrong contract
skip safety gates
believe a layer is DONE when it is not
trust stale schema information
call tools that should be blocked
expose incomplete MCP behavior
ignore missing tests
misread roadmap status
overwrite manual design decisions
promote incomplete work
```

Therefore this layer must fail closed, protect manual governed documents, write evidence, and keep generated material clearly separated from authoritative contracts.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because documentation synchronization affects system correctness, safety, reproducibility, and promotion decisions.

The layer must ensure:

```text
documentation updates are evidence-backed
drift detection is deterministic
DONE status is not invented by documentation sync
manual contracts are protected
sync output is auditable
schema references are checked
cross-references are checked
generated documents are clearly marked
unsafe rewrites are blocked
status claims are tied to completion records
```

A sync operation must never make the repository appear safer, more complete, or more validated than the evidence proves.

## 3.2 Required Supporting Standard: FIC

FIC is required because the layer has concrete implementation files.

Expected files include:

```text
tools/agentx_evolve/docs_sync/__init__.py
tools/agentx_evolve/docs_sync/doc_models.py
tools/agentx_evolve/docs_sync/doc_registry.py
tools/agentx_evolve/docs_sync/doc_scanner.py
tools/agentx_evolve/docs_sync/doc_classifier.py
tools/agentx_evolve/docs_sync/source_of_truth.py
tools/agentx_evolve/docs_sync/drift_detector.py
tools/agentx_evolve/docs_sync/sync_planner.py
tools/agentx_evolve/docs_sync/sync_executor.py
tools/agentx_evolve/docs_sync/link_checker.py
tools/agentx_evolve/docs_sync/coverage_matrix.py
tools/agentx_evolve/docs_sync/doc_evidence.py
tools/agentx_evolve/docs_sync/report_writer.py
```

Each file must have:

```text
clear responsibility
public API
inputs
outputs
invariants
failure behavior
safety limits
tests
```

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects documentation to multiple Agent_X subsystems:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution Layer
Tool / MCP Adapter Layer
Failure Taxonomy / Recovery Playbook
Model Adapter Layer
Prompt Contract / Prompt Versioning Layer
Evaluation Harness / Regression Benchmark Layer
Promotion / Release Gate
Git Integration Layer
Monitoring / Observability Layer
Packaging / Distribution Layer
Backup / Disaster Recovery Layer
```

The layer is an integration boundary. It must not operate as a standalone markdown formatter.

## 3.4 Required Schema Contract

Schema Contract is required because scan results, drift decisions, sync decisions, change records, coverage matrices, link checks, and evidence records must be machine-checkable.

Required schemas:

```text
documentation_registry.schema.json
documentation_source.schema.json
documentation_scope.schema.json
documentation_source_of_truth.schema.json
documentation_drift_record.schema.json
documentation_sync_decision.schema.json
documentation_change_record.schema.json
documentation_coverage_matrix.schema.json
documentation_link_check.schema.json
documentation_sync_report.schema.json
documentation_evidence_manifest.schema.json
documentation_review_report.schema.json
documentation_completion_record.schema.json
documentation_deviation.schema.json
documentation_lineage.schema.json
documentation_claim.schema.json
documentation_scan_scope.schema.json
documentation_document_identity.schema.json
documentation_command_proof.schema.json
documentation_tamper_evidence.schema.json
```

## 3.5 Required Evidence / Audit Rules

Evidence is required for:

```text
document scan
document classification
source-of-truth decision
drift detection
link validation
coverage matrix generation
sync plan generation
manual-doc protection decision
generated-doc update decision
blocked overwrite
proposal creation
runtime artifact creation
final sync report
```

## 3.6 Required Report Template

Report Template is required because this layer writes markdown or JSON reports.

Reports must distinguish:

```text
observed documentation state
inferred drift
source-of-truth references
proposed sync changes
executed sync changes
blocked changes
manual review needed
unsupported or unsafe changes
remaining drift
```

## 3.7 Conditional Standards

Use Command Acceptance Criteria if this layer exposes CLI commands.

Use MCP Protocol Acceptance Criteria only if this layer is exposed through MCP.

## 3.8 Optional Standard: ES

ES may be used only for ecosystem placement, such as identifying where this layer fits in the Agent_X architecture and roadmap.

---

# 4. Scope

## 4.1 Required in This Layer

This layer must define and implement contracts for:

```text
document discovery
document classification
document source-of-truth mapping
documentation drift detection
generated-vs-manual document separation
documentation sync planning
documentation sync execution under policy
broken-link detection
cross-reference validation
roadmap status alignment
contract/spec/review triad alignment
schema index alignment
test coverage summary alignment
documentation coverage matrix generation
documentation evidence logging
documentation sync report writing
manual update proposal creation
```

## 4.2 Not Required in This Layer

This layer must not implement:

```text
LLM document authoring as an authority
unreviewed architectural changes
source code generation
schema generation without policy
promotion decisions
release decisions
Git commit/push behavior
MCP runtime server
human approval UI
background daemon
external website publishing
```

This layer synchronizes documentation state. It does not decide product direction, approve architecture changes, or mark layers complete without evidence.

---

# 5. Execution Modes

The layer must support explicit execution modes. A sync request must declare one mode, and the mode must be recorded in every scan result, sync decision, change record, evidence manifest, and report.

Allowed modes:

```text
SCAN_ONLY
REPORT_ONLY
PROPOSE_ONLY
GENERATE_RUNTIME_ONLY
UPDATE_GENERATED_DOCS
GOVERNED_MANUAL_PROPOSAL
```

Mode rules:

```text
SCAN_ONLY may read approved documentation paths and write runtime evidence only.
REPORT_ONLY may write runtime reports under .agentx-init/docs_sync/ only.
PROPOSE_ONLY may create proposal artifacts but must not update repository docs.
GENERATE_RUNTIME_ONLY may generate reports under runtime artifact root only.
UPDATE_GENERATED_DOCS may update approved generated paths only after policy and sandbox approval.
GOVERNED_MANUAL_PROPOSAL may create proposals for manual governed documents, but actual repository changes must route through Governed Patch Execution.
```

Default mode:

```text
SCAN_ONLY
```

If the mode is missing, invalid, or ambiguous, the layer must return:

```text
BLOCKED
```

---

# 6. Status Vocabulary

Use only these status values in documentation sync records:

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
NEEDS_REVIEW
PROPOSE_ONLY
BLOCKED
DEFERRED SAFELY
```

Use only these sync decision values:

```text
ALLOW
BLOCK
NEEDS_REVIEW
PROPOSE_ONLY
NOOP
```

Use only these sync action values:

```text
SCAN
REPORT
GENERATE
UPDATE
PROPOSE
BLOCK
NOOP
```

Decision precedence:

```text
BLOCK
NEEDS_REVIEW
PROPOSE_ONLY
ALLOW
NOOP
```

If two rules conflict, the stricter decision wins.

---

# 7. Documentation Scope Contract

## 6.1 Documentation Categories

The layer must classify documentation into categories:

```text
MANUAL_GOVERNED_CONTRACT
MANUAL_IMPLEMENTATION_SPEC
MANUAL_REVIEW_DOD
MANUAL_ARCHITECTURE_DECISION
MANUAL_ROADMAP
GENERATED_INDEX
GENERATED_STATUS_REPORT
GENERATED_COVERAGE_REPORT
GENERATED_SCHEMA_INDEX
GENERATED_TEST_SUMMARY
GENERATED_LINK_REPORT
GENERATED_DRIFT_REPORT
RUNTIME_EVIDENCE_REPORT
README_OR_OVERVIEW
CHANGELOG_OR_RELEASE_NOTE
UNKNOWN_DOCUMENT
```

## 6.2 Manual Governed Documents

Manual governed documents include:

```text
EQC / FIC / SIB contracts
implementation specs
review / Definition of Done templates
roadmap layer contracts
policy documents
security contracts
architecture decisions
human-approved design notes
manual roadmap files
```

Rules:

```text
manual governed documents must not be overwritten automatically
manual governed documents may be scanned and referenced
manual governed documents may receive generated companion reports only
changes to manual governed documents require explicit proposal path
sync layer may propose changes but must not apply them automatically
manual governed documents are protected even if they lack a protection marker
```

## 6.3 Generated Documents

Generated documents include:

```text
index files
coverage summaries
schema indexes
test summaries
cross-reference maps
drift reports
sync reports
runtime evidence summaries
link reports
```

Rules:

```text
generated documents must be clearly marked as generated
generated documents may be updated automatically only under approved generated paths
generated documents must list source inputs and generation timestamp
generated documents must include source input hashes
generated documents must not replace manual governed documents
generated documents must not claim DONE without review evidence
```

## 6.4 Unknown Documents

Unknown documents must be treated cautiously.

Rules:

```text
unknown documents may be scanned
unknown documents may not be overwritten automatically
unknown documents must be classified before sync
ambiguous classification returns NEEDS_REVIEW
```

---

# 8. Protected Path and Generated Path Boundary

## 7.1 Protected Paths

Automatic updates are blocked for:

```text
contracts/
specs/
reviews/
docs/architecture/
docs/contracts/
docs/specs/
docs/reviews/
README.md
layer controlling documents
manual roadmap files
any file classified as MANUAL_GOVERNED_CONTRACT
any file classified as MANUAL_IMPLEMENTATION_SPEC
any file classified as MANUAL_REVIEW_DOD
```

README updates are blocked unless explicitly approved by Policy / Capability Registry and routed through Governed Patch Execution.

## 7.2 Approved Generated Paths

Automatic generated updates may occur only under:

```text
.agentx-init/docs_sync/
docs/generated/
docs/indexes/generated/
docs/reports/generated/
docs/schema_indexes/generated/
docs/test_summaries/generated/
```

## 7.3 Deviation Requirement

Any write outside approved generated paths must be recorded as a deviation and must require:

```text
policy approval
sandbox approval
governed patch execution path
human approval if the target is manual governed
```

No deviation can authorize silent overwrite of a manual governed document.

---

# 8.5 Repository Scan Scope and Document Identity Contract

## 9.1 Scan Scope Rules

Every scan must use an explicit scope object. The scope object must identify:

```text
repo_root
target_commit, if available
include_globs
exclude_globs
follow_symlinks
max_file_size_bytes
allowed_document_extensions
allowed_runtime_roots
restricted_paths
mode
```

Default include globs:

```text
README.md
docs/**/*.md
docs/**/*.txt
L*/**/*.md
L*/**/*.yaml
tools/**/docs/**/*.md
tools/agentx_evolve/schemas/*.json
tools/agentx_evolve/tests/test_*.py
.agentx-init/**/completion_record.json
.agentx-init/**/review_report.json
.agentx-init/**/evidence_manifest.json
```

Default exclude globs:

```text
.git/**
.venv/**
venv/**
__pycache__/**
node_modules/**
dist/**
build/**
.coverage
.pytest_cache/**
.agentx-init/**/tmp/**
large binary files
unknown binary files
```

Symlink rules:

```text
symlinks must not be followed by default
symlinks that resolve outside repo_root are BLOCKED
symlink targets must be recorded if symlink scanning is explicitly enabled
symlink loops must return BLOCKED or NEEDS_REVIEW
```

Path normalization rules:

```text
all paths must be normalized relative to repo_root
absolute paths must not be persisted unless redacted or explicitly allowed
path traversal attempts must be BLOCKED
case-sensitive and case-insensitive collisions must be detected when relevant
```

## 9.2 Document Identity Rules

A document identity must not rely on filename alone. Identity should be derived from:

```text
document_id metadata, when present
canonical relative path
component_id, when present
document type
version
content hash
lineage_id for generated documents
```

Duplicate identity handling:

```text
duplicate document_id in governed docs -> BLOCKER drift
duplicate document_id in generated docs -> HIGH drift unless lineage proves supersession
same title with different document_id -> NEEDS_REVIEW
same document_id with conflicting component_id -> BLOCKER drift
same document_id with changed path -> NEEDS_REVIEW unless rename mapping proves continuity
```

Rename and move continuity requires:

```text
old path
new path
before hash
after hash
reason
source evidence
approval or recorded migration decision
```

The layer must never treat a new file with a familiar filename as the same governed document without identity evidence.

## 9.3 Deletion and Archive Rules

Deleted or missing documents must not be silently removed from generated indexes.

Required behavior:

```text
required governed document missing -> MISSING_DOCUMENT drift
missing completion evidence for DONE layer -> BLOCKER drift
missing generated report -> INFO or HIGH depending on impact
archived document must be marked archived and excluded from current authority
deleted document references remain in drift report until resolved
```

Generated indexes may remove deleted generated documents only when:

```text
source scan proves absence
lineage or prior record proves the document was generated
removal is recorded in a change record
coverage matrix records the impact
```

---

# 9. Documentation Source-of-Truth Rules

## 8.1 Source-of-Truth Hierarchy

The layer must determine source-of-truth using this hierarchy:

```text
1. Final review / DoD evidence and completion records
2. Evidence manifests and command outputs from validation
3. Controlling contract documents
4. Implementation specs
5. Actual code files
6. Actual schema files
7. Actual test files and test outputs
8. Runtime evidence manifests
9. Generated reports and indexes
10. README / overview files
```

Generated reports and README files are not primary authority for implementation completeness.

## 8.2 DONE Status Rule

A document may show a layer as DONE only when evidence exists from:

```text
review / DoD report
completion record
validated commit
validation commands with exit codes
schema validation
pytest or equivalent test proof
evidence manifest
source mutation check
```

If this evidence is missing, documentation sync must use one of:

```text
NOT DONE
IMPLEMENTED_UNVALIDATED
PARTIAL
UNKNOWN
```

## 8.3 Stale Evidence Rule

Evidence is stale if:

```text
it does not identify a reviewed commit
it refers to a different commit than the target documentation status
it lacks command exit codes
it lacks schema validation status
it lacks source mutation status
it has been modified after sign-off without a new review report
```

Stale evidence must not support DONE status.

## 8.4 Conflict Resolution

When documents conflict, the layer must not silently choose the most optimistic value.

Decision rule:

```text
completion evidence beats README status
review report beats roadmap claim
contract beats generated summary
actual schema files beat stale schema index
actual tests beat stale test summary
latest validated evidence beats older report
manual governed contract beats generated index
```

If conflict remains unresolved, return:

```text
SYNC_DECISION = NEEDS_REVIEW
```

---

# 10. Documentation Claim Taxonomy

The layer must classify documentation claims before synchronizing or reporting them.

Claim types:

```text
EXISTENCE_CLAIM
STATUS_CLAIM
DONE_CLAIM
TEST_COVERAGE_CLAIM
SCHEMA_COVERAGE_CLAIM
SECURITY_CLAIM
MCP_EXPOSURE_CLAIM
POLICY_PERMISSION_CLAIM
IMPLEMENTATION_LOCATION_CLAIM
ROADMAP_POSITION_CLAIM
```

Claim authority rules:

```text
DONE_CLAIM requires review report, completion record, validated commit, command exit codes, schema validation, pytest or equivalent proof, and source mutation check.
TEST_COVERAGE_CLAIM requires actual test files or test output evidence.
SCHEMA_COVERAGE_CLAIM requires actual schema files or schema validation evidence.
SECURITY_CLAIM requires the relevant contract or validation evidence.
MCP_EXPOSURE_CLAIM requires Tool / MCP Adapter evidence or explicit safe-deferral evidence.
ROADMAP_POSITION_CLAIM may come from roadmap documents, but DONE status still requires completion evidence.
```

Unsupported claim handling:

```text
unsupported DONE claim -> BLOCKER drift
unsupported safety claim -> HIGH or BLOCKER drift depending on impact
unsupported coverage claim -> HIGH drift
unsupported location claim -> MEDIUM drift unless it blocks implementation lookup
```

A generated document must not upgrade a claim. It may only reproduce a claim when the required source evidence exists.

## 10.1 Status Text Update Rule

README, roadmap, and status-summary text must be treated as claim-bearing content.

Rules:

```text
generated status text may propose wording, but must not directly update README.md by default
status upgrades require completion evidence and reviewed commit
status downgrades caused by missing evidence may be reported without modifying manual docs
manual status documents require proposal-only handling unless Governed Patch Execution applies the change
```

A generated report may say:

```text
"Evidence indicates DONE" only when all DONE evidence exists.
"Documentation claims DONE but evidence is missing" when drift is detected.
```

A generated report must not say:

```text
"DONE" based only on a README, roadmap, generated index, or implementation spec.
```

---

# 11. Documentation Drift Rules

## 9.1 Drift Types

The layer must detect:

```text
MISSING_DOCUMENT
STALE_DOCUMENT
ORPHAN_DOCUMENT
BROKEN_REFERENCE
BROKEN_LINK
MISSING_SCHEMA_REFERENCE
MISSING_TEST_REFERENCE
MISSING_EVIDENCE_REFERENCE
STATUS_CONFLICT
DONE_WITHOUT_EVIDENCE
CONTRACT_SPEC_MISMATCH
SPEC_CODE_MISMATCH
SCHEMA_CODE_MISMATCH
TEST_DOC_MISMATCH
GENERATED_DOC_OUTDATED
MANUAL_DOC_CHANGED_WITHOUT_REVIEW
UNKNOWN_DOCUMENT_CLASSIFICATION
SOURCE_OF_TRUTH_CONFLICT
PROTECTED_PATH_WRITE_ATTEMPT
GENERATED_DOC_MISSING_MARKER
EVIDENCE_HASH_MISMATCH
```

## 9.2 Drift Severity

Use these severity levels:

```text
BLOCKER
HIGH
MEDIUM
LOW
INFO
```

BLOCKER drift includes:

```text
README claims DONE without completion evidence
roadmap claims DONE without review report
manual governed contract overwritten by generated sync
schema index contradicts actual schemas
review / DoD document references missing validation evidence
broken cross-reference prevents locating controlling contract
protected path write attempted automatically
evidence hash mismatch for a DONE claim
```

HIGH drift includes:

```text
implementation spec missing from layer index
schema file missing from schema index
test file missing from coverage summary
outdated generated report used as current evidence
unknown document under governed document path
generated document missing generated marker
```

MEDIUM drift includes:

```text
broken non-critical internal link
stale generated index
missing optional report summary
unclear document classification
```

LOW drift includes:

```text
formatting mismatch
minor title mismatch
old generated timestamp with no status impact
```

INFO includes:

```text
new document detected
new schema detected
new test detected
index can be refreshed
```

## 9.3 Drift Handling

```text
BLOCKER drift blocks automatic sync and requires review.
HIGH drift may allow generated report creation but blocks DONE claims.
MEDIUM drift may be recorded and optionally corrected if in generated docs.
LOW drift may be corrected only in generated docs.
INFO may be recorded without changing files.
```

---

# 12. Generated-vs-Manual Documentation Rules

## 10.1 Generated Document Marker

Every generated document must include this marker near the top:

```text
<!-- GENERATED BY AGENT_X DOCUMENTATION SYNCHRONIZATION. DO NOT EDIT MANUALLY. -->
```

It must also include:

```text
generated_at
generator_component
generator_version
source_inputs
source_input_hashes
review_status
validated_commit, if status is claimed
```

## 10.2 Manual Document Protection Marker

Manual governed documents may include:

```text
<!-- AGENT_X MANUAL GOVERNED DOCUMENT. DO NOT OVERWRITE BY DOC SYNC. -->
```

If absent, classification must still protect documents based on:

```text
path
metadata
document_id
section structure
document category
contract/spec/review naming
```

## 10.3 Idempotency Rule

Repeated sync runs with the same inputs must produce:

```text
the same generated content except timestamp fields explicitly allowed to change
the same classification results
the same drift decisions
the same source input hashes
the same proposed manual changes
no duplicate JSONL records for the same idempotent operation unless run_id differs
```

Generated content should be stable and deterministic.

## 10.4 Manual Change Proposals

For manual governed documents, the layer may create proposed changes under:

```text
.agentx-init/docs_sync/proposals/
```

Proposals must include:

```text
target file
reason for proposed change
source evidence
before hash
after proposal hash
before summary
after summary
risk level
approval requirement
```

The sync layer must not apply the proposal directly.

---

# 13. Documentation Lineage and Freshness Rules

Every generated document, generated report, proposal, and sync report must include lineage metadata.

Required lineage fields:

```text
lineage_id
run_id
generator_component
generator_version
generation_mode
generated_at
target_commit
source_inputs
source_input_hashes
source_input_types
source_input_timestamps_if_available
source_decision_refs
evidence_refs
```

Freshness rules:

```text
A generated document is stale if any source input hash differs from the recorded lineage.
A generated status report is stale if the target commit differs from the current reviewed commit.
A cached scan result is stale if the file set, file hash, or target commit changed.
A generated index cannot be used as source-of-truth if its lineage is missing.
A generated report with missing source hashes must be treated as informational only.
```

Deleted, renamed, moved, or duplicate document handling:

```text
deleted required document -> MISSING_DOCUMENT drift
renamed governed document -> NEEDS_REVIEW unless registry mapping proves continuity
moved governed document -> NEEDS_REVIEW unless path policy allows it and lineage is preserved
duplicate document_id -> BLOCKER drift for governed docs, HIGH drift for generated docs
duplicate generated report for same target -> keep newest only if lineage and source hashes match; otherwise NEEDS_REVIEW
```

---

# 14. Locking and Concurrency Rules

Documentation sync must avoid race conditions.

Required behavior:

```text
one sync run per repository root at a time
lock file or equivalent runtime lock under .agentx-init/docs_sync/tmp/
lock includes run_id, started_at, process_id if available, and target repo hash context
stale lock detection must be conservative
concurrent write attempts return BLOCKED or NEEDS_REVIEW
```

A sync run must not write generated docs while another run is writing evidence or reports for the same repository.

---

# 15. Documentation Sync Decision Schema Contract

A documentation sync decision must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_sync_decision.schema.json",
  "decision_id": "string",
  "run_id": "string",
  "timestamp": "string",
  "source_component": "DocumentationSynchronization",
  "target_document": "string",
  "document_category": "MANUAL_GOVERNED_CONTRACT",
  "requested_action": "SCAN|REPORT|GENERATE|UPDATE|PROPOSE|BLOCK|NOOP",
  "decision": "ALLOW|BLOCK|NEEDS_REVIEW|PROPOSE_ONLY|NOOP",
  "reason": "string",
  "drift_records": [],
  "source_of_truth_refs": [],
  "evidence_refs": [],
  "requires_human_approval": false,
  "requires_governed_patch": false,
  "writes_repository_file": false,
  "writes_runtime_artifact": true,
  "target_before_hash": "string|null",
  "source_input_hashes": [],
  "warnings": [],
  "errors": []
}
```

Decision rules:

```text
manual governed overwrite -> BLOCK
manual governed proposed update -> PROPOSE_ONLY
approved generated update -> ALLOW
generated update with missing source evidence -> BLOCK
ambiguous source-of-truth -> NEEDS_REVIEW
no drift -> NOOP
concurrent write lock exists -> BLOCK
```

---

# 16. Documentation Change Record Schema Contract

A documentation change record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_change_record.schema.json",
  "change_id": "string",
  "run_id": "string",
  "timestamp": "string",
  "source_component": "DocumentationSynchronization",
  "target_document": "string",
  "document_category": "GENERATED_INDEX",
  "action": "CREATED|UPDATED|PROPOSED|BLOCKED|UNCHANGED",
  "decision_id": "string",
  "before_hash": "string|null",
  "after_hash": "string|null",
  "source_input_hashes": [],
  "changed_sections": [],
  "drift_records_resolved": [],
  "drift_records_remaining": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
change records are required for every attempted sync action
blocked changes must be recorded
unchanged documents may be recorded in summary form
hashes must use SHA-256
manual governed documents require before_hash even for proposed changes
repository updates require before_hash and after_hash
```

---

# 17. Documentation Coverage Matrix

The layer must produce a coverage matrix showing whether each layer/component has required documentation.

Required coverage dimensions:

```text
contract document exists
implementation spec exists
review / DoD document exists
schemas exist
schema index references schemas
tests exist
test summary references tests
runtime evidence exists
completion record exists if DONE
README/index references correct status
cross-links valid
generated docs marked as generated
manual docs protected
```

Required matrix fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_coverage_matrix.schema.json",
  "matrix_id": "string",
  "run_id": "string",
  "timestamp": "string",
  "source_component": "DocumentationSynchronization",
  "repository": "string",
  "components": [],
  "coverage_rows": [],
  "missing_required_docs": [],
  "stale_docs": [],
  "broken_links": [],
  "status_conflicts": [],
  "protected_path_warnings": [],
  "coverage_score": 0.0,
  "warnings": [],
  "errors": []
}
```

Coverage scores must not be used alone to mark a layer DONE.

---

# 18. Documentation Evidence / Audit Contract

## 15.1 Runtime Artifact Root

All runtime evidence for this layer must be written under:

```text
.agentx-init/docs_sync/
```

## 15.2 Required Evidence Files

Expected files:

```text
.agentx-init/docs_sync/documentation_scan_history.jsonl
.agentx-init/docs_sync/documentation_drift_history.jsonl
.agentx-init/docs_sync/documentation_sync_decision_history.jsonl
.agentx-init/docs_sync/documentation_change_history.jsonl
.agentx-init/docs_sync/latest_documentation_scan.json
.agentx-init/docs_sync/latest_documentation_drift_report.json
.agentx-init/docs_sync/latest_documentation_coverage_matrix.json
.agentx-init/docs_sync/latest_documentation_sync_report.json
.agentx-init/docs_sync/documentation_sync_evidence_manifest.json
```

## 15.3 Evidence Manifest Required Fields

The evidence manifest must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_evidence_manifest.schema.json",
  "manifest_id": "string",
  "run_id": "string",
  "timestamp": "string",
  "source_component": "DocumentationSynchronization",
  "repository": "string",
  "target_commit": "string|null",
  "documents_scanned": [],
  "documents_classified": [],
  "drift_records": [],
  "sync_decisions": [],
  "change_records": [],
  "generated_artifacts": [],
  "proposal_artifacts": [],
  "blocked_changes": [],
  "source_input_hashes": [],
  "artifact_hashes": [],
  "deviation_register": [],
  "warnings": [],
  "errors": []
}
```

## 15.4 Evidence Rules

```text
append-only JSONL for history
atomic writes for latest JSON artifacts
SHA-256 hashes for generated reports and changed files
source input hashes required for generated docs
manual overwrite blocks must be evidenced
broken links must be evidenced
status conflicts must be evidenced
sync decisions must be evidenced
evidence must identify run_id and target commit when available
```

## 15.5 Redaction Rules

Before writing evidence, redact:

```text
secrets
tokens
API keys
provider credentials
private environment values
raw prompt text if captured from future prompt systems
unbounded command output
```

The layer should reuse the Security Sandbox secret redactor when available.

## 18.6 Command Proof and Review Evidence Rules

Any command used to support review, completion, drift status, schema status, or DONE status must be recorded as command proof.

Required command proof fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_command_proof.schema.json",
  "command_proof_id": "string",
  "run_id": "string",
  "timestamp": "string",
  "source_component": "DocumentationSynchronization",
  "command_name": "string",
  "command_text": "string",
  "exit_code": 0,
  "status": "PASS|FAIL|NOT RUN",
  "summary": "string",
  "output_artifact": "string|null",
  "output_sha256": "string|null",
  "target_commit": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
PASS requires exit_code 0
missing exit_code invalidates command proof
missing command text invalidates command proof
missing output hash caps review status at PARTIAL when an output artifact is used
commands must not require network, hosted model, GPU, Bun, Node, or MCP runtime
```

## 18.7 Tamper-Evidence Rules

Final evidence must be tamper-evident.

Required hashing:

```text
SHA-256 for generated documents
SHA-256 for proposals
SHA-256 for sync reports
SHA-256 for review reports
SHA-256 for completion records
SHA-256 for evidence manifests
SHA-256 for command output artifacts
SHA-256 for source inputs used to generate documents
```

History files must be append-only JSONL. If hash chaining is implemented, each record should include:

```text
record_hash
previous_record_hash
canonical_json_hash_basis
```

If hash chaining is not implemented in v1, the evidence manifest must still include file-level SHA-256 hashes for final histories used by the review.

Tamper handling:

```text
hash mismatch on evidence supporting DONE -> BLOCKER drift
modified review report after sign-off -> DONE invalid until re-reviewed
modified completion record after sign-off -> DONE invalid until re-reviewed
missing final evidence hash -> NOT DONE
```

---

# 19. Agent_X Integration Notes

## 16.1 Security Sandbox Integration

Documentation sync must use Security Sandbox checks before reading or writing repository files.

Required behavior:

```text
scan uses read/list permissions
link checker uses read/list permissions
sync executor uses approved generated-doc write paths only
manual document writes are blocked unless approved by policy/human review and routed through Governed Patch Execution
path traversal is blocked
generated artifacts stay in approved paths
```

If the Security Sandbox is missing:

```text
repository writes BLOCK
manual writes BLOCK
generated writes outside runtime root BLOCK
read-only scan may run only in explicitly approved restricted mode
```

## 16.2 Policy / Capability Registry Integration

Every sync action must check Policy / Capability Registry.

Policy must decide:

```text
which paths may be scanned
which generated paths may be written
which documents are manual protected
which actions require human approval
which reports may be generated
which status fields may be updated
which actions require Governed Patch Execution
```

If policy is missing, this layer must run in restricted mode:

```text
scan allowed for approved read-only paths
runtime evidence may be written
repository documentation updates blocked
manual document updates blocked
generated doc writes outside runtime root blocked
```

## 16.3 Tool / MCP Adapter Integration

This layer may expose tools through the Tool / MCP Adapter later.

Potential tool names:

```text
docs_scan
docs_detect_drift
docs_build_coverage_matrix
docs_plan_sync
docs_write_generated_report
docs_propose_manual_update
docs_validate_links
docs_sync_status
```

Default exposure must be read-only or report-only. Any write operation must require:

```text
policy approval
sandbox approval
generated-path allowlist
manual-doc protection check
```

MCP exposure must be read-only by default.

## 16.4 Governed Patch Execution Integration

This layer must not directly patch source documentation files that are governed.

If a manual governed document requires an update:

```text
create proposal artifact
record source evidence
record before_hash
require Policy / Capability Registry approval
route actual source change through Governed Patch Execution
```

## 16.5 Failure Taxonomy Integration

Failures must map to standard failure classes:

```text
DOC_SCAN_FAILED
DOC_CLASSIFICATION_FAILED
DOC_SOURCE_OF_TRUTH_CONFLICT
DOC_DRIFT_DETECTED
DOC_SYNC_BLOCKED
DOC_MANUAL_OVERWRITE_BLOCKED
DOC_GENERATED_WRITE_DENIED
DOC_LINK_CHECK_FAILED
DOC_SCHEMA_INVALID
DOC_EVIDENCE_WRITE_FAILED
DOC_LOCK_CONFLICT
DOC_HASH_MISMATCH
UNKNOWN_DOC_SYNC_FAILURE
```

## 16.6 Git Integration Layer

This layer must not commit, push, branch, merge, or rebase.

It may read Git status when allowed, only to support:

```text
drift detection
source mutation checks
target commit recording
stale evidence checks
```

---

# 20. CLI and Tool / MCP Exposure Contract

Documentation sync may be exposed through CLI commands or Tool / MCP Adapter tools only under restricted defaults.

Default exposure:

```text
docs_scan -> read/report only
docs_detect_drift -> read/report only
docs_build_coverage_matrix -> read/report only
docs_validate_links -> read/report only
docs_plan_sync -> proposal only
docs_write_generated_report -> runtime artifact only by default
docs_update_generated_docs -> disabled unless policy and sandbox approve
docs_propose_manual_update -> proposal only
docs_apply_manual_update -> not implemented in this layer
```

Repository-write exposure rule:

```text
Tool / MCP Adapter may expose repository-writing documentation sync only if the tool definition is disabled by default or policy-gated.
MCP must not expose repository-writing documentation sync by default.
A repository-writing tool call must include explicit mode, policy decision ID, sandbox decision ID, target path, before hash, and evidence refs.
Manual governed target paths must still return PROPOSE_ONLY or BLOCKED from this layer.
```

CLI rules:

```text
no raw shell
no network by default
no Git write
explicit mode required for repository writes
repository writes require policy and sandbox approval
manual governed updates require Governed Patch Execution and human approval
exit codes must be deterministic
command output must be bounded and redacted
```

MCP rules:

```text
MCP exposure is read-only by default.
MCP clients may scan, detect drift, build coverage matrices, and validate links.
MCP clients must not update repository documentation by default.
MCP clients must not apply manual-document changes through this layer.
Mutating MCP tools must be hidden or BLOCKED unless a later MCP acceptance pass explicitly authorizes them.
```

---

# 21. OpenCode Borrowing Notes

## 17.1 Useful Concepts to Borrow

Borrow these OpenCode-style ideas only as patterns:

```text
separate tool primitives for reading, searching, editing, and planning
explicit tool result structures
tool-specific permission checks
planning before mutation
evidence-backed tool calls
output truncation and redaction
human-question tool pattern for ambiguous decisions
```

## 17.2 Concepts to Restrict

Do not borrow:

```text
broad shell execution
implicit file mutation
model-decided edits without policy
plugin-loaded tools without registry
network-enabled behavior by default
ungoverned task/subagent behavior
```

## 17.3 Agent_X Mapping

| OpenCode-style concept | Documentation Sync equivalent | Required control |
|---|---|---|
| read/search docs | `docs_scan` / `docs_validate_links` | Security Sandbox read checks |
| plan changes | `docs_plan_sync` | policy + evidence |
| edit docs | generated-doc write or manual proposal only | sandbox + policy + human approval if manual |
| task/report | `docs_build_coverage_matrix` / report writer | schema + evidence |
| question/human | manual update approval path | Human Review later |
| invalid tool | invalid sync decision | fail closed and evidence |

---

# 22. Manual Proposal and Diff Contract

Manual governed documents must use proposal-only handling in this layer.

A manual update proposal must include:

```text
proposal_id
run_id
target_document
document_id
document_category
reason
source_of_truth_refs
evidence_refs
before_hash
proposed_after_hash
summary_of_change
changed_sections
risk_level
required_approvals
requires_governed_patch_execution
status
```

Proposal artifacts must be written under:

```text
.agentx-init/docs_sync/proposals/
```

Allowed proposal formats:

```text
JSON proposal record
Markdown proposal report
unified diff as text artifact
```

Rules:

```text
The proposal must not modify the target manual document.
The proposal must preserve the before_hash.
The proposal must identify the exact source evidence behind each change.
The proposal must not be treated as approved.
The proposal cannot mark the layer DONE.
Actual manual document updates must occur through Governed Patch Execution or another approved future layer.
```

---

# 23. Public API Contract

Expected classes:

```text
DocumentationSource
DocumentationRegistry
DocumentationScope
DocumentationSourceOfTruth
DocumentationDriftRecord
DocumentationSyncDecision
DocumentationChangeRecord
DocumentationCoverageMatrix
DocumentationLinkCheckResult
DocumentationEvidenceManifest
DocumentationSyncReport
DocumentationDeviation
```

Expected public functions:

```python
load_documentation_registry(repo_root: Path) -> DocumentationRegistry
scan_documentation(repo_root: Path, scope: DocumentationScope) -> dict
classify_document(path: Path, content: str) -> DocumentationSource
determine_source_of_truth(document: DocumentationSource, context: dict) -> DocumentationSourceOfTruth
detect_documentation_drift(registry: DocumentationRegistry, context: dict) -> list[DocumentationDriftRecord]
build_documentation_coverage_matrix(registry: DocumentationRegistry, context: dict) -> DocumentationCoverageMatrix
validate_documentation_links(registry: DocumentationRegistry) -> dict
plan_documentation_sync(drift_records: list[DocumentationDriftRecord], context: dict) -> list[DocumentationSyncDecision]
execute_documentation_sync(decisions: list[DocumentationSyncDecision], context: dict) -> list[DocumentationChangeRecord]
write_documentation_sync_evidence(records: list[DocumentationChangeRecord], repo_root: Path) -> dict
write_documentation_sync_report(context: dict, repo_root: Path) -> dict
```

---

# 24. Documentation Sync Pipeline

Every sync operation must follow this sequence:

```text
1. Receive sync request.
2. Normalize repository root and scope.
3. Acquire documentation sync lock.
4. Check policy for scan permission.
5. Use Security Sandbox to list/read approved documentation paths.
6. Classify documents.
7. Build documentation registry.
8. Determine source-of-truth references.
9. Detect drift.
10. Validate links and cross-references.
11. Build coverage matrix.
12. Generate sync decisions.
13. Block manual governed overwrites.
14. Write proposals for manual changes if needed.
15. Write generated documents only under approved generated paths.
16. Write change records.
17. Write evidence manifest.
18. Write sync report.
19. Release documentation sync lock.
20. Return schema-valid sync result.
```

No stage may be skipped unless explicitly marked not applicable.

---

# 25. Restricted Mode

If upstream dependencies are missing, the layer must run in restricted mode.

Restricted mode allows:

```text
read-only documentation scan of approved paths
document classification
drift report generation under runtime artifact root
coverage matrix generation under runtime artifact root
proposal generation under runtime artifact root
sync evidence writing under runtime artifact root
```

Restricted mode blocks:

```text
repository documentation updates
README updates
manual governed document updates
generated-document writes outside runtime artifact root
Git write behavior
network publishing
MCP mutating exposure
```

## 25.1 CI / Review Validation Mode

The implementation must support a non-mutating validation mode for CI and post-implementation review.

Validation mode may:

```text
scan documents
classify documents
detect drift
validate links
build coverage matrix
write runtime evidence under .agentx-init/docs_sync/
```

Validation mode must not:

```text
modify repository documentation
update generated repository docs
create manual patches
change README files
change roadmap files
commit, stage, branch, or push
```

The default review commands must use validation-safe behavior unless explicitly testing generated-doc write rules inside a temporary test repository.

---

# 26. Security Rules

This layer must enforce:

```text
no silent overwrite of manual governed docs
no generated content replacing contracts/specs/reviews
no DONE status without completion evidence
no repository writes without policy and sandbox checks
no path traversal
no writes outside approved generated paths
no Git write
no network by default
no raw shell
no unredacted secret logging
no broken-link report suppression
no status conflict suppression
no stale evidence used as DONE proof
no hash mismatch ignored
```

---

# 27. Runtime Artifact Rules

Runtime artifacts must stay under:

```text
.agentx-init/docs_sync/
```

Allowed runtime subdirectories:

```text
.agentx-init/docs_sync/reports/
.agentx-init/docs_sync/proposals/
.agentx-init/docs_sync/manifests/
.agentx-init/docs_sync/history/
.agentx-init/docs_sync/tmp/
```

Rules:

```text
history files are append-only JSONL
latest artifacts are written atomically
temporary files are cleaned or listed in evidence
generated reports include source hashes
proposals include target and evidence references
runtime artifacts do not replace source documentation
```

---

# 28. Schema Example and Validation Requirements

Each schema must have at least one valid example and at least two invalid examples in tests.

Required valid examples:

```text
valid_documentation_source
valid_documentation_registry
valid_documentation_scope
valid_documentation_source_of_truth
valid_documentation_drift_record
valid_documentation_sync_decision_allow
valid_documentation_sync_decision_block
valid_documentation_change_record_updated
valid_documentation_change_record_blocked
valid_documentation_coverage_matrix
valid_documentation_link_check
valid_documentation_sync_report
valid_documentation_evidence_manifest
valid_documentation_deviation
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
```

Expected validation utility:

```text
tools/agentx_evolve/tests/validate_documentation_sync_schemas.py
```

---

# 29. Test Acceptance Criteria

Required tests:

```text
test_docs_registry_loads
test_docs_scan_finds_expected_documents
test_manual_governed_document_classified
test_generated_document_classified
test_unknown_document_needs_review
test_source_of_truth_prefers_completion_record_over_readme
test_stale_evidence_cannot_support_done
test_done_without_evidence_detected_as_blocker
test_manual_document_overwrite_blocked
test_manual_document_proposal_created
test_generated_report_update_allowed_under_generated_path
test_generated_report_update_blocked_outside_allowed_path
test_broken_link_detected
test_missing_schema_reference_detected
test_missing_test_reference_detected
test_coverage_matrix_records_contract_spec_review
test_sync_decision_schema_accepts_valid_decision
test_sync_decision_schema_rejects_missing_target_document
test_change_record_schema_accepts_blocked_change
test_change_record_schema_requires_hashes_for_updates
test_evidence_manifest_written
test_source_input_hashes_recorded
test_secrets_redacted_before_doc_sync_logging
test_restricted_mode_blocks_repository_writes
test_sync_does_not_mutate_manual_docs
test_sync_report_schema_validates
test_lock_blocks_concurrent_sync_write
test_idempotent_generated_output_for_same_inputs
test_scan_scope_excludes_forbidden_paths
test_symlink_outside_repo_blocked
test_duplicate_document_id_blocks_governed_docs
test_readme_status_update_is_proposal_only
test_link_checker_resolves_relative_anchors
test_external_links_not_checked_without_network_policy
test_command_proof_requires_exit_code
test_final_evidence_hashes_required
test_deleted_required_document_remains_in_drift_report
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
document scan tests PASS
drift detection tests PASS
manual protection tests PASS
generated-doc update tests PASS
broken-link tests PASS
evidence tests PASS
idempotency tests PASS
lock/concurrency tests PASS
no unapproved source mutation
```

---

# 30. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] documentation scope is defined
[ ] manual-vs-generated rules are defined
[ ] protected/generated path boundary is defined
[ ] source-of-truth hierarchy is defined
[ ] stale evidence rules are defined
[ ] drift types are defined
[ ] sync decision schema is defined
[ ] change record schema is defined
[ ] coverage matrix schema is defined
[ ] evidence paths are defined
[ ] lock/concurrency rules are defined
[ ] idempotency rules are defined
[ ] Security Sandbox integration is defined
[ ] Policy / Capability Registry integration is defined
[ ] Tool / MCP Adapter integration is bounded
[ ] Governed Patch Execution integration is bounded
[ ] OpenCode borrowing is bounded
```

---

# 31. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] docs scan works
[ ] drift detection works
[ ] manual overwrite protection works
[ ] generated doc update rules work
[ ] broken-link detection works
[ ] coverage matrix is generated
[ ] sync decisions are evidenced
[ ] change records are evidenced
[ ] sync report exists
[ ] evidence manifest exists
[ ] source input hashes exist
[ ] lock/concurrency behavior works
[ ] idempotency behavior works
[ ] no unapproved source mutation occurs
```

---

# 32. Review Report and Completion Record Contract

The implementation review for this layer must create a review report and completion record. These are separate from ordinary sync reports.

Required review report artifact:

```text
.agentx-init/docs_sync/documentation_sync_review_report.json
```

Required completion record artifact:

```text
.agentx-init/docs_sync/documentation_sync_completion_record.json
```

Review report required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_review_report.schema.json",
  "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
  "reviewed_commit": "<commit hash>",
  "reviewed_at": "<UTC timestamp>",
  "review_environment": {},
  "commands_run": [],
  "command_proofs": [],
  "schema_validation_status": "PASS|FAIL|NOT RUN",
  "documentation_scan_status": "PASS|FAIL|NOT CHECKED",
  "drift_detection_status": "PASS|FAIL|NOT CHECKED",
  "manual_protection_status": "PASS|FAIL|NOT CHECKED",
  "generated_doc_status": "PASS|FAIL|NOT CHECKED",
  "evidence_manifest_path": "string",
  "evidence_manifest_sha256": "string",
  "review_report_sha256": "string",
  "completion_record_path": "string",
  "completion_record_sha256": "string",
  "final_verdict": "DONE|NOT DONE"
}
```

Completion record required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_completion_record.schema.json",
  "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
  "component_name": "Documentation Synchronization Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "manual_overwrite_blocks_verified": [],
  "generated_doc_updates_verified": [],
  "evidence_manifest_path": "string",
  "evidence_manifest_sha256": "string",
  "review_report_path": "string",
  "review_report_sha256": "string",
  "completion_record_sha256": "string",
  "deviation_register": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

Evidence immutability rule:

```text
After a DONE review report is written, final evidence files must not be modified without creating a new review report.
Changed hashes invalidate the previous DONE verdict.
Manual edits to evidence after sign-off must be recorded as deviations and require a new review.
```

---

# 33. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_DOCUMENTATION_SYNCHRONIZATION"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  documents_scanned: []
  drift_records_detected: []
  sync_decisions_recorded: []
  change_records_written: []
  manual_overwrite_blocks_verified: []
  generated_doc_updates_verified: []
  broken_links_detected_or_verified: []
  coverage_matrix_refs: []
  evidence_manifest_refs: []
  source_input_hashes: []
  deviation_register: []
  unresolved_risks: []
```

---

# 34. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded.

Required fields:

```yaml
deviations:
  - id: "DOC-SYNC-DEV-001"
    area: "Protected Path | Generated Path | Evidence | Schema | MCP | CLI | Other"
    description: "what differs from the contract"
    reason: "why accepted"
    safety_impact: "none|low|medium|high|critical"
    compensating_control: "test/evidence/control"
    accepted_status: "NOT APPLICABLE|DEFERRED SAFELY|NON-BLOCKING FOLLOW-UP"
    reviewer_decision: "ACCEPTED|REJECTED"
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
Manual governed overwrite cannot be accepted as a deviation.
Missing evidence cannot be accepted as a deviation for DONE.
Missing source hashes cannot be accepted as a deviation for generated docs.
```

---

# 35. Residual Risks

```yaml
residual_risks:
  - id: "DOC-SYNC-RISK-001"
    description: "Generated documentation could overwrite manually governed contracts."
    severity: "critical"
    mitigation: "Manual document classification, overwrite block, proposal-only path, and tests."
  - id: "DOC-SYNC-RISK-002"
    description: "README or roadmap could claim DONE without validation evidence."
    severity: "critical"
    mitigation: "DONE status rule requires review report, completion evidence, and command proof."
  - id: "DOC-SYNC-RISK-003"
    description: "Generated reports could become stale and be treated as authority."
    severity: "high"
    mitigation: "Source-of-truth hierarchy places generated reports below contracts, code, tests, and evidence."
  - id: "DOC-SYNC-RISK-004"
    description: "Broken links could hide missing contracts, specs, or review documents."
    severity: "medium"
    mitigation: "Required link checker and broken-reference evidence."
  - id: "DOC-SYNC-RISK-005"
    description: "Documentation sync could become a repository mutation bypass."
    severity: "critical"
    mitigation: "Security Sandbox and Policy Registry required before writes; restricted mode blocks repository writes."
  - id: "DOC-SYNC-RISK-006"
    description: "Concurrent sync runs could produce inconsistent reports or partial writes."
    severity: "high"
    mitigation: "Locking, atomic latest artifacts, and idempotency tests."
```

---

# 36. Definition of Done

The Documentation Synchronization Layer is done when it can safely scan, classify, compare, and synchronize documentation state without overwriting governed documents or inventing completion status.

It must prove:

```text
documentation registry loads
documents are classified correctly
manual governed documents are protected
generated documents are marked and controlled
protected/generated path boundary is enforced
source-of-truth hierarchy is enforced
stale evidence is rejected for DONE claims
drift is detected and classified
DONE without evidence is blocked
broken links are detected
coverage matrix is generated
sync decisions validate against schema
change records validate against schema
evidence manifest validates against schema
source input hashes are recorded
secrets are redacted
restricted mode blocks repository writes
Security Sandbox is used for file operations
Policy / Capability Registry is used for sync actions
Governed Patch Execution is required for governed manual-document changes
lock/concurrency behavior is safe
idempotency behavior is stable
no manual governed document is silently overwritten
no Git write occurs
no network is enabled by default
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_documentation_sync_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 36.5 Implementation Scoring and Hard Caps

Use this scoring model only after implementation validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schemas, tests, and runtime artifact paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Relevant tests pass with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass. |
| Scan/classification/source-of-truth | 1.0 | Scope, identity, classification, and source hierarchy work. |
| Drift/link/coverage detection | 1.0 | Drift, broken links, and coverage matrix are correct. |
| Manual/generated protection | 1.0 | Manual overwrite blocks and generated-path rules work. |
| Evidence/hash/report quality | 1.0 | Evidence manifest, hashes, reports, command proofs, and completion record exist. |
| Integration safety | 1.0 | Sandbox, policy, patch, Tool/MCP, Git, and restricted mode rules hold. |
| Idempotency/concurrency/source mutation safety | 1.0 | Locking, idempotency, and clean git status are proven. |

Hard caps:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
manual governed overwrite caps score at 4.0
README DONE without evidence caps score at 4.0
repository write without policy/sandbox caps score at 4.0
missing evidence manifest caps score at 7.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing source input hashes caps score at 8.0
missing final evidence hashes caps score at 8.0
lock/concurrency unsafe caps score at 8.0
idempotency failure caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

A final DONE verdict requires an implementation score of 10.0 and no BLOCKER.

---

# 37. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
manual governed document is overwritten automatically
generated doc replaces a contract/spec/review document
README claims DONE without completion evidence
roadmap claims DONE without review evidence
stale evidence supports DONE
sync writes outside approved paths without approved governed path
policy missing results in repository write ALLOW
sandbox missing results in repository write ALLOW
broken links are ignored
source-of-truth conflicts are silently resolved optimistically
evidence is missing
source input hashes are missing for generated docs
secrets are logged
lock/concurrency test fails
idempotency test fails
Git write is enabled
network is enabled by default
raw shell is executed
symlink outside repo is followed
duplicate governed document_id is ignored
command proof lacks exit code
final evidence hashes are missing
manual status text is automatically upgraded from generated report
```

---

# 38. Final Sign-Off Checklist

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] documentation scan works
[ ] document classification works
[ ] source-of-truth hierarchy works
[ ] stale evidence is rejected
[ ] drift detection works
[ ] manual overwrite protection works
[ ] generated update allowlist works
[ ] broken-link checker works
[ ] coverage matrix generated
[ ] sync decisions written
[ ] change records written
[ ] evidence manifest written
[ ] sync report written
[ ] source input hashes written
[ ] secrets redacted
[ ] restricted mode tested
[ ] lock/concurrency tested
[ ] idempotency tested
[ ] no unapproved source mutation
[ ] no Git write
[ ] no network by default
[ ] final completion evidence exists
```

---

# 39. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Documentation Synchronization Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed protected-path policy, changed generated-write policy, changed DONE evidence rules, new required schema family, new mutating tool exposure
```

Blocked without major revision:

```text
allowing manual governed overwrites by default
removing source-of-truth hierarchy
allowing README DONE claims without evidence
removing policy check for repository writes
removing sandbox check for file operations
allowing raw shell execution
allowing network by default
allowing Git write by default
removing evidence logging
removing source input hashes for generated docs
```

---

# 40. Final Rating

This v4 contract is rated:

```text
10/10
```

Reason:

```text
It defines the Documentation Synchronization Layer with EQC, FIC, SIB, schemas, execution modes, scan scope, document identity, protected/generated path boundaries, source-of-truth hierarchy, claim taxonomy, stale evidence rules, drift rules, link-resolution rules, generated-vs-manual rules, lineage and freshness rules, sync decision schema, change record schema, coverage matrix, evidence/audit requirements, command proofs, tamper-evidence, CLI/MCP exposure boundaries, manual proposal rules, review report and completion record contracts, locking, idempotency, deletion/archive handling, Agent_X integration boundaries, OpenCode borrowing limits, acceptance tests, scoring hard caps, No-Go rules, Definition of Done, and a final freeze rule.
```

The next artifact should be:

```text
DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC.md
```
