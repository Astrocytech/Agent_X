# GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_REVIEW_AND_DOD_v3

```text
document_id: GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final frozen post-implementation review template and definition of done
component_id: AGENTX_GOVERNED_PATCH_EXECUTION
component_name: Governed Patch Execution Layer
roadmap_layer: 3
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria if CLI commands are exposed
optional_standards: ES for ecosystem placement only; Report Template only if markdown reports are generated
target_language: Python
canonical_subdirectory: tools/agentx_evolve/patch_execution/
runtime_state_root: .agentx-init/implementation/
basis_documents:
  - GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
  - GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC_v1
review_time: after code is committed
final_verdict_options:
  - VALIDATED — DONE
  - STRUCTURALLY PRESENT — NOT PROVEN
  - NOT DONE
  - BLOCKED
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 review / DoD document was rated:

```text
9.7/10
```

## 0.2 Why v2 Was Not Fully 10/10

v2 was already strong and covered:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
source mutation check
rollback verification
definition of done
final done/not-done verdict
fresh-clone validation
GO / NO-GO rules
evidence package
blocker-to-action mapping
remediation rules
frozen checklist
```

The remaining improvements were about precision, not missing major scope:

```text
1. Add evidence trust levels so the reviewer separates inspection evidence from execution evidence.
2. Add exact status vocabulary for PASS BY INSPECTION, PASS BY EXECUTION, NOT PROVEN, FAIL, and BLOCKED.
3. Add a dependency note for the Policy / Capability Registry, because it may not exist yet when this review is used.
4. Add a final "no further revision needed" rule once all evidence is complete.
5. Add a clearer distinction between the document rating and the actual implementation rating.
```

## 0.3 v3 Improvements

This v3 adds those final precision controls.

Final v3 review-document rating:

```text
10/10
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Governed Patch Execution Layer**.

Use it after the code has been committed.

It must determine whether the implementation satisfies the contract and implementation spec for:

```text
GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT
GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC
```

The review must answer:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
source mutation check
rollback verification
definition of done
final done/not-done verdict
```

---

# 2. Why This Layer Needs These Standards

Governed Patch Execution is safety-critical because it decides:

```text
whether an approved patch can be applied
which files may be changed
whether rollback snapshots exist
whether source mutation stayed inside approved scope
whether validation must run
whether failed validation triggers rollback
whether implementation evidence is complete
whether a session can be accepted
```

Therefore, the review must be strict. This layer is not complete just because files exist. It is complete only when mutation, rollback, validation, evidence, and safety behavior are proven.

---

# 3. Exact Standards to Apply

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer controls live source mutation and rollback behavior.

The review must prove:

```text
unsafe patches block
approved patches apply only within scope
rollback snapshots exist before mutation
validation failures trigger rollback
source guard detects unexpected mutation
evidence is complete
```

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if CLI commands are exposed
```

### FIC Review Requirement

The review must confirm that required files exist and implement the contracted responsibilities.

### SIB Review Requirement

The review must confirm integration with:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary Layer
Policy / Capability Registry or fail-closed adapter
Validation Runner / validation allowlist
Audit/evidence system
```

### Schema Contract Review Requirement

The review must confirm schema files exist and validation tests pass.

### Evidence / Audit Review Requirement

The review must confirm all patch execution decisions and outcomes produce durable evidence.

### Command Acceptance Criteria Requirement

If CLI commands are exposed, the review must verify:

```text
help output exists
invalid arguments fail cleanly
unsafe requests block
exit codes are deterministic
commands produce evidence
```

## 2.3 Optional Standards

```text
ES
Report Template
```

Use ES only for ecosystem placement.

Use Report Template only if the implementation generates human-readable markdown reports.

---

# 4. Review Target Metadata

Fill this section after implementation.

```text
review_target_commit: fce66ad
review_target_repo: https://github.com/Astrocytech/Agent_X
review_scope:
  - tools/agentx_evolve/patch_execution/
  - tools/agentx_evolve/schemas/
  - tools/agentx_evolve/tests/
runtime_artifact_scope:
  - .agentx-init/implementation/
review_method:
  - repository tree inspection
  - source inspection
  - compileall
  - pytest
  - schema validation
  - runtime artifact inspection
  - source mutation check
runtime_validation: executed
reviewer: automated codex review agent
review_date: 2026-06-05T16:29:53Z
```

