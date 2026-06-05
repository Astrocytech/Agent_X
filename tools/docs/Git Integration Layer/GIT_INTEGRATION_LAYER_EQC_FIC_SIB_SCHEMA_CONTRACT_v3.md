# GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_GIT_INTEGRATION_LAYER
component_name: Git Integration Layer
roadmap_layer: 14
roadmap_phase: Phase C — Source Control Governance
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Command Acceptance Criteria
conditional_standards: Promotion / Release Gate Acceptance Criteria, Human Approval Acceptance Criteria
optional_standards: ES, Report Template
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/git/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/git/
contract_document_rating: 10/10
basis_pattern:
  - Security Sandbox / Filesystem Boundary Layer contracts
  - Policy / Capability Registry contracts
  - Governed Patch Execution contracts
  - Tool / MCP Adapter contracts
related_layers:
  - Security Sandbox / Filesystem Boundary Layer
  - Policy / Capability Registry
  - Governed Patch Execution Layer
  - Failure Taxonomy / Recovery Playbook
  - Tool / MCP Adapter Layer
  - Human Review / Approval Interface
  - Promotion / Release Gate
```

---

# 0. v3 Review and Upgrade Summary

The v2 contract was strong and close to final, but I would rate it:

```text
9.7/10
```

It already covered the required Git Integration Layer contract areas:

```text
EQC
FIC
SIB
Schema Contract
Git Operation Schema
Git Command Policy Schema
Git Status / Diff Schema
Git Mutation Request Schema
Git Commit Evidence Schema
Git Audit / Evidence Contract
Role Permission Matrix
Branch / Commit / Push Safety Rules
OpenCode borrowing notes
Agent_X integration notes
allowed and blocked Git operations
role permissions
human approval and governance requirements
Git allowlisting
branch, commit, push, rollback, and revert rules
integration with patch execution and promotion
Git hook, pager, external diff, locking, and idempotency controls
```

It was not fully 10/10 because a few implementation-critical controls were still under-specified:

```text
1. It did not define exact implementation files for the Git Integration package.
2. It listed public result classes but did not require a dedicated git_operation_result.schema.json.
3. It did not require schemas for Git lock records, ref validation records, and command execution results.
4. It did not fully isolate Git from global/system/user config, HOME, XDG config, credential helpers, GPG signing, and local include files.
5. It said hooks must not run by default, but did not specify the combined hook controls needed for commit commands.
6. It did not fully define safe command templates for read-only, stage, commit, branch, revert, and push operations.
7. It did not fully define ref validation for detached HEAD, symbolic refs, hash-like targets, tags, remotes, and protected namespaces.
8. It did not specify repository state snapshot hashes strongly enough for before/after mutation checks.
9. It did not make dependency-degraded behavior explicit when Policy, Sandbox, Patch Execution, Human Approval, or Promotion Gate are unavailable.
10. It did not require negative tests for Git config isolation, credential prompts, GPG signing, and hook-path isolation.
```

This v3 adds those details and is the final 10/10 controlling contract for the Git Integration Layer.

---

# 1. Purpose

This document defines the controlling safety contract for the **Git Integration Layer** in Agent_X.

The Git Integration Layer controls how Agent_X may inspect, stage, commit, branch, revert, and eventually push repository changes.

This layer must prevent Agent_X from using Git as a bypass around:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution Layer
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter Layer
Human Review / Approval Interface
Promotion / Release Gate
audit/evidence requirements
source mutation controls
```

The layer must answer:

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

This layer is safety-critical because Git is the boundary between generated or reviewed changes and durable repository history.

---

# 2. Scope

## 2.1 Required in This Layer

The Git Integration Layer must define contracts for:

```text
Git operation model
Git command policy
Git command allowlist
Git command execution environment
Git status / diff result model
Git mutation request model
Git branch request model
Git stage request model
Git commit evidence model
Git push request model
Git revert request model
Git audit / evidence model
Git evidence manifest
Git review report
Git completion record
Git role permission matrix
read-only Git inspection
branch creation controls
stage controls
commit controls
push controls
revert/rollback controls
command allowlisting
source mutation evidence
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Security Sandbox
integration with Governed Patch Execution
integration with Promotion / Release Gate
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
patch generation
LLM code generation
self-evolution planning
promotion approval policy
human approval UI
remote provider configuration
repository hosting administration
release packaging
deployment
background Git daemon
unrestricted Git shell
raw shell executor
full release automation
```

The Git Integration Layer executes or blocks Git operations according to policy. It does not decide project strategy, generate patches, approve releases, or override safety authorities.

---

# 3. Standards Applied

## 3.1 Primary Standard — EQC

```text
EQC
```

EQC is primary because Git operations can permanently change repository state, rewrite history, publish code remotely, or destroy local work.

The layer must fail closed for:

```text
unknown Git commands
unapproved mutation requests
unapproved staging
unapproved commits
unapproved branch creation
unapproved push
history rewrite commands
working-tree destructive commands
policy-unavailable states
sandbox-unavailable states
missing evidence states
missing approval states
missing promotion states
unsafe Git config states
unsafe hook states
unsafe external diff/pager states
```

## 3.2 Required Standard — FIC

```text
FIC
```

FIC is required because this layer will have concrete implementation files, each with explicit responsibilities.

Expected file responsibilities include:

```text
Git models
Git operation policy
Git command allowlist
Git status/diff readers
Git mutation gate
Git evidence writer
Git rollback/revert controls
Git integration dispatcher
Git command environment hardening
Git schema validation
```

Each file must have:

```text
clear public API
clear inputs and outputs
no side effects on import
fail-closed behavior
unit tests
schema-backed evidence
bounded output
secret redaction
```

## 3.3 Required Standard — SIB

```text
SIB
```

SIB is required because Git Integration connects multiple Agent_X layers:

```text
Tool / MCP Adapter calls Git tools
Policy / Capability Registry authorizes Git operations
Security Sandbox verifies repository/path boundaries
Governed Patch Execution produces approved mutation evidence
Failure Taxonomy classifies Git failures
Human Review approves high-risk operations
Promotion / Release Gate controls push/release behavior
```

The Git Integration Layer is an integration boundary, not a standalone Git helper.

## 3.4 Required Standard — Schema Contract

```text
Schema Contract
```

All Git requests, decisions, results, and evidence must be structured and schema-valid.

Required schemas:

```text
git_operation.schema.json
git_command_policy.schema.json
git_command_result.schema.json
git_status_diff_result.schema.json
git_operation_result.schema.json
git_mutation_request.schema.json
git_branch_request.schema.json
git_ref_validation_result.schema.json
git_stage_request.schema.json
git_commit_evidence.schema.json
git_push_request.schema.json
git_revert_request.schema.json
git_lock_record.schema.json
git_audit_event.schema.json
git_evidence_manifest.schema.json
git_review_report.schema.json
git_completion_record.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every Git operation attempt must create evidence, including blocked and invalid attempts.

Evidence is required for:

```text
read-only Git status
read-only Git diff
branch inspection
log inspection
stage request
commit request
push request
revert request
blocked Git command
invalid Git command
policy-denied Git operation
sandbox-denied Git operation
human-approval-required operation
governance-required operation
promotion-required operation
command execution failure
schema validation failure
secret scan failure
external diff/pager/hook block
```

## 3.6 Required Command Acceptance Criteria

Git commands must never be executed through raw shell text.

All Git command execution must use:

```text
argument-vector command construction
explicit allowlist
fixed command templates
timeouts
bounded output
secret redaction
evidence logging
policy decision reference
sandbox decision reference where applicable
safe environment variables
safe cwd
no shell=True
no command string parsing
```

---

# 4. Canonical Implementation Surface

## 4.1 Required Package Files

Expected location:

```text
tools/agentx_evolve/git/
```

Expected files:

```text
tools/agentx_evolve/git/__init__.py
tools/agentx_evolve/git/git_models.py
tools/agentx_evolve/git/git_command_policy.py
tools/agentx_evolve/git/git_command_runner.py
tools/agentx_evolve/git/git_environment.py
tools/agentx_evolve/git/git_ref_validator.py
tools/agentx_evolve/git/git_status.py
tools/agentx_evolve/git/git_diff.py
tools/agentx_evolve/git/git_mutation_gate.py
tools/agentx_evolve/git/git_stage.py
tools/agentx_evolve/git/git_commit.py
tools/agentx_evolve/git/git_branch.py
tools/agentx_evolve/git/git_revert.py
tools/agentx_evolve/git/git_push.py
tools/agentx_evolve/git/git_locks.py
tools/agentx_evolve/git/git_evidence.py
tools/agentx_evolve/git/git_dispatcher.py
```

## 4.2 File Responsibility Rules

```text
__init__.py must expose the public API only and perform no Git operation on import.
git_models.py must define dataclasses/constants only.
git_command_policy.py must define allowlisted operation templates and blocked operations.
git_command_runner.py must execute only argument-vector commands approved by policy.
git_environment.py must build the hardened Git environment and isolated config context.
git_ref_validator.py must validate branches, refs, tags, remotes, and protected namespaces.
git_status.py and git_diff.py must provide read-only operations only.
git_mutation_gate.py must verify policy, sandbox, patch, approval, promotion, state snapshots, and idempotency.
git_stage.py must stage only explicit approved paths.
git_commit.py must commit only approved staged changes and must not invoke editor, GPG, or hooks.
git_branch.py must create only approved non-protected branches.
git_revert.py must prepare revert plans and block actual revert unless approved.
git_push.py must block by default and require Promotion Gate approval when enabled.
git_locks.py must serialize mutation operations.
git_evidence.py must write append-only evidence, latest artifacts, manifests, hashes, and completion records.
git_dispatcher.py must enforce the full operation pipeline before any helper runs.
```

## 4.3 Required Schema Files

Expected location:

```text
tools/agentx_evolve/schemas/
```

Required schemas:

```text
git_operation.schema.json
git_command_policy.schema.json
git_command_result.schema.json
git_status_diff_result.schema.json
git_operation_result.schema.json
git_mutation_request.schema.json
git_branch_request.schema.json
git_ref_validation_result.schema.json
git_stage_request.schema.json
git_commit_evidence.schema.json
git_push_request.schema.json
git_revert_request.schema.json
git_lock_record.schema.json
git_audit_event.schema.json
git_evidence_manifest.schema.json
git_review_report.schema.json
git_completion_record.schema.json
```

## 4.4 Required Test Files

Expected location:

```text
tools/agentx_evolve/tests/
```

Required test files:

```text
test_git_command_policy.py
test_git_command_runner.py
test_git_environment.py
test_git_ref_validator.py
test_git_status.py
test_git_diff.py
test_git_mutation_gate.py
test_git_stage.py
test_git_commit.py
test_git_branch.py
test_git_revert.py
test_git_push.py
test_git_locks.py
test_git_evidence.py
test_git_dispatcher.py
test_git_negative_cases.py
test_git_schema_validation.py
validate_git_integration_schemas.py
```

---

# 5. Dependency Gates and Restricted Mode

The Git Integration Layer may be implemented before all later authorities are fully active, but unavailable dependencies must reduce capability, not increase it.

## 5.1 Dependency Gate Rules

```text
If Policy / Capability Registry is unavailable -> read-only known-role inspection may use restrictive fallback; all mutation blocks.
If Security Sandbox is unavailable -> all repo/path/command operations block, including read-only Git.
If Governed Patch Execution is unavailable -> stage and commit operations block.
If Human Review is unavailable -> operations requiring human approval block.
If Promotion / Release Gate is unavailable -> push, release tag, and protected-branch update block.
If Failure Taxonomy is unavailable -> use UNKNOWN_GIT_FAILURE while still blocking unsafe behavior.
If evidence writing is unavailable -> all Git operations block except pure schema validation tests.
```

## 5.2 Restricted Mode

Restricted mode may allow only:

```text
load Git command policy
validate Git operation schemas
validate refs without mutation
read current branch / HEAD / status / bounded diff after sandbox approval
write evidence for allowed read-only operations
return structured BLOCKED results for mutation operations
```

Restricted mode must block:

```text
staging
committing
branch creation
tag creation
revert execution
push
remote modification
history rewrite
submodule mutation
worktree mutation
interactive prompts
credential prompts
```


# 6. Risk Model

Git Integration is critical because unsafe Git access can:

```text
commit unapproved generated code
push unreviewed changes
rewrite repository history
delete working-tree files
stage unrelated files
include secrets in commits
bypass patch review
bypass promotion gates
hide evidence of source mutation
publish unsafe code remotely
run local Git hooks unexpectedly
invoke external diff drivers or pagers
leak remote credentials
mutate the Git index during read-only inspection
```

The safe default is:

```text
read-only inspection allowed only for approved roles
mutation blocked unless all authorities approve
push blocked by default
history rewrite commands permanently blocked in v1
external hooks, pagers, and external diff helpers disabled by default
```

---

# 5. Authority Rule

Git Integration does not grant permission by itself.

A Git operation is allowed only when all required authorities agree:

```text
Git Command Policy
Policy / Capability Registry
Security Sandbox, when repo, files, paths, or commands are involved
Governed Patch Execution, when staged/committed changes came from patches
Human Review, when required
Promotion / Release Gate, when push/release behavior is requested
Failure Taxonomy, for failure classification
Audit/Evidence system, for durable proof
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
NEEDS_PROMOTION_GATE
DRY_RUN_ONLY
ALLOW
```

No Git mutation may proceed if policy, sandbox, patch evidence, stage evidence, commit evidence, approval, promotion, or evidence writing is missing.

---

# 6. Git Operation Classification

## 6.1 Allowed by Default, Read-Only

These operations may be allowed for approved read roles:

```text
git status --short
git status --porcelain=v1
git diff --name-only --no-ext-diff -- <approved paths>
git diff --stat --no-ext-diff -- <approved paths>
git diff --no-ext-diff -- <approved paths>, bounded and redacted
git branch --show-current
git log --oneline -n <bounded number>
git rev-parse --show-toplevel
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git ls-files -- <approved paths>
```

Rules:

```text
bounded output required
no shell expansion
no unbounded history dump
no path outside repository root
no source mutation
no index mutation
all results evidenced
external diff disabled
pager disabled
optional Git locks disabled for read-only commands
```

## 6.2 Blocked by Default, Mutating

These operations must block unless explicitly approved by all required authorities:

```text
git add <explicit approved paths>
git commit
git branch <new-branch>
git checkout -b <new-branch>
git switch -c <new-branch>
git revert <commit>
git restore <explicit approved paths>
git checkout -- <explicit approved paths>
git tag <approved tag>
git push <approved remote> <approved refspec>
```

## 6.3 Permanently Blocked in v1

These operations are not allowed in v1:

```text
git reset --hard
git reset --mixed
git reset --soft
git clean -fdx
git clean -ffdx
git rebase
git merge
git push --force
git push --force-with-lease
git branch -D
git branch -d protected branch
git tag -d
git remote add
git remote remove
git remote set-url
git config --global
git config --system
git filter-branch
git reflog expire
git gc --aggressive
git update-ref
git symbolic-ref mutation
git worktree add/remove
git submodule update with network
```

## 6.4 Conditional Future Operations

These may become available only in later phases with explicit contracts:

```text
approved merge
approved release tag
approved push
approved revert
approved branch creation
approved commit signing
remote synchronization
submodule update
worktree management
```

---

# 7. Role Permission Matrix

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
MCP_CLIENT
UNKNOWN_CALLER
```

