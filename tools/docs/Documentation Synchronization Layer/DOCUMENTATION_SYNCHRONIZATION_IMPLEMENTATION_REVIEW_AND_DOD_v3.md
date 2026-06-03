# DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_DOCUMENTATION_SYNCHRONIZATION
component_name: Documentation Synchronization Layer
roadmap_layer: 17
roadmap_phase: Phase C — Documentation Integrity and Drift Control
review_use: use after code is committed
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Report Template
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
optional_standards: ES
canonical_subdirectory: tools/agentx_evolve/docs_sync/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/docs_sync/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 review / DoD template was strong and close to production-ready, but I would rate it:

```text
9.7/10
```

It already covered the requested post-implementation review areas and added strong controls for review validity, source-of-truth handling, traceability, documentation classification, protected/manual document boundaries, generated-document boundaries, before/after hashes, evidence immutability, CLI/MCP applicability, negative tests, deviation rules, scoring caps, and final sign-off.

It was not fully 10/10 because a few final controls were still under-specified:

```text
1. Dry-run versus apply mode needed stricter separation, with dry-run as the default safe mode.
2. Generated-section boundary markers needed exact required marker semantics.
3. Documentation synchronization locking and concurrency behavior needed explicit review coverage.
4. Deterministic ordering and canonical hashing rules needed stronger acceptance language.
5. False-positive and false-negative drift classification needed explicit review checks.
6. Append-only change history and evidence immutability needed tighter JSONL rules.
7. README/index/status update authority needed stronger rules for completion evidence dependency.
8. External link handling needed clearer offline-safe validation rules.
9. The review report needed explicit sync-mode, lock-status, and deterministic-output fields.
10. The final frozen checklist needed stronger reproducibility and non-destructive-operation checks.
```

This v3 applies those corrections and is the final 10/10 review / DoD template.


# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Documentation Synchronization Layer**.

Use this document after code is committed to determine whether the layer is implemented, safe, auditable, reproducible, and ready to mark as `DONE`.

The purpose of this review is to verify that the layer:

```text
exists in the expected location
passes compileall
passes pytest
passes schema validation
scans documentation correctly
detects documentation drift correctly
validates broken local links and cross-references
protects manually governed documentation
updates generated documentation only within approved boundaries
records runtime artifacts under the approved runtime root
writes evidence manifest and review report artifacts
records command outputs, exit codes, and hashes
prevents silent overwrites of important documentation
prevents README / roadmap false DONE claims
produces a final DONE / NOT DONE verdict based on evidence
```

This document reviews the implementation. A 10/10 rating for this document does not mean the implementation is done. The implementation is done only when the recorded validation evidence satisfies the GO criteria in this document.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because Documentation Synchronization affects what the project claims is true. If this layer is wrong, README files, indexes, roadmaps, status reports, generated summaries, and contract references may claim that incomplete, unsafe, stale, or unvalidated features are complete.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Report Template, if it writes markdown or JSON reports
Command Acceptance Criteria, if CLI commands are exposed
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, only if documentation sync is exposed through MCP
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
```

---

# 3. Why This Layer Needs These Standards

Documentation Synchronization is safety-critical because it decides:

```text
which documents are current
which documents are stale
which generated documents may be updated
which manually written documents must be protected
which architecture contracts are reflected in README/index files
which cross-references are valid
which roadmap/layer status documents are updated
which evidence proves documentation was synchronized correctly
whether implementation and documentation are drifting apart
```

It must prevent:

```text
silent overwrites of governed documentation
generated docs replacing manual contracts
README files claiming features are complete when they are not
stale roadmap status
broken links between contract/spec/review documents
missing traceability between code, tests, and docs
documentation generated without evidence
documentation updates outside approved paths
```

---

# 4. Review Target

Fill this section after implementation.

```text
review_target_commit: <commit hash>
review_target_branch: <branch name>
review_date_utc: <timestamp>
reviewer: <name or tool>
repository: https://github.com/Astrocytech/Agent_X
working_tree_start_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
working_tree_end_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
review_environment:
  os: <name/version>
  python_version: <version>
  pytest_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] output artifacts are recorded for compileall, pytest, and schema validation if stored as files
