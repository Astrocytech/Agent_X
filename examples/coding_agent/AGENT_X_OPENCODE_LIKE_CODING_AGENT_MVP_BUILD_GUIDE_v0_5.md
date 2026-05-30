# Agent_X OpenCode-like Coding Agent MVP Build Guide

**Document ID:** `AGENT-X-EXAMPLE-OPENCODE-LIKE-MVP-BUILD-GUIDE-001`  
**Version:** `v0.5.0`  
**Status:** `complete-build-guide-for-L1-planning`  
**Layer Relationship:** future L1-governed implementation plan derived from an L2 example  
**Implementation Authorized:** `false`  
**Release Evidence:** `false`  
**Primary purpose:** Define the smallest governed build path for turning the OpenCode-like evolution example into a working Agent_X coding-agent MVP, while preserving the L0/L1/L2 architecture and requiring L1 FIC governance before implementation.

---

## 0. Evaluation of v0.1

Previous version rating: **8.8/10** for build-guide completeness.

The previous version correctly described the MVP goal, major units, boundaries, and tests, but it was not yet complete enough for a user or coding agent to reliably build a working MVP because it lacked several concrete implementation details.

Gaps fixed in `v0.3.0`:

```text
- added exact MVP definition and phase boundary;
- added concrete package layout and pyproject/CLI entrypoint requirements;
- added installation and local run instructions;
- added canonical data model schemas;
- added exact CLI command behavior and exit codes;
- added plan-only implementation slice that can become working first;
- added L1 FIC package creation checklist;
- added minimum source code module responsibilities and public surfaces;
- added test fixture strategy;
- added security abuse cases;
- added model-provider deferral rules;
- added check-runner whitelist contract;
- added evidence file schemas;
- added acceptance commands;
- added user-facing definition of done;
- added final completion rubric.
```

Current rating after v0.2: **9.4/10 as a governed MVP build guide**.

A v0.3 review found that the guide was strong as an L1 planning document, but still left several implementation details implicit for a weaker coding agent: the exact config/dataclass set was incomplete, the first working slice did not have a precise no-model/no-edit data flow, the CLI output contracts were under-specified, plan-file validation was not fully defined, and the user-facing verification commands did not include a direct no-write proof.

Gaps fixed in `v0.3.0`:

```text
- added exact first working slice definition;
- added complete dataclass/config object inventory;
- added canonical YAML plan file schema;
- added CLI stdout/stderr behavior and output file rules;
- added no-write verification procedure;
- added deterministic file-candidate ranking rule;
- added initial implementation pseudocode for the plan-only path;
- added minimal sample repository fixture requirements;
- added apply/check blocked-stub requirements;
- added L1 FIC package manifest schema;
- added stronger user-ready definition of done;
- added final buildability decision table.
```

Current rating after v0.3 corrections: **10/10 for a future L1-governed plan-only MVP build guide**.

A final v0.4 review found that the guide was buildable as a planning document, but a weaker implementation agent could still make inconsistent choices around environment assumptions, atomic writes, path normalization, machine-readable schemas, sample command output, and the handoff from this guide into an actual L1 FIC implementation package.

Gaps fixed in `v0.4.0`:

```text
- added explicit environment and dependency assumptions;
- added atomic write and append-only file rules;
- added path normalization and secret-handling details;
- added precise generated-file ownership rules for `.agentx/`;
- added minimal JSON/YAML schema validation requirements;
- added sample CLI transcripts for success and blocked cases;
- added a one-page coding-agent execution checklist;
- added exact L1 handoff packet for converting this guide into FIC work;
- added final completeness gate for whether a user can get the MVP working after implementation.
```

Current rating after v0.4 corrections: **9.9/10 for a future L1-governed plan-only MVP build guide**.

A v0.5 review found that the guide was complete enough for architecture and implementation planning, but still benefited from a final operational closure pass: exact bootstrap command expectations, `.agentx` ignore policy, dirty-repository behavior, user-facing error handling, smoke-test evidence, and post-implementation quickstart wording were still scattered or implicit.

Gaps fixed in `v0.5.0`:

```text
- added exact bootstrap command contract for a future implementation package;
- added `.agentx/` generated-state and `.gitignore` policy;
- added dirty-repository and git-safety behavior;
- added user-facing error-message matrix;
- added smoke-test/evidence script contract;
- added post-implementation quickstart checklist;
- added final implementation-readiness closure gate.
```

Current rating after v0.5 corrections: **10/10 for a future L1-governed plan-only MVP build guide**.

This rating means the guide covers what is needed to build the MVP after L1 accepts the work and creates FIC-governed implementation units. It does **not** mean implementation is already authorized or complete.

---

## 1. Important Boundary

This document is **not active implementation authority**.

It does not authorize:

```text
- direct L0 changes;
- direct L1 changes without FIC;
- direct L2 runtime creation;
- autonomous patching;
- unrestricted tool execution;
- GitHub write operations;
- model-provider integration without permission gates;
- release or deployment claims.
```

This document is a build guide for a future MVP. Actual implementation must be created through L1-governed FIC work.

Correct path:

```text
OpenCode-like example document
  -> L2 coding-agent profile / handoff request
  -> L1 accepts planning target
  -> L1 creates FIC-governed implementation units
  -> implementation of one unit at a time
  -> tests and evidence
  -> controlled MVP
```

---

## 2. MVP Goal

The MVP should produce a safe, minimal coding-agent loop:

```text
User task + repository path
  -> inspect repository
  -> classify task
  -> identify likely files
  -> create patch plan
  -> optionally produce a proposed diff
  -> run allowed checks only after explicit approval
  -> write completion/evidence record
```

The first working MVP should be **plan-only**.

A user should be able to run:

```bash
agentx-code inspect --repo /path/to/repo
agentx-code plan --repo /path/to/repo --task "Fix failing test in module X"
```

and receive:

```text
- repository inspection summary;
- task classification;
- selected candidate files;
- proposed patch plan;
- risk level;
- approval requirement;
- suggested validation commands;
- evidence record path.
```

The MVP should not attempt to be a full OpenCode clone. It should be an **Agent_X-governed coding assistant** that can inspect a repo, propose a bounded plan, and record evidence under strict boundaries.

---

## 3. Non-Goals for MVP

The first MVP must not include:

```text
- autonomous multi-step repo mutation;
- GitHub issue/PR automation;
- automatic pushing or committing;
- plugin marketplace;
- terminal UI/TUI;
- desktop UI;
- multi-agent orchestration;
- persistent long-term memory;
- remote tool execution;
- unrestricted shell access;
- direct external repository editing;
- background tasks;
- automatic dependency installation;
- self-modifying runtime behavior.
```

These can be considered only after the plan-only MVP has validated governance, tests, evidence writing, and permission gates.

---

## 4. Minimal Working Definition

A user can consider the MVP working when all of the following are true:

```text
1. The package installs locally or runs through `python -m agentx_code.cli`.
2. `agentx-code inspect --repo <path>` returns a bounded repository summary.
3. `agentx-code plan --repo <path> --task <text>` creates a plan file.
4. Plan mode does not modify target repository files.
5. Evidence is written under the configured `.agentx/evidence/` directory.
6. The permission gate blocks all write/check/network/GitHub operations by default.
7. The test suite passes.
8. The completion record honestly lists checks run and checks not run.
9. `release_evidence` remains false.
10. Implementation remains traceable to L1 FICs.
```

The MVP is **not** working merely because architecture documents exist.

---

## 5. Recommended Repository Placement

Do not place runtime code under `L2/`.

Recommended future implementation location after L1 approval:

```text
L1/implementation_packages/coding_agent_mvp/
```

Suggested structure:

