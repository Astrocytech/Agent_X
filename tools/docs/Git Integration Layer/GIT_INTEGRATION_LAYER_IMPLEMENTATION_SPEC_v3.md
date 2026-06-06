# GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC_v3

```text
document_id: GIT_INTEGRATION_LAYER_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, subdirectory-explicit, integration-final
based_on: GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT_v3
component_id: AGENTX_GIT_INTEGRATION_LAYER
component_name: Git Integration Layer
roadmap_layer: 6
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Command Acceptance Criteria
target_language: Python
target_runtime: local-only first
target_package_preferred: tools/agentx_evolve
canonical_subdirectory: tools/agentx_evolve/git/
schema_directory: tools/agentx_evolve/schemas/
test_directory: tools/agentx_evolve/tests/
runtime_artifact_directory: .agentx-init/git/
opencode_basis: tool-specific Git operations, read-only status/diff tools, separate mutation tools, command allowlisting, output truncation, structured tool results, invalid-tool handling
rating_target: 10/10
```

---

# 1. Purpose

This document is the implementation specification for the **Git Integration Layer**.

It converts the controlling contract:

```text
GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT_v3
```

into concrete implementation instructions for a coding LLM or developer.

The Git Integration Layer controls how Agent_X may inspect, stage, commit, branch, revert, and eventually push repository changes. This layer must prevent Agent_X from using Git as a bypass around Security Sandbox, Policy / Capability Registry, Governed Patch Execution, and other safety layers.

## 1.1 Canonical Destination Summary

The implementation lives here:

```text
tools/agentx_evolve/git/
```

Schemas go here:

```text
tools/agentx_evolve/schemas/
```

Tests go here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts go here:

```text
.agentx-init/git/
```

## 1.2 OpenCode Borrowing Table

| OpenCode concept | Agent_X implementation in this spec | Borrowing limit |
|---|---|---|
| tool-specific Git ops | `git_status`, `git_diff`, `git_log` | Read-only by default |
| command allowlisting | `GitCommandPolicy` with fixed templates | Blocked by default |
| output truncation | bounded stdout/stderr, redacted | No unredacted secrets |
| invalid-tool handling | `GS_BLOCKED` result | Fail closed |
| human-question gating | approval gate references in mutation requests | Dry-run until approved |

## 1.3 Source-Copy Prohibition

OpenCode is a reference for architecture and tool shape only. Do not copy OpenCode TypeScript/Bun source code into Agent_X.

---

# 2. Required Directory Tree

```text
tools/
  agentx_evolve/
    git/
      __init__.py
      git_models.py
      git_command_policy.py
      git_command_runner.py
      git_environment.py
      git_ref_validator.py
      git_status.py
      git_diff.py
      git_mutation_gate.py
      git_stage.py
      git_commit.py
      git_branch.py
      git_revert.py
      git_push.py
      git_locks.py
      git_evidence.py
      git_dispatcher.py

  schemas/
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

  tests/
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

Current implementation status:

```text
EXISTING: __init__.py, git_models.py, git_policy.py, git_operations.py
FUTURE: git_command_policy.py (renamed from git_policy.py), git_command_runner.py,
        git_environment.py, git_ref_validator.py, git_status.py, git_diff.py,
        git_mutation_gate.py, git_stage.py, git_commit.py, git_branch.py,
        git_revert.py, git_push.py, git_locks.py, git_evidence.py, git_dispatcher.py

EXISTING SCHEMAS: git_operation.schema.json, git_result.schema.json
FUTURE SCHEMAS: 15 more schemas (listed above)
```

---

# 3. File-by-File Implementation Spec

## 3.1 `__init__.py`

### Purpose

Expose the public Git Integration API.

### Required Exports

```python
from .git_models import (
    GitOperation, GitResult, GitDiffResult, GitDiffEntry,
    GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT,
    GIT_OP_LOG, GIT_OP_BRANCH, GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG,
    GS_SUCCESS, GS_FAILED, GS_BLOCKED,
)
from .git_command_policy import GitCommandPolicy
from .git_command_runner import run_git_command
from .git_environment import build_git_environment
from .git_ref_validator import validate_ref
from .git_status import git_status
from .git_diff import git_diff, git_diff_name_only, git_diff_stat
from .git_dispatcher import dispatch_git_operation
```

### Must Not Do

```text
no Git operations on import
no filesystem writes
no shell commands
```

## 3.2 `git_models.py`

### Purpose

Define all shared data structures and constants.

### Existing Implementation

Already implemented with:

```python
# Operation constants
GIT_OP_STATUS, GIT_OP_DIFF, GIT_OP_DIFF_NAME_ONLY, GIT_OP_DIFF_STAT
GIT_OP_LOG, GIT_OP_SHOW, GIT_OP_BRANCH, GIT_OP_STAGE, GIT_OP_COMMIT, GIT_OP_TAG

