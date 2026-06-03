# GIT_INTEGRATION_LAYER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: GIT_INTEGRATION_LAYER_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_GIT_INTEGRATION_LAYER
component_name: Git Integration Layer
roadmap_layer: 6
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
review_use: use after code is committed
basis_documents:
  - GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Command Acceptance Criteria
conditional_standards:
  - Promotion / Release Gate Acceptance Criteria, only if push is gated
  - Human Approval Acceptance Criteria, only if approval is required
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if it writes markdown reports
canonical_subdirectory: tools/agentx_evolve/git/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/git/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v3 Review and Upgrade Summary

The v2 review / DoD document was strong and close to final, but I would rate it:

```text
9.7/10
```

It already had complete coverage for structure, command allowlisting, read-only operations, blocked operations, mutation gating, environment hardening, ref validation, evidence/audit, locking, idempotency, dependency fail-closed behavior, and final sign-off.

It was not fully 10/10 because several final production-control details were still under-specified:

```text
1. The metadata listed roadmap_layer: 14 but the correct layer for Git Integration is 6 (Phase A).
2. The file inventory did not distinguish existing files from required FUTURE files.
3. The schema validation checklist did not list all 17 required schemas explicitly.
4. Dependency degradation was implied but not checked as a separate DONE requirement.
5. Negative test coverage for Git config isolation, credential prompts, GPG signing, and hook-path isolation was underspecified.
6. Future implementation checklist was not explicit enough about locked/mutation features.
7. The completion evidence fields needed to track Git-specific validated capabilities.
8. The final frozen checklist needed environment hardening, ref validation, and evidence artifact checks as first-class gates.
```

This v3 applies those corrections and is the final 10/10 review / DoD template.

Freeze rule:

```text
This v3 document is frozen for the Git Integration Layer post-implementation review.
Future changes should be limited to PATCH-level wording, examples, or typo fixes unless the layer's mutation policy, push policy, role permissions, default safety behavior, or required schemas change.
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Git Integration Layer**.

Use this document after code is committed to determine whether the Git Integration Layer is complete, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether read-only Git operations work
whether mutation operations are blocked by default
whether blocked Git commands fail closed
whether Git command allowlist is enforced
whether environment hardening is in place
whether ref validation is in place
whether mutation gating is in place
whether evidence writing is in place
whether locking is in place
whether dependency degradation is handled safely
whether evidence manifest and hashes exist
whether review report and completion record exist
whether source mutation checks pass
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this review document does not mean the implementation is complete. The implementation is complete only when the validation commands, evidence checks, negative tests, and final sign-off criteria in this document pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because Git operations can permanently change repository state, rewrite history, publish code remotely, or destroy local work.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria
```

## 2.3 Conditional Standards

```text
Human Review / Approval Acceptance Criteria, only if human approval gates are active
Promotion / Release Gate Acceptance Criteria, only if push is gated
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The Git Integration Layer is safety-critical because Git is the boundary between generated or reviewed changes and durable repository history.

It controls:

```text
which Git operations are allowed
which Git operations are blocked
which roles can inspect Git
which roles can stage/commit/push
when human approval is required
when governance is required
how Git commands are allowlisted
how branch creation is controlled
how commits are evidenced
how push is blocked or approved
how rollback/revert is handled
how Git integrates with patch execution and promotion
```

It must not become a Git bypass layer.

The layer must avoid:

```text
direct filesystem mutation by Git commands without evidence
Git add . or implicit staging
unreviewed commits
push without promotion gate
history rewrite commands
remote credential leakage
hook/external-diff/pager execution by default
index mutation during read-only operations
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
  jsonschema_version: <version or NOT INSTALLED>
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
[ ] every expected-failure negative test records the expected failure condition
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] accepted deviations are recorded in the deviation register
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when recorded validation evidence satisfies the GO criteria.

---

# 5. Status Vocabulary

Use only these status values in review tables:

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, expose, approve, or bypass controls. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, mutate files, call network, approve, promote, or bypass policy/sandbox gates.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Mutation operations (stage, commit, branch create, revert, push) may be `DEFERRED SAFELY` only if the review proves:

```text
no mutation code path executes
all mutation entry points return BLOCKED
no mutation can bypass the BLOCKED default
safe deferral is recorded in the deviation register
```

---

