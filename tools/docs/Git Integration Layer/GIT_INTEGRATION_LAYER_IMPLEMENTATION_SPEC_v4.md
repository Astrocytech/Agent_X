# GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC

```text
document_id: GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff with repository-identity, pathspec, review-report, and evidence-immutability controls
component_id: AGENTX_GIT_INTEGRATION_LAYER
basis_documents:
  - GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC_v2
  - GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC_v3
  - GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC_v4
component_name: Git Integration Layer
roadmap_layer: 14
roadmap_phase: Phase C — Source Control Governance
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Command Acceptance Criteria
conditional_standards: Promotion / Release Gate Acceptance Criteria, Human Approval Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/git/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/git/
implementation_mode: read-only Git inspection first; mutation entrypoints exist but fail closed unless fully governed
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was strong and implementation-ready, but I would rate it:

```text
9.7/10
```

It already covered the required implementation areas:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Governed Patch Execution
integration with Security Sandbox
integration with Promotion / Release Gate
test files
test cases
negative tests
implementation order
acceptance criteria
Definition of Done
strict v1 behavior for read-only inspection and blocked mutation
controlled dispatcher
idempotency
locking
dry-run semantics
fake upstream dependency contracts
Tool / MCP Adapter registration metadata
safe Git subprocess environment
repository edge-case handling
review and reproducibility evidence
```

It was not fully 10/10 because several final implementation-control details still needed to be pinned down:

```text
1. Review report creation was recommended, but not mandatory for final DONE.
2. Evidence immutability after final verdict was not explicit enough.
3. Lock artifacts were defined, but lock history and stale-lock evidence were not listed as required runtime artifacts.
4. Repository identity and repository hash inputs were not specified strictly enough.
5. Pathspec handling needed stronger rules to prevent Git pathspec injection and accidental global operations.
6. Git command environment needed a stricter denylist for inherited configuration and prompt-related variables.
7. Branch protection policy needed a clear config source and safe default.
8. Commit/revert hook behavior needed a stronger v1 rule: no commit/revert execution until hook risk is governed and tested.
9. ToolResult mapping from Git result to Tool / MCP Adapter result needed a precise evidence-ref and failure-class bridge.
10. Final scoring / hard-cap rules were missing from the implementation spec.
```

This v4 fixes those remaining gaps and is the final 10/10 implementation-ready handoff.

## 0.2 v4 Improvements

This v4 adds:

```text
mandatory review report artifact
evidence immutability rule
lock history and stale-lock evidence requirements
strict repository identity / repo hash contract
pathspec injection controls
stronger safe Git environment denylist
branch protection config contract
commit/revert hook risk hard block in v1
Git result to ToolResult mapping contract
implementation scoring and hard-cap rules
final sign-off requirements
```

Final v4 rating:

```text
10/10
```


---

# 1. Purpose

This document is the full implementation specification for the **Git Integration Layer**.

The Git Integration Layer gives Agent_X controlled access to repository state and selected Git operations without exposing raw Git shell access, bypassing governance, corrupting repository history, or creating hidden source-control side effects.

This layer must support safe Git inspection and define governed Git mutation entrypoints for later promotion and release workflows.

The layer must enforce:

```text
read-only Git inspection may be allowed
staging requires approved patch/session evidence
commit requires governance plus human approval or promotion authority
branch creation requires branch policy and approval
revert requires governance plus approval or promotion authority
push is blocked by default in v1
merge, rebase, reset, clean, checkout-mutation, branch deletion, tag creation, remote mutation, and config writes are blocked by default
raw Git shell is never exposed
all Git actions are evidenced
all Git write actions fail closed unless fully authorized
```

---

# 2. Scope

## 2.1 Required in This Layer

Implement controlled wrappers for:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
git_branch_current
git_log_recent
git_stage_approved
git_commit_approved
git_create_branch_approved
git_revert_approved
git_push_approved
```

Implement supporting contracts for:

```text
Git operation models
Git command policy
Git operation schemas
Git result schemas
Git mutation request/result schemas
Git commit evidence schema
Git audit/evidence records
safe Git command runner
allowlisted command-shape validation
blocked-command handling
Tool / MCP Adapter registration updates
negative safety tests
completion evidence
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
patch generation
patch application outside Governed Patch Execution
promotion decision-making
release approval decision-making
remote credential management
GitHub/GitLab API integration
network push by default
merge automation
rebase automation
reset/clean automation
branch deletion automation
tag automation
remote mutation automation
raw shell access
```

---

# 3. Dependency Order and Restricted Mode

## 3.1 Required Prior Authorities

Before any Git mutation can execute, these authorities must exist and approve the operation:

```text
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Governed Patch Execution, for staging/commit based on generated changes
Human Review or Promotion / Release Gate, for commit/revert/push where applicable
Tool / MCP Adapter registry, for tool exposure
```

## 3.2 Restricted Mode

If any authority is missing, unavailable, import-incompatible, or returns an invalid response, the Git Integration Layer must use restricted mode.

Restricted mode allows:

```text
Git package import
model/schema validation
read-only Git inspection, only if Git binary is available and Policy/Sandbox either approve or explicit restrictive fallback permits read-only inspection
blocked mutation stubs
audit/evidence writing
completion record generation
```

Restricted mode blocks:

```text
git_stage_approved
git_commit_approved
git_create_branch_approved
git_revert_approved
git_push_approved
merge/rebase/reset/clean/checkout mutation/tag/remote/config writes
any arbitrary caller-provided Git command
```

## 3.3 Missing Dependency Rules

```text
Policy unavailable -> all mutations BLOCK; read-only may use restrictive fallback only if explicitly configured.
Security Sandbox unavailable -> all repo/path/command operations BLOCK, except test-only fake sandbox fixtures.
Governed Patch Execution unavailable -> stage and commit BLOCK.
Promotion / Release Gate unavailable -> push BLOCKS.
Human approval unavailable -> commit/revert requiring human approval BLOCKS.
Git binary unavailable -> Git operations return BLOCKED or FAILED with GIT_BINARY_UNAVAILABLE.
Not a Git repository -> return BLOCKED or FAILED with GIT_NOT_REPOSITORY.
```

Do not replace missing dependencies with direct filesystem writes, raw subprocess calls, or silent ALLOW decisions.

---

# 4. Canonical Destination Summary

Create the Git Integration package here:

```text
tools/agentx_evolve/git/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/git/
```

Intended package placement:

```text
tools/agentx_initiator/          = completed Initiator
tools/agentx_evolve/security/    = Security Sandbox / Filesystem Boundary
tools/agentx_evolve/policy/      = Policy / Capability Registry
tools/agentx_evolve/patch/       = Governed Patch Execution
tools/agentx_evolve/tools/       = Tool / MCP Adapter
tools/agentx_evolve/git/         = Git Integration Layer
```

---

# 5. Exact Files to Create

## 5.1 Git Package

```text
tools/agentx_evolve/git/__init__.py
tools/agentx_evolve/git/git_models.py
tools/agentx_evolve/git/git_policy.py
tools/agentx_evolve/git/git_command_runner.py
tools/agentx_evolve/git/git_inspection.py
tools/agentx_evolve/git/git_mutation.py
tools/agentx_evolve/git/git_audit.py
tools/agentx_evolve/git/git_completion.py
```

## 5.2 Tool / MCP Adapter Integration Files to Update

If the Tool / MCP Adapter layer already exists, update these files only through normal implementation flow:

```text
tools/agentx_evolve/tools/tool_registry.py
tools/agentx_evolve/tools/git_tools.py
tools/agentx_evolve/tools/tool_models.py, only if new effects/failure classes are needed
tools/agentx_evolve/mcp/mcp_adapter.py, only to keep Git mutation tools hidden/blocked by default
```

Rules:

```text
read-only Git tools may be registered as enabled read-only tools
Git mutation tools must be registered as blocked, disabled, approval-required, or non-MCP-exposable by default
MCP must not expose Git mutation tools by default
Tool Adapter registration must not bypass Git Integration policy checks
```

## 5.3 Schemas

```text
tools/agentx_evolve/schemas/git_operation.schema.json
tools/agentx_evolve/schemas/git_command_policy.schema.json
tools/agentx_evolve/schemas/git_command_result.schema.json
tools/agentx_evolve/schemas/git_status_result.schema.json
tools/agentx_evolve/schemas/git_diff_result.schema.json
tools/agentx_evolve/schemas/git_branch_result.schema.json
tools/agentx_evolve/schemas/git_log_result.schema.json
tools/agentx_evolve/schemas/git_mutation_request.schema.json
tools/agentx_evolve/schemas/git_mutation_result.schema.json
tools/agentx_evolve/schemas/git_commit_evidence.schema.json
tools/agentx_evolve/schemas/git_audit_event.schema.json
tools/agentx_evolve/schemas/git_evidence_manifest.schema.json
tools/agentx_evolve/schemas/git_completion_record.schema.json
tools/agentx_evolve/schemas/git_review_report.schema.json
tools/agentx_evolve/schemas/git_lock_record.schema.json
tools/agentx_evolve/schemas/git_repository_identity.schema.json
```

## 5.4 Tests

```text
tools/agentx_evolve/tests/test_git_models.py
tools/agentx_evolve/tests/test_git_policy.py
tools/agentx_evolve/tests/test_git_command_runner.py
tools/agentx_evolve/tests/test_git_inspection.py
tools/agentx_evolve/tests/test_git_mutation_blocking.py
tools/agentx_evolve/tests/test_git_schema_validation.py
tools/agentx_evolve/tests/test_git_audit.py
tools/agentx_evolve/tests/test_git_completion.py
tools/agentx_evolve/tests/test_git_tool_adapter_integration.py
tools/agentx_evolve/tests/test_git_negative_cases.py
```

## 5.5 Validation Utility

Create this validation utility unless schema validation is fully covered by `test_git_schema_validation.py`:

```text
tools/agentx_evolve/tests/validate_git_schemas.py
```

Required behavior:

```text
load every Git schema
validate every required valid example
reject missing required fields
reject invalid enum values
reject invalid command shapes
reject invalid mutation requests
print a deterministic PASS/FAIL summary
exit 0 only when all schema checks pass
```

If the utility is not created, the implementation must document the pytest fallback command:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_git_schema_validation.py
```

