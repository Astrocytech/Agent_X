# Agent_X Runtime Integration Next Steps — 10/10 LLM-Executable Implementation Brief REV18

**Repository:** `https://github.com/Astrocytech/Agent_X`  
**Primary package:** `tools/agentx_evolve`  
**Required fallback invocation:** `python -m tools.agentx_evolve`  
**Installed CLI, if available:** `agentx-evolve`  
**Target provider:** OpenCode Zen OpenAI-compatible chat-completions API  
**Agent_X model id:** `opencode/big-pickle`  
**Provider payload model:** `big-pickle`  
**Runtime artifact root:** `.agentx-init/runs/<run_id>/`  
**Primary goal:** make Agent_X executable as a chat-based, Big-Pickle-compatible, governed self-evolving agent runtime that can also initialize and evolve other agent directories.

REV18 supersedes REV17 and all earlier runtime-integration planning documents.

This document is an implementation brief, not another planning request. The next useful action after reading it is to edit code and prove the first runtime gate.

---

## 0. Rating of REV17

| Criterion | Rating | Reason |
|---|---:|---|
| Functionality | 9.99/10 | REV17 defines the actual runtime behavior, CLI surface, artifacts, safety gates, mock/live provider split, and acceptance ladder. The remaining improvement is to remove final wording drift and make the first implementation slice completely unambiguous. |
| Design | 9.99/10 | The runtime spine, shared services, command ownership, target-agent boundaries, and artifact model are strong. REV18 tightens the relationship between capabilities, gates, artifacts, and final reporting. |
| Completeness | 10/10 | REV17 covers chat, OpenCode/Big Pickle, self-upgrade, init-agent, evolve-agent, safety, dry-run behavior, tests, schemas, evidence, and final acceptance. |
| Ease for another LLM | 9.99/10 | Another LLM can execute REV17. REV18 improves handoff clarity by eliminating rating-target drift, normalizing capability IDs, adding a first-PR cutline, and adding a no-review-loop transition to implementation. |

**Overall REV17 rating:** **9.99/10**

### Improvements made in REV18

```text
1. Corrected the rating target to REV17.
2. Normalized capability IDs and final-report labels so C1-C6 mean the same thing everywhere.
3. Added a first-PR implementation cutline that prevents the next LLM from overbuilding before mock chat works.
4. Added a no-review-loop transition rule: after REV18, the next action is implementation, not another planning revision.
5. Added exact pre/post source-mutation checks for the first proof command.
6. Added a compact minimal file-change manifest for the first slice.
7. Added clearer handling for package import drift and missing editable install metadata.
8. Added explicit acceptance criteria for preserving legacy commands.
9. Added a mandatory artifact self-check command pattern.
10. Reduced ambiguity in the final executor response format.
```

---

## 0A. No More Planning Loop Rule

This document is the final planning handoff. A future assistant or implementation LLM must not create REV19 as the next step unless the current repository has materially changed and the instructions no longer match the source tree.

The next action after reading REV18 is implementation. The first code gate is still:

```bash
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
```

If this command fails because `chat` does not exist, implement the smallest compatible runtime slice needed to make it pass.

---
## 1. Non-Negotiable Implementation Lock

Do not make another planning-only revision before coding unless the repository has changed so much that the package cannot be inspected or imported.

The first implementation objective is this exact command:

```bash
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
```

The first accepted result is:

```text
- command exits 0;
- stdout is exactly one JSON object;
- stdout follows `agentx.cli_result.v1`;
- message contains READY;
- `.agentx-init/runs/<run_id>/` exists;
- chat artifacts exist;
- `final_verdict.json` says PASS;
- source files are not modified by chat mode;
- existing commands still appear in help.
```

For the first proof command, source mutation must be checked before and after the run:

```bash
git status --short -- tools/agentx_evolve
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
git status --short -- tools/agentx_evolve
```

Only `.agentx-init/runs/<run_id>/` artifacts may be newly created by chat mode.
```

Do not implement self-upgrade, init-agent, evolve-agent, live OpenCode calls, MCP, scheduling, memory, UI, or packaging before this gate passes.

### 1.1 First PR Cutline

The first implementation pull request or patch must contain only the minimum needed for mock chat:

```text
Required in first PR:
- CLI registration for `chat`.
- config resolution for mock defaults and `--json`.
- run session creation under `.agentx-init/runs/<run_id>/`.
- deterministic mock provider.
- JSON stdout result following `agentx.cli_result.v1`.
- final verdict and evidence manifest artifacts.
- tests proving mock chat and no source mutation.