# Status constants
GS_SUCCESS, GS_FAILED, GS_BLOCKED

# Dataclasses
GitOperation: op_id, timestamp, operation, target, repo_path, op_type, warnings, errors
GitResult: result_id, timestamp, operation, status, message, stdout, stderr, returncode, data, warnings, errors
GitDiffEntry: path, change_type, additions, deletions, diff_content
GitDiffResult(GitResult): entries, files_changed
```

### Future Enhancements

Add:

```python
GIT_OP_REVERT = "REVERT"
GIT_OP_PUSH = "PUSH"
GIT_OP_FETCH = "FETCH"

# Additional dataclasses for mutation operations
GitMutationRequest: mutation_request_id, operation_name, requested_effect, repo_root, ...
GitCommitEvidence: commit_evidence_id, branch_name, base_commit, new_commit, ...
GitPushRequest: push_request_id, remote_name, source_ref, target_ref, ...
GitBranchRequest: branch_request_id, base_branch, new_branch, ...
GitRevertRequest: revert_request_id, target_commit, ...
GitLockRecord: lock_record_id, lock_status, ...
GitEvidenceManifest: component_id, validated_commit, evidence_files, ...
GitReviewReport: report_id, findings, ...
GitCompletionRecord: component_id, status, files_created, ...
```

### Acceptance

```text
dataclasses instantiate
to_dict serializes them
IDs are unique
timestamps are ISO UTC
no filesystem writes
```

## 3.3 `git_command_policy.py`

### Purpose

Define allowlisted Git operation templates and blocked operations.

### Existing (as `git_policy.py`)

```python
class GitPolicyEnforcer:
    def __init__(self, allow_writes: bool = False): ...
    def add_rule(self, rule: GitPolicyRule) -> None: ...
    def enforce(self, op: GitOperation) -> GitPolicyResult: ...
    def check_result(self, op: GitOperation) -> GitResult | None: ...
```

### Future State

Rename to `git_command_policy.py`. Add:

```python
class GitCommandPolicy:
    def __init__(self, repo_root: Path): ...
    def is_allowed_operation(self, op: GitOperation) -> GitPolicyResult: ...
    def get_command_template(self, operation: str) -> list[str] | None: ...
    def validate_dynamic_args(self, operation: str, args: dict) -> bool: ...