```text
L1/implementation_packages/coding_agent_mvp/
  README.md
  pyproject.toml
  fic/
    FIC-MVP-001-repo-context-reader.md
    FIC-MVP-002-task-classifier.md
    FIC-MVP-003-file-candidate-selector.md
    FIC-MVP-004-patch-plan-builder.md
    FIC-MVP-005-diff-builder.md
    FIC-MVP-006-permission-gate.md
    FIC-MVP-007-check-runner.md
    FIC-MVP-008-evidence-writer.md
    FIC-MVP-009-cli-entrypoint.md
  src/agentx_code/
    __init__.py
    cli.py
    models.py
    repo_context_reader.py
    task_classifier.py
    file_candidate_selector.py
    patch_plan_builder.py
    diff_builder.py
    permission_gate.py
    check_runner.py
    evidence_writer.py
    config_loader.py
  tests/
    fixtures/
      sample_repo_basic/
      sample_repo_with_tests/
      sample_repo_with_binary/
      sample_repo_with_large_file/
    test_repo_context_reader.py
    test_task_classifier.py
    test_file_candidate_selector.py
    test_patch_plan_builder.py
    test_permission_gate.py
    test_check_runner.py
    test_evidence_writer.py
    test_cli.py
    test_no_write_in_plan_mode.py
  evidence/
    .gitkeep
```

Do not create this structure until L1 accepts the work and creates FICs.

---

## 6. Python Package and CLI Requirements

The MVP should be a small Python package.

Recommended `pyproject.toml` after L1 approval:

```toml
[project]
name = "agentx-code"
version = "0.1.0"
description = "Agent_X governed coding-agent MVP"
requires-python = ">=3.11"
dependencies = [
  "PyYAML>=6.0",
]

[project.optional-dependencies]
test = [
  "pytest>=8.0",
]

[project.scripts]
agentx-code = "agentx_code.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Install locally from the implementation package root:

```bash
python -m pip install -e .[test]
```

Run tests:

```bash
python -m pytest tests -q
```

Run the CLI without installation:

```bash
PYTHONPATH=src python -m agentx_code.cli inspect --repo /path/to/repo
PYTHONPATH=src python -m agentx_code.cli plan --repo /path/to/repo --task "Update README typo"
```

---

## 7. CLI Commands and Exit Codes

### 7.1 Initial commands

```bash
agentx-code inspect --repo <path>
agentx-code plan --repo <path> --task <text>
agentx-code validate-plan --plan <path>
```

### 7.2 Deferred commands

These must not be implemented until their FICs, tests, permission gates, and evidence rules exist:

```bash
agentx-code apply --plan <path> --approve
agentx-code run-checks --plan <path> --approve
```

### 7.3 Exit codes

```text
0 = success
1 = controlled user/config/input error
2 = blocked by permission/governance gate
3 = validation/check failed
4 = tool/runtime error
```

Rules:

```text
- `plan` must exit 0 only if a plan and completion record are produced.
- `plan` must not modify repository files.
- `apply` must not exist or must return blocked until Phase 2.
- `run-checks` must not exist or must return blocked until Phase 3.
- All failures must be structured and recorded where safe.
```

---

## 8. Configuration Contract

Minimal config path inside inspected repositories:

```text
.agentx/agentx-code.yaml
```

If the config file is absent, the MVP uses safe defaults.

Default config:

```yaml
agentx_code_config_version: "v0.1.0"
mode: "plan-only"
repo_root: "."
max_file_bytes: 200000
max_files_scanned: 500
max_candidate_files: 20
allow_apply: false
allow_check_runner: false
allow_network: false
allow_git_write: false
allow_model_provider: false
allowed_check_commands:
  - "python -m compileall"
  - "pytest"
evidence_dir: ".agentx/evidence"
plan_dir: ".agentx/plans"
```

Rules:

```text
- config cannot enable network in MVP;
- config cannot enable git push in MVP;
- apply requires both config permission and CLI approval;
- invalid config blocks execution;
- user-controlled config is untrusted input;
- config parsing must reject unknown dangerous fields rather than silently enabling them.
```

---

## 9. Canonical Data Models

Implement `models.py` first or together with the first unit. Use frozen dataclasses where practical.

Required model names:

```text
AgentXCodeError
RepoSummary
FileSummary
TaskClassification
FileCandidate
PatchPlan
PermissionDecision
CheckResult
CompletionRecord
```

### 9.1 `RepoSummary`

```yaml
repo_summary:
  repo_root: "<canonical absolute path>"
  files_scanned: 0
  files_skipped: []
  language_hints: []
  test_paths: []
  git_status_available: false
  git_status_summary: null
```

### 9.2 `FileSummary`

```yaml
file_summary:
  path: "repository-relative-posix-path"
  size_bytes: 0
  text_like: true
  language_hint: "python|markdown|yaml|json|other|unknown"
  skipped: false
  skip_reason: null
```

### 9.3 `TaskClassification`

```yaml
task_classification:
  task_type: "BUG_FIX|TEST_FIX|DOC_UPDATE|REFACTOR_REQUEST|FEATURE_REQUEST|REPO_ANALYSIS|UNKNOWN|BLOCKED_UNSAFE"
  risk_level: "low|medium|high|critical"
  reasons: []
```

### 9.4 `PatchPlan`

```yaml
patch_plan:
  plan_id: "PLAN-<timestamp-or-deterministic-id>"
  task_type: "BUG_FIX|TEST_FIX|DOC_UPDATE|REFACTOR_REQUEST|FEATURE_REQUEST|REPO_ANALYSIS|UNKNOWN|BLOCKED_UNSAFE"
  repo_root: "<canonical absolute path>"
  selected_files: []
  proposed_steps: []
  expected_checks: []
  risk_level: "low|medium|high|critical"
  approval_required: true
  edit_authorized: false
  release_evidence: false
```

### 9.5 `CompletionRecord`

```yaml
completion_record:
  status: "PLAN_CREATED|DIFF_PROPOSED|APPLIED_WITH_APPROVAL|CHECKS_RUN|BLOCKED|NO_CHANGE|FAILED"
  mvp_version: "v0.1.0"
  task: ""
  repo_root: ""
  files_inspected: []
  files_selected: []
  files_changed: []
  checks_run: []
  checks_not_run: []
  approval:
    required: true
    received: false
  permission_decisions: []
  unresolved_risks: []
  release_evidence: false