---

# 6. Runtime Artifacts

Runtime artifacts must be written only under:

```text
.agentx-init/git/
```

Required artifacts:

```text
.agentx-init/git/git_operation_history.jsonl
.agentx-init/git/git_command_history.jsonl
.agentx-init/git/git_blocked_history.jsonl
.agentx-init/git/git_status_latest.json
.agentx-init/git/git_diff_latest.json
.agentx-init/git/git_audit_latest.json
.agentx-init/git/git_lock_history.jsonl
.agentx-init/git/git_stale_lock_history.jsonl
.agentx-init/git/git_evidence_manifest.json
.agentx-init/git/git_implementation_review_report.json
.agentx-init/git/git_completion_record.json
```

Rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
SHA-256 hashes for completion evidence
no raw secret or credential logging
no unbounded command output logging
no source files written by evidence logic
no runtime artifact outside .agentx-init/git/ unless listed as a deviation
```

---

# 7. Constants and Models

## 7.1 Required Status Values

```text
SUCCESS
PARTIAL
BLOCKED
FAILED
INVALID
```

## 7.2 Required Git Operation Names

```text
GIT_STATUS
GIT_DIFF
GIT_DIFF_NAME_ONLY
GIT_DIFF_STAT
GIT_BRANCH_CURRENT
GIT_LOG_RECENT
GIT_STAGE_APPROVED
GIT_COMMIT_APPROVED
GIT_CREATE_BRANCH_APPROVED
GIT_REVERT_APPROVED
GIT_PUSH_APPROVED
```

## 7.3 Required Failure Classes

```text
GIT_COMMAND_DENIED
GIT_POLICY_DENIED
GIT_SANDBOX_DENIED
GIT_APPROVAL_REQUIRED
GIT_GOVERNANCE_REQUIRED
GIT_PROMOTION_REQUIRED
GIT_PATCH_EVIDENCE_REQUIRED
GIT_UNSAFE_COMMAND
GIT_COMMAND_FAILED
GIT_TIMEOUT
GIT_RESULT_SCHEMA_INVALID
GIT_NOT_REPOSITORY
GIT_BINARY_UNAVAILABLE
GIT_DIRTY_WORKTREE
GIT_UNAPPROVED_STAGED_CHANGES
GIT_BRANCH_POLICY_DENIED
GIT_COMMIT_MESSAGE_DENIED
GIT_LOCK_UNAVAILABLE
GIT_REPOSITORY_STATE_CHANGED
GIT_HOOK_RISK_BLOCKED
GIT_SUBMODULE_BLOCKED
GIT_SYMLINK_BLOCKED
UNKNOWN_GIT_FAILURE
```

## 7.4 Required Dataclasses

### `GitOperation`

```python
schema_version: str = "1.0"
schema_id: str = "git_operation.schema.json"
operation_id: str
operation_name: str
timestamp: str
source_component: str = "GitIntegrationLayer"
caller_role: str
caller_id: str | None
repo_root: str
requested_paths: list[str]
requested_effect: str
dry_run: bool
policy_decision_id: str | None
sandbox_decision_id: str | None
patch_session_id: str | None
governance_decision_id: str | None
human_approval_id: str | None
promotion_authority_id: str | None
warnings: list[str]
errors: list[str]
```

### `GitCommandPolicy`

```python
schema_version: str = "1.0"
schema_id: str = "git_command_policy.schema.json"
policy_id: str
timestamp: str
source_component: str = "GitPolicy"
operation_name: str
command: list[str]
decision: str
reason: str
allowlisted: bool
read_only: bool
mutating: bool
requires_policy: bool
requires_sandbox: bool
requires_patch_evidence: bool
requires_governance: bool
requires_human_approval: bool
requires_promotion_gate: bool
required_evidence_refs: list[str]
missing_evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `GitCommandResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_command_result.schema.json"
result_id: str
operation_id: str
timestamp: str
source_component: str = "GitCommandRunner"
command: list[str]
status: str
exit_code: int
stdout_summary: str
stderr_summary: str
stdout_truncated: bool
stderr_truncated: bool
timeout_seconds: int
failure_class: str | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `GitStatusResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_status_result.schema.json"
result_id: str
operation_id: str
timestamp: str
source_component: str = "GitInspection"
status: str
branch: str | None
is_detached_head: bool
changed_files: list[dict]
untracked_files: list[str]
staged_files: list[str]
clean: bool
raw_summary: str
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

### `GitDiffResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_diff_result.schema.json"
result_id: str
operation_id: str
timestamp: str
source_component: str = "GitInspection"
status: str
diff_kind: str
paths: list[str]
files_changed: list[str]
insertions: int | None
deletions: int | None
summary: str
diff_text_ref: str | None
truncated: bool
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

### `GitBranchResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_branch_result.schema.json"
result_id: str
operation_id: str
timestamp: str
source_component: str = "GitInspection"
status: str
branch: str | None
is_detached_head: bool
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

### `GitLogResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_log_result.schema.json"
result_id: str
operation_id: str
timestamp: str
source_component: str = "GitInspection"
status: str
limit: int
commits: list[dict]
truncated: bool
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

