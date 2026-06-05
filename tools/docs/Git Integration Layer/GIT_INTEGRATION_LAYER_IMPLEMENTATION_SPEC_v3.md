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
opencode_basis: read/edit/write/patch/shell tool separation, command allowlisting, output truncation, invalid-tool fail-closed behavior
rating_target: 10/10
```

---

# 0. v3 Review and Improvement Summary

## 0.1 v2 Rating

The v2 implementation spec was rated:

```text
9.7/10
```

## 0.2 Why v2 Was Not Fully 10/10

v2 correctly defined the canonical subdirectory:

```text
tools/agentx_evolve/git/
```

However, it still needed several final implementation-control improvements:

```text
1. A single explicit destination summary at the top for coding agents.
2. Exact file-by-file implementation spec matching the required package files in the contract.
3. All 17 required schema implementations in a single section.
4. Clear documentation of what already exists (git_models.py, git_operations.py, git_policy.py) vs what is still needed.
5. Explicit dependency-degraded behavior rules.
6. A final "ready to hand to coding LLM" checklist.
```

## 0.3 v3 Improvements

This v3 adds:

```text
canonical destination summary
existing-file audit with current behavior notes
future-file spec for all 14 still-needed implementation files
all 17 schema specs (2 existing + 15 FUTURE)
implementation order
coding-LLM handoff checklist
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Git Integration Layer**.

## 1.1 Canonical Destination Summary

The implementation lives here:

```text
tools/agentx_evolve/git/
```

The schemas must go here:

```text
tools/agentx_evolve/schemas/
```

The tests must go here:

```text
tools/agentx_evolve/tests/
```

The runtime artifacts must go here:

```text
.agentx-init/git/
```

This spec converts the controlling contract:

```text
GIT_INTEGRATION_LAYER_EQC_FIC_SIB_SCHEMA_CONTRACT_v3
```

into exact implementation instructions for a coding LLM or developer.

The implementation must create or extend a deterministic Git Integration Layer that Agent_X self-evolution components use for all Git inspection and mutation. This layer controls which Git operations are allowed, how they are executed, what evidence is recorded, and what authorities are required before mutation may proceed.

This layer must borrow useful OpenCode-style concepts:

```text
command allowlisting
read-only tool separation
structured tool results
output truncation
invalid-tool fail-closed behavior
```

but must implement them under Agent_X's stricter rules:

```text
no raw shell execution
no unbounded Git output
no implicit git add
no unreviewed commits
no push by default
no hooks/external-diff/pager by default
no credential prompts
all operations schema-governed
all decisions evidence-backed
```

## 1.2 Existing Implementation Audit

The following files already exist under `tools/agentx_evolve/git/`:

### Existing: `__init__.py`
- Exports `GitOperation`, `GitResult`, `GitDiffResult`, `GitDiffEntry`, `run_git_operation`, `git_status`, `git_diff`, `git_diff_name_only`, `git_diff_stat`, `git_log`, `git_knows_repo`, `GitPolicyEnforcer`, `GitPolicyRule`, `GitPolicyResult`.
- No side effects on import.
- **Status: Present. No changes required for exports.**

### Existing: `git_models.py`
- Defines `GitOperation`, `GitResult`, `GitDiffResult`, `GitDiffEntry` dataclasses.
- Defines operation constants: `GIT_OP_STATUS`, `GIT_OP_DIFF`, `GIT_OP_DIFF_NAME_ONLY`, `GIT_OP_DIFF_STAT`, `GIT_OP_LOG`, `GIT_OP_SHOW`, `GIT_OP_BRANCH`, `GIT_OP_STAGE`, `GIT_OP_COMMIT`, `GIT_OP_TAG`.
- Defines status constants: `GS_SUCCESS`, `GS_FAILED`, `GS_BLOCKED`.
- Defines `GitOpType` enum (READ/WRITE).
- Defines helpers: `utc_now_iso()`, `new_id()`, `to_dict()`.
- **Status: Present. Models are simpler than contract requires. Missing: `GitCommandPolicy`, `GitOperationResult`, `GitStatusDiffResult`, `GitMutationRequest`, `GitBranchRequest`, `GitStageRequest`, `GitCommitEvidence`, `GitPushRequest`, `GitRevertRequest`, `GitLockRecord`, `GitAuditEvent`, `GitEvidenceManifest`, `GitReviewReport`, `GitCompletionRecord`, `GitRefValidationResult`, `GitCommandResult`. These are FUTURE additions.**

### Existing: `git_operations.py`
- `run_git_operation(op)` — builds args from fixed templates, runs subprocess with 30s timeout, redacts secrets.
- `git_status(repo_path)` — calls run_git_operation with GIT_OP_STATUS.
- `git_diff(target, repo_path)` — calls run_git_operation with GIT_OP_DIFF.
- `git_diff_name_only(target, repo_path)` — calls run_git_operation with GIT_OP_DIFF_NAME_ONLY.
- `git_diff_stat(target, repo_path)` — calls run_git_operation with GIT_OP_DIFF_STAT.
- `git_log(count, repo_path)` — calls run_git_operation with GIT_OP_LOG.
- `git_knows_repo(repo_path)` — runs `git rev-parse --git-dir` directly.
- Write operations return BLOCKED. Forbidden words (push, fetch, pull, merge, rebase, reset, clean, cherry-pick, revert) checked on target string.
- Uses `subprocess.run()` with argument vectors. No `shell=True`.
- Environment is NOT hardened (no GIT_TERMINAL_PROMPT, no GIT_PAGER, no HOME isolation).
- **Status: Present. Lacks environment hardening, Git config isolation, ref validation, diff flags (--no-ext-diff, --no-textconv, --porcelain), bounded output enforcement, mutation gate, evidence writing, and the full 29-step pipeline.**

### Existing: `git_policy.py`
- `GitPolicyEnforcer` class — enforces read/write policy, blocks forbidden commands by substring match.
- `GitPolicyRule` dataclass — rule_id, operation, effect, reason.
- `GitPolicyResult` dataclass — result_id, operation, allowed, message, matched_rules.
- Uses substring matching against target for forbidden ops.
- `check_result()` returns `GitResult` with BLOCKED or None.
- **Status: Present. Simpler than contract's `git_command_policy.py` which needs structured allowlist with fixed_args, allowed_dynamic_args, allowed_roles, effect, requires_* fields. This should be renamed/extended.**

### Existing: `tools/agentx_evolve/schemas/git_operation.schema.json`
- Draft 2020-12. Required: `operation`. Properties match `GitOperation` fields.
- **Status: Present.**

### Existing: `tools/agentx_evolve/schemas/git_result.schema.json`
- Draft 2020-12. Required: `operation`, `status`. Properties match `GitResult` fields.
- **Status: Present.**

