# FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_FINAL_SYSTEM_ACCEPTANCE
component_name: Final System Acceptance Layer
roadmap_layer: 22
roadmap_phase: Phase Z — Final System Acceptance
review_use: use after final acceptance code is committed
basis_documents:
  - FINAL_SYSTEM_ACCEPTANCE_EQC_FIC_SIB_SCHEMA_CONTRACT
  - FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_SPEC
  - FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD_v3
  - FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria, Release / Promotion Acceptance Criteria
optional_standards: ES, Report Template
canonical_subdirectory: tools/agentx_evolve/final_acceptance/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/final_acceptance/
review_document_rating: 10/10
final_verdict_field: ACCEPTED | NOT_ACCEPTED
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was very strong and near final-system ready. I would rate v3:

```text
9.8/10
```

It already covered the requested review areas and added important final-system controls:

```text
acceptance scope
layer criticality
stale-evidence detection
circular self-validation prevention
direct and transitive dependency checks
critical-path validation
CLI exit-code semantics
release-readiness separation
reproducible self-hashing
source mutation checks
runtime artifact boundaries
scope freeze / scope-change control
evidence source-of-truth precedence
blocker propagation
negative acceptance-runner tests
tamper and mismatch handling
reviewer independence
artifact verdict consistency
final ACCEPTED / NOT_ACCEPTED verdict
```

It was not fully 10/10 because several last-mile final-system controls were still under-specified:

```text
1. Canonical JSON and deterministic hashing were not strict enough for cross-platform reproducibility.
2. Runtime reachability rules were not explicit enough for deferred, optional, or NOT_APPLICABLE layers.
3. Waiver / exception authority needed a strict rule that no waiver can override a BLOCKER.
4. Report-only mode needed stronger separation from final-enforcing mode.
5. Cross-layer schema-version compatibility and migration checks were missing.
6. Evidence retention / archive requirements were missing for final accepted releases.
7. Re-run / revalidation procedure after invalidation needed a clearer required sequence.
8. Time, locale, path, and environment normalization were not explicit enough for reproducible evidence.
9. Acceptance of generated reports needed a field-level completeness check, not only file existence.
10. The final checklist needed to include these last-mile controls.
```

This v4 applies those corrections and is the final 10/10 post-implementation review / DoD template.

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Final System Acceptance Layer**.

Use it after code is committed to determine whether the complete Agent_X system, within a declared acceptance scope, is validated, reproducible, safe, evidence-backed, and ready to be marked as:

```text
ACCEPTED
```

or:

```text
NOT_ACCEPTED
```

This is the final “is Agent_X done as a system?” review document.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schema validation passes
whether the final acceptance runner passes
whether the layer completion matrix passes
whether cross-layer dependencies are satisfied
whether critical-path dependencies are satisfied
whether evidence exists and is fresh for the reviewed commit
whether evidence hashes are complete and reproducible
whether source mutation checks pass
whether runtime artifact boundaries are respected
whether release readiness passes or is explicitly not claimed
whether all implemented required layers are validated
whether deferred layers are safely recorded
whether final acceptance evidence is reproducible
whether unresolved blockers remain
whether the final system verdict is ACCEPTED or NOT_ACCEPTED
```

Final acceptance does **not** mean perfect forever.

It means:

```text
all layers required in the declared acceptance scope pass their acceptance gates
all deferred layers are explicitly recorded
all safety-critical deferrals are blocked or safely stubbed
all required evidence is present
all validation commands are reproducible
all required hashes are present
no unresolved BLOCKER remains
final verdict is recorded as ACCEPTED or NOT_ACCEPTED
```

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because Final System Acceptance decides whether Agent_X is safe and validated enough to be considered accepted within the declared scope.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if final acceptance runner exposes CLI commands
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, only if final acceptance directly validates MCP runtime behavior
Release / Promotion Acceptance Criteria, if this layer produces release-ready verdicts
```

## 2.4 Optional Standards

```text
ES, for ecosystem placement
Report Template, because this layer should produce final acceptance reports
```

---

# 3. Why This Layer Needs These Standards

Final System Acceptance is safety-critical because it decides:

```text
whether all required Agent_X layers exist
whether every required layer is validated
whether compileall and pytest pass
whether schema validation passes
whether evidence exists and is hashable
whether evidence is fresh enough for the reviewed commit
whether runtime artifacts are inside approved boundaries
whether policy, sandbox, patch, tools, models, orchestrator, monitoring, backup, and release gates are mutually consistent
whether any layer has unresolved blockers
whether deferred items are safe
whether the system can be marked accepted
whether release readiness is valid or not claimed
whether final acceptance evidence is reproducible
```

This layer validates the complete Agent_X stack. It must not implement new agent behavior, patch behavior, model behavior, runtime model behavior, promotion behavior, orchestration behavior, or deployment behavior. It only reviews, checks, aggregates, verifies, and records the final system verdict.

---

# 4. Review Target

Fill this section after implementation.

```text
review_target_commit: <commit hash>
review_target_branch: <branch name>
review_date_utc: <timestamp>
reviewer: <name or tool>
repository: https://github.com/Astrocytech/Agent_X
acceptance_scope_id: <scope id>
acceptance_scope_name: <scope name>
acceptance_scope_version: <scope version>
working_tree_start_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
working_tree_end_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
review_environment:
  os: <name/version>
  python_version: <version>
  pytest_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

The review is invalid if the acceptance scope is not recorded.

---

# 5. Acceptance Scope Rules

Final acceptance must be tied to a declared scope.

The scope must define which layers are:

```text
REQUIRED_NOW
REQUIRED_FOR_RELEASE
OPTIONAL
FUTURE_DEFERRED
NOT_APPLICABLE
```

Use these meanings:

| Scope Status | Meaning | ACCEPTED allowed? |
|---|---|---|
| REQUIRED_NOW | Must exist, validate, and provide evidence for this final acceptance pass. | Yes, only if PASS / VALIDATED |
| REQUIRED_FOR_RELEASE | Not required for internal system acceptance, but required before release-ready status can be claimed. | Yes for ACCEPTED, No for RELEASE_READY if missing |
| OPTIONAL | Useful but not required for acceptance. | Yes if absence is recorded |
| FUTURE_DEFERRED | Planned future layer or feature; must be safely inert if any code exists. | Yes only if DEFERRED SAFELY |
| NOT_APPLICABLE | Truly outside the current Agent_X scope and no runtime entry point exists. | Yes if justified |

The scope must include at least:

```text
Layer 0 seed kernel
Layer 1 standards / framework contracts
Layer 2 profiles / SIB / ES / EQC docs
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Local Model Runtime Profile
Context Builder / Task Packer
Prompt Contract / Prompt Versioning
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Git Integration
Evaluation Harness / Regression Benchmark
Long-Term Learning / Outcome Review
Documentation Synchronization
Task Queue / Session Scheduler
Monitoring / Observability
Packaging / Distribution
Backup / Disaster Recovery
Final System Acceptance
```

Safety-critical layers cannot be silently omitted.

Safety-critical layers include:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution, if source mutation is in scope
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter, if model execution is in scope
LLM Implementation Worker, if autonomous implementation is in scope
Self-Evolution Orchestrator, if autonomous evolution is in scope
Human Review / Approval Interface, if human approval is required by policies
Promotion / Release Gate, if release-ready status is claimed
Git Integration, if Git write behavior is in scope
Evaluation Harness / Regression Benchmark
Backup / Disaster Recovery, if release-ready status is claimed
Final System Acceptance
```

---