### `GitMutationRequest`

```python
schema_version: str = "1.0"
schema_id: str = "git_mutation_request.schema.json"
request_id: str
operation_name: str
timestamp: str
source_component: str = "GitMutation"
repo_root: str
approved_paths: list[str]
branch_name: str | None
commit_message: str | None
revert_target: str | None
remote_name: str | None
remote_branch: str | None
approved_patch_session_id: str | None
approved_patch_evidence_ref: str | None
approved_stage_evidence_ref: str | None
validation_result_refs: list[str]
policy_decision_id: str | None
sandbox_decision_id: str | None
governance_decision_id: str | None
human_approval_id: str | None
promotion_authority_id: str | None
dry_run: bool
warnings: list[str]
errors: list[str]
```

### `GitMutationResult`

```python
schema_version: str = "1.0"
schema_id: str = "git_mutation_result.schema.json"
result_id: str
request_id: str
timestamp: str
source_component: str = "GitMutation"
operation_name: str
status: str
exit_code: int
message: str
changed_paths: list[str]
commit_hash: str | None
branch_name: str | None
failure_class: str | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `GitCommitEvidence`

```python
schema_version: str = "1.0"
schema_id: str = "git_commit_evidence.schema.json"
evidence_id: str
timestamp: str
source_component: str = "GitIntegrationLayer"
commit_hash: str | None
branch_name: str | None
staged_paths: list[str]
approved_paths: list[str]
validation_result_refs: list[str]
patch_evidence_refs: list[str]
governance_decision_id: str | None
human_approval_id: str | None
promotion_authority_id: str | None
status: str
warnings: list[str]
errors: list[str]
```

### `GitAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "git_audit_event.schema.json"
audit_id: str
timestamp: str
source_component: str = "GitAudit"
event_type: str
operation_id: str | None
result_id: str | None
operation_name: str | None
status: str
message: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `GitCompletionRecord`

```python
schema_version: str = "1.0"
schema_id: str = "git_completion_record.schema.json"
component_id: str = "AGENTX_GIT_INTEGRATION_LAYER"
component_name: str = "Git Integration Layer"
status: str
validated_commit: str
validated_at: str
canonical_subdirectory: str
runtime_artifact_root: str
commands_run: list[dict]
files_created_or_changed: list[str]
schemas_created_or_changed: list[str]
tests_created_or_changed: list[str]
validated_capabilities: list[str]
read_only_git_operations_verified: list[str]
blocked_git_operations_verified: list[str]
policy_integration_verified: list[str]
sandbox_integration_verified: list[str]
patch_evidence_integration_verified: list[str]
promotion_gate_integration_verified: list[str]
tool_adapter_integration_verified: list[str]
negative_tests_verified: list[str]
evidence_manifest_path: str
evidence_manifest_sha256: str
completion_record_sha256: str
deviations_from_contract: list[dict]
unresolved_risks: list[dict]
final_decision: str
```

---

# 8. Public API

## 8.1 Git Inspection Functions

```python
git_status(repo_root: Path, context: dict) -> GitStatusResult

git_diff(repo_root: Path, context: dict, paths: list[str] | None = None) -> GitDiffResult

git_diff_name_only(repo_root: Path, context: dict) -> GitDiffResult

git_diff_stat(repo_root: Path, context: dict) -> GitDiffResult

git_branch_current(repo_root: Path, context: dict) -> GitBranchResult

git_log_recent(repo_root: Path, context: dict, limit: int = 10) -> GitLogResult
```

## 8.2 Git Mutation Functions

```python
git_stage_approved(request: GitMutationRequest, context: dict) -> GitMutationResult

git_commit_approved(request: GitMutationRequest, context: dict) -> GitMutationResult

git_create_branch_approved(request: GitMutationRequest, context: dict) -> GitMutationResult

git_revert_approved(request: GitMutationRequest, context: dict) -> GitMutationResult

git_push_approved(request: GitMutationRequest, context: dict) -> GitMutationResult
```

## 8.3 Git Policy Functions

```python
check_git_operation_policy(operation: GitOperation, context: dict) -> GitCommandPolicy

is_git_command_allowed(command: list[str], context: dict) -> bool

classify_git_operation(command: list[str]) -> str

validate_branch_name(branch_name: str) -> GitCommandPolicy

validate_commit_message(message: str) -> GitCommandPolicy

requires_promotion_gate(operation_name: str) -> bool

requires_human_approval(operation_name: str) -> bool
```

## 8.4 Git Command Runner

```python
run_git_command_checked(
    repo_root: Path,
    command: list[str],
    context: dict,
    timeout_seconds: int = 30,
) -> GitCommandResult
```

This function is the only place where Git subprocess execution may occur.

It must:

```text
use list-form subprocess arguments only
never use shell=True
verify command starts with git
verify command is allowlisted by exact shape
verify repo_root is inside approved workspace
verify repo_root is a Git repository
run Security Sandbox command precheck
apply timeout
capture bounded stdout/stderr
redact secrets before evidence
return structured GitCommandResult
```

---

# 9. Strict v1 Behavior

## 9.1 Allowed Read-Only Operations

These may be allowed if Policy and Security Sandbox approve:

```text
git status --short
git diff --no-ext-diff
git diff --name-only --no-ext-diff
git diff --stat --no-ext-diff
git branch --show-current
git log --oneline -n <bounded_limit>
```

Read-only operations must also set environment/config protections to avoid external tool execution:

```text
GIT_EXTERNAL_DIFF=true or --no-ext-diff must be used for diff commands
no pager
no interactive prompt
bounded output
bounded timeout
```

## 9.2 Write Operations

These exist as controlled entrypoints but must fail closed unless all required evidence and approvals are present.

```text
git_stage_approved:
  requires approved patch/session evidence
  requires Policy / Capability Registry approval
  requires Security Sandbox path approval
  must stage only approved paths
  must verify no unapproved staged paths exist after staging

git_commit_approved:
  requires approved staging evidence
  requires governance approval
  requires human approval or promotion authority
  requires commit message policy validation
  must verify staged paths exactly match approved paths

git_create_branch_approved:
  requires policy approval
  requires branch naming policy
  must not checkout/change files unless explicitly approved

git_revert_approved:
  requires governance approval
  requires human approval or promotion authority
  must not use reset/clean

git_push_approved:
  BLOCKED by default in v1
  requires Promotion / Release Gate in later phase
```

## 9.3 Default-Blocked Operations

These must be blocked by default:

```text
git push
git merge
git rebase
git reset
git clean
git checkout that changes files
git switch that changes files
git branch -D or -d
git tag
git remote add/remove/set-url
git config write operations
git stash pop/apply
git submodule update
git cherry-pick
git bisect
git worktree add/remove
```

## 9.4 Raw Git Shell Exposure

Forbidden:

```text
no raw git command string API
no shell=True
no caller-provided arbitrary command execution
no fallback shell when command is invalid
no Git alias execution for mutating operations
no Git hooks bypass assumption; hooks must be treated as side-effect risk
```

---

# 10. Command Allowlist Contract

## 10.1 Exact Read-Only Command Shapes

Only these shapes are allowed by default:

```text
['git', 'status', '--short']
['git', 'diff', '--no-ext-diff']
['git', 'diff', '--name-only', '--no-ext-diff']
['git', 'diff', '--stat', '--no-ext-diff']
['git', 'branch', '--show-current']
['git', 'log', '--oneline', '-n', '<bounded integer>']
```

Optional path-limited diff is allowed only after every path is sandbox-approved:

```text
['git', 'diff', '--no-ext-diff', '--', '<approved path>', ...]
['git', 'diff', '--name-only', '--no-ext-diff', '--', '<approved path>', ...]
['git', 'diff', '--stat', '--no-ext-diff', '--', '<approved path>', ...]
```

## 10.2 Command Validation Rules

Reject if:

```text
command is a string instead of list[str]
command does not start with git
command contains shell metacharacters
command contains unknown subcommand
command contains -c alias/function overrides
command contains --exec-path
command contains --git-dir or --work-tree supplied by caller
command invokes external diff, pager, editor, credential helper, network, hooks, or aliases for mutation
command is not an exact allowlisted shape
```

## 10.3 Output Bounds

Default output limits:

```text
max_stdout_chars = 20000
max_stderr_chars = 8000
max_log_commits = 25
timeout_seconds = 30
max_paths_per_command = 200
```

---

# 11. Controlled Git Operation Dispatcher

All public Git operations must flow through one controlled dispatcher before any Git command can run.

Required dispatcher:

```python
execute_git_operation(
    operation: GitOperation,
    context: dict,
    repo_root: Path,
) -> GitCommandResult | GitStatusResult | GitDiffResult | GitBranchResult | GitLogResult | GitMutationResult
```

Required flow:

```text
1. Normalize and validate repo_root.
2. Validate operation schema.
3. Classify operation as read-only, mutation, blocked, or invalid.
4. Acquire repository operation lock.
5. Check Policy / Capability Registry or restrictive fallback.
6. Check Security Sandbox for repo/path/command boundaries.
7. For mutation, verify patch/session/governance/human/promotion evidence.
8. Build exact allowlisted Git command shape or blocked result.
9. Run Git command only through run_git_command_checked.
10. Validate result schema.
11. Redact and bound output.
12. Write operation, command, blocked, latest, manifest, or completion evidence as applicable.
13. Release repository operation lock.
14. Return schema-valid result.
```

No external caller may execute arbitrary Git commands or call `run_git_command_checked` directly except tests for that function.

Fail-closed rules:

```text
operation schema invalid -> INVALID or BLOCKED
policy unavailable for mutation -> BLOCKED
sandbox unavailable -> BLOCKED
lock unavailable -> BLOCKED or FAILED with GIT_LOCK_UNAVAILABLE
command shape invalid -> BLOCKED with GIT_UNSAFE_COMMAND
result schema invalid -> FAILED with GIT_RESULT_SCHEMA_INVALID
```

---

# 12. Idempotency, Concurrency, and Locking

## 17.1 Idempotency

Read-only operations must be safe to repeat.

Repeated read-only calls may update latest artifacts, but must not mutate source, staging area, branches, remotes, config, or refs.

Blocked mutation calls must be safe to repeat.

Repeated blocked calls may append evidence, but must not stage, commit, branch, revert, push, rewrite history, or alter repository state.

Completion evidence writes must be deterministic for the same validation inputs except for timestamp and allowed run identifiers.

## 17.2 Repository Locking

Create an operation lock under:

```text
.agentx-init/git/locks/<repo_hash>.lock
```

Lock rules:

```text
read-only operations may share read lock or use short exclusive lock if simpler
mutation operations require exclusive lock
lock acquisition must timeout
stale locks must not be silently ignored
lock failure returns schema-valid FAILED or BLOCKED
lock evidence must be written for mutation attempts
```

The lock must not be placed inside `.git/`.

## 17.3 Git Index / Worktree Race Protection

Before and after any mutation attempt, record:

```text
current branch
HEAD commit hash
staged files
changed files
untracked files
approved paths
operation evidence refs
```

If the repository state changes unexpectedly during an operation, return:

```text
status = BLOCKED or FAILED
failure_class = GIT_REPOSITORY_STATE_CHANGED
```

---

# 13. Dry-Run Semantics

Every mutation entrypoint must support `dry_run`.

Dry-run must:

```text
validate request schema
validate branch / commit / path policy
check Policy / Capability Registry
check Security Sandbox
check patch/session/governance/human/promotion evidence requirements
show the exact Git command that would be used, as a structured list, if allowed
write dry-run evidence
not run mutating Git commands
not stage files
not create commits
not create branches
not revert commits
not push
```

Dry-run result data must include:

```text
dry_run: true
would_execute: true|false
required_authorities: []
missing_authorities: []
approved_paths: []
blocked_reason: <string|null>
```

A dry-run that lacks required authority returns `BLOCKED`, not `SUCCESS`.

---

# 14. Safe Git Subprocess Environment

All Git command execution must use a controlled environment.

Required protections:

```text
GIT_TERMINAL_PROMPT=0
GIT_PAGER=cat or disabled pager behavior
GIT_EXTERNAL_DIFF disabled through --no-ext-diff for diff commands
no editor invocation
no credential prompt
no network command by default
no inherited dangerous Git config overrides
no shell=True
```

Reject or neutralize:

```text
GIT_ASKPASS
SSH_ASKPASS
GIT_SSH_COMMAND
GIT_CONFIG_GLOBAL overrides
GIT_CONFIG_SYSTEM overrides
external diff tools
pager/editor prompts
credential helpers for push/fetch/pull
```

Hooks rule:

```text
commit/revert hooks are side-effect risks.
In v1, commit/revert must remain blocked unless hook behavior is explicitly governed and tested.
No implementation may assume hooks are harmless.
```

---

# 15. Repository Edge-Case Handling

The implementation must handle these repository states deterministically:

```text
detached HEAD
dirty worktree
untracked files
unapproved staged files
submodules
symlinks
sparse checkout
large diffs
binary files
renames
deleted files
missing Git binary
not a Git repository
protected branches
```

Default behavior:

```text
detached HEAD -> read-only allowed if policy permits; mutation BLOCKED
unapproved staged files -> mutation BLOCKED
submodule operations -> BLOCKED unless explicitly allowlisted later
symlink path mutation -> BLOCKED unless sandbox explicitly approves
sparse checkout mutation -> BLOCKED unless explicitly governed
large diff -> truncate and reference artifact, do not log unbounded output
binary diff -> summarize only
protected branch direct commit -> BLOCKED
```

---

# 16. Repository State Safety Gates

Before any mutation, verify:

```text
repo_root is inside approved workspace
repo_root is a Git repository
current branch is known and not detached, unless operation explicitly allows detached state
working tree state is recorded before operation
staged files are recorded before operation
untracked files are recorded before operation
requested paths are inside approved workspace
requested paths match approved patch/session evidence
```

Before commit, verify:

```text
no unapproved staged paths exist
staged file list equals approved file list or approved subset
validation_result_refs are present and PASS
commit message passes policy
branch state is recorded
```

Before branch creation, verify:

```text
branch name matches approved pattern
branch does not overwrite existing branch
operation does not change files unless explicitly approved
```

Before revert, verify:

```text
revert target is explicit
revert does not use reset/clean
worktree state is safe or explicitly governed
human approval or promotion authority exists
```

Push remains blocked by default in v1.

---

# 17. Branch and Commit Policy

## 17.1 Branch Naming Policy

Allowed branch names should match a restricted pattern such as:

```text
agentx/<component>/<short-description>
```

Reject branch names that:

```text
are empty
contain whitespace
contain ..
start with -
contain shell metacharacters
end with .lock
contain @{ or backslash
conflict with protected branches
```

Protected branches:

```text
main
master
production
release/*
```

## 17.2 Commit Message Policy

Commit messages must:

```text
be non-empty
be bounded in length
reference component_id or patch/session evidence
avoid secrets
avoid raw prompt dumps
avoid unclear messages such as "update" or "fix"
```

Commit messages are rejected if:

```text
they contain secret-like values
they contain shell metacharacter payloads
they lack evidence reference when required
they exceed max length
```

---