## 7.1 Role Rules

| Role | Inspect Status/Diff | Stage | Commit | Branch Create | Revert | Push |
|---|---|---|---|---|---|---|
| `ORCHESTRATOR` | Yes, policy-checked | Request only | Request only | Request only | Request only | No |
| `IMPLEMENTATION_WORKER` | Yes, limited | No direct staging | No | No | No | No |
| `VALIDATION_REPAIR_WORKER` | Yes, limited | No direct staging | No | No | No | No |
| `REVIEWER_ASSISTANT` | Yes, read-only | No | No | No | No | No |
| `PROMOTION_CHECKER` | Yes | Only with approved evidence | Only with approval | Only with approval | Only with approval | Promotion-gated only |
| `HUMAN_OPERATOR` | Yes | May approve, not bypass | May approve, not bypass | May approve, not bypass | May approve, not bypass | May approve, not bypass |
| `MCP_CLIENT` | Read-only minimum | No | No | No | No | No |
| `UNKNOWN_CALLER` | No | No | No | No | No | No |

## 7.2 Non-Override Rule

Human approval cannot override:

```text
sandbox denial
policy hard block
forbidden Git command
missing patch evidence
missing stage evidence
missing commit evidence
missing promotion gate for push
secret detection failure
invalid schema
unsafe Git hook/config state
unsafe external diff/pager state
```

---

# 8. Git Command Allowlist Contract

All Git commands must be represented as structured operations, not raw command strings.

A Git command policy entry must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_command_policy.schema.json",
  "operation_name": "git_status_short",
  "command": "git",
  "fixed_args": ["status", "--short"],
  "allowed_dynamic_args": [],
  "allowed_roles": ["ORCHESTRATOR", "REVIEWER_ASSISTANT", "PROMOTION_CHECKER"],
  "effect": "READ",
  "requires_policy": true,
  "requires_sandbox": true,
  "requires_patch_evidence": false,
  "requires_stage_evidence": false,
  "requires_commit_evidence": false,
  "requires_human_approval": false,
  "requires_governance": false,
  "requires_promotion_gate": false,
  "mutates_repository": false,
  "writes_index": false,
  "writes_history": false,
  "uses_remote": false,
  "allows_hooks": false,
  "allows_external_diff": false,
  "allows_pager": false,
  "enabled": true,
  "warnings": [],
  "errors": []
}
```

Allowlist rules:

```text
command must be git
args must be generated from fixed templates
all pathspecs must follow `--`
no shell=True
no command string parsing
no shell metacharacters
no unbounded dynamic args
no remote operations unless explicitly approved
no destructive operations in v1
no Git aliases
no external diff drivers
no pager
no credential helper invocation
no hook execution unless explicitly approved by a later hook policy
```

---

# 9. Git Command Execution Environment

Every Git command must run in a hardened environment.

Required execution controls:

```text
cwd must be the approved repo root
repo root must match sandbox-approved repository boundary
command must be an argument vector
shell must be false
stdout/stderr must be bounded
timeout must be enforced
stdin must be closed or controlled
interactive prompts must be disabled
network prompts must be disabled
credential prompts must be disabled
```

Required environment defaults:

```text
GIT_TERMINAL_PROMPT=0
GIT_ASKPASS=
SSH_ASKPASS=
GIT_PAGER=cat
PAGER=cat
GIT_EXTERNAL_DIFF=
GIT_OPTIONAL_LOCKS=0 for read-only operations
GIT_CONFIG_NOSYSTEM=1
HOME=<controlled temporary empty home>
XDG_CONFIG_HOME=<controlled temporary empty config dir>
LC_ALL=C
```

Required command-level config isolation:

```text
-c core.pager=cat
-c color.ui=false
-c core.quotepath=false
-c commit.gpgsign=false
-c tag.gpgSign=false
-c log.showSignature=false
-c core.hooksPath=<controlled empty hooks directory for commands that could trigger hooks>
-c credential.helper=
-c safe.directory=<approved repo root only when needed>
```

Rules for Git config:

```text
system and user Git config must not affect command behavior.
repository-local config must not enable hooks, external diff, pager, credential prompts, signing, or network behavior.
include.path and includeIf config behavior must not introduce unapproved command behavior.
if config isolation cannot be proven, all mutating operations block.
```

Required Git flags where applicable:

```text
--no-pager
--no-ext-diff for diff operations
--no-textconv for diff operations unless explicitly allowed
--porcelain=v1 for parseable status
--no-optional-locks or GIT_OPTIONAL_LOCKS=0 for read-only operations
--no-verify for commit only as an additional hook bypass, not as a substitute for hooksPath isolation
--no-gpg-sign for commit operations
-- before pathspecs
```

Rules:

```text
read-only operations must not write index or source files
mutating operations must not run hooks unless a future hook policy explicitly allows them
commit operations must not rely on editor invocation
commit messages must be supplied from approved evidence, not from an interactive editor
```

---

# 10. Safe Git Command Templates

Only fixed templates may be used. Dynamic values must be validated before insertion.

## 10.1 Read-Only Templates

```text
git --no-pager status --porcelain=v1
git --no-pager status --short
git --no-pager diff --no-ext-diff --no-textconv --stat -- <validated paths>
git --no-pager diff --no-ext-diff --no-textconv --name-only -- <validated paths>
git --no-pager diff --no-ext-diff --no-textconv -- <validated paths>
git --no-pager branch --show-current
git --no-pager rev-parse --show-toplevel
git --no-pager rev-parse --abbrev-ref HEAD
git --no-pager rev-parse HEAD
git --no-pager log --oneline -n <bounded integer>
git --no-pager ls-files -- <validated paths>
```

## 10.2 Mutating Templates, Disabled Unless Fully Approved

```text
git add -- <explicit approved paths>
git commit --no-gpg-sign --no-verify -m <approved message>
git branch <validated new branch> <validated base commit>
git switch -c <validated new branch> <validated base commit>
git revert --no-edit <validated commit>
git push <allowlisted remote> <allowlisted source_ref>:<allowlisted target_ref>
```

Rules:

```text
Templates do not imply permission. They may be used only after policy, sandbox, evidence, approval, and gate checks pass.
No template may accept raw user-supplied command fragments.
No template may accept shell syntax, glob expansion, command substitution, pipes, redirects, semicolons, or environment assignment.
Every dynamic argument must have a validation evidence ID.
```

---

# 11. Git Operation Schema

Every Git operation request must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_operation.schema.json",
  "operation_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "caller_role": "ORCHESTRATOR",
  "caller_id": "string|null",
  "session_id": "string|null",
  "operation_name": "git_status_short",
  "requested_effect": "READ|STAGE|COMMIT|BRANCH|REVERT|PUSH",
  "repo_root": "string",
  "paths": [],
  "arguments": {},
  "dry_run": true,
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "patch_session_id": "string|null",
  "patch_evidence_id": "string|null",
  "stage_evidence_id": "string|null",
  "commit_evidence_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "promotion_gate_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
operation_id is required
operation_name is required
caller_role is required
requested_effect is required
repo_root is required
arguments must be an object
paths must be an array
unknown caller_role blocks
unknown requested_effect blocks
mutation requests require dry_run=false only after approval
```