### Existing: `tools/agentx_evolve/tests/test_git_integration.py`
- Tests for models, run_git_operation, git_knows_repo, GitPolicyEnforcer.
- 183 lines. Covers model defaults, serialization, write blocking, policy enforcement.
- **Status: Present and passing.**

### Existing: `tools/agentx_evolve/tests/test_git_tools.py`
- Tests for tool-layer git wrappers (git_status, git_diff, git_create_branch, etc.).
- Tests that read-only tools return ToolResult and write tools are BLOCKED.
- **Status: Present.**

### Existing: `tools/agentx_evolve/tests/test_git_evidence.py`
- Tests for promotion git_evidence module (validate_git_evidence, verify_git_state_allows_promotion, write/load).
- **Status: Present.**

---

# 2. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic Git Integration package that can answer:

```text
ALLOW
BLOCK
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
NEEDS_PROMOTION_GATE
DRY_RUN_ONLY
```

for:

```text
git status
git diff (name-only, stat, full)
git log
git branch (inspect)
git rev-parse
git ls-files
git add (explicit approved paths only)
git commit (approved evidence only)
git branch creation (governed)
git revert (governed)
git push (promotion-gated only)
```

It must expose safe equivalents of OpenCode-style Git primitives:

```text
OpenCode shell git commands -> git_status / git_diff / git_log (read-only)
OpenCode shell git add      -> git_stage_approved (patch-evidence-gated)
OpenCode shell git commit   -> git_commit_approved (stage-evidence-gated)
OpenCode shell git push     -> git_push_approved (promotion-gated)
OpenCode shell git branch   -> git_create_branch_approved (governance-gated)
OpenCode invalid commands   -> BLOCKED structured result
```

The component must not implement:

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

---

# 3. Required Build Shape and Exact `tools/` Subdirectory

## 3.1 Canonical Location

This component resides under the post-Initiator tool package:

```text
tools/agentx_evolve/git/
```

## 3.2 Full Required Directory Tree

Create or update this exact tree:

```text
tools/
  agentx_evolve/
    git/
      __init__.py           [EXISTS — extend exports as new modules are added]
      git_models.py         [EXISTS — extend with missing models]
      git_command_policy.py [FUTURE — rename/extend from git_policy.py]
      git_command_runner.py [FUTURE — hardened subprocess wrapper]
      git_environment.py    [FUTURE — hardened env builder]
      git_ref_validator.py  [FUTURE — branch/ref/tag validation]
      git_status.py         [FUTURE — read-only status wrapper]
      git_diff.py           [FUTURE — read-only diff wrapper]
      git_mutation_gate.py  [FUTURE — policy + sandbox + evidence gating]
      git_stage.py          [FUTURE — stage mutation, blocked by default]
      git_commit.py         [FUTURE — commit mutation, blocked by default]
      git_branch.py         [FUTURE — branch creation, blocked by default]
      git_revert.py         [FUTURE — revert, blocked by default]
      git_push.py           [FUTURE — push, blocked by default]
      git_locks.py          [FUTURE — mutation serialization]
      git_evidence.py       [FUTURE — append-only evidence]
      git_dispatcher.py     [FUTURE — full operation pipeline]

    schemas/
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

    tests/
      test_git_integration.py       [EXISTS — extend coverage]
      test_git_tools.py             [EXISTS]
      test_git_evidence.py          [EXISTS]
      test_git_command_policy.py    [FUTURE]
      test_git_command_runner.py    [FUTURE]
      test_git_environment.py       [FUTURE]
      test_git_ref_validator.py     [FUTURE]
      test_git_status.py            [FUTURE]
      test_git_diff.py              [FUTURE]
      test_git_mutation_gate.py     [FUTURE]
      test_git_stage.py             [FUTURE]
      test_git_commit.py            [FUTURE]
      test_git_branch.py            [FUTURE]
      test_git_revert.py            [FUTURE]
      test_git_push.py              [FUTURE]
      test_git_locks.py             [FUTURE]
      test_git_evidence.py          [EXISTS — extend]
      test_git_dispatcher.py        [FUTURE]
      test_git_negative_cases.py    [FUTURE]
      test_git_schema_validation.py [FUTURE]
      validate_git_integration_schemas.py [FUTURE]
```

## 3.3 Import Rule

Source imports should use installed package names:

```python
from agentx_evolve.git.git_models import GitOperation
from agentx_evolve.git.git_command_policy import GitCommandPolicyEnforcer
```

Do not use this as the default import form:

```python
from tools.agentx_evolve.git.git_models import GitOperation
```

## 3.4 Packaging Expectation

If `tools/agentx_evolve` does not yet have packaging metadata, add it later. For this implementation slice, tests may import by adding `tools/` to `PYTHONPATH`, but source code should be written as if `agentx_evolve` is a package.

Expected test-time import style:

```python
from agentx_evolve.git.git_models import GitOperation
```

---

# 4. Implementation Order

Implement in this exact order.

```text
1. git_models.py               [extend existing]
2. schemas                      [create all 15 FUTURE schemas]
3. git_command_policy.py        [from git_policy.py]
4. git_environment.py           [hardened env builder]
5. git_command_runner.py        [safe subprocess wrapper]
6. git_ref_validator.py         [ref/branch/tag validation]
7. git_status.py                [read-only status]
8. git_diff.py                  [read-only diff]
9. git_mutation_gate.py         [gate logic]
10. git_stage.py                [mutation — blocked by default]
11. git_commit.py               [mutation — blocked by default]
12. git_branch.py               [mutation — blocked by default]
13. git_revert.py               [mutation — blocked by default]
14. git_push.py                 [mutation — blocked by default]
15. git_locks.py                [mutation serialization]
16. git_evidence.py             [append-only evidence]
17. git_dispatcher.py           [full pipeline orchestrator]
18. __init__.py                 [update exports]
19. tests
20. completion evidence
```

Rationale:

```text
models first
schemas second
policy and environment before command runner
ref validator before status/diff
mutation gate before any mutation module
locks before stage/commit/push
evidence after mutation modules exist
dispatcher last — ties everything together
tests after all source modules exist
```

---

# 5. File-by-File Implementation Spec

---

## 5.1 `tools/agentx_evolve/git/__init__.py`

### Purpose

Expose the public Git Integration API.

### Current Content

Already exports `GitOperation`, `GitResult`, `GitDiffResult`, `GitDiffEntry`, operation/status constants, `run_git_operation`, convenience functions, and policy classes.

### Required Additions

As new modules are implemented, add their public exports:

```python
# FUTURE exports to add:
from .git_command_policy import GitCommandPolicy, GitCommandPolicyEnforcer
from .git_command_runner import run_git_command_safe
from .git_environment import build_hardened_git_env, HardenedGitEnvironment
from .git_ref_validator import validate_ref, RefValidationResult
from .git_status import run_git_status_readonly
from .git_diff import run_git_diff_readonly
from .git_mutation_gate import MutationGate, MutationGateResult
from .git_stage import stage_approved_paths
from .git_commit import commit_approved_changes
from .git_branch import create_approved_branch
from .git_revert import revert_approved_commit
from .git_push import push_approved_commit
from .git_locks import GitMutationLock
from .git_evidence import write_git_evidence
from .git_dispatcher import dispatch_git_operation
```