# 6. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT_CHECKED
NOT_RUN
NOT_APPLICABLE
DEFERRED_SAFELY
```

| Status | Meaning | Final ACCEPTED allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present, but coverage is incomplete. | No, unless explicitly non-blocking and documented |
| FAIL | Requirement was checked and failed. | No |
| NOT_CHECKED | Requirement was not validated. | No |
| NOT_RUN | Required command or executable check was not run. | No |
| NOT_APPLICABLE | Requirement does not apply to the implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED_SAFELY | Feature or layer is intentionally deferred and cannot execute unsafe behavior. | Yes, only if recorded and non-blocking |

A review cannot mark the system `ACCEPTED` if any `REQUIRED_NOW` area remains `NOT_CHECKED`, any required command remains `NOT_RUN`, or any required evidence is stale or missing.

---

# 7. Final Acceptance Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] acceptance scope is recorded
[ ] validation was run against that exact commit or a documented clean equivalent
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, summary, and output artifact
[ ] every command marked PASS has exit_code 0
[ ] every command marked expected-failure records the expected failure condition
[ ] layer completion matrix exists
[ ] dependency matrix exists
[ ] critical-path dependency summary exists
[ ] evidence manifest exists
[ ] evidence freshness report exists
[ ] runtime artifact report exists
[ ] release readiness report exists or release-ready status is explicitly NOT_CLAIMED
[ ] review report artifact exists
[ ] completion record exists
[ ] required evidence hashes are present
[ ] self-hash handling is reproducible
[ ] circular self-validation is handled explicitly
[ ] reviewer did not rely only on any document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `ACCEPTED` because this document says `review_document_rating: 10/10`. The system can be marked `ACCEPTED` only when recorded validation evidence satisfies the ACCEPTED criteria.

---

# 8. Circular Self-Validation Rule

The Final System Acceptance Layer must validate itself without circularly granting itself acceptance.

Required rule:

```text
1. Validate all prerequisite layers first.
2. Validate Final System Acceptance implementation structure, schemas, tests, runner, and evidence generation independently.
3. Run the final acceptance runner only after its own unit/schema tests pass.
4. The runner may include its own output in the final evidence set, but it cannot be the only evidence proving itself.
5. Final ACCEPTED requires independent compileall, pytest, schema validation, source mutation, and artifact boundary evidence.
```

Blocking if:

```text
Final acceptance runner marks itself ACCEPTED without independent tests
Final acceptance completion record is used as sole proof that final acceptance works
self-validation evidence is missing
```

---

# 9. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall L0 L1 L2 tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_final_system_acceptance_schemas.py
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.acceptance_runner --repo-root . --mode final-review --scope <scope-id> --output-root .agentx-init/final_acceptance
git status --short
```

If the exact final acceptance runner path differs, record the actual command and explain the deviation.

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final acceptance runner: PASS, exit_code 0 if ACCEPTED is claimed
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
running MCP server
external service credentials
```

---

# 10. CLI / Command Acceptance Rules

If the final acceptance runner exposes a CLI, it must obey these rules.

Required CLI behavior:

```text
--help exits 0 and prints usage
--repo-root is explicit or defaults to current repository root safely
--scope is explicit for final acceptance claims
--mode final-review is deterministic
--output-root defaults to .agentx-init/final_acceptance/
--json or equivalent machine-readable mode is available
ACCEPTED exits 0
NOT_ACCEPTED exits non-zero unless --allow-not-accepted-exit-zero is explicitly used for report-only mode
invalid arguments exit non-zero
missing required evidence exits non-zero
schema validation failure exits non-zero
runtime artifact boundary failure exits non-zero
source mutation failure exits non-zero
```

A final `ACCEPTED` verdict is invalid if the runner reports `ACCEPTED` but exits non-zero, or if it exits zero while the report verdict is `NOT_ACCEPTED` without an explicitly documented report-only mode.

---

# 11. Expected Implementation Scope

## 11.1 Required Package

Expected location:

```text
tools/agentx_evolve/final_acceptance/
```

Expected files:

```text
tools/agentx_evolve/final_acceptance/__init__.py
tools/agentx_evolve/final_acceptance/acceptance_models.py
tools/agentx_evolve/final_acceptance/layer_catalog.py
tools/agentx_evolve/final_acceptance/layer_completion_matrix.py
tools/agentx_evolve/final_acceptance/cross_layer_dependency_checker.py
tools/agentx_evolve/final_acceptance/evidence_collector.py
tools/agentx_evolve/final_acceptance/evidence_freshness_checker.py
tools/agentx_evolve/final_acceptance/runtime_artifact_checker.py
tools/agentx_evolve/final_acceptance/release_readiness_checker.py
tools/agentx_evolve/final_acceptance/final_report_writer.py
tools/agentx_evolve/final_acceptance/acceptance_runner.py
```

## 11.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
final_acceptance_scope.schema.json
final_acceptance_layer_record.schema.json
final_acceptance_layer_matrix.schema.json
final_acceptance_dependency_matrix.schema.json
final_acceptance_evidence_manifest.schema.json
final_acceptance_evidence_freshness_report.schema.json
final_acceptance_runtime_artifact_report.schema.json
final_acceptance_release_readiness_report.schema.json
final_acceptance_review_report.schema.json
final_acceptance_completion_record.schema.json
```

## 11.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_final_acceptance_models.py
test_final_acceptance_layer_catalog.py
test_final_acceptance_layer_completion_matrix.py
test_final_acceptance_cross_layer_dependencies.py
test_final_acceptance_evidence_collector.py
test_final_acceptance_evidence_freshness.py
test_final_acceptance_runtime_artifact_boundary.py
test_final_acceptance_release_readiness.py
test_final_acceptance_runner.py
test_final_acceptance_report_writer.py
test_final_acceptance_schema_validation.py
test_final_acceptance_negative_cases.py
```

## 11.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/final_acceptance/
```

Expected artifacts:

```text
final_acceptance_scope.json
final_acceptance_layer_matrix.json
final_acceptance_dependency_matrix.json
final_acceptance_evidence_manifest.json
final_acceptance_evidence_freshness_report.json
final_acceptance_runtime_artifact_report.json
final_acceptance_release_readiness_report.json
final_acceptance_review_report.json
final_acceptance_completion_record.json
final_acceptance_command_output_compileall.txt
final_acceptance_command_output_pytest.txt
final_acceptance_command_output_schema_validation.txt
final_acceptance_command_output_runner.txt
```

---

# 12. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Acceptance scope | scope exists and classifies all layers | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Final acceptance package | `tools/agentx_evolve/final_acceptance/` exists | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Schemas | all required final acceptance schemas exist | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Tests | all required final acceptance tests exist | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Acceptance runner | deterministic runner exists with CLI semantics | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Layer catalog | all Agent_X layers listed and classified | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Layer completion matrix | every required layer has status and evidence | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Cross-layer dependencies | direct and transitive dependencies checked | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Critical path | safety-critical path is complete or safely deferred | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Evidence manifest | evidence exists, hashes present | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Evidence freshness | layer evidence matches or is valid for reviewed commit | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Runtime artifact boundary | artifacts inside approved roots or deviations recorded | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Release readiness | report produced; release-ready status valid or not claimed | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Source mutation safety | final review does not mutate source | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Deferred layer handling | deferred items are safe and recorded | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Circular self-validation | independent self-validation exists | PASS / PARTIAL / FAIL / NOT_CHECKED |
| Final verdict | ACCEPTED / NOT_ACCEPTED is recorded | PASS / PARTIAL / FAIL / NOT_CHECKED |

---

# 13. What Exists Checklist

## 13.1 Package Files

```text
[ ] tools/agentx_evolve/final_acceptance/__init__.py
[ ] tools/agentx_evolve/final_acceptance/acceptance_models.py
[ ] tools/agentx_evolve/final_acceptance/layer_catalog.py
[ ] tools/agentx_evolve/final_acceptance/layer_completion_matrix.py
[ ] tools/agentx_evolve/final_acceptance/cross_layer_dependency_checker.py
[ ] tools/agentx_evolve/final_acceptance/evidence_collector.py
[ ] tools/agentx_evolve/final_acceptance/evidence_freshness_checker.py
[ ] tools/agentx_evolve/final_acceptance/runtime_artifact_checker.py
[ ] tools/agentx_evolve/final_acceptance/release_readiness_checker.py
[ ] tools/agentx_evolve/final_acceptance/final_report_writer.py
[ ] tools/agentx_evolve/final_acceptance/acceptance_runner.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

## 13.2 Schema Files

```text
[ ] final_acceptance_scope.schema.json
[ ] final_acceptance_layer_record.schema.json
[ ] final_acceptance_layer_matrix.schema.json
[ ] final_acceptance_dependency_matrix.schema.json
[ ] final_acceptance_evidence_manifest.schema.json
[ ] final_acceptance_evidence_freshness_report.schema.json
[ ] final_acceptance_runtime_artifact_report.schema.json
[ ] final_acceptance_release_readiness_report.schema.json
[ ] final_acceptance_review_report.schema.json
[ ] final_acceptance_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

