# Agent_X Self-Evolving System — Full Required Stack After Initiator v7

## 0. Document Status

```text
document_id: AGENT_X_SELF_EVOLVING_SYSTEM_FULL_REQUIRED_STACK
version: v7.0
status: FINAL FROZEN FULL-STACK ROADMAP
scope: post-agentx-init governed self-evolving Agent_X system
previous_version_reviewed: v6
rating: 10/10
```

## 0.1 Final Verification Result

The v6 document covered the required stack, but it accumulated several addendum-style sections across revisions. The remaining issue was not missing architecture. The remaining issue was document hygiene: the roadmap needed one final consolidated version with:

```text
single clean structure
no reliance on later addenda
clear build order
clear layer list
clear control requirements
clear acceptance evidence
clear freeze rule
```

This v7 document is the cleaned and final controlling version.

---

# 1. Purpose

This document defines every major system layer needed after the completed `agentx-init` Initiator to create a governed self-evolving Agent_X system.

The current Initiator is complete and provides:

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

The missing post-Initiator system must add controlled source-change capability, model integration, task context building, patch execution, rollback, review, promotion, and long-term improvement tracking.

---

# 2. Formal Definition of Self-Evolution

In Agent_X, self-evolution means:

```text
The system may improve its own non-protected implementation files through governed proposals, approved bounded patch execution, validation, rollback, evidence recording, and review/promotion gates where required.
```

It does not mean:

```text
free autonomous source rewriting
uncontrolled self-modification
L0 modification
governance-rule bypass
automatic promotion without gates
unrestricted command execution
unrestricted Git operations
model-only safety decisions
```

A valid self-evolution attempt must follow this chain:

```text
Initiator evidence
→ proposal
→ governance/risk review
→ bounded task packet
→ model-generated implementation candidate
→ deterministic patch execution
→ validation
→ source guard
→ audit/memory/graph update
→ review/promotion gate
```

---

# 3. Completed Foundation: Agent_X Initiator

## 3.1 Status

```text
COMPLETE
```

## 3.2 Role

The Initiator remains the control, evidence, planning, validation, memory, and graph foundation.

Later systems must consume Initiator artifacts rather than recreating their own independent truth.

## 3.3 Later Layers Must Not Bypass

```text
governance
risk
validation
audit
memory
graph
source mutation guard
schema validation
```

---

# 4. Complete Required Layer List

The complete post-Initiator stack contains:

```text
0. Agent_X Initiator — complete
1. Security Sandbox / Filesystem Boundary Layer
2. Policy / Capability Registry
3. Governed Patch Execution Layer
4. Failure Taxonomy / Recovery Playbook
5. Tool / MCP Adapter Layer
6. Model Adapter Layer
7. Local Model Runtime Profile Layer
8. Context Builder / Task Packer
9. Prompt Contract / Prompt Versioning Layer
10. LLM Implementation Worker
11. Self-Evolution Orchestrator
12. Human Review / Approval Interface
13. Promotion / Release Gate
14. Git Integration Layer
15. Evaluation Harness / Regression Benchmark Layer
16. Long-Term Learning / Outcome Review Layer
17. Documentation Synchronization Layer
18. Task Queue / Session Scheduler
19. Monitoring / Observability Layer
20. Packaging / Distribution Layer
21. Backup / Disaster Recovery Layer
22. Final System Acceptance Layer
```

The minimum first working self-evolving prototype requires layers 1 through 11.

---

# 5. Recommended Build Order

## Phase A — Deterministic Safety and Patch Foundation

```text
1. Security Sandbox / Filesystem Boundary Layer
2. Policy / Capability Registry
3. Failure Taxonomy / Recovery Playbook
4. Governed Patch Execution Layer
```

Goal:

```text
safe deterministic source mutation without LLM
```

## Phase B — Tool Exposure

```text
5. Tool / MCP Adapter Layer
6. Git Integration Layer, read-only first
```

Goal:

```text
controlled tool interface for later agents
```

## Phase C — Model Integration

```text
7. Model Adapter Layer
8. Local Model Runtime Profile Layer
9. Prompt Contract / Prompt Versioning Layer
10. Context Builder / Task Packer
11. LLM Implementation Worker
```

Goal:

```text
bounded model-generated patch candidates
```