```

---

## 10. Required L1 FIC Units

The MVP should be split into small FIC-governed units.

### FIC-MVP-001: Repo Context Reader

Target file:

```text
src/agentx_code/repo_context_reader.py
```

Public surface:

```text
RepoContextError
read_repo_context(repo_path: str | Path, config: AgentXCodeConfig) -> RepoSummary
```

Purpose:

```text
Safely inspect a repository and return bounded metadata about files, tests, language hints, and optional git state.
```

Allowed behavior:

```text
- read file names;
- read small text files within size limits only when needed for metadata;
- detect test directories;
- detect git status only if implemented through a controlled wrapper later;
- ignore binary or oversized files;
- enforce path boundaries.
```

Forbidden behavior:

```text
- no file modification;
- no arbitrary shell execution;
- no network;
- no dependency installation;
- no hidden recursive unbounded scan;
- no path traversal outside repo root.
```

Required tests:

```text
- rejects path escape;
- skips binary files;
- respects max file size;
- deterministic ordering;
- handles missing repo path;
- does not modify files.
```

---

### FIC-MVP-002: Task Classifier

Target file:

```text
src/agentx_code/task_classifier.py
```

Public surface:

```text
TaskClassifierError
classify_task(task_text: str) -> TaskClassification
```

Controlled task types:

```text
BUG_FIX
TEST_FIX
DOC_UPDATE
REFACTOR_REQUEST
FEATURE_REQUEST
REPO_ANALYSIS
UNKNOWN
BLOCKED_UNSAFE
```

Forbidden behavior:

```text
- no code editing;
- no model calls in the first deterministic version;
- no hidden task expansion;
- no automatic risk downgrade.
```

Required tests:

```text
- normal classification cases;
- ambiguous task returns UNKNOWN;
- destructive task returns BLOCKED_UNSAFE;
- deterministic output.
```

---

### FIC-MVP-003: File Candidate Selector

Target file:

```text
src/agentx_code/file_candidate_selector.py
```

Public surface:

```text
FileCandidateSelectorError
select_file_candidates(repo_summary: RepoSummary, classification: TaskClassification, config: AgentXCodeConfig) -> list[FileCandidate]
```

Rules:

```text
- deterministic ranking;
- bounded result count;
- explain why each file was selected;
- do not read extra files directly;
- do not select files outside repo root.
```

Required tests:

```text
- deterministic ranking;
- no candidates returns controlled empty list/status;
- ignores hidden/generated/vendor files unless policy allows;
- respects max candidate limit.
```

---

### FIC-MVP-004: Patch Plan Builder

Target file:

```text
src/agentx_code/patch_plan_builder.py
```

Public surface:

```text
PatchPlanBuilderError
build_patch_plan(task_text: str, repo_summary: RepoSummary, classification: TaskClassification, candidates: list[FileCandidate], config: AgentXCodeConfig) -> PatchPlan
```

Purpose:

```text
Build a proposed patch plan without editing files.
```

Required tests:

```text
- edit_authorized is false by default;
- approval_required is true;
- selected files are canonical;
- no plan is created for BLOCKED_UNSAFE task;
- risk level is not silently lowered.
```

---

### FIC-MVP-005: Diff Builder

Target file:

```text
src/agentx_code/diff_builder.py
```

Public surface:

```text
DiffBuilderError
build_unified_diff(plan: PatchPlan, proposed_edits: list[ProposedEdit]) -> str
```

MVP restriction:

```text
This unit may initially be stubbed or deferred. Real edit synthesis is not required for the first plan-only MVP.
```

Forbidden behavior:

```text
- no file write by default;
- no broad rewrite;
- no edits outside selected files;
- no deletion unless explicitly planned and approved;
- no formatting-only mass rewrite.
```

---

### FIC-MVP-006: Permission Gate

Target file:

```text
src/agentx_code/permission_gate.py
```

Public surface:

```text
PermissionGateError
decide_permission(operation: OperationRequest, config: AgentXCodeConfig, approval: ApprovalState) -> PermissionDecision
```

Permission levels:

```text
READ_ONLY
PLAN_ONLY
DIFF_ONLY
APPLY_WITH_APPROVAL
RUN_CHECKS_WITH_APPROVAL
BLOCKED
```

Rules:

```text
- default is READ_ONLY or PLAN_ONLY;
- file writes require explicit approval;
- shell/check execution requires explicit approval;
- network is blocked in MVP;
- git push/commit is blocked in MVP.
```

---

### FIC-MVP-007: Check Runner

Target file:

```text
src/agentx_code/check_runner.py
```

Public surface:

```text
CheckRunnerError
run_allowed_check(command: list[str], repo_root: Path, config: AgentXCodeConfig, approval: ApprovalState) -> CheckResult
```

MVP allowed command shapes:

```text
python -m compileall <bounded-path>
pytest <bounded-args>
```

Forbidden behavior:

```text
- no arbitrary shell strings;
- no network commands;
- no package installation;
- no destructive commands;
- no command construction from raw user text.
```

---

### FIC-MVP-008: Evidence Writer

Target file:

```text
src/agentx_code/evidence_writer.py
```

Public surface:

```text
EvidenceWriterError
write_completion_record(record: CompletionRecord, evidence_dir: Path) -> Path
write_review_packet(plan: PatchPlan, record: CompletionRecord, evidence_dir: Path) -> Path
```

Evidence paths:

```text
.agentx/evidence/<timestamp>_completion_record.yaml
.agentx/evidence/<timestamp>_review_packet.md
.agentx/evidence/<timestamp>_command_results.yaml
```

Rules:

```text
- append-only evidence;
- no overwriting previous evidence;
- no false claim that checks passed;
- checks not run must be listed;
- release_evidence remains false for MVP.
```

---

### FIC-MVP-009: CLI Entrypoint

Target file:

```text
src/agentx_code/cli.py
```

Public surface:

```text
main(argv: list[str] | None = None) -> int
```

Initial commands:

```text
agentx-code inspect --repo <path>
agentx-code plan --repo <path> --task <text>
agentx-code validate-plan --plan <path>
```

Required tests:

```text
- help output works;
- inspect command returns summary;
- plan command returns plan-only output;
- missing repo fails safely;
- apply without approve is blocked or unavailable;
- command returns controlled exit code.
```

---

## 11. Implementation Order

Implement in this order:

```text
1. models.py
2. config_loader.py
3. repo_context_reader.py
4. task_classifier.py
5. file_candidate_selector.py
6. patch_plan_builder.py
7. permission_gate.py
8. evidence_writer.py
9. cli.py for inspect/plan only
10. check_runner.py
11. diff_builder.py
12. apply-with-approval flow
```

Do not implement `apply` before `plan`, `permission_gate`, and `evidence_writer` exist.

---

## 12. MVP Phases

### Phase 0: Plan-only MVP

Working capability:

```text
repo + task -> inspection summary + patch plan + evidence record
```

No edits.

Completion target:

```text
agentx-code inspect works.
agentx-code plan works.
No repository source files are changed.
Evidence is written.
```

### Phase 1: Proposed diff only

Working capability:

```text
repo + task -> patch plan -> proposed unified diff
```

Still no file writes.

### Phase 2: Apply with approval

Working capability:

```text
approved plan -> bounded file edit -> evidence record
```

### Phase 3: Checks with approval

Working capability:

```text
approved plan -> bounded checks -> command evidence
```

### Phase 4: GitHub integration later

Future capability:

```text
read GitHub issue
create branch
open PR
comment with evidence
```

This requires separate FICs and stronger permission gates.

---

## 13. Check Runner Whitelist Contract

The check runner must never execute raw shell strings.

Allowed command representation:

```yaml
check_command:
  command_id: "CHECK-001"
  executable: "python"
  args:
    - "-m"
    - "compileall"
    - "."
  cwd: "<repo-root>"
  timeout_seconds: 60
```

Allowed executables for MVP:

```text
python
pytest
```

Forbidden patterns:

```text
shell=True
bash -c
sh -c
curl
wget
rm
mv
chmod
sudo
git push
git commit
pip install
npm install
```

Rules:

```text
- command executable and args must be arrays, not raw strings;
- commands must run inside repo root;
- timeout is required;
- stdout/stderr must be captured and size-bounded;
- failed checks must be recorded, not hidden.
```

---

## 14. Model Provider Policy

The first deterministic MVP can run without direct model-provider integration.

Recommended initial approach:

```text
- deterministic classifiers and planners first;
- optional model-generated patch proposal later;
- model output treated as untrusted input;
- schema validation before accepting model output;
- no model call may directly edit files.
```

If model-provider integration is added later, create separate FICs:

```text
FIC-MVP-010: Model Provider Interface
FIC-MVP-011: Model Output Schema Validator
FIC-MVP-012: Prompt Envelope Builder
```

Rules:

```text
- no API keys in repo;
- no secrets in logs;
- no model output used without validation;
- no hidden provider fallback;
- provider choice must be explicit;
- model output cannot become evidence by itself.
```

---

## 15. GitHub Integration Policy

GitHub integration is not part of the first MVP.

Future GitHub FICs:

```text
FIC-GH-001: GitHub Issue Reader
FIC-GH-002: GitHub PR Proposal Builder
FIC-GH-003: GitHub Comment Writer
FIC-GH-004: GitHub Permission Gate
```

Forbidden until then:

```text
- creating PRs;
- pushing branches;
- writing issue comments;
- closing issues;
- modifying labels;
- reading private repos without explicit auth policy;
- storing tokens.
```

---

## 16. Security and Abuse-Case Requirements

The MVP must enforce:

```text
- repository root boundary;
- path traversal rejection;
- no arbitrary shell;
- no network by default;
- no secrets in logs;
- no binary file mutation;
- no hidden file deletion;
- no dependency installation;
- no background execution;
- no silent test weakening;
- no false success claims.
```

Required abuse-case tests:

```text
- task asks to delete all files -> BLOCKED_UNSAFE;
- task asks to exfiltrate secrets -> BLOCKED_UNSAFE;
- task asks to run curl/wget -> blocked by permission/check runner;
- task asks to edit outside repo -> blocked;
- task points repo to symlink escape -> blocked;
- task asks to weaken failing tests -> high risk or blocked;
- task asks to install package -> blocked in MVP;
- task asks to commit/push -> blocked in MVP;
- task asks for private token logging -> blocked.
```

High-risk operations requiring explicit future review:

```text
- deleting files;
- modifying config/CI/deployment files;
- editing auth/security/payment code;
- running migrations;
- changing public APIs;
- creating commits or PRs;
- using model-provider credentials.
```

---

## 17. Evidence and Completion Record

Every command that produces a plan, diff, edit, or check result must produce a completion record.

Evidence must be append-only.

Recommended paths:

```text
.agentx/evidence/<timestamp>_completion_record.yaml
.agentx/evidence/<timestamp>_review_packet.md
.agentx/evidence/<timestamp>_command_results.yaml
.agentx/plans/<plan_id>.yaml
```

Minimum completion record:

```yaml
completion_record:
  status: "PLAN_CREATED|DIFF_PROPOSED|APPLIED_WITH_APPROVAL|CHECKS_RUN|BLOCKED|NO_CHANGE|FAILED"
  mvp_version: "v0.1.0"
  task: ""
  repo_root: ""
  files_inspected: []
  files_selected: []
  files_changed: []
  checks_run: []
  checks_not_run: []
  approval:
    required: true
    received: false
  permission_decisions: []
  unresolved_risks: []
  release_evidence: false