## 13.3 Test Files

```text
[ ] test_final_acceptance_models.py
[ ] test_final_acceptance_layer_catalog.py
[ ] test_final_acceptance_layer_completion_matrix.py
[ ] test_final_acceptance_cross_layer_dependencies.py
[ ] test_final_acceptance_evidence_collector.py
[ ] test_final_acceptance_evidence_freshness.py
[ ] test_final_acceptance_runtime_artifact_boundary.py
[ ] test_final_acceptance_release_readiness.py
[ ] test_final_acceptance_runner.py
[ ] test_final_acceptance_report_writer.py
[ ] test_final_acceptance_schema_validation.py
[ ] test_final_acceptance_negative_cases.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

---

# 14. Validation Commands

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall L0 L1 L2 tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_final_system_acceptance_schemas.py
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.acceptance_runner --repo-root . --mode final-review --scope <scope-id> --output-root .agentx-init/final_acceptance
git status --short
```

If the full pytest suite contains future or intentionally deferred tests, also record a scoped command for final acceptance tests:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_final_acceptance_models.py \
  tools/agentx_evolve/tests/test_final_acceptance_layer_catalog.py \
  tools/agentx_evolve/tests/test_final_acceptance_layer_completion_matrix.py \
  tools/agentx_evolve/tests/test_final_acceptance_cross_layer_dependencies.py \
  tools/agentx_evolve/tests/test_final_acceptance_evidence_collector.py \
  tools/agentx_evolve/tests/test_final_acceptance_evidence_freshness.py \
  tools/agentx_evolve/tests/test_final_acceptance_runtime_artifact_boundary.py \
  tools/agentx_evolve/tests/test_final_acceptance_release_readiness.py \
  tools/agentx_evolve/tests/test_final_acceptance_runner.py \
  tools/agentx_evolve/tests/test_final_acceptance_report_writer.py \
  tools/agentx_evolve/tests/test_final_acceptance_schema_validation.py \
  tools/agentx_evolve/tests/test_final_acceptance_negative_cases.py
```

---

# 15. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall L0 L1 L2 tools
exit_code: <integer>
status: PASS | FAIL | NOT_RUN
summary: <paste summary>
failures: <none or list>
output_artifact: .agentx-init/final_acceptance/final_acceptance_command_output_compileall.txt
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required Agent_X Python file fails compile
any final acceptance module fails compile
exit code is missing
output hash is missing for final ACCEPTED
```

---

# 16. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest
scoped_command: <optional scoped command>
exit_code: <integer>
status: PASS | FAIL | NOT_RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: .agentx-init/final_acceptance/final_acceptance_command_output_pytest.txt
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
required final acceptance tests fail
safety-critical layer tests fail
pytest is not run
exit code is missing
output hash is missing for final ACCEPTED
```

---

# 17. Schema Validation Result

Record the schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_final_system_acceptance_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_final_acceptance_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT_RUN
summary: <paste summary>
failures: <none or list>
output_artifact: .agentx-init/final_acceptance/final_acceptance_command_output_schema_validation.txt
output_sha256: <sha256>
```

Required schema tests:

```text
acceptance scope schema accepts valid scope
layer record schema accepts valid layer record
layer matrix schema accepts valid matrix
dependency matrix schema accepts valid dependency records
evidence manifest schema accepts valid evidence manifest
evidence freshness report schema accepts valid report
runtime artifact report schema accepts valid report
release readiness report schema accepts valid report
review report schema accepts valid final review report
completion record schema accepts valid completion record
schemas reject missing required fields
schemas reject invalid status values
schemas reject invalid final verdict values
schemas reject invalid scope status values
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
schema-invalid final acceptance records are accepted
schema-invalid completion records are accepted
final verdict schema cannot represent ACCEPTED and NOT_ACCEPTED
scope schema cannot represent required/deferred/not-applicable status
hash/evidence fields are not representable
exit code is missing
```

---

# 18. Final Acceptance Runner Result

Record the runner result.

```text
command: PYTHONPATH=tools python -m agentx_evolve.final_acceptance.acceptance_runner --repo-root . --mode final-review --scope <scope-id> --output-root .agentx-init/final_acceptance
exit_code: <integer>
status: PASS | FAIL | NOT_RUN
reported_verdict: ACCEPTED | NOT_ACCEPTED
summary: <paste summary>
output_artifact: .agentx-init/final_acceptance/final_acceptance_command_output_runner.txt
output_sha256: <sha256>
```

Acceptance:

```text
PASS required for ACCEPTED
exit_code must be 0 for ACCEPTED
reported_verdict must equal final review verdict
```

Blocking if:

```text
runner not run
runner exits zero while reporting NOT_ACCEPTED without report-only mode
runner reports ACCEPTED while any BLOCKER exists
runner output artifact or hash missing for final ACCEPTED
```

---

# 19. Layer Completion Matrix Result

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_layer_matrix.json
```

The matrix must include every required Agent_X layer.

Required fields per layer:

```text
layer_id
layer_name
roadmap_order
scope_status
validation_status
required_for_acceptance
required_for_release
criticality
implementation_commit
review_document
review_document_version
completion_record_path
completion_record_sha256
evidence_manifest_path
evidence_manifest_sha256
review_report_path
review_report_sha256
tests_status
schema_status
runtime_artifact_status
source_mutation_status
blockers
high_issues
accepted_deviations
safe_deferral_reason
freshness_status
```

Required result:

```text
all REQUIRED_NOW layers are VALIDATED
all FUTURE_DEFERRED layers are DEFERRED_SAFELY with reason and evidence
no safety-critical layer is NOT_CHECKED
no safety-critical REQUIRED_NOW layer is NOT_IMPLEMENTED
no layer claims VALIDATED without a completion record
no layer claims VALIDATED with unresolved BLOCKER
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
required layer missing from matrix
safety-critical layer lacks status
safety-critical layer lacks evidence
layer claims VALIDATED without completion record
layer evidence is stale and not justified
layer has unresolved BLOCKER
unsafe deferral is marked DEFERRED_SAFELY
```

---

# 20. Evidence Freshness Result

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_evidence_freshness_report.json
```

Required freshness checks:

```text
layer completion record commit equals reviewed commit, or
layer completion record commit is an ancestor of reviewed commit and changed files since then do not affect that layer, or
layer has been revalidated for the reviewed commit
```

Required fields per layer:

```text
layer_id
layer_name
layer_evidence_commit
reviewed_commit
commit_relation
changed_files_since_layer_validation
affected_by_changes
freshness_status
reason
```

Allowed freshness statuses:

```text
FRESH
STALE_BUT_UNAFFECTED
STALE_REQUIRES_REVALIDATION
NOT_CHECKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
required layer evidence is stale and affected by changes
commit relation is unknown
changed files affecting required layer are not checked
freshness report is missing
```

---

