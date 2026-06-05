# SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_REVIEW_AND_DOD
version: v3.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY
component_name: Security Sandbox / Filesystem Boundary Layer
roadmap_layer: 1
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
basis_documents:
  - SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_EQC_FIC_SIB_SCHEMA_CONTRACT
  - SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_SPEC
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
canonical_subdirectory: tools/agentx_evolve/security/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/security/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Security Sandbox / Filesystem Boundary Layer**.

Use this document after code is committed to determine whether the sandbox is complete, safe, auditable, deterministic, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether path boundary checks are complete
whether safe file operations are complete
whether subprocess checks block by default
whether network checks block by default
whether secret redaction covers known patterns
whether sandbox evidence writing is atomic
whether Initiator compatibility integration is complete
whether negative safety tests pass
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

EQC is primary because the Security Sandbox is a safety-critical deterministic gate. It decides whether a file, path, command, network request, or secret operation is ALLOW, BLOCK, WARN, or needs additional governance.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
None for this layer.
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The Security Sandbox / Filesystem Boundary Layer is the first deterministic safety layer in the Agent_X self-evolution stack. It gates all file, path, subprocess, network, and secret operations.

It must not be bypassable. It must not have default-allow behavior for dangerous operations. It must fail closed.

The sandbox decides:

```text
whether a path is inside the repository
whether a symlink escapes the repository
whether an L0 path may be written
whether a protected path may be written
whether a file may be read
whether a file may be written (and under which conditions: runtime vs source)
whether a subprocess command may run
whether a network request may proceed
whether secrets are redacted from output text
```

It must not decide:

```text
which patch to apply
which model to call
which tool to invoke
which orchestration step to execute
which promotion to allow
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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, expose, promote, approve, or bypass controls. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

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
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_sandbox_schema.py -v
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation (scoped): PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If unrelated future-layer tests exist under `tools/agentx_evolve/tests`, the review must also record a scoped Security Sandbox pytest command such as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_path_boundary.py \
  tools/agentx_evolve/tests/test_safe_file_ops.py \
  tools/agentx_evolve/tests/test_safe_subprocess.py \
  tools/agentx_evolve/tests/test_network_policy.py \
  tools/agentx_evolve/tests/test_secret_redactor.py \
  tools/agentx_evolve/tests/test_sandbox_schema.py \
  tools/agentx_evolve/tests/test_sandbox_negative_cases.py \
  tools/agentx_evolve/tests/test_sandbox_evidence.py \
  tools/agentx_evolve/tests/test_sandbox_agentx_integration.py
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

## 7.1 Required Security Package

Expected location:

```text
tools/agentx_evolve/security/
```

Expected files:

```text
tools/agentx_evolve/security/__init__.py
tools/agentx_evolve/security/security_models.py
tools/agentx_evolve/security/sandbox_policy.py
tools/agentx_evolve/security/path_boundary.py
tools/agentx_evolve/security/safe_file_ops.py
tools/agentx_evolve/security/safe_subprocess.py
tools/agentx_evolve/security/network_policy.py
tools/agentx_evolve/security/secret_redactor.py
tools/agentx_evolve/security/sandbox_evidence.py
tools/agentx_evolve/security/initiator_compat.py
```

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
sandbox_policy.schema.json
sandbox_decision.schema.json
path_boundary_result.schema.json
safe_file_operation.schema.json
safe_subprocess_result.schema.json
network_policy_result.schema.json
secret_redaction_result.schema.json
sandbox_violation.schema.json
sandbox_audit.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_path_boundary.py
test_safe_file_ops.py
test_safe_subprocess.py
test_network_policy.py
test_secret_redactor.py
test_sandbox_schema.py
test_sandbox_evidence.py
test_sandbox_negative_cases.py
test_sandbox_agentx_integration.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/security/
```

Expected artifacts:

```text
sandbox_decisions.jsonl
sandbox_violations.jsonl
latest_sandbox_decision.json
security_sandbox_evidence_manifest.json
security_sandbox_review_report.json
security_sandbox_completion_record.json
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Security package location | `tools/agentx_evolve/security/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation test | `test_sandbox_schema.py` exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Path boundary (inside/outside repo) | `check_path_boundary` blocks outside paths | PASS / PARTIAL / FAIL / NOT CHECKED |
| Symlink escape detection | symlink escape always blocks for all ops | PASS / PARTIAL / FAIL / NOT CHECKED |
| L0 write block | `L0/` writes always BLOCK | PASS / PARTIAL / FAIL / NOT CHECKED |
| Protected path block | protected paths block writes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Blocked write paths | `blocked_write_paths` enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source write default block | source writes BLOCK by default | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime write allow | `.agentx-init/` writes ALLOW by default | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe read file | read succeeds for existing, blocks for forbidden | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe write file | write with governance/session/rollback gates | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe exact edit | single match replace succeeds, no match / multi blocks | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch precheck | `safe_patch_precheck` blocks forbidden targets | PASS / PARTIAL / FAIL / NOT CHECKED |
| Subprocess default block | `check_subprocess_allowed` blocks by default | PASS / PARTIAL / FAIL / NOT CHECKED |
| Subprocess destructive patterns | rm -rf, sudo, curl|sh, git push blocked | PASS / PARTIAL / FAIL / NOT CHECKED |
| Subprocess allowlist | allowlisted commands pass | PASS / PARTIAL / FAIL / NOT CHECKED |
| Network default block | `check_network_allowed` blocks by default | PASS / PARTIAL / FAIL / NOT CHECKED |
| Secret redaction | API keys, tokens, long secrets redacted | PASS / PARTIAL / FAIL / NOT CHECKED |
| Custom redaction patterns | policy-provided patterns applied | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence writing | `append_sandbox_decision` writes JSONL | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence atomic write | `write_latest_sandbox_decision` atomic | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence schema validation | schema-invalid decisions are rejected | PASS / PARTIAL / FAIL / NOT CHECKED |
| Initiator compat | `InitiatorCompat` adapts to initiator services | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source guard integration | `check_source_guard` enforces mutation scope | PASS / PARTIAL / FAIL / NOT CHECKED |
| Degraded mode | missing initiator falls back, fails closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety tests | escape, traversal, L0, shell, network all blocked | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| SandboxPolicy dataclass | `security_models.py` | `test_sandbox_schema.py` | policy schema validation | PASS / PARTIAL / FAIL / NOT CHECKED |
| SandboxDecision dataclass | `security_models.py` | `test_sandbox_schema.py` | decision schema validation | PASS / PARTIAL / FAIL / NOT CHECKED |
| PathBoundaryResult dataclass | `security_models.py` | `test_sandbox_schema.py` | path_boundary_result schema | PASS / PARTIAL / FAIL / NOT CHECKED |
| Default policy creation | `sandbox_policy.py` | policy tests | sandbox_policy.jsonl | PASS / PARTIAL / FAIL / NOT CHECKED |
| Path normalization | `path_boundary.py` | `test_path_boundary.py` | path_boundary decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Path boundary check | `path_boundary.py` | `test_path_boundary.py` | sandbox_decisions.jsonl | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe read file | `safe_file_ops.py` | `test_safe_file_ops.py` | decision evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe write file | `safe_file_ops.py` | `test_safe_file_ops.py` | decision evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Safe exact edit | `safe_file_ops.py` | `test_safe_file_ops.py` | decision evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch precheck | `safe_file_ops.py` | `test_safe_file_ops.py` | decision evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Subprocess check | `safe_subprocess.py` | `test_safe_subprocess.py` | subprocess decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Network policy | `network_policy.py` | `test_network_policy.py` | network decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Secret redaction | `secret_redactor.py` | `test_secret_redactor.py` | redaction results | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence append | `sandbox_evidence.py` | `test_sandbox_evidence.py` | sandbox_decisions.jsonl | PASS / PARTIAL / FAIL / NOT CHECKED |
| Initiator compat | `initiator_compat.py` | `test_sandbox_agentx_integration.py` | integration status | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | all modules | `test_sandbox_negative_cases.py` | pytest output | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | schemas/ | `test_sandbox_schema.py` | schema test output | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Security Package Files