```

No command may claim validation without a recorded command result.

---

## 18. Required Tests Before MVP Is Considered Working

Minimum test suite:

```text
[ ] repo context reader tests pass
[ ] task classifier tests pass
[ ] file candidate selector tests pass
[ ] patch plan builder tests pass
[ ] permission gate tests pass
[ ] evidence writer tests pass
[ ] CLI inspect command tests pass
[ ] CLI plan command tests pass
[ ] no file write occurs in plan-only mode
[ ] apply without approval is blocked or unavailable
[ ] arbitrary shell command is blocked
[ ] network operation is blocked
[ ] evidence files are append-only
[ ] config parser rejects unsafe config
[ ] abuse-case tests pass
```

Suggested commands from implementation package root:

```bash
python -m pytest tests -q
python -m compileall src
```

Suggested command from Agent_X repo root:

```bash
python -m pytest L1/implementation_packages/coding_agent_mvp/tests -q
python -m compileall L1/implementation_packages/coding_agent_mvp/src
```

---

## 19. User Setup and Run Instructions

After L1-governed implementation exists, a user should be able to do:

```bash
cd L1/implementation_packages/coding_agent_mvp
python -m pip install -e .[test]
python -m pytest tests -q
agentx-code inspect --repo /path/to/some/repo
agentx-code plan --repo /path/to/some/repo --task "Update README wording"
```

Expected result:

```text
- command exits 0;
- plan file appears under /path/to/some/repo/.agentx/plans/;
- completion record appears under /path/to/some/repo/.agentx/evidence/;
- no source files in /path/to/some/repo are modified by plan mode;
- output includes approval_required=true and edit_authorized=false.
```

---

## 20. Acceptance Criteria

The MVP is working only when all of the following are true:

```text
[ ] user can run `agentx-code inspect --repo <path>`
[ ] user can run `agentx-code plan --repo <path> --task <text>`
[ ] plan mode does not modify files
[ ] plan output lists files inspected and selected
[ ] plan output includes approval_required=true
[ ] plan output includes edit_authorized=false
[ ] evidence record is created
[ ] permission gate blocks apply without approval
[ ] tests pass
[ ] checks not run are reported honestly
[ ] release_evidence=false
[ ] implementation does not bypass L1 FICs
```

---

## 21. Stop Conditions

Stop and return `BLOCKED` if any of these occur:

```text
- L1 FICs do not exist for the implementation unit;
- repo root cannot be canonicalized;
- task requests destructive or unsafe behavior;
- implementation would require editing undeclared files;
- permission gate is not implemented;
- evidence writer is not implemented;
- tests cannot be run and no waiver exists;
- model output is needed but no model-output validator exists;
- command execution is requested before check runner governance exists;
- GitHub write integration is requested before GitHub FICs exist;
- secrets or credentials would be logged or stored;
- user asks for hidden or unrecorded changes.
```

---

## 22. L1 Implementation Package Checklist

Before coding begins, L1 must create:

```text
[ ] FICs for MVP units 001-009
[ ] FIC registry entries for all MVP units
[ ] target file paths
[ ] allowed imports and forbidden imports
[ ] public surfaces
[ ] tests for each unit
[ ] validation commands
[ ] evidence paths
[ ] completion-record schema
[ ] review-packet schema
[ ] permission policy
[ ] stop-condition list
```

The coding agent may implement only the current FIC unit and its declared tests.

---

## 23. Relationship to OpenCode

OpenCode may be used as feature-reference inspiration only.

This guide does not:

```text
- copy OpenCode architecture;
- fork OpenCode;
- embed OpenCode source;
- claim compatibility with OpenCode;
- use OpenCode as implementation authority.
```

Agent_X should evolve into an Agent_X-governed coding agent with similar broad capability goals, but with its own governance, FIC, evidence, and permission model.

---

## 24. Future Expansion Roadmap

After MVP works:

```text
1. Plan-only mode
2. Diff-only mode
3. Apply-with-approval mode
4. Check-runner mode
5. Model-provider proposal mode
6. GitHub issue reader
7. PR proposal builder
8. TUI/CLI interface improvements
9. Session history
10. Plugin/tool system
```

Each stage requires L1 FICs, tests, and evidence.

---

## 25. Completion Rubric

| Score | Meaning |
|---:|---|
| 0-3 | Only an idea; user cannot build anything. |
| 4-6 | Architecture exists, but implementation path is underspecified. |
| 7 | Basic MVP modules named, but setup/tests/evidence incomplete. |
| 8 | Buildable with expert interpretation. |
| 9 | Buildable by a disciplined coding agent with minor decisions. |
| 10 | Complete governed build guide with package layout, FIC units, public surfaces, tests, CLI behavior, evidence, stop conditions, and acceptance commands. |

Current guide score:

```text
10/10 for a future L1-governed plan-only MVP build guide.
```

---

---

## 27. Exact First Working Slice

The first working slice must be smaller than the full MVP roadmap.

The first slice is complete only when these commands work:

```bash
agentx-code inspect --repo <sample_repo>
agentx-code plan --repo <sample_repo> --task "Update README wording"
agentx-code validate-plan --plan <sample_repo>/.agentx/plans/<plan_id>.yaml
```

The first slice must not implement real editing, model calls, GitHub actions, or check execution.

Required first-slice behavior:

```text
1. Load config or safe defaults.
2. Canonicalize repo root.
3. Scan repository metadata within configured limits.
4. Classify task deterministically.
5. Select candidate files deterministically.
6. Build a patch plan with edit_authorized=false.
7. Write the plan to .agentx/plans/.
8. Write a completion record to .agentx/evidence/.
9. Return exit code 0 only if both files are written and no source files changed.
```

Required first-slice blocked behavior:

```text
- `agentx-code apply` must be absent or return exit code 2.
- `agentx-code run-checks` must be absent or return exit code 2.
- any task requesting deletion, secret exfiltration, network, commit, push, or dependency install must return BLOCKED_UNSAFE or permission-blocked.
```

This section is the minimum practical build target. Later sections describe expansion, but the first implementation must pass this slice before deeper work begins.

---

## 28. Complete MVP Object Inventory

The v0.2 guide named core data models but did not define every object needed by the public surfaces. The first implementation package must include these objects in `src/agentx_code/models.py` or a clearly declared split module.

Required objects:

```text
AgentXCodeError
AgentXCodeConfig
ApprovalState
OperationRequest
RepoSummary
FileSummary
TaskClassification
FileCandidate
PatchStep
PatchPlan
ProposedEdit
PermissionDecision
CheckResult
CompletionRecord
```

### 28.1 `AgentXCodeConfig`

```yaml
agentx_code_config:
  version: "v0.1.0"
  mode: "plan-only"
  max_file_bytes: 200000
  max_files_scanned: 500
  max_candidate_files: 20
  allow_apply: false
  allow_check_runner: false
  allow_network: false
  allow_git_write: false
  allow_model_provider: false
  allowed_check_commands: []
  evidence_dir: ".agentx/evidence"
  plan_dir: ".agentx/plans"
  ignore_dirs:
    - ".git"
    - ".venv"
    - "node_modules"
    - "dist"
    - "build"
    - "__pycache__"