# 21. Cross-Layer Dependency Result

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_dependency_matrix.json
```

The dependency matrix must prove that layer relationships are consistent.

Required dependency checks:

```text
Tool / MCP Adapter depends on Security Sandbox, Policy / Capability Registry, Failure Taxonomy, Governed Patch Execution status/precheck rules
Model Adapter depends on Policy, Prompt Contract, Evaluation Harness, and runtime profile rules
LLM Implementation Worker depends on Model Adapter, Context Builder, Prompt Contract, Tool / MCP Adapter, Policy, Sandbox
Self-Evolution Orchestrator depends on Tool / MCP Adapter, Patch Execution, Human Review, Promotion Gate, Evaluation Harness
Promotion / Release Gate depends on Git Integration, Evaluation Harness, Documentation Sync, Backup / Disaster Recovery
Monitoring / Observability depends on evidence and runtime artifact conventions
Packaging / Distribution depends on release gate and backup/recovery status if release-ready is claimed
Backup / Disaster Recovery depends on packaging, runtime artifacts, repository state, and recovery tests
Final System Acceptance depends on evidence from all REQUIRED_NOW layers
```

Required graph checks:

```text
direct dependencies checked
transitive dependencies checked
critical path checked
dependency cycles detected and classified
unsafe bypass paths rejected
deferred dependency edges recorded with compensating controls
```

Required result:

```text
all required dependency edges are satisfied
missing dependencies are blocked or safely deferred
no layer depends on an unsafe or unvalidated mutating capability
no tool path bypasses policy or sandbox
no release path bypasses promotion gate if release-ready is claimed
final acceptance cannot pass without evidence from REQUIRED_NOW layers
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
required dependency missing
unsafe dependency bypass exists
mutating layer can operate without policy/sandbox/governance
release readiness can pass without promotion/release gate checks
final acceptance can pass without evidence from required layers
dependency cycle enables bypass or unvalidated acceptance
transitive dependency status is not checked
```

---

# 22. Critical-Path Result

The final review must identify the safety-critical path that makes Agent_X safe to operate within the declared scope.

Minimum critical path when autonomous evolution is in scope:

```text
Security Sandbox
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Prompt Contract / Prompt Versioning
Context Builder / Task Packer
LLM Implementation Worker
Governed Patch Execution
Human Review / Approval Interface
Promotion / Release Gate
Evaluation Harness / Regression Benchmark
Git Integration
Backup / Disaster Recovery
Final System Acceptance
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED | NOT_APPLICABLE
```

Blocking if:

```text
autonomous evolution is in scope but critical path is incomplete
a mutating path exists without sandbox/policy/governance/human-review controls
release-ready status is claimed without promotion, evaluation, Git, packaging, and backup controls
```

---

# 23. Evidence Manifest Result

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "final_acceptance_evidence_manifest.schema.json",
  "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "acceptance_scope_id": "<scope id>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [],
  "layer_evidence": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "evidence_freshness_status": "PASS",
  "release_ready_claimed": false,
  "final_verdict": "ACCEPTED"
}
```

The manifest must include SHA-256 hashes for:

```text
final_acceptance_scope.json
final_acceptance_layer_matrix.json
final_acceptance_dependency_matrix.json
final_acceptance_evidence_manifest.json
final_acceptance_evidence_freshness_report.json
final_acceptance_runtime_artifact_report.json
final_acceptance_release_readiness_report.json
final_acceptance_review_report.json
final_acceptance_completion_record.json
command output artifacts
layer completion records used by final acceptance
layer evidence manifests used by final acceptance
layer review reports used by final acceptance
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final ACCEPTED verdict is invalid if required final evidence hashes are missing.
```

Self-hash rule:

```text
If a file contains its own hash, compute the hash over a canonicalized copy with the self-hash field set to null or "<SELF_HASH_PENDING>".
The canonicalization method must be recorded in the evidence manifest.
Alternatively, store self-hashes in a separate hash index file and hash the manifest without embedding its own hash.
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
evidence manifest missing
evidence hashes missing
self-hash method missing or not reproducible
reviewed commit missing
command exit codes missing
layer evidence references missing
manual evidence is not traceable
```

---

# 24. Source Mutation Check

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
only expected runtime artifacts under approved runtime roots
```

Approved runtime roots:

```text
.agentx-init/
```

Primary final acceptance runtime root:

```text
.agentx-init/final_acceptance/
```

Status:

```text
PASS | FAIL | NOT_CHECKED
```

Blocking if:

```text
source files are modified by final acceptance validation
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots without deviation
final acceptance runner changes implementation files
```

---

# 25. Runtime Artifact Boundary Check

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_runtime_artifact_report.json
```

Required checks:

```text
all final acceptance artifacts are under .agentx-init/final_acceptance/
referenced layer artifacts are under approved .agentx-init/ subdirectories
no source directories are used for runtime state
no evidence is written into L0, L1, L2, tools source directories, or schema directories
exceptions are listed in deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
unapproved runtime artifact path exists
source directory is used for runtime state
runtime artifact boundary exceptions lack deviation entry
acceptance runner mutates source files
```

---

# 26. Release Readiness Result

Create and validate:

```text
.agentx-init/final_acceptance/final_acceptance_release_readiness_report.json
```

Final acceptance and release readiness are related but not identical.

Allowed release readiness statuses:

```text
RELEASE_READY
NOT_RELEASE_READY
NOT_CLAIMED
```

Release readiness must check:

```text
all REQUIRED_NOW and REQUIRED_FOR_RELEASE layers are validated
all safety-critical deferrals are safe and recorded
compileall passes
pytest passes
schema validation passes
final acceptance runner passes
source mutation check passes
runtime artifact boundary check passes
evidence manifest exists and hashes are present
review report exists
completion record exists
remaining blockers are empty
promotion / release gate status is compatible with release readiness
backup / disaster recovery status is compatible with release readiness
packaging / distribution status is compatible with release readiness
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED | NOT_APPLICABLE
```

Blocking if release-ready status is claimed and:

```text
release readiness report missing
promotion or release gate is bypassed
backup / disaster recovery layer is missing when required
packaging / distribution layer is missing when required
system claims release-ready with unresolved BLOCKER
```

Final `ACCEPTED` may still be possible when release readiness is `NOT_CLAIMED`, but only if the acceptance scope explicitly says release readiness is not being claimed.

---

# 27. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
final acceptance runner:
acceptance scope:
layer completion matrix:
evidence freshness:
cross-layer dependency matrix:
critical path:
evidence manifest:
evidence hashes:
runtime artifact boundary:
source mutation check:
release readiness:
review report:
completion record:
circular self-validation:
```

---

# 28. What Failed

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
stale_evidence_items:
  - <none or list>
unsafe_deferrals:
  - <none or list>
```

---

# 29. Issue Severity Classification

## 29.1 BLOCKER

The system cannot be marked accepted if any BLOCKER exists.

```text
reviewed commit is missing
acceptance scope is missing
review environment is missing
required command exit code is missing
compileall fails
pytest fails
schema validation fails
final acceptance runner fails for ACCEPTED claim
required layer missing from completion matrix
REQUIRED_NOW layer lacks evidence
REQUIRED_NOW layer evidence is stale and affected by code changes
REQUIRED_NOW layer has unresolved BLOCKER
cross-layer dependency check fails
critical path check fails for active scope
evidence manifest is missing
evidence hashes are missing
self-hash method is missing or irreproducible
runtime artifact boundary fails
source mutation check fails
release readiness fails when release-ready is claimed
final review report is missing
completion record is missing
circular self-validation exists
unsafe deferral is marked DEFERRED_SAFELY
final verdict is missing
required area remains NOT_CHECKED
required command remains NOT_RUN
```

## 29.2 HIGH

High issues must be fixed before final acceptance unless explicitly outside active runtime scope and recorded as safe.

```text
incomplete evidence references
partial layer evidence for non-critical layer
partial dependency coverage for non-critical edge
missing non-critical layer review document
runtime artifact boundary exception lacks detail
review environment partially recorded
deferred layer lacks sufficient future-work note
release readiness is NOT_CLAIMED but release scope is ambiguous
```

## 29.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled future-layer files
optional ecosystem placement not complete
optional report formatting issue
non-runtime future layer explicitly deferred safely
release readiness not claimed for internal acceptance scope
```

---

# 30. GO / NO-GO Rules

## 30.1 ACCEPTED Criteria

The system may be marked `ACCEPTED` only if:

```text
reviewed commit is recorded
acceptance scope is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
final acceptance runner passes with exit code 0 for ACCEPTED claim
acceptance scope check passes
layer completion matrix passes
evidence freshness passes
cross-layer dependency matrix passes
critical-path check passes for active scope
evidence manifest exists
evidence hashes exist
self-hash method is reproducible
runtime artifact boundary passes
source mutation check passes
release readiness passes or is explicitly NOT_CLAIMED by scope
review report exists
completion record exists
circular self-validation rule passes
no required area remains NOT_CHECKED
no required command remains NOT_RUN
no unresolved BLOCKER exists
all accepted deviations are non-blocking or safely deferred
final verdict is recorded as ACCEPTED
```

## 30.2 NOT_ACCEPTED Criteria

The system must remain `NOT_ACCEPTED` if any are true:

```text
reviewed commit is not recorded
acceptance scope is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
final acceptance runner fails for ACCEPTED claim
required layer is missing or unvalidated
required layer evidence is stale and affected by changes
cross-layer dependency check fails
critical path check fails for active scope
evidence manifest is missing
evidence hashes are missing
self-hash method is missing or invalid
runtime artifact boundary fails
source mutation check fails
release readiness fails when release-ready is claimed
review report is missing
completion record is missing
any required area remains NOT_CHECKED
any required command remains NOT_RUN
any unresolved BLOCKER remains
unsafe deferral exists
circular self-validation exists
```

---

# 31. Remediation Rules

If final acceptance fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix final acceptance runner command
fix acceptance scope definitions
fix layer catalog entries
fix layer completion evidence references
fix stale evidence checks
fix dependency matrix checks
fix critical-path checks
fix evidence manifest generation
fix SHA-256 hashing and self-hash handling
fix runtime artifact path checks
fix source mutation detection
fix release readiness logic
fix tests to reflect the contract
fix review report generation
fix completion record generation
```