```text
[ ] tools/agentx_evolve/security/__init__.py
[ ] tools/agentx_evolve/security/security_models.py
[ ] tools/agentx_evolve/security/sandbox_policy.py
[ ] tools/agentx_evolve/security/path_boundary.py
[ ] tools/agentx_evolve/security/safe_file_ops.py
[ ] tools/agentx_evolve/security/safe_subprocess.py
[ ] tools/agentx_evolve/security/network_policy.py
[ ] tools/agentx_evolve/security/secret_redactor.py
[ ] tools/agentx_evolve/security/sandbox_evidence.py
[ ] tools/agentx_evolve/security/initiator_compat.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] sandbox_policy.schema.json
[ ] sandbox_decision.schema.json
[ ] path_boundary_result.schema.json
[ ] safe_file_operation.schema.json
[ ] safe_subprocess_result.schema.json
[ ] network_policy_result.schema.json
[ ] secret_redaction_result.schema.json
[ ] sandbox_violation.schema.json
[ ] sandbox_audit.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_path_boundary.py
[ ] test_safe_file_ops.py
[ ] test_safe_subprocess.py
[ ] test_network_policy.py
[ ] test_secret_redactor.py
[ ] test_sandbox_schema.py
[ ] test_sandbox_evidence.py
[ ] test_sandbox_negative_cases.py
[ ] test_sandbox_agentx_integration.py
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
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_sandbox_schema.py -v
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
any Security Sandbox Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_command: <optional scoped security sandbox pytest command>
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
any required path_boundary, safe_file_ops, safe_subprocess, network_policy, secret_redactor, sandbox_evidence, sandbox_schema, sandbox_negative_cases, or sandbox_agentx_integration test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_sandbox_schema.py -v
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_sandbox_schema.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Required schema tests:

```text
sandbox_policy schema accepts valid policy
sandbox_decision schema accepts valid decision
sandbox_decision schema rejects missing required fields
path_boundary_result schema accepts valid result
safe_file_operation schema accepts valid result
safe_subprocess_result schema accepts valid result
secret_redaction schema accepts valid result
sandbox_audit schema accepts valid audit
sandbox_audit schema rejects missing required fields
```

Blocking if:

```text
schema-invalid policies are accepted
schema-invalid decisions are accepted
schema-invalid audit events are accepted
schema validation exit code is missing
```

---

# 15. Module Verification Checklist

## 15.1 security_models.py — Model Checks

```text
[ ] SandboxPolicy dataclass with all required fields
[ ] SandboxDecision dataclass with all required fields
[ ] SandboxViolation dataclass with all required fields
[ ] PathBoundaryResult dataclass with all required fields
[ ] SafeFileOperationResult dataclass with all required fields
[ ] SafeSubprocessResult dataclass with all required fields
[ ] NetworkPolicyResult dataclass with all required fields
[ ] SecretRedactionResult dataclass with all required fields
[ ] Decision string constants: ALLOW, BLOCK, WARN, NEEDS_GOVERNANCE, NEEDS_ROLLBACK_SNAPSHOT, NEEDS_SESSION
[ ] Status string constants: SUCCESS, BLOCKED, FAILED, DRY_RUN, PASS
[ ] Operation string constants: READ, WRITE, EDIT, PATCH_PRECHECK, SUBPROCESS, NETWORK, REDACT
[ ] Helper functions: utc_now_iso, new_id, to_dict, sha256_text, sha256_file, has_control_chars
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.2 sandbox_policy.py — Policy Module Checks