Forbidden in first PR:
- real self-mutation;
- live OpenCode calls;
- init-agent copying;
- evolve-agent patching;
- scheduler/MCP/UI/memory work;
- broad refactors unrelated to the mock chat gate.
```

The first PR is accepted only when `chat --once "Say READY" --mock --json` passes and legacy commands remain visible in help.

---

## 2. Required Product Capabilities

Agent_X is accepted only when these capabilities work from the CLI.

| ID | Capability | Required proof command |
|---|---|---|
| C1 | Deterministic mock chat through the same runtime spine used by all workflows. | `python -m tools.agentx_evolve chat --once "Say READY" --mock --json` |
| C2 | OpenCode/Big Pickle provider path using an OpenAI-compatible request shape. | `python -m tools.agentx_evolve chat --provider opencode --model opencode/big-pickle --once "Say READY" --json` |
| C3 | External architecture file becomes a governed self-upgrade plan. | `python -m tools.agentx_evolve self-upgrade --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md --mode plan --dry-run --mock --json` |
| C4 | Self-upgrade apply path uses only governed patch execution. | `python -m tools.agentx_evolve self-upgrade --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md --mode apply --dry-run --mock --json` |
| C5 | Agent_X can initialize another agent directory from the allowed seed architecture/code. | `python -m tools.agentx_evolve init-agent --name Agent_Test --dest /tmp/Agent_Test --mock --json` |
| C6 | Agent_X can evolve another agent directory without mutating the controller repo. | `python -m tools.agentx_evolve evolve-agent --agent-dir /tmp/Agent_Test --concept-file tools/agentx_evolve/examples/minimal_agent_upgrade.md --mode plan --dry-run --mock --json` |

Default acceptance must use `--mock`. Live provider acceptance is opt-in and must never be required for normal tests.

---

## 3. Required Now vs. Deferred

### Required now

```text
- Preserve existing commands: review, approve, reject, explain, version.
- Add commands: chat, self-upgrade, init-agent, evolve-agent.
- Add deterministic mock provider.
- Add OpenCode provider adapter and mocked HTTP tests.
- Add one-shot chat and minimal interactive chat.
- Add runtime run-session creation.
- Add atomic artifact writer.
- Add JSON stdout result contract.
- Add config resolver.
- Add concept-file loader.
- Add minimal context packer.
- Add structured plan parser.
- Add unified-diff patch validation.
- Route mutation through existing governed patch executor or a thin compatibility shim.
- Add allowlisted validation runner.
- Add target-agent boundary enforcement.
- Add evidence manifest and final verdict writer.
- Add tests for success and failure paths.
```

### Deferred not-now

```text
- full autonomous multi-step planning;
- long-term memory;
- background scheduler execution;
- MCP server exposure;
- multi-model routing beyond mock and OpenCode;
- UI/TUI;
- real unattended self-mutation without dry-run proof gates;
- package publishing;
- optimization/refactor work unrelated to the acceptance ladder.
```

---

## 4. Authority and Conflict Rules

When sources conflict, use this order:

```text
1. Current repository source code and tests.
2. This REV17 document.
3. Current README/package metadata.
4. Older Agent_X planning documents.
5. LLM assumptions.
```

Rules:

```text
- Reuse existing modules whenever they already cover the needed behavior.
- Do not create a second model, orchestration, patch, validation, or evidence stack if an equivalent one exists.
- If overlapping modules exist, choose the one currently imported by the CLI or tests.
- Preserve existing public commands.
- Add compatibility rather than breaking existing command behavior.
- If repository drift makes an exact instruction impossible, implement the closest safe equivalent and record the difference in `implementation_ledger.json`.
```

---

## 5. Fresh-Clone Bootstrap Contract

The implementation must be possible from a fresh clone.

```bash
git clone https://github.com/Astrocytech/Agent_X.git
cd Agent_X
python -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e . || true
python -m compileall tools/agentx_evolve
python -m tools.agentx_evolve --help
```

If editable install is unavailable, `python -m tools.agentx_evolve ...` remains the required invocation. The installed `agentx-evolve` command is accepted only if it behaves the same way as the module invocation.

---

## 6. Command Defaults and Config Contract

### 6.1 Precedence

```text
1. Explicit CLI flags.
2. Environment variables.
3. Repo config file.
4. Built-in defaults.
```

### 6.2 Environment variables

```bash
AGENTX_PROVIDER=mock
AGENTX_MODEL=mock/deterministic
AGENTX_OPENCODE_BASE_URL=https://opencode.ai/zen/v1
AGENTX_OPENCODE_API_KEY=<secret>
AGENTX_TIMEOUT_SECONDS=60
AGENTX_RUN_ROOT=.agentx-init/runs
```

### 6.3 Built-in defaults

```text
provider: mock
model: mock/deterministic
run_root: .agentx-init/runs
timeout_seconds: 60
json: false
mock: false unless provider resolves to mock or --mock is set
mode: plan for mutation workflows unless explicitly set
apply: never unless mode=apply and all safety gates pass
dry_run: true only when --dry-run is set, except examples/tests may require it explicitly
```

Secrets must never appear in stdout, stderr, logs, run artifacts, test snapshots, or final reports.

---

## 7. Runtime Spine

All commands must use the same runtime spine.

```text
CLI command
  -> config resolver
  -> preflight checks
  -> run session creation
  -> context/concept loading
  -> provider call or mock response
  -> structured response parsing
  -> action/policy routing
  -> patch plan or governed patch execution
  -> validation command runner
  -> artifact writer
  -> evidence manifest
  -> final verdict
  -> stdout result