---

# 11. Git Command Result Schema

Every executed or blocked Git command must produce a structured command result.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_command_result.schema.json",
  "command_result_id": "string",
  "operation_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "operation_name": "git_status_short",
  "command_template_id": "string",
  "argv_redacted": [],
  "argv_sha256": "string",
  "cwd": "string",
  "environment_profile_id": "string",
  "exit_code": 0,
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "stdout_summary": "string",
  "stderr_summary": "string",
  "stdout_truncated": false,
  "stderr_truncated": false,
  "duration_ms": 0,
  "timeout_seconds": 30,
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
argv_redacted must not contain secrets, credentials, or unbounded path data.
argv_sha256 must hash the exact pre-redaction argument vector where safe, or a canonical redacted vector when unsafe.
stdout/stderr must be bounded and redacted before persistence.
exit_code must be recorded for every command that reaches execution.
blocked commands must still create a command result with status BLOCKED and an appropriate failure_class.
```

---

# 12. Git Status / Diff Schema

Read-only Git results must be structured.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_status_diff_result.schema.json",
  "result_id": "string",
  "operation_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "operation_name": "git_status_short",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "repo_root": "string",
  "current_branch": "string|null",
  "head_commit": "string|null",
  "changed_files": [],
  "diff_summary": {},
  "bounded_output": "string",
  "output_truncated": false,
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
raw diff output must be bounded
large diffs must be summarized
secrets must be redacted before evidence
read-only result must not mutate repository state or index
external diff must be disabled
pager must be disabled
```

---

# 13. Git Operation Result Schema

Every Git operation, including dry-run, blocked, invalid, and failed operations, must produce a structured operation result.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_operation_result.schema.json",
  "operation_result_id": "string",
  "operation_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "operation_name": "git_commit_approved",
  "requested_effect": "READ|STAGE|COMMIT|BRANCH|REVERT|PUSH",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "repo_root": "string",
  "pre_state_snapshot_id": "string|null",
  "post_state_snapshot_id": "string|null",
  "command_result_ids": [],
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
Every public Git API must return GitOperationResult or a more specific schema-compatible result.
BLOCKED, FAILED, and INVALID results must include failure_class.
Mutating results must include pre and post state snapshot references.
Schema-invalid results must not replace valid latest artifacts.
```

---

# 14. Git Mutation Request Schema

Any stage, commit, branch, revert, or push operation must use a mutation request.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_mutation_request.schema.json",
  "mutation_request_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "operation_name": "git_commit_approved",
  "requested_effect": "STAGE|COMMIT|BRANCH|REVERT|PUSH",
  "repo_root": "string",
  "target_branch": "string|null",
  "base_commit": "string|null",
  "target_commit": "string|null",
  "paths": [],
  "patch_session_id": "string|null",
  "patch_evidence_id": "string|null",
  "stage_evidence_id": "string|null",
  "commit_evidence_id": "string|null",
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "promotion_gate_id": "string|null",
  "commit_message": "string|null",
  "dry_run": true,
  "idempotency_key": "string|null",
  "warnings": [],
  "errors": []
}
```

Mutation request rules:

```text
stage requires approved patch evidence
commit requires approved stage evidence
branch creation requires policy and governance
revert requires governance and human approval
push requires promotion gate
paths must be sandbox-approved
commit message must be generated from evidence or human-approved text
mutation must be dry-run until all approvals are present
idempotency key must be recorded for repeated mutation requests
```

---

# 13. Branch Request Schema