```text
[ ] default_sandbox_policy creates policy with safe defaults
[ ] default sandbox policy: source_write_allowed=False
[ ] default sandbox policy: runtime_write_allowed=True
[ ] default sandbox policy: network_allowed=False
[ ] default sandbox policy: shell_allowed=False
[ ] default sandbox policy: protected_paths includes L0/, agent_x/runtime/, core/
[ ] default sandbox policy: allowlisted_write_paths includes .agentx-init/
[ ] default sandbox policy: blocked_write_paths includes L0/
[ ] load_sandbox_policy_from_dict loads from dict with field filtering
[ ] merge_sandbox_policy merges without duplicating protected/blocked paths
[ ] is_runtime_path detects paths under .agentx-init/
[ ] is_protected_path matches protected path prefixes
[ ] is_l0_path detects L0/ prefix
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.3 path_boundary.py — Path Boundary Checks

```text
[ ] normalize_repo_path resolves relative paths against repo_root
[ ] normalize_repo_path detects control characters
[ ] normalize_repo_path resolves absolute paths
[ ] normalize_repo_path detects inside/outside repo
[ ] normalize_repo_path detects symlinks and symlink escape
[ ] normalize_repo_path computes is_l0 and is_protected when policy given
[ ] check_path_boundary returns BLOCK for outside-repo paths
[ ] check_path_boundary returns BLOCK for symlink escape
[ ] check_path_boundary returns BLOCK for L0 writes/edits
[ ] check_path_boundary returns BLOCK for protected path writes
[ ] check_path_boundary returns BLOCK for blocked_write_paths
[ ] check_path_boundary returns BLOCK for source writes when disabled
[ ] check_path_boundary returns ALLOW for valid inside-repo read
[ ] path_to_repo_relative returns correct relative path
[ ] is_inside_repo returns correct boolean
[ ] detect_symlink_escape returns correct boolean
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.4 safe_file_ops.py — Safe File Operations

```text
[ ] safe_read_file returns SUCCESS with content for valid file
[ ] safe_read_file returns BLOCKED for paths outside repo
[ ] safe_read_file returns FAILED for non-existent file
[ ] safe_read_file returns FAILED for directory path
[ ] safe_read_file returns BLOCKED for files exceeding max_file_size_bytes
[ ] safe_read_file returns FAILED on read error
[ ] safe_write_file returns BLOCKED when source writes disabled
[ ] safe_write_file returns SUCCESS for runtime writes (under .agentx-init/)
[ ] safe_write_file returns NEEDS_GOVERNANCE when governance required
[ ] safe_write_file returns NEEDS_SESSION when session required
[ ] safe_write_file returns NEEDS_ROLLBACK_SNAPSHOT when rollback required
[ ] safe_write_file returns BLOCKED when compat missing for source write
[ ] safe_write_file returns BLOCKED when source guard non-enforcing
[ ] safe_write_file returns BLOCKED when mutation not allowlisted
[ ] safe_write_file performs atomic write with fsync
[ ] safe_write_file cleans up temp file on error
[ ] safe_exact_edit returns SUCCESS for single match
[ ] safe_exact_edit returns BLOCKED for no match (OLD_TEXT_NOT_FOUND)
[ ] safe_exact_edit returns BLOCKED for multiple matches (MULTIPLE_MATCHES)
[ ] safe_exact_edit dry_run does not modify file
[ ] safe_patch_precheck returns BLOCK when any target is blocked
[ ] safe_patch_precheck returns ALLOW when all targets allowed
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.5 safe_subprocess.py — Subprocess Checks

```text
[ ] check_subprocess_allowed blocks when shell not allowed by policy
[ ] check_subprocess_allowed validates command is list of strings
[ ] check_subprocess_allowed blocks control characters in command tokens
[ ] check_subprocess_allowed blocks empty command
[ ] check_subprocess_allowed blocks rm -rf /
[ ] check_subprocess_allowed blocks rm -rf .
[ ] check_subprocess_allowed blocks sudo
[ ] check_subprocess_allowed blocks su
[ ] check_subprocess_allowed blocks curl | sh
[ ] check_subprocess_allowed blocks wget | sh
[ ] check_subprocess_allowed blocks bash -c
[ ] check_subprocess_allowed blocks sh -c
[ ] check_subprocess_allowed blocks python -c
[ ] check_subprocess_allowed blocks git push
[ ] check_subprocess_allowed blocks git reset --hard
[ ] check_subprocess_allowed blocks git clean -fdx
[ ] check_subprocess_allowed blocks | sh pipe ending
[ ] check_subprocess_allowed blocks | bash pipe ending
[ ] check_subprocess_allowed blocks | zsh pipe ending
[ ] check_subprocess_allowed blocks commands ending in | sh
[ ] check_subprocess_allowed blocks commands starting with bash/sh/zsh
[ ] check_subprocess_allowed blocks if working_directory is outside repo
[ ] check_subprocess_allowed returns ALLOW if command matches allowlist (list form)
[ ] check_subprocess_allowed returns ALLOW if command matches allowlist (string form)
[ ] check_subprocess_allowed blocks unallowlisted command even when shell_allowed=True
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.6 network_policy.py — Network Checks