## Phase D — Self-Evolution Loop

```text
12. Self-Evolution Orchestrator
13. Human Review / Approval Interface
14. Promotion / Release Gate
```

Goal:

```text
one governed low-risk self-evolution session
```

## Phase E — Hardening and Operations

```text
15. Evaluation Harness / Regression Benchmark Layer
16. Long-Term Learning / Outcome Review Layer
17. Documentation Synchronization Layer
18. Task Queue / Session Scheduler
19. Monitoring / Observability Layer
20. Packaging / Distribution Layer
21. Backup / Disaster Recovery Layer
22. Final System Acceptance Layer
```

Goal:

```text
operational reliability, repeatability, and acceptance evidence
```

---

# 6. Canonical Runtime State Layout

All new runtime state must live under `.agentx-init/`.

```text
.agentx-init/
  implementation/
    sessions/
    rollback_snapshots/
    implementation_history.jsonl
    implementation_evidence.jsonl
    latest_implementation_session.json

  tool_calls/
    tool_call_history.jsonl
    tool_result_history.jsonl
    latest_tool_call.json

  model_runs/
    model_run_history.jsonl
    model_request_history.jsonl
    model_response_history.jsonl
    latest_model_run.json

  task_packets/
    task_packet_history.jsonl
    latest_task_packet.json

  prompts/
    prompt_registry.json
    prompt_run_history.jsonl

  sessions/
    evolution_session_history.jsonl
    latest_evolution_session.json

  approvals/
    approval_history.jsonl
    latest_approval.json

  promotion/
    promotion_history.jsonl
    latest_promotion_decision.json

  rollback/
    rollback_history.jsonl
    latest_rollback.json

  evaluations/
    evaluation_history.jsonl
    latest_evaluation_report.json

  policies/
    capability_policy.json
    tool_policy.json
    model_policy.json
    dependency_allowlist.json
    model_allowlist.json
    mcp_server_allowlist.json
    dependency_provenance.json

  observability/
    session_trace_history.jsonl
    tool_trace_history.jsonl
    error_history.jsonl

  backups/
    manifests/
    archives/
```

Rules:

```text
No new top-level runtime state directory without contract update.
All runtime state must be schema-governed.
All latest JSON artifacts must be written atomically.
All history JSONL files must be append-only.
```

---

# 7. Universal Schema Contract

Every new subsystem must define schemas before implementation.

## 7.1 Required Schemas

```text
implementation_session.schema.json
patch_application.schema.json
rollback_snapshot.schema.json
rollback_record.schema.json
source_change_guard.schema.json
tool_call.schema.json
tool_result.schema.json
model_request.schema.json
model_response.schema.json
model_run.schema.json
task_packet.schema.json
prompt_contract.schema.json
prompt_run.schema.json
worker_output.schema.json
patch_candidate.schema.json
evolution_session.schema.json
human_approval.schema.json
promotion_decision.schema.json
failure_record.schema.json
capability_policy.schema.json
tool_policy.schema.json
model_policy.schema.json
dependency_provenance.schema.json
evaluation_report.schema.json
session_trace.schema.json
backup_manifest.schema.json
completion_record.schema.json
```

## 7.2 Universal Required Fields

Every structured runtime artifact must include:

```json
{
  "schema_version": "string",
  "schema_id": "string",
  "artifact_id": "string",
  "timestamp": "string",
  "source_component": "string",
  "status": "string",
  "warnings": [],
  "errors": []
}
```

## 7.3 Schema Rules

```text
validate before writing latest JSON
validate before appending history where practical
invalid artifacts must not replace prior valid latest artifacts
schema validation failure must produce failure evidence
schema failures must not be silently downgraded to warnings
```

---

# 8. Atomic Write and Recovery Contract

For every `latest_*.json` artifact:

```text
1. Build object in memory.
2. Validate against schema.
3. Write to temp file in same directory.
4. Flush/fsync where practical.
5. Rename atomically.
6. Never overwrite a valid latest artifact with invalid output.
```

For JSONL:

```text
one JSON object per line
append only
never rewrite previous lines
never reorder previous lines
never delete malformed lines
record malformed line as warning/evidence
```

On interruption:

```text
preserve prior valid latest artifact
record recovery event
do not mark session accepted
do not silently continue as success
```