```

Must implement blocked operations permanently in v1:

```text
reset, clean, rebase, merge
push --force, push --force-with-lease
branch -D, tag -d
remote add/remove/set-url
config --global, config --system
filter-branch, reflog expire, gc --aggressive
update-ref, symbolic-ref mutation
worktree add/remove
submodule update with network
```

### Tests

```text
read-only operation allowed
write operation blocked by default
forbidden operation blocked
allowlisted operation passes
unknown operation blocked
dynamic arg validation
```

## 3.4 `git_command_runner.py`

### Purpose

Execute argument-vector Git commands safely with hardened environment.

### Required Public Functions

```python
def run_git_command(
    argv: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout_seconds: int = 30,
    max_output_bytes: int = 1048576,
) -> GitCommandResult: ...
```

### Required Behavior

```text
command must be argument vector (list[str])
shell must be False
stdin must be closed
stdout/stderr bounded to max_output_bytes
timeout enforced
interactive prompts disabled
credential prompts disabled
all output redacted before returning
```

### Required Environment

```text
GIT_TERMINAL_PROMPT=0
GIT_ASKPASS=""
SSH_ASKPASS=""
GIT_PAGER=cat
PAGER=cat
GIT_EXTERNAL_DIFF=""
GIT_CONFIG_NOSYSTEM=1
HOME=<isolated temp dir>
XDG_CONFIG_HOME=<isolated temp dir>
LC_ALL=C
```

### Tests

```text
argument vector executes
shell injection blocked
timeout enforced
output bounded
credential prompt blocked
```

## 3.5 `git_environment.py`

### Purpose

Build the hardened Git environment and isolated config context.

### Required Public Functions

```python
def build_git_environment(repo_root: Path) -> dict[str, str]: ...
def build_isolated_home() -> Path: ...
def build_isolated_config() -> Path: ...
```

### Required Environment Variables

```text
GIT_TERMINAL_PROMPT=0
GIT_ASKPASS=""
SSH_ASKPASS=""
GIT_PAGER=cat
PAGER=cat
GIT_EXTERNAL_DIFF=""
GIT_OPTIONAL_LOCKS=0 for read-only
GIT_CONFIG_NOSYSTEM=1
HOME=<isolated>
XDG_CONFIG_HOME=<isolated>
LC_ALL=C
```

### Tests

```text
environment contains required vars
HOME is isolated from system
no credential helper in env
no GPG config leak
no include.path leak
```

## 3.6 `git_ref_validator.py`

### Purpose

Validate branches, refs, tags, remotes, and protected namespaces.

### Required Public Functions

```python
def validate_ref(ref: str, repo_root: Path) -> GitRefValidationResult: ...
def is_protected_branch(ref: str) -> bool: ...
def is_valid_branch_name(name: str) -> bool: ...
def normalize_ref(ref: str) -> str: ...
```

### Rejection Rules

```text
HEAD as mutation target
detached HEAD as branch base
@{-1} and checkout shorthand
refs containing .., @{, ASCII control, .lock suffixes
refs beginning with dash
refs ending with /, ., .lock
consecutive slashes
remote-tracking refs as local mutation targets
refs/tags/* mutation in v1
refs/remotes/* mutation in v1
protected branch namespaces
hash-like strings as branch names
```

### Protected Branches

```text
main, master, release, production, stable
refs/heads/main, refs/heads/master, refs/heads/release/*
refs/tags/*, refs/remotes/*
```

### Tests

```text
valid branch accepted
protected branch detected
detached HEAD detected
hash-like branch name rejected
shell metacharacters in name rejected
path traversal in name rejected
```

## 3.7 `git_status.py`

### Purpose

Read-only Git status via allowed template.

### Required Public Functions

```python
def git_status(repo_root: Path) -> GitResult: ...
```

Template:

```text
git --no-pager status --porcelain=v1
```

### Tests

```text
status returns SUCCESS in git repo
status returns BLOCKED outside git repo
output bounded
secrets redacted
```

## 3.8 `git_diff.py`

### Purpose

Read-only Git diff via allowed templates.

### Required Public Functions

```python
def git_diff(repo_root: Path, target: str = "HEAD") -> GitResult: ...
def git_diff_name_only(repo_root: Path, target: str = "HEAD") -> GitResult: ...
def git_diff_stat(repo_root: Path, target: str = "HEAD") -> GitResult: ...
```

Templates:

```text
git --no-pager diff --no-ext-diff --no-textconv -- <paths>
git --no-pager diff --no-ext-diff --no-textconv --name-only -- <paths>
git --no-pager diff --no-ext-diff --no-textconv --stat -- <paths>
```

### Tests

```text
diff returns changes
diff name-only returns filenames
diff stat returns summary
external diff disabled
pager disabled
```

## 3.9 `git_mutation_gate.py`

### Purpose

Verify all required authorities before allowing mutation.

### Required Public Functions

```python
def check_mutation_allowed(
    op: GitOperation,
    repo_root: Path,
    policy_decision_id: str | None = None,
    sandbox_decision_id: str | None = None,
    patch_evidence_id: str | None = None,
    approval_id: str | None = None,
    promotion_gate_id: str | None = None,
) -> GitPolicyResult: ...
```

### Gate Order

```text
1. Git command policy allows operation
2. Policy / Capability Registry allows operation
3. Security Sandbox allows paths/commands
4. Patch evidence exists (for stage/commit)
5. Stage evidence exists (for commit)
6. Human approval exists (if required)
7. Promotion gate exists (for push)
8. Git mutation lock acquired
9. ALLOW
```

### Tests

```text
blocks when policy missing
blocks when sandbox missing
blocks when patch evidence missing
blocks when approval missing
blocks when promotion gate missing
allows when all gates pass
```

## 3.10 `git_stage.py`

### Purpose

Stage only explicit approved paths.

### Required Public Functions

```python
def git_stage(
    repo_root: Path,
    paths: list[str],
    patch_evidence_id: str,
    dry_run: bool = True,
) -> GitResult: ...
```

### Rules

```text
paths must be explicit
paths must match approved patch evidence
git add . / git add -A forbidden
must record pre-stage and post-stage status
```

### Template

```text
git add -- <explicit approved paths>
```

### Tests

```text
blocks without patch evidence
blocks with unapproved paths
blocks on git add . attempt
allows explicit approved paths in dry-run
```

## 3.11 `git_commit.py`

### Purpose

Commit only approved staged changes.

### Required Public Functions

```python
def git_commit(
    repo_root: Path,
    message: str,
    stage_evidence_id: str,
    dry_run: bool = True,
) -> GitCommitEvidence: ...
```

### Rules

```text
requires approved stage evidence
requires governance if needed
no editor invocation
no GPG signing
no hook execution
commit message from approved evidence
```

### Template

```text
git commit --no-gpg-sign --no-verify -m <approved message>
```

### Tests

```text
blocks without stage evidence
blocks with empty message
blocks when HEAD changed since approval
records commit evidence on success
```

## 3.12 `git_branch.py`

### Purpose

Create only approved non-protected branches.

### Required Public Functions

```python
def git_branch(
    repo_root: Path,
    new_branch: str,
    base_branch: str = "HEAD",
    governance_decision_id: str | None = None,
    dry_run: bool = True,
) -> GitResult: ...
```

### Rules

```text
requires policy approval
requires governance decision
requires ref validation
protected branch names blocked
base commit recorded
```

### Template

```text
git branch <validated new branch> <validated base commit>
```

### Tests

```text
blocks without governance
blocks protected branch name
blocks invalid branch name
allows valid branch in dry-run
```

## 3.13 `git_revert.py`

### Purpose

Prepare revert plans and block actual revert unless approved.

### Required Public Functions

```python
def git_revert(
    repo_root: Path,
    target_commit: str,
    governance_decision_id: str | None = None,
    human_approval_id: str | None = None,
    dry_run: bool = True,
) -> GitResult: ...
```

### Rules

```text
dry-run by default
requires governance and human approval for live revert
reset-based rollback forbidden
history rewrite rollback forbidden
post-revert status evidenced
```

### Template

```text
git revert --no-edit <validated commit>
```

### Tests

```text
blocks without governance
blocks without human approval
blocked for history-rewrite targets
dry-run succeeds without mutation
```

## 3.14 `git_push.py`

### Purpose

Block push by default; require Promotion Gate approval.

### Required Public Functions

```python
def git_push(
    repo_root: Path,
    remote: str = "origin",
    source_ref: str = "HEAD",
    target_ref: str = "",
    promotion_gate_id: str | None = None,
    dry_run: bool = True,
) -> GitResult: ...
```

### Rules

```text
push blocked by default
remote must be allowlisted
refspec must be allowlisted
force flags forbidden
promotion gate required
commit evidence required
credential prompts disabled
```

### Template

```text
git push <allowlisted remote> <allowlisted source_ref>:<allowlisted target_ref>
```

### Tests

```text
blocks without promotion gate
blocks without commit evidence
blocks force push
blocks unallowlisted remote
blocks in v1 for all callers
```

## 3.15 `git_locks.py`

### Purpose

Serialize mutation operations.

### Required Public Functions

```python
def acquire_git_lock(repo_root: Path, operation_id: str) -> GitLockRecord: ...
def release_git_lock(repo_root: Path, lock_record: GitLockRecord) -> None: ...
def is_git_lock_stale(repo_root: Path) -> bool: ...
```

### Rules

```text
lock file under .agentx-init/git/locks/
fcntl flock
timeout configurable (default 30s)
stale lock handling explicit
```

### Tests

```text
lock acquired and released
second acquire blocks
stale lock detected
timeout enforced
```

## 3.16 `git_evidence.py`

### Purpose

Write append-only evidence, latest artifacts, manifests, hashes.

### Required Public Functions

```python
def append_git_operation(op: GitOperation, result: GitResult, repo_root: Path) -> dict: ...
def append_git_mutation_request(req: GitMutationRequest, repo_root: Path) -> dict: ...
def write_latest_git_artifact(artifact: dict, name: str, repo_root: Path) -> dict: ...
def write_git_evidence_manifest(repo_root: Path) -> dict: ...
def write_git_completion_record(repo_root: Path, status: str) -> dict: ...
```

### Required Artifacts

```text
.agentx-init/git/git_operation_history.jsonl
.agentx-init/git/git_blocked_history.jsonl
.agentx-init/git/git_mutation_request_history.jsonl
.agentx-init/git/git_commit_evidence_history.jsonl
.agentx-init/git/git_latest_operation.json
.agentx-init/git/git_latest_result.json
.agentx-init/git/git_evidence_manifest.json
.agentx-init/git/git_completion_record.json
```

### Rules

```text
append-only JSONL
atomic JSON writes
SHA-256 hashes in manifest
no raw secrets
no unbounded output
blocked operations are evidenced
```

### Tests

```text
operation appended
blocked operation appended
latest artifact written
manifest created
completion record created
```

## 3.17 `git_dispatcher.py`

### Purpose

Enforce the full operation pipeline before any Git helper runs.

### Required Public Functions

```python
def dispatch_git_operation(
    op: GitOperation,
    repo_root: Path,
    policy_decision_id: str | None = None,
    sandbox_decision_id: str | None = None,
) -> GitResult: ...
```

### Pipeline Order

```text
1. Validate GitOperation schema
2. Check GitCommandPolicy
3. Check caller role permission
4. Check sandbox (for repo root + paths)
5. For mutation: check mutation gate
6. For read-only: run command
7. For mutation: acquire lock, run, release lock
8. Write evidence
9. Return result
```

### Tests

```text
dispatch read-only operation
dispatch blocked operation
dispatch mutation blocked
dispatch with policy deny
dispatch with sandbox deny
```

---

# 4. Schema Implementation Spec

Create JSON Schema Draft 7 or Draft 2020-12 files.

## 4.1 `git_operation.schema.json`

EXISTING. Required fields:

```text
schema_version, schema_id, operation_id, timestamp, source_component,
caller_role, caller_id, session_id, operation_name, requested_effect,
repo_root, paths, arguments, dry_run, warnings, errors
```

## 4.2 `git_command_policy.schema.json` (FUTURE)

## 4.3 `git_command_result.schema.json` (FUTURE)

## 4.4 `git_status_diff_result.schema.json` (FUTURE)

## 4.5 `git_operation_result.schema.json` (FUTURE)

## 4.6 `git_mutation_request.schema.json` (FUTURE)

## 4.7 `git_branch_request.schema.json` (FUTURE)

## 4.8 `git_ref_validation_result.schema.json` (FUTURE)

## 4.9 `git_stage_request.schema.json` (FUTURE)

## 4.10 `git_commit_evidence.schema.json` (FUTURE)

## 4.11 `git_push_request.schema.json` (FUTURE)

## 4.12 `git_revert_request.schema.json` (FUTURE)

## 4.13 `git_lock_record.schema.json` (FUTURE)

## 4.14 `git_audit_event.schema.json` (FUTURE)

## 4.15 `git_evidence_manifest.schema.json` (FUTURE)

## 4.16 `git_review_report.schema.json` (FUTURE)

## 4.17 `git_completion_record.schema.json` (FUTURE)

Each schema must require:

```text
schema_version (pattern ^1\.0$)
schema_id (const)
timestamp
source_component
warnings
errors
```

---

# 5. Implementation Order

Implement in this order:

```text
1. git_models.py (enhance existing)
2. git_command_policy.py (rename + enhance git_policy.py)
3. git_command_runner.py (new)
4. git_environment.py (new)
5. git_ref_validator.py (new)
6. git_status.py (enhance git_operations.py)
7. git_diff.py (enhance git_operations.py)
8. git_mutation_gate.py (new)
9. git_stage.py (new)
10. git_commit.py (new)
11. git_branch.py (new)
12. git_revert.py (new)
13. git_push.py (new)
14. git_locks.py (new)
15. git_evidence.py (new)
16. git_dispatcher.py (new)
17. schemas (15 new)
18. tests
19. completion evidence
```

---

# 6. Coding Constraints for LLM Implementer

```text
do not implement raw shell executor
do not implement credential storage
do not implement remote provider config
do not implement GPG signing
do not implement prompt/editor interaction
do not implement merge or rebase
do not implement submodule mutation
do not implement worktree mutation
do not implement Git daemon
do not implement MCP server for Git
do not modify L0
do not use shell=True
do not add non-standard dependencies
```

---

# 7. Definition of Done

This implementation is done only when:

```text
all 17 target files exist
all 17 schemas exist (2 now, 15 future)
all tests exist and pass
read-only operations succeed
write operations block by default
push operations block by default
forbidden operations block permanently
environment hardening is complete
evidence writing works
completion record exists
```

---

# 8. Completion Evidence

After implementation, write:

```text
.agentx-init/git/git_integration_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "component_id": "AGENTX_GIT_INTEGRATION_LAYER",
  "status": "VALIDATED",
  "canonical_subdirectory": "tools/agentx_evolve/git/",
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "commands_run": [],
  "artifacts_generated": [],
  "deviations_from_contract": [],
  "unresolved_risks": []
}
```

---

# 9. Coding LLM Handoff Checklist

```text
[ ] The target repository is Agent_X.
[ ] Existing files are under tools/agentx_evolve/git/.
[ ] New files go in the same directory.
[ ] OpenCode is used only as design reference.
[ ] No OpenCode source code is copied.
[ ] Implementation language is Python.
[ ] Runtime artifacts go under .agentx-init/git/.
[ ] Git write operations are blocked by default.
[ ] Shell is blocked; only argument-vector execution.
[ ] Tests must run without GPU, network, or hosted model.
[ ] All mutation operations require dry_run first.
```