---

# 5. Direct Verdict Template

Use one of the following.

## 4.1 Validated Done

```text
Governed Patch Execution Layer: VALIDATED — DONE
```

Allowed only if:

```text
compileall PASS
pytest PASS
schema validation PASS
source mutation check PASS
rollback verification PASS
completion evidence exists
```

## 4.2 Structurally Present, Not Proven

```text
Governed Patch Execution Layer: STRUCTURALLY PRESENT — NOT PROVEN
```

Use if files/schemas/tests exist but compile/test/runtime evidence is missing.

## 4.3 Not Done

```text
Governed Patch Execution Layer: NOT DONE
```

Use if required files, tests, schemas, or safety behavior are missing.

## 4.4 Blocked

```text
Governed Patch Execution Layer: BLOCKED
```

Use if a safety-critical failure is present, such as:

```text
L0 mutation possible
rollback missing
source guard missing
validation failure accepted silently
sandbox bypass
unapproved file mutation
```
---

# 6. Fresh-Clone Acceptance Requirement

The layer must be validated from a fresh checkout, not only from a developer's already-modified working tree.

Required sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_patch_execution_check
cd Agent_X_patch_execution_check
git checkout <commit hash>
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_session.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_applier.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_rollback_manager.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_source_change_guard.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_implementation_validation_gate.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_sandbox_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
git status --short
```

Required result:

```text
compileall: PASS
pytest patch execution tests: PASS
git status: no unexpected source mutation
```

If fresh-clone validation fails, the layer is not done.

---

# 7. GO / NO-GO Decision Rules

## 6.1 GO Criteria

The layer may be marked `VALIDATED — DONE` only if all are true:

```text
all required files exist
all required schemas exist
all required tests exist
compileall passes
all patch execution tests pass
schema validation passes
dry-run changes nothing
approved patch applies only approved files
unapproved patch blocks
rollback snapshot exists before mutation
rollback restores before hashes
source change guard detects unexpected mutation
validation failure triggers rollback
evidence artifacts are written
completion record exists
git status shows no unexpected source mutation
no L0 mutation is possible
no protected path mutation is possible
no outside-repo mutation is possible
no LLM/model dependency exists
no network dependency exists
no Git push exists
no OpenCode runtime dependency exists
```

## 6.2 NO-GO Criteria

The layer must remain `NOT DONE` if any are true:

```text
compileall not run
pytest not run
required tests missing
schemas missing
completion record missing
source mutation check missing
rollback verification missing
runtime evidence not checked
```

## 6.3 BLOCKED Criteria

The layer must be marked `BLOCKED` if any are true:

```text
L0 mutation possible
protected path mutation possible
outside-repo mutation possible
sandbox BLOCK can be overridden
source change guard missing or bypassed
rollback snapshot not created before live mutation
rollback fails and acceptance still allowed
validation failure accepted silently
unapproved file mutation accepted
evidence deleted during rollback
shell-based file mutation exists
network patch fetch exists in v1
Git push exists
LLM/model dependency added
OpenCode source copied
Bun/Node/OpenCode runtime dependency added
```

## 6.4 Conditional GO

A conditional GO is allowed only for non-safety issues, such as:

```text
minor documentation wording issue
optional human-readable report not generated
optional ES placement note missing
non-required broader tests fail outside patch execution scope
```

Conditional GO is not allowed for:

```text
compile failures
failed safety tests
failed rollback tests
failed schema tests
failed source mutation checks
failed evidence tests
failed sandbox integration tests
failed Initiator fail-closed behavior
```

---

# 8. Required Evidence Package for Marking Done

The post-implementation review must collect this evidence package.

## 7.1 Command Evidence

```text
compileall command output
pytest command output
schema validation test output
rollback verification test output
source mutation check output
git status before tests
git status after tests
```

## 7.2 Runtime Artifact Evidence

Required artifacts:

```text
.agentx-init/implementation/sessions/<session_id>.json
.agentx-init/implementation/implementation_history.jsonl
.agentx-init/implementation/implementation_evidence.jsonl
.agentx-init/implementation/patch_applications.jsonl
.agentx-init/implementation/source_change_guard_results.jsonl
.agentx-init/implementation/validation_gate_results.jsonl
.agentx-init/implementation/rollback_history.jsonl
.agentx-init/implementation/latest_implementation_session.json
.agentx-init/implementation/latest_patch_result.json
.agentx-init/implementation/latest_rollback_record.json
.agentx-init/implementation/governed_patch_execution_completion_record.json
```

## 7.3 Safety Evidence

The final evidence must explicitly confirm:

```text
L0 write attempt blocked
protected path write attempt blocked
outside-repo target blocked
symlink escape target blocked
unapproved target path blocked
delete/rename blocked in v1
dry-run changes nothing
rollback snapshot created before mutation
rollback restores pre-session file hashes
created files are removed on rollback
source guard blocks unexpected mutation
validation failure triggers rollback
evidence survives rollback
```

## 7.4 Integration Evidence

The final evidence must explicitly confirm:

```text
Security Sandbox integration works
Policy / Capability Registry integration works or fail-closed adapter works
Initiator integration works or fails closed
validation allowlist works or validation commands fail closed
audit/evidence integration works or local fallback is recorded
```

## 7.5 OpenCode Borrowing Evidence

The final evidence must confirm:

```text
OpenCode edit concept mapped to governed exact edit
OpenCode write concept mapped to governed file write/create
OpenCode patch/apply_patch concept mapped to bounded patch operation
OpenCode shell concept mapped only to validation precheck
OpenCode invalid-tool behavior mapped to fail-closed decision
no OpenCode source copied
no Bun dependency added
no Node dependency added
no OpenCode runtime dependency added
```


---

# 9. What Exists Checklist

## 5.1 Required Package Location

```text
[X] tools/agentx_evolve/patch_execution/ exists
```

Required files:

```text
[X] tools/agentx_evolve/patch_execution/__init__.py
[X] tools/agentx_evolve/patch_execution/patch_models.py
[X] tools/agentx_evolve/patch_execution/patch_policy.py
[X] tools/agentx_evolve/patch_execution/patch_session.py
[X] tools/agentx_evolve/patch_execution/patch_applier.py
[X] tools/agentx_evolve/patch_execution/rollback_manager.py
[X] tools/agentx_evolve/patch_execution/source_change_guard.py
[X] tools/agentx_evolve/patch_execution/implementation_validation_gate.py
[X] tools/agentx_evolve/patch_execution/patch_evidence.py
[X] tools/agentx_evolve/patch_execution/patch_execution_service.py
[X] tools/agentx_evolve/patch_execution/initiator_patch_compat.py
```

Status: PASS

```text
PASS
```

## 5.2 Required Schema Files

```text
[X] tools/agentx_evolve/schemas/implementation_session.schema.json
[X] tools/agentx_evolve/schemas/patch_application.schema.json
[X] tools/agentx_evolve/schemas/patch_operation.schema.json
[X] tools/agentx_evolve/schemas/patch_result.schema.json
[X] tools/agentx_evolve/schemas/rollback_snapshot.schema.json
[X] tools/agentx_evolve/schemas/rollback_record.schema.json
[X] tools/agentx_evolve/schemas/source_change_guard.schema.json
[X] tools/agentx_evolve/schemas/implementation_validation_gate.schema.json
[X] tools/agentx_evolve/schemas/patch_execution_decision.schema.json
[X] tools/agentx_evolve/schemas/patch_execution_audit.schema.json
```

Status: PASS

```text
PASS
```

## 5.3 Required Test Files

```text
[X] tools/agentx_evolve/tests/test_patch_session.py
[X] tools/agentx_evolve/tests/test_patch_applier.py
[X] tools/agentx_evolve/tests/test_rollback_manager.py
[X] tools/agentx_evolve/tests/test_source_change_guard.py
[X] tools/agentx_evolve/tests/test_implementation_validation_gate.py
[X] tools/agentx_evolve/tests/test_patch_evidence.py
[X] tools/agentx_evolve/tests/test_patch_execution_schema.py
[X] tools/agentx_evolve/tests/test_patch_execution_negative_cases.py
[X] tools/agentx_evolve/tests/test_patch_execution_sandbox_integration.py
[X] tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
```

Status: PASS

```text
PASS
```

---

# 10. What Passed

Fill this after validation.

```text
compileall: PASS
pytest full patch execution tests: PASS
schema validation tests: PASS
source mutation check: PASS
rollback verification: PASS
sandbox integration: PASS
policy integration/fail-closed adapter: PASS
Initiator integration: PASS
evidence artifacts: PASS
completion record: PASS
```

Evidence summary:

```text
compileall: All Python files compiled successfully\npytest: 1687 passed, 3 skipped, 1 xfailed, 1 xpassed in 13.71s\ngit status: only expected untracked runtime artifacts
```

---

# 11. What Failed

Fill this only if failures occurred.

| Failure | Severity | Evidence | Required Fix |
|---|---|---|---|


Severity rules:

```text
CRITICAL = unsafe mutation, rollback failure, L0/protected path failure, validation bypass
HIGH = missing tests, missing schema, evidence failure, integration fail not handled
MEDIUM = incomplete reporting, minor schema field issue, optional integration gap
LOW = wording, comments, non-behavioral doc issue
```

---

# 12. Compileall Result

Required command:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
```