# 6. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_integration_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation command: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If `validate_git_integration_schemas.py` is not implemented, equivalent schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_git_schema_validation.py
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
human interactive input
Git write access
```

---

# 7. Expected Implementation Scope

## 7.1 Required Git Package Files

Expected location:

```text
tools/agentx_evolve/git/
```

Expected files:

```text
tools/agentx_evolve/git/__init__.py              [EXISTS]
tools/agentx_evolve/git/git_models.py            [EXISTS]
tools/agentx_evolve/git/git_command_policy.py    [FUTURE — extend from git_policy.py]
tools/agentx_evolve/git/git_command_runner.py    [FUTURE]
tools/agentx_evolve/git/git_environment.py       [FUTURE]
tools/agentx_evolve/git/git_ref_validator.py     [FUTURE]
tools/agentx_evolve/git/git_status.py            [FUTURE]
tools/agentx_evolve/git/git_diff.py              [FUTURE]
tools/agentx_evolve/git/git_mutation_gate.py     [FUTURE]
tools/agentx_evolve/git/git_stage.py             [FUTURE]
tools/agentx_evolve/git/git_commit.py            [FUTURE]
tools/agentx_evolve/git/git_branch.py            [FUTURE]
tools/agentx_evolve/git/git_revert.py            [FUTURE]
tools/agentx_evolve/git/git_push.py              [FUTURE]
tools/agentx_evolve/git/git_locks.py             [FUTURE]
tools/agentx_evolve/git/git_evidence.py          [FUTURE]
tools/agentx_evolve/git/git_dispatcher.py        [FUTURE]
```

Current file inventory:

```text
EXISTS: 4 files (__init__.py, git_models.py, git_operations.py, git_policy.py)
FUTURE: 13 files (git_command_policy.py replaces git_policy.py, plus 12 new modules)
```

Note: `git_policy.py` currently exists. The contract requires `git_command_policy.py`. The implementation may either rename/extend `git_policy.py` to `git_command_policy.py` or create a new module that imports/extends it.

Note: `git_operations.py` currently provides `run_git_operation()` and convenience functions. It uses subprocess without full environment hardening. The `git_command_runner.py` and `git_environment.py` futures should provide the hardened execution path; `git_operations.py` may be kept for backward compatibility or migrated.

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
git_operation.schema.json              [EXISTS]
git_result.schema.json                 [EXISTS]
git_command_policy.schema.json         [FUTURE]
git_command_result.schema.json         [FUTURE]
git_status_diff_result.schema.json     [FUTURE]
git_operation_result.schema.json       [FUTURE]
git_mutation_request.schema.json       [FUTURE]
git_branch_request.schema.json         [FUTURE]
git_ref_validation_result.schema.json  [FUTURE]
git_stage_request.schema.json          [FUTURE]
git_commit_evidence.schema.json        [FUTURE]
git_push_request.schema.json           [FUTURE]
git_revert_request.schema.json         [FUTURE]
git_lock_record.schema.json            [FUTURE]
git_audit_event.schema.json            [FUTURE]
git_evidence_manifest.schema.json      [FUTURE]
git_review_report.schema.json          [FUTURE]
git_completion_record.schema.json      [FUTURE]
```

Current schema inventory:

```text
EXISTS: 2 schemas (git_operation.schema.json, git_result.schema.json)
FUTURE: 15 schemas
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_git_integration.py              [EXISTS — covers models, operations, policy]
test_git_tools.py                    [EXISTS — covers tool-layer git wrappers]
test_git_evidence.py                 [EXISTS — covers promotion git evidence]
test_git_command_policy.py           [FUTURE]
test_git_command_runner.py           [FUTURE]
test_git_environment.py              [FUTURE]
test_git_ref_validator.py            [FUTURE]
test_git_status.py                   [FUTURE]
test_git_diff.py                     [FUTURE]
test_git_mutation_gate.py            [FUTURE]
test_git_stage.py                    [FUTURE]
test_git_commit.py                   [FUTURE]
test_git_branch.py                   [FUTURE]
test_git_revert.py                   [FUTURE]
test_git_push.py                     [FUTURE]
test_git_locks.py                    [FUTURE]
test_git_dispatcher.py               [FUTURE]
test_git_negative_cases.py           [FUTURE]
test_git_schema_validation.py        [FUTURE]
validate_git_integration_schemas.py  [FUTURE]
```

Current test inventory:

```text
EXISTS: 3 test files (test_git_integration.py, test_git_tools.py, test_git_evidence.py)
FUTURE: 17 test files
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/git/
```

Expected artifacts:

```text
git_operation_history.jsonl
git_result_history.jsonl
git_blocked_history.jsonl
git_mutation_request_history.jsonl
git_commit_evidence_history.jsonl
git_latest_operation.json
git_latest_result.json
git_evidence_manifest.json
git_review_report.json
git_integration_completion_record.json
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Git package location | `tools/agentx_evolve/git/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all 17 required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Git models | GitOperation, GitResult, GitDiffResult, plus all FUTURE models | PASS / PARTIAL / FAIL / NOT CHECKED |
| Command allowlist | structured allowlist with at least 10 read-only entries | PASS / PARTIAL / FAIL / NOT CHECKED |
| Command runner | argument-vector execution, no shell, bounded output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Environment hardening | GIT_TERMINAL_PROMPT, GIT_PAGER, HOME isolation, etc. | PASS / PARTIAL / FAIL / NOT CHECKED |
| Ref validation | branch/ref/tag validation with protected namespace detection | PASS / PARTIAL / FAIL / NOT CHECKED |
| Read-only operations | status, diff, log work for approved roles | PASS / PARTIAL / FAIL / NOT CHECKED |
| Mutation gating | policy + sandbox + evidence checks before mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| Stage operation | blocked by default, requires patch evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Commit operation | blocked by default, requires stage evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Branch operation | blocked by default, requires governance | PASS / PARTIAL / FAIL / NOT CHECKED |
| Revert operation | dry-run by default, blocked unless approved | PASS / PARTIAL / FAIL / NOT CHECKED |
| Push operation | blocked by default, requires promotion gate | PASS / PARTIAL / FAIL / NOT CHECKED |
| Mutation locking | serialized mutation with lock records | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence/audit | append-only evidence for all operations | PASS / PARTIAL / FAIL / NOT CHECKED |
| Dispatcher pipeline | full 29-step operation pipeline | PASS / PARTIAL / FAIL / NOT CHECKED |
| Dependency degradation | missing upstream layers fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | forbidden actions fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Git operation model | `git_models.py` | `test_git_integration.py` | operation history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Git result model | `git_models.py` | `test_git_integration.py` | result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Git command policy | `git_command_policy.py` / `git_policy.py` | `test_git_command_policy.py` | policy decision ref | PASS / PARTIAL / FAIL / NOT CHECKED |
| Command execution | `git_command_runner.py` / `git_operations.py` | `test_git_command_runner.py` | command result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Environment hardening | `git_environment.py` | `test_git_environment.py` | environment profile ref | PASS / PARTIAL / FAIL / NOT CHECKED |
| Ref validation | `git_ref_validator.py` | `test_git_ref_validator.py` | ref validation history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Read-only status | `git_status.py` | `test_git_status.py` | operation evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Read-only diff | `git_diff.py` | `test_git_diff.py` | operation evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Mutation gate | `git_mutation_gate.py` | `test_git_mutation_gate.py` | gate decision ref | PASS / PARTIAL / FAIL / NOT CHECKED |
| Stage | `git_stage.py` | `test_git_stage.py` | stage evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Commit | `git_commit.py` | `test_git_commit.py` | commit evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Branch | `git_branch.py` | `test_git_branch.py` | branch evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Revert | `git_revert.py` | `test_git_revert.py` | revert evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Push | `git_push.py` | `test_git_push.py` | push evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Mutation locks | `git_locks.py` | `test_git_locks.py` | lock records | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence/audit | `git_evidence.py` | `test_git_evidence.py` | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Operation pipeline | `git_dispatcher.py` | `test_git_dispatcher.py` | completion record | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety | all public surfaces | `test_git_negative_cases.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | all `.schema.json` files | `test_git_schema_validation.py` | schema validation output | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Git Package Files

```text
[ ] tools/agentx_evolve/git/__init__.py
[ ] tools/agentx_evolve/git/git_models.py
[ ] tools/agentx_evolve/git/git_operations.py
[ ] tools/agentx_evolve/git/git_policy.py
[ ] tools/agentx_evolve/git/git_command_policy.py
[ ] tools/agentx_evolve/git/git_command_runner.py
[ ] tools/agentx_evolve/git/git_environment.py
[ ] tools/agentx_evolve/git/git_ref_validator.py
[ ] tools/agentx_evolve/git/git_status.py
[ ] tools/agentx_evolve/git/git_diff.py
[ ] tools/agentx_evolve/git/git_mutation_gate.py
[ ] tools/agentx_evolve/git/git_stage.py
[ ] tools/agentx_evolve/git/git_commit.py
[ ] tools/agentx_evolve/git/git_branch.py
[ ] tools/agentx_evolve/git/git_revert.py
[ ] tools/agentx_evolve/git/git_push.py
[ ] tools/agentx_evolve/git/git_locks.py
[ ] tools/agentx_evolve/git/git_evidence.py
[ ] tools/agentx_evolve/git/git_dispatcher.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] git_operation.schema.json
[ ] git_result.schema.json
[ ] git_command_policy.schema.json
[ ] git_command_result.schema.json
[ ] git_status_diff_result.schema.json
[ ] git_operation_result.schema.json
[ ] git_mutation_request.schema.json
[ ] git_branch_request.schema.json
[ ] git_ref_validation_result.schema.json
[ ] git_stage_request.schema.json
[ ] git_commit_evidence.schema.json
[ ] git_push_request.schema.json
[ ] git_revert_request.schema.json
[ ] git_lock_record.schema.json
[ ] git_audit_event.schema.json
[ ] git_evidence_manifest.schema.json
[ ] git_review_report.schema.json
[ ] git_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_git_integration.py
[ ] test_git_tools.py
[ ] test_git_evidence.py
[ ] test_git_command_policy.py
[ ] test_git_command_runner.py
[ ] test_git_environment.py
[ ] test_git_ref_validator.py
[ ] test_git_status.py
[ ] test_git_diff.py
[ ] test_git_mutation_gate.py
[ ] test_git_stage.py
[ ] test_git_commit.py
[ ] test_git_branch.py
[ ] test_git_revert.py
[ ] test_git_push.py
[ ] test_git_locks.py
[ ] test_git_dispatcher.py
[ ] test_git_negative_cases.py
[ ] test_git_schema_validation.py
[ ] validate_git_integration_schemas.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 11. Validation Commands