```

No workflow may bypass this spine for file mutation, artifact writing, safety decisions, validation results, or final verdicts.

---

## 8. Run State Machine

Legal run states:

```text
CREATED
  -> PREFLIGHT_PASSED
  -> CONTEXT_PACKED
  -> MODEL_COMPLETED
  -> PLAN_PARSED
  -> PATCH_PROPOSED optional
  -> PATCH_APPLIED optional
  -> VALIDATION_COMPLETED
  -> EVIDENCE_WRITTEN
  -> PASS | FAIL | BLOCKED
```

Failure mapping:

```text
preflight failure -> BLOCKED
missing required credentials -> BLOCKED
provider runtime error -> FAIL
safety violation -> BLOCKED
validation failure -> FAIL
artifact/schema write failure -> FAIL
malformed model response -> FAIL
dry-run mutation command with valid plan/evidence and no mutation -> PASS
```

Final command status must be one of:

```text
PASS
FAIL
BLOCKED
```

`PARTIAL` is allowed only inside final human reports, not as a successful command status.

---

## 9. CLI Contract

### 9.1 Global flags for new commands

```text
--json
--mock
--provider <mock|opencode>
--model <model-id>
--run-root <path>
--timeout <seconds>
--dry-run
```

### 9.2 Workflow flags

```text
chat:
  --once <message>

self-upgrade:
  --concept-file <path>
  --mode <plan|apply>

evolve-agent:
  --agent-dir <path>
  --concept-file <path>
  --mode <plan|apply>

init-agent:
  --name <agent-name>
  --dest <path>