Forbidden fixes:

```text
do not mark NOT_CHECKED as PASS
do not mark NOT_RUN as PASS
do not mark unsafe deferral as DEFERRED_SAFELY
do not ignore failed layer evidence
do not ignore stale evidence affected by code changes
do not bypass dependency checks
do not remove required layers from the matrix to pass
do not downgrade safety-critical layers to optional without scope revision
do not omit evidence hashes
do not fake self-hashes
do not write runtime artifacts into source directories
do not accept unresolved BLOCKER items
do not claim ACCEPTED without reviewed commit and command exit codes
do not claim release-ready without promotion, packaging, backup, and release evidence
do not weaken policy, sandbox, patch, tool, model, orchestrator, release, monitoring, or backup gates to pass final acceptance
```

---

# 32. Deviation Register

Any exception, deferral, stale-but-accepted evidence item, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Layer | Dependency | Evidence | Evidence Freshness | Runtime Artifact Boundary | Release Readiness | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high | critical>
    compensating_control: <test/evidence/control>
    accepted_status: NOT_APPLICABLE | DEFERRED_SAFELY | NON_BLOCKING_FOLLOW_UP | STALE_BUT_UNAFFECTED
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for final ACCEPTED unless proven outside the active runtime path.
Runtime artifact writes outside approved roots require a deviation entry.
Deferred safety-critical layers require a deviation entry and blocking/stub proof.
Stale evidence requires a freshness entry proving the layer is unaffected.
Missing evidence hashes cannot be accepted as a deviation for ACCEPTED.
```

---

# 33. Review Report Artifact

Create:

```text
.agentx-init/final_acceptance/final_acceptance_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "final_acceptance_review_report.schema.json",
  "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
  "review_document_id": "FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "acceptance_scope_id": "<scope id>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "layer_completion_matrix_path": ".agentx-init/final_acceptance/final_acceptance_layer_matrix.json",
  "layer_completion_matrix_sha256": "<sha256>",
  "dependency_matrix_path": ".agentx-init/final_acceptance/final_acceptance_dependency_matrix.json",
  "dependency_matrix_sha256": "<sha256>",
  "evidence_freshness_report_path": ".agentx-init/final_acceptance/final_acceptance_evidence_freshness_report.json",
  "evidence_freshness_report_sha256": "<sha256>",
  "evidence_manifest_path": ".agentx-init/final_acceptance/final_acceptance_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "runtime_artifact_report_path": ".agentx-init/final_acceptance/final_acceptance_runtime_artifact_report.json",
  "runtime_artifact_report_sha256": "<sha256>",
  "release_readiness_report_path": ".agentx-init/final_acceptance/final_acceptance_release_readiness_report.json",
  "release_readiness_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/final_acceptance/final_acceptance_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "self_hash_method": "canonicalize_self_hash_field",
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "release_ready_status": "RELEASE_READY | NOT_RELEASE_READY | NOT_CLAIMED",
  "implementation_rating": 10.0,
  "final_verdict": "ACCEPTED"
}
```

The review report is the bridge between this template and the actual implementation. A final `ACCEPTED` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit and scope, or if it lacks command exit codes and evidence hashes.

---

# 34. Evidence Immutability Rule

After the review report records a final `ACCEPTED` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous ACCEPTED verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 35. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Scope, structure, and expected files | 1.0 | Acceptance scope, package, schemas, tests, and runtime paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0 and output hash. |
| Pytest | 1.0 | Relevant test suite passes with exit code 0 and output hash. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including scope and freshness schemas. |
| Layer completion matrix and evidence freshness | 1.0 | Every REQUIRED_NOW layer has valid, fresh evidence. |
| Cross-layer dependencies and critical path | 1.0 | Direct/transitive dependency edges and safety-critical path pass. |
| Evidence manifest and hashes | 1.0 | Evidence manifest exists with SHA-256 hashes and reproducible self-hash handling. |
| Runtime artifact and source mutation safety | 1.0 | Artifact boundaries pass and source is not mutated. |
| Release readiness handling | 1.0 | Release readiness passes or is explicitly not claimed by scope. |
| Final report, completion record, and self-validation | 1.0 | Review report, completion record, verdict, rating, and circular self-validation proof are recorded. |

Scoring rule:

```text
10.0 = fully ACCEPTED
9.0-9.9 = strong but NOT_ACCEPTED if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not final-system complete
below 7.0 = not acceptable for final system acceptance
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing acceptance scope caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
layer completion matrix FAIL caps score at 6.5
evidence freshness FAIL caps score at 6.5
cross-layer dependency FAIL caps score at 6.5
critical-path FAIL caps score at 6.5
evidence manifest missing caps score at 7.0
evidence hashes missing caps score at 8.0
self-hash method missing caps score at 8.0
runtime artifact boundary FAIL caps score at 7.0
source mutation check FAIL caps score at 7.0
release readiness FAIL caps score at 7.0 if release-ready is claimed
review report missing caps score at 8.0
completion record missing caps score at 8.0
circular self-validation caps score at 7.0
any NOT_CHECKED required area caps score at 8.0
any NOT_RUN required command caps score at 8.0
unresolved BLOCKER caps score at 6.0
unsafe deferral caps score at 6.0
```

---

# 36. Scope Freeze and Scope-Change Control

Final acceptance scope must be frozen before final validation begins.

Required scope freeze artifact:

```text
.agentx-init/final_acceptance/final_acceptance_scope.json
```

Required fields:

```text
scope_id
scope_version
scope_created_at
scope_frozen_at
scope_author
reviewed_commit
layer_scope_records
safety_critical_layers
release_ready_claimed
scope_change_history
scope_sha256
```

Rules:

```text
Scope cannot be narrowed after validation starts unless a new scope version is created.
Scope cannot reclassify a failing REQUIRED_NOW safety-critical layer as OPTIONAL to obtain ACCEPTED.
Scope cannot mark a runtime-reachable layer as NOT_APPLICABLE.
Scope changes after validation require re-running final acceptance.
Scope changes must be recorded in the deviation register and scope_change_history.
```

Blocking if:

```text
acceptance scope is changed after validation without revalidation
failing safety-critical layer is reclassified to avoid failure
runtime-reachable layer is marked NOT_APPLICABLE
scope hash is missing or mismatched
```

---

# 37. Evidence Source-of-Truth and Conflict Resolution

Final acceptance must define which evidence wins when records disagree.

Source-of-truth precedence:

```text
1. Actual command exit code and captured command output
2. Current Git state at reviewed commit
3. Layer review report with matching commit and valid hash
4. Layer evidence manifest with matching commit and valid hash
5. Layer completion record with matching commit and valid hash
6. Manual reviewer note, only as explanation, never as sole proof
```

Conflict rules:

```text
If command output says FAIL but completion record says VALIDATED, final acceptance treats the layer as FAIL.
If layer review report and completion record disagree, final acceptance treats the stricter status as authoritative.
If artifact hash mismatches, the artifact is invalid until regenerated and revalidated.
If reviewed commit differs across artifacts, evidence freshness must resolve the mismatch or final acceptance fails.
If release readiness status differs across artifacts, the least permissive status wins.
```

Blocking if:

```text
conflicting evidence is ignored
manual notes override command failure
completion record is accepted despite hash mismatch
layer is treated as VALIDATED when its review report says NOT DONE / NOT_ACCEPTED / BLOCKED
```

---

# 38. Blocker Propagation and Deviation Inheritance

Unresolved blockers propagate upward. Final acceptance cannot hide blocker status inside lower-layer evidence.

Required propagation rules:

```text
Any unresolved BLOCKER in a REQUIRED_NOW layer becomes a final acceptance BLOCKER.
Any unresolved BLOCKER in a dependency of a REQUIRED_NOW layer becomes a final acceptance BLOCKER.
Any HIGH issue in a safety-critical runtime path must be resolved or proven outside active scope.
Accepted deviations from lower layers must be re-evaluated at final-system level.
A lower-layer non-blocking deviation may become blocking if combined with another layer.
```

Examples of system-level escalation:

```text
Tool / MCP Adapter has mutating tools safely hidden, but MCP runtime later exposes them -> BLOCKER.
Policy Registry has deferred network policy, and Model Adapter enables hosted network calls -> BLOCKER unless explicit release scope permits it.
Patch layer has safe stubs, but Orchestrator can call patch apply directly -> BLOCKER.
Evidence hash missing in a lower layer used for final acceptance -> BLOCKER for ACCEPTED.
```

Required fields in final layer matrix:

```text
local_blockers
propagated_blockers
local_high_issues
propagated_high_issues
accepted_deviations
system_level_deviation_decision
```

---

# 39. Negative Acceptance-Runner Test Pack

The final acceptance runner must prove it fails closed, not only that it can pass happy-path data.

Required negative tests:

```text
[ ] missing acceptance scope -> NOT_ACCEPTED / non-zero exit
[ ] missing reviewed commit -> NOT_ACCEPTED / non-zero exit
[ ] missing layer completion record for REQUIRED_NOW layer -> NOT_ACCEPTED / non-zero exit
[ ] stale affected evidence -> NOT_ACCEPTED / non-zero exit
[ ] hash mismatch -> NOT_ACCEPTED / non-zero exit
[ ] unresolved lower-layer BLOCKER -> NOT_ACCEPTED / non-zero exit
[ ] unsafe deferral marked DEFERRED_SAFELY -> NOT_ACCEPTED / non-zero exit
[ ] dependency bypass path -> NOT_ACCEPTED / non-zero exit
[ ] runtime artifact outside approved root -> NOT_ACCEPTED / non-zero exit
[ ] source mutation after validation -> NOT_ACCEPTED / non-zero exit
[ ] runner reports ACCEPTED with failing command -> test fails
[ ] release-ready claimed without promotion/release evidence -> NOT_ACCEPTED or NOT_RELEASE_READY
[ ] circular self-validation only -> NOT_ACCEPTED / non-zero exit
[ ] artifact verdict mismatch -> NOT_ACCEPTED / non-zero exit
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
negative test pack is missing
runner accepts missing evidence
runner accepts hash mismatch
runner accepts unresolved lower-layer blocker
runner accepts unsafe deferral
runner accepts artifact verdict mismatch
```

---

# 40. Tamper, Hash Mismatch, and Evidence Invalidation Rules

Final acceptance evidence must be treated as immutable after sign-off.

Hash mismatch response:

```text
If any required evidence artifact hash mismatches, mark final acceptance NOT_ACCEPTED.
If a layer artifact changed after its review report, require revalidation or stale-but-unaffected proof.
If a final acceptance artifact changed after final ACCEPTED, invalidate the prior ACCEPTED verdict.
If the hash index changed, regenerate the full evidence manifest and review report.
```

Manual edit rule:

```text
Manual edits to evidence artifacts after command execution are not allowed for ACCEPTED unless explicitly recorded as deviations and re-hashed.
Manual edits cannot change command status, exit code, blocker status, layer status, or final verdict.
Manual edits to explanatory text are allowed only before final sign-off and must preserve hashes.
```

Acceptance invalidation triggers:

```text
new commit after reviewed commit
changed acceptance scope
changed final evidence artifact
changed lower-layer evidence artifact used by final acceptance
changed command output artifact
changed dependency matrix
changed layer matrix
changed release readiness claim
new unresolved blocker discovered
```

When invalidated:

```text
previous final ACCEPTED verdict becomes stale
new validation run is required
new review report and completion record are required
old evidence remains historical but not current proof
```

---

# 41. Verdict Consistency Rule

All machine-readable final acceptance artifacts must agree on the final verdict and release readiness status.

Artifacts that must agree:

```text
final_acceptance_evidence_manifest.json
final_acceptance_review_report.json
final_acceptance_completion_record.json
final_acceptance_release_readiness_report.json
final_acceptance_command_output_runner.txt or JSON equivalent
```

Required consistency:

```text
final verdict values match
release readiness values match or are explicitly explained
reviewed commit values match
acceptance scope values match
validated_at timestamps are ordered consistently
command exit codes match command status fields
```

Blocking if:

```text
manifest says ACCEPTED but review report says NOT_ACCEPTED
completion record says VALIDATED but runner output says failure
release readiness differs without explanation
reviewed commit differs without freshness resolution
```

---

# 42. Reviewer Independence and Reproducibility Rule

Final acceptance should not rely only on the same component that generated the acceptance evidence.

Required independence controls:

```text
reviewer identity recorded
commands are reproducible from fresh checkout
final acceptance runner output is independently checked against command outputs
review report is checked against evidence manifest
completion record is checked against review report
manual overrides are not allowed for blockers
```

A human or separate review agent may perform this review. If the final acceptance runner generates the report, the review must still verify:

```text
command exit codes
hashes
layer matrix
dependency matrix
evidence freshness
runtime artifact boundary
source mutation status
final verdict consistency
```

Blocking if:

```text
runner-generated ACCEPTED verdict is accepted without independent evidence checks
reviewer identity is missing
manual override changes a BLOCKER to non-blocking
```

---

# 43. Updated GO / NO-GO Addendum

The ACCEPTED criteria in Section 30.1 also require:

```text
scope is frozen before validation
scope hash is present and valid
evidence conflicts are resolved by source-of-truth precedence
all lower-layer blockers are propagated
all inherited deviations are re-evaluated at system level
negative acceptance-runner tests pass
no hash mismatch or tamper condition exists
all verdict-bearing artifacts agree
reviewer-independence checks pass
final acceptance has not been invalidated by a later commit, scope change, artifact change, or new blocker
```

The NOT_ACCEPTED criteria in Section 30.2 also include:

```text
scope changed after validation without revalidation
required artifact verdict mismatch exists
lower-layer blocker is not propagated
inherited deviation is unsafe at system level
negative acceptance-runner tests fail or are missing
evidence tamper or hash mismatch exists
reviewer-independence rule fails
acceptance invalidation trigger exists without revalidation
```

---

# 44. Definition of Done

The Final System Acceptance Layer is done when it can validate the complete Agent_X system within a declared scope without implementing new agent behavior.

It must prove:

```text
acceptance scope is declared
all final acceptance package files exist
all final acceptance schemas exist
all final acceptance tests exist
compileall passes
pytest passes
schema validation passes
final acceptance runner passes
layer completion matrix is complete
evidence freshness report passes
cross-layer dependency matrix is complete
critical-path check passes for active scope
evidence manifest is complete
evidence hashes are present
self-hash method is reproducible
runtime artifact boundary check passes
source mutation check passes
release readiness passes or is explicitly not claimed
all REQUIRED_NOW layers are validated
all deferred layers are explicitly recorded
all safety-critical deferrals are blocked or safely stubbed
no unresolved BLOCKER remains
circular self-validation rule passes
scope freeze rule passes
evidence source-of-truth conflicts are resolved
blocker propagation rule passes
negative acceptance-runner tests pass
tamper / hash mismatch checks pass
verdict consistency rule passes
reviewer-independence checks pass
review report exists
completion record exists
final verdict is recorded as ACCEPTED or NOT_ACCEPTED
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall L0 L1 L2 tools
PYTHONPATH=tools python -m pytest
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_final_system_acceptance_schemas.py
PYTHONPATH=tools python -m agentx_evolve.final_acceptance.acceptance_runner --repo-root . --mode final-review --scope <scope-id> --output-root .agentx-init/final_acceptance
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
final acceptance runner PASS, exit_code 0 for ACCEPTED claim
git status CLEAN or only expected runtime artifacts
```

---

# 45. Required Evidence Package

The final acceptance evidence package must include:

```text
acceptance scope
compileall output
pytest output
schema validation output
final acceptance runner output
layer completion matrix
evidence freshness report
dependency matrix
critical-path summary
evidence manifest
runtime artifact report
release readiness report
review report
git status output
completion record
SHA-256 hashes for final evidence artifacts
self-hash method record
scope freeze record
evidence source-of-truth conflict report
blocker propagation report
negative acceptance-runner test output
tamper / hash mismatch status
verdict consistency report
reviewer-independence status
```

The evidence package must show:

```text
reviewed commit
acceptance scope
validation timestamp
review environment
command exit codes
all required layer statuses
all required dependency statuses
evidence freshness status
no source mutation
runtime artifacts inside approved boundaries
release readiness status or NOT_CLAIMED status
no unresolved BLOCKER
final ACCEPTED or NOT_ACCEPTED verdict
```

---

# 46. Completion Evidence Record

After validation, create:

```text
.agentx-init/final_acceptance/final_acceptance_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "final_acceptance_completion_record.schema.json",
  "component_id": "AGENTX_FINAL_SYSTEM_ACCEPTANCE",
  "component_name": "Final System Acceptance Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "acceptance_scope_id": "<scope id>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/final_acceptance/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/final_acceptance/",
  "basis_documents": [
    "FINAL_SYSTEM_ACCEPTANCE_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_SPEC",
    "FINAL_SYSTEM_ACCEPTANCE_IMPLEMENTATION_REVIEW_AND_DOD_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_layers": [],
  "deferred_layers": [],
  "blocked_layers": [],
  "dependency_edges_verified": [],
  "critical_path_verified": [],
  "evidence_freshness_verified": [],
  "evidence_manifest_path": ".agentx-init/final_acceptance/final_acceptance_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/final_acceptance/final_acceptance_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "self_hash_method": "canonicalize_self_hash_field",
  "deviation_register": [],
  "unresolved_risks": [],
  "scope_freeze_status": "PASS",
  "source_of_truth_conflict_status": "PASS",
  "blocker_propagation_status": "PASS",
  "negative_acceptance_tests_status": "PASS",
  "tamper_hash_mismatch_status": "PASS",
  "verdict_consistency_status": "PASS",
  "reviewer_independence_status": "PASS",
  "acceptance_invalidation_status": "CURRENT",
  "release_ready_status": "RELEASE_READY | NOT_RELEASE_READY | NOT_CLAIMED",
  "implementation_score": 10.0,
  "final_decision": "ACCEPTED"
}
```

---

# 47. Final Accepted / Not Accepted Verdict

Fill after validation.

```text
final_verdict: ACCEPTED | NOT_ACCEPTED
release_ready_status: RELEASE_READY | NOT_RELEASE_READY | NOT_CLAIMED
implementation_rating: <0-10>
review_document_rating: 10/10
reason:
  - <summary>