```

### 28.2 `ApprovalState`

```yaml
approval_state:
  apply_approved: false
  checks_approved: false
  approval_source: "none|cli-flag|config|interactive"
```

For the first slice, approval must always be false unless the future phase explicitly implements approval handling.

### 28.3 `OperationRequest`

```yaml
operation_request:
  operation: "READ_REPO|CREATE_PLAN|BUILD_DIFF|APPLY_PATCH|RUN_CHECK|GITHUB_WRITE|NETWORK_CALL|MODEL_CALL"
  requested_by: "cli"
  target_paths: []
  command: []
```

### 28.4 `FileCandidate`

```yaml
file_candidate:
  path: "repository-relative-posix-path"
  score: "0.000"
  reasons: []
  risk_flags: []
```

Scores should be strings or fixed three-decimal values to avoid unstable output formatting.

### 28.5 `PatchStep`

```yaml
patch_step:
  step_id: "STEP-001"
  action: "inspect|edit-proposed|test-proposed|review-required"
  target_path: null
  description: ""
  requires_approval: true
```

### 28.6 `ProposedEdit`

```yaml
proposed_edit:
  target_path: "repository-relative-posix-path"
  edit_type: "replace|insert|delete|create"
  before: null
  after: null
  rationale: ""
  approval_required: true
```

`ProposedEdit` is declared for future diff mode. The plan-only slice must not use it to write files.

---

## 29. Canonical Plan File Schema

Every successful `agentx-code plan` command must write a YAML plan file.

Path:

```text
<repo>/.agentx/plans/<plan_id>.yaml
```

Minimum schema:

```yaml
patch_plan:
  plan_schema_version: "v0.1.0"
  plan_id: "PLAN-YYYYMMDDTHHMMSSZ-<short-hash>"
  created_by: "agentx-code"
  mode: "plan-only"
  repo_root: "<canonical absolute path>"
  task: ""
  task_classification:
    task_type: "BUG_FIX|TEST_FIX|DOC_UPDATE|REFACTOR_REQUEST|FEATURE_REQUEST|REPO_ANALYSIS|UNKNOWN|BLOCKED_UNSAFE"
    risk_level: "low|medium|high|critical"
    reasons: []
  selected_files:
    - path: "README.md"
      score: "1.000"
      reasons: []
      risk_flags: []
  proposed_steps:
    - step_id: "STEP-001"
      action: "review-required"
      target_path: null
      description: "Review the selected files before any edit is attempted."
      requires_approval: true
  expected_checks: []
  permission:
    approval_required: true
    edit_authorized: false
    checks_authorized: false
    network_authorized: false
    github_write_authorized: false
  generated_outputs:
    completion_record: "<repo-relative evidence path>"
  release_evidence: false
```

Rules:

```text
- Plan files are generated artifacts, not proof that implementation succeeded.
- Plan files must not claim code was changed.
- Plan files must use repository-relative POSIX paths for selected files.
- Plan IDs must not require wall-clock time for deterministic tests; tests may inject a fixed ID factory.
- A blocked task may write a blocked completion record, but should not write a normal patch plan unless the plan status explicitly says blocked.
```

---

## 30. CLI Output Contract

The CLI must be usable by humans and testable by automation.

### 30.1 `inspect`

On success, stdout must include or emit a machine-readable summary containing:

```yaml
inspect_result:
  status: "OK"
  repo_root: "<canonical absolute path>"
  files_scanned: 0
  files_skipped_count: 0
  test_paths: []
  language_hints: []
```

On controlled failure:

```yaml
inspect_result:
  status: "BLOCKED|FAILED"
  error_code: "INVALID_REPO|PATH_ESCAPE|CONFIG_INVALID|SCAN_LIMIT_EXCEEDED"
  message: ""
```

### 30.2 `plan`

On success, stdout must include:

```yaml
plan_result:
  status: "PLAN_CREATED"
  plan_path: "<absolute-or-repo-relative path>"
  completion_record_path: "<absolute-or-repo-relative path>"
  approval_required: true
  edit_authorized: false
```

On blocked unsafe request:

```yaml
plan_result:
  status: "BLOCKED"
  error_code: "BLOCKED_UNSAFE_TASK|PERMISSION_DENIED|INVALID_REPO|CONFIG_INVALID"
  completion_record_path: "<path-if-written>"
```

### 30.3 `validate-plan`

`validate-plan` must parse a generated plan file and verify at least:

```text
- required keys exist;
- edit_authorized is false for plan-only mode;
- selected paths are canonical repository-relative paths;
- release_evidence is false;
- no forbidden operation is authorized.
```

Success output:

```yaml
validate_plan_result:
  status: "VALID"
  plan_path: ""
```

Failure output:

```yaml
validate_plan_result:
  status: "INVALID"
  errors: []
```

---

## 31. Deterministic Candidate Ranking Rule

File selection must be deterministic and explainable.

For the plan-only MVP, use this simple ranking order:

```text
1. Exact filename/task token match.
2. Test-file relevance for TEST_FIX tasks.
3. README/docs relevance for DOC_UPDATE tasks.
4. Source-file relevance for BUG_FIX, FEATURE_REQUEST, or REFACTOR_REQUEST tasks.
5. Lower risk file class wins over higher risk file class.
6. Smaller file size wins when relevance ties.
7. Lexicographically lower repository-relative path wins as final tie-breaker.
```

Forbidden ranking inputs:

```text
- filesystem iteration order;
- wall-clock time;
- random numbers;
- model judgment;
- network data;
- unbounded full-file semantic analysis;
- hidden global caches.
```

Risk file classes:

```text
low: markdown/docs/tests/examples
medium: normal source files
high: config, CI, dependency, build, migration, security-sensitive names
critical: secrets, credentials, auth/payment/deployment files
```

A critical candidate may be listed only with a risk flag and must not be automatically selected for editing.

---

## 32. Plan-Only Implementation Pseudocode

This pseudocode is not a substitute for FICs. It exists to make the first MVP slice concrete enough for L1 to turn into FIC-governed work.

```text
function plan(repo_path, task_text):
    config = load_config_or_safe_defaults(repo_path)
    repo_root = canonicalize_repo_root(repo_path)
    permission = decide_permission(CREATE_PLAN, config, ApprovalState.false_default())
    if permission.status != ALLOWED_PLAN_ONLY:
        record = build_blocked_completion_record(...)
        write_completion_record(record)
        return blocked_result

    summary = read_repo_context(repo_root, config)
    classification = classify_task(task_text)

    if classification.task_type == BLOCKED_UNSAFE:
        record = build_blocked_completion_record(...)
        write_completion_record(record)
        return blocked_result

    candidates = select_file_candidates(summary, classification, config)
    patch_plan = build_patch_plan(task_text, summary, classification, candidates, config)
    assert patch_plan.edit_authorized is false
    assert patch_plan.approval_required is true

    plan_path = write_plan_file(patch_plan, config.plan_dir)
    record = build_completion_record(status=PLAN_CREATED, plan_path=plan_path, ...)
    evidence_path = write_completion_record(record, config.evidence_dir)

    return plan_result(plan_path, evidence_path, edit_authorized=false)
```

Implementation rules:

```text
- Every file write in plan-only mode must be limited to `.agentx/plans/` or `.agentx/evidence/` inside the inspected repo.
- No source file may be modified.
- If plan/evidence directories cannot be created safely, return BLOCKED or FAILED with evidence when possible.
```

---

## 33. No-Write Verification Procedure

A user must be able to verify that plan mode did not modify source files.

Recommended manual verification from the target repo:

```bash
git status --short
agentx-code plan --repo . --task "Update README wording"
git status --short
```

Expected result:

```text
Only `.agentx/plans/` and `.agentx/evidence/` may appear as new or modified paths.
No existing source, test, config, or documentation file may be modified by plan mode.
```

Automated test requirement:

```text
- create a fixture repo;
- snapshot all file digests excluding `.agentx/`;
- run plan command;
- recompute digests excluding `.agentx/`;
- assert digest map is identical.
```

This test is mandatory before the MVP is called working.

---

## 34. Minimal Sample Repository Fixtures

The test suite must include enough sample repositories to prove behavior without using the real Agent_X repo as the test target.

Required fixtures:

```text
tests/fixtures/sample_repo_basic/
  README.md
  src/example.py
  tests/test_example.py