Run from a fresh checkout of the implementation commit.

Record exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is expected and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_integration_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

---

# 12. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Git Integration Layer Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_command: <optional scoped git pytest command>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required Git Integration Layer test fails
any Git model, operation, policy, environment, ref validation, mutation gate, stage, commit, branch, revert, push, lock, evidence, or dispatcher test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_integration_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_git_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Required schema tests:

```text
git operation schema accepts valid operation
git operation schema rejects missing required fields
git result schema accepts valid result
git result schema rejects missing status
git command policy schema accepts valid policy entry
git command policy schema rejects unknown effect
git command result schema accepts SUCCESS result
git command result schema accepts BLOCKED result
git status diff result schema accepts valid result
git operation result schema accepts valid operation result
git mutation request schema accepts valid STAGE request
git mutation request schema rejects missing evidence for COMMIT
git branch request schema accepts valid branch request
git branch request schema rejects missing policy_decision_id
git ref validation result schema accepts valid validation
git ref validation result schema rejects invalid ref
git stage request schema accepts valid stage request
git commit evidence schema accepts valid commit evidence
git commit evidence schema rejects missing stage_evidence_id
git push request schema accepts valid push request
git push request schema rejects missing promotion_gate_id
git revert request schema accepts dry-run revert request
git lock record schema accepts acquired lock record
git audit event schema accepts valid audit event
git evidence manifest schema accepts valid evidence manifest
git review report schema accepts valid review report
git completion record schema accepts final completion record
```

Blocking if:

```text
schema-invalid operations are accepted
schema-invalid results are accepted
schema-invalid mutation requests are accepted
schema-invalid evidence manifests are accepted
schema-invalid completion records are accepted
schema validation exit code is missing
```

---

# 15. Git Models Verification

Required coverage:

```text
[ ] GitOperation dataclass works with defaults
[ ] GitResult dataclass works with defaults
[ ] GitDiffResult dataclass works
[ ] GitDiffEntry dataclass works
[ ] operation constants are correct strings
[ ] status constants are correct strings
[ ] GitOpType.READ and GitOpType.WRITE are correct
[ ] utc_now_iso returns ISO-like string
[ ] new_id generates unique IDs
[ ] to_dict serializes dataclasses properly
[ ] ALL_GIT_OPS list includes all operations
[ ] GitCommandPolicy dataclass works (FUTURE)
[ ] GitCommandResult dataclass works (FUTURE)
[ ] GitOperationResult dataclass works (FUTURE)
[ ] GitStatusDiffResult dataclass works (FUTURE)
[ ] GitMutationRequest dataclass works (FUTURE)
[ ] GitBranchRequest dataclass works (FUTURE)
[ ] GitRefValidationResult dataclass works (FUTURE)
[ ] GitStageRequest dataclass works (FUTURE)
[ ] GitCommitEvidence dataclass works (FUTURE)
[ ] GitPushRequest dataclass works (FUTURE)
[ ] GitRevertRequest dataclass works (FUTURE)
[ ] GitLockRecord dataclass works (FUTURE)
[ ] GitAuditEvent dataclass works (FUTURE)
[ ] GitEvidenceManifest dataclass works (FUTURE)
[ ] GitReviewReport dataclass works (FUTURE)
[ ] GitCompletionRecord dataclass works (FUTURE)
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 16. Git Operation Correctness

## 16.1 Allowed Read-Only Operations

```text
[ ] git status --short returns structured data (or graceful non-repo error)
[ ] git diff returns bounded output
[ ] git diff --name-only returns file list
[ ] git diff --stat returns summary
[ ] git log --oneline -n 20 returns recent commits
[ ] git branch --list returns branches
[ ] git rev-parse --show-toplevel returns repo root
[ ] git rev-parse HEAD returns current commit
[ ] git knows repo detection works
[ ] read-only operations do not mutate index/source
[ ] read-only operations use GIT_OPTIONAL_LOCKS=0 where available
[ ] read-only operations use --no-ext-diff for diff
[ ] read-only operations use --no-pager
[ ] read-only operations disable pager in env
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 16.2 Blocked Write Operations

Each must return `status=BLOCKED` with appropriate `failure_class`:

```text
[ ] git add . is blocked
[ ] git add -A is blocked
[ ] git add --all is blocked
[ ] git commit is blocked without evidence
[ ] git branch <name> is blocked without governance
[ ] git checkout -b is blocked
[ ] git switch -c is blocked
[ ] git revert is blocked without approval
[ ] git push is blocked
[ ] git push --force is blocked
[ ] git push --force-with-lease is blocked
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 16.3 Permanently Blocked Operations (v1)

Each must return `status=BLOCKED`:

```text
[ ] git reset --hard is blocked
[ ] git reset --mixed is blocked
[ ] git reset --soft is blocked
[ ] git clean -fdx is blocked
[ ] git clean -ffdx is blocked
[ ] git rebase is blocked
[ ] git merge is blocked
[ ] git branch -D is blocked
[ ] git tag -d is blocked
[ ] git remote add is blocked
[ ] git remote remove is blocked
[ ] git remote set-url is blocked
[ ] git config --global is blocked
[ ] git config --system is blocked
[ ] git filter-branch is blocked
[ ] git reflog expire is blocked
[ ] git gc --aggressive is blocked
[ ] git update-ref is blocked
[ ] git worktree add/remove is blocked
[ ] git submodule update with network is blocked
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 17. Git Environment Hardening Checklist

```text
[ ] GIT_TERMINAL_PROMPT=0 is set
[ ] GIT_ASKPASS is empty
[ ] SSH_ASKPASS is empty
[ ] GIT_PAGER=cat is set
[ ] PAGER=cat is set
[ ] GIT_EXTERNAL_DIFF is empty
[ ] GIT_OPTIONAL_LOCKS=0 for read-only operations
[ ] GIT_CONFIG_NOSYSTEM=1 is set
[ ] HOME is isolated (controlled temp directory)
[ ] XDG_CONFIG_HOME is isolated
[ ] LC_ALL=C is set
[ ] -c core.pager=cat is passed
[ ] -c color.ui=false is passed
[ ] -c core.quotepath=false is passed
[ ] -c commit.gpgsign=false is passed
[ ] -c tag.gpgSign=false is passed
[ ] -c log.showSignature=false is passed
[ ] -c credential.helper= is passed
[ ] -c safe.directory=<repo_root> is passed when needed
[ ] -c core.hooksPath=<empty-dir> is passed for mutation commands
[ ] system and user Git config do not affect commands
[ ] include.path and includeIf do not introduce unapproved behavior
[ ] credential prompts are disabled
[ ] GPG signing is disabled
[ ] external diff drivers are disabled
[ ] pager is disabled
[ ] no interactive prompts possible
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 18. Ref Validation Checklist

```text
[ ] empty branch name is rejected
[ ] branch beginning with `-` is rejected
[ ] branch containing `..` is rejected
[ ] branch containing `@{` is rejected
[ ] branch containing ASCII control chars is rejected
[ ] branch with `.lock` suffix is rejected
[ ] branch ending with `/` is rejected
[ ] branch ending with `.` is rejected
[ ] branch with consecutive slashes is rejected
[ ] `main` is detected as protected
[ ] `master` is detected as protected
[ ] `release/` is detected as protected
[ ] `refs/heads/main` is detected as protected
[ ] `refs/tags/*` mutation is blocked
[ ] `refs/remotes/*` mutation is blocked
[ ] remote-tracking ref as local target is rejected
[ ] hash-like string as branch name is rejected
[ ] detached HEAD as mutation target is rejected
[ ] git check-ref-format is called and result recorded
[ ] validation result includes is_valid, is_protected, failure_class
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 19. Evidence / Audit Checklist

```text
[ ] git_operation_history.jsonl is written
[ ] git_result_history.jsonl is written
[ ] git_blocked_history.jsonl is written
[ ] git_mutation_request_history.jsonl is written when mutations attempted
[ ] git_commit_evidence_history.jsonl is written when commits attempted
[ ] git_latest_operation.json is written atomically
[ ] git_latest_result.json is written atomically
[ ] git_evidence_manifest.json is written
[ ] git_review_report.json is written
[ ] git_integration_completion_record.json is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes operation IDs
[ ] evidence includes command text, exit codes, statuses for validation commands
[ ] evidence includes SHA-256 hashes for final evidence artifacts
[ ] secrets are redacted before durable evidence
[ ] unbounded command output is not persisted raw
[ ] blocked operations are evidence events
[ ] invalid operations are evidence events
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 20. Dependency Degradation Checklist

```text
[ ] Policy / Capability Registry unavailable -> mutation blocks, read-only may use restrictive fallback
[ ] Security Sandbox unavailable -> all Git operations block
[ ] Governed Patch Execution unavailable -> stage/commit block
[ ] Human Review unavailable -> approval-required operations block
[ ] Promotion / Release Gate unavailable -> push/release-tag/protected-branch-update block
[ ] Failure Taxonomy unavailable -> use UNKNOWN_GIT_FAILURE, unsafe behavior still blocked
[ ] Evidence writing unavailable -> all Git operations block except schema validation tests
[ ] Missing dependency never defaults to ALLOW
[ ] Missing dependency never triggers direct fallback execution
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 21. Negative Test Checklist