[ ] SHA-256 hashes are recorded for final evidence files
[ ] review report artifact exists
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] reviewer did not rely only on the document's internal rating
```

A document rating and implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when the recorded validation evidence satisfies the GO criteria.

---

# 5. Review Scope Distinction

This layer has two different review dimensions.

## 5.1 Implementation Correctness

Implementation correctness asks:

```text
does the Documentation Synchronization Layer work as designed?
do tests prove scan, drift, link, protection, generated sync, schema, evidence, and safety behavior?
do negative tests prove unsafe behavior fails closed?
```

This dimension determines whether the layer itself can be marked `DONE`.

## 5.2 Repository Documentation State

Repository documentation state asks:

```text
are the current repository docs actually synchronized right now?
are there unresolved stale docs, broken links, or false status claims?
```

Unresolved repository documentation drift may be recorded as drift output. It is a blocker only if:

```text
the layer claims the repository is synchronized when it is not
README / roadmap claims DONE without evidence
manual-doc protection failed
broken links are hidden or misclassified
drift evidence is missing
```

A correct implementation may detect real drift and still pass implementation tests, but the final review must clearly record whether project documentation itself is currently clean or contains unresolved drift.

---

# 6. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | DONE allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present, but coverage is incomplete. | No, unless explicitly non-blocking and documented |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or executable check was not run. | No |
| NOT APPLICABLE | Requirement does not apply to the implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, overwrite, publish, expose, or mutate documentation. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 6.1 Applicability Rules

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but cannot write docs, publish reports, open ports, expose tools, or bypass evidence.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

CLI may be `NOT APPLICABLE` only if no CLI entrypoint exists. MCP may be `NOT APPLICABLE` only if no MCP exposure exists. MCP may be `DEFERRED SAFELY` only if MCP files exist but tests prove no MCP tool exposure, server start, port open, or documentation mutation can occur.

---

# 7. Source-of-Truth and Documentation Classification Rules

The review must confirm that the implementation distinguishes these documentation classes.

| Class | Meaning | Default sync behavior |
|---|---|---|
| Governed manual documentation | Contracts, implementation specs, review / DoD docs, standards, roadmap controls, architecture decisions. | Protected from overwrite. |
| Generated source documentation | Generated indexes, generated schema indexes, generated coverage summaries, generated drift reports. | May update only inside approved generated boundaries. |
| Runtime evidence documentation | Reports and manifests under `.agentx-init/docs_sync/`. | May be written by the layer. |
| Derived README / index sections | README or index fragments that summarize validated state. | May update only with explicit evidence and approved markers. |
| External references | URLs or non-local references. | Optional validation; must not be required for base tests. |

Required source-of-truth behavior:

```text
manual contracts are authoritative over generated summaries
completion evidence is authoritative for DONE status
implementation code and tests are authoritative for actual implemented files
schemas are authoritative for JSON artifact shape
runtime evidence is authoritative for validation outcome
generated documentation must cite or reference source evidence when claiming status
```

Blocking if:

```text
generated documentation overrides a manual contract
a README/index claims DONE without completion evidence
status is inferred only from filenames or stale text
generated output becomes the sole source of truth for a governed contract
```

---

# 8. Sync Mode, Locking, and Determinism Rules

The review must confirm that documentation synchronization has explicit modes and cannot silently mutate source documentation.

## 8.1 Sync Modes

Allowed modes:

```text
SCAN_ONLY
DRIFT_REPORT_ONLY
PLAN_ONLY
APPLY_GENERATED_ONLY
APPLY_APPROVED_PLAN
```

Required behavior:

```text
default mode is SCAN_ONLY or PLAN_ONLY
APPLY_GENERATED_ONLY requires generated boundary markers or registry approval
APPLY_APPROVED_PLAN requires a schema-valid sync plan
manual governed docs are blocked in every automatic apply mode
source-doc changes require before/after hashes and change-history records
```

Blocking if:

```text
default command mutates source documentation
apply mode runs without explicit mode/flag
manual docs can be changed in generated-only mode
source-doc update occurs without a sync plan
```

## 8.2 Locking and Concurrency

The implementation must prevent two documentation sync operations from writing conflicting evidence or generated documents at the same time.

Required behavior:

```text
sync lock is created under .agentx-init/docs_sync/ when write/apply mode runs
stale locks are detected and reported
concurrent apply attempts fail closed or wait only under documented bounded rules
scan-only mode does not corrupt runtime artifacts
lock acquire/release events are evidenced
```

Blocking if:

```text
concurrent apply can interleave writes
lock file is written outside approved runtime root
stale lock causes silent success
lock failure is ignored
```

## 8.3 Deterministic Output and Canonical Hashing

Documentation synchronization must be reproducible.

Required behavior:

```text
scan output is sorted deterministically
registry output is sorted deterministically
drift output is sorted deterministically
link validation output is sorted deterministically
JSON artifacts use stable key ordering where practical
SHA-256 hashes are computed on documented canonical bytes
line-ending normalization is defined for text-document hashes
non-deterministic timestamps are excluded from content hashes when comparing generated output
```

Blocking if:

```text
identical inputs produce different generated docs
identical inputs produce different drift classification without documented reason
hash comparison changes only because of timestamp noise
canonical hashing method is undefined
```

## 8.4 Generated Boundary Marker Rules

Generated source-document sections must be explicitly bounded.

Accepted generated boundary markers:

```text
<!-- AGENTX-DOCSYNC:BEGIN <section-id> -->
<!-- AGENTX-DOCSYNC:END <section-id> -->
```

Required behavior:

```text
begin and end markers must match
section-id must be stable and non-empty
nested generated sections are rejected unless explicitly supported
missing end marker blocks apply
missing begin marker blocks apply
unmarked generated output may be written only under approved generated-output files or runtime artifact roots
```

Blocking if:

```text
generated sync writes outside matching markers
generated sync creates or repairs markers inside governed manual docs without approval
marker mismatch is ignored
manual text outside markers is changed
```

## 8.5 Drift Classification Quality

The review must check both missed drift and false drift.

Required behavior:

```text
known stale fixture is classified as drift
known current fixture is not classified as drift
false DONE fixture is classified as BLOCKING_DRIFT
manual protected document fixture is not treated as generated
generated section fixture is classified correctly
drift reasons include source evidence references
```

Blocking if:

```text
stale docs are reported as current
current docs are repeatedly reported as stale without reason
false DONE claim is missed
drift report lacks reason or evidence reference
```

---

# 9. Expected Implementation Scope

## 8.1 Required Package

Expected location:

```text
tools/agentx_evolve/docs_sync/
```

Expected files:

```text
tools/agentx_evolve/docs_sync/__init__.py
tools/agentx_evolve/docs_sync/doc_models.py
tools/agentx_evolve/docs_sync/doc_scanner.py
tools/agentx_evolve/docs_sync/doc_registry.py
tools/agentx_evolve/docs_sync/drift_detector.py
tools/agentx_evolve/docs_sync/link_validator.py
tools/agentx_evolve/docs_sync/manual_doc_protector.py
tools/agentx_evolve/docs_sync/generated_doc_sync.py
tools/agentx_evolve/docs_sync/sync_planner.py
tools/agentx_evolve/docs_sync/sync_reporter.py
tools/agentx_evolve/docs_sync/evidence_writer.py
tools/agentx_evolve/docs_sync/cli.py
```

If CLI commands are not exposed, `cli.py` may be absent or implemented as a non-running stub. The review must record that status.

## 8.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
documentation_scan.schema.json
documentation_registry.schema.json
documentation_drift_report.schema.json
documentation_link_validation.schema.json
documentation_sync_plan.schema.json
documentation_sync_result.schema.json
documentation_change_record.schema.json
documentation_manual_protection.schema.json
documentation_evidence_manifest.schema.json
documentation_review_report.schema.json
documentation_completion_record.schema.json
```