remaining_blockers:
  - <none or list>
remaining_high_issues:
  - <none or list>
stale_evidence_items:
  - <none or list>
unsafe_deferrals:
  - <none or list>
accepted_non_blocking_followups:
  - <none or list>
accepted_deviations:
  - <none or list>
```

A final verdict of `ACCEPTED` is invalid if:

```text
implementation_rating is below 10.0
reviewed commit is missing
acceptance scope is missing
review environment is missing
any required command was not run
any required command exit code is missing
any required area is NOT_CHECKED
any required command is NOT_RUN
any BLOCKER remains
evidence hashes are missing
self-hash method is missing or invalid
review report is missing
completion record is missing
circular self-validation rule fails
```

---

# 48. Final Frozen Checklist

Use this checklist for the final review.

```text
Scope:
[ ] acceptance scope recorded
[ ] all layers classified as REQUIRED_NOW / REQUIRED_FOR_RELEASE / OPTIONAL / FUTURE_DEFERRED / NOT_APPLICABLE
[ ] safety-critical layers not silently omitted

Structure:
[ ] tools/agentx_evolve/final_acceptance/ exists
[ ] final acceptance schemas exist
[ ] final acceptance tests exist
[ ] final acceptance runner exists

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] final acceptance runner PASS with exit_code 0 for ACCEPTED claim
[ ] git status clean or expected runtime artifacts only