The review must prove that forbidden actions fail closed.

```text
[ ] unknown git operation blocks
[ ] unknown caller role blocks
[ ] git add without patch evidence blocks
[ ] git commit without stage evidence blocks
[ ] git push without promotion gate blocks
[ ] git force push always blocks
[ ] git reset --hard blocks
[ ] git clean -fdx blocks
[ ] git rebase blocks
[ ] git merge blocks
[ ] branch creation without governance blocks
[ ] protected branch overwrite blocks
[ ] stage without explicit paths blocks
[ ] commit without evidence blocks
[ ] commit when HEAD changed since approval blocks
[ ] push without commit evidence blocks
[ ] mutating operation dry-run does not mutate
[ ] git output is bounded
[ ] secret-like output is redacted or blocked
[ ] external diff is disabled
[ ] pager is disabled
[ ] hooks do not run by default
[ ] GIT_OPTIONAL_LOCKS disabled for read-only
[ ] Git config isolation blocks global/user config
[ ] credential prompts disabled
[ ] GPG signing disabled for commit
[ ] hooksPath is isolated for mutation commands
[ ] --no-textconv enforced for diff
[ ] ref validation blocks detached HEAD mutation target
[ ] ref validation blocks tag/remote mutation
[ ] state snapshot required before mutation
[ ] mutation lock required
[ ] idempotency prevents duplicate commit
[ ] nested repo blocks by default
[ ] submodule mutation blocks by default
[ ] evidence is written for all operations including blocked
[ ] latest result is written atomically
[ ] evidence manifest written with hashes
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 22. Future Implementation Checklist

These items are DEFERRED SAFELY for v1. They must not be executable or must return BLOCKED.

## 22.1 Mutation Operations (all blocked by default in v1)

```text
[ ] stage_approved_paths returns BLOCKED without mutation gate pass
[ ] commit_approved_changes returns BLOCKED without mutation gate pass
[ ] create_approved_branch returns BLOCKED without mutation gate pass
[ ] revert_approved_commit returns BLOCKED without mutation gate pass
[ ] push_approved_commit returns BLOCKED without promotion gate
[ ] mutation gate checks all authorities before allowing
[ ] git mutation lock is acquired before mutation execution
[ ] pre/post state snapshots are captured for mutations
[ ] commit evidence is written for successful commits
```

## 22.2 Locking / Concurrency

```text
[ ] GitMutationLock exists and serializes mutation operations
[ ] lock is evidenced on acquire
[ ] lock is evidenced on release
[ ] stale lock handling exists
[ ] read-only operations do not require locks
```

## 22.3 Idempotency

```text
[ ] mutation requests include idempotency_key
[ ] same request with same evidence does not duplicate commits
[ ] HEAD change since original request blocks
[ ] staged state change since original request blocks
```

## 22.4 Dispatcher Pipeline

```text
[ ] dispatch_git_operation exists
[ ] 29-step pipeline is implemented
[ ] read-only operations skip unnecessary gates
[ ] mutating operations pass through all gates
[ ] pipeline failure returns schema-valid BLOCKED/FAILED result
```

Status for each:

```text
PASS (implemented and tested) | DEFERRED SAFELY (stub exists, returns BLOCKED) | NOT IMPLEMENTED
```

---

# 23. Completion Evidence Checklist

## 23.1 Evidence Manifest

Create:

```text
.agentx-init/git/git_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_evidence_manifest.schema.json",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_APPROVED_GIT_MUTATION_ONLY",
  "final_decision": "DONE"
}
```

## 23.2 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 24. Review Report Artifact

Create:

```text
.agentx-init/git/git_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_review_report.schema.json",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "review_document_id": "GIT_INTEGRATION_LAYER_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/git/git_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/git/git_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/git/git_integration_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

---