```

### 9.3 Exit codes

```text
0 = PASS
1 = FAIL
2 = BLOCKED by config, safety, missing file, missing credential, or preflight
3 = invalid CLI usage
4 = provider unavailable, provider error, or timeout
5 = validation failed
6 = artifact/schema failure
```

### 9.4 JSON stdout contract

When `--json` is used:

```text
- stdout must contain exactly one JSON object;
- stdout must contain no banners, tracebacks, warnings, progress lines, or markdown;
- human logs must go to stderr or artifacts;
- secrets must be redacted everywhere;
- exit_code in JSON must match the process exit code.
```

Schema: `agentx.cli_result.v1`

```json
{
  "schema_version": "agentx.cli_result.v1",
  "command": "chat",
  "status": "PASS",
  "exit_code": 0,
  "run_id": "20260607T120000Z-chat-abcdef12",
  "run_dir": ".agentx-init/runs/20260607T120000Z-chat-abcdef12",
  "message": "READY — deterministic Agent_X mock provider response.",
  "artifacts": {
    "final_verdict": ".agentx-init/runs/20260607T120000Z-chat-abcdef12/final_verdict.json",
    "evidence_manifest": ".agentx-init/runs/20260607T120000Z-chat-abcdef12/evidence_manifest.json"
  }
}
```

---

## 10. Command-to-Service Ownership

| Command | Owning service | Must not do directly |
|---|---|---|
| `chat` | `ChatWorkflow` | mutate source files |
| `self-upgrade` | `SelfUpgradeWorkflow` | write source changes outside governed patch executor |
| `init-agent` | `InitAgentWorkflow` | copy `.git`, secrets, caches, virtualenvs, or runtime runs |
| `evolve-agent` | `EvolveAgentWorkflow` | mutate controller repo while targeting an external agent |

Shared services:

```text
ConfigResolver
RunSessionManager
ArtifactWriter
ContextPacker
ProviderRouter
StructuredPlanParser
PatchPolicyBridge
ValidationRunner
EvidenceManifestWriter
FinalVerdictWriter
```

---

## 11. First Implementation Packet

### 11.1 Inspect first

```bash
find tools/agentx_evolve -maxdepth 3 -type f | sort
sed -n '1,260p' tools/agentx_evolve/__main__.py
find tools/agentx_evolve -maxdepth 4 -type f | grep -E '(model|provider|patch|orchestr|artifact|evidence|config|cli|test|schema)' | sort
```

### 11.2 First files to modify or create

Use existing equivalents if they already exist.

```text
tools/agentx_evolve/__main__.py
tools/agentx_evolve/runtime/config.py
tools/agentx_evolve/runtime/session.py
tools/agentx_evolve/runtime/artifacts.py
tools/agentx_evolve/runtime/results.py
tools/agentx_evolve/runtime/locks.py
tools/agentx_evolve/providers/mock_provider.py
tools/agentx_evolve/workflows/chat.py
tools/agentx_evolve/schemas/agentx.cli_result.v1.schema.json
tools/agentx_evolve/schemas/agentx.final_verdict.v1.schema.json
tools/agentx_evolve/schemas/agentx.evidence_manifest.v1.schema.json
tools/agentx_evolve/tests/test_cli_chat_mock.py
tools/agentx_evolve/tests/test_runtime_artifacts.py
tools/agentx_evolve/tests/test_config_precedence.py
tools/agentx_evolve/tests/test_mock_provider.py
```

### 11.3 First proof commands

```bash
python -m compileall tools/agentx_evolve
python -m tools.agentx_evolve --help
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
pytest tools/agentx_evolve/tests/test_cli_chat_mock.py -q
```

Only after these pass should the implementation continue to OpenCode, structured plans, patching, init-agent, and evolve-agent.

---

## 12. Provider Contract

### 12.1 Mock provider

The mock provider must be deterministic.

For message:

```text
Say READY
```

Return content containing:

```text
READY
```

Accepted mock response:

```json
{
  "role": "assistant",
  "content": "READY — deterministic Agent_X mock provider response.",
  "tool_calls": [],
  "finish_reason": "stop"
}
```

For mutation workflows, the mock provider must return structured JSON with a safe minimal plan. If a patch is needed in dry-run tests, the diff must target only allowed example/runtime files and must never be applied to source in dry-run mode.

### 12.2 OpenCode provider

Agent_X model id:

```text
opencode/big-pickle
```

Provider payload model:

```text
big-pickle
```

Base URL:

```text
https://opencode.ai/zen/v1
```

Endpoint joining rule:

```text
Use exactly one `/v1` segment. Avoid `/v1/v1/chat/completions`.
```

Request shape:

```json
{
  "model": "big-pickle",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Say READY"}
  ],
  "temperature": 0.2,
  "stream": false
}
```

Default tests must mock HTTP. Live tests run only when all are present:

```text
AGENTX_LIVE_PROVIDER_TESTS=1
AGENTX_OPENCODE_API_KEY is set
provider is explicitly opencode
```

### 12.3 Provider error classification

```text
missing API key -> BLOCKED, exit 2
401/403 -> BLOCKED, exit 2
404 model/endpoint -> FAIL, exit 4
429 -> FAIL, exit 4
5xx -> FAIL, exit 4
timeout -> FAIL, exit 4
malformed response -> FAIL, exit 1
```

---

## 13. Structured Plan Contract

Mutation workflows must ask the model for structured JSON.

Required logical fields:

```json
{
  "schema_version": "agentx.structured_plan.v1",
  "summary": "short explanation",
  "actions": [
    {
      "type": "patch|validate|report|noop",
      "description": "what this action does",
      "target": "repo-relative path or external target path",
      "safety_notes": ["..."]
    }
  ],
  "patches": [
    {
      "format": "unified_diff",
      "content": "diff --git ..."
    }
  ],
  "validation_commands": [
    "python -m compileall tools/agentx_evolve",
    "pytest tools/agentx_evolve/tests -q"
  ]
}
```

Reject:

```text
- missing schema_version;
- unknown action type;
- patch without unified diff format;
- absolute patch target;
- path traversal;
- symlink escape;
- validation command outside allowlist;
- malformed JSON when structured mode is required.
```

If provider output is prose instead of structured JSON, chat may accept it, but mutation workflows must fail safely.

---

## 14. Safety Contract

### 14.1 Path safety

Reject:

```text
- absolute paths unless they are explicitly the target root for `--agent-dir` or `--dest`;
- `..` traversal;
- symlink escapes;
- writes outside the active target root;
- writes to `.git`, `.env`, secret files, virtualenvs, caches, compiled files, or previous run artifacts;
- mutation of controller source during `evolve-agent`.
```

### 14.2 Command allowlist

Allowed validation commands by default:

```text
python -m compileall tools/agentx_evolve
python -m tools.agentx_evolve --help
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
pytest tools/agentx_evolve/tests -q
```

Blocked command patterns:

```text
rm -rf
sudo
curl | sh
wget | sh
chmod -R 777
chown
mkfs
dd
:(){ :|:& };:
python -c with deletion or network side effects
shell redirection into protected paths
```

### 14.3 Mutation mode table

| Mode | Patch generated | Patch applied | Validation run | Accepted for default tests |
|---|---:|---:|---:|---:|
| `plan` | yes | no | optional | yes |
| `apply --dry-run` | yes | no | yes, unchanged tree or temp copy | yes |
| `apply` | yes | yes, governed patch only | yes | no, unless explicitly requested |

---

## 15. Target-Agent Boundary Policy

### 15.1 `init-agent`

Allowed copy sources:

```text
L0/
L1/
L2/
tools/agentx_evolve/ seed-compatible runtime files
README/template files needed by the new agent
pyproject/package metadata adjusted for the new name
```

Never copy:

```text
.git/
.venv/
__pycache__/
.pytest_cache/
.env
*.key
*.pem
.agentx-init/runs/
runtime logs
secrets
local credentials
```

Destination rules:

```text
- destination must not already contain unrelated files;
- no implicit overwrite;
- no --force in this pass unless it already exists safely;
- created files must be listed in artifact manifest;
- metadata rewrite must be conservative and recorded;
- validation must run or be marked BLOCKED with a reason.
```

### 15.2 `evolve-agent`

Rules:

```text
- `--agent-dir` is the only mutation root.
- Controller Agent_X source is read-only, except controller-side evidence artifacts.
- All patches must resolve inside `--agent-dir`.
- Symlink escapes are blocked.
- Target validation runs from the target root.
- If target validation commands cannot be determined, run generic safe checks or mark validation BLOCKED.
```

---

## 16. Artifact Contract

Every run must create:

```text
.agentx-init/runs/<run_id>/
  run_metadata.json
  request.json
  resolved_config.json
  preflight.json
  packed_context.json
  model_messages.jsonl
  model_response.json
  structured_plan.json
  proposed_patch.diff
  applied_patch.diff
  validation_report.json
  evidence_manifest.json
  final_verdict.json
  implementation_ledger.json