```text
[ ] check_network_allowed blocks by default (network_allowed=False)
[ ] check_network_allowed fails when target is None
[ ] check_network_allowed blocks all targets in v1 (no allowlist)
[ ] check_network_allowed returns NetworkPolicyResult with correct fields
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 15.7 secret_redactor.py — Secret Redactor

```text
[ ] redact_secrets redacts OPENAI_API_KEY values
[ ] redact_secrets redacts ANTHROPIC_API_KEY values
[ ] redact_secrets redacts GOOGLE_API_KEY values
[ ] redact_secrets redacts GITHUB_TOKEN values
[ ] redact_secrets redacts GITLAB_TOKEN values
[ ] redact_secrets redacts AWS_SECRET_ACCESS_KEY values
[ ] redact_secrets redacts generic long tokens (sk-...)
[ ] redact_secrets redacts 40+ char alphanumeric tokens
[ ] redact_secrets preserves non-secret text unchanged
[ ] redact_secrets applies custom patterns from policy
[ ] redact_secrets returns SUCCESS for empty input
[ ] redact_secrets works with None policy (uses default patterns only)
[ ] redact_secrets records redaction_count and redaction_types
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

---

# 16. Schema Validation Checklist

For each schema, validate that:

```text
- valid example passes
- missing required field is rejected
- invalid enum value is rejected (where applicable)
```

```text
[ ] sandbox_policy.schema.json — valid policy accepts
[ ] sandbox_policy.schema.json — missing required field rejects
[ ] sandbox_decision.schema.json — valid decision accepts
[ ] sandbox_decision.schema.json — missing decision field rejects
[ ] sandbox_decision.schema.json — invalid decision enum rejects
[ ] path_boundary_result.schema.json — valid result accepts
[ ] safe_file_operation.schema.json — valid operation accepts
[ ] safe_subprocess_result.schema.json — valid result accepts
[ ] secret_redaction_result.schema.json — valid result accepts
[ ] sandbox_audit.schema.json — valid audit accepts
[ ] sandbox_audit.schema.json — missing decision field rejects
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

---

# 17. Security Decision Correctness Checklist

Every security decision must follow fail-closed semantics.

```text
[ ] Path outside repo -> BLOCK (any operation)
[ ] Path with control characters -> BLOCK
[ ] Symlink escape -> BLOCK (any operation)
[ ] L0 path write -> BLOCK (WRITE, EDIT, PATCH_PRECHECK)
[ ] L0 path read -> ALLOW (READ not blocked by L0 rule)
[ ] Protected path write -> BLOCK
[ ] Blocked write path -> BLOCK
[ ] Source write (outside .agentx-init/) -> BLOCK by default
[ ] Source write with governance requirement, no gov ID -> NEEDS_GOVERNANCE
[ ] Source write with session requirement, no session ID -> NEEDS_SESSION
[ ] Source write with rollback requirement, no rollback ID -> NEEDS_ROLLBACK_SNAPSHOT
[ ] Source write with no compat -> BLOCK (source guard required)
[ ] Source write with non-enforcing source guard -> BLOCK
[ ] Source write with mutation allowlist (approved) -> ALLOW
[ ] Source write with mutation allowlist (unapproved) -> BLOCK
[ ] Runtime write under .agentx-init/ -> ALLOW (when runtime_write_allowed=True)
[ ] Runtime write not in allowlisted_write_paths -> BLOCK
[ ] Read inside repo -> ALLOW (path boundary only)
[ ] Read non-existent file -> FAILED (not BLOCKED)
[ ] Read file > max_size -> BLOCKED
[ ] Subprocess by default -> BLOCK
[ ] Subprocess with shell_allowed=False -> BLOCK
[ ] Subprocess with destructive pattern -> BLOCK
[ ] Subprocess with allowlisted command -> ALLOW
[ ] Network by default -> BLOCK
[ ] Network with network_allowed=True but v1 no allowlist -> BLOCK
[ ] Secret redaction (no secrets) -> SUCCESS with 0 redactions
[ ] Secret redaction (known patterns) -> SUCCESS with redactions
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