## 8.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_docs_sync_scanner.py
test_docs_sync_registry.py
test_docs_sync_drift_detector.py
test_docs_sync_link_validator.py
test_docs_sync_manual_doc_protection.py
test_docs_sync_generated_doc_sync.py
test_docs_sync_planner.py
test_docs_sync_reporter.py
test_docs_sync_evidence_writer.py
test_docs_sync_schemas.py
test_docs_sync_negative_cases.py
test_docs_sync_cli.py
```

If no CLI is exposed, `test_docs_sync_cli.py` may be absent or marked `NOT APPLICABLE` with justification.

## 8.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/docs_sync/
```

Expected artifacts:

```text
documentation_scan_result.json
documentation_registry.json
documentation_drift_report.json
broken_link_report.json
manual_doc_protection_report.json
generated_doc_sync_report.json
documentation_sync_plan.json
documentation_sync_result.json
documentation_change_history.jsonl
documentation_sync_lock.json, if write/apply mode uses a lock
documentation_evidence_manifest.json
documentation_review_report.json
documentation_completion_record.json
```

---

# 10. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_docs_sync_schemas.py
git status --short
```

If `validate_docs_sync_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_docs_sync_schemas.py
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
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
external MCP server
```

---

# 11. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Package location | `tools/agentx_evolve/docs_sync/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required documentation sync schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required documentation sync tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Documentation classification | manual/generated/runtime/derived docs distinguished | PASS / PARTIAL / FAIL / NOT CHECKED |
| Documentation scan | scans approved documentation paths | PASS / PARTIAL / FAIL / NOT CHECKED |
| Documentation registry | records known docs, type, owner, generated/manual status, hashes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Drift detection | detects stale or mismatched docs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Broken-link validation | detects broken local references and anchors where supported | PASS / PARTIAL / FAIL / NOT CHECKED |
| Manual-doc protection | governed/manual docs are protected from overwrite | PASS / PARTIAL / FAIL / NOT CHECKED |
| Generated-doc sync | generated docs update only within approved boundaries | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sync mode safety | dry-run/plan/apply modes separated and default is non-mutating | PASS / PARTIAL / FAIL / NOT CHECKED |
| Locking/concurrency | write/apply operations use safe lock behavior | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deterministic output | scan, registry, drift, reports, and generated docs are reproducible | PASS / PARTIAL / FAIL / NOT CHECKED |
| Generated markers | generated sections use exact begin/end markers | PASS / PARTIAL / FAIL / NOT CHECKED |
| README/index sync | reflects only validated status | PASS / PARTIAL / FAIL / NOT CHECKED |
| Before/after hashing | touched docs have before/after hashes where applicable | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifacts | writes only under `.agentx-init/docs_sync/` unless deviation accepted | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence manifest | records commands, outputs, hashes, reviewed commit | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | records final review evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | final validation record exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | no unapproved source doc writes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Report Template | markdown/JSON reports are structured and schema-backed | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| CLI commands | CLI commands obey command acceptance criteria | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| MCP exposure | MCP exposure is absent or safe | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |

---

# 12. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Documentation scan | `doc_scanner.py` | `test_docs_sync_scanner.py` | `documentation_scan_result.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Documentation registry | `doc_registry.py` | `test_docs_sync_registry.py` | `documentation_registry.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Drift detection | `drift_detector.py` | `test_docs_sync_drift_detector.py` | `documentation_drift_report.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Broken-link validation | `link_validator.py` | `test_docs_sync_link_validator.py` | `broken_link_report.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Manual-doc protection | `manual_doc_protector.py` | `test_docs_sync_manual_doc_protection.py` | `manual_doc_protection_report.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Generated-doc sync | `generated_doc_sync.py` | `test_docs_sync_generated_doc_sync.py` | `generated_doc_sync_report.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sync mode safety | `sync_planner.py` / `generated_doc_sync.py` | `test_docs_sync_negative_cases.py` | `documentation_sync_plan.json` / `documentation_sync_result.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Locking/concurrency | `evidence_writer.py` / `generated_doc_sync.py` | `test_docs_sync_evidence_writer.py` | lock event evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deterministic output | scanner/registry/drift/link/report modules | relevant module tests | repeated-run output hashes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sync planning | `sync_planner.py` | `test_docs_sync_planner.py` | `documentation_sync_plan.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sync reporting | `sync_reporter.py` | `test_docs_sync_reporter.py` | `documentation_sync_result.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence writing | `evidence_writer.py` | `test_docs_sync_evidence_writer.py` | `documentation_evidence_manifest.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | schema files | `test_docs_sync_schemas.py` or validator | schema validation output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety behavior | all relevant modules | `test_docs_sync_negative_cases.py` | pytest output + review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| CLI safety | `cli.py` | `test_docs_sync_cli.py` | CLI output artifact or N/A note | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| MCP safety | MCP adapter if exposed | MCP-specific test or N/A note | MCP deviation or safe exposure report | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Review report | reporter/evidence writer | schema validation | `documentation_review_report.json` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | reporter/evidence writer | schema validation | `documentation_completion_record.json` | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 13. What Exists Checklist

## 12.1 Package Files