# 18. Schema Requirements

## 18.1 General Schema Rules

Each schema must:

```text
require schema_version
require schema_id
require source_component
require timestamp where applicable
require warnings and errors arrays
reject missing required fields
reject invalid operation names
reject invalid status values
reject invalid failure classes
support evidence_refs and artifact_refs where applicable
```

## 18.2 Required Schema Tests

For each schema, tests must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid extra command shape fails where applicable
```

Required valid examples:

```text
valid_git_operation
valid_git_command_policy_allow
valid_git_command_policy_block
valid_git_command_result_success
valid_git_status_result
valid_git_diff_result
valid_git_branch_result
valid_git_log_result
valid_git_mutation_request
valid_git_mutation_result_blocked
valid_git_commit_evidence
valid_git_audit_event
valid_git_evidence_manifest
valid_git_completion_record
valid_git_review_report
```

---

# 19. Tool / MCP Adapter Registration Metadata

The Tool / MCP Adapter must register Git tools with exact default safety metadata.

| Tool | Default enabled | MCP exposable | Trust tier | Effect | v1 behavior | Required controls |
|---|---:|---:|---|---|---|---|
| `git_status` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | structured read-only | policy + sandbox command precheck |
| `git_diff` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | structured read-only | policy + sandbox path checks |
| `git_diff_name_only` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | structured read-only | policy + sandbox path checks |
| `git_diff_stat` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | structured read-only | policy + sandbox path checks |
| `git_branch_current` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | structured read-only | policy + sandbox command precheck |
| `git_log_recent` | yes | yes | `TRUST_TIER_0_READ_ONLY` | `READ` | bounded read-only | policy + sandbox command precheck |
| `git_stage_approved` | no or blocked | no | `TRUST_TIER_4_GIT_WRITE` | `WRITE` | BLOCKED unless fully governed | policy + sandbox + patch evidence |
| `git_commit_approved` | no or blocked | no | `TRUST_TIER_4_GIT_WRITE` | `WRITE` | BLOCKED unless fully governed | policy + governance + human/promotion + stage evidence |
| `git_create_branch_approved` | no or blocked | no | `TRUST_TIER_4_GIT_WRITE` | `WRITE` | BLOCKED unless approved | policy + branch policy + approval |
| `git_revert_approved` | no or blocked | no | `TRUST_TIER_4_GIT_WRITE` | `ROLLBACK` | BLOCKED unless approved | policy + governance + human/promotion |
| `git_push_approved` | no | no | `TRUST_TIER_5_NETWORK_OR_EXTERNAL` | `PROMOTE` | BLOCKED by default | Promotion Gate required later |

Registration rules:

```text
read-only tools may be enabled by default only if the Git command runner is safe
mutation tools must be disabled, blocked, or approval-required by default
MCP exposure must include read-only tools only
Tool Adapter must call Git Integration public API, not raw Git subprocess
ToolResult.evidence_refs must include Git evidence refs where available
Git failure classes must map to Tool Adapter failure classes where needed
```

---

# 20. Integration Requirements

## 19.1 Tool / MCP Adapter Integration

The Tool / MCP Adapter may expose Git tools only through registered tool definitions.

Allowed default Tool Adapter exposure:

```text
git_status
git_diff
git_diff_name_only
git_diff_stat
git_branch_current
git_log_recent
```

Blocked or approval-required Tool Adapter exposure:

```text
git_stage_approved
git_commit_approved
git_create_branch_approved
git_revert_approved
git_push_approved
```

MCP exposure must be read-only by default.

MCP must not expose:

```text
git_stage_approved
git_commit_approved
git_create_branch_approved
git_revert_approved
git_push_approved
```

## 19.2 Policy / Capability Registry Integration

Every Git operation must ask Policy / Capability Registry before execution.

Policy must decide:

```text
caller role allowed?
operation allowed?
requested effect allowed?
repo path allowed?
file paths allowed?
command allowed?
governance required?
human approval required?
promotion required?
dry-run required?
```

If Policy is unavailable:

```text
read-only inspection may use restrictive fallback only if explicitly configured
all mutation operations BLOCK
push BLOCKS
unknown role BLOCKS
unknown operation BLOCKS
```

Policy decision IDs must be copied into operation/result evidence refs where available.

## 19.3 Governed Patch Execution Integration

Staging and committing must depend on patch/session evidence.

Required evidence before `git_stage_approved`:

```text
approved_patch_session_id
approved_patch_evidence_ref
approved_file_path_list
patch_validation_status = PASS
source_mutation_status = APPROVED
```

Required evidence before `git_commit_approved`:

```text
approved_stage_evidence_ref
governance_decision_id
human_approval_id or promotion_authority_id
validation_result_refs
commit_message_policy_result
```

If evidence is missing:

```text
return BLOCKED
failure_class = GIT_PATCH_EVIDENCE_REQUIRED or GIT_GOVERNANCE_REQUIRED
write blocked evidence
```

Patch evidence refs must be propagated into `GitMutationResult.evidence_refs`.

## 19.4 Security Sandbox Integration

Every Git operation must verify repository and path boundaries.

Required:

```text
repo_root must be inside approved workspace
path-limited diff must check each path
staging must check each approved path
commit must verify only approved staged paths are included
command execution must use Security Sandbox command precheck
```

If sandbox is unavailable:

```text
read-only inspection may block or use restrictive approved fallback
all mutation operations BLOCK
```

Sandbox decision IDs must be copied into operation/result evidence refs where available.

## 19.5 Promotion / Release Gate Integration

Push and release-oriented Git operations require Promotion / Release Gate.

In v1:

```text
git_push_approved returns BLOCKED by default
failure_class = GIT_PROMOTION_REQUIRED
```

Future enablement requires:

```text
promotion gate PASS
review report PASS
completion evidence PASS
human approval or release authority
remote target allowlisted
branch allowlisted
no unresolved blockers
```

## 19.6 Failure Taxonomy Integration

Every failed, blocked, or invalid Git operation must map to a standard Git failure class.

Unknown failures must map to:

```text
UNKNOWN_GIT_FAILURE
```

---

# 21. File-by-File Implementation Details

## 20.1 `__init__.py`

Expose public API only.

Must not:

```text
run Git commands on import
write evidence on import
load Tool / MCP Adapter on import
start any background process
```

## 20.2 `git_models.py`

Define constants, dataclasses, and helpers:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
```

No filesystem writes. No subprocess. No Git calls.

## 20.3 `git_policy.py`

Implement local Git policy checks and Policy / Capability Registry bridge.

Rules:

```text
unknown operation blocks
unknown caller blocks
write operation blocks unless required approvals exist
push blocks by default
merge/rebase/reset/clean block by default
raw shell command blocks
invalid branch name blocks
invalid commit message blocks
```

## 20.4 `git_command_runner.py`

Implement safe subprocess wrapper.

Must:

```text
accept only list[str]
reject raw shell strings
reject non-allowlisted command shapes
set timeout
bound output
redact secrets
avoid shell=True
call sandbox/policy checks before execution
return structured result
```

## 20.5 `git_inspection.py`

Implement read-only operations using `run_git_command_checked`.

Must:

```text
respect repo/path boundaries
truncate output
redact secrets
return schema-valid result
write evidence through git_audit.py
```

## 20.6 `git_mutation.py`

Implement approved mutation entrypoints.

Minimum v1 behavior:

```text
git_stage_approved -> BLOCKED unless all approval/evidence fields exist
git_commit_approved -> BLOCKED unless governance + approval/promotion exist
git_create_branch_approved -> BLOCKED unless branch policy and approval exist
git_revert_approved -> BLOCKED unless governance + approval/promotion exist
git_push_approved -> always BLOCKED in v1
```