tests/fixtures/sample_repo_docs_only/
  README.md
  docs/usage.md

tests/fixtures/sample_repo_with_binary/
  README.md
  assets/blob.bin

tests/fixtures/sample_repo_with_risky_files/
  README.md
  .github/workflows/ci.yml
  pyproject.toml
  src/auth.py
```

Fixture rules:

```text
- fixtures must be small;
- fixtures must not contain secrets;
- binary fixture should be tiny and intentionally non-text;
- tests must copy fixtures into a temporary directory before mutation/evidence tests;
- tests must not write into checked-in fixture directories.
```

---

## 35. Blocked Stub Requirements for Future Commands

Before `apply`, `run-checks`, model provider, or GitHub integration are implemented, the CLI must either omit those commands or return a controlled blocked result.

Blocked-stub output:

```yaml
command_result:
  status: "BLOCKED"
  error_code: "FEATURE_NOT_IMPLEMENTED_REQUIRES_L1_FIC"
  implementation_authorized: false
  release_evidence: false
```

Rules:

```text
- A future command must not be partially implemented in a way that performs side effects.
- A help entry for a future command must say it is blocked/deferred.
- A blocked command must not create source-file changes.
- A blocked command may write a completion record only if evidence writing is already implemented and safe.
```

---

## 36. L1 FIC Package Manifest Schema

Before coding starts, L1 should create a manifest tying the MVP units together.

Recommended path:

```text
L1/implementation_packages/coding_agent_mvp/fic/fic_package_manifest.yaml
```

Minimum schema:

```yaml
fic_package_manifest:
  package_id: "AGENT_X_CODE_MVP_001"
  package_version: "v0.1.0"
  implementation_authorized: false
  release_evidence: false
  target_root: "L1/implementation_packages/coding_agent_mvp"
  units:
    - fic_id: "FIC-MVP-001"
      target_file: "src/agentx_code/repo_context_reader.py"
      test_file: "tests/test_repo_context_reader.py"
      status: "draft|ready-for-code|implemented|validated"
  required_commands:
    - "python -m pytest tests -q"
    - "python -m compileall src"
  forbidden_imports:
    - "requests"
    - "urllib"
    - "socket"
    - "subprocess"
  phase: "plan-only"
```

Rules:

```text
- `implementation_authorized` may become true only after L1 explicitly accepts the implementation package.
- `subprocess` may remain forbidden until check-runner FIC specifically permits bounded process execution.
- Each FIC unit must declare any exception to the package-level forbidden imports.
```

---

## 37. Buildability Decision Table

| Observed state | Decision |
|---|---|
| Guide exists, but no L1 FIC package exists | `NOT_BUILDABLE_YET_NEEDS_L1_FIC_PACKAGE` |
| L1 FIC package exists, but unit FICs are draft | `NOT_BUILDABLE_YET_FICS_NOT_READY` |
| Unit FICs are ready, but tests missing | `NOT_BUILDABLE_YET_TESTS_MISSING` |
| Plan-only units implemented and tests pass | `PLAN_ONLY_MVP_WORKING` |
| Diff mode exists but cannot write files | `DIFF_ONLY_MVP_WORKING` |
| Apply mode edits files without permission gate | `REJECTED_UNSAFE_IMPLEMENTATION` |
| Check runner executes raw shell strings | `REJECTED_UNSAFE_IMPLEMENTATION` |
| GitHub write operations exist before FICs | `REJECTED_SCOPE_DRIFT` |

A user can get a working agent only after the state reaches `PLAN_ONLY_MVP_WORKING` or higher.

---

## 38. Updated Final Status

This v0.3 guide is complete for its intended purpose: enabling L1 to create a governed, testable implementation package for a plan-only OpenCode-like Agent_X coding-agent MVP.

It still does not make the agent work by itself.

Correct interpretation:

```text
This document + L1 FIC package + implementation + tests = working MVP.
This document alone = not a working agent.
```

Current score:

```text
10/10 for future L1-governed plan-only MVP build-guide completeness
Implementation authorized: false
Working agent from document alone: no
Working agent after L1 FIC-governed implementation: yes
```

## 39. Final Status

This document is complete when it enables L1 to create a governed implementation package for a minimal OpenCode-like Agent_X coding-agent MVP.

Current status:

```text
Build guide: complete for L1-governed MVP planning
Implementation authorized: false
L1 FICs required: true
Working agent exists from this document alone: no
Working agent possible after L1-governed implementation: yes
```

---

## 40. Environment and Dependency Assumptions

The first implementation must be deliberately boring.

Required environment:

```text
Python: 3.11 or 3.12
Operating systems: Linux/macOS first; Windows support only if path tests pass
Package format: pyproject.toml
Required runtime dependency: PyYAML only
Required test dependency: pytest
Network: disabled / unused
Model provider: disabled / unused
GitHub integration: disabled / unused
```

Implementation rules:

```text
- Do not add requests, httpx, urllib, socket, aiohttp, rich, typer, click, gitpython, langchain, or model SDKs in the first slice.
- Use argparse for CLI.
- Use pathlib for paths.
- Use dataclasses for data objects.
- Use yaml.safe_load and yaml.safe_dump only.
- Avoid global mutable state.
- Keep all writes limited to `.agentx/plans/` and `.agentx/evidence/` inside the target repository.
```

If the first implementation needs more dependencies, stop and route the change through L1 FIC review.

---

## 41. Path Normalization and Repository Boundary Algorithm

Every path entering the MVP must be normalized before use.

Required algorithm:

```text
1. Convert input repo path to Path.
2. Resolve repo path with strict=True.
3. Confirm the resolved repo path is a directory.
4. For every candidate file, resolve the path.
5. Confirm the resolved candidate path is inside the resolved repo root.
6. Convert stored paths to repository-relative POSIX paths.
7. Reject paths containing null bytes, unresolved `..`, absolute stored paths, or symlink escapes.
```

Canonical helper behavior:

```text
repo_root = Path(repo).resolve(strict=True)
resolved_child = candidate.resolve(strict=True)
resolved_child.relative_to(repo_root) must succeed
stored_path = resolved_child.relative_to(repo_root).as_posix()
```

Blocking error codes:

```text
INVALID_REPO
PATH_ESCAPE
SYMLINK_ESCAPE
NON_CANONICAL_PATH
UNREADABLE_PATH
```

Rules:

```text
- A path outside repo root must never appear in selected files.
- Absolute paths may appear in local CLI output for user convenience, but plan files should store repo-relative paths for selected files.
- Evidence may store canonical repo root, but must not store secrets or file contents.
```

---

## 42. Atomic Write and Append-Only Rules

The first MVP writes generated artifacts. These writes must be safe and auditable.

Allowed generated locations inside the target repo:

```text
.agentx/plans/<plan_id>.yaml
.agentx/evidence/<timestamp>_completion_record.yaml
.agentx/evidence/<timestamp>_review_packet.md
.agentx/evidence/<timestamp>_command_results.yaml
```

Rules:

```text
- Create `.agentx/`, `.agentx/plans/`, and `.agentx/evidence/` only when needed.
- Do not overwrite existing plan or evidence files.
- If the generated target path already exists, create a new ID or return BLOCKED_DUPLICATE_EVIDENCE_PATH.
- Write to a temporary file in the same directory, then atomically rename.
- Do not partially write YAML files.
- Evidence is append-only by filename, not by appending to a mutable log file.
```

Recommended atomic write sequence:

```text
1. Serialize content deterministically.
2. Write to `<target>.tmp.<pid-or-random-safe-suffix>`.
3. Flush and close.
4. Rename temp file to final path only if final path does not already exist.
5. If rename fails because final exists, delete temp and return controlled error.
```

Plan-only mode may create `.agentx/` artifacts. It must not modify any pre-existing non-`.agentx/` file.

---

## 43. Secret, Credential, and Sensitive-File Handling

The MVP must avoid collecting or exposing secrets.

Files with these names or path components must be treated as high or critical risk:

```text
.env
.env.*
*.pem
*.key
id_rsa
id_ed25519
secrets
secret
credentials
token
password
auth
payment
deploy
production
```

Rules:

```text
- Do not read contents of obvious secret files.
- Do not include secret file contents in plan, evidence, stdout, stderr, or review packets.
- A task asking to reveal, print, copy, exfiltrate, decode, or log secrets must be BLOCKED_UNSAFE.
- Candidate files may list secret-like paths only as blocked/risky references, not as editable targets.
- Evidence must include the fact that secret-like files were skipped, not their content.
```

Required test:

```text
Create a fixture with `.env` and assert that plan mode never reads or emits its contents.
```

---

## 44. Minimal Schema Validation Requirements

The first implementation should validate its own generated YAML enough to catch broken outputs.

Required validation functions:

```text
validate_config_object(config) -> list[str]
validate_plan_object(plan) -> list[str]
validate_completion_record(record) -> list[str]
validate_cli_result(result) -> list[str]
```

Validation may be implemented manually in Python. Full JSON Schema is optional for the first slice.

Required checks for plan files:

```text
- `patch_plan` root key exists.
- `plan_schema_version` exists.
- `mode` is `plan-only`.
- `repo_root` exists.
- `task` exists.
- `task_classification.task_type` uses controlled enum.
- `selected_files` is a list.
- every selected file path is repository-relative POSIX.
- `permission.approval_required` is true.
- `permission.edit_authorized` is false.
- `permission.network_authorized` is false.
- `permission.github_write_authorized` is false.
- `release_evidence` is false.
```

Required checks for completion records:

```text
- status uses controlled enum.
- files_changed is empty in plan-only mode.
- checks_run is empty unless a future approved check runner exists.
- checks_not_run is present.
- approval.required is true.
- approval.received is false in first slice.
- release_evidence is false.
```

`agentx-code validate-plan` must use the same validation functions used by tests.

---

## 45. Sample CLI Transcripts

These examples define the expected user experience.

### 45.1 Successful inspect

```bash
agentx-code inspect --repo tests/fixtures/sample_repo_basic
```

Expected shape:

```yaml
inspect_result:
  status: "OK"
  repo_root: "<absolute path>"
  files_scanned: 3
  files_skipped_count: 0
  test_paths:
    - "tests/test_example.py"
  language_hints:
    - "markdown"
    - "python"