### Must Not Do

```text
no side effects on import
no filesystem writes
no network
no Git commands on import
```

---

## 5.2 `git_models.py`

### Purpose

Define all shared Git data structures and constants.

### Current Content

Already defines: `GitOperation`, `GitResult`, `GitDiffResult`, `GitDiffEntry`, operation constants, status constants, `GitOpType`, `utc_now_iso()`, `new_id()`, `to_dict()`.

### Required Extensions

Add these dataclasses for contract compliance. Each should be a plain Python dataclass with `schema_version`, `schema_id`, `to_dict()`:

#### `GitCommandPolicy` (FUTURE)

```python
@dataclass
class GitCommandPolicy:
    schema_version: str = "1.0"
    schema_id: str = "git_command_policy.schema.json"
    policy_id: str = ""
    operation_name: str = ""
    command: str = "git"
    fixed_args: list[str] = field(default_factory=list)
    allowed_dynamic_args: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    effect: str = "READ"
    requires_policy: bool = True
    requires_sandbox: bool = True
    requires_patch_evidence: bool = False
    requires_stage_evidence: bool = False
    requires_commit_evidence: bool = False
    requires_human_approval: bool = False
    requires_governance: bool = False
    requires_promotion_gate: bool = False
    mutates_repository: bool = False
    writes_index: bool = False
    writes_history: bool = False
    uses_remote: bool = False
    allows_hooks: bool = False
    allows_external_diff: bool = False
    allows_pager: bool = False
    enabled: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitCommandResult` (FUTURE)

```python
@dataclass
class GitCommandResult:
    schema_version: str = "1.0"
    schema_id: str = "git_command_result.schema.json"
    command_result_id: str = ""
    operation_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    operation_name: str = ""
    command_template_id: str = ""
    argv_redacted: list[str] = field(default_factory=list)
    argv_sha256: str = ""
    cwd: str = ""
    environment_profile_id: str = ""
    exit_code: int = 0
    status: str = GS_SUCCESS
    stdout_summary: str = ""
    stderr_summary: str = ""
    stdout_truncated: bool = False
    stderr_truncated: bool = False
    duration_ms: int = 0
    timeout_seconds: int = 30
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    failure_class: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitOperationResult` (FUTURE)

```python
@dataclass
class GitOperationResult:
    schema_version: str = "1.0"
    schema_id: str = "git_operation_result.schema.json"
    operation_result_id: str = ""
    operation_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    operation_name: str = ""
    requested_effect: str = "READ"
    status: str = GS_SUCCESS
    exit_code: int = 0
    repo_root: str = ""
    pre_state_snapshot_id: str = ""
    post_state_snapshot_id: str = ""
    command_result_ids: list[str] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    failure_class: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitStatusDiffResult` (FUTURE)

```python
@dataclass
class GitStatusDiffResult:
    schema_version: str = "1.0"
    schema_id: str = "git_status_diff_result.schema.json"
    result_id: str = ""
    operation_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    operation_name: str = ""
    status: str = GS_SUCCESS
    exit_code: int = 0
    repo_root: str = ""
    current_branch: str = ""
    head_commit: str = ""
    changed_files: list[str] = field(default_factory=list)
    diff_summary: dict = field(default_factory=dict)
    bounded_output: str = ""
    output_truncated: bool = False
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    failure_class: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitMutationRequest` (FUTURE)

```python
@dataclass
class GitMutationRequest:
    schema_version: str = "1.0"
    schema_id: str = "git_mutation_request.schema.json"
    mutation_request_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    operation_name: str = ""
    requested_effect: str = ""
    repo_root: str = ""
    target_branch: str = ""
    base_commit: str = ""
    target_commit: str = ""
    paths: list[str] = field(default_factory=list)
    patch_session_id: str = ""
    patch_evidence_id: str = ""
    stage_evidence_id: str = ""
    commit_evidence_id: str = ""
    policy_decision_id: str = ""
    sandbox_decision_id: str = ""
    governance_decision_id: str = ""
    human_approval_id: str = ""
    promotion_gate_id: str = ""
    commit_message: str = ""
    dry_run: bool = True
    idempotency_key: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitBranchRequest` (FUTURE)

```python
@dataclass
class GitBranchRequest:
    schema_version: str = "1.0"
    schema_id: str = "git_branch_request.schema.json"
    branch_request_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    base_branch: str = ""
    base_commit: str = ""
    new_branch: str = ""
    policy_decision_id: str = ""
    governance_decision_id: str = ""
    human_approval_id: str = ""
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitRefValidationResult` (FUTURE)

```python
@dataclass
class GitRefValidationResult:
    schema_version: str = "1.0"
    schema_id: str = "git_ref_validation_result.schema.json"
    ref_validation_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    ref_kind: str = "BRANCH"
    raw_ref: str = ""
    normalized_ref: str = ""
    is_valid: bool = False
    is_protected: bool = False
    is_remote_tracking: bool = False
    is_symbolic: bool = False
    is_detached_head: bool = False
    check_ref_format_status: str = "NOT_RUN"
    failure_class: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitStageRequest` (FUTURE)

```python
@dataclass
class GitStageRequest:
    schema_version: str = "1.0"
    schema_id: str = "git_stage_request.schema.json"
    stage_request_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    base_commit: str = ""
    paths: list[str] = field(default_factory=list)
    patch_session_id: str = ""
    patch_evidence_id: str = ""
    approved_path_set_hash: str = ""
    policy_decision_id: str = ""
    sandbox_decision_id: str = ""
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitCommitEvidence` (FUTURE)

```python
@dataclass
class GitCommitEvidence:
    schema_version: str = "1.0"
    schema_id: str = "git_commit_evidence.schema.json"
    commit_evidence_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    branch_name: str = ""
    base_commit: str = ""
    new_commit: str = ""
    operation_id: str = ""
    mutation_request_id: str = ""
    stage_evidence_id: str = ""
    patch_session_id: str = ""
    patch_evidence_id: str = ""
    staged_paths: list[str] = field(default_factory=list)
    staged_path_set_hash: str = ""
    diff_stat: dict = field(default_factory=dict)
    commit_message: str = ""
    policy_decision_id: str = ""
    sandbox_decision_id: str = ""
    governance_decision_id: str = ""
    human_approval_id: str = ""
    promotion_gate_id: str = ""
    secret_scan_status: str = "NOT_AVAILABLE"
    status: str = GS_SUCCESS
    artifact_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    sha256_refs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitPushRequest` (FUTURE)