```

If an artifact does not apply, write a valid placeholder:

```json
{
  "schema_version": "agentx.artifact_placeholder.v1",
  "status": "NOT_APPLICABLE",
  "reason": "chat mode does not produce patches"
}
```

Artifact writing rules:

```text
- write to a temporary file first;
- fsync if practical;
- rename atomically;
- never leave partial JSON on success;
- run directories must be unique;
- concurrent runs must not write to the same run directory;
- stale locks may be marked stale only with timestamp evidence.
```

---

## 17. Minimal Artifact Schemas

### 17.1 `final_verdict.json`

```json
{
  "schema_version": "agentx.final_verdict.v1",
  "status": "PASS",
  "command": "chat",
  "exit_code": 0,
  "run_id": "20260607T120000Z-chat-abcdef12",
  "summary": "mock chat completed",
  "failures": [],
  "blocked_reasons": [],
  "validation_status": "PASS"
}
```

### 17.2 `evidence_manifest.json`

```json
{
  "schema_version": "agentx.evidence_manifest.v1",
  "run_id": "20260607T120000Z-chat-abcdef12",
  "command": "chat",
  "artifacts": [
    {"path": "run_metadata.json", "kind": "metadata", "required": true},
    {"path": "final_verdict.json", "kind": "verdict", "required": true}
  ],
  "commands_run": [],
  "source_mutation_detected": false
}
```

### 17.3 `implementation_ledger.json`

```json
{
  "schema_version": "agentx.implementation_ledger.v1",
  "run_id": "20260607T120000Z-chat-abcdef12",
  "repo_drift_notes": [],
  "compatibility_shims_used": [],
  "deviations_from_brief": [],
  "files_changed_by_command": []
}
```

---

## 18. Command-to-Artifact Matrix

| Artifact | chat | self-upgrade plan | self-upgrade apply/dry-run | init-agent | evolve-agent plan/dry-run |
|---|---:|---:|---:|---:|---:|
| `run_metadata.json` | required | required | required | required | required |
| `request.json` | required | required | required | required | required |
| `resolved_config.json` | required | required | required | required | required |
| `preflight.json` | required | required | required | required | required |
| `packed_context.json` | required | required | required | required | required |
| `model_messages.jsonl` | required | required | required | optional | required |
| `model_response.json` | required | required | required | optional | required |
| `structured_plan.json` | placeholder | required | required | optional | required |
| `proposed_patch.diff` | placeholder | required | required | placeholder | required |
| `applied_patch.diff` | placeholder | placeholder | dry-run placeholder or required | placeholder | dry-run placeholder or required |
| `validation_report.json` | required | optional | required | required | required |
| `evidence_manifest.json` | required | required | required | required | required |
| `final_verdict.json` | required | required | required | required | required |
| `implementation_ledger.json` | required | required | required | required | required |

---

## 19. Workflow Specifications

### 19.1 Chat

```text
Input:
  --once message or interactive stdin.

