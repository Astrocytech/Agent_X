# Agent_X OpenCode-like Coding Agent — Coding LLM TODO

**Document ID:** `AGENT-X-CODING-LLM-TODO-OPENCODE-LIKE-MVP-001`  
**Version:** `v1.2.0`  
**Status:** `ready-for-coding-llm-handoff`  
**Intended user:** a coding LLM working inside the Agent_X repository  
**Primary purpose:** Provide exact instructions for evolving Agent_X toward an OpenCode-like coding agent by implementing only the first L1-governed, plan-only MVP slice.  
**Implementation authorized by this document:** `false`  
**L1 FIC governance required:** `true`  
**Runtime target:** `plan-only MVP`  
**Forbidden target:** full OpenCode clone, OpenCode fork, autonomous coding agent, ungoverned repository editor

---

## 0. Source Documents

Use these two documents as governing source material:

```text
examples/evolutions/opencode_like_coding_agent.md
AGENT_X_OPENCODE_LIKE_CODING_AGENT_MVP_BUILD_GUIDE_v0_5.md
```

If the exact files are not already in the repository, place them as documentation/source material first, without treating them as implementation authority.

Expected source roles:

| Source | Role |
|---|---|
| `opencode_like_coding_agent.md` | Non-authoritative evolution example. Explains the desired OpenCode-like direction and the L2-to-L1 governance path. |
| `AGENT_X_OPENCODE_LIKE_CODING_AGENT_MVP_BUILD_GUIDE_v0_5.md` | Future L1-governed build guide for the first plan-only MVP. Defines the package layout, commands, modules, safety rules, tests, evidence, and acceptance criteria. |

Do **not** use either document as permission to skip L1 governance.

---

## 1. Core Objective

Implement the smallest useful Agent_X coding-agent MVP:

```text
User task + repository path
  -> inspect repository
  -> classify task
  -> select candidate files
  -> create a patch plan
  -> write plan/evidence under .agentx/
  -> modify no source files
```

The first working commands must be:

```bash
agentx-code inspect --repo <repo>
agentx-code plan --repo <repo> --task "<task>"
agentx-code validate-plan --plan <repo>/.agentx/plans/<plan_id>.yaml
```

The first MVP must be **plan-only**.

It must not apply patches, run arbitrary shell, call model providers, use GitHub APIs, create commits, push branches, or perform autonomous actions.

---

## 2. Non-Negotiable Boundaries

The coding LLM must obey these boundaries:

```text
- Do not modify L0.
- Do not modify L2 runtime behavior.
- Do not create executable code under L2.
- Do not copy OpenCode source code.
- Do not fork OpenCode.
- Do not claim OpenCode compatibility.
- Do not create autonomous patching behavior.
- Do not implement GitHub write operations.
- Do not implement model-provider calls.
- Do not run arbitrary shell commands.
- Do not apply file edits in the first slice.
- Do not claim release evidence.
```

Allowed implementation location only after the package/FIC scaffold is created:

```text
L1/implementation_packages/coding_agent_mvp/
```

Forbidden implementation locations:

```text
L0/
L2/
examples/
root scripts unrelated to the implementation package
```

---

## 3. Required Final Repository Placement

Create this package:

```text
L1/implementation_packages/coding_agent_mvp/
  README.md
  pyproject.toml
  fic/
    fic_package_manifest.yaml
    FIC-MVP-001-repo-context-reader.md
    FIC-MVP-002-task-classifier.md
    FIC-MVP-003-file-candidate-selector.md
    FIC-MVP-004-patch-plan-builder.md
    FIC-MVP-006-permission-gate.md
    FIC-MVP-008-evidence-writer.md
    FIC-MVP-009-cli-entrypoint.md
  src/agentx_code/
    __init__.py
    cli.py
    models.py
    config_loader.py
    repo_context_reader.py
    task_classifier.py
    file_candidate_selector.py
    patch_plan_builder.py
    permission_gate.py
    evidence_writer.py
  tests/
    fixtures/
      sample_repo_basic/
      sample_repo_docs_only/
      sample_repo_with_binary/
      sample_repo_with_risky_files/
    test_cli.py
    test_config_loader.py
    test_repo_context_reader.py
    test_task_classifier.py
    test_file_candidate_selector.py
    test_patch_plan_builder.py
    test_permission_gate.py
    test_evidence_writer.py
    test_no_write_in_plan_mode.py
    test_validate_plan.py
  scripts/
    smoke_test_plan_only.py
  evidence/
    .gitkeep
```

Deferred files may be added later, but must not perform side effects in this first slice:

```text
diff_builder.py
check_runner.py
model_provider_adapter.py
github_*.py
session_store.py
```

If added now, they must be blocked stubs only.

---

## 4. FIC Package Requirement

Before writing implementation code, create the `fic/` directory and the FIC package manifest.

File:

```text
L1/implementation_packages/coding_agent_mvp/fic/fic_package_manifest.yaml
```

Minimum content:

```yaml
fic_package_manifest:
  package_id: "AGENT_X_CODE_MVP_001"
  package_version: "v0.1.0"
  implementation_authorized: false
  release_evidence: false
  target_root: "L1/implementation_packages/coding_agent_mvp"
  phase: "plan-only"
  units:
    - fic_id: "FIC-MVP-001"
      target_file: "src/agentx_code/repo_context_reader.py"
      test_file: "tests/test_repo_context_reader.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-002"
      target_file: "src/agentx_code/task_classifier.py"
      test_file: "tests/test_task_classifier.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-003"
      target_file: "src/agentx_code/file_candidate_selector.py"
      test_file: "tests/test_file_candidate_selector.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-004"
      target_file: "src/agentx_code/patch_plan_builder.py"
      test_file: "tests/test_patch_plan_builder.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-006"
      target_file: "src/agentx_code/permission_gate.py"
      test_file: "tests/test_permission_gate.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-008"
      target_file: "src/agentx_code/evidence_writer.py"
      test_file: "tests/test_evidence_writer.py"
      status: "ready-for-code"
    - fic_id: "FIC-MVP-009"
      target_file: "src/agentx_code/cli.py"
      test_file: "tests/test_cli.py"
      status: "ready-for-code"
  required_commands:
    - "python -m compileall src"
    - "python -m pytest tests -q"
  forbidden_imports:
    - "requests"
    - "urllib"
    - "socket"
    - "httpx"
    - "aiohttp"
    - "gitpython"
    - "langchain"
    - "openai"
    - "anthropic"
  subprocess_policy:
    default: "forbidden"
    exception: "none in first slice"
```

Each FIC markdown file must state:

```text
- target file
- public surface
- allowed behavior
- forbidden behavior
- tests required
- evidence required
- implementation_allowed: false until package review is complete
- release_evidence: false
```

Do not treat the FIC package as release evidence.

---

## 5. Python Package Requirements

Create:

```text
L1/implementation_packages/coding_agent_mvp/pyproject.toml
```

Minimum content:

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
dev = [
  "pytest>=8.0",
]

[project.scripts]
agentx-code = "agentx_code.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Dependency rules:

```text
- Use argparse, pathlib, dataclasses, hashlib, json/yaml, tempfile, os, sys.
- Runtime dependency: PyYAML only.
- Test dependency: pytest only.
- Do not add model SDKs.
- Do not add HTTP/network libraries.
- Do not add GitHub libraries.
- Do not add rich/click/typer unless separately approved later.
```

---

## 6. Required Data Models

Create `src/agentx_code/models.py`.

Use dataclasses and simple enums/constants. Keep output serialization deterministic.

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
PermissionDecision
CompletionRecord
```

Recommended status constants:

```text
PLAN_CREATED
BLOCKED
FAILED
NO_CHANGE
VALID
INVALID
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

Risk levels:

```text
low
medium
high
critical
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

---

## 7. Config Loader

Create:

```text
src/agentx_code/config_loader.py
```

Public surface:

```text
ConfigLoaderError
load_config(repo_root: Path) -> AgentXCodeConfig
safe_default_config() -> AgentXCodeConfig
validate_config(config: AgentXCodeConfig) -> list[str]
```

Default config:

```yaml
agentx_code_config_version: "v0.1.0"
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

Rules:

```text
- Missing config uses safe defaults.
- Config cannot enable network in first slice.
- Config cannot enable Git write in first slice.
- Config cannot enable model provider in first slice.
- Unknown dangerous fields must fail validation.
```

---

## 8. Repository Context Reader

Create:

```text
src/agentx_code/repo_context_reader.py
```

Public surface:

```text
RepoContextError
canonicalize_repo_root(repo_path: str | Path) -> Path
is_within_repo(repo_root: Path, child: Path) -> bool
read_repo_context(repo_path: str | Path, config: AgentXCodeConfig) -> RepoSummary
```

Required behavior:

```text
- Resolve repo root with strict=True.
- Reject missing path.
- Reject non-directory path.
- Scan files deterministically.
- Respect max_files_scanned.
- Respect max_file_bytes.
- Skip binary files.
- Skip ignored directories.
- Store paths as repository-relative POSIX paths.
- Detect language hints.
- Detect test paths.
- Detect secret-like files and mark them skipped/risky without reading contents.
```

Forbidden behavior:

```text
- no writes;
- no network;
- no shell;
- no dependency installation;
- no reading outside repo root;
- no following symlink escapes.
```

---

## 9. Task Classifier

Create:

```text
src/agentx_code/task_classifier.py
```

Public surface:

```text
TaskClassifierError
classify_task(task_text: str) -> TaskClassification
```

Rules:

```text
- Empty task is controlled error.
- Destructive tasks return BLOCKED_UNSAFE.
- Secret exfiltration tasks return BLOCKED_UNSAFE.
- Network/curl/wget requests return BLOCKED_UNSAFE or high risk blocked.
- Commit/push requests are blocked in first slice.
- Test-weakening requests are high risk or blocked.
- Ambiguous tasks return UNKNOWN.
```

No model calls. Deterministic rules only.

---

## 10. File Candidate Selector

Create:

```text
src/agentx_code/file_candidate_selector.py
```

Public surface:

```text
FileCandidateSelectorError
select_file_candidates(repo_summary: RepoSummary, classification: TaskClassification, config: AgentXCodeConfig) -> list[FileCandidate]
```

Deterministic ranking:

```text
1. Exact filename/task token match.
2. Test-file relevance for TEST_FIX.
3. README/docs relevance for DOC_UPDATE.
4. Source-file relevance for BUG_FIX, FEATURE_REQUEST, REFACTOR_REQUEST.
5. Lower risk file class wins.
6. Smaller file size wins.
7. Lexicographically lower repository-relative path wins.
```

Candidate selector must not read extra files directly.

---

## 11. Patch Plan Builder

Create:

```text
src/agentx_code/patch_plan_builder.py
```

Public surface:

```text
PatchPlanBuilderError
build_patch_plan(
    task_text: str,
    repo_summary: RepoSummary,
    classification: TaskClassification,
    candidates: list[FileCandidate],
    config: AgentXCodeConfig,
) -> PatchPlan
validate_plan_object(plan: PatchPlan | dict) -> list[str]
write_plan_file(plan: PatchPlan, repo_root: Path, config: AgentXCodeConfig) -> Path
```

Required plan YAML:

```yaml
patch_plan:
  plan_schema_version: "v0.1.0"
  plan_id: "PLAN-..."
  created_by: "agentx-code"
  mode: "plan-only"
  repo_root: "<canonical absolute path>"
  task: ""
  task_classification:
    task_type: ""
    risk_level: ""
    reasons: []
  selected_files: []
  proposed_steps: []
  expected_checks: []
  permission:
    approval_required: true
    edit_authorized: false
    checks_authorized: false
    network_authorized: false
    github_write_authorized: false
  generated_outputs:
    completion_record: ""
  release_evidence: false
```

Rules:

```text
- edit_authorized must be false.
- approval_required must be true.
- release_evidence must be false.
- plan-only mode may write only under .agentx/plans/.
- blocked unsafe tasks must not produce a normal successful plan.
```

---

## 12. Permission Gate

Create:

```text
src/agentx_code/permission_gate.py
```

Public surface:

```text
PermissionGateError
decide_permission(operation: OperationRequest, config: AgentXCodeConfig, approval: ApprovalState) -> PermissionDecision
```

Required default:

```text
READ_REPO -> allowed
CREATE_PLAN -> allowed
BUILD_DIFF -> blocked or deferred
APPLY_PATCH -> blocked
RUN_CHECK -> blocked
GITHUB_WRITE -> blocked
NETWORK_CALL -> blocked
MODEL_CALL -> blocked
```

No operation may silently escalate permission.

---

## 13. Evidence Writer

Create:

```text
src/agentx_code/evidence_writer.py
```

Public surface:

```text
EvidenceWriterError
write_completion_record(record: CompletionRecord, evidence_dir: Path) -> Path
write_review_packet(plan: PatchPlan, record: CompletionRecord, evidence_dir: Path) -> Path
atomic_write_yaml(path: Path, data: dict) -> Path
```

Allowed evidence paths:

```text
.agentx/evidence/<timestamp>_completion_record.yaml
.agentx/evidence/<timestamp>_review_packet.md
.agentx/evidence/<timestamp>_command_results.yaml
```

Rules:

```text
- append-only by filename;
- never overwrite existing evidence;
- write temp file then atomic rename;
- no false check-pass claims;
- checks_not_run must be present;
- release_evidence false.
```

---

## 14. CLI Entrypoint

Create:

```text
src/agentx_code/cli.py
```

Public surface:

```text
main(argv: list[str] | None = None) -> int
```

Commands:

```text
inspect --repo <path>
plan --repo <path> --task <text>
validate-plan --plan <path>
```

Deferred commands:

```text
apply
run-checks
```

Either omit deferred commands or return controlled blocked result:

```yaml
command_result:
  status: "BLOCKED"
  error_code: "FEATURE_NOT_IMPLEMENTED_REQUIRES_L1_FIC"
  implementation_authorized: false
  release_evidence: false
```

Exit codes:

```text
0 = success
1 = unexpected/tool/runtime error
2 = blocked by permission/governance gate or invalid user input
3 = validation/check failed
4 = controlled internal failure
5 = evidence write failure
```

CLI output should be YAML-like or JSON-like enough for tests to assert status, paths, and flags.

---

## 15. Generated State Policy

The MVP may create only:

```text
<target_repo>/.agentx/plans/
<target_repo>/.agentx/evidence/
<target_repo>/.agentx/tmp/
```

Plan-only mode must not modify existing target repository source, test, config, README, docs, or CI files.

`.agentx/tmp/` is not evidence.

Do not automatically edit `.gitignore`.

---

## 16. Tests Required

Create tests before or alongside implementation.

Minimum tests:

```text
[ ] package imports
[ ] CLI help works
[ ] inspect works on sample repo
[ ] plan works on sample repo
[ ] validate-plan accepts generated valid plan
[ ] validate-plan rejects malformed plan
[ ] no source files change in plan mode
[ ] .agentx/plans file is created
[ ] .agentx/evidence file is created
[ ] task asking deletion is blocked
[ ] task asking secret exfiltration is blocked
[ ] path traversal rejected
[ ] symlink escape rejected if platform supports it
[ ] binary file skipped
[ ] secret-like file skipped without reading contents
[ ] candidate ranking deterministic
[ ] unsafe config rejected
[ ] apply command absent or blocked
[ ] run-checks command absent or blocked
[ ] forbidden imports absent
```

Use fixture repos under:

```text
tests/fixtures/
```

Do not run tests against the real Agent_X repo as the primary fixture.

---

## 17. Smoke Test Script

Create:

```text
scripts/smoke_test_plan_only.py
```

Required behavior:

```text
1. Create/copy temporary sample repo.
2. Snapshot hashes of all non-.agentx files.
3. Run inspect.
4. Run plan.
5. Run validate-plan.
6. Snapshot hashes again.
7. Assert source hashes unchanged.
8. Assert plan and evidence files exist.
9. Assert apply/run-checks are blocked or absent.
10. Print machine-readable result.
```

Minimum result:

```yaml
agentx_code_mvp_smoke_test:
  status: "PASS|FAIL|BLOCKED"
  plan_only: true
  source_hashes_unchanged: true
  inspect_command_passed: true
  plan_command_passed: true
  validate_plan_passed: true
  apply_command_blocked: true
  evidence_written: true
  release_evidence: false
```

---

## 18. README Requirements

Create:

```text
L1/implementation_packages/coding_agent_mvp/README.md
```

Must say:

```text
- This is a plan-only Agent_X coding-agent MVP.
- It does not edit source files.
- It does not call model providers.
- It does not use GitHub APIs.
- It does not run arbitrary shell.
- It writes generated plan/evidence under .agentx/.
- It is L1-governed work.
- release_evidence is false.
```