```python
@dataclass
class GitPushRequest:
    schema_version: str = "1.0"
    schema_id: str = "git_push_request.schema.json"
    push_request_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    remote_name: str = ""
    remote_url_redacted: str = ""
    source_ref: str = ""
    target_ref: str = ""
    commit_evidence_id: str = ""
    review_report_id: str = ""
    completion_record_id: str = ""
    policy_decision_id: str = ""
    promotion_gate_id: str = ""
    human_approval_id: str = ""
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitRevertRequest` (FUTURE)

```python
@dataclass
class GitRevertRequest:
    schema_version: str = "1.0"
    schema_id: str = "git_revert_request.schema.json"
    revert_request_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    current_branch: str = ""
    head_commit: str = ""
    target_commit: str = ""
    revert_plan_id: str = ""
    policy_decision_id: str = ""
    governance_decision_id: str = ""
    human_approval_id: str = ""
    dry_run: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitLockRecord` (FUTURE)

```python
@dataclass
class GitLockRecord:
    schema_version: str = "1.0"
    schema_id: str = "git_lock_record.schema.json"
    lock_record_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    repo_root: str = ""
    lock_path: str = ".agentx-init/git/locks/git_mutation.lock"
    operation_id: str = ""
    mutation_request_id: str = ""
    lock_status: str = "ACQUIRED"
    holder_id: str = ""
    timeout_seconds: int = 30
    pre_head_commit: str = ""
    pre_index_hash: str = ""
    pre_worktree_hash: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitAuditEvent` (FUTURE)

```python
@dataclass
class GitAuditEvent:
    schema_version: str = "1.0"
    schema_id: str = "git_audit_event.schema.json"
    event_id: str = ""
    timestamp: str = ""
    source_component: str = "GitIntegrationLayer"
    event_type: str = ""
    operation_id: str = ""
    caller_role: str = ""
    status: str = ""
    failure_class: str = ""
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
```

#### `GitEvidenceManifest` (FUTURE)

```python
@dataclass
class GitEvidenceManifest:
    schema_version: str = "1.0"
    schema_id: str = "git_evidence_manifest.schema.json"
    component_id: str = "AGENTX_GIT_INTEGRATION_LAYER"
    validated_commit: str = ""
    validated_at: str = ""
    commands: list[dict] = field(default_factory=list)
    evidence_files: list[str] = field(default_factory=list)
    evidence_file_hashes: list[dict] = field(default_factory=list)
    runtime_artifacts: list[str] = field(default_factory=list)
    known_expected_runtime_artifacts: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    source_mutation_status: str = "CLEAN_OR_APPROVED_GIT_MUTATION_ONLY"
    final_decision: str = "NOT_DONE"
```

#### `GitReviewReport` (FUTURE)

```python
@dataclass
class GitReviewReport:
    schema_version: str = "1.0"
    schema_id: str = "git_review_report.schema.json"
    review_id: str = ""
    component_id: str = "AGENTX_GIT_INTEGRATION_LAYER"
    reviewed_commit: str = ""
    reviewed_at: str = ""
    commands_run: list[dict] = field(default_factory=list)
    coverage_statuses: dict = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    high_issues: list[str] = field(default_factory=list)
    deviation_register: list[dict] = field(default_factory=list)
    final_verdict: str = "NOT_DONE"
```

#### `GitCompletionRecord` (FUTURE)

```python
@dataclass
class GitCompletionRecord:
    schema_version: str = "1.0"
    schema_id: str = "git_completion_record.schema.json"
    component_id: str = "AGENTX_GIT_INTEGRATION_LAYER"
    status: str = "VALIDATED"
    validated_commit: str = ""
    validated_at: str = ""
    canonical_subdirectory: str = "tools/agentx_evolve/git/"
    canonical_schema_subdirectory: str = "tools/agentx_evolve/schemas/"
    canonical_test_subdirectory: str = "tools/agentx_evolve/tests/"
    runtime_artifact_root: str = ".agentx-init/git/"
    files_created_or_changed: list[str] = field(default_factory=list)
    schemas_created_or_changed: list[str] = field(default_factory=list)
    tests_created_or_changed: list[str] = field(default_factory=list)
    commands_run: list[dict] = field(default_factory=list)
    git_operations_verified: list[str] = field(default_factory=list)
    blocked_git_operations_verified: list[str] = field(default_factory=list)
    branch_rules_verified: list[str] = field(default_factory=list)
    commit_rules_verified: list[str] = field(default_factory=list)
    push_rules_verified: list[str] = field(default_factory=list)
    rollback_revert_rules_verified: list[str] = field(default_factory=list)
    policy_integration_verified: list[str] = field(default_factory=list)
    sandbox_integration_verified: list[str] = field(default_factory=list)
    patch_execution_integration_verified: list[str] = field(default_factory=list)
    promotion_gate_integration_verified: list[str] = field(default_factory=list)
    environment_hardening_verified: list[str] = field(default_factory=list)
    lock_idempotency_verified: list[str] = field(default_factory=list)
    evidence_artifacts: list[str] = field(default_factory=list)
    evidence_hashes: list[str] = field(default_factory=list)
    deviations_from_contract: list[str] = field(default_factory=list)
    unresolved_risks: list[str] = field(default_factory=list)
    final_decision: str = "NOT_DONE"
    def to_dict(self) -> dict:
        return to_dict(self)
```

### Acceptance

```text
existing dataclasses continue to work unchanged
new dataclasses instantiate
to_dict serializes them
IDs are unique enough for local evidence
timestamps are ISO-like UTC strings
no filesystem writes
no imports from LLM/network packages
```

---

## 5.3 `git_command_policy.py` (FUTURE — extends existing `git_policy.py`)

### Purpose

Define structured Git command allowlist entries and enforce policy.

### Current Content (`git_policy.py`)

`GitPolicyEnforcer` uses simple allow_writes flag and substring-based forbidden word check. `GitPolicyRule` has basic fields. This is sufficient for v1 but lacks the structured allowlist entries required by the contract.

### Required Class

```python
class GitCommandPolicyEnforcer:
    def __init__(self, command_policies: list[GitCommandPolicy] | None = None): ...

    def add_command_policy(self, policy: GitCommandPolicy) -> None: ...

    def find_policy(self, operation_name: str) -> GitCommandPolicy | None: ...

    def check_operation_allowed(
        self,
        operation: GitOperation,
        caller_role: str,
    ) -> GitPolicyResult: ...

    def list_allowed_operations(self, caller_role: str) -> list[str]: ...

    def list_blocked_operations(self, caller_role: str) -> list[str]: ...
```

### Required Default Allowlist

Built-in allowlist entries matching the contract's allowed read-only operations:

| Operation | Fixed Args | Roles | Effect |
|---|---|---|---|
| `git_status_short` | `["status", "--short"]` | ORCHESTRATOR, REVIEWER_ASSISTANT, PROMOTION_CHECKER | READ |
| `git_status_porcelain` | `["status", "--porcelain=v1"]` | ORCHESTRATOR, REVIEWER_ASSISTANT | READ |
| `git_diff_name_only` | `["diff", "--no-ext-diff", "--name-only"]` | ORCHESTRATOR, REVIEWER_ASSISTANT | READ |
| `git_diff_stat` | `["diff", "--no-ext-diff", "--stat"]` | ORCHESTRATOR, REVIEWER_ASSISTANT | READ |
| `git_diff_full` | `["diff", "--no-ext-diff"]` | ORCHESTRATOR | READ |
| `git_branch_show_current` | `["branch", "--show-current"]` | ORCHESTRATOR, REVIEWER_ASSISTANT | READ |
| `git_log_oneline` | `["log", "--oneline", "-n", "20"]` | ORCHESTRATOR, REVIEWER_ASSISTANT | READ |
| `git_rev_parse_toplevel` | `["rev-parse", "--show-toplevel"]` | ORCHESTRATOR | READ |
| `git_rev_parse_head` | `["rev-parse", "HEAD"]` | ORCHESTRATOR | READ |
| `git_ls_files` | `["ls-files"]` | ORCHESTRATOR | READ |

### Must Keep

```text
existing GitPolicyEnforcer for backward compatibility
existing forbidden word checks (push, fetch, pull, merge, rebase, reset, clean, cherry-pick, revert)
```
---

## 5.4 `git_command_runner.py` (FUTURE)

### Purpose

Execute Git commands using argument vectors only, with no shell, bounded output, timeouts, and hardened environment.

### Required Class / Functions

```python
@dataclass
class SafeCommandResult:
    argv: list[str]
    exit_code: int
    stdout: str
    stderr: str
    stdout_truncated: bool
    stderr_truncated: bool
    duration_ms: int
    timeout_seconds: int
    failure_class: str | None

def run_git_command_safe(
    argv: list[str],
    cwd: str,
    timeout_seconds: int = 30,
    max_output_bytes: int = 1048576,
    env: dict | None = None,
) -> SafeCommandResult: ...
```

### Required Behavior

```text
accept argument vector only (no shell=True)
enforce timeout
bound stdout/stderr at max_output_bytes
redact secrets from captured output
construct SafeCommandResult with duration, truncation flags, failure_class
raise no exceptions — catch and return FAILED result
```

### Must Not Do

```text
no shell=True
no command string parsing
no raw env passing without filtering
no unbounded output
no network from this module
no Git config mutation
```

---

## 5.5 `git_environment.py` (FUTURE)

### Purpose

Build the hardened Git execution environment and isolated Git config context.

### Required Data Class

```python
@dataclass
class HardenedGitEnvironment:
    env: dict
    config_args: list[str]
    profile_id: str
```

### Required Function

```python
def build_hardened_git_env(
    repo_root: str,
    read_only: bool = True,
) -> HardenedGitEnvironment: ...
```

### Required Environment Variables

```text
GIT_TERMINAL_PROMPT=0
GIT_ASKPASS=
SSH_ASKPASS=
GIT_PAGER=cat
PAGER=cat
GIT_EXTERNAL_DIFF=
GIT_OPTIONAL_LOCKS=0  (for read-only operations)
GIT_CONFIG_NOSYSTEM=1
HOME=<tempdir>/agentx_git_home
XDG_CONFIG_HOME=<tempdir>/agentx_git_config
LC_ALL=C
PATH=<existing PATH>
```

### Required Git Config Arguments

```text
-c core.pager=cat
-c color.ui=false
-c core.quotepath=false
-c commit.gpgsign=false
-c tag.gpgSign=false
-c log.showSignature=false
-c credential.helper=
-c safe.directory=<repo_root>
```

For commands that could trigger hooks, also add:

```text
-c core.hooksPath=<tempdir>/agentx_git_empty_hooks
```

Create the empty hooks directory if it does not exist.

### Rules

```text
system and user Git config must not affect command behavior
include.path and includeIf must not introduce unapproved behavior
HOME must be isolated to prevent .gitconfig, .netrc, .ssh/config leakage
if config isolation cannot be proven, block all mutating operations
```
---

## 5.6 `git_ref_validator.py` (FUTURE)

### Purpose

Validate branches, refs, tags, remotes, and protected namespaces before Git mutation.

### Required Function

```python
def validate_ref(
    raw_ref: str,
    repo_root: str,
    ref_kind: str = "BRANCH",
) -> GitRefValidationResult: ...
```

### Required Logic