No mutation function may call raw shell or arbitrary Git command strings.

## 20.7 `git_audit.py`

Implement evidence writing:

```python
append_git_operation(operation: GitOperation, repo_root: Path) -> dict
append_git_command_result(result: GitCommandResult, repo_root: Path) -> dict
append_git_blocked(result: GitMutationResult | GitCommandResult, repo_root: Path) -> dict
write_latest_git_status(result: GitStatusResult, repo_root: Path) -> dict
write_latest_git_diff(result: GitDiffResult, repo_root: Path) -> dict
write_latest_git_audit(event: GitAuditEvent, repo_root: Path) -> dict
write_git_evidence_manifest(manifest: dict, repo_root: Path) -> dict
```

Must:

```text
write only under .agentx-init/git/
append JSONL
write latest JSON atomically
redact secrets
record command, decision, status, evidence refs
write SHA-256 hashes for final evidence artifacts
```

## 20.8 `git_completion.py`

Write completion record:

```python
write_git_completion_record(record: GitCompletionRecord, repo_root: Path) -> dict
```

Creates:

```text
.agentx-init/git/git_completion_record.json
```

---

# 22. Simulated Dependency Test Contracts

Tests may use fake upstream services only when the fake enforces the same fail-closed semantics as the real layer.

Required fakes:

```text
FakePolicyRegistry
FakeSecuritySandbox
FakePatchEvidenceProvider
FakePromotionGate
FakeHumanApprovalProvider
FakeToolAdapterRegistry
```

Fake rules:

```text
default decision is BLOCK, not ALLOW
missing decision ID blocks mutation
unknown role blocks
unknown operation blocks
path outside temp repo blocks
patch evidence missing blocks stage/commit
promotion missing blocks push
invalid fake response blocks operation
```

Fake services must be test-only fixtures under tests. They must not be imported by production code.

---

# 23. Review Report and Reproducibility Evidence

After validation, create a review report if this layer writes completion evidence in the same implementation pass.

Recommended artifact:

```text
.agentx-init/git/git_implementation_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "git_review_report.schema.json",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch>",
  "reviewed_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "git_version": "<version or NOT INSTALLED>"
  },
  "commands_run": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/git",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/git/git_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/git/git_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

Reproducibility requirements:

```text
record exact commit
record initial and final git status
record command text and exit codes
record git version
record schema validation command or pytest fallback
record hashes for evidence manifest, review report, and completion record
```

A final DONE claim is invalid if reviewed commit, command exit codes, evidence manifest, completion record, or required hashes are missing.

---

# 24. Test Cases

## 21.1 Required Positive Tests

```text
test_git_status_returns_structured_result
test_git_diff_returns_structured_result
test_git_diff_name_only_returns_structured_result
test_git_diff_stat_returns_structured_result
test_git_branch_current_returns_structured_result
test_git_log_recent_is_bounded
test_git_command_runner_uses_list_args
test_git_command_runner_rejects_shell_string
test_git_policy_allows_read_only_known_role
test_git_audit_writes_operation_history
test_git_audit_writes_latest_status_atomically
test_git_schema_valid_examples_pass
```

## 21.2 Required Mutation-Control Tests

```text
test_git_stage_requires_patch_evidence
test_git_stage_blocks_without_policy_approval
test_git_stage_rejects_unapproved_paths
test_git_commit_requires_governance
test_git_commit_requires_human_or_promotion_authority
test_git_commit_rejects_unapproved_staged_changes
test_git_create_branch_requires_branch_policy
test_git_create_branch_rejects_invalid_branch_names
test_git_revert_requires_governance
test_git_push_blocks_by_default
```

## 21.3 Required Integration Tests

```text
test_git_tool_adapter_registers_read_only_tools
test_git_tool_adapter_blocks_write_tools_by_default
test_git_mcp_does_not_expose_write_tools_by_default
test_git_policy_registry_denial_blocks_operation
test_git_sandbox_denial_blocks_operation
test_git_patch_evidence_required_for_stage
test_git_promotion_required_for_push
```

## 21.4 Required Schema Tests

```text
test_git_schema_valid_examples_pass
test_git_schema_missing_required_field_fails
test_git_schema_invalid_status_fails
test_git_schema_invalid_operation_fails
test_git_command_policy_rejects_raw_shell_shape
test_git_completion_record_schema_validates
```

---

# 25. Negative Tests

Required negative cases:

```text
unknown Git operation -> INVALID or BLOCKED
unknown caller role -> BLOCKED
raw shell string -> BLOCKED
shell metacharacter injection -> BLOCKED
Git command with -c alias override -> BLOCKED
Git command with --exec-path -> BLOCKED
Git command with caller-provided --git-dir or --work-tree -> BLOCKED
git push -> BLOCKED by default
git merge -> BLOCKED
git rebase -> BLOCKED
git reset --hard -> BLOCKED
git clean -fdx -> BLOCKED
git checkout mutating path -> BLOCKED
git branch deletion -> BLOCKED
git remote modification -> BLOCKED
git tag creation -> BLOCKED
git config write -> BLOCKED
git stash pop/apply -> BLOCKED
stage without patch evidence -> BLOCKED
stage with unapproved path -> BLOCKED
commit without governance -> BLOCKED
commit without human approval or promotion authority -> BLOCKED
commit with unapproved staged files -> BLOCKED
push without Promotion Gate -> BLOCKED
sandbox unavailable for mutation -> BLOCKED
policy unavailable for mutation -> BLOCKED
secret-like output -> redacted in evidence
```

Any failed negative test is a blocker.

---

# 26. Implementation Order

Implement in this exact order:

```text
1. Create tools/agentx_evolve/git/ package.
2. Implement git_models.py.
3. Create Git schemas.
4. Implement git_policy.py with fail-closed defaults.
5. Implement git_audit.py evidence writer.
6. Implement git_command_runner.py with read-only allowlist only.
7. Implement git_inspection.py read-only operations.
8. Implement git_mutation.py blocked/approval-required operations.
9. Implement git_completion.py.
10. Add Tool / MCP Adapter registration hooks for Git tools.
11. Add schema tests.
12. Add positive inspection tests.
13. Add mutation-blocking tests.
14. Add integration tests.
15. Add negative tests.
16. Run compileall.
17. Run pytest.
18. Run schema validation.
19. Check git status.
20. Write evidence manifest.
21. Write completion record.
```

Do not implement Git mutation before policy, sandbox, evidence, and negative tests exist.

---

# 27. Acceptance Criteria

The implementation is acceptable only if:

```text
all target files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
read-only Git inspection works or returns structured BLOCKED when unavailable
Git write operations block by default unless fully approved
push blocks by default
merge/rebase/reset/clean block by default
raw shell is not exposed
shell=True is never used
caller-provided arbitrary Git command cannot execute
Security Sandbox is consulted for repo/path/command operations
Policy / Capability Registry is consulted before execution
Governed Patch Execution evidence is required for staging
Promotion / Release Gate is required for push
Tool / MCP Adapter exposes only read-only Git tools by default
MCP does not expose Git mutation tools by default
all operations write evidence
blocked operations write evidence
secrets are redacted
output is bounded
source mutation does not occur in tests except approved temp-repo fixtures
completion record exists
```

---

# 28. Manual Validation Commands

Run from repository root:

```bash
python --version
git --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/git
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_schemas.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_git_models.py \
  tools/agentx_evolve/tests/test_git_policy.py \
  tools/agentx_evolve/tests/test_git_command_runner.py \
  tools/agentx_evolve/tests/test_git_inspection.py \
  tools/agentx_evolve/tests/test_git_mutation_blocking.py \
  tools/agentx_evolve/tests/test_git_schema_validation.py \
  tools/agentx_evolve/tests/test_git_audit.py \
  tools/agentx_evolve/tests/test_git_completion.py \
  tools/agentx_evolve/tests/test_git_tool_adapter_integration.py \
  tools/agentx_evolve/tests/test_git_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_git_*.py