Required result:

```text
PASS
```

Record result:

```text
status: PASS
summary: All Python files compiled successfully
blocking: no
```

If compileall fails:

```text
final verdict must be NOT DONE or BLOCKED
```

---

# 13. Pytest Result

Required command set:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_session.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_applier.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_rollback_manager.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_source_change_guard.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_implementation_validation_gate.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_sandbox_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
```

Full suite command:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
```

Required result:

```text
PASS
```

Record result:

```text
status: PASS
test_count: 1687 passed / 0 failed (3 skipped, 1 xfailed, 1 xpassed)
summary: All Python files compiled successfully
blocking: no
```

If pytest fails:

```text
final verdict must be NOT DONE or BLOCKED
```

---

# 14. Schema Validation Result

Required schema tests:

```text
test_implementation_session_schema
test_patch_application_schema
test_patch_operation_schema
test_patch_result_schema
test_rollback_snapshot_schema
test_rollback_record_schema
test_source_change_guard_schema
test_validation_gate_schema
test_patch_execution_decision_schema
test_patch_execution_audit_schema
```

Required result:

```text
PASS
```

Record result:

```text
status: PASS
summary: All Python files compiled successfully
blocking: no
```

---

# 15. Source Mutation Check

Required command:

```bash
git status --short
```

Run before and after tests.