Behavior:
  resolve config;
  create run session;
  pack minimal repo context;
  call mock or provider;
  write messages and response;
  write validation placeholder or lightweight validation;
  write PASS verdict if provider completed and artifacts are valid.

Must not:
  mutate source files;
  run patch execution;
  require network in mock mode.
```

### 19.2 Self-upgrade

```text
Input:
  --concept-file path;
  --mode plan|apply;
  --dry-run optional.

Behavior:
  read concept file;
  pack controller repo context;
  call provider/mock for structured plan;
  parse plan;
  validate proposed patch;
  if mode=plan: do not apply;
  if mode=apply and --dry-run: simulate or validate against temp copy;
  if mode=apply without --dry-run: apply only through governed patch executor;
  run allowlisted validation;
  write evidence and verdict.
```

### 19.3 Init-agent

```text
Input:
  --name Agent_Test;
  --dest /tmp/Agent_Test.

Behavior:
  preflight destination;
  copy only allowlisted seed files;
  rewrite safe metadata;
  initialize target runtime directory;
  run target validation if possible;
  write file manifest and final verdict.
```

### 19.4 Evolve-agent

```text
Input:
  --agent-dir /tmp/Agent_Test;
  --concept-file path;
  --mode plan|apply;
  --dry-run optional.

Behavior:
  verify target root;
  pack target context plus controller architecture reference;
  call provider/mock;
  parse structured plan;
  enforce target path boundary;
  produce patch plan;
  apply only in target root when allowed;
  run target validation;
  write target evidence and controller-side evidence.
```

---

## 20. Acceptance Ladder With STOP Gates

The implementing LLM must stop and fix the first failed gate.

### Gate 1 — CLI integrity

```bash
python -m compileall tools/agentx_evolve
python -m tools.agentx_evolve --help
python -m tools.agentx_evolve version || true
```

Required:

```text
- compile succeeds;
- help lists existing commands and new commands;
- existing commands are not removed.
```

### Gate 2 — mock chat vertical slice

```bash
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
python - <<'PY'
import json, pathlib, sys
root = pathlib.Path(".agentx-init/runs")
runs = sorted(root.glob("*"), key=lambda p: p.stat().st_mtime)
assert runs, "no run dirs"
run = runs[-1]
for name in ["final_verdict.json", "evidence_manifest.json", "request.json", "resolved_config.json"]:
    path = run / name
    assert path.exists(), f"missing {name}"
    json.loads(path.read_text())