```text
[ ] tools/agentx_evolve/docs_sync/__init__.py
[ ] tools/agentx_evolve/docs_sync/doc_models.py
[ ] tools/agentx_evolve/docs_sync/doc_scanner.py
[ ] tools/agentx_evolve/docs_sync/doc_registry.py
[ ] tools/agentx_evolve/docs_sync/drift_detector.py
[ ] tools/agentx_evolve/docs_sync/link_validator.py
[ ] tools/agentx_evolve/docs_sync/manual_doc_protector.py
[ ] tools/agentx_evolve/docs_sync/generated_doc_sync.py
[ ] tools/agentx_evolve/docs_sync/sync_planner.py
[ ] tools/agentx_evolve/docs_sync/sync_reporter.py
[ ] tools/agentx_evolve/docs_sync/evidence_writer.py
[ ] tools/agentx_evolve/docs_sync/cli.py or documented N/A
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 12.2 Schema Files

```text
[ ] documentation_scan.schema.json
[ ] documentation_registry.schema.json
[ ] documentation_drift_report.schema.json
[ ] documentation_link_validation.schema.json
[ ] documentation_sync_plan.schema.json
[ ] documentation_sync_result.schema.json
[ ] documentation_change_record.schema.json
[ ] documentation_manual_protection.schema.json
[ ] documentation_evidence_manifest.schema.json
[ ] documentation_review_report.schema.json
[ ] documentation_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 12.3 Test Files

```text
[ ] test_docs_sync_scanner.py
[ ] test_docs_sync_registry.py
[ ] test_docs_sync_drift_detector.py
[ ] test_docs_sync_link_validator.py
[ ] test_docs_sync_manual_doc_protection.py
[ ] test_docs_sync_generated_doc_sync.py
[ ] test_docs_sync_planner.py
[ ] test_docs_sync_reporter.py
[ ] test_docs_sync_evidence_writer.py
[ ] test_docs_sync_schemas.py
[ ] test_docs_sync_negative_cases.py
[ ] test_docs_sync_cli.py or documented N/A
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 12.4 Runtime Artifacts

```text
[ ] .agentx-init/docs_sync/documentation_scan_result.json
[ ] .agentx-init/docs_sync/documentation_registry.json
[ ] .agentx-init/docs_sync/documentation_drift_report.json
[ ] .agentx-init/docs_sync/broken_link_report.json
[ ] .agentx-init/docs_sync/manual_doc_protection_report.json
[ ] .agentx-init/docs_sync/generated_doc_sync_report.json
[ ] .agentx-init/docs_sync/documentation_sync_plan.json
[ ] .agentx-init/docs_sync/documentation_sync_result.json
[ ] .agentx-init/docs_sync/documentation_change_history.jsonl
[ ] .agentx-init/docs_sync/documentation_evidence_manifest.json
[ ] .agentx-init/docs_sync/documentation_review_report.json
[ ] .agentx-init/docs_sync/documentation_completion_record.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 14. Validation Commands

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly an expected-failure negative test where the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_docs_sync_schemas.py
git status --short
```

If there is a scoped documentation sync test suite, also record:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_docs_sync_scanner.py \
  tools/agentx_evolve/tests/test_docs_sync_registry.py \
  tools/agentx_evolve/tests/test_docs_sync_drift_detector.py \
  tools/agentx_evolve/tests/test_docs_sync_link_validator.py \
  tools/agentx_evolve/tests/test_docs_sync_manual_doc_protection.py \
  tools/agentx_evolve/tests/test_docs_sync_generated_doc_sync.py \
  tools/agentx_evolve/tests/test_docs_sync_planner.py \
  tools/agentx_evolve/tests/test_docs_sync_reporter.py \
  tools/agentx_evolve/tests/test_docs_sync_evidence_writer.py \
  tools/agentx_evolve/tests/test_docs_sync_schemas.py \
  tools/agentx_evolve/tests/test_docs_sync_negative_cases.py
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
external MCP server
```

---

# 15. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Documentation Synchronization Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 16. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required documentation scan, drift, link, manual-protection, generated-sync, schema, evidence, report, CLI, or negative test fails
exit code is missing
```

---

# 17. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_docs_sync_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_docs_sync_schemas.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output artifact is stored>
```

Required schema tests:

```text
documentation scan schema accepts valid scan result
documentation scan schema rejects missing document path
documentation registry schema accepts valid registry
documentation registry schema records manual/generated/runtime classification
documentation drift report schema accepts valid report
documentation link validation schema accepts valid broken-link report
documentation sync plan schema accepts valid plan
documentation sync result schema accepts valid result
documentation change record schema accepts valid change record with before/after hashes
documentation manual protection schema accepts protected manual doc result
documentation evidence manifest schema accepts valid evidence manifest
documentation review report schema accepts valid review report
documentation completion record schema accepts final completion record
schemas reject invalid status values
schemas reject missing reviewed commit where required
schemas reject missing evidence hashes where required
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid documentation records are accepted
drift results cannot represent stale/current/protected states
manual protection schema cannot represent blocked overwrite attempts
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 18. Documentation Scan Result

The implementation must scan approved documentation roots and produce a structured scan result.

Expected scan coverage:

```text
README files
contract documents
implementation spec documents
review / DoD documents
schema files
roadmap or layer status files
index files
generated markdown reports, if applicable
JSON reports, if applicable
```

Required behavior:

```text
[ ] approved documentation paths are scanned
[ ] ignored paths are excluded
[ ] generated docs are identified
[ ] manual/governed docs are identified
[ ] runtime evidence docs are identified
[ ] stale candidates are identified
[ ] missing expected docs are identified
[ ] scan result includes document hashes
[ ] scan result is schema-valid
[ ] scan result is written under .agentx-init/docs_sync/
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
scanner misses required documentation roots
scanner treats governed manual docs as generated docs
scanner writes outside approved runtime root
scanner result is unstructured or schema-invalid
```

---

# 19. Documentation Registry Result

The implementation must create or validate a documentation registry.

Required registry metadata:

```text
document path
document id, if present
document type
owner component
manual/generated/runtime classification
generated boundary marker, if applicable
source-of-truth reference
expected update authority
current hash
last scan timestamp
warnings
errors
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
registry cannot distinguish manual and generated documents
registry lacks document hashes
registry lacks owner/source-of-truth metadata for governed docs
registry permits generated replacement of manual docs
```

---

# 20. Documentation Drift Result

The implementation must detect documentation drift without silently rewriting documents.

Expected drift checks:

```text
contract/spec/review version mismatch
README claims DONE without review evidence
roadmap status mismatch
missing cross-reference between contract, spec, and review documents
schema list mismatch
expected test list mismatch
stale generated documentation
manual document modified without approved sync plan
completion evidence missing for DONE status
```

Required behavior:

```text
[ ] drift report is generated
[ ] stale documents are listed
[ ] current documents are listed
[ ] protected manual documents are listed
[ ] drift severity is recorded
[ ] recommended action is recorded
[ ] source evidence for drift decision is recorded
[ ] drift report is schema-valid
[ ] drift report is written under .agentx-init/docs_sync/
```

Required drift severities:

```text
BLOCKING_DRIFT
HIGH_DRIFT
NON_BLOCKING_DRIFT
NO_DRIFT
NOT_CHECKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
README can claim DONE without completion evidence
drift report silently changes documents instead of reporting plan
drift severity is missing
drift source evidence is missing
drift report is schema-invalid
```

---

# 21. Broken-Link Validation Result

The implementation must validate local documentation links and cross-references.

Required checks:

```text
[ ] contract document links resolve
[ ] implementation spec links resolve
[ ] review / DoD links resolve
[ ] schema references resolve
[ ] test file references resolve
[ ] README/index local links resolve
[ ] roadmap/layer references resolve
[ ] local heading anchors resolve where supported
[ ] missing local files are listed
[ ] broken links are listed with source document and target
[ ] validation result is schema-valid
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
broken links are not detected
cross-reference checks are skipped
broken-link result lacks source and target
broken-link report is schema-invalid
```

Network link validation is optional and must not be required for the base validation suite.

---

# 22. Manual-Doc Protection Result

The implementation must protect manually governed documents.

Protected documentation includes:

```text
controlling contracts
implementation specs
review / DoD documents
roadmap control documents
manual architecture decisions
manual standards documents
manual evidence records
```

Required behavior:

```text
[ ] manual docs are detected
[ ] generated docs are detected separately
[ ] manual docs are never overwritten without explicit approved plan
[ ] attempted manual-doc overwrite is blocked
[ ] blocked overwrite is evidenced
[ ] before/after hashes prove protected docs were not changed
[ ] manual protection report is schema-valid
[ ] manual protection report is written under .agentx-init/docs_sync/
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
manual contract can be overwritten as generated output
generated doc sync can replace manual docs
manual protection result is missing
blocked overwrite lacks evidence
protected doc hashes changed without approved plan
```

---

# 23. Generated-Doc Sync Result

Generated documentation may be updated only inside approved generated-document boundaries.

Allowed generated documentation examples:

```text
generated index sections clearly marked as generated
generated schema index files
generated test coverage summaries
generated documentation drift reports
generated cross-reference maps
generated runtime documentation reports under .agentx-init/docs_sync/
```

Required behavior:

```text
[ ] generated docs are updated only when marked as generated or listed in approved sync plan
[ ] updates are deterministic
[ ] updates include before/after hashes
[ ] updates are recorded in documentation_change_history.jsonl
[ ] generated-doc sync report is schema-valid
[ ] generated-doc sync report is written under .agentx-init/docs_sync/
[ ] no manual docs are rewritten
[ ] no source docs are changed without approved plan
[ ] dry-run mode exists and does not mutate source docs
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
generated sync rewrites manual docs
generated sync writes outside approved paths
generated sync is nondeterministic
generated sync lacks before/after hash evidence
generated sync lacks change evidence
```

---

# 24. Sync Plan and Change Approval Result

The implementation must create a sync plan before writing any generated documentation outside runtime artifacts.

Required sync plan behavior:

```text
[ ] plan lists every proposed source-doc change
[ ] plan identifies generated/manual classification for every target
[ ] plan includes reason, source evidence, and expected output path
[ ] plan includes dry_run flag
[ ] plan includes approval status or governance reference, if required
[ ] plan blocks manual-doc targets by default
[ ] plan blocks writes outside approved generated boundaries
[ ] plan is schema-valid
```

Required change record behavior:

```text
[ ] change record includes target path
[ ] change record includes before_sha256
[ ] change record includes after_sha256
[ ] change record includes change_type
[ ] change record includes source evidence refs
[ ] change record includes reviewer or approval ID where required
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
source documentation changes occur without a sync plan
manual docs are modified without explicit approval
generated docs are modified without boundary marker or registry entry
change history lacks hashes
```

---

# 25. Runtime Artifact Check

Runtime artifacts must be written under:

```text
.agentx-init/docs_sync/
```

Required checks:

```text
[ ] runtime directory exists after validation
[ ] scan result exists
[ ] documentation registry exists
[ ] drift report exists
[ ] broken-link report exists
[ ] manual protection report exists
[ ] generated sync report exists where applicable
[ ] sync plan exists
[ ] sync result exists
[ ] change history JSONL exists if changes were proposed or made
[ ] evidence manifest exists
[ ] review report exists
[ ] completion record exists before DONE
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
runtime artifacts are missing
runtime artifacts are written outside approved runtime root
source documents are used as runtime evidence files without copy/reference
runtime artifacts are schema-invalid
```

---

# 26. Evidence Manifest Check

Create:

```text
.agentx-init/docs_sync/documentation_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_evidence_manifest.schema.json",
  "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "documentation_scan_result": "<path>",
  "documentation_registry": "<path>",
  "documentation_drift_report": "<path>",
  "broken_link_report": "<path>",
  "manual_doc_protection_report": "<path>",
  "generated_doc_sync_report": "<path or NOT_APPLICABLE>",
  "documentation_sync_plan": "<path>",
  "documentation_sync_result": "<path>",
  "evidence_files": [],
  "evidence_file_hashes": [],
  "protected_document_hashes": [],
  "generated_document_change_hashes": [],
  "runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "sync_mode": "SCAN_ONLY | DRIFT_REPORT_ONLY | PLAN_ONLY | APPLY_GENERATED_ONLY | APPLY_APPROVED_PLAN",
  "lock_status": "NOT_APPLICABLE | ACQUIRED_AND_RELEASED | BLOCKED_BY_ACTIVE_LOCK",
  "deterministic_output_status": "PASS",
  "generated_boundary_marker_status": "PASS",
  "manual_doc_protection_status": "PASS",
  "generated_doc_sync_status": "PASS_OR_NOT_APPLICABLE",
  "broken_link_status": "PASS",
  "drift_detection_status": "PASS",
  "repository_documentation_state": "CURRENT | DRIFT_DETECTED | NOT_CHECKED",
  "sync_mode": "SCAN_ONLY | DRIFT_REPORT_ONLY | PLAN_ONLY | APPLY_GENERATED_ONLY | APPLY_APPROVED_PLAN",
  "lock_status": "NOT_APPLICABLE | ACQUIRED_AND_RELEASED | BLOCKED_BY_ACTIVE_LOCK",
  "deterministic_output_status": "PASS | FAIL | NOT_CHECKED",
  "generated_boundary_marker_status": "PASS | FAIL | NOT_CHECKED",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence files.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Self-hash rule:

```text
If an artifact cannot include its own final SHA-256 inside itself without changing its hash, record the artifact hash in the review report or separate hash list.
Do not claim a self-hash inside a file unless the implementation uses a clearly defined canonical hashing method that excludes the self-hash field.
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
evidence manifest is missing
evidence manifest lacks reviewed commit
evidence manifest lacks command exit codes
evidence hashes are missing
evidence files are outside approved runtime root without deviation
```

---

# 27. Review Report Check

Create:

```text
.agentx-init/docs_sync/documentation_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_review_report.schema.json",
  "component_id": "AGENTX_DOCUMENTATION_SYNCHRONIZATION",
  "review_document_id": "DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "repository_documentation_state": "CURRENT | DRIFT_DETECTED | NOT_CHECKED",
  "sync_mode": "SCAN_ONLY | DRIFT_REPORT_ONLY | PLAN_ONLY | APPLY_GENERATED_ONLY | APPLY_APPROVED_PLAN",
  "lock_status": "NOT_APPLICABLE | ACQUIRED_AND_RELEASED | BLOCKED_BY_ACTIVE_LOCK",
  "deterministic_output_status": "PASS | FAIL | NOT_CHECKED",
  "generated_boundary_marker_status": "PASS | FAIL | NOT_CHECKED",
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/docs_sync/documentation_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/docs_sync/documentation_review_report.json",
  "review_report_sha256": "<sha256 or external hash reference>",
  "completion_record_path": ".agentx-init/docs_sync/documentation_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 26.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 28. Source Mutation Check

Required command:

```bash
git status --short
```

Expected:

```text
clean working tree
```

or:

```text
only expected runtime artifacts under .agentx-init/docs_sync/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
manual documentation was modified without approved sync plan
contract/spec/review documents were overwritten
runtime artifacts were written outside approved runtime root
generated docs were written outside approved generated sections
source files were modified by tests without approval
```

---

# 29. CLI / Command Acceptance Check

This section applies if documentation synchronization exposes CLI commands.

Required CLI behavior:

```text
[ ] CLI commands are deterministic
[ ] CLI supports scan/report/dry-run before any apply behavior
[ ] CLI apply behavior requires explicit flag and approved sync plan
[ ] CLI refuses unknown commands
[ ] CLI records exit codes
[ ] CLI writes evidence under .agentx-init/docs_sync/
[ ] CLI does not require network, LLM, hosted model, Bun, Node, or OpenCode runtime
[ ] CLI does not overwrite manual docs
[ ] CLI reports schema-valid output or structured error
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
CLI apply mode overwrites manual docs
CLI writes outside approved roots
CLI claims success without evidence
CLI requires external runtime for base validation
```

---

# 30. MCP Exposure Check

This section applies only if documentation synchronization is exposed through MCP.

Required MCP behavior:

```text
[ ] no MCP server starts on import
[ ] no network port opens by default
[ ] MCP exposure is read-only or plan-only by default
[ ] MCP cannot directly apply documentation changes by default
[ ] MCP cannot overwrite manual docs
[ ] MCP calls are policy-checked if Tool / MCP Adapter is used
[ ] MCP calls write evidence if executed
[ ] MCP exposure status is recorded as PASS, NOT APPLICABLE, or DEFERRED SAFELY
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
MCP starts automatically
MCP opens a port by default
MCP can apply documentation changes by default
MCP can overwrite manual docs
MCP bypasses policy or evidence
```

---

# 31. Negative Test Pack

The review must prove that forbidden documentation behavior fails closed.

Required negative cases:

```text
[ ] manual contract overwrite attempt -> BLOCKED
[ ] manual implementation spec overwrite attempt -> BLOCKED
[ ] review / DoD overwrite attempt -> BLOCKED
[ ] README DONE claim without completion evidence -> BLOCKED or DRIFT_DETECTED
[ ] stale roadmap status -> DRIFT_DETECTED
[ ] broken local link -> LINK_BROKEN result
[ ] missing referenced schema -> DRIFT_DETECTED or LINK_BROKEN
[ ] generated doc update outside generated boundary -> BLOCKED
[ ] sync write outside approved path -> BLOCKED
[ ] generated section without boundary marker -> BLOCKED
[ ] generated marker mismatch -> BLOCKED
[ ] default sync mode attempts write -> BLOCKED
[ ] concurrent apply lock conflict -> BLOCKED
[ ] repeated scan with identical input produces stable output
[ ] known current fixture is not falsely reported as stale
[ ] missing evidence manifest -> NOT DONE
[ ] missing reviewed commit -> NOT DONE
[ ] missing command exit code -> NOT DONE
[ ] missing evidence hash -> NOT DONE
[ ] schema-invalid sync result -> FAIL
[ ] CLI unknown command -> FAIL or INVALID, if CLI exists
[ ] MCP apply request -> BLOCKED or NOT APPLICABLE, if MCP exists
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 32. Deviation Register