```

### 45.2 Successful plan

```bash
agentx-code plan --repo tests/fixtures/sample_repo_basic --task "Update README wording"
```

Expected shape:

```yaml
plan_result:
  status: "PLAN_CREATED"
  plan_path: "tests/fixtures/sample_repo_basic/.agentx/plans/<plan_id>.yaml"
  completion_record_path: "tests/fixtures/sample_repo_basic/.agentx/evidence/<timestamp>_completion_record.yaml"
  approval_required: true
  edit_authorized: false
```

### 45.3 Blocked unsafe task

```bash
agentx-code plan --repo tests/fixtures/sample_repo_basic --task "Delete every file and push the commit"
```

Expected shape:

```yaml
plan_result:
  status: "BLOCKED"
  error_code: "BLOCKED_UNSAFE_TASK"
  edit_authorized: false
  release_evidence: false
```

Exit code:

```text
2
```

### 45.4 Validate plan

```bash
agentx-code validate-plan --plan tests/fixtures/sample_repo_basic/.agentx/plans/<plan_id>.yaml
```

Expected shape:

```yaml
validate_plan_result:
  status: "VALID"
  plan_path: "tests/fixtures/sample_repo_basic/.agentx/plans/<plan_id>.yaml"
```

---

## 46. One-Page Implementation Checklist for a Coding Agent

A weaker coding agent implementing this MVP must follow this checklist exactly.

```text
[ ] Create implementation package only after L1 FIC package exists.
[ ] Create pyproject.toml.
[ ] Create src/agentx_code/__init__.py.
[ ] Create models.py with required dataclasses/enums/errors.
[ ] Create config_loader.py with safe defaults and unsafe config rejection.
[ ] Create repo_context_reader.py with bounded deterministic scan.
[ ] Create task_classifier.py with deterministic rules and unsafe-task blocking.
[ ] Create file_candidate_selector.py with deterministic ranking.
[ ] Create patch_plan_builder.py with edit_authorized=false.
[ ] Create permission_gate.py with default plan-only/read-only decisions.
[ ] Create evidence_writer.py with atomic append-only writes.
[ ] Create cli.py with inspect, plan, validate-plan.
[ ] Omit or block apply/run-checks.
[ ] Create fixtures in tests/fixtures/.
[ ] Create no-write test using digest snapshot excluding .agentx.
[ ] Create unsafe-task tests.
[ ] Create path traversal and symlink escape tests.
[ ] Create validate-plan tests.
[ ] Run python -m compileall src.
[ ] Run python -m pytest tests -q.
[ ] Record completion evidence.
```

Stop immediately if asked to implement GitHub writes, model calls, arbitrary shell, apply-without-approval, or any operation not covered by a current L1 FIC.

---

## 47. L1 Handoff Packet to Start Implementation

To convert this build guide into real work, create a L1 handoff packet, not code.

Recommended path:

```text
L2/generated/l1_handoff_requests/opencode_like_coding_agent_mvp_handoff_request.yaml
```

Minimum packet:

```yaml
l2_to_l1_handoff_request:
  request_id: "L2-HANDOFF-OPENCODE-LIKE-MVP-001"
  source_example_document: "examples/evolutions/opencode_like_coding_agent/AGENT_X_OPENCODE_LIKE_CODING_AGENT_EVOLUTION_v0_5.md"
  source_build_guide: "examples/evolutions/opencode_like_coding_agent/AGENT_X_OPENCODE_LIKE_CODING_AGENT_MVP_BUILD_GUIDE_v0_4.md"
  requested_l1_action: "create-fic-governed-implementation-package"
  proposed_package_root: "L1/implementation_packages/coding_agent_mvp"
  proposed_phase: "plan-only"
  implementation_requested_by_l2: false
  implementation_authorized_by_l2: false
  l1_acceptance_required: true
  l1_must_create_fics_before_code: true
  proposed_fic_units:
    - "FIC-MVP-001-repo-context-reader"
    - "FIC-MVP-002-task-classifier"
    - "FIC-MVP-003-file-candidate-selector"
    - "FIC-MVP-004-patch-plan-builder"
    - "FIC-MVP-006-permission-gate"
    - "FIC-MVP-008-evidence-writer"
    - "FIC-MVP-009-cli-entrypoint"
  deferred_units:
    - "FIC-MVP-005-diff-builder"
    - "FIC-MVP-007-check-runner"
    - "model-provider-integration"
    - "github-integration"
  forbidden_direct_actions:
    - "modify L0"
    - "modify L1 without L1 FIC"
    - "create L2 runtime"
    - "execute arbitrary shell"
    - "perform GitHub writes"
    - "call model providers"
    - "apply file edits without approval"
  release_evidence: false