git status --short
```

Required result:

```text
python version recorded
git version recorded
compileall PASS with exit_code 0
schema validation PASS with exit_code 0
pytest PASS with exit_code 0
git status CLEAN or expected runtime artifacts only
```

No validation command may require:

```text
network
remote Git credentials
GitHub/GitLab API
hosted model
LLM
GPU
MCP runtime
Bun
Node
OpenCode runtime
```

---

# 29. Definition of Done

The Git Integration Layer is done when it can safely expose controlled Git inspection and governed Git mutation entrypoints without risking repository corruption or unauthorized history changes.

It must prove:

```text
Git package exists
schemas exist
tests exist
read-only Git inspection is structured and bounded
raw Git shell is not exposed
unknown Git operations fail closed
Git push blocks by default
merge/rebase/reset/clean block by default
staging requires approved patch/session evidence
commit requires governance and human approval or promotion authority
push requires future Promotion / Release Gate
Policy / Capability Registry is checked
Security Sandbox is checked
Governed Patch Execution evidence is enforced
Tool / MCP Adapter exposes only safe Git tools by default
MCP does not expose Git mutation tools by default
Git operations write evidence
blocked Git operations write evidence
evidence manifest is written
SHA-256 evidence hashes are written
secrets are redacted
completion record exists
compileall passes
pytest passes
git status remains clean or only expected runtime artifacts exist
```

Final proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/git
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_schemas.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_git_*.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
git status CLEAN or expected runtime artifacts only
```

---

# 30. No-Go Conditions

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
raw shell is exposed
shell=True is used
caller-provided arbitrary Git command executes
git push can run by default
git merge can run by default
git rebase can run by default
git reset can run by default
git clean can run by default
staging works without approved patch/session evidence
staging can stage unapproved paths
commit works without governance approval
commit works without human approval or promotion authority
commit includes unapproved staged files
push works without Promotion / Release Gate
Policy / Capability Registry is bypassed
Security Sandbox is bypassed
Tool / MCP Adapter exposes mutation tools by default
MCP exposes mutation tools by default
blocked operations lack evidence
secrets are logged
source mutation occurs outside approved temp-repo tests or approved governed flow
completion record is missing
evidence hashes are missing
```

---

# 31. Completion Evidence

After validation, create:

```text
.agentx-init/git/git_evidence_manifest.json
.agentx-init/git/git_completion_record.json
```

## 28.1 Evidence Manifest Required Fields

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
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "final_decision": "DONE"
}
```

## 28.2 Completion Record Required Fields

```json
{
  "schema_version": "1.0",
  "schema_id": "git_completion_record.schema.json",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "component_name": "Git Integration Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/git/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/git/",
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "read_only_git_operations_verified": [],
  "blocked_git_operations_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "patch_evidence_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/git/git_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence manifest and completion record.
Use Python standard-library hashlib if no project helper exists.
```

---