print(run)
PY
```

Required:

```text
- exit 0;
- stdout is one JSON object;
- message contains READY;
- run dir exists;
- final_verdict.json says PASS;
- no source mutation.
```

### Gate 3 — artifact/schema validation

```bash
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
```

Required:

```text
- all required artifacts exist;
- JSON artifacts parse;
- evidence_manifest references existing files;
- final_verdict status matches CLI result.
```

### Gate 4 — provider adapter mocked test

```bash
pytest tools/agentx_evolve/tests/test_opencode_provider_adapter.py -q
```

Required:

```text
- maps opencode/big-pickle to payload model big-pickle;
- uses configured base URL;
- avoids /v1/v1 path;
- redacts API key in logs/artifacts;
- classifies provider errors.
```

### Gate 5 — self-upgrade dry-run

```bash
python -m tools.agentx_evolve self-upgrade --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md --mode plan --dry-run --mock --json
python -m tools.agentx_evolve self-upgrade --concept-file tools/agentx_evolve/examples/minimal_architecture_change.md --mode apply --dry-run --mock --json
```

Required:

```text
- plan is structured;
- patch is proposed;
- dry-run does not mutate source;
- evidence records dry-run status.
```

### Gate 6 — init-agent

```bash
rm -rf /tmp/Agent_Test
python -m tools.agentx_evolve init-agent --name Agent_Test --dest /tmp/Agent_Test --mock --json
```

Required:

```text
- destination exists;
- denylisted files are not copied;
- file manifest exists;
- validation result exists.
```

### Gate 7 — evolve-agent dry-run

```bash
python -m tools.agentx_evolve evolve-agent --agent-dir /tmp/Agent_Test --concept-file tools/agentx_evolve/examples/minimal_agent_upgrade.md --mode plan --dry-run --mock --json
```

Required:

```text
- target boundary enforced;
- controller source not mutated;
- proposed patch targets only /tmp/Agent_Test;
- evidence is written.
```

### Gate 8 — full test suite

```bash
pytest tools/agentx_evolve/tests -q
```

Required:

```text
- all tests pass;
- no live network required;
- no secrets required.
```

### Gate 9 — live provider opt-in

```bash
AGENTX_LIVE_PROVIDER_TESTS=1 \
AGENTX_OPENCODE_API_KEY=<secret> \
python -m tools.agentx_evolve chat --provider opencode --model opencode/big-pickle --once "Say READY" --json
```

Required:

```text
- only required for live acceptance;
- skipped or BLOCKED cleanly when credentials are absent;
- never run by default tests.
```

---

## 21. Negative Test Matrix

At minimum, tests must cover:

| Case | Expected result |
|---|---|
| missing concept file | BLOCKED, exit 2 |
| invalid CLI flag | exit 3 |
| malformed structured plan | FAIL, exit 1 |
| patch path escapes root | BLOCKED, exit 2 |
| absolute patch path | BLOCKED, exit 2 |
| symlink escape | BLOCKED, exit 2 |
| blocked command such as `rm -rf /` | BLOCKED, exit 2 |
| missing OpenCode API key in live provider mode | BLOCKED, exit 2 |
| provider timeout | FAIL, exit 4 |
| artifact write failure | FAIL, exit 6 |
| existing non-empty init-agent destination | BLOCKED, exit 2 |
| evolve-agent tries to patch controller source | BLOCKED, exit 2 |

---

## 22. Source-Mutation Verification

For commands that must not mutate source, the implementing LLM must verify using one of these methods:

```bash
git status --short
```

or, when git is unavailable:

```text
record file hashes before command;
record file hashes after command;
compare only source-controlled paths;
ignore `.agentx-init/runs/` artifacts.
```

Commands that must not mutate controller source:

```text
chat
self-upgrade --mode plan
self-upgrade --mode apply --dry-run
evolve-agent --mode plan --dry-run
```

---

## 23. Final Acceptance Bundle

Final implementation must produce or identify:

```text
.agentx-init/acceptance/final_acceptance_report.md
.agentx-init/acceptance/final_acceptance_report.json
.agentx-init/acceptance/command_transcripts/
.agentx-init/acceptance/artifact_manifest.json
.agentx-init/acceptance/test_results.json
.agentx-init/acceptance/safety_results.json
```

The final report must include:

```text
- repository commit hash;
- branch name;
- files changed;
- commands run;
- exit codes;
- test results;
- artifact locations;
- capability verdicts C1-C6;
- safety verdicts;
- live-provider status: PASS, FAIL, SKIPPED, or BLOCKED;
- final DONE / NOT DONE verdict.
```

---

## 24. Final Definition of Done

Agent_X runtime integration is DONE only when all are true:

```text
- `python -m compileall tools/agentx_evolve` passes;
- `python -m tools.agentx_evolve --help` works;
- existing commands remain available;
- `chat --once "Say READY" --mock --json` passes;
- self-upgrade plan and apply dry-run pass in mock mode;
- init-agent passes in mock/default mode;
- evolve-agent plan dry-run passes in mock mode;
- default pytest suite passes without network or secrets;
- required artifacts are written for each command;
- final verdict files match CLI results;
- safety negative tests pass;
- live provider is either proven with credentials or cleanly marked SKIPPED/BLOCKED;
- final acceptance bundle exists.
```

If any item is false, the final verdict is NOT DONE.

---

## 25. Final Executor Checklist

Use this exact implementation order:

```text
1. Inspect current package and CLI.
2. Preserve existing commands.
3. Add shared result/config/session/artifact primitives.
4. Add deterministic mock provider.
5. Add `chat --once ... --mock --json`.
6. Prove mock chat artifacts.
7. Add OpenCode adapter with mocked HTTP tests.
8. Add structured plan parser.
9. Add self-upgrade plan/dry-run.
10. Add init-agent.
11. Add evolve-agent plan/dry-run.
12. Add safety negative tests.
13. Add final acceptance bundle.
14. Run full acceptance ladder.
```

Do not skip ahead. Do not implement later workflows before the mock chat gate passes.

---

## 26. Implementation Acceptance Ledger

The implementing LLM should fill this ledger during the work:

| Gate | Command/test | Exit code | Verdict | Artifact/run dir | Notes |
|---|---|---:|---|---|---|
| 1 | `python -m compileall tools/agentx_evolve` |  |  |  |  |
| 1 | `python -m tools.agentx_evolve --help` |  |  |  |  |
| 2 | `chat --once "Say READY" --mock --json` |  |  |  |  |
| 4 | `pytest ...test_opencode_provider_adapter.py -q` |  |  |  |  |
| 5 | `self-upgrade --mode plan --dry-run --mock --json` |  |  |  |  |
| 5 | `self-upgrade --mode apply --dry-run --mock --json` |  |  |  |  |
| 6 | `init-agent --name Agent_Test --dest /tmp/Agent_Test --mock --json` |  |  |  |  |
| 7 | `evolve-agent --agent-dir /tmp/Agent_Test ... --dry-run --mock --json` |  |  |  |  |
| 8 | `pytest tools/agentx_evolve/tests -q` |  |  |  |  |

---

## 27. Final Response Format for Implementing LLM

When implementation is complete, the implementing LLM should report:

```text
Status: DONE or NOT DONE

Repository state:
- commit:
- branch:
- files changed:

Commands run:
- command -> exit code -> PASS/FAIL

Capabilities:
- C1 mock chat:
- C2 OpenCode/Big Pickle provider path:
- C3 self-upgrade plan/apply dry-run:
- C4 self-upgrade apply dry-run:
- C5 init-agent:
- C6 evolve-agent:

Safety:
- path boundary:
- command allowlist:
- secrets redaction:
- dry-run no-mutation:

Artifacts:
- final acceptance report:
- evidence manifest:
- representative run dirs:

Remaining blockers:
- none, or exact blocker list
```

---

## 28. Start Here

Run:

```bash
python -m compileall tools/agentx_evolve
python -m tools.agentx_evolve --help
python -m tools.agentx_evolve chat --once "Say READY" --mock --json
```

If the third command does not exist, implement the smallest safe set of changes required to make it pass while preserving all existing commands.

Then proceed gate by gate.

**Final REV18 rating:** **10/10** for functionality, design, completeness, and ease of execution by another LLM.
