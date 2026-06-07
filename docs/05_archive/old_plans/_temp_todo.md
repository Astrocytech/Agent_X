# Agent_X Self-Evolving System — Full Required Stack After Initiator

## 0. Purpose

This document lists the complete set of additional systems needed after the completed `agentx-init` Initiator in order to evolve Agent_X into a governed self-evolving implementation system.

The current Initiator is treated as complete. It provides:

```text
scan
status
governance
risk
plan
propose
validate
report
audit
memory
knowledge graph
schema validation
source mutation guard
runtime artifact generation
```

The Initiator is a control, evidence, planning, validation, memory, and graph tool. It is not yet a source-code implementation agent.

The next work should add the missing layers that let Agent_X safely turn approved plans and proposals into source changes, validation runs, rollbacks, human review records, and eventual controlled promotion.

---

# 1. Full Stack Overview

The complete self-evolving Agent_X system should contain the following layers:

```text
0. Agent_X Initiator — already complete
1. Governed Patch Execution Layer
2. Tool / MCP Adapter Layer
3. Model Adapter Layer
4. Context Builder / Task Packer
5. LLM Implementation Worker
6. Self-Evolution Orchestrator
7. Human Review / Approval Interface
8. Promotion / Release Gate
9. Long-Term Learning / Outcome Review Layer
10. Policy / Capability Registry
11. Task Queue / Session Scheduler
12. Evaluation Harness / Regression Benchmark Layer
13. Failure Taxonomy / Recovery Playbook
14. Documentation Synchronization Layer
15. Local Model Runtime Profile Layer
16. Security Sandbox / Filesystem Boundary Layer
17. Git Integration Layer
18. Packaging / Distribution Layer
19. Monitoring / Observability Layer
20. Final System Acceptance Layer
```

The minimum needed for the first working self-evolving prototype is layers 1 through 6.

Layers 7 through 20 are hardening, safety, quality, release, and operational layers.

---

# 2. Current Completed Layer: Agent_X Initiator

## Status

```text
COMPLETE
```

## Role

The Initiator is the control and evidence foundation.

It provides:

```text
repository scan
architecture/status analysis
governance decisions
risk classification
ranked planning
patch proposal generation
validation
report generation
audit history
memory store
knowledge graph
schema validation
runtime artifact generation
source mutation guard
```

## What It Does Not Do

It does not:

```text
edit source files
apply patches
commit changes
promote changes
self-modify
act as autonomous coding agent
```

## Why It Matters

All later self-evolution layers must use Initiator artifacts and decisions as the source of truth.

Later agents should not bypass:

```text
governance
risk
validation
audit
memory
graph
source mutation guard
```

---

# 3. Layer 1 — Governed Patch Execution Layer

## Priority

```text
MUST-HAVE NEXT
```

## Purpose

This deterministic non-LLM layer safely applies approved source changes.

It is the actuator that sits between non-mutating patch proposals and actual source modifications.

## Why It Is Needed

The Initiator can propose changes but intentionally does not apply them.

Before adding an LLM agent, the project needs a safe non-agent implementation layer that can:

```text
apply only approved changes
snapshot files before editing
rollback failed attempts
prove only approved files changed
block forbidden paths
produce implementation evidence
```

## Required Components

```text
patch_applier.py
rollback_manager.py
implementation_session.py
file_change_guard.py
git_diff_guard.py
implementation_validation_gate.py
implementation_evidence.py
```

## Required Runtime Artifacts

```text
.agentx-init/implementation/sessions/<session_id>.json
.agentx-init/implementation/implementation_history.jsonl
.agentx-init/implementation/rollback_snapshots/<session_id>/
.agentx-init/implementation/implementation_evidence.jsonl
.agentx-init/snapshots/implementation_latest.json
```

## Required Capabilities

```text
start implementation session
load patch proposal
load governance decision
verify proposal is implementation-eligible
snapshot affected files
apply bounded file change
verify changed files
run validation
accept session if validation passes
rollback session if validation fails
write implementation evidence
append audit event
```