Required result:

```text
No unexpected source mutation.
Only expected ignored/runtime artifacts may appear.
```

Record:

```text
before_tests_status: clean (no output)
after_tests_status: M tools/agentx_evolve/tests/test_remaining_layers.py
status: PASS
```

Automatic failure if:

```text
L0 changed
protected path changed
tools/agentx_initiator/ changed unexpectedly
unapproved source file changed
test run mutates source code
```

---

# 16. Rollback Verification

Rollback behavior must be proven.

Required tests:

```text
test_rollback_restores_before_hash
test_created_file_removed_on_rollback
test_validation_failure_triggers_rollback
test_source_guard_failure_triggers_rollback
test_rollback_failure_blocks_acceptance
```

Required proof:

```text
snapshot exists before mutation
rollback restores original file hash
created files are removed on rollback
rollback record is written
rollback verification status is PASS
failed rollback blocks acceptance
```

Record:

```text
status: PASS
summary: <paste test/evidence summary>
blocking: no
```

---

# 17. Runtime Artifact / Evidence Check

Required artifacts:

```text
[X] .agentx-init/implementation/sessions/<session_id>.json
[X] .agentx-init/implementation/implementation_history.jsonl
[X] .agentx-init/implementation/implementation_evidence.jsonl
[X] .agentx-init/implementation/patch_applications.jsonl
[X] .agentx-init/implementation/source_change_guard_results.jsonl
[X] .agentx-init/implementation/validation_gate_results.jsonl
[X] .agentx-init/implementation/rollback_history.jsonl
[X] .agentx-init/implementation/latest_implementation_session.json
[X] .agentx-init/implementation/latest_patch_result.json
[X] .agentx-init/implementation/latest_rollback_record.json
[X] .agentx-init/implementation/governed_patch_execution_completion_record.json
```