Quickstart:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest tests -q
agentx-code inspect --repo /path/to/repo
agentx-code plan --repo /path/to/repo --task "Describe the change you want"
agentx-code validate-plan --plan /path/to/repo/.agentx/plans/<plan_id>.yaml
```

---

## 19. Required Commands to Run

From package root:

```bash
python -m compileall src
python -m pytest tests -q
python scripts/smoke_test_plan_only.py
```

Optional after install:

```bash
agentx-code --help
agentx-code inspect --repo tests/fixtures/sample_repo_basic
agentx-code plan --repo tests/fixtures/sample_repo_basic --task "Update README wording"
```

If any command cannot run, report it in completion evidence.

---

## 20. Completion Evidence

Create evidence under:

```text
L1/implementation_packages/coding_agent_mvp/evidence/
```

Required file:

```text
<timestamp>_coding_agent_mvp_completion_record.yaml
```

Minimum content:

```yaml
completion_record:
  package_id: "AGENT_X_CODE_MVP_001"
  status: "PLAN_ONLY_MVP_WORKING|BLOCKED|FAILED|PARTIAL"
  implementation_authorized_by_l1: true
  release_evidence: false
  files_created: []
  files_modified: []
  commands_run:
    - command: "python -m compileall src"
      result: "pass|fail|not-run"
    - command: "python -m pytest tests -q"
      result: "pass|fail|not-run"
    - command: "python scripts/smoke_test_plan_only.py"
      result: "pass|fail|not-run"
  checks_not_run: []
  source_files_modified_by_plan_mode: false
  unsafe_features_implemented: false
  deferred_features:
    - "diff builder"
    - "apply with approval"
    - "check runner"
    - "model provider"
    - "github integration"
  unresolved_risks: []
```

Also create:

```text
<timestamp>_coding_agent_mvp_review_packet.md
```

Review packet must summarize:

```text
- what was implemented;
- what was deferred;
- commands run;
- no-write verification result;
- permission-gate result;
- evidence paths;
- remaining risks.
```

---

## 21. Build Completion Decision Table

| State | Final status |
|---|---|
| No L1 package created | `NOT_STARTED` |
| Package exists but FICs missing | `BLOCKED_MISSING_FICS` |
| FICs exist but code missing | `PARTIAL_FIC_SCAFFOLD_ONLY` |
| Code exists but tests missing | `BLOCKED_TESTS_MISSING` |
| Inspect works, plan fails | `PARTIAL_INSPECT_ONLY` |
| Plan works, but source files modified | `REJECTED_UNSAFE_IMPLEMENTATION` |
| Plan works, evidence missing | `BLOCKED_EVIDENCE_MISSING` |
| Plan/inspect/validate-plan work and tests pass | `PLAN_ONLY_MVP_WORKING` |
| Apply/check/GitHub/model implemented without FIC | `REJECTED_SCOPE_DRIFT` |

Only `PLAN_ONLY_MVP_WORKING` counts as successful first-slice completion.

---

## 22. Final Response Required From Coding LLM

The coding LLM must end with this machine-readable summary:

```yaml
agentx_coding_llm_result:
  status: "PLAN_ONLY_MVP_WORKING|BLOCKED|FAILED|PARTIAL|REJECTED_SCOPE_DRIFT"
  package_root: "L1/implementation_packages/coding_agent_mvp"
  implementation_phase: "plan-only"
  files_created: []
  files_modified: []
  commands_run: []
  commands_not_run: []
  tests_passed: true
  compile_passed: true
  smoke_test_passed: true
  source_files_modified_by_plan_mode: false
  unsafe_features_implemented: false
  release_evidence: false
  implementation_notes: []
  deferred_features: []
  evidence_paths: []
```

No prose-only final answer is acceptable.

---

## 23. Stop Conditions

Stop immediately and return `BLOCKED` if:

```text
- asked to modify L0;
- asked to create runtime code under L2;
- asked to copy OpenCode source;
- asked to add model-provider calls in first slice;
- asked to add GitHub writes in first slice;
- asked to implement apply before permission gate and evidence writer exist;
- asked to run arbitrary shell;
- path safety cannot be implemented;
- evidence writer cannot be implemented;
- no-write test cannot be created;
- source files are modified during plan mode.
```

---

## 24. Done Definition

The task is done only when:

```text
[ ] L1 implementation package exists.
[ ] FIC package manifest exists.
[ ] Required FIC stubs exist.
[ ] Python package installs or runs with PYTHONPATH.
[ ] inspect command works.
[ ] plan command works.
[ ] validate-plan command works.
[ ] plan mode writes .agentx plan/evidence only.
[ ] plan mode modifies no source files.
[ ] unsafe tasks are blocked.
[ ] apply/run-checks are absent or blocked.
[ ] compileall passes.
[ ] pytest passes.
[ ] smoke test passes.
[ ] completion evidence exists.
[ ] final coding LLM result is machine-readable.
```

If these are not true, return `PARTIAL`, `BLOCKED`, or `FAILED`; do not claim success.

---

## 25. Optional Root Integration

Only after the MVP package works, optionally update root or L1 README with a short pointer:

```md
## Coding Agent MVP