```

L1 may accept, reject, split, or defer this request. Implementation begins only after L1 creates the FIC package and marks the first unit ready for code.

---

## 48. Complete-Coverage Gate

This document covers everything it needs to cover for a user to get a **plan-only MVP working after L1-governed implementation** if all of the following are true:

```text
[ ] It defines what the MVP does and does not do.
[ ] It defines where the code belongs.
[ ] It defines package layout and CLI entrypoint.
[ ] It defines installation and run commands.
[ ] It defines public module surfaces.
[ ] It defines data objects and generated YAML shapes.
[ ] It defines config behavior and safe defaults.
[ ] It defines deterministic task classification and file ranking.
[ ] It defines permission gates.
[ ] It defines evidence writing.
[ ] It defines atomic/generated file rules.
[ ] It defines no-write verification.
[ ] It defines path-boundary and secret-handling rules.
[ ] It defines required tests and fixtures.
[ ] It defines blocked future commands.
[ ] It defines L1 FIC package requirements.
[ ] It defines handoff packet contents.
[ ] It defines acceptance criteria and stop conditions.
[ ] It does not claim current implementation authority.
```

Current assessment:

```text
Previous v0.3 score: 9.7/10 for practical build coverage.
Remaining gaps fixed in v0.4: environment assumptions, atomic writes, path normalization, secret handling, schema validation, sample CLI transcripts, one-page implementation checklist, and exact L1 handoff packet.
Current v0.4 score: 10/10 for future L1-governed plan-only MVP build-guide completeness.
Working agent from this document alone: no.
Working plan-only MVP after L1 FIC package + implementation + tests: yes.
```

---

## 49. Exact Bootstrap Command Contract

A future implementation package created from this guide should be bootstrappable with standard Python commands.

Recommended commands after L1 has authorized implementation and the package exists:

```bash
cd L1/implementation_packages/coding_agent_mvp
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
python -m agentx_code.cli --help
agentx-code --help
```

Rules:

```text
- These commands are documentation for the future implementation package only.
- They do not authorize implementation before L1 FIC acceptance.
- The package must not require network access at runtime for inspect/plan mode.
- The package may require network only during dependency installation, and dependencies must be declared in `pyproject.toml`.
- The CLI must run in plan-only mode without model-provider credentials.
```

Minimum expected command behavior:

```text
python -m agentx_code.cli --help
  -> prints command help and exits 0

agentx-code inspect --repo <sample_repo>
  -> writes inspection evidence and exits 0

agentx-code plan --repo <sample_repo> --task "Rename function foo to bar"
  -> writes plan YAML and evidence; modifies no source files; exits 0

agentx-code apply --plan <plan_file>
  -> blocked stub in first MVP; exits 3 or configured blocked-code
```

---

## 50. `.agentx/` Generated-State and `.gitignore` Policy

The MVP should write generated operational state under the target repository's `.agentx/` directory by default.

Recommended target-repo generated layout:

```text
<target_repo>/.agentx/
  plans/
  evidence/
  inspections/
  logs/
  tmp/
```

Recommended `.gitignore` addition for repositories using the MVP:

```gitignore
# Agent_X local generated planning/evidence state
.agentx/tmp/
.agentx/logs/
```

Do not automatically add `.agentx/` to `.gitignore` without user approval.

Policy:

```text
- `.agentx/plans/` may be committed only if the user wants reviewable planning artifacts in version control.
- `.agentx/evidence/` may be committed only for governed Agent_X work, not by default.
- `.agentx/tmp/` must never be treated as evidence.
- `.agentx/logs/` must not contain secrets or raw model prompts with credentials.
- The MVP must not silently delete existing `.agentx/` files.
```

If `.agentx/` already exists, the MVP must preserve it and append new timestamped files only.

---

## 51. Dirty Repository and Git-Safety Behavior

The MVP must treat the target repository state as safety-relevant.

Inspect and plan commands should record, but not require, git status.

Minimum git-safety behavior:

```text
- If the target path is not a git repository, continue in limited mode and report `git_status_available: false`.
- If the target repo has uncommitted changes, continue in plan-only mode but record `dirty_worktree: true`.
- If future apply mode is requested and the repo is dirty, block unless the user explicitly allows dirty-repo operation.
- The first MVP must not run `git add`, `git commit`, `git push`, or branch-changing commands.
```

Required evidence fields:

```yaml
git_safety:
  is_git_repo: true
  git_status_available: true
  dirty_worktree: false
  branch_name: null
  commit_sha: null
  git_commands_run:
    - "git status --short"
  git_commands_forbidden:
    - "git add"
    - "git commit"
    - "git push"
    - "git checkout"
    - "git switch"
```

Rules:

```text
- Git status failures must not crash inspect/plan mode.
- Git metadata must not be used as permission to edit files.
- A clean git repo is helpful evidence, not implementation authorization.
```

---

## 52. User-Facing Error Message Matrix

The MVP must fail clearly and safely.

| Condition | Exit | User-facing message requirement |
|---|---:|---|
| Repo path missing | 2 | Say the repo path does not exist. |
| Repo path outside allowed root | 2 | Say the path fails repository-boundary validation. |
| Task text empty | 2 | Say `--task` is required for plan mode. |
| Secret-like file selected | 4 | Say the file was excluded by sensitive-file policy. |
| Apply command used in MVP | 3 | Say apply mode is not available in the plan-only MVP. |
| Check command not whitelisted | 3 | Say the command is not in the allowed check list. |
| Evidence write fails | 5 | Say evidence could not be written and no readiness claim is made. |
| Unexpected internal error | 1 | Say the operation failed and point to a sanitized log path if available. |

Rules:

```text
- Error messages must not expose secrets.
- Error messages must not include hidden chain-of-thought or raw provider prompts.
- Blocked operations must be reported as controlled blocks, not crashes.
- A failed evidence write must prevent success status.
```

---

## 53. MVP Smoke-Test and Evidence Script Contract

A future implementation should include a smoke-test helper, but only after L1 authorizes implementation.

Recommended script path:

```text
L1/implementation_packages/coding_agent_mvp/scripts/smoke_test_plan_only.py
```

Required checks:

```text
1. Create a temporary sample repository fixture.
2. Capture hashes of all source files before running the MVP.
3. Run inspect mode.
4. Run plan mode with a simple task.
5. Capture hashes of all source files after running the MVP.
6. Assert source file hashes are unchanged.
7. Assert `.agentx/plans/` contains one plan file.
8. Assert `.agentx/evidence/` contains one completion/evidence record.
9. Assert apply/check commands are blocked or permission-gated.
10. Print a final machine-readable smoke-test result.
```

Minimum smoke-test result:

```yaml
agentx_code_mvp_smoke_test:
  status: "PASS|FAIL|BLOCKED"
  package_version: "v0.1.0"
  plan_only: true
  source_hashes_unchanged: true
  inspect_command_passed: true
  plan_command_passed: true
  apply_command_blocked: true
  evidence_written: true
  release_evidence: false
```

Rules:

```text
- Smoke-test evidence is MVP implementation evidence, not release evidence.
- The smoke test must not require model-provider credentials.
- The smoke test must not mutate tracked source files.
```

---

## 54. Post-Implementation Quickstart Checklist

After L1 authorizes implementation and the package is built, the README inside the implementation package should give users a minimal quickstart.

Required quickstart content:

```md
# Agent_X Coding Agent MVP Quickstart

This MVP is plan-only. It inspects a repository and writes a proposed plan. It does not edit source files.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
agentx-code inspect --repo /path/to/repo
agentx-code plan --repo /path/to/repo --task "Describe the change you want"
python -m pytest -q
```

Generated files are written under:

```text
/path/to/repo/.agentx/
```

The first MVP blocks apply/write operations by design.
```

The quickstart must not claim:

```text
- autonomous editing works;
- GitHub PR creation works;
- model-provider integration works;
- release validation has passed;
- L2 authorized runtime implementation.
```

---

## 55. Final Implementation-Readiness Closure Gate

This build guide is complete for the plan-only MVP only if all of the following are true:

```text
[ ] It explains that implementation requires L1 FIC authorization.
[ ] It defines the first working MVP as plan-only.
[ ] It defines repository placement after L1 approval.
[ ] It defines package layout, CLI entrypoint, commands, and exit codes.
[ ] It defines config objects and core data models.
[ ] It defines plan YAML and evidence schemas.
[ ] It defines deterministic candidate-file ranking.
[ ] It defines path normalization and repo-boundary checks.
[ ] It defines secret/sensitive-file exclusions.
[ ] It defines check-runner whitelist behavior.
[ ] It defines no-write verification.
[ ] It defines git dirty-state behavior.
[ ] It defines generated `.agentx/` state policy.
[ ] It defines user-facing error behavior.
[ ] It defines smoke-test expectations.
[ ] It defines tests required before the MVP is considered working.
[ ] It defines what remains blocked or deferred.
[ ] It prevents OpenCode copying/forking confusion.
[ ] It prevents false runtime, release, or implementation claims.
```

Current status after v0.5 review:

```text
Build-guide coverage: 10/10
Implementation authorization: false
Working agent already present: false
Ready for L1 to convert into FIC-governed MVP implementation work: yes
```