---

# 9. Locking and Concurrency Rules

Default:

```text
one active implementation session at a time
```

Required locks:

```text
implementation_session.lock
patch_apply.lock
rollback.lock
promotion.lock
```

Rules:

```text
one patch session may modify files at a time
affected files must be locked before write
stale locks must be detectable and recoverable
status/report/graph must not consume half-written artifacts
two agents may not edit the same file concurrently
```

No background daemon or parallel autonomous sessions in the first version.

---

# 10. Layer 1 — Security Sandbox / Filesystem Boundary

Purpose:

```text
prevent tools, agents, and models from escaping approved boundaries
```

Required components:

```text
sandbox_policy.py
path_boundary.py
safe_file_ops.py
safe_subprocess.py
network_policy.py
secret_redactor.py
```

Required protections:

```text
path traversal block
symlink escape block
write boundary enforcement
network disabled by default
shell mode disabled by default
environment variables not logged
secrets not logged
unapproved paths blocked
L0 writes blocked
```

Acceptance:

```text
unsafe filesystem operations rejected
unsafe subprocess operations rejected
secrets redacted
path traversal tests pass
symlink escape tests pass
L0 writes blocked
```

---

# 11. Layer 2 — Policy / Capability Registry

Purpose:

```text
define what each agent, tool, and model may do
```

Required components:

```text
capability_registry.py
policy_registry.py
agent_permissions.py
tool_permissions.py
model_permissions.py
approval_policy.py
```

Must define:

```text
available tools
which roles may call which tools
which models may be used for which tasks
which paths are writable
which actions require approval
which actions are blocked
which commands are allowlisted
which runtime locations are writable
```

Acceptance:

```text
every tool call is checked against policy before execution
```

---

# 12. Layer 3 — Governed Patch Execution Layer

Purpose:

```text
apply approved bounded source changes safely
```

Required components:

```text
patch_applier.py
rollback_manager.py
implementation_session.py
file_change_guard.py
git_diff_guard.py
implementation_validation_gate.py
implementation_evidence.py
```

Required capabilities:

```text
start session
load proposal
load governance decision
verify proposal eligibility
snapshot affected files
apply bounded file change
verify changed files
run validation
accept if validation passes
rollback if validation fails
write evidence
append audit event
```

Forbidden:

```text
uncontrolled file edits
path traversal
L0 mutation
writing outside approved paths
applying changes without governance
skipping validation
destructive delete without approval
direct git commit
```

Acceptance:

```text
approved edit applied
unapproved edit rejected
L0 edit rejected
outside-repo edit rejected
snapshot created
rollback succeeds
source mutation limited to approved paths
session/evidence/audit records written
```

---

# 13. Layer 4 — Failure Taxonomy / Recovery Playbook