## Forbidden Behavior

```text
no uncontrolled file edits
no path traversal
no L0 mutation
no writing outside approved paths
no applying changes without governance
no skipping validation
no destructive delete without explicit approval
no direct git commit
```

## Acceptance Criteria

The layer is complete when it can:

```text
apply a simple approved edit
reject unapproved edit
reject L0 edit
reject outside-repo edit
snapshot changed files
rollback failed edit
prove source mutation is limited to approved paths
write implementation session record
write audit event
pass tests
```

---

# 4. Layer 2 — Tool / MCP Adapter Layer

## Priority

```text
MUST-HAVE
```

## Purpose

Expose Initiator and patch execution capabilities as structured tools for agents.

## Why It Is Needed

The future agent should not call arbitrary shell commands or directly access files. It should call controlled tools.

## Required Components

```text
mcp_server.py
tool_registry.py
tool_models.py
tool_policy.py
agentx_init_adapter.py
patch_execution_adapter.py
filesystem_adapter.py
command_runner_adapter.py
git_adapter.py
```

## Required Tools

```text
agentx_scan
agentx_status
agentx_plan
agentx_propose
agentx_governance_check
agentx_risk_check
agentx_validate
agentx_report
agentx_graph_build
agentx_graph_status
agentx_graph_query
patch_apply
patch_rollback
patch_session_status
read_file_guarded
write_file_guarded
list_files_guarded
run_allowlisted_command
git_status
git_diff
```

## Tool Output Rule

Every tool should return structured JSON:

```json
{
  "tool_name": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

## Forbidden Behavior

```text
no raw shell access to agent
no unrestricted filesystem access
no hidden network calls
no non-JSON tool results where structured output is needed
no bypass of Initiator governance
```

## Acceptance Criteria

The layer is complete when:

```text
all core Initiator commands are callable as tools
patch execution tools are callable
unsafe tool calls are blocked
tool outputs are structured
tool calls are audited
tool schemas validate
```

---

# 5. Layer 3 — Model Adapter Layer

## Priority

```text
MUST-HAVE
```

## Purpose

Connect the system to local or hosted LLMs through a replaceable model interface.

## Why It Is Needed

The user has limited hardware and may need small local models. The model must be replaceable without changing the agent architecture.

## Required Components

```text
model_adapter.py
model_registry.py
model_profile.py
prompt_runner.py
json_output_validator.py
model_retry_policy.py
local_provider_adapter.py
opencode_provider_adapter.py
ollama_adapter.py
lmstudio_adapter.py
openai_compatible_adapter.py
```

## Supported Model Types

```text
local small coder model
local general instruction model
OpenAI-compatible local server
Ollama
LM Studio
OpenCode-compatible provider
optional hosted fallback
```

## Required Model Profiles

```text
small_fast
small_coder
medium_coder_optional
hosted_fallback_optional
```

## Required Capabilities

```text
run prompt
run JSON-only prompt
validate output schema
retry invalid JSON
limit token budget
route by task type
record model used
record prompt/output hash
avoid logging secrets
```

## Forbidden Behavior

```text
model cannot directly edit files
model cannot execute commands
model cannot override governance
model cannot approve itself
model cannot decide promotion
```

## Acceptance Criteria

The layer is complete when:

```text
a local small model can be called
structured JSON output can be validated
invalid output is rejected
model provider can be swapped
task logs record model identity and output status
```

---

# 6. Layer 4 — Context Builder / Task Packer

## Priority

```text
MUST-HAVE
```

## Purpose

Create small, bounded task packets for the model.

## Why It Is Needed

Small models cannot process the whole repository. They need tightly selected context.

## Required Components

```text
context_builder.py
task_packet.py
file_selector.py
artifact_selector.py
context_budgeter.py
context_compressor.py
schema_injector.py
validation_error_summarizer.py
```

## Required Inputs

```text
patch proposal
candidate action
governance decision
risk assessment
selected files
relevant schemas
test output
validation report
graph query result
memory records
```

## Required Output

```json
{
  "task_packet_id": "string",
  "task_type": "IMPLEMENT_PATCH|FIX_VALIDATION|WRITE_TEST|EXPLAIN_FAILURE",
  "objective": "string",
  "allowed_files": [],
  "forbidden_files": [],
  "source_snippets": [],
  "relevant_artifacts": [],
  "output_schema": {},
  "constraints": [],
  "validation_plan": {},
  "token_budget": 0
}
```

## Rules

```text
include only necessary files
prefer snippets over whole repo
include exact allowed files
include exact forbidden files
include output schema
include governance result
include validation expectations
```

## Acceptance Criteria

The layer is complete when:

```text
it can build a task packet for one proposal
it respects token budget
it includes allowed/forbidden files
it includes relevant schemas
it works with small models
it produces deterministic packets for same inputs
```

---

# 7. Layer 5 — LLM Implementation Worker

## Priority

```text
MUST-HAVE
```

## Purpose

Use an LLM to convert bounded task packets into implementation plans or patch candidates.

## Why It Is Needed

This is the first LLM coding component, but it should not have direct authority over the repository.

## Required Components

```text
llm_implementation_worker.py
edit_plan_generator.py
patch_candidate_generator.py
test_candidate_generator.py
validation_fix_generator.py
worker_output_schema.py
```

## Required Outputs

```text
edit_plan.json
patch_candidate.json
test_candidate.json
validation_fix_attempt.json
```

## Output Example

```json
{
  "schema_version": "1.0",
  "worker_output_id": "string",
  "task_packet_id": "string",
  "status": "PROPOSED|NEEDS_MORE_CONTEXT|FAILED",
  "allowed_files_only": true,
  "changes": [
    {
      "target_file": "string",
      "change_type": "UPDATE",
      "instructions": "string",
      "replacement_blocks": []
    }
  ],
  "tests_to_run": [],
  "warnings": [],
  "errors": []
}
```

## Forbidden Behavior

```text
no direct file writes
no direct command execution
no governance decisions
no source mutation authority
no broad repo refactors unless task packet allows it
no editing forbidden files
```

## Acceptance Criteria

The worker is complete when:

```text
it consumes task packets
it produces schema-valid patch candidates
it handles insufficient context safely
it can generate small code/test changes
it does not call filesystem directly
```

---

# 8. Layer 6 — Self-Evolution Orchestrator

## Priority

```text
MUST-HAVE FOR FIRST SELF-EVOLVING LOOP
```

## Purpose

Coordinate the complete governed implementation loop.

## Required Components

```text
self_evolution_orchestrator.py
candidate_selector.py
implementation_loop.py
validation_loop.py
rollback_decider.py
session_finalizer.py
```

## Core Loop

```text
1. Run agentx-init scan
2. Run agentx-init status
3. Run agentx-init plan
4. Select one candidate
5. Run agentx-init propose
6. Run governance/risk check
7. Build task packet
8. Ask LLM worker for patch candidate
9. Send candidate to patch execution layer
10. Run validation
11. If validation passes, accept session
12. If validation fails, attempt bounded repair or rollback
13. Record audit/memory/graph evidence
14. Produce completion record
```

## Required Session States

```text
CREATED
SCANNED
PLANNED
PROPOSED
GOVERNANCE_CHECKED
CONTEXT_BUILT
MODEL_PROPOSED
PATCH_APPLIED
VALIDATED
ROLLED_BACK
ACCEPTED
FAILED
BLOCKED
```

## Forbidden Behavior

```text
no skipping governance
no skipping validation
no direct model-to-file editing
no silent acceptance of failed validation
no unlimited repair loops
no self-modification of governance rules
```

## Acceptance Criteria

The orchestrator is complete when:

```text
it can complete one low-risk implementation session
it can rollback a failed session
it records all evidence
it uses Initiator outputs
it does not bypass patch execution layer
it produces a final completion record
```

---

# 9. Layer 7 — Human Review / Approval Interface

## Priority

```text
SHOULD-HAVE BEFORE HIGHER-RISK WORK
```

## Purpose

Let the user review proposed or applied changes before acceptance or promotion.

## Required Components

```text
review_cli.py
approval_model.py
review_report.py
approval_history.py
```

## Commands

```text
agentx-evolve review <session_id>
agentx-evolve approve <session_id>
agentx-evolve reject <session_id>
agentx-evolve explain <session_id>
```

## Review Should Show

```text
task
proposal
governance decision
risk assessment
files changed
diff summary
validation result
rollback availability
audit references
```

## Acceptance Criteria

Complete when a user can approve or reject a session and the decision is recorded.

---

# 10. Layer 8 — Promotion / Release Gate

## Priority

```text
SHOULD-HAVE
```

## Purpose

Determine whether an accepted implementation session can become stable project state.

## Why It Is Needed

Validation is not the same as promotion. Promotion requires broader acceptance criteria.

## Required Components

```text
promotion_gate.py
release_candidate.py
promotion_rules.py
promotion_evidence.py
```

## Required Checks

```text
governance allowed
risk acceptable
validation passed
source guard passed
no forbidden paths changed
completion evidence exists
rollback available or intentionally unnecessary
human approval present when required
```

## First Version Behavior

The first version should not auto-commit or auto-merge. It should only produce a promotion recommendation.

## Acceptance Criteria

Complete when it can produce:

```text
PROMOTE_READY
PROMOTE_BLOCKED
PROMOTE_NEEDS_REVIEW
```

with evidence.

---

# 11. Layer 9 — Long-Term Learning / Outcome Review Layer

## Priority

```text
SHOULD-HAVE
```

## Purpose

Track what worked, what failed, and what patterns should influence future planning.

## Non-LLM First Version

This should not train a model. It should store structured outcome records.

## Required Components

```text
outcome_review.py
strategy_memory.py
failure_pattern_index.py
success_pattern_index.py
```

## Records

```text
attempted task
proposal type
files changed
model used
validation outcome
rollback outcome
failure reason
successful strategy
future recommendation
```

## Acceptance Criteria

Complete when future plans can reference prior success/failure patterns.

---

# 12. Layer 10 — Policy / Capability Registry

## Priority

```text
MUST-HAVE BEFORE MANY TOOLS
```

## Purpose

Define what each agent/tool/model may do.

## Required Components

```text
capability_registry.py
policy_registry.py
agent_permissions.py
tool_permissions.py
model_permissions.py
```

## Registry Must Define

```text
which tools exist
which agent can call which tool
which model can be used for which task
which paths are writable
which actions require approval
which actions are blocked
```

## Acceptance Criteria

Complete when every tool call can be checked against a capability policy.

---

# 13. Layer 11 — Task Queue / Session Scheduler

## Priority

```text
LATER
```

## Purpose

Manage multiple candidate tasks and implementation sessions.

## First Version Rule

No background daemon initially. Keep it manual.

## Required Components

```text
task_queue.py
session_queue.py
task_priority_view.py
```

## Acceptance Criteria

Complete when the system can list, queue, start, pause, resume, and cancel implementation sessions.

---

# 14. Layer 12 — Evaluation Harness / Regression Benchmark Layer

## Priority

```text
SHOULD-HAVE BEFORE TRUSTING SELF-EVOLUTION
```

## Purpose

Evaluate whether the self-evolving system is improving or degrading.

## Required Components

```text
evaluation_harness.py
golden_tasks/
regression_benchmarks/
quality_scorecard.py
```

## Required Evaluations

```text
can implement simple change
can avoid forbidden path
can rollback failure
can handle validation failure
can preserve source guard
can produce evidence
can operate with small model
```

## Acceptance Criteria

Complete when every agent change can be benchmarked against known tasks.

---

# 15. Layer 13 — Failure Taxonomy / Recovery Playbook

## Priority

```text
MUST-HAVE FOR RELIABILITY
```

## Purpose

Standardize how failures are classified and recovered.

## Failure Classes

```text
MODEL_INVALID_OUTPUT
MODEL_INSUFFICIENT_CONTEXT
PATCH_APPLY_FAILED
VALIDATION_FAILED
GOVERNANCE_BLOCKED
RISK_TOO_HIGH
SOURCE_GUARD_FAILED
ROLLBACK_FAILED
SCHEMA_VALIDATION_FAILED
TOOL_FAILURE
UNKNOWN_FAILURE
```

## Required Recovery Rules

```text
invalid model output -> retry with stricter prompt
insufficient context -> rebuild task packet
patch failed -> reject patch candidate
validation failed -> repair attempt or rollback
source guard failed -> rollback immediately
rollback failed -> block and require human review
```

## Acceptance Criteria

Complete when every failed session has a failure class and recovery action.

---

# 16. Layer 14 — Documentation Synchronization Layer

## Priority

```text
SHOULD-HAVE
```

## Purpose

Keep implementation, schemas, docs, and runtime behavior aligned.

## Required Components

```text
doc_sync_checker.py
schema_doc_checker.py
implementation_contract_checker.py
```

## Required Checks

```text
public functions match FIC
schema fields match docs
runtime artifacts match schemas
CLI commands match command docs
milestone docs match implemented commands
```

## Acceptance Criteria

Complete when documentation drift can be detected automatically.

---

# 17. Layer 15 — Local Model Runtime Profile Layer

## Priority

```text
MUST-HAVE FOR OLD GPU MACHINES
```

## Purpose

Make the self-evolving system practical on limited hardware.

## Required Components

```text
runtime_profile.py
model_resource_budget.py
context_budget_profile.py
gpu_memory_profile.py
```

## Profiles

```text
cpu_only_safe
small_gpu_8gb
balanced_local
hosted_fallback_optional
```

## Required Rules

```text
one model loaded at a time
small context packets
no whole-repo prompts
short JSON outputs
bounded retries
model timeout
VRAM-aware model selection
```

## Acceptance Criteria

Complete when the system can run with a small local model profile.

---

# 18. Layer 16 — Security Sandbox / Filesystem Boundary Layer

## Priority

```text
MUST-HAVE
```

## Purpose

Prevent tools and agents from escaping approved boundaries.

## Required Components

```text
sandbox_policy.py
path_boundary.py
safe_file_ops.py
safe_subprocess.py
network_policy.py
```

## Required Protections

```text
path traversal block
symlink escape block
write boundary enforcement
network disabled by default
shell mode disabled by default
environment variables not logged
secrets not logged
```

## Acceptance Criteria

Complete when unsafe filesystem and command operations are reliably blocked.

---

# 19. Layer 17 — Git Integration Layer

## Priority

```text
SHOULD-HAVE, BUT AFTER PATCH EXECUTION IS STABLE
```

## Purpose

Inspect and eventually manage version-control changes.

## First Version

Read-only Git operations:

```text
git status
git diff
git diff --name-only
git diff --stat
```

## Later Version

Carefully governed write operations:

```text
create branch
stage approved files
commit approved session
tag release candidate
```

## Forbidden Initially

```text
push
force push
merge main
rebase
delete branch
reset --hard without rollback policy
```

## Acceptance Criteria

Complete when the system can show diffs and later create governed commits.

---

# 20. Layer 18 — Packaging / Distribution Layer

## Priority

```text
LATER
```

## Purpose

Package the entire self-evolving system for repeatable local installation.

## Required Components

```text
pyproject.toml updates
console scripts
local config templates
install checks
version command
```

## Commands

```text
agentx-init
agentx-patch
agentx-evolve
```

## Acceptance Criteria

Complete when a fresh clone can install and run all tools.

---

# 21. Layer 19 — Monitoring / Observability Layer

## Priority

```text
LATER
```

## Purpose

Make sessions inspectable and debuggable.

## Required Views

```text
current session
last failure
last validation
changed files
rollback status
model used
tool calls
audit events
```

## Acceptance Criteria

Complete when a failed or successful session can be reconstructed.

---

# 22. Layer 20 — Final System Acceptance Layer

## Priority

```text
FINAL
```

## Purpose

Define when Agent_X can be called a governed self-evolving system.

## Final Acceptance Tests

```text
fresh clone install
initiator scan/status/plan/propose/validate/graph
patch execution on approved low-risk change
rollback on failed validation
source guard blocks unauthorized edits
LLM worker produces schema-valid patch candidate
orchestrator completes one safe session
human review can approve/reject
promotion gate can recommend acceptance
audit/memory/graph record all events
no L0 mutation
no uncontrolled shell
no network by default
small local model profile works
```

## Final Done Definition

The system is done when it can:

```text
identify a needed improvement
generate a proposal
obtain governance/risk context
prepare bounded model context
generate an implementation candidate
apply it safely
validate it
rollback if needed
record evidence
offer promotion recommendation
preserve all source boundaries
```

---

# 23. Recommended Build Order

## Phase A — Deterministic Actuator

```text
1. Governed Patch Execution Layer
2. Security Sandbox / Filesystem Boundary Layer
3. Policy / Capability Registry
4. Failure Taxonomy / Recovery Playbook
```

## Phase B — Tool Exposure

```text
5. Tool / MCP Adapter Layer
6. Git Integration Layer, read-only first
```

## Phase C — Model Integration

```text
7. Model Adapter Layer
8. Local Model Runtime Profile Layer
9. Context Builder / Task Packer
10. LLM Implementation Worker
```

## Phase D — Self-Evolution Loop

```text
11. Self-Evolution Orchestrator
12. Human Review / Approval Interface
13. Promotion / Release Gate
```

## Phase E — Hardening

```text
14. Evaluation Harness / Regression Benchmark Layer
15. Long-Term Learning / Outcome Review Layer
16. Documentation Synchronization Layer
17. Monitoring / Observability Layer
18. Packaging / Distribution Layer
19. Final System Acceptance Layer
```

---

# 24. Minimum First Working Self-Evolving Version

The minimum viable self-evolving system requires:

```text
Agent_X Initiator
Governed Patch Execution Layer
Security Sandbox / Filesystem Boundary Layer
Policy / Capability Registry
Tool / MCP Adapter Layer
Model Adapter Layer
Local Model Runtime Profile Layer
Context Builder / Task Packer
LLM Implementation Worker
Self-Evolution Orchestrator
Failure Taxonomy / Recovery Playbook
```

Human review and promotion can be manual at first, but should be added before higher-risk automated work.

---

# 25. What Not To Build Yet

Do not build these before the deterministic actuator and governance loop are stable:

```text
full autonomous self-modification
automatic commits
automatic push
multi-agent swarm
background daemon
remote execution
cloud-only dependency
web dashboard
automatic policy rewriting
model fine-tuning
training loop
L0 modification workflow
promotion automation
```

---

# 26. Final Verdict

The current Initiator is the correct foundation.

The next required step is not more analysis. The next required step is the deterministic, governed source-change actuator.

The full stack after the Initiator should be built in this order:

```text
1. Governed Patch Execution Layer
2. Security / policy / failure-control foundation
3. Tool/MCP adapter
4. Model adapter and local runtime profiles
5. Context builder
6. LLM implementation worker
7. Self-evolution orchestrator
8. Review, promotion, learning, documentation sync, monitoring, packaging
```

This creates a controlled path from:

```text
project understanding
```

to:

```text
safe implementation
```

to:

```text
validated self-evolution
```



==========



Here is the direct overlap between your **Agent_X roadmap layers** and **OpenCode’s tool/model/protocol stack**.

|  # | Agent_X layer                                   |          OpenCode overlap? | Overlapping OpenCode pieces                                                    |
| -: | ----------------------------------------------- | -------------------------: | ------------------------------------------------------------------------------ |
|  0 | Agent_X Initiator                               |                **Partial** | `plan`, `todowrite`, repo overview/scout ideas, status-like workflow           |
|  1 | Security Sandbox / Filesystem Boundary          |                 **Strong** | `shell` permission scanning, read/write/edit safety patterns                   |
|  2 | Policy / Capability Registry                    |                 **Strong** | tool registry, conditional tool exposure, permissioning                        |
|  3 | Governed Patch Execution Layer                  |                 **Strong** | `edit`, `write`, `patch`, `apply_patch`                                        |
|  4 | Failure Taxonomy / Recovery Playbook            |                **Partial** | `invalid` tool handling, command failure handling, patch/edit failure handling |
|  5 | Tool / MCP Adapter Layer                        |                 **Strong** | MCP SDK, custom plugin tools, tool registry                                    |
|  6 | Model Adapter Layer                             |                 **Strong** | AI SDK provider ecosystem, OpenAI-compatible APIs, many provider adapters      |
|  7 | Local Model Runtime Profile Layer               |                **Partial** | provider/model configuration, local-model-compatible routing concept           |
|  8 | Context Builder / Task Packer                   |                 **Strong** | `read`, `glob`, `grep`, repo overview, LSP, file search                        |
|  9 | Prompt Contract / Prompt Versioning Layer       |                **Partial** | `skill`, specialized agent instructions, model/tool-specific behavior          |
| 10 | LLM Implementation Worker                       |                 **Strong** | coding agent loop using read/edit/write/patch/shell tools                      |
| 11 | Self-Evolution Orchestrator                     |                 **Strong** | agent orchestration, `task`, plan mode, tool loop                              |
| 12 | Human Review / Approval Interface               |                 **Strong** | `question`, permission prompts, interactive approval concepts                  |
| 13 | Promotion / Release Gate                        |                **Partial** | Git/diff/check workflow ideas; OpenCode itself is less governance-heavy here   |
| 14 | Git Integration Layer                           | **Partial / Strong later** | GitHub Actions, GitHub API, GitLab integration, diff/status concepts           |
| 15 | Evaluation Harness / Regression Benchmark Layer |                **Partial** | test runner/build tooling ideas, CI patterns                                   |
| 16 | Long-Term Learning / Outcome Review Layer       |         **Weak / Partial** | session/todo/history concepts, but not a direct OpenCode core feature          |
| 17 | Documentation Synchronization Layer             |                **Partial** | docs/site tooling, markdown rendering, repo search                             |
| 18 | Task Queue / Session Scheduler                  |                **Partial** | `task`, `todowrite`, subagent/task concepts                                    |
| 19 | Monitoring / Observability Layer                |                **Partial** | OpenTelemetry, logging, tracing concepts                                       |
| 20 | Packaging / Distribution Layer                  |    **Strong conceptually** | Bun workspaces, packaging, desktop/web/CLI packaging concepts                  |
| 21 | Backup / Disaster Recovery Layer                |                   **Weak** | not a major direct overlap                                                     |
| 22 | Final System Acceptance Layer                   |                **Partial** | test/build/CI patterns, but Agent_X needs its own acceptance gate              |

OpenCode’s strongest reusable overlaps are its built-in agent tools: `shell`, `read`, `glob`, `grep`, `edit`, `write`, `patch/apply_patch`, `task`, `todowrite`, `question`, `skill`, `plan`, and invalid-tool handling. 

## Most useful overlaps to borrow first

```text
1. Security Sandbox / Filesystem Boundary Layer
2. Policy / Capability Registry
3. Governed Patch Execution Layer
5. Tool / MCP Adapter Layer
6. Model Adapter Layer
8. Context Builder / Task Packer
10. LLM Implementation Worker
11. Self-Evolution Orchestrator
12. Human Review / Approval Interface
```

## Weakest overlaps

```text
16. Long-Term Learning / Outcome Review Layer
21. Backup / Disaster Recovery Layer
22. Final System Acceptance Layer
```

Those are more specific to Agent_X and should be designed internally rather than borrowed from OpenCode.