Any exception, deferral, unresolved drift, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Scan | Registry | Drift | Links | Manual Protection | Generated Sync | Evidence | Runtime Artifact Boundary | CLI | MCP | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for DONE unless the review proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/docs_sync/` require a deviation entry.
MCP deferral requires a deviation entry if MCP files exist.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Manual-doc overwrite cannot be accepted as a deviation for DONE.
False DONE claim cannot be accepted as a deviation for DONE.
```

---

# 33. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
documentation classification:
documentation scan:
documentation registry:
documentation drift detection:
broken-link validation:
manual-doc protection:
generated-doc sync:
sync plan / change record:
CLI / command acceptance:
MCP exposure:
runtime artifact check:
evidence manifest:
review report:
evidence hashes:
negative tests:
source mutation check:
completion record:
```

---

# 34. What Failed

Fill after validation.

```text
failures:
  - <none or list>
blocking_failures:
  - <none or list>
high_priority_failures:
  - <none or list>
non_blocking_failures:
  - <none or list>
rejected_deviations:
  - <none or list>
unresolved_repository_drift:
  - <none or list>
```

---

# 35. Issue Severity Classification

## 34.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
documentation scan fails
documentation classification fails
documentation registry fails
drift detection fails
manual-doc protection fails
generated-doc sync overwrites manual docs
README claims DONE without completion evidence
broken-link validation is missing or fails unhandled
source mutation occurs without approved sync plan
runtime artifacts are written outside approved runtime root
review report is missing
evidence manifest is missing
evidence hashes are missing
completion record is missing
required area remains NOT CHECKED
required command remains NOT RUN
```

## 34.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete drift severity mapping
partial broken-link coverage
partial generated-doc boundary checks
missing documentation registry metadata
runtime artifact boundary exception lacks justification
review environment not recorded
non-critical report formatting mismatch
unresolved repository drift that is correctly reported but not yet fixed
```

## 34.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
additional future documentation roots not yet scanned
optional network-link validation omitted
CLI intentionally absent
MCP exposure intentionally absent
extra generated report not yet implemented
```

---

# 36. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Scan / registry coverage | 1.0 | Approved docs are scanned and classified with registry metadata and hashes. |
| Drift / link validation | 1.0 | Drift, false DONE claims, stale roadmap status, and broken links are detected. |
| Manual protection / generated sync | 1.0 | Manual docs protected, generated docs update only inside approved boundaries, before/after hashes recorded, generated markers enforced. |
| Evidence / reports | 1.0 | Evidence manifest, review report, completion record, command outputs, and hashes exist. |
| Negative tests / safety | 1.0 | Unsafe overwrite, false DONE, missing evidence, invalid schema, and boundary bypass cases fail closed. |
| Integration and source-mutation safety | 1.0 | CLI/MCP applicability handled, sync mode and locking safe, deterministic output proven, clean git status, no unapproved source mutation. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled documentation synchronization
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
manual-doc overwrite caps score at 4.0
README false DONE claim allowed caps score at 4.0
generated sync outside approved boundary caps score at 5.0
missing generated marker enforcement caps score at 7.0
default mode mutates source docs caps score at 5.0
concurrent apply can interleave writes caps score at 6.0
non-deterministic output without reason caps score at 8.0
missing drift detection caps score at 6.5
missing broken-link validation caps score at 7.0
source mutation by tests without approved plan caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 37. GO / NO-GO Rules

## 36.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
documentation classification passes
documentation scan passes
documentation registry passes
documentation drift detection passes
broken-link validation passes
manual-doc protection passes
generated-doc sync passes or is not applicable
sync mode safety passes
locking/concurrency checks pass for write/apply mode or are not applicable
deterministic output checks pass
generated boundary marker checks pass
sync plan / change record checks pass when source docs are changed
runtime artifact check passes
evidence manifest exists
evidence hashes exist
review report exists
completion record exists
negative tests pass
source mutation check passes
CLI tests pass or CLI is not applicable
MCP exposure tests pass, are safely deferred, or MCP is not applicable
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 36.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
documentation scan fails
documentation registry fails
drift detection fails
manual-doc protection fails
generated-doc sync overwrites governed manual docs
default sync mode mutates source documentation
generated marker mismatch is ignored
concurrent apply can interleave writes
broken-link validation is missing
README/status files claim DONE without evidence
source documents are modified without approved sync plan
runtime artifacts are missing
runtime artifacts are written outside approved root without deviation
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 38. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix scan path configuration
fix generated/manual document classification
fix documentation registry fields
fix drift detection rules
fix broken-link parser
fix manual-doc protection checks
fix generated-doc boundary markers
fix sync plan generation
fix before/after hashing
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix tests to reflect the contract
fix command acceptance checks
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove manual-doc protection to pass tests
do not let generated docs overwrite contracts
do not mark stale docs as current without evidence
do not let README claim DONE without completion evidence
do not skip broken-link validation
do not skip evidence writing
do not omit hashes for final DONE
do not write runtime artifacts outside approved root without deviation
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
do not require network, hosted model, LLM, Bun, Node, or OpenCode runtime for validation
```

---

# 39. Definition of Done

The Documentation Synchronization Layer is done when it can safely detect, report, and synchronize documentation state without silently rewriting important documentation.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all schemas exist
all tests exist
documentation classification works
documentation scan works
documentation registry works
documentation drift detection works
broken-link validation works
manual-governed documents are protected
generated docs update only within approved boundaries
generated boundary markers are enforced
default sync mode is non-mutating
write/apply modes use lock behavior
outputs are deterministic for identical inputs
sync plans are required for source-doc updates
change records include before/after hashes
README/index/status updates do not claim DONE without evidence
runtime artifacts are written only under .agentx-init/docs_sync/
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs without approved sync plan
no network is required for base validation
no LLM or hosted model is required for base validation
CLI behavior is safe or not applicable
MCP exposure is safe, safely deferred, or not applicable
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_docs_sync_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 40. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
documentation scan result
documentation registry
documentation drift report
broken-link validation report
manual-doc protection report
generated-doc sync report or N/A note
sync plan and sync result
change history, if source docs changed
runtime artifact check
evidence manifest
review report
git status output
completion record
SHA-256 hashes for final evidence artifacts
before/after hashes for changed generated docs
protected-document hashes proving no unauthorized manual-doc change
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no silent manual-doc overwrite
no README DONE claim without evidence
no stale roadmap status accepted as current
no broken cross-reference accepted silently
no runtime artifact outside approved root without deviation
hashes for final evidence artifacts
```