`L1/implementation_packages/coding_agent_mvp/` contains a plan-only, L1-governed coding-agent MVP. It can inspect a repository and generate a patch plan, but it does not edit source files in the first slice.
```

Do not claim:

```text
- OpenCode compatibility;
- autonomous coding;
- GitHub integration;
- model-provider integration;
- release readiness.
```

---

## 26. Final Note

The correct target is:

```text
Agent_X-governed coding-agent MVP
```

not:

```text
OpenCode clone
OpenCode fork
full autonomous coding agent
```

Implement the smallest safe plan-only agent first. Deeper capabilities require separate L1 FICs, tests, evidence, and explicit permission gates.


---

## 27. v1.1 Coverage Upgrade Summary

Previous version rating: **9.4/10** for coding-LLM execution coverage.

The v1.0 TODO was strong enough to direct a disciplined coding model, but a weaker coding model could still make avoidable mistakes in these areas:

```text
- not reconciling an existing Agent_X repo before creating files;
- treating the FIC manifest as implementation authorization;
- producing a plan-only CLI that is hard to test because stdout schemas are loose;
- failing to create deterministic IDs in tests;
- silently skipping root/L1 integration checks;
- forgetting forbidden-import scans;
- not proving that only .agentx/ files changed in the target repo;
- not distinguishing target-repo .agentx evidence from Agent_X package evidence;
- not producing enough post-implementation audit material for review.
```

Fixes in `v1.1.0`:

```text
- added preflight repository reconciliation;
- added source-document placement and integrity rules;
- added exact implementation authorization state rules;
- added stdout schema requirements;
- added deterministic ID/time injection requirements for tests;
- added generated artifact and target-repo evidence separation;
- added forbidden import scan command;
- added no-write proof command contract;
- added package audit manifest;
- added root/L1 README update limits;
- added weak-coding-model sequencing and stop-on-first-unsafe-change rule;
- added final completion gate with required evidence artifacts.
```

Current rating after v1.1 corrections: **10/10 for coding-LLM plan-only MVP execution handoff coverage**.

This score does not mean the agent already exists. It means a coding LLM has enough instructions to create the first plan-only MVP safely if it follows the document.

---

## 28. Preflight Repository Reconciliation

Before creating or editing files, the coding LLM must inspect the current repository state.

Required preflight checks:

```text
[ ] Confirm repository root contains L0/, L1/, and L2/.
[ ] Confirm examples/ exists or create it only for documentation source files.
[ ] Confirm no executable coding-agent package already exists at L1/implementation_packages/coding_agent_mvp/.
[ ] If the package already exists, inspect before modifying and preserve existing valid work.
[ ] Do not delete or rename existing governed files without explicit migration instructions.
[ ] Do not move L0, L1, or L2 directories.
[ ] Do not modify existing L0 code.
[ ] Do not create executable files under L2.
```

Required command suggestions:

```bash
git status --short
find L1 -maxdepth 3 -type d | sort
find L2 -maxdepth 3 -type d | sort
find examples -maxdepth 3 -type f | sort 2>/dev/null || true
```

Decision table:

| Observed state | Required action |
|---|---|
| Package path absent | Create package from this TODO. |
| Package path exists and is empty/scaffold only | Complete missing files without deleting valid scaffolds. |
| Package path exists with implementation code | Inspect and reconcile; do not overwrite blindly. |
| Runtime code appears under L2 | Stop with `REJECTED_SCOPE_DRIFT`. |
| L0 would need changes | Stop with `BLOCKED`. |
| Source documents missing | Add them as examples/docs first or report `BLOCKED_SOURCE_DOCS_MISSING`. |

---

## 29. Source Document Placement and Integrity

The coding LLM must keep the two source documents as documentation, not executable authority.

Recommended source placement:

```text
examples/evolutions/opencode_like_coding_agent.md
examples/evolutions/opencode_like_coding_agent_mvp_build_guide.md
```

Allowed alternatives:

```text
docs/examples/opencode_like_coding_agent.md
L1/implementation_packages/coding_agent_mvp/docs/source_material/
```

Rules:

```text
- Do not place the example document under L2 as an active profile unless doing full L2 conversion.
- Do not treat either source document as code.
- Do not edit the source documents while implementing the MVP unless the task explicitly asks for documentation updates.
- Record source document paths in the package README and evidence.
- If source documents are not present, continue only if their contents are supplied in the task context; otherwise stop.
```

Recommended evidence fields:

```yaml
source_documents:
  - path: "examples/evolutions/opencode_like_coding_agent.md"
    role: "example-only evolution scenario"
    present: true
  - path: "examples/evolutions/opencode_like_coding_agent_mvp_build_guide.md"
    role: "future L1-governed plan-only MVP build guide"
    present: true
```

---

## 30. Implementation Authorization State Rule

There are two different meanings of authorization that must not be confused.

```text
Document authority:
  The example/build-guide/TODO documents do not authorize implementation by themselves.

Task authority:
  If the user explicitly gives this TODO to a coding LLM and asks it to implement the MVP, the coding LLM may create the L1 implementation package described here, but must still mark release_evidence=false and keep the MVP plan-only.
```

Therefore:

```yaml
implementation_authorized_by_this_document_alone: false
implementation_authorized_by_current_user_task: true_if_user_explicitly_asked_to_implement
release_evidence: false
runtime_scope: "plan-only"
```

The FIC package manifest may use:

```yaml
implementation_authorized: true
implementation_authorized_basis: "explicit user task using AGENT_X_OPENCODE_LIKE_CODING_AGENT_CODING_LLM_TODO_v1_2.md"
release_evidence: false
phase: "plan-only"
```

If the coding LLM is only asked to review or plan, `implementation_authorized` must remain false.

---

## 31. Exact CLI Stdout Schemas

The CLI must emit predictable YAML or JSON. Prefer YAML for consistency with this guide.

### 31.1 `inspect` success

```yaml
inspect_result:
  status: "OK"
  repo_root: "<canonical absolute path>"
  files_scanned: 0
  files_skipped_count: 0
  language_hints: []
  test_paths: []
  evidence_path: "<path-or-null>"
  release_evidence: false
```

### 31.2 `plan` success

```yaml
plan_result:
  status: "PLAN_CREATED"
  plan_path: "<path>"
  completion_record_path: "<path>"
  approval_required: true
  edit_authorized: false
  source_files_modified: false
  release_evidence: false