Branch creation must use a structured branch request.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_branch_request.schema.json",
  "branch_request_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "base_branch": "string",
  "base_commit": "string",
  "new_branch": "string",
  "policy_decision_id": "string",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "dry_run": true,
  "warnings": [],
  "errors": []
}
```

Branch request rules:

```text
new branch must pass strict ref validation
base branch and base commit must be recorded
protected branch names cannot be overwritten
remote-tracking branch mutation is blocked in v1
branch creation is dry-run until approved
```

---

# 15. Git Ref Validation Result Schema

Every branch, tag, remote ref, or refspec used by a Git mutation must be validated and evidenced.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_ref_validation_result.schema.json",
  "ref_validation_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "ref_kind": "BRANCH|TAG|REMOTE|REFSPEC|COMMIT",
  "raw_ref": "string",
  "normalized_ref": "string|null",
  "is_valid": false,
  "is_protected": false,
  "is_remote_tracking": false,
  "is_symbolic": false,
  "is_detached_head": false,
  "check_ref_format_status": "PASS|FAIL|NOT_RUN",
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Ref validation must reject:

```text
HEAD as a mutation target
detached HEAD as a branch base unless explicitly read-only
@{-1} and other checkout shorthand
refs containing `..`, `@{`, ASCII control characters, or `.lock` suffixes
refs beginning with `-`
refs ending with `/`, `.`, or `.lock`
refs containing consecutive slashes
remote-tracking refs as local mutation targets
refs/tags/* mutation in v1
refs/remotes/* mutation in v1
protected branch and release namespaces unless Promotion Gate explicitly approves
hash-like strings used as branch names
```

---

# 16. Stage Request Schema

Staging must use a structured stage request.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_stage_request.schema.json",
  "stage_request_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "base_commit": "string",
  "paths": [],
  "patch_session_id": "string",
  "patch_evidence_id": "string",
  "approved_path_set_hash": "string",
  "policy_decision_id": "string",
  "sandbox_decision_id": "string",
  "dry_run": true,
  "warnings": [],
  "errors": []
}
```

Stage request rules:

```text
paths must be explicit
paths must match approved patch evidence
path set hash must match evidence
`git add .`, `git add -A`, and path globs are forbidden
stage request must record pre-stage status and post-stage status
```

---

# 15. Git Commit Evidence Schema

Every approved commit attempt must create commit evidence.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_commit_evidence.schema.json",
  "commit_evidence_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "branch_name": "string",
  "base_commit": "string",
  "new_commit": "string|null",
  "operation_id": "string",
  "mutation_request_id": "string",
  "stage_evidence_id": "string",
  "patch_session_id": "string|null",
  "patch_evidence_id": "string|null",
  "staged_paths": [],
  "staged_path_set_hash": "string",
  "diff_stat": {},
  "commit_message": "string",
  "policy_decision_id": "string",
  "sandbox_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "promotion_gate_id": "string|null",
  "secret_scan_status": "PASS|BLOCKED|NOT_AVAILABLE",
  "status": "SUCCESS|BLOCKED|FAILED|INVALID",
  "artifact_refs": [],
  "evidence_refs": [],
  "sha256_refs": [],
  "warnings": [],
  "errors": []
}
```

Commit evidence rules:

```text
base commit must be recorded before mutation
new commit must be recorded after successful commit
staged paths must be explicit
unrelated files must not be staged
commit message must be evidenced
secret scan status must be recorded if available
commit evidence must be written before push can be considered
commit must not invoke editor
commit hook execution is blocked unless future hook policy explicitly allows it
```

---

# 16. Push Request Schema

Push must use a structured push request.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_push_request.schema.json",
  "push_request_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "remote_name": "string",
  "remote_url_redacted": "string|null",
  "source_ref": "string",
  "target_ref": "string",
  "commit_evidence_id": "string",
  "review_report_id": "string|null",
  "completion_record_id": "string|null",
  "policy_decision_id": "string",
  "promotion_gate_id": "string",
  "human_approval_id": "string|null",
  "dry_run": true,
  "warnings": [],
  "errors": []
}
```

Push request rules:

```text
push is blocked by default
remote must be allowlisted
refspec must be allowlisted
force flags are forbidden
credential prompts are disabled
promotion gate is required
commit evidence is required
```

---

# 17. Revert Request Schema

Revert must use a structured revert request.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_revert_request.schema.json",
  "revert_request_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "current_branch": "string",
  "head_commit": "string",
  "target_commit": "string",
  "revert_plan_id": "string|null",
  "policy_decision_id": "string",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "dry_run": true,
  "warnings": [],
  "errors": []
}
```

Revert request rules:

```text
revert is dry-run by default
reset-based rollback is forbidden
history rewrite rollback is forbidden
working tree must be clean or controlled
post-revert status must be evidenced
```

---

# 19. Git Lock Record Schema

Every mutation lock acquisition, denial, timeout, and release must be evidenced.

```json
{
  "schema_version": "1.0",
  "schema_id": "git_lock_record.schema.json",
  "lock_record_id": "string",
  "timestamp": "string",
  "source_component": "GitIntegrationLayer",
  "repo_root": "string",
  "lock_path": ".agentx-init/git/locks/git_mutation.lock",
  "operation_id": "string",
  "mutation_request_id": "string|null",
  "lock_status": "ACQUIRED|RELEASED|BLOCKED|TIMEOUT|STALE_REJECTED",
  "holder_id": "string|null",
  "timeout_seconds": 30,
  "pre_head_commit": "string|null",
  "pre_index_hash": "string|null",
  "pre_worktree_hash": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
A mutation may not run without an ACQUIRED lock record.
A stale lock may not be removed unless the owning process/session is proven inactive and repo state is unchanged.
Lock release must be evidenced even when the operation fails.
A failed lock release is a HIGH issue and may be a BLOCKER if the repo state is uncertain.
```

---

# 20. Git Audit / Evidence Contract

Runtime artifacts must be written under:

```text
.agentx-init/git/
```

Required artifacts:

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

Rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
SHA-256 hashes for final evidence artifacts
no raw secrets in evidence
no unbounded command output in evidence
blocked Git operations are evidence events
invalid Git operations are evidence events
schema-invalid results must not replace valid latest artifacts
no hidden or duplicate artifact filenames
```

## 18.1 Evidence Manifest

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
  "final_decision": "DONE|NOT_DONE"
}
```

## 18.2 Evidence Immutability Rule

After a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 19. Branch Safety Rules

Branch creation is blocked by default unless all are true:

```text
caller role is authorized
policy allows branch creation
governance decision exists
branch name passes validation
branch name does not overwrite protected branch
base branch is recorded
base commit is recorded
working tree state is recorded
operation is evidenced
```

Protected branches and refs include:

```text
main
master
release
production
stable
refs/heads/main
refs/heads/master
refs/heads/release/*
refs/tags/*
refs/remotes/*
```

Branch names must reject:

```text
empty names
names with shell metacharacters
names beginning with dash
names containing whitespace-only segments
names targeting protected branch overwrite
names containing path traversal patterns
names failing `git check-ref-format --branch`
remote-tracking ref names
```

---

# 20. Stage Safety Rules

Staging is blocked by default unless all are true:

```text
patch session is approved
patch evidence exists
paths are explicitly listed
paths are sandbox-approved
paths belong to approved mutation set
path set hash matches patch evidence
policy allows staging
working-tree status is recorded before staging
diff stat is recorded before staging
operation is evidenced
Git mutation lock is acquired
```

Staging must never use:

```text
git add .
git add -A
git add --all
unbounded path globs
implicit working-tree staging
pathspecs without `--`
```

Only explicit approved paths may be staged.

---

# 21. Commit Safety Rules

Commit is blocked by default unless all are true:

```text
approved staging evidence exists
staged paths match approved patch evidence
base commit is recorded
current HEAD still equals expected base commit or approved staged-state commit
policy allows commit
governance decision exists if required
human approval exists if required
commit message is validated
secret scan status is recorded if available
diff stat is recorded
commit evidence is created
Git mutation lock is acquired
```

Commit must not proceed if:

```text
staged files include unrelated paths
working tree has unexpected untracked files that affect the commit
commit message is empty
commit message contains secret-like material
policy decision is missing
approval evidence is missing
HEAD changed since approval
staged diff changed since approval
Git hooks would run without an approved hook policy
```

---

# 22. Push Safety Rules

Push is blocked by default.

Push may be considered only when all are true:

```text
Promotion / Release Gate approves push
policy allows push
human approval exists if required
commit evidence exists
review report exists
completion record exists
branch target is allowed
remote target is allowlisted
refspec is allowlisted
no force flag is used
credential prompts are disabled
operation is evidenced
Git mutation lock is acquired
```

Push must always block for:

```text
UNKNOWN_CALLER
MCP_CLIENT
IMPLEMENTATION_WORKER
unreviewed commit
missing promotion gate
missing commit evidence
unallowlisted remote
force push
protected branch direct push without explicit release approval
credential prompt requirement
```

---

# 23. Rollback / Revert Rules

Rollback and revert must be treated as mutating operations.

Allowed safe behavior in v1:

```text
inspect recent commits
inspect current branch
inspect diff/stat
prepare revert plan in dry-run
block actual revert unless approved
```

Actual revert requires:

```text
policy approval
governance approval
human approval, if required
known target commit
clean or controlled working tree
revert evidence
post-revert status evidence
Git mutation lock
```

Blocked in v1:

```text
git reset --hard
git clean -fdx
history rewrite rollback
force push rollback
unreviewed revert
```

---

# 24. Concurrency and Locking Rules

Git mutation operations must be serialized.

Required lock behavior:

```text
stage, commit, branch creation, revert, tag, and push require a Git mutation lock
read-only operations may run concurrently only if they do not write index or source state
lock file must live under .agentx-init/git/locks/
lock acquisition must be evidenced
stale lock handling must be explicit and safe
lock timeout must be bounded
```

Blocking conditions:

```text
mutation lock unavailable
stale lock cannot be verified safely
another mutation is in progress
working tree changed since approval
HEAD changed since approval
```

---

# 25. Idempotency Rules

Repeated Git mutation requests must be safe.

Rules:

```text
mutation requests must include idempotency_key where applicable
same request with same evidence should not create duplicate commits
if requested commit already exists with same evidence, return SUCCESS/PARTIAL with existing commit evidence
if HEAD changed since original request, block and require revalidation
if staged state changed since original request, block and require revalidation
push retry must verify remote state before execution
```

---

# 26. Repository State Snapshot Rules

Before and after every mutating Git operation, the layer must record a canonical repository state snapshot.

Required snapshot fields:

```text
state_snapshot_id
timestamp
repo_root
current_branch
head_commit
index_hash
worktree_status_hash
staged_diff_hash
unstaged_diff_hash
untracked_file_summary_hash
approved_path_set_hash
policy_decision_id
sandbox_decision_id
lock_record_id
```

Rules:

```text
state must be captured before lock-sensitive mutation begins
HEAD must match the approved base commit before staging or commit
staged_diff_hash must match the approved stage evidence before commit
post-state must be captured after mutation or after failure cleanup
if pre/post state cannot be captured, mutation blocks or reports FAILED with evidence
state snapshot hashes must be included in commit evidence and completion evidence where relevant
```

---

# 27. Repository Boundary Rules

Git Integration must respect repository boundaries.

Rules:

```text
repo root must be approved by Security Sandbox
nested repositories are blocked unless explicitly approved
submodule mutation is blocked in v1
worktree mutation is blocked in v1
symlink traversal outside approved root is blocked
paths must be normalized and verified before command construction
all pathspecs must be explicit and passed after `--`
```

---

# 27. Integration with Tool / MCP Adapter Layer

The Tool / MCP Adapter may expose Git Integration through controlled tools only.

Allowed read-only tool mapping:

```text
git_status -> Git Integration status operation
git_diff -> Git Integration diff operation
git_diff_name_only -> Git Integration diff name-only operation
git_diff_stat -> Git Integration diff stat operation
git_branch_current -> Git Integration branch inspection
git_log_recent -> Git Integration bounded log inspection
```

Mutating tool mapping:

```text
git_stage_approved -> blocked unless approved mutation request exists
git_commit_approved -> blocked unless commit requirements pass
git_create_branch_approved -> blocked unless governance/policy pass
git_revert_approved -> blocked unless revert requirements pass
git_push_approved -> blocked unless promotion gate passes
```

MCP exposure rule:

```text
MCP_CLIENT may receive read-only Git inspection only.
MCP_CLIENT must not stage, commit, branch, revert, push, merge, rebase, reset, clean, tag, or modify remotes.
```

---

# 28. Integration with Policy / Capability Registry

Policy must decide:

```text
caller role allowed?
Git operation allowed?
requested effect allowed?
path set allowed?
branch target allowed?
remote target allowed?
human approval required?
governance required?
promotion gate required?
dry-run required?
```

If Policy / Capability Registry is unavailable:

```text
read-only operations may use restrictive local fallback for known read roles
all mutation operations block
all push operations block
all remote operations block
unknown roles block
```

Policy-denied Git operations must return:

```text
status = BLOCKED
failure_class = GIT_POLICY_DENIED
```

---

# 29. Integration with Security Sandbox

Security Sandbox must verify:

```text
repo root is approved
paths are inside approved repository boundary
stage paths are approved
patch files are approved
no path traversal exists
no protected path is touched
commands are allowlisted
subprocess execution is permitted
symlink targets stay inside approved boundary
nested repository and submodule behavior is approved or blocked
```

Sandbox-denied Git operations must return:

```text
status = BLOCKED
failure_class = GIT_SANDBOX_DENIED
```

No Git mutation may proceed if sandbox is unavailable or denies the operation.

---

# 30. Integration with Governed Patch Execution

Git Integration must not commit arbitrary working-tree changes.

Stage/commit must be linked to Governed Patch Execution evidence:

```text
patch_session_id
patch_evidence_id
approved changed paths
approved path set hash
diff stat
validation result
review result
rollback plan
```

Rules:

```text
patch evidence must precede staging
staging evidence must precede commit
commit evidence must precede push
unrelated files must not be staged or committed
patch_apply and Git commit must remain separate authorities
```

---

# 31. Integration with Promotion / Release Gate

Push and release-like operations require Promotion / Release Gate approval.

Promotion gate must verify:

```text
validated commit
review report
completion record
accepted risk state
no blockers
target branch allowed
remote allowed
human approval, if required
```

Without promotion gate approval:

```text
git_push_approved -> BLOCKED / GIT_PROMOTION_REQUIRED
release tag -> BLOCKED / GIT_PROMOTION_REQUIRED
protected branch update -> BLOCKED / GIT_PROMOTION_REQUIRED
```

---

# 32. OpenCode Borrowing Notes

## 32.1 Concepts to Borrow

Borrow these OpenCode-style concepts:

```text
explicit tool-specific Git operations
read-only status/diff tools
separate mutation tools
command allowlisting
output truncation
human-question gating for risky operations
structured tool results
invalid-tool handling
```

## 32.2 Concepts to Restrict

Do not borrow:

```text
broad shell access
model-driven arbitrary Git command selection
unrestricted plugin Git tools
implicit file staging
unreviewed commits
network/remote operations by convenience
force push behavior
history rewrite behavior
external tool execution by default
```

## 32.3 Agent_X Mapping

| OpenCode-style concept | Agent_X Git equivalent | Required control |
|---|---|---|
| shell Git status | `git_status` | allowlisted read-only command |
| shell Git diff | `git_diff` | bounded output, no external diff, redaction |
| shell Git add | `git_stage_approved` | patch evidence + sandbox + policy |
| shell Git commit | `git_commit_approved` | staging evidence + governance/human approval |
| shell Git push | `git_push_approved` | promotion gate + remote allowlist |
| shell Git branch | `git_create_branch_approved` | branch validation + governance |
| shell Git reset | blocked | v1 permanent block |
| shell Git clean | blocked | v1 permanent block |
| shell Git rebase | blocked | v1 permanent block |

---

# 33. Failure Classes

The Git Integration Layer must use standardized failure classes.

Required Git failure classes:

```text
GIT_OPERATION_INVALID
GIT_COMMAND_NOT_ALLOWLISTED
GIT_POLICY_DENIED
GIT_SANDBOX_DENIED
GIT_GOVERNANCE_REQUIRED
GIT_HUMAN_APPROVAL_REQUIRED
GIT_PROMOTION_REQUIRED
GIT_PATCH_EVIDENCE_REQUIRED
GIT_STAGE_EVIDENCE_REQUIRED
GIT_COMMIT_EVIDENCE_REQUIRED
GIT_BRANCH_PROTECTED
GIT_REMOTE_NOT_ALLOWLISTED
GIT_DESTRUCTIVE_COMMAND_BLOCKED
GIT_HISTORY_REWRITE_BLOCKED
GIT_SECRET_SCAN_BLOCKED
GIT_HOOK_BLOCKED
GIT_EXTERNAL_DIFF_BLOCKED
GIT_PAGER_BLOCKED
GIT_LOCK_UNAVAILABLE
GIT_IDEMPOTENCY_CONFLICT
GIT_REPO_BOUNDARY_DENIED
GIT_EXECUTION_FAILED
GIT_TIMEOUT
GIT_RESULT_SCHEMA_INVALID
UNKNOWN_GIT_FAILURE
```

Failure rules:

```text
every BLOCKED result must include failure_class
every FAILED result must include failure_class
unknown failures map to UNKNOWN_GIT_FAILURE
policy denials map to GIT_POLICY_DENIED
sandbox denials map to GIT_SANDBOX_DENIED
destructive commands map to GIT_DESTRUCTIVE_COMMAND_BLOCKED
history rewrite commands map to GIT_HISTORY_REWRITE_BLOCKED
unsafe hook execution maps to GIT_HOOK_BLOCKED
```

---

# 34. Public API Contract

Expected public classes:

```text
GitOperation
GitCommandPolicy
GitOperationResult
GitStatusDiffResult
GitMutationRequest
GitBranchRequest
GitStageRequest
GitCommitEvidence
GitPushRequest
GitRevertRequest
GitAuditEvent
GitEvidenceManifest
```

Expected public functions:

```python
load_git_command_policy() -> dict

check_git_operation_allowed(
    operation: GitOperation,
    command_policy: dict,
    policy_context: dict,
) -> dict

run_git_status(
    operation: GitOperation,
    repo_root: str,
) -> GitOperationResult

run_git_diff(
    operation: GitOperation,
    repo_root: str,
) -> GitStatusDiffResult

prepare_git_mutation_request(
    operation: GitOperation,
    context: dict,
) -> GitMutationRequest

stage_approved_paths(
    mutation_request: GitMutationRequest,
    context: dict,
) -> GitOperationResult

commit_approved_changes(
    mutation_request: GitMutationRequest,
    context: dict,
) -> GitOperationResult

create_approved_branch(
    mutation_request: GitMutationRequest,
    context: dict,
) -> GitOperationResult

revert_approved_commit(
    mutation_request: GitMutationRequest,
    context: dict,
) -> GitOperationResult

push_approved_commit(
    mutation_request: GitMutationRequest,
    context: dict,
) -> GitOperationResult

write_git_evidence(
    operation: GitOperation,
    result: GitOperationResult,
    repo_root: str,
) -> dict
```

---

# 35. Execution Pipeline

Every Git operation must follow this sequence:

```text
1. Receive raw Git operation request.
2. Normalize caller context.
3. Build GitOperation object.
4. Validate GitOperation schema.
5. Resolve and validate repo root through Security Sandbox.
6. Load Git command policy.
7. Verify operation exists in allowlist.
8. Check caller role.
9. Check requested effect.
10. Check Policy / Capability Registry.
11. Check Security Sandbox for repo/path/command boundary.
12. Check patch evidence for stage/commit operations.
13. Check stage evidence for commit operations.
14. Check commit evidence for push operations.
15. Check governance for branch/commit/revert where required.
16. Check human approval where required.
17. Check promotion gate for push/release operations.
18. Acquire Git mutation lock for mutating operations.
19. Recheck HEAD, branch, staged state, and working tree if mutating.
20. Build argument-vector Git command.
21. Build hardened Git execution environment.
22. Execute only if allowed and not dry-run.
23. Bound stdout/stderr.
24. Redact secrets.
25. Validate result schema.
26. Write Git operation evidence.
27. Write latest Git result atomically.
28. Release Git mutation lock.
29. Return schema-valid result.
```

No Git wrapper may skip this pipeline unless the operation is a unit test of an internal helper.

---

# 36. Dry-Run Semantics

Every mutating Git operation must support dry-run.

Dry-run must:

```text
validate schema
check command allowlist
check policy
check sandbox
check patch evidence
check stage evidence where applicable
check approval requirements
show what would execute
write dry-run evidence
avoid Git mutation
avoid staging
avoid commit
avoid branch creation
avoid revert
avoid push
```

Dry-run result must include:

```text
dry_run = true
would_execute = true|false
required_authorities
missing_authorities
expected_command_template
expected_artifacts
```

---

# 37. Secret and Sensitive Output Rules

Before durable logging, redact:

```text
API keys
tokens
passwords
private keys
environment values
provider credentials
remote URLs with credentials
commit output containing secrets
raw diff lines containing likely secrets
```

Rules:

```text
raw full diffs should not be persisted by default
large outputs must be summarized
secret-like diff content blocks commit unless explicitly reviewed and approved
secret redaction failures block Git mutation
```

---

# 38. Schema Example and Validation Requirements

Each schema must have at least one valid example and one invalid example in tests.

Required examples:

```text
valid_git_operation_read
valid_git_command_policy_read
valid_git_status_diff_success
valid_git_mutation_request_stage
valid_git_branch_request
valid_git_stage_request
valid_git_commit_evidence_blocked
valid_git_push_request_blocked
valid_git_revert_request_dry_run
valid_git_audit_event
valid_git_evidence_manifest
valid_git_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
forbidden operation value fails
missing evidence ID fails for mutation schemas
```

---

# 39. Preconditions for Implementation

Implementation must not begin unless these are defined:

```text
Git operation schema
Git command policy schema
Git status/diff schema
Git mutation request schema
Git branch request schema
Git stage request schema
Git commit evidence schema
Git push request schema
Git revert request schema
Git audit/evidence schema
role permission matrix
read-only Git allowlist
blocked Git command list
branch safety rules
stage safety rules
commit safety rules
push safety rules
rollback/revert rules
Git command environment hardening
Policy integration boundary
Sandbox integration boundary
Patch Execution integration boundary
Promotion Gate integration boundary
```

---

# 40. Test Acceptance Criteria

Required tests:

```text
test_git_command_policy_loads
test_git_status_allowed_for_reviewer
test_git_diff_allowed_for_reviewer
test_unknown_git_operation_blocks
test_unknown_caller_blocks
test_git_add_blocks_without_patch_evidence
test_git_commit_blocks_without_stage_evidence
test_git_push_blocks_without_promotion_gate
test_git_force_push_always_blocks
test_git_reset_hard_blocks
test_git_clean_fdx_blocks
test_git_rebase_blocks
test_branch_creation_requires_governance
test_protected_branch_overwrite_blocks
test_stage_requires_explicit_paths
test_commit_requires_evidence
test_commit_blocks_when_head_changed_since_approval
test_push_requires_commit_evidence
test_mutating_operation_dry_run_no_mutation
test_git_output_is_bounded
test_git_secret_like_output_redacted_or_blocked
test_external_diff_is_disabled
test_pager_is_disabled
test_hooks_do_not_run_by_default
test_git_optional_locks_disabled_for_read_only
test_git_config_isolation_blocks_global_and_user_config
test_git_credential_prompts_disabled
test_git_gpg_signing_disabled_for_commit
test_git_hooks_path_is_isolated
test_git_no_textconv_for_diff
test_git_ref_validation_blocks_detached_head_mutation
test_git_ref_validation_blocks_tag_and_remote_mutation
test_git_state_snapshot_required_before_mutation
test_git_mutation_lock_required
test_git_idempotency_prevents_duplicate_commit
test_nested_repo_blocks_by_default
test_submodule_mutation_blocks_by_default
test_git_evidence_written
test_git_latest_result_written_atomically
test_git_evidence_manifest_written_with_hashes
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
read-only Git tests PASS
blocked Git mutation tests PASS
evidence tests PASS
source mutation tests PASS
push-block tests PASS
hook/external-diff/pager safety tests PASS
lock/idempotency tests PASS
```

---

# 41. No-Go Conditions

The Git Integration Layer is NOT DONE if any are true:

```text
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
Git operation evidence is missing
evidence hashes are missing
secrets are logged unredacted
unbounded diff output is persisted
external diff runs by default
pager runs by default
Git hook runs by default
read-only Git operation mutates index/source state
source mutation occurs outside approved Git operation pipeline
```

---

# 42. Definition of Done

The Git Integration Layer is done when it proves:

```text
Git command policy exists
Git operation schemas exist
Git status/diff schemas exist
Git mutation request schema exists
Git branch/stage/push/revert schemas exist
Git commit evidence schema exists
Git audit/evidence schema exists
role permissions are enforced
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
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 43. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] command allowlist exists
[ ] read-only Git operations pass
[ ] mutation operations block without approvals
[ ] destructive commands block
[ ] branch rules pass
[ ] commit evidence rules pass
[ ] push gate rules pass
[ ] hook/external-diff/pager rules pass
[ ] lock/idempotency rules pass
[ ] audit/evidence artifacts are written
[ ] evidence manifest and hashes exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] source mutation check passes
[ ] completion record exists
```

---

# 44. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_GIT_INTEGRATION_LAYER"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  git_operations_verified: []
  blocked_git_operations_verified: []
  branch_rules_verified: []
  commit_rules_verified: []
  push_rules_verified: []
  rollback_revert_rules_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  patch_execution_integration_verified: []
  promotion_gate_integration_verified: []
  environment_hardening_verified: []
  lock_idempotency_verified: []
  evidence_artifacts: []
  evidence_hashes: []
  deviations_from_contract: []
  unresolved_risks: []
  final_decision: "DONE|NOT_DONE"
```

---

# 45. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded.

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
BLOCKER items cannot be accepted as deviations
missing evidence hashes cannot be accepted as a deviation for DONE
raw shell cannot be accepted as a deviation
Git destructive commands cannot be accepted as a deviation in v1
push without promotion gate cannot be accepted as a deviation
```

---

# 46. Residual Risks

```yaml
residual_risks:
  - id: "GIT-RISK-001"
    description: "Git mutation could stage unrelated files."
    severity: "critical"
    mitigation: "Only explicit sandbox-approved paths from patch evidence may be staged."
  - id: "GIT-RISK-002"
    description: "Push could publish unreviewed generated code."
    severity: "critical"
    mitigation: "Push is blocked by default and requires Promotion / Release Gate approval."
  - id: "GIT-RISK-003"
    description: "History rewrite could destroy evidence."
    severity: "critical"
    mitigation: "reset, rebase, clean, and force-push are blocked in v1."
  - id: "GIT-RISK-004"
    description: "Diff output could leak secrets into durable evidence."
    severity: "high"
    mitigation: "Bound, summarize, redact, and block secret-like outputs where required."
  - id: "GIT-RISK-005"
    description: "Git Integration could bypass Patch Execution."
    severity: "critical"
    mitigation: "Stage and commit require patch/session evidence."
  - id: "GIT-RISK-006"
    description: "Git hooks, external diff, or pagers could execute unexpected local code."
    severity: "critical"
    mitigation: "Disable hooks, external diff, and pagers by default; test this explicitly."
  - id: "GIT-RISK-007"
    description: "Read-only Git operations could mutate the index."
    severity: "medium"
    mitigation: "Use read-only command modes and GIT_OPTIONAL_LOCKS=0 where applicable."
```

---

# 47. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Git Integration Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed Git mutation policy, changed push policy, changed role permissions, changed default safety behavior, new required Git operation category
```

Blocked without major revision:

```text
allowing push by default
allowing Git write for MCP_CLIENT
allowing raw shell
allowing git add .
allowing git reset --hard
allowing git clean -fdx
allowing git rebase by default
allowing force push
removing patch evidence requirement for staging
removing stage evidence requirement for commit
removing promotion gate requirement for push
removing audit/evidence logging
allowing hooks/external diff/pagers by default
removing evidence hashes
```

The next document should be:

```text
GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC
```

---

# 48. Final Rating

This v3 contract document is rated:

```text
10/10
```

Reason:

```text
It defines the Git Integration Layer using EQC, FIC, SIB, Schema Contract, exact package/file boundaries, Git operation schemas, command policy, command-result and operation-result schemas, hardened Git configuration isolation, safe command templates, status/diff structures, mutation request controls, branch/ref validation, stage/commit/push/revert schemas, lock records, state snapshots, commit evidence, audit/evidence rules, evidence hashing, role permissions, branch/commit/push safety, rollback/revert handling, locking, idempotency, repository boundary controls, OpenCode borrowing boundaries, Agent_X integration points, no-go conditions, negative test requirements, and a precise Definition of Done.
```