```text
reject empty names
reject names beginning with `-`
reject names containing `..`, `@{`, ASCII control characters, `.lock` suffix
reject names ending with `/`, `.`, or `.lock`
reject names with consecutive slashes
reject names matching protected branch patterns:
  main, master, release, production, stable
  refs/heads/main, refs/heads/master, refs/heads/release/*
  refs/tags/*, refs/remotes/*
reject remote-tracking refs as local mutation targets
reject hash-like strings used as branch names
run git check-ref-format --branch <name> and record result
```

### Protected Branch Detection

```python
PROTECTED_BRANCHES = frozenset({"main", "master", "release", "production", "stable"})
PROTECTED_REF_PATTERNS = [
    re.compile(r"^refs/heads/main$"),
    re.compile(r"^refs/heads/master$"),
    re.compile(r"^refs/heads/release/"),
    re.compile(r"^refs/tags/"),
    re.compile(r"^refs/remotes/"),
]
```

---

## 5.7 `git_status.py` (FUTURE)

### Purpose

Read-only Git status operation with hardened environment.

### Required Function

```python
def run_git_status_readonly(
    repo_root: str,
    porcelain: bool = True,
) -> GitOperationResult: ...
```

### Required Behavior

```text
use --no-pager
use --porcelain=v1 when porcelain=True
use --short when porcelain=False
use GIT_OPTIONAL_LOCKS=0
use hardened environment from git_environment.py
bounded output
never writes index or source state
returns GitOperationResult with status=SUCCESS or FAILED
evidence is written by caller
```

---

## 5.8 `git_diff.py` (FUTURE)

### Purpose

Read-only Git diff operations with hardened environment.

### Required Functions

```python
def run_git_diff_readonly(
    repo_root: str,
    target: str = "HEAD",
    mode: str = "full",
) -> GitOperationResult: ...

def run_git_diff_name_only_readonly(
    repo_root: str,
    target: str = "HEAD",
) -> GitOperationResult: ...

def run_git_diff_stat_readonly(
    repo_root: str,
    target: str = "HEAD",
) -> GitOperationResult: ...
```

### Required Behavior

```text
use --no-pager
use --no-ext-diff
use --no-textconv
use --name-only or --stat when mode requests it
bounded output
redacted output before evidence
no index mutation
```

---

## 5.9 `git_mutation_gate.py` (FUTURE)

### Purpose

Verify all required authorities before a Git mutation may proceed.

### Required Class

```python
@dataclass
class MutationGateResult:
    allowed: bool = False
    dry_run: bool = True
    missing_authorities: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    policy_decision_id: str = ""
    sandbox_decision_id: str = ""
    patch_evidence_valid: bool = False
    stage_evidence_valid: bool = False
    commit_evidence_valid: bool = False
    governance_valid: bool = False
    human_approval_valid: bool = False
    promotion_gate_valid: bool = False
    lock_acquired: bool = False
    idempotency_conflict: bool = False
    pre_state_match: bool = False
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

class MutationGate:
    def __init__(self, repo_root: str): ...

    def check_mutation_allowed(
        self,
        request: GitMutationRequest,
        caller_role: str,
    ) -> MutationGateResult: ...
```

### Required Check Order

```text
1. caller role not UNKNOWN_CALLER
2. requested_effect is a known mutation type
3. policy decision exists and allows
4. sandbox decision exists and allows
5. patch evidence present for STAGE/COMMIT
6. stage evidence present for COMMIT
7. commit evidence present for PUSH
8. governance decision present for BRANCH/COMMIT/REVERT if required
9. human approval present if required
10. promotion gate present for PUSH
11. mutation lock acquired
12. idempotency key does not conflict
13. pre-state HEAD matches expected base commit
```

If any check fails, the result must list `missing_authorities` and `failed_checks`.

---

## 5.10 `git_stage.py` (FUTURE — blocked by default)

### Purpose

Stage only explicit approved paths. Blocked by default unless all authorities approve.

### Required Function

```python
def stage_approved_paths(
    request: GitStageRequest,
    caller_role: str,
) -> GitOperationResult: ...
```

### Required Behavior

```text
run mutation gate first
if not allowed, return BLOCKED result
if dry_run, return DRY_RUN result without executing
build argv: git add -- <explicit paths> (no wildcards, no --all, no -A)
use hardened environment
acquire mutation lock
capture pre-state snapshot
execute add
capture post-state snapshot
write stage evidence
release lock
```

### Must Never

```text
allow git add .
allow git add -A
allow git add --all
allow path globs
allow `--` omission
allow staging without patch evidence
```

---

## 5.11 `git_commit.py` (FUTURE — blocked by default)

### Purpose

Commit only approved staged changes. Blocked by default unless all authorities approve.

### Required Function

```python
def commit_approved_changes(
    request: GitMutationRequest,
    caller_role: str,
) -> GitOperationResult: ...
```

### Required Behavior

```text
run mutation gate first
if not allowed, return BLOCKED result
if dry_run, return DRY_RUN result without executing
verify staged state matches approved evidence
build argv: git commit --no-gpg-sign --no-verify -m <approved message>
use --no-gpg-sign and --no-verify
hardened environment with hooksPath isolated
acquire mutation lock
capture pre-state snapshot
execute commit
capture post-state snapshot (new commit hash)
write commit evidence
release lock
```

### Must Not

```text
allow editor invocation
allow GPG signing (unless explicit future policy)
allow hook execution
allow empty commit message
allow commit without stage evidence
```

---

## 5.12 `git_branch.py` (FUTURE — blocked by default)

### Purpose

Create only approved non-protected branches. Blocked by default.

### Required Function

```python
def create_approved_branch(
    request: GitBranchRequest,
    caller_role: str,
) -> GitOperationResult: ...
```

### Required Behavior

```text
validate ref first
if protected branch, block
build argv: git branch <validated-name> <base-commit>
acquire mutation lock
execute
release lock
write evidence
```

---

## 5.13 `git_revert.py` (FUTURE — blocked by default)

### Purpose

Prepare revert plans and block actual revert unless approved.

### Required Function

```python
def revert_approved_commit(
    request: GitRevertRequest,
    caller_role: str,
) -> GitOperationResult: ...
```

### Required Behavior

```text
dry-run by default
inspect target commit
prepare revert plan (diff stat, files affected, conflicts expected)
block actual revert unless governance + human approval present
use git revert --no-edit <commit>
never use git reset for rollback
```

---

## 5.14 `git_push.py` (FUTURE — blocked by default)

### Purpose

Block push by default. Require Promotion Gate approval.

### Required Function

```python
def push_approved_commit(
    request: GitPushRequest,
    caller_role: str,
) -> GitOperationResult: ...
```

### Required Behavior

```text
block by default unless promotion gate approves
verify commit evidence exists
verify promotion_gate_id is present
verify remote is allowlisted
verify refspec is allowlisted
block force push always
build argv: git push <remote> <refspec>
use hardened environment with credential prompts disabled
```

---

## 5.15 `git_locks.py` (FUTURE)

### Purpose

Serialize mutation operations with file-based locking.

### Required Class

```python
class GitMutationLock:
    def __init__(self, repo_root: str, timeout_seconds: int = 30): ...

    def acquire(self, operation_id: str) -> GitLockRecord: ...

    def release(self, lock_record: GitLockRecord) -> GitLockRecord: ...

    def is_locked(self) -> bool: ...

    def is_stale(self) -> bool: ...

    def break_stale(self, operation_id: str) -> GitLockRecord: ...
```

### Required Behavior

```text
lock file at .agentx-init/git/locks/git_mutation.lock
acquire atomically (mkdir or O_EXCL)
timeout after timeout_seconds
stale lock detection (process liveness, age)
always write lock record evidence
release always evidenced even on failure
```

---

## 5.16 `git_evidence.py` (FUTURE)

### Purpose

Write append-only Git operation evidence.

### Required Functions

```python
def write_git_operation_evidence(
    result: GitOperationResult,
    repo_root: str,
) -> dict: ...

def write_git_blocked_evidence(
    result: GitOperationResult,
    repo_root: str,
) -> dict: ...

def write_git_latest_result(
    result: GitOperationResult,
    repo_root: str,
) -> dict: ...

def write_git_evidence_manifest(
    artifacts: list[str],
    hashes: list[dict],
    repo_root: str,
    validated_commit: str,
) -> dict: ...

def write_git_completion_record(
    record: GitCompletionRecord,
    repo_root: str,
) -> dict: ...
```

### Required Artifacts

```text
.agentx-init/git/git_operation_history.jsonl
.agentx-init/git/git_result_history.jsonl
.agentx-init/git/git_blocked_history.jsonl
.agentx-init/git/git_mutation_request_history.jsonl
.agentx-init/git/git_commit_evidence_history.jsonl
.agentx-init/git/git_latest_operation.json
.agentx-init/git/git_latest_result.json
.agentx-init/git/git_evidence_manifest.json
.agentx-init/git/git_review_report.json
.agentx-init/git/git_integration_completion_record.json
```

### Rules

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
SHA-256 hashes for final evidence artifacts
no raw secrets in evidence
no unbounded command output in evidence
blocked operations are evidence events
invalid operations are evidence events
```

---

## 5.17 `git_dispatcher.py` (FUTURE)

### Purpose

Enforce the full 29-step operation pipeline before any Git helper runs.

### Required Function

```python
def dispatch_git_operation(
    operation: GitOperation,
    caller_role: str,
    repo_root: str,
    context: dict | None = None,
) -> GitOperationResult: ...
```

### Required Pipeline (matching contract section 35)

```text
1.  Receive raw Git operation request.
2.  Normalize caller context.
3.  Build GitOperation object.
4.  Validate GitOperation schema.
5.  Resolve and validate repo root through Security Sandbox.
6.  Load Git command policy.
7.  Verify operation exists in allowlist.
8.  Check caller role.
9.  Check requested effect.
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

For read-only operations, skip steps 12–19 and 28.

---

# 6. Schema Implementation Spec

## 6.1 Existing Schemas

### `git_operation.schema.json` (EXISTS)

Required fields: `operation` minimum. Properties match `GitOperation` dataclass fields. Draft 2020-12. No changes required.

### `git_result.schema.json` (EXISTS)

Required fields: `operation`, `status`. Properties match `GitResult` dataclass fields. Draft 2020-12. No changes required.

## 6.2 Future Schemas

Create each as JSON Schema Draft 2020-12. Each schema must require `schema_version`, `schema_id`, and fields specific to the data type.

### `git_command_policy.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, policy_id, operation_name, command,
fixed_args, allowed_dynamic_args, allowed_roles, effect,
requires_policy, requires_sandbox, requires_patch_evidence,
requires_stage_evidence, requires_commit_evidence,
requires_human_approval, requires_governance, requires_promotion_gate,
mutates_repository, writes_index, writes_history, uses_remote,
allows_hooks, allows_external_diff, allows_pager, enabled,
warnings, errors
```

Allowed effects: `READ`, `STAGE`, `COMMIT`, `BRANCH`, `REVERT`, `PUSH`.

### `git_command_result.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, command_result_id, operation_id, timestamp,
source_component, operation_name, command_template_id, argv_redacted,
argv_sha256, cwd, environment_profile_id, exit_code, status,
stdout_summary, stderr_summary, stdout_truncated, stderr_truncated,
duration_ms, timeout_seconds, artifact_refs, evidence_refs,
failure_class, warnings, errors
```

Allowed statuses: `SUCCESS`, `PARTIAL`, `BLOCKED`, `FAILED`, `INVALID`.

### `git_status_diff_result.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, result_id, operation_id, timestamp,
source_component, operation_name, status, exit_code, repo_root,
current_branch, head_commit, changed_files, diff_summary,
bounded_output, output_truncated, artifact_refs, evidence_refs,
failure_class, warnings, errors
```

### `git_operation_result.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, operation_result_id, operation_id, timestamp,
source_component, operation_name, requested_effect, status, exit_code,
repo_root, pre_state_snapshot_id, post_state_snapshot_id,
command_result_ids, artifact_refs, evidence_refs,
failure_class, warnings, errors
```

### `git_mutation_request.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, mutation_request_id, timestamp,
source_component, operation_name, requested_effect, repo_root,
target_branch, base_commit, target_commit, paths,
patch_session_id, patch_evidence_id, stage_evidence_id,
commit_evidence_id, policy_decision_id, sandbox_decision_id,
governance_decision_id, human_approval_id, promotion_gate_id,
commit_message, dry_run, idempotency_key, warnings, errors
```

Allowed effects: `STAGE`, `COMMIT`, `BRANCH`, `REVERT`, `PUSH`.

### `git_branch_request.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, branch_request_id, timestamp,
source_component, repo_root, base_branch, base_commit,
new_branch, policy_decision_id, governance_decision_id,
human_approval_id, dry_run, warnings, errors
```

### `git_ref_validation_result.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, ref_validation_id, timestamp,
source_component, repo_root, ref_kind, raw_ref,
normalized_ref, is_valid, is_protected, is_remote_tracking,
is_symbolic, is_detached_head, check_ref_format_status,
failure_class, warnings, errors
```

Allowed ref_kinds: `BRANCH`, `TAG`, `REMOTE`, `REFSPEC`, `COMMIT`.

### `git_stage_request.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, stage_request_id, timestamp,
source_component, repo_root, base_commit, paths,
patch_session_id, patch_evidence_id, approved_path_set_hash,
policy_decision_id, sandbox_decision_id, dry_run,
warnings, errors
```

### `git_commit_evidence.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, commit_evidence_id, timestamp,
source_component, repo_root, branch_name, base_commit,
new_commit, operation_id, mutation_request_id,
stage_evidence_id, patch_session_id, patch_evidence_id,
staged_paths, staged_path_set_hash, diff_stat,
commit_message, policy_decision_id, sandbox_decision_id,
governance_decision_id, human_approval_id, promotion_gate_id,
secret_scan_status, status, artifact_refs, evidence_refs,
sha256_refs, warnings, errors
```

Allowed secret_scan_status: `PASS`, `BLOCKED`, `NOT_AVAILABLE`.

### `git_push_request.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, push_request_id, timestamp,
source_component, repo_root, remote_name, remote_url_redacted,
source_ref, target_ref, commit_evidence_id, review_report_id,
completion_record_id, policy_decision_id, promotion_gate_id,
human_approval_id, dry_run, warnings, errors
```

### `git_revert_request.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, revert_request_id, timestamp,
source_component, repo_root, current_branch, head_commit,
target_commit, revert_plan_id, policy_decision_id,
governance_decision_id, human_approval_id, dry_run,
warnings, errors
```

### `git_lock_record.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, lock_record_id, timestamp,
source_component, repo_root, lock_path, operation_id,
mutation_request_id, lock_status, holder_id, timeout_seconds,
pre_head_commit, pre_index_hash, pre_worktree_hash,
warnings, errors
```

Allowed lock_status: `ACQUIRED`, `RELEASED`, `BLOCKED`, `TIMEOUT`, `STALE_REJECTED`.

### `git_audit_event.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, event_id, timestamp,
source_component, event_type, operation_id, caller_role,
status, failure_class, summary, warnings, errors
```

### `git_evidence_manifest.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, component_id, validated_commit,
validated_at, commands, evidence_files, evidence_file_hashes,
runtime_artifacts, known_expected_runtime_artifacts,
deviation_register, source_mutation_status, final_decision
```

Allowed final_decision: `DONE`, `NOT_DONE`.

### `git_review_report.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, review_id, component_id,
reviewed_commit, reviewed_at, commands_run, coverage_statuses,
blockers, high_issues, deviation_register, final_verdict
```

### `git_completion_record.schema.json` (FUTURE)

Required fields:

```text
schema_version, schema_id, component_id, status,
validated_commit, validated_at,
canonical_subdirectory, canonical_schema_subdirectory,
canonical_test_subdirectory, runtime_artifact_root,
files_created_or_changed, schemas_created_or_changed,
tests_created_or_changed, commands_run,
git_operations_verified, blocked_git_operations_verified,
branch_rules_verified, commit_rules_verified,
push_rules_verified, rollback_revert_rules_verified,
policy_integration_verified, sandbox_integration_verified,
patch_execution_integration_verified,
promotion_gate_integration_verified,
environment_hardening_verified, lock_idempotency_verified,
evidence_artifacts, evidence_hashes,
deviations_from_contract, unresolved_risks, final_decision
```

---

# 7. Authority Precedence Implementation

Every Git operation must follow this precedence:

```text
1. INVALID (schema failure, unknown operation)
2. BLOCKED (policy denial, sandbox denial, forbidden command)
3. NEEDS_HUMAN_APPROVAL (approval-required operation without approval)
4. NEEDS_GOVERNANCE (governance-required operation without governance)
5. NEEDS_PROMOTION_GATE (push without promotion gate)
6. DRY_RUN_ONLY (all authorities present but dry_run=true)
7. ALLOW (all authorities present and dry_run=false)
```

A later ALLOW can never override an earlier BLOCK.

---

# 8. Dependency Gates and Restricted Mode

## 8.1 Dependency Gate Rules

```text
If Policy / Capability Registry is unavailable -> read-only known-role inspection may use restrictive fallback; all mutation blocks.
If Security Sandbox is unavailable -> all repo/path/command operations block, including read-only Git.
If Governed Patch Execution is unavailable -> stage and commit operations block.
If Human Review is unavailable -> operations requiring human approval block.
If Promotion / Release Gate is unavailable -> push, release tag, and protected-branch update block.
If Failure Taxonomy is unavailable -> use UNKNOWN_GIT_FAILURE while still blocking unsafe behavior.
If evidence writing is unavailable -> all Git operations block except pure schema validation tests.
```

## 8.2 Restricted Mode

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

---

# 9. Failure Classes

Use these standardized failure classes (from contract section 33):

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

Every BLOCKED/FAILED result must include `failure_class`.

---

# 10. Coding Constraints for LLM Implementer

```text
do not implement model adapter
do not implement MCP
do not implement patch applier
do not implement network fetch
do not implement background daemon
do not modify L0
do not use shell helpers except subprocess
do not add hosted dependencies
do not add non-standard dependencies unless already present
standard library first
jsonschema only if already used
dataclasses over Pydantic unless project standard says otherwise
pytest tests
schema files as plain JSON
```

---

# 11. Definition of Done

This implementation is done only when:

```text
all target files exist (16 .py files, 17 schemas, 20+ test files)
all existing files continue to pass tests
command allowlist exists with at least 10 read-only entries
read-only Git operations work for approved roles
write operations block without approvals
destructive commands (reset, clean, rebase, merge, force-push) block
branch validation passes
commit evidence rules pass
push gate rules pass
hook/external-diff/pager safety passes
environment hardening passes
lock/idempotency rules pass
audit/evidence artifacts are written
evidence manifest and hashes exist
compileall passes
pytest passes
schema validation passes
source mutation check passes
completion record exists
```

---

# 12. OpenCode Borrowing Table for Implementation

| OpenCode primitive/concept | Agent_X implementation | Borrowing limit |
|---|---|---|
| `shell` git status | `git_status` (read-only) | Allowlisted command, bounded output, no mutation. |
| `shell` git diff | `git_diff` / `git_diff_name_only` / `git_diff_stat` | No `--no-ext-diff` yet, no bounded output enforcement yet. |
| `shell` git add | `git_stage_approved` (blocked by default) | Requires patch evidence + sandbox + policy. |
| `shell` git commit | `git_commit_approved` (blocked by default) | Requires stage evidence + governance/human approval. |
| `shell` git push | `git_push_approved` (blocked by default) | Requires promotion gate + commit evidence. |
| `shell` git branch | `git_create_branch_approved` (blocked by default) | Branch validation + governance required. |
| invalid tool handling | `GitOperationResult(status='BLOCKED')` with failure_class | Fail closed with evidence. |

---

# 13. Manual Validation Commands

From repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_git_integration_schemas.py
git status --short
```

No command may require GPU, network, hosted provider, or LLM.

---

# 14. Completion Evidence

After implementation, write:

```text
.agentx-init/git/git_integration_completion_record.json
```

Required fields match `GitCompletionRecord` dataclass above.

---

# 15. Final Implementation Sequence for Coding Agent

```text
1.  Extend git_models.py with all FUTURE dataclasses.
2.  Create all 15 FUTURE schemas.
3.  Create git_command_policy.py (extend git_policy.py).
4.  Create git_environment.py.
5.  Create git_command_runner.py.
6.  Create git_ref_validator.py.
7.  Create git_status.py.
8.  Create git_diff.py.
9.  Create git_mutation_gate.py.
10. Create git_stage.py.
11. Create git_commit.py.
12. Create git_branch.py.
13. Create git_revert.py.
14. Create git_push.py.
15. Create git_locks.py.
16. Create git_evidence.py.
17. Create git_dispatcher.py.
18. Update __init__.py exports.
19. Create or extend tests.
20. Run compileall.
21. Run pytest.
22. Fix failures without weakening safety.
23. Generate completion record.
24. Report final evidence.
```

---

# 16. Coding LLM Handoff Checklist

```text
[ ] The target repository is Agent_X.
[ ] The existing implementation is under tools/agentx_evolve/git/.
[ ] 4 .py files exist (__init__.py, git_models.py, git_operations.py, git_policy.py).
[ ] 2 schemas exist (git_operation.schema.json, git_result.schema.json).
[ ] 3 test files exist (test_git_integration.py, test_git_tools.py, test_git_evidence.py).
[ ] 14 new .py files must be created (see implementation order).
[ ] 15 new schemas must be created.
[ ] 17+ new test files must be created.
[ ] git_policy.py should be renamed/extended to git_command_policy.py.
[ ] git_operations.py should be kept for backward compatibility; new operations use git_dispatcher.py.
[ ] OpenCode is used only as a design reference.
[ ] No OpenCode source code is copied.
[ ] The implementation language is Python.
[ ] Runtime artifacts go under .agentx-init/git/.
[ ] Git write operations are blocked by default.
[ ] Shell is not used directly (subprocess with argument vectors only).
[ ] Tests must run without GPU, network, hosted model, Bun, or Node.
[ ] Environment hardening (GIT_TERMINAL_PROMPT, GIT_PAGER, HOME isolation) is REQUIRED.
[ ] evidence writing is REQUIRED for all operations, including blocked ones.
[ ] All 17 schemas must validate their respective dataclass structures.
```

---

# 17. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It specifies every implementation file for the Git Integration Layer, documents what already exists, defines all 17 schemas with exact required fields, provides file-by-file implementation instructions with Required/Behavior/Rules sections, establishes implementation order, sets coding constraints, defines a precise Definition of Done, and includes a coding-LLM handoff checklist. roadmap_layer is corrected to 6 (Phase A). The spec is ready to hand to a coding LLM.
```