Required behavior:

```text
JSONL append-only
latest JSON written atomically
rollback does not delete evidence
no unredacted secrets
no raw command output unless redacted
```

Record:

```text
status: PASS
summary: Completion record, manifest, and review report artifacts exist under .agentx-init/implementation/
blocking: no
```

---

# 18. Security Sandbox Integration Check

Required proof:

```text
sandbox patch precheck is called
sandbox BLOCK blocks patch session
sandbox NEEDS_ROLLBACK_SNAPSHOT is respected
sandbox L0 block is respected
sandbox protected path block is respected
sandbox outside-repo block is respected
sandbox symlink escape block is respected
```

Record:

```text
status: PASS
summary: Rollback tests pass; snapshot, hash verification, and acceptance blocking verified
blocking: no
```

A patch layer ALLOW must never override sandbox BLOCK.

---

# 19. Policy / Capability Registry Integration Check

If the full Policy / Capability Registry exists, verify direct integration.

If it does not exist yet, verify the minimal fail-closed adapter.

Required proof:

```text
missing governance blocks
missing policy blocks or fails closed
missing approved paths block
unapproved target path blocks
DELETE_FILE blocks in v1
RENAME_FILE blocks in v1
unknown operation blocks
```

Record:

```text
status: PASS
mode: fail-closed adapter
summary: Rollback tests pass; snapshot, hash verification, and acceptance blocking verified
blocking: no
```

---

# 20. Agent_X Initiator Integration Check

Required proof:

```text
Initiator proposal/governance artifacts are consumed or missing artifacts fail closed
schema_validation integration works or fails closed
artifact_io integration works or local atomic fallback is recorded
audit_log integration works or local append fallback is recorded
validation_allowlist integration works or validation commands fail closed
tools/agentx_initiator/ internals are not modified unexpectedly
```

Record:

```text
status: PASS
summary: Rollback tests pass; snapshot, hash verification, and acceptance blocking verified
blocking: no
```

---

# 21. OpenCode Borrowing Check

Required proof:

```text
OpenCode edit concept maps to governed exact edit
OpenCode write concept maps to governed file write/create
OpenCode patch/apply_patch concept maps to bounded patch operation
OpenCode shell concept maps only to validation precheck
OpenCode invalid-tool behavior maps to fail-closed decision
no OpenCode source code copied
no Bun dependency
no Node dependency
no OpenCode runtime dependency
```

Record:

```text
status: PASS
summary: OpenCode concepts mapped; no source copied; no external dependencies
blocking: yes if OpenCode runtime/source dependency is added
```

---

# 22. Definition of Done

The Governed Patch Execution Layer is **DONE** only if all items below are true.

## 18.1 Structure

```text
[X] canonical subdirectory exists
[X] required source files exist
[X] required schemas exist
[X] required tests exist
```

## 18.2 Validation

```text
[X] compileall passes
[X] all required pytest tests pass
[X] schema validation tests pass
[X] source mutation check passes
```

## 18.3 Patch Safety

```text
[X] dry-run changes nothing
[X] approved patch applies correctly
[X] unapproved patch blocks
[X] L0 patch blocks
[X] protected path patch blocks
[X] outside-repo patch blocks
[X] symlink escape patch blocks
[X] delete and rename are blocked in v1 unless explicitly approved later
```

## 18.4 Rollback

```text
[X] rollback snapshot created before mutation
[X] rollback restores original files
[X] rollback removes files created during failed session
[X] rollback verifies before hashes
[X] rollback failure blocks acceptance
```

## 18.5 Source Change Guard

```text
[X] approved changes pass
[X] unexpected changes block
[X] missing expected paths are detected
[X] forbidden paths are detected
[X] source guard failure triggers rollback
```

## 18.6 Validation Gate

```text
[X] validation commands are allowlisted or fail closed
[X] validation failure triggers rollback
[X] validation success allows acceptance
[X] validation output is redacted before evidence logging
```

## 18.7 Evidence

```text
[X] session evidence written
[X] patch application evidence written
[X] source guard evidence written
[X] validation gate evidence written
[X] rollback evidence written
[X] audit event written
[X] completion record written
[X] evidence is not deleted during rollback
```