# 25. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/git/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by Git Integration tests
Git Integration writes source files directly
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots without deviation
```

---

# 26. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Git Command | Evidence | Schema | Runtime Artifact Boundary | Hook | Remote | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high | critical>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
HIGH items cannot be accepted for DONE unless the review explicitly proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/git/` require a deviation entry.
Mutation deferrals require deviation entries.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 27. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
git models:
command allowlist:
command runner:
environment hardening:
ref validation:
read-only operations:
blocked operations:
mutation gating:
mutation operations:
locking:
evidence/audit:
dispatcher pipeline:
dependency degradation:
negative tests:
source mutation check:
evidence manifest:
review report:
evidence hashes:
completion record:
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
```

---

# 29. Issue Severity Classification

## 29.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
raw shell executes
unknown Git command executes
git add . is allowed
git add -A is allowed
git commit runs without approved stage evidence
git push runs without promotion gate
git reset --hard is allowed
git clean -fdx is allowed
git rebase is allowed
git push --force is allowed
protected branch can be overwritten
MCP client can mutate Git state
policy denial is ignored
sandbox denial is ignored
patch evidence is not required for staging
stage evidence is not required for commit
commit evidence is missing
required evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
secrets are logged unredacted
unbounded diff output is persisted
external diff runs by default
pager runs by default
Git hook runs by default
read-only Git operation mutates index/source state
source mutation occurs outside approved Git operation pipeline
required area remains NOT CHECKED
required command remains NOT RUN
```

## 29.2 HIGH

High issues must be fixed before this layer is used by an autonomous orchestrator.

```text
partial environment hardening
partial ref validation coverage
partial mutation gate coverage
partial evidence coverage
review environment not recorded
some expected Git modules missing but not used yet
runtime artifact boundary exception lacks justification
mutation deferral lacks deviation entry
```

## 29.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled future-step definitions
push intentionally deferred with proof
revert intentionally deferred with proof
human approval interface intentionally stubbed with blocking behavior
markdown report writer intentionally absent
```

---

# 30. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---|---:|---|
| Structure and expected files | 1.0 | Git package, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Git models | 1.0 | All required dataclasses exist and serialize correctly. |
| Read-only operations | 1.0 | Status, diff, log work for approved roles with bounded output and redaction. |
| Blocked operations | 1.0 | All forbidden and mutation operations return BLOCKED with failure_class. |
| Environment hardening | 1.0 | All required env vars, Git config args, and isolation controls are in place. |
| Ref validation | 1.0 | Branch/ref/tag validation with protected namespace detection works. |
| Evidence/audit | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, and completion record exist. |
| Negative safety behavior | 1.0 | All blocked, forbidden, and bypass cases fail closed. |
| Source-mutation and reproducibility safety | 1.0 | Clean git status, exact commands, exit codes, environment, hashes, and deviation register are recorded. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled Git integration
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
raw shell execution caps score at 4.0
direct source mutation caps score at 4.0
policy/sandbox bypass caps score at 4.0
unbounded output persisted caps score at 5.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
```

---

# 31. GO / NO-GO Rules

## 31.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
Git models tests pass
read-only Git operation tests pass
blocked Git operation tests pass
environment hardening tests pass
ref validation tests pass
evidence/audit tests pass
negative tests pass
source mutation check passes
evidence manifest exists
evidence hashes exist
review report exists
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 31.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
raw shell executes
unknown Git command executes
git add . is allowed
git commit runs without approved stage evidence
git push runs without promotion gate
git reset --hard is allowed
git clean -fdx is allowed
git rebase is allowed
git push --force is allowed
protected branch can be overwritten
policy denial is ignored
sandbox denial is ignored
patch evidence is not required for staging
stage evidence is not required for commit
commit evidence is missing
required evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
secrets are logged unredacted
external diff/pager/hooks run by default
read-only operation mutates index/source state
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 32. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix command allowlist entries
fix argument-vector construction
fix environment hardening
fix ref validation logic
fix mutation gate checks
fix bounded output enforcement
fix evidence writing
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not remove sandbox checks to pass tests
do not allow raw shell execution
do not allow unbounded output persistence
do not allow git add . to pass tests
do not allow commit without evidence
do not allow push without promotion gate
do not skip environment hardening
do not skip ref validation
do not omit hashes for final DONE
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 33. Definition of Done

The Git Integration Layer is done when it proves:

```text
all target files exist
all schemas exist
all tests exist
Git command policy exists and is enforced
Git operation schemas validate correctly
read-only Git operations work for approved roles
unknown Git operations fail closed
blocked Git commands fail closed
Git mutation requires policy approval
Git mutation requires sandbox approval
staging requires patch evidence
commit requires stage evidence and commit evidence
push requires promotion gate
branch creation is controlled
rollback/revert is controlled
raw shell is not used
Git write operations are blocked by default
MCP clients cannot mutate Git state
external diff/pager/hooks do not run by default
read-only commands do not mutate index/source state
all Git operations write evidence
evidence hashes are written
secrets are redacted before evidence
environment hardening is in place for all Git commands
ref validation is in place for all mutation operations
mutation locking is in place for all mutation operations
dependency degradation is handled safely
no unapproved source mutation occurs
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_integration_schemas.py
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

# 34. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
Git models test result
read-only operation test result
blocked operation test result
environment hardening test result
ref validation test result
evidence/audit test result
negative-test result
git status output
evidence manifest
review report
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
operation IDs and result IDs
no direct source mutation
no raw shell execution
no policy bypass
no sandbox bypass
no commit without evidence
no push without promotion gate
bounded output behavior
environment hardening proof
ref validation proof
mutation gating proof
evidence/audit proof
secrets redacted
hashes for final evidence artifacts
```