Layer Matrix:
[ ] all required layers listed
[ ] all REQUIRED_NOW layers validated
[ ] deferred layers recorded
[ ] safety-critical deferrals blocked or safely stubbed
[ ] no required layer has unresolved BLOCKER

Evidence Freshness:
[ ] layer evidence commit checked
[ ] changed files since layer validation checked
[ ] stale affected evidence rejected
[ ] freshness report written

Dependencies:
[ ] cross-layer dependency matrix exists
[ ] direct dependencies checked
[ ] transitive dependencies checked
[ ] critical path checked
[ ] no unsafe dependency bypass exists

Evidence:
[ ] evidence manifest written
[ ] layer evidence referenced
[ ] command outputs recorded
[ ] SHA-256 hashes written
[ ] self-hash method recorded
[ ] review report written
[ ] completion record written

Runtime Safety:
[ ] runtime artifact boundary passes
[ ] source mutation check passes
[ ] no final acceptance source mutation

Release Readiness:
[ ] release readiness report written
[ ] release readiness PASS or NOT_CLAIMED by scope
[ ] promotion/release gate status compatible if release-ready is claimed
[ ] backup/disaster recovery status compatible if release-ready is claimed
[ ] packaging/distribution status compatible if release-ready is claimed

Self-Validation:
[ ] final acceptance unit tests passed
[ ] final acceptance schema tests passed
[ ] final acceptance runner did not self-approve without independent evidence

Scope / Evidence Integrity:
[ ] scope frozen before validation
[ ] scope hash valid
[ ] source-of-truth precedence applied to conflicts
[ ] lower-layer blockers propagated
[ ] inherited deviations re-evaluated
[ ] negative acceptance-runner tests passed
[ ] tamper / hash mismatch checks passed
[ ] verdict-bearing artifacts agree
[ ] reviewer-independence checks passed
[ ] acceptance not invalidated by later commit, scope change, artifact change, or new blocker

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT_CHECKED
[ ] no required command is NOT_RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 49. Final Sign-Off Template

Use this after implementation validation.