---

# 18. Integration Checklist

## 18.1 InitiatorCompat Integration

```text
[ ] InitiatorCompat imports initiator modules gracefully (degraded on ImportError)
[ ] get_repo_root returns repo root from path_registry or fallback
[ ] get_runtime_state_root returns .agentx-init path
[ ] get_protected_paths returns L0/, agent_x/runtime/, core/
[ ] check_source_guard uses mutation_allowlist when available
[ ] check_source_guard falls back to initiator source_guard
[ ] check_source_guard returns enforcing/non-enforcing status
[ ] validate_schema delegates to initiator schema_validation
[ ] validate_schema fails closed when schema validation unavailable
[ ] write_json_atomic delegates to initiator artifact_io
[ ] write_json_atomic falls back to local atomic write
[ ] append_audit_event delegates to initiator audit_log
[ ] append_audit_event falls back to local audit file
[ ] refresh_integration_status updates module cache and degraded flag
[ ] integration_failures list records import errors
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 18.2 sandbox_evidence Integration

```text
[ ] append_sandbox_decision writes to .agentx-init/security/sandbox_decisions.jsonl
[ ] append_sandbox_decision validates schema when compat provided
[ ] append_sandbox_decision rejects schema-invalid decisions
[ ] append_sandbox_violation writes to .agentx-init/security/sandbox_violations.jsonl
[ ] append_sandbox_violation validates schema when compat provided
[ ] write_latest_sandbox_decision writes atomically
[ ] write_latest_sandbox_decision validates schema when compat provided
[ ] build_sandbox_audit_event creates correct audit dict
[ ] JSONL appends are atomic with fcntl locking
[ ] Concurrent appends are safe (flock)
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

## 18.3 Path Integration

```text
[ ] safe_read_file calls check_path_boundary internally
[ ] safe_write_file calls check_path_boundary internally
[ ] safe_write_file checks allowlisted_write_paths for runtime writes
[ ] safe_write_file checks source_write_allowed for source writes
[ ] safe_exact_edit calls safe_read_file then safe_write_file
[ ] safe_patch_precheck calls check_write_allowed for each target
[ ] check_path_boundary returns SandboxDecision (not PathBoundaryResult)
[ ] check_path_boundary uses normalize_repo_path internally
[ ] safe_file_ops uses check_read_allowed / check_write_allowed helpers
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

---

# 19. Negative Test Checklist

Negative tests prove that the sandbox cannot be bypassed.

```text
[ ] Attempted symlink escape never allows any operation (READ, WRITE, EDIT)
[ ] Attempted L0 write never allows (WRITE, EDIT, PATCH_PRECHECK)
[ ] Attempted path escape ../ never allows any operation
[ ] Attempted raw shell (bash -c, sh -c) always blocks
[ ] Attempted network always blocks by default
[ ] rm -rf / always blocks (even with shell_allowed=True)
[ ] rm -rf . always blocks (even with shell_allowed=True)
[ ] sudo always blocks
[ ] curl | sh always blocks
[ ] git push always blocks
[ ] Unallowlisted commands always block even when shell_allowed=True
[ ] Empty subprocess command blocks
[ ] Write outside .agentx-init/ blocks by default (source writes blocked)
[ ] Read outside repo blocks
[ ] Write to blocked_write_paths always blocks
[ ] Write to protected_paths always blocks
```

Status: PASS / PARTIAL / FAIL / NOT CHECKED

---

# 20. Completion Evidence Checklist

## 20.1 Evidence Manifest

Create:

```text
.agentx-init/security/security_sandbox_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "security_sandbox_evidence_manifest",
  "component_id": "AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
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
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_sandbox_schema.py -v",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [
    ".agentx-init/security/sandbox_decisions.jsonl",
    ".agentx-init/security/sandbox_violations.jsonl",
    ".agentx-init/security/latest_sandbox_decision.json"
  ],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "path_boundary_status": "PASS",
  "safe_file_ops_status": "PASS",
  "safe_subprocess_status": "PASS",
  "network_policy_status": "PASS",
  "secret_redaction_status": "PASS",
  "sandbox_evidence_status": "PASS",
  "initiator_compat_status": "PASS_OR_DEGRADED_SAFELY",
  "negative_test_status": "PASS",
  "schema_validation_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