```

### 31.3 `validate-plan` success

```yaml
validate_plan_result:
  status: "VALID"
  plan_path: "<path>"
  release_evidence: false
```

### 31.4 blocked result

```yaml
command_result:
  status: "BLOCKED"
  error_code: "<controlled-code>"
  message: "<short safe message>"
  release_evidence: false
```

Tests must parse stdout and assert these fields.

---

## 32. Deterministic ID and Time Injection

Tests must not rely on wall-clock time.

Implementation should support small internal helpers or injectable factories:

```text
make_plan_id(task_text, repo_root, fixed_time=None) -> str
make_timestamp(fixed_time=None) -> str
```

Rules:

```text
- Production may use current UTC time.
- Tests must be able to pass a fixed timestamp or monkeypatch the ID factory.
- Plan IDs must be unique enough for normal use but deterministic under tests.
- Evidence file names must not overwrite existing files.
```

Suggested plan ID format:

```text
PLAN-YYYYMMDDTHHMMSSZ-<8-char-sha256-prefix>
```

---

## 33. Target-Repo Generated Artifacts vs Package Evidence

Do not confuse two evidence locations.

### 33.1 Target repository generated artifacts

Written when a user runs the CLI against a target repo:

```text
<target_repo>/.agentx/plans/*.yaml
<target_repo>/.agentx/evidence/*.yaml
```

These prove command behavior for that target repo only.

### 33.2 Agent_X package implementation evidence

Written after implementing the package:

```text
L1/implementation_packages/coding_agent_mvp/evidence/*_coding_agent_mvp_completion_record.yaml
L1/implementation_packages/coding_agent_mvp/evidence/*_coding_agent_mvp_review_packet.md
L1/implementation_packages/coding_agent_mvp/evidence/*_coding_agent_mvp_audit_manifest.yaml
```

These summarize implementation and validation of the MVP package.

Rules:

```text
- Target-repo .agentx evidence is not release evidence.
- Package evidence is not release evidence.
- Both must keep release_evidence=false.
- Both must honestly list commands not run.
```

---

## 34. Forbidden Import and Side-Effect Scan

Add a test or script step that scans source files for forbidden imports and obvious side-effect APIs.

Forbidden in first slice:

```text
requests
httpx
aiohttp
urllib
socket
openai
anthropic
langchain
gitpython
subprocess
os.system
pty
paramiko
```

Allowed standard library modules include:

```text
argparse
pathlib
dataclasses
hashlib
json
os
sys
tempfile
shutil
stat
fnmatch
time
datetime
typing
```

Suggested command is specified in the full TODO as a local Python scan over `src/agentx_code/*.py`. If this scan is not run, report it under `commands_not_run`.

---

## 35. No-Write Proof Contract

The no-write proof is mandatory.

Test algorithm:

```text
1. Copy a fixture repo into a temporary directory.
2. Hash every file except paths under .agentx/.
3. Run inspect.
4. Run plan.
5. Run validate-plan.
6. Hash every file except paths under .agentx/ again.
7. Assert the hash maps are identical.
8. Assert .agentx/plans contains a plan.
9. Assert .agentx/evidence contains a completion record.
```

Required test name:

```text
test_no_write_in_plan_mode.py
```

Required assertion:

```text
source_files_modified_by_plan_mode == false
```

If this proof fails, final status must be `REJECTED_SCOPE_DRIFT` or `FAILED`, not `PLAN_ONLY_MVP_WORKING`.

---

## 36. Package Audit Manifest

Create an audit manifest after implementation.

Recommended path:

```text
L1/implementation_packages/coding_agent_mvp/evidence/<timestamp>_coding_agent_mvp_audit_manifest.yaml
```

Minimum content:

```yaml
coding_agent_mvp_audit_manifest:
  package_id: "AGENT_X_CODE_MVP_001"
  phase: "plan-only"
  package_root: "L1/implementation_packages/coding_agent_mvp"
  source_documents: []
  implementation_files: []
  test_files: []
  fic_files: []
  generated_target_repo_artifacts_allowed:
    - ".agentx/plans/"
    - ".agentx/evidence/"
  prohibited_features_confirmed_absent:
    - "model_provider_calls"
    - "github_writes"
    - "arbitrary_shell"
    - "apply_patch"
    - "autonomous_loop"
    - "l2_runtime_code"
  commands_run: []
  commands_not_run: []
  final_status: "PLAN_ONLY_MVP_WORKING|BLOCKED|FAILED|PARTIAL|REJECTED_SCOPE_DRIFT"
  release_evidence: false
```

---

## 37. Root and L1 Integration Limits

The coding LLM may update root or L1 README only after the MVP package exists and tests pass.

Allowed root README addition:

```md
## Coding Agent MVP

`L1/implementation_packages/coding_agent_mvp/` contains a plan-only, L1-governed coding-agent MVP. It can inspect a repository and generate a patch plan. The first slice does not edit source files, call model providers, use GitHub APIs, or run arbitrary shell commands.
```

Forbidden README claims:

```text
OpenCode clone
OpenCode-compatible
runtime autonomous agent
edits code automatically
GitHub integration working
model-provider integration working
release-ready
```

If README is updated, tests/evidence must mention the README update.

---

## 38. Weak-Coding-Model Sequencing Rule

A weaker coding model must implement in strict sequence and stop after the first blocking failure.

Strict sequence:

```text
1. Preflight repository reconciliation.
2. Source document placement check.
3. Create package directories.
4. Create FIC manifest and FIC stubs.
5. Create pyproject and README.
6. Create models and config loader.
7. Create repo context reader.
8. Create task classifier.
9. Create candidate selector.
10. Create patch plan builder.
11. Create permission gate.
12. Create evidence writer.
13. Create CLI.
14. Create tests and fixtures.
15. Create smoke test.
16. Run compileall.
17. Run pytest.
18. Run smoke test.
19. Run forbidden import scan.
20. Create package evidence.
21. Optionally update README pointer.
```

Stop if any step requires a forbidden feature.

---

## 39. Final Completion Gate v1.1

The coding LLM may report `PLAN_ONLY_MVP_WORKING` only if all are true:

```text
[ ] Source documents are present or their supplied content is recorded.
[ ] Package is under L1/implementation_packages/coding_agent_mvp/.
[ ] No executable code was created under L2.
[ ] No L0 files were modified.
[ ] FIC manifest and FIC stubs exist.
[ ] inspect works.
[ ] plan works.
[ ] validate-plan works.
[ ] plan mode writes only .agentx/plans and .agentx/evidence in target repo.
[ ] no-write test passes.
[ ] unsafe task tests pass.
[ ] forbidden import scan passes.
[ ] compileall passes.
[ ] pytest passes.
[ ] smoke test passes.
[ ] package evidence exists.
[ ] audit manifest exists.
[ ] unsafe future features are absent or blocked stubs only.
[ ] release_evidence=false everywhere.
```

If any item is false, use `PARTIAL`, `BLOCKED`, `FAILED`, or `REJECTED_SCOPE_DRIFT`.


---

## 40. v1.2 Coverage Upgrade Summary

Previous pair rating: **9.8/10** for coding-LLM execution coverage.

The v1.1 TODO/prompt pair was strong enough for a disciplined coding model, but a final review found several practical gaps that could still cause inconsistent implementations:

```text
- FIC stub content was described but not templated exactly;
- implementation authorization fields could be misread as release authorization;
- the forbidden-import scan was described but not given as a copy-paste script;
- CLI output was allowed to be YAML-like or JSON-like instead of choosing one canonical format;
- idempotency/re-run behavior was not explicit;
- package evidence and target-repo evidence could still be mixed during tests;
- a weaker model could implement too much in the first pass by adding diff/check/apply stubs with side effects;
- final review did not require a clean verification pass.
```

Fixes in `v1.2.0`:

```text
- added exact FIC stub template;
- added canonical stdout format: YAML only;
- added precise authorization vocabulary;
- added copy-paste forbidden import/side-effect scan script;
- added idempotency and re-run rules;
- added clean verification pass requirements;
- added target-repo versus implementation-package evidence separation test;
- added blocked-stub no-side-effect rules;
- added package README and root README claim scan;
- updated the copy-paste prompt to match the stricter v1.2 scope.
```

Current rating after v1.2 corrections: **10/10 for coding-LLM plan-only MVP execution handoff coverage**.

This rating means the instructions are complete enough for a coding LLM to implement the first plan-only MVP safely. It does not mean the MVP already exists.

---

## 41. Exact FIC Stub Template

Every required FIC markdown file under:

```text
L1/implementation_packages/coding_agent_mvp/fic/
```

must use this exact minimum structure, adjusted only for the unit name, target file, public surface, and tests.

````markdown
# <FIC Title>

**FIC ID:** `<FIC-MVP-###>`  
**Version:** `v0.1.0`  
**Status:** `ready-for-code`  
**Package:** `AGENT_X_CODE_MVP_001`  
**Phase:** `plan-only`  
**Target file:** `<src/agentx_code/...py>`  
**Test file:** `<tests/test_...py>`  
**Implementation authorized by user task:** `true`  
**Release evidence:** `false`

## Purpose

<One-paragraph purpose for this unit.>

## Public Surface

```text
<exact public functions/classes/errors>
```

## Allowed Behavior

```text
- <allowed behavior>
```

## Forbidden Behavior

```text
- no network access
- no model-provider calls
- no GitHub operations
- no arbitrary shell execution
- no source-file mutation in plan-only mode
- no writes outside allowed .agentx generated-state directories
```

## Inputs

```text
<declared inputs>
```

## Outputs

```text
<declared outputs>
```

## Required Tests

```text
- <test requirement>
```

## Evidence Requirements

```text
- command results must be reported in package completion evidence
- release_evidence must remain false
```

## Stop Conditions

```text
- stop if implementing this unit requires a forbidden behavior
```
````

Rules:

```text
- FIC stubs are not decorative. Each target source file must have exactly one FIC stub.
- A source file without a FIC stub is not allowed in the package.
- A FIC stub must not claim release readiness.
- A FIC stub must not authorize apply/check/model/GitHub behavior unless that unit is explicitly part of a later phase.
```

---

## 42. Canonical CLI Output Format

The CLI must emit **YAML only** for machine-readable command output in the first MVP slice.

Rules:

```text
- stdout must contain exactly one YAML document for inspect, plan, and validate-plan.
- stderr may contain short human-readable diagnostics only on failure.
- tests must parse stdout with yaml.safe_load.
- success outputs must not include stack traces.
- blocked outputs must include a controlled error_code.
```

Success schemas remain those in Section 31, but the implementation must choose YAML, not JSON-like text.

Required serialization behavior:

```text
- use yaml.safe_dump;
- sort keys only where it does not reduce readability;
- never dump Python object reprs;
- never include file contents;
- never include secrets;
- release_evidence must be false in every command output.
```

---

## 43. Precise Authorization Vocabulary

Use these exact fields to avoid confusing document authority, user-task authority, L1 package scope, and release evidence.

In documentation/FIC/source docs:

```yaml
implementation_authorized_by_this_document_alone: false
implementation_authorized_by_current_user_task: true
implementation_scope: "L1/implementation_packages/coding_agent_mvp plan-only MVP"
release_evidence: false
```

In `fic_package_manifest.yaml`:

```yaml
implementation_authorized: true
implementation_authorized_basis: "explicit user task using AGENT_X_OPENCODE_LIKE_CODING_AGENT_CODING_LLM_TODO_v1_2.md"
implementation_scope: "plan-only MVP"
release_evidence: false
```

In generated plan/evidence files written by the CLI into target repositories:

```yaml
implementation_authorized: false
edit_authorized: false
release_evidence: false
```

Rules:

```text
- Package implementation may be authorized by the explicit user task.
- Editing target repositories is not authorized in the first slice.
- Release evidence is always false.
- L2 runtime remains unauthorized.
```

---

## 44. Copy-Paste Forbidden Import and Side-Effect Scan

After implementation, run this command from:

```text
L1/implementation_packages/coding_agent_mvp/
```

````bash
python - <<'SCAN_PY'
from pathlib import Path

root = Path('src/agentx_code')
forbidden_tokens = [
    'import requests', 'from requests',
    'import httpx', 'from httpx',
    'import aiohttp', 'from aiohttp',
    'import urllib', 'from urllib',
    'import socket', 'from socket',
    'import openai', 'from openai',
    'import anthropic', 'from anthropic',
    'import langchain', 'from langchain',
    'import git', 'from git',
    'import subprocess', 'from subprocess',
    'os.system(', 'pty.', 'paramiko',
    'shell=True',
]
violations = []
for path in sorted(root.glob('*.py')):
    text = path.read_text(encoding='utf-8')
    for token in forbidden_tokens:
        if token in text:
            violations.append((path.as_posix(), token))
if violations:
    for path, token in violations:
        print(f'FORBIDDEN_IMPORT_OR_SIDE_EFFECT {path}: {token}')
    raise SystemExit(1)
print('FORBIDDEN_IMPORT_SCAN PASS')
SCAN_PY
````

Rules:

```text
- If this scan fails, final status cannot be PLAN_ONLY_MVP_WORKING.
- If the scan is not run, list it under commands_not_run and do not claim full success.
- Do not weaken the scan by removing tokens without recording the reason in evidence.
```

---

## 45. Idempotency and Re-Run Rules

The implementation must be safe to run more than once.

Required behavior:

```text
- Running inspect multiple times may create additional timestamped evidence only if evidence is enabled for inspect.
- Running plan multiple times must not overwrite an existing plan.
- Evidence writer must never overwrite existing evidence.
- Existing .agentx/plans and .agentx/evidence directories must be preserved.
- Tests must use temporary directories and must not mutate checked-in fixtures.
```

Required tests:

```text
[ ] running plan twice produces two distinct plan paths or a controlled duplicate-path block;
[ ] running validate-plan twice does not modify the plan file;
[ ] smoke test can run twice without corrupting fixture source files;
[ ] evidence files are append-only by filename.
```

---

## 46. Clean Verification Pass

After the coding LLM finishes implementation, it must perform a final verification pass from a clean or controlled working tree state.

Required checks:

```bash
git status --short
cd L1/implementation_packages/coding_agent_mvp
python -m compileall src
python -m pytest tests -q
python scripts/smoke_test_plan_only.py
# run the forbidden import scan from Section 44
```

Required review statements in the package audit manifest:

```yaml
clean_verification:
  git_status_reviewed: true
  compileall_passed: true
  pytest_passed: true
  smoke_test_passed: true
  forbidden_import_scan_passed: true
  no_l0_files_modified: true
  no_l2_runtime_files_created: true
  no_target_repo_source_files_modified_by_plan_mode: true
  release_evidence: false
```

If the working tree contains unrelated user changes, the coding LLM must not claim those changes as its own. It must list them as pre-existing or unresolved.

---

## 47. Blocked Stub No-Side-Effect Rule

If deferred commands or modules are present, they must be side-effect-free.

Deferred commands/modules:

```text
apply
run-checks
diff_builder.py
check_runner.py
model_provider_adapter.py
github integration
session_store.py
```

Blocked stubs may:

```text
- return a controlled BLOCKED result;
- print a YAML blocked result;
- document why the feature requires later L1 FIC work.
```

Blocked stubs must not:

```text
- write files;
- read secrets;
- call shell;
- call network;
- edit repositories;
- import forbidden dependencies;
- create Git commits, branches, PRs, or issue comments.
```

Required test:

```text
A future/deferred command, if exposed, returns controlled blocked output and modifies no source files.
```

---

## 48. Documentation Claim Scan

If README files are created or updated, scan them for false claims.

Required files to inspect if present:

```text
README.md
L1/README.md
L1/implementation_packages/coding_agent_mvp/README.md
examples/README.md
```

Forbidden claims:

```text
OpenCode clone
OpenCode-compatible
autonomous coding agent
edits code automatically
GitHub integration working
model-provider integration working
release-ready
production-ready
```

Allowed claim:

```text
plan-only, L1-governed coding-agent MVP
```

Record the claim scan in the audit manifest.

---

## 49. Final Completion Gate v1.2

The coding LLM may report `PLAN_ONLY_MVP_WORKING` only if all v1.1 checks pass and these additional checks pass:

```text
[ ] every source file has exactly one FIC stub;
[ ] CLI output is YAML and parseable by tests;
[ ] authorization vocabulary is consistent;
[ ] forbidden import scan script passes;
[ ] idempotency tests pass;
[ ] blocked stubs, if present, have no side effects;
[ ] clean verification pass is recorded;
[ ] documentation claim scan is recorded;
[ ] audit manifest includes pre-existing/unrelated changes if any;
[ ] release_evidence=false remains true across package docs, CLI outputs, target repo generated artifacts, package evidence, and audit manifest.
```

If any item fails, use `PARTIAL`, `BLOCKED`, `FAILED`, or `REJECTED_SCOPE_DRIFT`.