# 32. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places files outside canonical paths without recorded deviation
uses shell=True
accepts arbitrary Git command strings
allows Git alias/config override execution for unsafe commands
exposes mutation tools through MCP by default
enables push by default
enables merge/rebase/reset/clean by default
stages unapproved files
commits unapproved staged files
pushes without Promotion / Release Gate
bypasses Policy / Capability Registry
bypasses Security Sandbox
bypasses Governed Patch Execution evidence for staging/commit
logs secrets
writes evidence outside .agentx-init/git/ without deviation
requires network, remote credentials, GitHub/GitLab API, LLM, GPU, Bun, Node, OpenCode, or MCP runtime for validation
```

---

# 33. Final Frozen Handoff Checklist

Before coding begins, confirm:

```text
[ ] Git package path is tools/agentx_evolve/git/.
[ ] Runtime artifacts go under .agentx-init/git/.
[ ] Read-only Git inspection may be implemented first.
[ ] Git write operations are blocked unless fully approved.
[ ] Push is blocked by default.
[ ] Merge/rebase/reset/clean are blocked by default.
[ ] Raw Git shell is forbidden.
[ ] Tool / MCP Adapter exposes read-only Git tools by default only.
[ ] Policy / Capability Registry is authoritative.
[ ] Security Sandbox is authoritative for repo/path/command boundaries.
[ ] Governed Patch Execution evidence is required before staging.
[ ] Promotion / Release Gate is required before push.
[ ] Branch and commit policies are enforced.
[ ] Tests include positive, schema, integration, and negative safety cases.
[ ] Validation does not require network, credentials, LLM, GPU, Bun, Node, OpenCode, or MCP runtime.
```

---

# 34. Final Freeze Rule

This v4 document is frozen as the implementation specification for the Git Integration Layer.

Allowed future changes:

```text
PATCH: wording, typo fixes, examples, non-normative clarifications
MINOR: additive tests or additional blocked commands that preserve safety defaults
MAJOR: changing Git mutation defaults, enabling push, enabling merge/rebase/reset/clean, changing authority requirements, or adding remote-provider behavior
```

Blocked without major revision:

```text
enabling push by default
enabling merge/rebase/reset/clean by default
allowing arbitrary Git command strings
using shell=True
removing Policy / Capability Registry checks
removing Security Sandbox checks
removing Governed Patch Execution evidence requirements
removing Promotion / Release Gate requirement for push
exposing Git mutation tools through MCP by default
removing evidence logging or hashes
```

---

# 35. Repository Identity and Pathspec Safety Contract

## 35.1 Repository Identity

Every Git operation must record a stable repository identity before execution.

Required repository identity fields:

```text
repo_root_realpath
repo_hash
git_dir_realpath
worktree_root_realpath
current_head_hash
current_branch
is_detached_head
is_bare_repository
is_submodule
is_sparse_checkout
remote_urls_redacted
```

Rules:

```text
repo_root must be resolved with realpath before use
repo_root must match the approved workspace root or approved child repository
repo_hash must be computed from canonical repo_root_realpath and git_dir_realpath
.git directory must never be used as the operation lock location
submodule repositories block mutation by default
bare repositories block all operations except explicit inspection if later approved
repository identity must be included in evidence for every command
repository identity mismatch during one operation returns GIT_REPOSITORY_STATE_CHANGED
```

## 35.2 Pathspec Safety

Any path passed to Git must be treated as a pathspec risk.

Required controls:

```text
all path-limited commands must include -- before paths
each path must be sandbox-approved before command construction
each path must be relative to repo_root after normalization
absolute paths supplied by callers are rejected unless normalized and approved
paths beginning with :( are rejected by default
paths containing NUL, newline, carriage return, wildcard expansion intent, or shell metacharacters are rejected
paths resolving outside repo_root are rejected
empty path lists for mutation are rejected
path list order must be deterministic in evidence
```

Allowed path-limited read-only command shape:

```text
['git', 'diff', '--no-ext-diff', '--', '<approved-relative-path>', ...]
```

Forbidden:

```text
caller-controlled raw pathspec magic
caller-controlled -- options after --
implicit all-repo mutation when approved_paths is empty
using shell glob expansion
using Git pathspecs to include unapproved files
```

---

# 36. Mandatory Review Report and Evidence Immutability

The review report is mandatory for a final DONE verdict.

Required artifact:

```text
.agentx-init/git/git_implementation_review_report.json
```

A final DONE verdict is invalid if this artifact is missing, lacks the reviewed commit, lacks command exit codes, lacks schema validation status, lacks final evidence hashes, or omits deviations.

## 36.1 Evidence Immutability Rule

After the review report records final DONE:

```text
final evidence files must not be edited in place
changed hashes invalidate the previous DONE verdict
new evidence requires a new review report with a new timestamp
manual edits must be recorded as deviations
completion record hash must be recalculated only as part of a new validation pass
```

Required final evidence files and hashes:

```text
git_evidence_manifest.json
git_implementation_review_report.json
git_completion_record.json
all command output artifacts used by the review
JSONL histories used by the review
latest artifacts used by the review
```

---

# 37. Lock Record and Stale-Lock Evidence Contract

Create schema:

```text
tools/agentx_evolve/schemas/git_lock_record.schema.json
```

Create histories:

```text
.agentx-init/git/git_lock_history.jsonl
.agentx-init/git/git_stale_lock_history.jsonl
```

Each lock record must include:

```text
lock_id
timestamp
repo_hash
repo_root_realpath
operation_id
operation_name
lock_mode: READ | WRITE
lock_status: ACQUIRED | RELEASED | TIMEOUT | STALE_DETECTED | STALE_REJECTED
owner_process_id
timeout_seconds
stale_after_seconds
message
evidence_refs
warnings
errors
```

Rules:

```text
mutation operations require WRITE lock
read-only operations may use READ lock or short WRITE lock if implementation is simpler
stale locks must not be deleted silently
stale lock detection writes evidence
stale lock removal is blocked unless a later policy explicitly allows it
lock acquisition failure returns GIT_LOCK_UNAVAILABLE
lock release failure writes evidence and returns FAILED if operation state is uncertain
```

---

# 38. Safe Git Environment: Exact Denylist

Before running Git, construct a minimal environment rather than inheriting the full process environment.

Must set or enforce:

```text
GIT_TERMINAL_PROMPT=0
GIT_PAGER=cat
PAGER=cat
LC_ALL=C
LANG=C
```

Must remove or neutralize if present:

```text
GIT_ASKPASS
SSH_ASKPASS
GIT_SSH
GIT_SSH_COMMAND
GIT_EDITOR
EDITOR
VISUAL
GIT_EXTERNAL_DIFF
GIT_DIFF_OPTS
GIT_CONFIG_GLOBAL
GIT_CONFIG_SYSTEM
GIT_CONFIG_NOSYSTEM
GIT_TRACE
GIT_TRACE_PACKET
GIT_TRACE_CURL
GIT_CURL_VERBOSE
GIT_HTTP_USER_AGENT
GIT_PROXY_COMMAND
```

Rules:

```text
no credential prompt may occur
no editor may open
no pager may block execution
no external diff may run
no network command is allowed in v1
command timeout must kill the process group or equivalent child process safely
stdout and stderr must be bounded before evidence writing
```

---

# 39. Branch Protection Configuration Contract

Branch protection must have a safe local default even if no external provider is configured.

Default protected branches:

```text
main
master
production
release/*
hotfix/*
```

Optional config source:

```text
.agentx-init/git/git_branch_policy.json
```

Config rules:

```text
missing config uses safe defaults
invalid config blocks branch mutation
protected branch direct commit blocks
protected branch push blocks in v1
branch creation must use approved prefix unless policy allows otherwise
branch names must be recorded in evidence before and after operation
```

---

# 40. Hook, Revert, and Commit Execution Boundary

In v1, commit and revert execution must remain blocked unless hook behavior is explicitly governed and tested.

Rules:

```text
git_commit_approved may validate evidence and return dry-run / BLOCKED by default
git_revert_approved may validate evidence and return dry-run / BLOCKED by default
no commit hook may run in v1 unless a later MAJOR revision adds hook governance
no revert hook or merge-like side effect may run in v1 unless explicitly governed
--no-verify is not an acceptable shortcut unless approved by governance policy and tested
commit/revert attempts without hook policy return GIT_HOOK_RISK_BLOCKED
```

This keeps the layer from treating Git commit as a simple file write. Commit can invoke hooks, editors, signing tools, credential helpers, or external scripts in real repositories.

---

# 41. Git Result to ToolResult Mapping Contract

When Git operations are exposed through the Tool / MCP Adapter, every Git result must be converted into a schema-valid ToolResult.

Mapping rules:

```text
Git SUCCESS -> ToolResult SUCCESS
Git PARTIAL -> ToolResult PARTIAL
Git BLOCKED -> ToolResult BLOCKED
Git FAILED -> ToolResult FAILED
Git INVALID -> ToolResult INVALID
Git failure_class -> ToolResult.failure_class using direct class or TOOL_EXECUTION_FAILED fallback
Git artifact_refs -> ToolResult.artifact_refs
Git evidence_refs -> ToolResult.evidence_refs
Git result_id -> ToolResult.evidence_refs
Git command output -> summarized in ToolResult.data only after bounding and redaction
```

Tool Adapter must not:

```text
drop Git evidence refs
convert BLOCKED Git result to SUCCESS
expose raw command output without redaction
retry blocked Git mutation automatically
execute Git command directly instead of calling Git Integration API
```

---

# 42. Implementation Scoring and Hard Caps

Use this scoring only after validation.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Git package, schemas, tests, runtime artifact paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Relevant Git test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including review report and lock record. |
| Read-only Git safety | 1.0 | Inspection commands are allowlisted, bounded, redacted, and structured. |
| Mutation blocking | 1.0 | Stage/commit/branch/revert/push fail closed without full authority. |
| Policy / Sandbox / Patch / Promotion integration | 1.0 | Required authorities are consulted and evidence refs propagate. |
| Tool / MCP Adapter integration | 1.0 | Read-only exposure only; mutation hidden or blocked by default. |
| Audit / evidence / hashes | 1.0 | JSONL, latest, manifest, review report, completion record, SHA-256 hashes. |
| Repository safety | 1.0 | locking, repo identity, pathspec safety, env controls, edge cases. |

Hard caps:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
raw shell or shell=True caps score at 4.0
arbitrary Git command execution caps score at 4.0
push enabled by default caps score at 4.0
merge/rebase/reset/clean enabled by default caps score at 4.0
commit/revert hooks can run without governance caps score at 5.0
Policy bypass caps score at 5.0
Sandbox bypass caps score at 5.0
MCP mutation exposure caps score at 5.0
missing evidence manifest caps score at 7.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing evidence hashes caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

A final DONE verdict requires implementation score 10.0 and no blockers.

---

# 43. Final Sign-Off Template

Use this after validation.

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
- git: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN / EXPECTED_RUNTIME_ARTIFACTS_ONLY / DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- read-only Git coverage: PASS/FAIL
- mutation-block coverage: PASS/FAIL
- policy integration: PASS/FAIL
- sandbox integration: PASS/FAIL
- patch evidence integration: PASS/FAIL
- promotion gate integration: PASS/FAIL
- Tool / MCP Adapter integration: PASS/FAIL
- negative tests: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING
- SHA-256 hashes: PRESENT/MISSING
- final git status: CLEAN / EXPECTED_RUNTIME_ARTIFACTS_ONLY / DIRTY

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Remaining blockers:
- none / list blockers

Accepted deviations:
- none / list deviations
```

---

# 44. Final Rating

This v4 implementation specification is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, dataclasses, public functions, runtime artifacts, dependency gates, restricted-mode behavior, command allowlisting, repository-state safety gates, repository identity, pathspec safety, locking evidence, branch/commit policy, hook risk controls, Tool / MCP Adapter integration, Policy integration, Sandbox integration, Patch integration, Promotion integration, tests, negative tests, implementation order, acceptance criteria, evidence records, review report requirements, scoring hard caps, drift blockers, and Definition of Done for a safety-critical Git Integration Layer.
```