security_sandbox_evidence_manifest.json
security_sandbox_review_report.json
security_sandbox_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_sandbox_decision.json, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/security/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register. Unapproved evidence writes outside the runtime root are a source-mutation or artifact-boundary failure.

## 20.2 Review Report Artifact

Create:

```text
.agentx-init/security/security_sandbox_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "security_sandbox_review_report",
  "component_id": "AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY",
  "review_document_id": "SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_REVIEW_AND_DOD",
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
  "evidence_manifest_path": ".agentx-init/security/security_sandbox_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/security/security_sandbox_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/security/security_sandbox_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

### 20.2.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

## 20.3 Completion Record Artifact

Create:

```text
.agentx-init/security/security_sandbox_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "security_sandbox_completion_record",
  "component_id": "AGENTX_SECURITY_SANDBOX_FILESYSTEM_BOUNDARY",
  "review_document_id": "SECURITY_SANDBOX_FILESYSTEM_BOUNDARY_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "completed_at": "<UTC timestamp>",
  "final_verdict": "DONE",
  "blockers_resolved": 0,
  "issues_resolved": 0,
  "total_positive_tests": <int>,
  "total_negative_tests": <int>,
  "schema_validations_passed": <int>,
  "manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "deviations_accepted": []
}
```

---

# 21. Implementation Rating

```text
implementation_rating: <0.0 - 10.0>
```

Ratings guidance:

```text
10.0 — all checks pass, all evidence exists, no blockers, no deviations without documentation
9.0-9.9 — minor documentation or test gaps, no safety bypass possible
7.0-8.9 — some coverage gaps but safety invariants hold
< 7.0 — safety invariants not provably enforced
```

A rating below 10.0 must document the gap and record it in the deviation register.

---

# 22. Final Verdict

```text
final_verdict: DONE | NOT DONE
```

The implementation is `DONE` only when:

```text
[ ] compileall passes (exit_code 0)
[ ] all required tests pass (exit_code 0)
[ ] all schema validations pass
[ ] all negative tests confirm block behavior
[ ] path boundary checks block all escape vectors
[ ] safe file ops enforce all gates
[ ] subprocess blocks all destructive patterns
[ ] network blocks by default
[ ] secret redactor covers known patterns
[ ] evidence writing is atomic and schema-validated
[ ] InitiatorCompat degrades safely
[ ] evidence manifest is written
[ ] review report is written
[ ] completion record is written
[ ] all evidence hashes are present
[ ] working tree is clean or only expected runtime artifacts exist
[ ] no safety-critical bypass exists
[ ] all blockers are resolved
[ ] accepted deviations are documented
```

---

# 23. Deviation Register

Record any accepted deviations from the contract here.

```text
| Deviation ID | Description | Reason | Impact | Accepted By |
|---|---|---|---|---|
| <id> | <description> | <reason> | <safety impact> | <reviewer> |
```

---

# 24. Final Sign-Off

```text
review_document_rating: 10/10
implementation_rating: <rating>
final_verdict: <DONE | NOT DONE>
signed_off_by: <name or tool>
signed_off_at: <UTC timestamp>
```

The implementation shall not be marked `DONE` without a completed review report, evidence manifest, and completion record.