```text
Final System Acceptance Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- acceptance scope: <scope id/version>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- final acceptance runner: PASS/FAIL, exit_code=<code>
- layer completion matrix: PASS/FAIL
- evidence freshness: PASS/FAIL
- cross-layer dependency matrix: PASS/FAIL
- critical path: PASS/FAIL/N/A
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- self-hash method: PRESENT/MISSING
- runtime artifact boundary: PASS/FAIL
- source mutation check: PASS/FAIL
- release readiness: RELEASE_READY/NOT_RELEASE_READY/NOT_CLAIMED
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING
- circular self-validation: PASS/FAIL
- scope freeze: PASS/FAIL
- source-of-truth conflict resolution: PASS/FAIL
- blocker propagation: PASS/FAIL
- negative acceptance-runner tests: PASS/FAIL
- tamper / hash mismatch: PASS/FAIL
- verdict consistency: PASS/FAIL
- reviewer independence: PASS/FAIL
- acceptance invalidation status: CURRENT/STALE/INVALIDATED

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- evidence freshness recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
ACCEPTED / NOT_ACCEPTED

Implementation rating:
<0-10>

Evidence paths:
- acceptance scope: <path>, sha256=<hash>
- layer matrix: <path>, sha256=<hash>
- evidence freshness report: <path>, sha256=<hash>
- dependency matrix: <path>, sha256=<hash>
- evidence manifest: <path>, sha256=<hash>
- runtime artifact report: <path>, sha256=<hash>
- release readiness report: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 50. Canonical JSON, Hashing, and Determinism Rules

Final acceptance evidence must be reproducible across machines, operating systems, and repeated runs.

Canonical JSON rule:

```text
all machine-readable final acceptance artifacts must be UTF-8 JSON
JSON must be serialized with deterministic key ordering
JSON must use normalized newline behavior
timestamps must be ISO-8601 UTC with explicit Z or +00:00
paths must be repository-relative where possible
absolute paths may appear only in environment/debug sections and must not affect acceptance hashes
arrays that represent unordered sets must be sorted deterministically before hashing
```

Hashing rule:

```text
SHA-256 is required for all final evidence artifacts
hashes must be computed over canonical artifact bytes
hashing method must be recorded in the evidence manifest
hash results must be reproducible by a fresh clone reviewer
hashes must not depend on local username, temp directory, random order, locale, or wall-clock ordering except for recorded timestamp fields
```

Blocking if:

```text
canonicalization method is missing
hashes differ across repeated clean runs without recorded reason
absolute local paths affect acceptance hashes
unordered collections produce unstable hashes
```

---

# 51. Runtime Reachability and Deferred-Layer Safety Rules

A layer may be `OPTIONAL`, `FUTURE_DEFERRED`, or `NOT_APPLICABLE` only if runtime reachability is checked.

Required reachability checks:

```text
entrypoints are listed
CLI commands are listed
registered tools are listed
MCP-exposed tools are listed if MCP is in scope
importable runtime modules are listed
configuration flags that enable the layer are listed
policy/capability rules that may call the layer are listed
orchestrator paths that may call the layer are listed
```

Rules:

```text
NOT_APPLICABLE is invalid if the layer has an active runtime entrypoint.
FUTURE_DEFERRED requires proof that entrypoints are absent, disabled, blocked, or safe stubs.
OPTIONAL layers must not be required by a REQUIRED_NOW layer unless the dependency is safely bypassed or recorded.
A deferred mutating layer must not be reachable through Tool / MCP Adapter, Orchestrator, CLI, Git, or MCP paths.
A deferred network/external layer must not be reachable unless network/external behavior is explicitly in scope and policy-approved.
```

Blocking if:

```text
runtime-reachable layer is marked NOT_APPLICABLE
mutating deferred layer is callable
network/external deferred layer is callable by default
optional layer is actually required by a REQUIRED_NOW dependency path
```

---

# 52. Waiver, Exception, and Override Rules

Final acceptance may record deviations, but it must not use waivers to override safety.

Allowed waiver use:

```text
non-runtime documentation mismatch
optional ecosystem placement gap
formatting issue in non-authoritative report text
future-layer safe stub with evidence
release readiness not claimed for internal acceptance scope
```

Forbidden waiver use:

```text
compileall failure
pytest failure
schema validation failure
missing reviewed commit
missing acceptance scope
missing command exit code
missing required evidence
missing required hashes
unsafe deferral
runtime artifact boundary failure
source mutation failure
unresolved BLOCKER
policy bypass
sandbox bypass
patch/governance bypass
release-ready claim without release evidence
verdict mismatch
hash mismatch or tamper condition
```

Authority rule:

```text
No human, runner, review report, or completion record may override a BLOCKER for ACCEPTED.
A waiver may explain why the system is NOT_ACCEPTED or why release readiness is NOT_CLAIMED.
A waiver may not convert a BLOCKER into PASS.
```

Blocking if:

```text
waiver changes BLOCKER to non-blocking
manual override changes command result
manual override changes final verdict without rerun
manual exception hides missing required evidence
```

---

# 53. Report-Only Mode vs Enforcing Mode

The final acceptance runner may support report-only mode, but report-only output must not be confused with final acceptance.

Modes:

```text
final-review / enforcing mode: may produce ACCEPTED only when all gates pass
report-only mode: may summarize failures without making ACCEPTED claim
diagnostic mode: may run partial checks but cannot produce ACCEPTED
```

Required behavior:

```text
mode must be recorded in runner output, review report, evidence manifest, and completion record
ACCEPTED is valid only in final-review / enforcing mode
report-only mode may exit 0 while reporting NOT_ACCEPTED only if explicitly configured and recorded
report-only mode must not write a VALIDATED completion record
partial diagnostic runs must not overwrite final accepted evidence
```

Blocking if:

```text
report-only run produces ACCEPTED
report-only run writes VALIDATED completion record
mode is missing from final evidence artifacts
partial diagnostic evidence overwrites final accepted evidence
```

---

# 54. Cross-Layer Schema-Version Compatibility and Migration Check

Final acceptance must verify that layer evidence schemas are compatible with the final acceptance reader.

Required checks:

```text
schema_id present for every layer evidence artifact
schema_version present for every layer evidence artifact
schema version is supported by final acceptance reader
unknown schema versions fail closed unless a migration adapter exists
migration adapter has tests
migrated evidence preserves command statuses, exit codes, hashes, blockers, deviations, and verdicts
```

Status:

```text
PASS | PARTIAL | FAIL | NOT_CHECKED
```

Blocking if:

```text
required layer evidence uses unknown schema version
migration changes safety-critical fields
schema compatibility is not checked
layer artifact is parsed loosely and accepted despite missing required fields
```

---

# 55. Evidence Retention and Archive Requirements

A final accepted system must produce an evidence package that can be archived and rechecked.

Required archive package:

```text
final acceptance scope
final acceptance review report
final acceptance completion record
final acceptance evidence manifest
all command output artifacts
layer matrix
dependency matrix
evidence freshness report
runtime artifact report
release readiness report
hash index
list of referenced lower-layer artifacts
```

Archive rules:

```text
archive manifest must identify reviewed commit and scope
archive manifest must include SHA-256 hashes for archived files
archive must not include secrets
archive must not include raw confidential command output unless redacted
archive must not be required for ACCEPTED if local evidence package exists, but release-ready status requires archive readiness
```

Blocking for RELEASE_READY if:

```text
archive manifest is missing
archive contains unredacted secrets
archive hashes are missing
archive does not identify reviewed commit and scope
```

---

# 56. Revalidation Procedure After Invalidation

If acceptance is invalidated, use this required sequence.

Required sequence:

```text
1. Record invalidation reason.
2. Freeze or update acceptance scope with a new scope version.
3. Re-run compileall.
4. Re-run pytest.
5. Re-run schema validation.
6. Re-run final acceptance runner in final-review mode.
7. Regenerate layer matrix, dependency matrix, freshness report, runtime artifact report, release readiness report, evidence manifest, review report, and completion record.
8. Recompute hashes.
9. Recheck source mutation and runtime artifact boundaries.
10. Record new final verdict.
```

Rules:

```text
old ACCEPTED evidence remains historical only
new acceptance requires new reviewed timestamp and hash set
new commit requires new validation
new scope requires new validation
changed evidence artifact requires new validation or explicit stale-but-unaffected proof where applicable
```

Blocking if:

```text
invalidated ACCEPTED verdict is reused
new commit is accepted using old final acceptance evidence without freshness proof
changed scope is accepted without rerun
```

---

# 57. Final Completeness Addendum

The ACCEPTED criteria also require:

```text
canonical JSON / deterministic hashing rules pass
runtime reachability checks pass for deferred, optional, and not-applicable layers
waiver / override rules pass
report-only mode is not confused with final-review mode
schema-version compatibility checks pass
final evidence is archive-ready if release-ready is claimed
revalidation procedure is followed after any invalidation
```

The NOT_ACCEPTED criteria also include:

```text
unstable or non-reproducible hashes
runtime-reachable layer marked NOT_APPLICABLE
unsafe callable deferred layer
waiver used to override BLOCKER
report-only evidence used as ACCEPTED proof
unknown schema version accepted without tested migration
invalidated verdict reused without revalidation
```

Add these items to the final frozen checklist:

```text
[ ] canonical JSON and deterministic hashing pass
[ ] runtime reachability checks pass
[ ] deferred and NOT_APPLICABLE layers are not runtime-reachable unsafely
[ ] no waiver overrides a BLOCKER
[ ] runner mode is final-review / enforcing for ACCEPTED
[ ] report-only artifacts do not overwrite final evidence
[ ] schema-version compatibility passes
[ ] migration adapters, if any, are tested
[ ] archive readiness passes if release-ready is claimed
[ ] invalidated acceptance was not reused
```

---

# 58. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the requested post-implementation review areas and the strong v3 final-system controls, then closes the remaining last-mile gaps: canonical JSON hashing, deterministic evidence, runtime reachability for deferred/not-applicable layers, waiver/override limits, report-only versus enforcing-mode separation, schema-version compatibility, evidence archive readiness, and required revalidation after invalidation.
```