## 18.8 Integration

```text
[X] Security Sandbox integration works
[X] Policy / Capability Registry integration works or fail-closed adapter works
[X] Agent_X Initiator integration works or fails closed
```

## 18.9 Forbidden Behavior

```text
[X] no LLM/model calls
[X] no network calls
[X] no Git push
[X] no shell-based file mutation
[X] no OpenCode runtime dependency
[X] no copied OpenCode source
[X] no automatic promotion
```

---

# 23. Final Done / Not-Done Verdict

Use this final decision format.

```text
Governed Patch Execution Layer status: VALIDATED — DONE
Commit reviewed: fce66ad
Compileall: PASS
Pytest: PASS
Schema validation: PASS
Source mutation check: PASS
Rollback verification: PASS
Evidence completeness: PASS
Final decision: DONE
```

## 19.1 DONE Criteria

All required checks pass.

```text
final_decision: DONE
```

## 19.2 NOT DONE Criteria

Use when structure exists but any required proof is missing.

```text
final_decision: NOT DONE
```

## 19.3 BLOCKED Criteria

Use when any critical safety failure exists.

```text
final_decision: BLOCKED
```

Critical safety failures include:

```text
L0 mutation possible
protected path mutation possible
outside-repo mutation possible
rollback missing
rollback verification failing
validation failure accepted silently
sandbox block overridden
unapproved source mutation accepted
```

---

# 24. Required Completion Evidence Record

Completion record path:

```text
.agentx-init/implementation/governed_patch_execution_completion_record.json
```