Required failure classes:

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
LOCK_CONFLICT
ATOMIC_WRITE_FAILED
PROMPT_CONTRACT_FAILED
POLICY_DENIED
UNKNOWN_FAILURE
```

Required recovery behavior:

```text
invalid model output -> retry stricter prompt
insufficient context -> rebuild task packet
patch failed -> reject candidate
validation failed -> repair attempt or rollback
source guard failed -> rollback immediately
rollback failed -> safe mode + human review
schema failure -> do not write latest artifact
lock conflict -> block or wait safely
policy denied -> block and record evidence
```

Acceptance:

```text
every failed session has class, evidence, recovery action, final status, audit event
```

---

# 14. Layer 5 — Tool / MCP Adapter Layer

Purpose:

```text
expose controlled tools to agents
```

Required components:

```text
mcp_server.py
tool_registry.py
tool_models.py
tool_policy.py
tool_call_logger.py
agentx_init_adapter.py
patch_execution_adapter.py
filesystem_adapter.py
command_runner_adapter.py
git_adapter.py
```

Required tools:

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

Tool request schema:

```json
{
  "schema_version": "1.0",
  "tool_call_id": "string",
  "tool_name": "string",
  "caller": "string",
  "timestamp": "string",
  "arguments": {},
  "requested_effect": "read|write|execute|validate|report|plan|proposal",
  "session_id": "string|null"
}
```

Tool result schema:

```json
{
  "schema_version": "1.0",
  "tool_result_id": "string",
  "tool_call_id": "string",
  "tool_name": "string",
  "timestamp": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "exit_code": 0,
  "message": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "errors": []
}
```

Acceptance:

```text
Initiator tools callable
patch tools callable
unsafe tool calls blocked
tool outputs schema-valid
tool calls audited
```

---

# 15. MCP and Tool Trust Tiers

Trust tiers:

```text
TRUST_TIER_0_READ_ONLY
TRUST_TIER_1_LOCAL_STATE_WRITE
TRUST_TIER_2_APPROVED_SOURCE_WRITE
TRUST_TIER_3_VALIDATION_EXECUTION
TRUST_TIER_4_GIT_WRITE
TRUST_TIER_5_NETWORK_OR_EXTERNAL
TRUST_TIER_6_BLOCKED
```

Each tool must declare:

```json
{
  "tool_name": "string",
  "trust_tier": "TRUST_TIER_0_READ_ONLY",
  "requested_effects": [],
  "requires_governance": false,
  "requires_human_approval": false,
  "writes_source": false,
  "uses_network": false,
  "allowlisted": true
}
```

Rule:

```text
no tool executes unless trust tier, policy, and permission checks pass
```

---

# 16. Layer 6 — Model Adapter Layer

Purpose:

```text
connect to local or hosted LLMs through replaceable interface
```

Required components:

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

Supported model types:

```text
local small coder model
local general instruction model
OpenAI-compatible local server
Ollama
LM Studio
OpenCode-compatible provider
optional hosted fallback
```

Model acceptance criteria:

```text
JSON validity rate
schema-valid worker output rate
forbidden-file compliance
patch success rate
validation repair success rate
latency
VRAM use
context budget compatibility
failure rate
```

Forbidden:

```text
model directly edits files
model executes commands
model overrides governance
model approves itself
model decides promotion
```

---

# 17. Layer 7 — Local Model Runtime Profile

Purpose:

```text
make the system practical on limited hardware
```

Profiles:

```text
cpu_only_safe
small_gpu_8gb
balanced_local
hosted_fallback_optional
```

Rules:

```text
one model loaded at a time
small context packets
no whole-repo prompts
short JSON outputs
bounded retries
model timeout
VRAM-aware model selection
fallback only when configured
```

Acceptance:

```text
system can run with small local model profile
```

---

# 18. Layer 8 — Context Builder / Task Packer

Purpose:

```text
create bounded task packets for the model
```

Required components:

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

Task packet:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_packet.schema.json",
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
  "token_budget": 0,
  "warnings": [],
  "errors": []
}
```

Acceptance:

```text
bounded packet produced
allowed/forbidden files included
schema included
token budget respected
deterministic for same inputs
```

---

# 19. Layer 9 — Prompt Contract / Prompt Versioning

Purpose:

```text
make prompts controlled, testable, and versioned
```

Prompt contract:

```json
{
  "schema_version": "1.0",
  "prompt_id": "string",
  "prompt_version": "string",
  "task_type": "string",
  "input_schema": "string",
  "output_schema": "string",
  "allowed_tools": [],
  "forbidden_behavior": [],
  "model_profiles": [],
  "template": "string",
  "test_cases": []
}
```

Rules:

```text
no production prompt may be unversioned
prompt changes must be recorded
output schema must be explicit
prompt tests must include invalid-output cases
```

---

# 20. Layer 10 — LLM Implementation Worker

Purpose:

```text
convert task packets into implementation plans or patch candidates
```

Required components:

```text
llm_implementation_worker.py
edit_plan_generator.py
patch_candidate_generator.py
test_candidate_generator.py
validation_fix_generator.py
worker_output_schema.py
```

Outputs:

```text
edit_plan.json
patch_candidate.json
test_candidate.json
validation_fix_attempt.json
```

Forbidden:

```text
direct file writes
direct command execution
governance decisions
source mutation authority
broad repo refactors unless task packet allows
editing forbidden files
```

Acceptance:

```text
consumes task packets
produces schema-valid patch candidates
handles insufficient context safely
generates small code/test changes
does not call filesystem directly
```

---

# 21. Layer 11 — Self-Evolution Orchestrator

Purpose:

```text
coordinate the governed implementation loop
```

Core loop:

```text
1. Run agentx-init scan.
2. Run agentx-init status.
3. Run agentx-init plan.
4. Select one candidate.
5. Run agentx-init propose.
6. Run governance/risk check.
7. Build task packet.
8. Ask LLM worker for patch candidate.
9. Send candidate to patch execution layer.
10. Run validation.
11. If validation passes, accept session.
12. If validation fails, attempt bounded repair or rollback.
13. Record audit/memory/graph evidence.
14. Produce completion record.
```

Session states:

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

Forbidden:

```text
skipping governance
skipping validation
direct model-to-file editing
silent acceptance of failed validation
unlimited repair loops
self-modification of governance rules
```

---

# 22. Agent Roles and Tool Permission Matrix

Roles:

```text
Orchestrator
Implementation Worker
Validation Repair Worker
Reviewer Assistant
Promotion Checker
```

| Role | Allowed Tools | Forbidden Tools |
|---|---|---|
| Orchestrator | agentx_scan, agentx_status, agentx_plan, agentx_propose, agentx_validate, patch_session_status | direct file write, raw shell |
| Implementation Worker | model_adapter only | filesystem, shell, git, governance override |
| Validation Repair Worker | model_adapter, context_builder | direct patch apply, raw shell |
| Reviewer Assistant | read-only session/report/graph tools | patch_apply, write_file, commit |
| Promotion Checker | git_status, git_diff, validation read, governance read | push, merge, force reset |

Rule:

```text
only deterministic tool layers may mutate files
no model role may mutate files directly
```

---

# 23. Risk-Tiered Automation Levels

Automation levels:

```text
AUTO_LEVEL_0_READ_ONLY
AUTO_LEVEL_1_DRY_RUN_ONLY
AUTO_LEVEL_2_LOW_RISK_AUTOMATED_PATCH
AUTO_LEVEL_3_HUMAN_APPROVED_PATCH
AUTO_LEVEL_4_PROMOTION_REVIEW_REQUIRED
AUTO_LEVEL_5_BLOCKED
```

Default mapping:

```text
docs/report-only change              -> LEVEL_2 if validation passes
test-only change                     -> LEVEL_2 or LEVEL_3
schema change                        -> LEVEL_3
tool policy change                   -> LEVEL_3 or LEVEL_4
model/prompt contract change         -> LEVEL_3
validation allowlist change          -> LEVEL_4
governance rule change               -> LEVEL_4
security/path-boundary change        -> LEVEL_4
L0 change                            -> LEVEL_5 BLOCKED
governance bypass                    -> LEVEL_5 BLOCKED
uncontrolled shell/network access    -> LEVEL_5 BLOCKED
```

---

# 24. Human Review / Approval Interface

Commands:

```text
agentx-evolve review <session_id>
agentx-evolve approve <session_id>
agentx-evolve reject <session_id>
agentx-evolve explain <session_id>
```

Approval required for:

```text
L1 governance/rules changes
schema contract changes
multi-file source changes above threshold
validation failure override
promotion decision
Git commit
HIGH or CRITICAL risk
rollback failure
```

Human may not override:

```text
L0 mutation block
path traversal block
missing rollback snapshot for source mutation
source guard failure
governance artifact missing for mutation
schema validation failure for promotion evidence
uncontrolled shell execution
network access in local_only mode
```

---

# 25. Promotion / Release Gate

Promotion statuses:

```text
IMPLEMENTED_UNVALIDATED
VALIDATED_LOCAL
REVIEWED
PROMOTION_READY
PROMOTED
REJECTED
ROLLED_BACK
```

Required checks:

```text
governance allowed
risk acceptable
validation passed
source guard passed
no forbidden paths changed
completion evidence exists
rollback available or intentionally unnecessary
human approval present when required
Git diff cleanly scoped
```

First version:

```text
no auto-commit or auto-merge
promotion recommendation only
```

---

# 26. Git Integration Layer

Git phases:

```text
Git Phase 1: status/diff only
Git Phase 2: create branch only
Git Phase 3: stage approved files only
Git Phase 4: commit approved session only
Git Phase 5: push never automatic unless separately authorized
```

Initially forbidden:

```text
push
force push
merge main
rebase
delete branch
reset --hard without rollback policy
```

---

# 27. Dry-Run Mode

Required commands:

```text
agentx-patch apply --dry-run
agentx-evolve run --dry-run
agentx-evolve approve --dry-run
agentx-evolve promote --dry-run
```

Dry-run must:

```text
load same inputs
run same governance checks
run same path checks
show intended changed files
show intended commands
show validation plan
show rollback plan
write dry-run evidence
avoid source mutation
avoid Git mutation
```

---

# 28. Artifact Integrity and Provenance

Major artifacts must include:

```json
{
  "artifact_id": "string",
  "artifact_type": "string",
  "source_component": "string",
  "source_command": "string|null",
  "source_session_id": "string|null",
  "input_artifact_refs": [],
  "output_artifact_refs": [],
  "content_hash": "string",
  "created_at": "string"
}
```

Rules:

```text
hash deterministic
hash excludes content_hash field
canonical JSON for JSON hashes
unknown provenance requires human review
```

---

# 29. Cross-Layer Traceability Matrix

| Stage | Required Artifact | Required Link |
|---|---|---|
| Scan/status | scan/status artifacts | input_refs |
| Planning | evolution plan/candidate | candidate_action_id |
| Proposal | patch proposal | proposal_id |
| Governance | governance decision | decision_id |
| Risk | risk assessment | assessment_id |
| Context | task packet | task_packet_id |
| Prompt/model | prompt run/model response | prompt_run_id/model_run_id |
| Worker output | patch candidate | worker_output_id |
| Patch execution | implementation session | implementation_session_id |
| Rollback | rollback record | rollback_id |
| Validation | validation report | validation_report_id |
| Review | approval record | approval_id |
| Promotion | promotion decision | promotion_decision_id |
| Evidence | audit/memory/graph records | evidence_ids |

Rule:

```text
no session may be ACCEPTED or PROMOTION_READY unless this chain is complete or missing links are explicitly justified
```

---

# 30. Secrets, Environment, and Provider Policy

Rules:

```text
API keys only in approved local config or environment
secrets never written to audit/memory/model logs
prompt logs redacted before persistence
provider credentials excluded from task packets
hosted provider use explicitly configured
network disabled by default
```

Provider modes:

```text
local_only
local_with_hosted_fallback
hosted_allowed
```

Default:

```text
local_only
```

---

# 31. Privacy and Prompt-Data Retention

Defaults:

```text
prompt metadata retained
prompt hash retained
full prompt text disabled by default
full model response disabled by default
schema-invalid model response retained redacted if needed for debugging
```

If provider mode is not `local_only`, task packets must be redacted and size-limited before external transmission.

---

# 32. Supply-Chain and Dependency Provenance

Required records:

```text
dependency_provenance.json
dependency_allowlist.json
model_allowlist.json
mcp_server_allowlist.json
```

Dependency categories:

```text
python packages
system binaries
model providers
local inference servers
MCP servers
Git commands
validation commands
network endpoints
```

Rules:

```text
no dependency introduced silently
no model provider introduced silently
no MCP server introduced silently
no system binary used unless allowlisted
local-only mode has no hidden network dependency
```

---

# 33. License and Third-Party Model Policy

Every model profile must record:

```text
model_id
provider
license
local_or_hosted
commercial_use_allowed
redistribution_allowed
notes
```

Rules:

```text
model license recorded before use
unknown license only experimental
hosted provider terms noted
no model weights committed to repository
no third-party proprietary prompt/data embedded in source
```

---

# 34. Resource and Backpressure Limits

Required limits:

```text
max active sessions
max changed files per session
max repair attempts
max model retries
max validation runtime
max tool runtime
max context tokens
max file size in context
max rollback snapshot size
max JSONL read window
```

First defaults:

```text
max active sessions: 1
max changed files per session: 5
max repair attempts: 1
max model retries: 2
network access: disabled
parallel model runs: disabled
parallel patch sessions: disabled
```

If exceeded:

```text
BLOCKED_RESOURCE_LIMIT
```

---

# 35. Contract-Change Governance

Higher-risk contract-controlled files:

```text
governance rules
capability policy
tool policy
model policy
schemas
prompt contracts
security sandbox rules
path boundary rules
validation allowlists
promotion rules
rollback rules
```

Changes require:

```text
explicit proposal
governance review
risk review
human approval
schema validation
documentation sync check
rollback snapshot
promotion gate
```