---

# 41. Completion Evidence Record

After validation, create:

```text
.agentx-init/docs_sync/documentation_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "documentation_completion_record.schema.json",
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
    "DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_SPEC",
    "DOCUMENTATION_SYNCHRONIZATION_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "documentation_roots_scanned": [],
  "manual_docs_protected": [],
  "generated_docs_synced": [],
  "broken_links_detected": [],
  "drift_items_detected": [],
  "drift_items_resolved": [],
  "repository_documentation_state": "CURRENT | DRIFT_DETECTED | NOT_CHECKED",
  "sync_mode": "SCAN_ONLY | DRIFT_REPORT_ONLY | PLAN_ONLY | APPLY_GENERATED_ONLY | APPLY_APPROVED_PLAN",
  "lock_status": "NOT_APPLICABLE | ACQUIRED_AND_RELEASED | BLOCKED_BY_ACTIVE_LOCK",
  "deterministic_output_status": "PASS | FAIL | NOT_CHECKED",
  "generated_boundary_marker_status": "PASS | FAIL | NOT_CHECKED",
  "evidence_manifest_path": ".agentx-init/docs_sync/documentation_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/docs_sync/documentation_review_report.json",
  "review_report_sha256": "<sha256 or external hash reference>",
  "completion_record_sha256": "<sha256 or external hash reference>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 42. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: 10/10
repository_documentation_state: CURRENT | DRIFT_DETECTED | NOT_CHECKED
reason:
  - <summary>
remaining_blockers:
  - <none or list>
remaining_high_issues:
  - <none or list>
accepted_non_blocking_followups:
  - <none or list>
accepted_deviations:
  - <none or list>
unresolved_repository_drift:
  - <none or list>
```

A final verdict of `DONE` is invalid if:

```text
implementation_rating is below 10.0
reviewed commit is missing
review environment is missing
any required command was not run
any required command exit code is missing
any required area is NOT CHECKED
any required command is NOT RUN
any BLOCKER remains
evidence hashes are missing
review report is missing
completion record is missing
manual-doc protection failed
generated-doc sync overwrote governed docs
README/status false DONE claim is allowed
```

---

# 43. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/docs_sync/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Documentation Classification:
[ ] manual docs identified
[ ] generated docs identified
[ ] runtime evidence docs identified
[ ] source-of-truth rules enforced

Documentation Scan:
[ ] approved docs scanned
[ ] generated docs identified
[ ] manual docs identified
[ ] scan result written
[ ] document hashes recorded

Registry:
[ ] documentation registry written
[ ] owner/type/source-of-truth metadata recorded
[ ] manual/generated classification recorded

Drift:
[ ] stale docs detected
[ ] roadmap/status drift detected
[ ] README DONE claims require evidence
[ ] drift severity recorded
[ ] drift report written

Links:
[ ] local links validated
[ ] local anchors validated where supported
[ ] broken links detected
[ ] cross-references validated
[ ] broken-link report written

Manual Protection:
[ ] governed manual docs protected
[ ] manual overwrite attempts blocked
[ ] blocked overwrite evidenced
[ ] protected doc hashes unchanged unless approved

Generated Sync:
[ ] generated docs update only in approved boundaries
[ ] sync plan exists before source-doc changes
[ ] sync changes recorded
[ ] before/after hashes recorded
[ ] no manual docs overwritten

CLI / MCP:
[ ] CLI safe or N/A
[ ] MCP safe, deferred safely, or N/A

Evidence:
[ ] runtime artifacts under .agentx-init/docs_sync/
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] evidence immutability rule satisfied

Safety:
[ ] no silent overwrites
[ ] no source mutation without approved plan
[ ] no network required for base validation
[ ] no LLM/model dependency required for base validation

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] repository documentation state recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 44. Final Sign-Off Template

Use this after implementation validation.

```text
Documentation Synchronization Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- documentation classification: PASS/FAIL
- documentation scan: PASS/FAIL
- documentation registry: PASS/FAIL
- documentation drift detection: PASS/FAIL
- broken-link validation: PASS/FAIL
- manual-doc protection: PASS/FAIL
- generated-doc sync: PASS/FAIL/N/A
- sync mode safety: PASS/FAIL
- lock/concurrency safety: PASS/FAIL/N/A
- deterministic output: PASS/FAIL
- generated boundary markers: PASS/FAIL
- sync plan / change record: PASS/FAIL/N/A
- CLI / command acceptance: PASS/FAIL/N/A
- MCP exposure: PASS/FAIL/N/A/DEFERRED SAFELY
- runtime artifact check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- source mutation check: PASS/FAIL
- completion record: PRESENT/MISSING
- repository documentation state: CURRENT/DRIFT_DETECTED/NOT_CHECKED

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash or external hash reference>
- completion record: <path>, sha256=<hash or external hash reference>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups

Unresolved repository documentation drift:
- none / list drift items
```

---

# 45. Final Rating

This v3 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the requested post-implementation review coverage and adds the final production-control details: review validity rules, implementation-vs-repository-state distinction, source-of-truth rules, traceability matrix, documentation classification, dry-run/apply separation, sync locking, deterministic output, canonical hashing, generated boundary marker rules, protected/generated boundary checks, before/after hashing, evidence immutability, CLI/MCP applicability, stricter negative tests, deviation rules, scoring caps, and a final sign-off template that prevents DONE from being claimed without reviewed commit, command evidence, hashes, review report, and completion record.
```