---

# 35. Completion Evidence Record

After validation, create:

```text
.agentx-init/git/git_integration_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_completion_record.schema.json",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "component_name": "Git Integration Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/git/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/git/",
  "basis_documents": [
    "GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC",
    "GIT_INTEGRATION_LAYER_IMPLEMENTATION_REVIEW_AND_DOD_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "git_operations_verified": [],
  "blocked_git_operations_verified": [],
  "branch_rules_verified": [],
  "commit_rules_verified": [],
  "push_rules_verified": [],
  "rollback_revert_rules_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "patch_execution_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "environment_hardening_verified": [],
  "lock_idempotency_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/git/git_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/git/git_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 36. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: 10/10
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
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 37. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/git/ exists
[ ] schemas exist (2 existing + 15 FUTURE)
[ ] tests exist (3 existing + 17 FUTURE)

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Git Models:
[ ] GitOperation, GitResult, GitDiffResult work
[ ] GitOpType.READ/WRITE correct
[ ] helpers (new_id, utc_now_iso, to_dict) work
[ ] all FUTURE dataclasses defined and instantiable

Command Allowlist:
[ ] structured allowlist exists with 10+ read-only entries
[ ] unknown operations blocked
[ ] unknown caller roles blocked

Environment Hardening:
[ ] GIT_TERMINAL_PROMPT=0
[ ] GIT_PAGER=cat, PAGER=cat
[ ] GIT_EXTERNAL_DIFF disabled
[ ] GIT_OPTIONAL_LOCKS=0 for read-only
[ ] GIT_CONFIG_NOSYSTEM=1
[ ] HOME isolated
[ ] XDG_CONFIG_HOME isolated
[ ] credential helper disabled
[ ] GPG signing disabled
[ ] hooksPath isolated for mutation commands
[ ] --no-ext-diff for diff operations

Ref Validation:
[ ] empty name rejected
[ ] protected branch patterns rejected
[ ] remote-tracking refs rejected as local targets
[ ] detached HEAD rejected as mutation target
[ ] tag mutation blocked in v1

Read-Only Operations:
[ ] status returns structured data
[ ] diff returns bounded output
[ ] log returns bounded history
[ ] no index/source mutation during read-only

Blocked Operations:
[ ] git commit blocked without evidence
[ ] git push blocked without promotion gate
[ ] git reset --hard blocked
[ ] git clean -fdx blocked
[ ] git rebase blocked
[ ] git merge blocked
[ ] force push blocked

Evidence:
[ ] operation history written
[ ] result history written
[ ] blocked history written
[ ] latest operation written atomically
[ ] latest result written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Negative Safety:
[ ] all forbidden operations fail closed
[ ] bypass attempts fail closed
[ ] missing dependencies fail closed

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 38. Final Sign-Off Template

Use this after implementation validation.

```text
Git Integration Layer Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>
- jsonschema: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- git models coverage: PASS/FAIL
- command allowlist coverage: PASS/FAIL
- command runner coverage: PASS/FAIL/DEFERRED SAFELY
- environment hardening coverage: PASS/FAIL
- ref validation coverage: PASS/FAIL
- read-only operation coverage: PASS/FAIL
- blocked operation coverage: PASS/FAIL
- mutation gate coverage: PASS/FAIL
- stage operation: PASS/FAIL/DEFERRED SAFELY
- commit operation: PASS/FAIL/DEFERRED SAFELY
- branch operation: PASS/FAIL/DEFERRED SAFELY
- revert operation: PASS/FAIL/DEFERRED SAFELY
- push operation: PASS/FAIL/DEFERRED SAFELY
- lock/concurrency coverage: PASS/FAIL/DEFERRED SAFELY
- dispatcher pipeline coverage: PASS/FAIL/DEFERRED SAFELY
- evidence/audit coverage: PASS/FAIL
- dependency degradation coverage: PASS/FAIL
- negative safety coverage: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING

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
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 39. Final Rating

This v3 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It provides a complete post-implementation review template for the Git Integration Layer with all required checklist sections: file inventory (4 existing + 15 FUTURE .py files, 2 existing + 15 FUTURE schemas, 3 existing + 17 FUTURE test files), validation commands, compile/pytest/schema results, git model verification, read-only operation correctness, blocked operation verification, environment hardening checklist (25 controls), ref validation checklist (18 controls), evidence/audit checklist (19 controls), dependency degradation checklist (9 controls), negative test checklist (37 tests), future implementation checklist, scoring rubric with hard caps, GO/NO-GO rules, remediation rules, frozen final checklist (66 items), and final sign-off template. roadmap_layer is corrected to 6 (Phase A).
```