Always blocked:

```text
automatic L0 modification
automatic governance bypass
automatic disabling of source guard
automatic disabling of validation
automatic weakening of path boundary
automatic weakening of rollback
```

---

# 36. Safe Mode and Emergency Stop

Safe mode allows:

```text
scan
status
report
audit read
memory read
graph read/query
session status
rollback inspection
```

Safe mode blocks:

```text
patch apply
write file
delete file
model implementation worker
live self-evolution session
Git write operations
promotion
```

Emergency stop triggers:

```text
source guard fails
rollback fails
unexpected file changes detected
schema validation repeatedly fails
tool policy missing
capability registry missing
lock corruption detected
governance artifact missing for mutation
```

Recovery requires:

```text
human inspection
audit evidence
reason for stop
specific unlock action
no evidence deletion
```

---

# 37. Rollback Verification

After rollback, verify:

```text
changed files match pre-session hashes
unexpected files removed or reported
deleted files restored
new files removed if created by session
source guard passes
git diff matches expected rollback state
rollback record validates
audit event written
```

If rollback verification fails:

```text
enter safe mode
block further patch sessions
record ROLLBACK_FAILED
require human review
preserve all evidence
```

---

# 38. Evaluation Harness / Regression Benchmarks

Required fixtures:

```text
simple docs change
simple test addition
simple schema addition
simple bug fix
forbidden L0 edit attempt
unsafe shell attempt
validation failure repair
rollback scenario
malformed model output
insufficient context scenario
concurrent session lock conflict
schema validation failure
source guard failure
```

Required metrics:

```text
task success rate
rollback success rate
schema-valid output rate
forbidden action block rate
validation pass rate
small-model completion rate
average runtime
failure recovery rate
```

---

# 39. Simulated Model Mode

A deterministic simulated model must support:

```text
return valid patch candidate
return invalid JSON
return forbidden-file edit
return insufficient-context result
return validation-fix candidate
return hallucinated file path
```

The evaluation harness must pass in simulated model mode before real model mode is trusted.

---

# 40. Long-Term Learning / Outcome Review

First version:

```text
no model training
structured outcome records only
```

Records:

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

---

# 41. Documentation Synchronization

Required checks:

```text
public functions match FIC
schema fields match docs
runtime artifacts match schemas
CLI commands match command docs
milestone docs match implemented commands
prompt contracts match output schemas
tool schemas match MCP behavior
```

---

# 42. Task Queue / Session Scheduler

First version:

```text
manual queue only
no background daemon
```

Capabilities:

```text
list candidate sessions
queue task
start task
pause task
resume task
cancel task
show blocked reason
```

---

# 43. Monitoring / Observability

Required views:

```text
current session
last failure
last validation
changed files
rollback status
model used
tool calls
audit events
prompt version
token/context budget
```

A failed or successful session must be reconstructable from traces.

---

# 44. Backup and Disaster Recovery

Backup categories:

```text
audit history
implementation sessions
rollback snapshots
approvals
promotion records
policies
model run metadata
tool call history
evaluation results
```

Commands reserved:

```text
agentx-evolve backup
agentx-evolve restore --from <backup>
agentx-evolve backup-status
```

Recovery scenarios:

```text
corrupted latest artifact
malformed JSONL line
missing rollback snapshot
interrupted patch session
interrupted validation
partial tool call record
stale lock
failed migration
lost policy file
```

---

# 45. Cross-Platform Path Rules

First target:

```text
Linux primary
macOS possible if tests pass
Windows not guaranteed unless tested
```

Rules:

```text
normalize all paths before policy checks
store repo-relative paths in durable artifacts where possible
document case sensitivity assumptions
resolve symlinks before writes
canonicalize separators in JSON artifacts
```

Tests:

```text
relative traversal
absolute path escape
symlink escape
mixed separators
case ambiguity note
write outside repository
write outside allowed source scope
```

---

# 46. Controlled Degradation Mode

Modes:

```text
NO_MODEL_MODE
NO_MCP_MODE
NO_GIT_MODE
NO_NETWORK_MODE
NO_PROMOTION_MODE
READ_ONLY_SAFE_MODE
```

Behavior:

```text
without model: dry-run, proposal review, explicit patch only
without MCP: direct CLI adapters may be used
without Git: source guard works, commit/promotion limited
without network: local-only models/tools only
without promotion: sessions validated but not promoted
read-only safe mode: no mutation tools
```

Missing optional layers must produce clear `BLOCKED` or `DEGRADED` status, not a crash.

---

# 47. Packaging / Distribution

Commands:

```text
agentx-init
agentx-patch
agentx-evolve
```

Acceptance:

```text
fresh clone can install and run all tools
optional dependencies grouped
base install does not require GPU or hosted provider
```

Optional dependency groups:

```text
[local-model]
[mcp]
[git]
[dev]
[hosted-model]
```

---

# 48. Operator Runbook

Required sections:

```text
how to run dry-run session
how to run live low-risk session
how to inspect session status
how to approve/reject session
how to rollback session
how to inspect audit/memory/graph evidence
how to recover from failed validation
how to recover from failed rollback
how to disable model access
how to disable all mutation
how to clean temporary files safely
```

Emergency commands:

```text
agentx-evolve stop
agentx-evolve lock
agentx-evolve unlock --manual
agentx-patch rollback <session_id>
agentx-evolve status
```

---

# 49. Readiness Scorecard

Score categories:

```text
schema coverage
test coverage
negative-test coverage
source-boundary safety
rollback safety
audit/evidence quality
local-only compatibility
small-model compatibility
documentation alignment
operator recoverability
```

Minimum scores:

```text
deterministic safety layers: 10/10 required
model worker layer: 9/10 minimum with known limitations
orchestrator layer: 10/10 required for low-risk loop
promotion layer: 10/10 required before Git write operations
```

A layer below required score must not be used by later autonomous workflows.

---

# 50. Final System Acceptance Layer

Final acceptance tests:

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
schema validation passes for all new artifacts
tool protocol validates
prompt contracts validate
backup/restore can recover inspection state
controlled degradation works
```

Final done definition:

```text
identify a needed improvement
generate proposal
obtain governance/risk context
prepare bounded model context
generate implementation candidate
apply it safely
validate it
rollback if needed
record evidence
offer promotion recommendation
preserve source boundaries
operate with small local model profile
```

---

# 51. Minimum First Working Self-Evolving Version

The minimum viable self-evolving system requires:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer
Tool / MCP Adapter Layer
Model Adapter Layer
Local Model Runtime Profile
Prompt Contract / Prompt Versioning
Context Builder / Task Packer
LLM Implementation Worker
Self-Evolution Orchestrator
```

Human review and promotion may be manual at first, but must exist before higher-risk automated work.

---

# 52. What Not To Build Yet

Do not build before deterministic actuator and governance loop are stable:

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

# 53. Final Freeze Rule

This document is now frozen as the broad controlling full-stack roadmap.

Allowed future changes:

```text
PATCH: wording, examples, clarifications
MINOR: additive optional layer detail
MAJOR: new required layer, removed layer, changed build order, changed safety boundary
```

Blocked without explicit major revision:

```text
removing governance
removing rollback
removing source guard
removing human approval for high-risk work
allowing automatic L0 mutation
allowing uncontrolled shell/network
making hosted model mandatory
making Git push automatic
```

---

# 54. Next Required Document

The next document should not be another broad stack list.

The next document should be:

```text
AGENT_X_GOVERNED_PATCH_EXECUTION_LAYER_IMPLEMENTATION_SPEC.md
```

It should define the first concrete post-Initiator implementation slice.

---

# 55. Final Completeness Verdict

This v7 document covers:

```text
all required layers
build order
minimum implementation slices
schema contracts
runtime state layout
tool/MCP protocol
tool trust tiers
model adapter
local/small model constraints
context packing
prompt versioning
LLM worker boundaries
orchestration loop
human approval rules
non-overridable safety rules
promotion lifecycle
Git phases
evaluation fixtures
simulated model mode
rollback verification
dry-run behavior
artifact provenance
dependency allowlists
operator runbook
resource limits
safe mode
emergency stop
privacy and prompt retention
traceability matrix
readiness scorecard
supply-chain provenance
state backup/recovery
cross-platform path rules
license/model policy
controlled degradation
final freeze rule
```

Final rating:

```text
10/10 as the controlling post-Initiator full-stack roadmap
```