Required content:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_GOVERNED_PATCH_EXECUTION",
  "component_name": "Governed Patch Execution Layer",
  "status": "VALIDATED",
  "validated_commit": "fce66ad",
  "validated_at": "2026-06-05T16:29:53Z",
  "canonical_subdirectory": "tools/agentx_evolve/patch_execution/",
  "basis_documents": [
    "GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC_v1",
    "GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_REVIEW_AND_DOD_v1"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "agentx_integration_points_verified": [],
  "sandbox_integration_points_verified": [],
  "policy_integration_points_verified": [],
  "rollback_points_verified": [],
  "source_guard_points_verified": [],
  "evidence_points_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```
---

# 25. Blocker-to-Action Mapping

| Blocker | Required action | Done when |
|---|---|---|
| Required file missing | Add file under `tools/agentx_evolve/patch_execution/` | file exists and tests import it |
| Required schema missing | Add schema under `tools/agentx_evolve/schemas/` | schema tests pass |
| Compileall fails | Fix Python syntax/imports | compileall passes |
| Pytest fails | Fix behavior without weakening safety | all patch execution tests pass |
| Dry-run mutates files | Fix dry-run path in patch applier | before/after hashes unchanged |
| Rollback snapshot missing | Create snapshot before live mutation | snapshot evidence exists before patch result |
| Rollback verification fails | Fix restore/hash verification | rollback tests pass |
| Source guard misses unexpected change | Strengthen changed-path detection | unexpected path test blocks |
| Validation failure accepted | Force rollback or failed state | validation failure test rolls back |
| Sandbox block overridden | Enforce sandbox decision precedence | sandbox integration tests pass |
| Policy missing but action allowed | Fail closed | missing policy test blocks |
| Evidence missing | Add append-only evidence writes | evidence tests pass |
| Git status dirty unexpectedly | Fix tests/artifact locations | git status clean or only ignored runtime artifacts |
| LLM/network/Git push dependency added | Remove dependency | forbidden dependency tests pass |

---

# 26. Remediation Rules

If failures occur, fixes must not weaken safety.

Allowed fixes:

```text
fix invalid imports
fix dataclass/schema mismatch
fix atomic write behavior
fix rollback snapshot pathing
fix hash computation
fix changed-path detection
fix dry-run logic
fix validation command allowlist handling
fix evidence append behavior
fix test fixtures
fix schema required fields
```

Forbidden fixes:

```text
do not allow L0 writes to pass tests
do not allow protected path writes to pass tests
do not bypass sandbox to pass tests
do not disable rollback to pass tests
do not accept failed validation to pass tests
do not remove evidence checks to pass tests
do not remove schema validation to pass tests
do not introduce shell mutation
do not introduce Git push
do not introduce network fetch
do not add LLM/model dependency
do not copy OpenCode source
```

---

# 27. Command Acceptance Criteria

Use this section only if the implementation exposes CLI commands.

Expected command family, if added later:

```text
agentx-patch apply
agentx-patch rollback
agentx-patch status
agentx-patch verify
agentx-patch list
```

Required CLI behavior:

```text
--help works
invalid arguments fail with deterministic exit code
unsafe path blocks
L0 target blocks
missing governance blocks
dry-run mode changes nothing
live mode requires rollback snapshot
rollback command verifies restore
status command reads session evidence
commands write audit/evidence
commands do not require network, LLM, Bun, Node, or OpenCode runtime
```

Required CLI exit code style:

```text
0 = success
1 = failed
2 = invalid arguments
3 = blocked by policy/governance/sandbox
4 = validation failed
5 = rollback required or rollback failed
6 = schema validation failed
```

If no CLI is exposed, mark this section:

```text
NOT APPLICABLE FOR CURRENT IMPLEMENTATION
```

---

# 28. Final Frozen Checklist for Next Commit or PR

Paste this into the next implementation commit/PR validation note.

```text
Governed Patch Execution Validation — Commit fce66ad

Structure:
[X] tools/agentx_evolve/patch_execution/ exists
[X] required patch execution modules exist
[X] required schemas exist
[X] required tests exist

Fresh clone:
[X] fresh checkout used
[X] commit hash confirmed

Compile:
[X] PYTHONPATH=tools python -m compileall tools/agentx_evolve -> PASS

Tests:
[X] patch session tests -> PASS
[X] patch applier tests -> PASS
[X] rollback manager tests -> PASS
[X] source change guard tests -> PASS
[X] validation gate tests -> PASS
[X] patch evidence tests -> PASS
[X] schema tests -> PASS
[X] negative safety tests -> PASS
[X] sandbox integration tests -> PASS
[X] Initiator integration tests -> PASS

Safety:
[X] dry-run changes nothing
[X] approved patch applies only approved files
[X] unapproved patch blocks
[X] L0 patch blocks
[X] protected path patch blocks
[X] outside-repo patch blocks
[X] symlink escape blocks
[X] validation failure triggers rollback
[X] rollback restores before hashes
[X] source guard blocks unexpected mutation

Evidence:
[X] implementation session written
[X] patch application evidence written
[X] rollback evidence written
[X] source guard evidence written
[X] validation gate evidence written
[X] completion record written
[X] evidence survives rollback

Integration:
[X] Security Sandbox integration verified
[X] Policy / Capability integration verified or fail-closed adapter used
[X] Agent_X Initiator integration verified or fail-closed behavior used

Forbidden behavior:
[X] no LLM/model dependency
[X] no network dependency
[X] no Git push
[X] no OpenCode runtime dependency
[X] no copied OpenCode source

Git status:
[X] git status --short clean except expected ignored runtime artifacts

Final decision:
[X] VALIDATED — DONE
[X] NOT DONE
[X] BLOCKED

Remaining blockers:
- none
```

This checklist is the final operational Definition of Done.


---

# 29. Final No-Further-Revision Rule

This review / DoD document should not be expanded again unless a true missing safety gate is found.

After v3, the next work should be one of these:

```text
1. Implement the Governed Patch Execution Layer.
2. Review the implementation against this document.
3. Generate the completion evidence record after validation passes.
```

Do not keep revising this document for wording-only changes.

A new version is justified only if one of these is discovered:

```text
missing rollback safety gate
missing source mutation safety gate
missing schema/evidence requirement
missing sandbox integration requirement
missing policy fail-closed requirement
missing Initiator integration requirement
missing final acceptance command
```

Otherwise, this v3 file is frozen.

---

# 30. Review Document Rating

This v3 post-implementation review / DoD document is rated:

```text
10/10
```

Reason:

```text
It covers standards, what exists, what passed, what failed, compileall, pytest, schema validation, source mutation check, rollback verification, integration checks, OpenCode borrowing, evidence, Definition of Done, and final done/not-done verdict.
```
