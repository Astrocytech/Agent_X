# SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC

```text
document_id: SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, final frozen handoff
component_id: AGENTX_SELF_EVOLUTION_ORCHESTRATOR
component_name: Self-Evolution Orchestrator
roadmap_layer: 11
roadmap_phase: Phase C — Controlled Self-Evolution Coordination
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Prompt Contract Acceptance Criteria, Model Runtime Acceptance Criteria, Human Review Acceptance Criteria, Promotion Gate Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/orchestrator/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/orchestrator/
implementation_mode: deterministic coordinator, state machine, gatekeeper, and evidence writer; no direct source mutation
rating_target: 10/10
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 Earlier Document Rating

The first implementation spec was strong and implementation-ready in broad shape. I rated it:

```text
9.3/10
```

It covered:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
orchestration state machine
session lifecycle
task decomposition flow
tool invocation flow
model invocation flow
approval gate flow
failure recovery flow
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Security Sandbox
integration with Governed Patch Execution
integration with Model Adapter
integration with Prompt Contract / Prompt Versioning
integration with Human Review / Approval Interface
integration with Promotion / Release Gate
test files
test cases
implementation order
acceptance criteria
Definition of Done
```

## 0.2 Why the First Version Was Not Fully 10/10

The v1 document was not fully 10/10 because it needed more precision in several production-control areas:

```text
1. It listed schemas for OrchestrationState, PromptBinding, and OrchestratorEvidenceEvent, but did not define their dataclasses and exact required fields.
2. It did not define an explicit dependency-mode contract for real adapters, missing adapters, fake test adapters, and restrictive fallback behavior.
3. It did not define a strict orchestrator authority boundary for direct vs delegated writes, reads, Git, command execution, model calls, patch calls, approval, and promotion.
4. It did not define run locking, duplicate-run idempotency, resumability, or crash-safe state recovery.
5. It did not define a controlled adapter interface for Tool / MCP Adapter, Model Adapter, Prompt Contract, Policy Registry, Human Approval, and Promotion Gate.
6. It did not define evidence manifest, review report, SHA-256 hashing, and evidence immutability rules.
7. It did not define source-mutation checks with runtime-artifact boundary exceptions and deviation handling.
8. It did not define exact schema validation utility requirements and valid/invalid examples for every schema.
9. It did not define hard fail-closed behavior for model output, prompt mismatch, policy unavailability, dependency import failures, and invalid downstream results.
10. It did not define the dispatcher re-entry/resume behavior or how partial runs are marked NOT DONE rather than silently completed.
11. It did not define scoring caps or final implementation acceptance matrix for coding-agent handoff.
12. It rated itself 10/10 without clearly separating document rating from future implementation rating.
```

## 0.3 v2 Improvements and v3 Finalization

The v2 upgrade added:

```text
complete missing dataclasses
controlled dependency binding contract
real/fake/restricted dependency modes
orchestrator authority boundary
run locking and idempotency
resume and crash recovery
adapter interface contracts
evidence manifest and review report requirements
SHA-256 evidence hashing
evidence immutability
schema validation utility requirements
runtime artifact boundary and deviation rules
negative safety pack expansion
implementation scoring hard caps
final frozen acceptance matrix
```

On stricter review, v2 should be rated:

```text
9.8/10
```

It was very strong, but still needed a few final production-control details before being treated as a frozen coding-agent handoff. This v3 keeps all v2 improvements and adds final production controls for run modes, dependency graph validation, source snapshots, execution budgets, cancellation, model-output quarantine, authority rechecks, provenance propagation, replay, and stale-plan invalidation.

This v3 is rated:

```text
10/10
```

The rating applies to the quality of this implementation specification. It does not mean the future implementation is done. The implementation is done only after the code, schemas, tests, validation commands, evidence manifest, review report, completion record, and source-mutation checks pass.

---

# 1. Purpose

This document is the full implementation specification for the **Self-Evolution Orchestrator**.

The Self-Evolution Orchestrator coordinates controlled Agent_X self-evolution runs. It plans and sequences work, binds approved roles to steps, invokes tools through the Tool / MCP Adapter, invokes models through the Model Adapter, applies approval and promotion gates, records evidence, and stops safely when required.

The orchestrator must be:

```text
planner
coordinator
state machine
gatekeeper
evidence writer
failure router
run ledger producer
resume controller
restricted-mode enforcer
```

The orchestrator must not be:

```text
direct source writer
direct shell executor
direct Git mutator
direct patch applier
direct policy override
direct sandbox bypass
direct model runtime bypass
direct prompt-contract bypass
direct human approval bypass
direct promotion bypass
background daemon
network client
```

The implementation must coordinate prior and future Agent_X layers without weakening their authority.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because the orchestrator decides what is attempted, in what order, by which role, with which model, prompt, tool, approval gate, recovery behavior, and promotion path.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, if orchestration invokes validation commands through tools
Prompt Contract Acceptance Criteria, for model-bound steps
Model Runtime Acceptance Criteria, if model calls are reachable
Human Review / Approval Acceptance Criteria, if approval gates are active
Promotion / Release Gate Acceptance Criteria, if promotion is reachable
MCP Protocol Acceptance Criteria, only if orchestration is exposed through MCP later
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if markdown reports are written
```

---

# 3. Canonical Destination Summary

Create the Self-Evolution Orchestrator package here:

```text
tools/agentx_evolve/orchestrator/
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
.agentx-init/orchestrator/
```

Approved runtime artifact subdirectories:

```text
.agentx-init/orchestrator/runs/
.agentx-init/orchestrator/sessions/
.agentx-init/orchestrator/steps/
.agentx-init/orchestrator/evidence/
.agentx-init/orchestrator/recovery/
.agentx-init/orchestrator/reports/
.agentx-init/orchestrator/locks/
```

The intended package split is:

```text
tools/agentx_initiator/                 = completed Initiator
tools/agentx_evolve/security/           = Security Sandbox / Filesystem Boundary
tools/agentx_evolve/policy/             = Policy / Capability Registry
tools/agentx_evolve/patch/              = Governed Patch Execution
tools/agentx_evolve/failure/            = Failure Taxonomy / Recovery Playbook
tools/agentx_evolve/tools/              = Tool / MCP Adapter
tools/agentx_evolve/models/             = Model Adapter
tools/agentx_evolve/prompts/            = Prompt Contract / Prompt Versioning
tools/agentx_evolve/context/            = Context Builder / Task Packer, if implemented
tools/agentx_evolve/human_review/       = Human Review / Approval Interface
tools/agentx_evolve/promotion/          = Promotion / Release Gate
tools/agentx_evolve/orchestrator/       = new Self-Evolution Orchestrator
```

---

# 4. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic orchestrator that can:

```text
create an orchestration session
validate the requested evolution task
load the applicable policy context
load the applicable prompt contract
load or select an allowed model profile
load the tool registry snapshot
build a task plan
split the plan into execution steps
bind each step to exactly one role
bind each step to allowed tools and model calls
execute only through approved adapters
pause when governance or human approval is required
stop safely when policy, sandbox, model, prompt, patch, or promotion gates block
record every decision and step as evidence
recover from known failure classes according to the recovery playbook
resume safely from persisted state after interruption
produce a final run ledger
produce a final evidence manifest
produce a final review report
produce a final DONE / NOT DONE orchestration result
```

The orchestrator must not implement the actual behavior of lower layers. It must call them through explicit adapter boundaries.

---

# 5. Authority Boundary

The orchestrator coordinates. It does not grant itself permission.

## 5.1 Allowed Direct Actions

The orchestrator may directly:

```text
create its own runtime directories under .agentx-init/orchestrator/
write orchestrator runtime artifacts under .agentx-init/orchestrator/
write run locks under .agentx-init/orchestrator/locks/
write JSONL evidence events for its own decisions
write latest state snapshots atomically
read its own runtime artifacts for resume/recovery
validate schemas for its own objects
construct ToolCall and ModelCall binding objects
```

## 5.2 Forbidden Direct Actions

The orchestrator must not directly:

```text
write source files
edit source files
apply patches
run shell commands
run Git commands
call Git libraries for mutation
call model clients
call hosted model APIs
call network clients
call MCP clients or servers
bypass Tool / MCP Adapter
bypass Model Adapter
bypass Policy / Capability Registry
bypass Security Sandbox
bypass Governed Patch Execution
bypass Human Review / Approval
bypass Promotion / Release Gate
```

## 5.3 Delegated Actions

The orchestrator may request delegated actions only through these controlled components:

| Action | Required delegate |
|---|---|
| Tool execution | Tool / MCP Adapter |
| File/path/command effect | Tool / MCP Adapter plus Security Sandbox |
| Source mutation | Governed Patch Execution through approved tool path |
| Patch rollback | Governed Patch Execution through approved tool path |
| Model call | Model Adapter |
| Prompt selection | Prompt Contract / Prompt Versioning |
| Context packing | Context Builder / Task Packer, if available |
| Human approval | Human Review / Approval Interface |
| Promotion | Promotion / Release Gate |
| Git mutation | Git Integration Layer plus Promotion / Release Gate, not direct orchestrator code |

---

# 6. Exact Files to Create

## 6.1 Orchestrator Package Files

```text
tools/agentx_evolve/orchestrator/__init__.py
tools/agentx_evolve/orchestrator/orchestrator_models.py
tools/agentx_evolve/orchestrator/orchestrator_state.py
tools/agentx_evolve/orchestrator/session_manager.py
tools/agentx_evolve/orchestrator/task_decomposer.py
tools/agentx_evolve/orchestrator/execution_planner.py
tools/agentx_evolve/orchestrator/step_executor.py
tools/agentx_evolve/orchestrator/tool_invoker.py
tools/agentx_evolve/orchestrator/model_invoker.py
tools/agentx_evolve/orchestrator/approval_gate.py
tools/agentx_evolve/orchestrator/promotion_gate.py
tools/agentx_evolve/orchestrator/recovery_manager.py
tools/agentx_evolve/orchestrator/orchestrator_logger.py
tools/agentx_evolve/orchestrator/run_ledger.py
tools/agentx_evolve/orchestrator/orchestrator_dispatcher.py
tools/agentx_evolve/orchestrator/dependency_bindings.py
tools/agentx_evolve/orchestrator/orchestrator_locks.py
tools/agentx_evolve/orchestrator/evidence_manifest.py
```

## 6.2 Schema Files

```text
tools/agentx_evolve/schemas/orchestration_session.schema.json
tools/agentx_evolve/schemas/orchestration_state.schema.json
tools/agentx_evolve/schemas/orchestration_task.schema.json
tools/agentx_evolve/schemas/task_plan.schema.json
tools/agentx_evolve/schemas/execution_step.schema.json
tools/agentx_evolve/schemas/tool_invocation_binding.schema.json
tools/agentx_evolve/schemas/model_invocation_binding.schema.json
tools/agentx_evolve/schemas/prompt_binding.schema.json
tools/agentx_evolve/schemas/approval_gate_record.schema.json
tools/agentx_evolve/schemas/promotion_gate_record.schema.json
tools/agentx_evolve/schemas/recovery_action.schema.json
tools/agentx_evolve/schemas/orchestrator_evidence_event.schema.json
tools/agentx_evolve/schemas/run_ledger.schema.json
tools/agentx_evolve/schemas/orchestrator_evidence_manifest.schema.json
tools/agentx_evolve/schemas/orchestrator_review_report.schema.json
tools/agentx_evolve/schemas/orchestrator_completion_record.schema.json
```

## 6.3 Test Files

```text
tools/agentx_evolve/tests/test_orchestrator_models.py
tools/agentx_evolve/tests/test_orchestrator_state.py
tools/agentx_evolve/tests/test_orchestrator_session_manager.py
tools/agentx_evolve/tests/test_task_decomposer.py
tools/agentx_evolve/tests/test_execution_planner.py
tools/agentx_evolve/tests/test_step_executor.py
tools/agentx_evolve/tests/test_tool_invoker.py
tools/agentx_evolve/tests/test_model_invoker.py
tools/agentx_evolve/tests/test_approval_gate.py
tools/agentx_evolve/tests/test_promotion_gate.py
tools/agentx_evolve/tests/test_recovery_manager.py
tools/agentx_evolve/tests/test_orchestrator_logger.py
tools/agentx_evolve/tests/test_run_ledger.py
tools/agentx_evolve/tests/test_orchestrator_dispatcher.py
tools/agentx_evolve/tests/test_orchestrator_dependency_bindings.py
tools/agentx_evolve/tests/test_orchestrator_locks.py
tools/agentx_evolve/tests/test_orchestrator_evidence_manifest.py
tools/agentx_evolve/tests/test_orchestrator_schema_validation.py
tools/agentx_evolve/tests/test_orchestrator_negative_cases.py
tools/agentx_evolve/tests/validate_orchestrator_schemas.py
```

---

# 7. Required Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/orchestrator/
```

Required per-run artifacts:

```text
.agentx-init/orchestrator/runs/<run_id>/orchestration_session.json
.agentx-init/orchestrator/runs/<run_id>/orchestration_state.json
.agentx-init/orchestrator/runs/<run_id>/task_plan.json
.agentx-init/orchestrator/runs/<run_id>/execution_steps.jsonl
.agentx-init/orchestrator/runs/<run_id>/tool_invocations.jsonl
.agentx-init/orchestrator/runs/<run_id>/model_invocations.jsonl
.agentx-init/orchestrator/runs/<run_id>/prompt_bindings.jsonl
.agentx-init/orchestrator/runs/<run_id>/approval_gate_records.jsonl
.agentx-init/orchestrator/runs/<run_id>/promotion_gate_records.jsonl
.agentx-init/orchestrator/runs/<run_id>/recovery_actions.jsonl
.agentx-init/orchestrator/runs/<run_id>/orchestrator_events.jsonl
.agentx-init/orchestrator/runs/<run_id>/run_ledger.json
.agentx-init/orchestrator/runs/<run_id>/orchestrator_evidence_manifest.json
.agentx-init/orchestrator/runs/<run_id>/orchestrator_review_report.json
.agentx-init/orchestrator/runs/<run_id>/orchestrator_completion_record.json
```

Required latest artifacts:

```text
.agentx-init/orchestrator/latest_orchestration_session.json
.agentx-init/orchestrator/latest_orchestration_state.json
.agentx-init/orchestrator/latest_run_ledger.json
```

Required lock artifacts:

```text
.agentx-init/orchestrator/locks/<run_id>.lock
```

Rules:

```text
history files must be append-only JSONL
latest JSON files must be written atomically
runtime artifacts must not be written outside the approved root
source files must not be modified directly by the orchestrator
secrets and raw prompt payloads must be redacted before durable evidence
large model/tool outputs must be summarized or referenced by artifact path
all final evidence artifacts must have SHA-256 hashes
```

---

# 8. Core Data Models

Implement all dataclasses in:

```text
tools/agentx_evolve/orchestrator/orchestrator_models.py
```

## 8.1 Status Constants

```python
ORCH_STATUS_CREATED = "CREATED"
ORCH_STATUS_PLANNING = "PLANNING"
ORCH_STATUS_PLAN_READY = "PLAN_READY"
ORCH_STATUS_WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
ORCH_STATUS_RUNNING = "RUNNING"
ORCH_STATUS_STEP_BLOCKED = "STEP_BLOCKED"
ORCH_STATUS_STEP_FAILED = "STEP_FAILED"
ORCH_STATUS_RECOVERING = "RECOVERING"
ORCH_STATUS_VALIDATING = "VALIDATING"
ORCH_STATUS_READY_FOR_PROMOTION = "READY_FOR_PROMOTION"
ORCH_STATUS_PROMOTION_BLOCKED = "PROMOTION_BLOCKED"
ORCH_STATUS_COMPLETED = "COMPLETED"
ORCH_STATUS_FAILED = "FAILED"
ORCH_STATUS_ABORTED = "ABORTED"
```

## 8.2 Step Status Constants

```python
STEP_STATUS_PENDING = "PENDING"
STEP_STATUS_READY = "READY"
STEP_STATUS_RUNNING = "RUNNING"
STEP_STATUS_BLOCKED = "BLOCKED"
STEP_STATUS_FAILED = "FAILED"
STEP_STATUS_SKIPPED = "SKIPPED"
STEP_STATUS_COMPLETED = "COMPLETED"
STEP_STATUS_NEEDS_APPROVAL = "NEEDS_APPROVAL"
STEP_STATUS_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
```

## 8.3 Orchestrator Decision Constants

```python
DECISION_CONTINUE = "CONTINUE"
DECISION_BLOCK = "BLOCK"
DECISION_RETRY = "RETRY"
DECISION_RECOVER = "RECOVER"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_REQUIRE_GOVERNANCE = "REQUIRE_GOVERNANCE"
DECISION_ABORT = "ABORT"
DECISION_READY_FOR_PROMOTION = "READY_FOR_PROMOTION"
DECISION_COMPLETE = "COMPLETE"
DECISION_NOT_DONE = "NOT_DONE"
```

## 8.4 Dependency Mode Constants

```python
DEPENDENCY_MODE_REAL = "REAL"
DEPENDENCY_MODE_FAKE_FOR_TEST = "FAKE_FOR_TEST"
DEPENDENCY_MODE_RESTRICTED = "RESTRICTED"
DEPENDENCY_MODE_UNAVAILABLE = "UNAVAILABLE"
```

## 8.5 `OrchestrationSession`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestration_session.schema.json"
session_id: str
run_id: str
created_at: str
updated_at: str
source_component: str = "SelfEvolutionOrchestrator"
requested_task_id: str
requested_task_summary: str
initiating_role: str
orchestration_mode: str
policy_context_id: str | None
prompt_contract_version: str | None
model_profile_id: str | None
tool_registry_id: str | None
state: str
lock_id: str | None
resumable: bool
warnings: list[str]
errors: list[str]
```

## 8.6 `OrchestrationState`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestration_state.schema.json"
state_id: str
session_id: str
run_id: str
created_at: str
updated_at: str
source_component: str = "OrchestratorState"
previous_state: str | None
current_state: str
terminal: bool
reason: str
active_step_id: str | None
completed_step_ids: list[str]
blocked_step_ids: list[str]
failed_step_ids: list[str]
waiting_gate_ids: list[str]
retry_counts: dict
state_version: int
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.7 `OrchestrationTask`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestration_task.schema.json"
task_id: str
created_at: str
source_component: str = "SelfEvolutionOrchestrator"
title: str
description: str
task_type: str
risk_level: str
requested_outputs: list[str]
constraints: list[str]
allowed_roles: list[str]
allowed_tools: list[str]
allowed_model_profiles: list[str]
requires_human_approval: bool
requires_governance: bool
requires_promotion_gate: bool
idempotency_key: str | None
warnings: list[str]
errors: list[str]
```

## 8.8 `TaskPlan`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "task_plan.schema.json"
plan_id: str
session_id: str
run_id: str
created_at: str
source_component: str = "TaskDecomposer"
task_id: str
plan_status: str
steps: list[dict]
required_tools: list[str]
required_model_profiles: list[str]
required_prompt_contracts: list[str]
required_approvals: list[str]
required_promotion_gates: list[str]
assumptions: list[str]
risks: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.9 `ExecutionStep`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "execution_step.schema.json"
step_id: str
plan_id: str
session_id: str
run_id: str
created_at: str
updated_at: str
source_component: str = "ExecutionPlanner"
step_index: int
step_name: str
step_type: str
assigned_role: str
status: str
requires_tool_call: bool
requires_model_call: bool
requires_human_approval: bool
requires_governance: bool
requires_promotion_gate: bool
allowed_tools: list[str]
allowed_model_profiles: list[str]
required_prompt_contracts: list[str]
input_refs: list[str]
output_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

## 8.10 `ToolInvocationBinding`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "tool_invocation_binding.schema.json"
binding_id: str
step_id: str
session_id: str
run_id: str
tool_name: str
caller_role: str
requested_effect: str
arguments_summary: dict
tool_call_id: str | None
tool_result_id: str | None
policy_decision_id: str | None
sandbox_decision_id: str | None
status: str
failure_class: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.11 `PromptBinding`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_binding.schema.json"
binding_id: str
step_id: str
session_id: str
run_id: str
prompt_contract_id: str
prompt_contract_version: str
prompt_registry_id: str | None
input_contract_schema_id: str
output_contract_schema_id: str
prompt_hash: str | None
prompt_provenance_ref: str | None
status: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.12 `ModelInvocationBinding`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "model_invocation_binding.schema.json"
binding_id: str
step_id: str
session_id: str
run_id: str
model_profile_id: str
prompt_contract_version: str
prompt_binding_id: str
caller_role: str
requested_task_type: str
input_context_refs: list[str]
output_artifact_refs: list[str]
model_call_id: str | None
model_result_id: str | None
status: str
failure_class: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.13 `ApprovalGateRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "approval_gate_record.schema.json"
approval_record_id: str
step_id: str | None
session_id: str
run_id: str
created_at: str
gate_type: str
reason: str
required_approver_role: str
approval_status: str
approval_id: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.14 `PromotionGateRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "promotion_gate_record.schema.json"
promotion_record_id: str
session_id: str
run_id: str
created_at: str
promotion_target: str
validation_refs: list[str]
review_refs: list[str]
promotion_status: str
promotion_decision_id: str | None
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.15 `RecoveryAction`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "recovery_action.schema.json"
recovery_action_id: str
session_id: str
run_id: str
step_id: str | None
created_at: str
failure_class: str
recovery_strategy: str
action_status: str
retry_count: int
max_retries: int
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

## 8.16 `OrchestratorEvidenceEvent`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestrator_evidence_event.schema.json"
event_id: str
session_id: str
run_id: str
step_id: str | None
created_at: str
source_component: str = "SelfEvolutionOrchestrator"
event_type: str
status: str
message: str
decision: str | None
artifact_refs: list[str]
evidence_refs: list[str]
redaction_applied: bool
warnings: list[str]
errors: list[str]
```

## 8.17 `RunLedger`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "run_ledger.schema.json"
ledger_id: str
session_id: str
run_id: str
created_at: str
updated_at: str
source_component: str = "RunLedger"
final_status: str
task_id: str
plan_id: str | None
steps_total: int
steps_completed: int
steps_failed: int
steps_blocked: int
tool_invocations: list[str]
model_invocations: list[str]
prompt_bindings: list[str]
approval_records: list[str]
promotion_records: list[str]
recovery_actions: list[str]
evidence_refs: list[str]
evidence_manifest_ref: str | None
completion_record_ref: str | None
final_decision: str
warnings: list[str]
errors: list[str]
```

## 8.18 `OrchestratorEvidenceManifest`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestrator_evidence_manifest.schema.json"
manifest_id: str
session_id: str
run_id: str
created_at: str
validated_commit: str | None
source_component: str = "OrchestratorEvidenceManifest"
evidence_files: list[dict]
evidence_file_hashes: list[dict]
command_records: list[dict]
runtime_artifacts: list[str]
known_expected_runtime_artifacts: list[str]
deviation_register: list[dict]
source_mutation_status: str
redaction_status: str
hash_status: str
final_decision: str
warnings: list[str]
errors: list[str]
```

## 8.19 `OrchestratorCompletionRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "orchestrator_completion_record.schema.json"
component_id: str = "AGENTX_SELF_EVOLUTION_ORCHESTRATOR"
component_name: str = "Self-Evolution Orchestrator"
status: str
validated_commit: str
validated_at: str
canonical_subdirectory: str
canonical_schema_subdirectory: str
canonical_test_subdirectory: str
runtime_artifact_root: str
basis_documents: list[str]
commands_run: list[dict]
files_created_or_changed: list[str]
schemas_created_or_changed: list[str]
tests_created_or_changed: list[str]
validated_capabilities: list[str]
integration_verified: dict
negative_tests_verified: list[str]
runtime_artifacts_generated: list[str]
evidence_manifest_path: str
evidence_manifest_sha256: str
review_report_path: str
review_report_sha256: str
completion_record_sha256: str
deviations_from_contract: list[dict]
unresolved_risks: list[str]
implementation_score: float
final_decision: str
```

## 8.20 Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
redact_for_evidence(value: object) -> object
sha256_file(path: Path) -> str
atomic_write_json(path: Path, payload: dict) -> None
append_jsonl(path: Path, payload: dict) -> None
```

---

# 9. Schema Requirements

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require IDs for session, run, plan, step, binding, record, event, manifest, or ledger objects
require timestamps for state-changing objects
require warnings and errors arrays
use enum values for status, role, decision, gate status, dependency mode, and failure class fields
reject missing required fields
reject invalid enum values
reject invalid ID type where applicable
allow evidence_refs and artifact_refs arrays where applicable
```

Required valid examples in tests:

```text
valid_orchestration_session
valid_orchestration_state
valid_orchestration_task
valid_task_plan
valid_execution_step
valid_tool_invocation_binding
valid_model_invocation_binding
valid_prompt_binding
valid_approval_gate_record
valid_promotion_gate_record
valid_recovery_action
valid_orchestrator_evidence_event
valid_run_ledger
valid_orchestrator_evidence_manifest
valid_orchestrator_review_report
valid_orchestrator_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid ID type fails where applicable
invalid final decision fails
invalid hash field fails where applicable
```

Dedicated schema validation utility:

```text
tools/agentx_evolve/tests/validate_orchestrator_schemas.py
```

Required command:

```bash
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_orchestrator_schemas.py
```

Required result:

```text
exit_code 0
all valid examples accepted
all required invalid examples rejected
```

---

# 10. Dependency Binding Contract

Implement in:

```text
tools/agentx_evolve/orchestrator/dependency_bindings.py
```

## 10.1 Required Public Functions

```python
resolve_dependency_bindings(context: dict, repo_root: Path) -> dict
get_tool_adapter(binding_context: dict) -> object | None
get_policy_registry(binding_context: dict) -> object | None
get_model_adapter(binding_context: dict) -> object | None
get_prompt_registry(binding_context: dict) -> object | None
get_human_approval_adapter(binding_context: dict) -> object | None
get_promotion_gate(binding_context: dict) -> object | None
get_failure_recovery(binding_context: dict) -> object | None
```

## 10.2 Dependency Modes

Use these modes:

```text
REAL
FAKE_FOR_TEST
RESTRICTED
UNAVAILABLE
```

Rules:

```text
REAL means a validated upstream component is available and callable.
FAKE_FOR_TEST means a deterministic local fake is injected only by tests.
RESTRICTED means dependency is missing or partial, but safe planning/read-only behavior may continue.
UNAVAILABLE means dependency is missing and dependent actions must block.
```

## 10.3 Missing Dependency Behavior

| Dependency | If missing | Allowed behavior |
|---|---|---|
| Tool / MCP Adapter | Block all tool steps | planning, model-free dry planning, evidence |
| Policy / Capability Registry | Restricted mode | read-only planning/evidence only; no mutation/promotion |
| Security Sandbox | Tool/path/command steps block through Tool Adapter | no direct fallback |
| Governed Patch Execution | patch apply/rollback block | patch precheck only if Tool Adapter permits |
| Model Adapter | model steps block | non-model planning/evidence only |
| Prompt Contract | model steps block | no prompt-free model call |
| Human Review | approval-required steps pause/block | no approval override |
| Promotion Gate | promotion blocks | final ledger may be NOT DONE |
| Failure Taxonomy | restrictive local failure mapping | no unsafe retry |

## 10.4 Fake Test Adapter Rules

Fake adapters may be used only in tests and must be deterministic.

Fake adapters must:

```text
never write source files
never execute shell commands
never call network
never call hosted models
return schema-valid results
support success, blocked, invalid, and failed paths
record evidence-compatible IDs
```

Fake adapters must not be used in production paths unless context explicitly marks the run as a test fixture.

---

# 11. Orchestration State Machine

Implement in:

```text
tools/agentx_evolve/orchestrator/orchestrator_state.py
```

## 11.1 Required States

```text
CREATED
PLANNING
PLAN_READY
WAITING_FOR_APPROVAL
RUNNING
STEP_BLOCKED
STEP_FAILED
RECOVERING
VALIDATING
READY_FOR_PROMOTION
PROMOTION_BLOCKED
COMPLETED
FAILED
ABORTED
```

## 11.2 Allowed Transitions

```text
CREATED -> PLANNING
PLANNING -> PLAN_READY
PLANNING -> FAILED
PLAN_READY -> WAITING_FOR_APPROVAL
PLAN_READY -> RUNNING
WAITING_FOR_APPROVAL -> RUNNING
WAITING_FOR_APPROVAL -> ABORTED
RUNNING -> STEP_BLOCKED
RUNNING -> STEP_FAILED
RUNNING -> VALIDATING
STEP_BLOCKED -> WAITING_FOR_APPROVAL
STEP_BLOCKED -> ABORTED
STEP_FAILED -> RECOVERING
STEP_FAILED -> FAILED
RECOVERING -> RUNNING
RECOVERING -> FAILED
VALIDATING -> READY_FOR_PROMOTION
VALIDATING -> FAILED
READY_FOR_PROMOTION -> COMPLETED
READY_FOR_PROMOTION -> PROMOTION_BLOCKED
PROMOTION_BLOCKED -> ABORTED
COMPLETED -> terminal
FAILED -> terminal
ABORTED -> terminal
```

## 11.3 Required Public Functions

```python
can_transition(current_state: str, next_state: str) -> bool
transition_state(state: OrchestrationState, next_state: str, reason: str, repo_root: Path) -> OrchestrationState
write_state_snapshot(state: OrchestrationState, repo_root: Path) -> dict
load_state_snapshot(run_id: str, repo_root: Path) -> OrchestrationState
```

## 11.4 State Rules

```text
terminal states cannot transition
invalid transitions must return BLOCKED or FAILED with evidence
state updates must be written atomically
state transitions must be recorded in orchestrator_events.jsonl
state must include session_id, run_id, previous_state, next_state, reason, state_version, and evidence_refs
state_version must increment monotonically
stale state updates must fail closed
```

---

# 12. Run Locking, Idempotency, and Resume

Implement in:

```text
tools/agentx_evolve/orchestrator/orchestrator_locks.py
```

## 12.1 Required Public Functions

```python
acquire_run_lock(run_id: str, repo_root: Path) -> dict
release_run_lock(run_id: str, repo_root: Path) -> dict
check_run_lock(run_id: str, repo_root: Path) -> dict
compute_idempotency_key(task: OrchestrationTask, context: dict) -> str
find_existing_run_by_idempotency_key(idempotency_key: str, repo_root: Path) -> str | None
```

## 12.2 Rules

```text
only one active writer may update a run at a time
repeated requests with the same idempotency_key must not start duplicate mutating runs
resume must load persisted session, state, plan, steps, and ledger
resume must not re-run completed side-effecting steps
resume may re-run safe read-only or validation steps only if policy allows
stale lock handling must be conservative and evidenced
```

## 12.3 Acceptance

```text
second active run with same lock blocks
same idempotency key returns existing run or blocks duplicate execution
resume from PLAN_READY does not recreate conflicting plan
resume from STEP_FAILED routes to recovery or final NOT DONE
```

---

# 13. Session Lifecycle

Implement in:

```text
tools/agentx_evolve/orchestrator/session_manager.py
```

Required public functions:

```python
create_orchestration_session(task: OrchestrationTask, context: dict, repo_root: Path) -> OrchestrationSession
load_orchestration_session(run_id: str, repo_root: Path) -> OrchestrationSession
update_orchestration_session(session: OrchestrationSession, updates: dict, repo_root: Path) -> OrchestrationSession
close_orchestration_session(session: OrchestrationSession, final_status: str, repo_root: Path) -> OrchestrationSession
resume_orchestration_session(run_id: str, repo_root: Path) -> OrchestrationSession
```

Required lifecycle:

```text
1. create session
2. validate requested task
3. compute or accept idempotency key
4. assign run_id and session_id
5. acquire run lock
6. load policy context
7. bind prompt contract version if needed
8. bind model profile if needed
9. load tool registry snapshot
10. create initial state
11. write session artifact
12. write latest session artifact atomically
13. create run ledger shell
14. close session only after ledger and completion record are written
15. release run lock only after final state is written
```

Acceptance:

```text
session can be created deterministically
session IDs are unique
session artifact validates against schema
latest session artifact is written atomically
session cannot close as COMPLETED if required run ledger is missing
session can resume from persisted state
```

---

# 14. Task Decomposition Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/task_decomposer.py
```

Required public function:

```python
decompose_task(
    task: OrchestrationTask,
    session: OrchestrationSession,
    policy_context: dict,
    dependency_context: dict,
    repo_root: Path,
) -> TaskPlan
```

Required flow:

```text
1. validate task schema
2. classify task risk
3. identify required authorities
4. identify allowed tools
5. identify whether model calls are required
6. identify prompt contracts required
7. identify approval gates required
8. identify promotion gates required
9. create ordered task plan
10. write task_plan.json atomically
11. record evidence event
```

Required decomposition output:

```text
plan_id
session_id
run_id
task_id
ordered execution steps
required tools
required model profiles
required prompt contracts
required approvals
required promotion gates
assumptions
risks
warnings
errors
evidence_refs
```

Must not:

```text
call tools directly
call models directly
write source files
apply patches
execute commands
```

---

# 15. Execution Planning Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/execution_planner.py
```

Required public functions:

```python
build_execution_steps(plan: TaskPlan, session: OrchestrationSession, context: dict) -> list[ExecutionStep]
validate_execution_step(step: ExecutionStep, policy_context: dict) -> dict
order_execution_steps(steps: list[ExecutionStep]) -> list[ExecutionStep]
write_execution_steps(steps: list[ExecutionStep], repo_root: Path) -> list[dict]
```

Required rules:

```text
every step has exactly one assigned role
every tool step lists allowed tools
every model step lists allowed model profiles
every model step lists required prompt contracts
every source-affecting step requires governance
every promotion-affecting step requires promotion gate
every human-approval step must pause before execution
step order must be deterministic
```

Acceptance:

```text
steps are deterministic
steps validate against schema
invalid role blocks planning
unknown tool blocks planning or marks step BLOCKED
unknown model profile blocks planning or marks step BLOCKED
prompt-required model step without prompt contract blocks planning
```

---

# 16. Step Execution Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/step_executor.py
```

Required public function:

```python
execute_step(
    step: ExecutionStep,
    session: OrchestrationSession,
    context: dict,
    repo_root: Path,
) -> ExecutionStep
```

Required execution flow:

```text
1. validate step schema
2. confirm session is not terminal
3. confirm step is READY or PENDING
4. check policy for assigned role and step type
5. check approval gate if required
6. check governance gate if required
7. invoke tool only through tool_invoker.py
8. invoke model only through model_invoker.py
9. validate downstream result schema
10. route failures to recovery_manager.py
11. write step result evidence
12. update run ledger
13. update state snapshot
14. return updated step
```

Must not:

```text
call wrapper tools directly without Tool / MCP Adapter
call model runtime directly without Model Adapter
write source files directly
execute shell commands directly
apply patches directly
commit or push Git directly
```

---

# 17. Tool Invocation Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/tool_invoker.py
```

Required public function:

```python
invoke_tool_for_step(
    step: ExecutionStep,
    tool_name: str,
    arguments: dict,
    session: OrchestrationSession,
    policy_context: dict,
    dependency_context: dict,
    repo_root: Path,
) -> ToolInvocationBinding
```

Required integration:

```text
Tool / MCP Adapter must be the only tool execution path.
```

Required flow:

```text
1. validate step allows tool calls
2. validate tool_name is in step.allowed_tools
3. summarize and redact arguments for evidence
4. create ToolCall using assigned_role
5. attach session_id and run_id
6. call Tool / MCP Adapter execute_tool_call
7. receive ToolResult
8. validate ToolResult schema
9. map ToolResult status to step status
10. record tool_call_id and tool_result_id
11. write tool invocation binding
12. append evidence reference to step
```

Blocked conditions:

```text
tool not listed in step.allowed_tools
Tool / MCP Adapter unavailable
ToolResult status is BLOCKED
ToolResult status is INVALID
ToolResult schema invalid
mutating tool requested without governance/session authority
```

Acceptance:

```text
orchestrator never calls tool wrappers directly
tool invocation creates binding artifact
tool BLOCKED result blocks or pauses step
tool INVALID result routes to failure taxonomy
```

---

# 18. Model Invocation Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/model_invoker.py
```

Required public function:

```python
invoke_model_for_step(
    step: ExecutionStep,
    prompt_binding: PromptBinding,
    session: OrchestrationSession,
    policy_context: dict,
    dependency_context: dict,
    repo_root: Path,
) -> ModelInvocationBinding
```

Required integration:

```text
Model Adapter must be the only model execution path.
Prompt Contract / Prompt Versioning must supply the prompt contract.
Context Builder / Task Packer must supply input context if available.
```

Required flow:

```text
1. validate step allows model calls
2. validate selected model_profile_id is allowed for the step
3. validate prompt_contract_version is approved
4. validate prompt input contract
5. build context through Context Builder if available
6. call Model Adapter
7. validate model output contract
8. write model invocation binding
9. append evidence reference to step
10. return binding
```

Blocked conditions:

```text
model profile not allowed
prompt contract missing
prompt version not approved
prompt input contract invalid
model adapter unavailable
hosted model requested in local-only mode
model output schema invalid
model output contains direct mutation instruction without approved patch path
```

Acceptance:

```text
orchestrator never calls LLM client directly
model call uses Model Adapter
prompt contract is recorded
model output evidence is recorded
invalid output blocks downstream mutation
```

---

# 19. Prompt Binding Flow

Prompt binding may be implemented inside `model_invoker.py` or as helper functions in the same module.

Required public function:

```python
create_prompt_binding_for_step(
    step: ExecutionStep,
    session: OrchestrationSession,
    prompt_context: dict,
    repo_root: Path,
) -> PromptBinding
```

Required rules:

```text
every model step must have a prompt binding
prompt contract version must be explicit
prompt input schema must be validated before model call
prompt output schema must be validated after model call
prompt provenance or hash must be recorded
raw prompt payloads must not be durably logged unless explicitly redacted/summarized
```

Acceptance:

```text
model step without prompt binding blocks
prompt binding artifact is written
prompt binding validates against schema
prompt version mismatch blocks model call
```

---

# 20. Approval Gate Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/approval_gate.py
```

Required public functions:

```python
check_approval_required(step: ExecutionStep, session: OrchestrationSession, policy_context: dict) -> ApprovalGateRecord | None
create_approval_gate_record(step: ExecutionStep, session: OrchestrationSession, reason: str, repo_root: Path) -> ApprovalGateRecord
resolve_approval_gate(record: ApprovalGateRecord, approval_context: dict, repo_root: Path) -> ApprovalGateRecord
```

Required rules:

```text
source mutation requires governance and may require human approval
Git write requires future approval and promotion authority
promotion requires promotion gate
high-risk model output cannot proceed to mutation without approval
missing approval pauses, not bypasses
approval records must be evidenced
approval cannot override non-overridable policy/sandbox blocks
```

Acceptance:

```text
approval-required step pauses
missing approval cannot be treated as allow
approval record validates against schema
resolved approval records are written to JSONL
```

---

# 21. Promotion Gate Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/promotion_gate.py
```

Required public functions:

```python
check_promotion_ready(session: OrchestrationSession, ledger: RunLedger, repo_root: Path) -> PromotionGateRecord
create_promotion_gate_record(session: OrchestrationSession, ledger: RunLedger, repo_root: Path) -> PromotionGateRecord
request_promotion_decision(record: PromotionGateRecord, dependency_context: dict, repo_root: Path) -> PromotionGateRecord
```

Required rules:

```text
promotion cannot occur unless validation passed
promotion cannot occur unless review evidence exists
promotion cannot occur with unresolved blockers
promotion cannot occur from dirty source state unless approved by Git layer and promotion gate
orchestrator must not promote directly
orchestrator may only request promotion through Promotion / Release Gate
```

Acceptance:

```text
promotion gate blocks missing validation
promotion gate blocks missing review
promotion gate blocks unresolved blockers
promotion gate record validates against schema
orchestrator does not directly promote
```

---

# 22. Failure Recovery Flow

Implement in:

```text
tools/agentx_evolve/orchestrator/recovery_manager.py
```

Required public functions:

```python
classify_step_failure(step: ExecutionStep, result: dict, context: dict) -> str
choose_recovery_action(failure_class: str, step: ExecutionStep, context: dict) -> RecoveryAction
apply_recovery_action(action: RecoveryAction, session: OrchestrationSession, repo_root: Path) -> RecoveryAction
```

Required integration:

```text
Failure Taxonomy / Recovery Playbook is authoritative when available.
```

Restrictive fallback if failure layer is unavailable:

```text
schema invalid -> abort step
policy denied -> block step
sandbox denied -> block step
tool invalid -> block step
model output invalid -> block step
approval missing -> pause step
unknown failure -> fail step; no automatic retry unless retry is explicitly safe
```

Recovery rules:

```text
retry count must be bounded
no retry may bypass policy
no retry may bypass sandbox
no retry may lower safety requirements
no recovery action may mutate source directly
rollback must go through Governed Patch Execution
unknown failure defaults to NOT DONE, not silent success
```

Acceptance:

```text
known failure class maps to recovery action
unknown failure fails closed
retry count is enforced
recovery action is evidenced
```

---

# 23. Evidence Logger

Implement in:

```text
tools/agentx_evolve/orchestrator/orchestrator_logger.py
```

Required public functions:

```python
append_orchestrator_event(event: OrchestratorEvidenceEvent, repo_root: Path) -> dict
append_execution_step(step: ExecutionStep, repo_root: Path) -> dict
append_tool_invocation(binding: ToolInvocationBinding, repo_root: Path) -> dict
append_model_invocation(binding: ModelInvocationBinding, repo_root: Path) -> dict
append_prompt_binding(binding: PromptBinding, repo_root: Path) -> dict
append_approval_gate(record: ApprovalGateRecord, repo_root: Path) -> dict
append_promotion_gate(record: PromotionGateRecord, repo_root: Path) -> dict
append_recovery_action(action: RecoveryAction, repo_root: Path) -> dict
write_latest_session(session: OrchestrationSession, repo_root: Path) -> dict
write_latest_state(state: OrchestrationState, repo_root: Path) -> dict
write_latest_ledger(ledger: RunLedger, repo_root: Path) -> dict
```

Rules:

```text
append-only JSONL for histories
atomic writes for latest artifacts
redact secrets and raw prompt payloads
truncate large outputs or record artifact references
never write outside .agentx-init/orchestrator/ unless deviation is recorded
```

---

# 24. Run Ledger

Implement in:

```text
tools/agentx_evolve/orchestrator/run_ledger.py
```

Required public functions:

```python
create_run_ledger(session: OrchestrationSession, task: OrchestrationTask, repo_root: Path) -> RunLedger
update_run_ledger(ledger: RunLedger, update: dict, repo_root: Path) -> RunLedger
finalize_run_ledger(ledger: RunLedger, final_decision: str, repo_root: Path) -> RunLedger
load_run_ledger(run_id: str, repo_root: Path) -> RunLedger
```

Rules:

```text
ledger must summarize every step
ledger must link tool, model, prompt, approval, promotion, and recovery evidence
ledger final_decision must be DONE only when all required gates pass
ledger final_decision must be NOT DONE when dependencies are missing, steps block, validation fails, or promotion blocks
```

---

# 25. Evidence Manifest and Review Report

Implement in:

```text
tools/agentx_evolve/orchestrator/evidence_manifest.py
```

Required public functions:

```python
create_orchestrator_evidence_manifest(run_id: str, repo_root: Path, command_records: list[dict]) -> OrchestratorEvidenceManifest
write_orchestrator_review_report(run_id: str, repo_root: Path, review_context: dict) -> dict
write_orchestrator_completion_record(run_id: str, repo_root: Path, completion_context: dict) -> OrchestratorCompletionRecord
```

Required files:

```text
.agentx-init/orchestrator/runs/<run_id>/orchestrator_evidence_manifest.json
.agentx-init/orchestrator/runs/<run_id>/orchestrator_review_report.json
.agentx-init/orchestrator/runs/<run_id>/orchestrator_completion_record.json
```

Required hashing:

```text
SHA-256 hashes are required for final evidence manifest, review report, completion record, run ledger, and important JSONL evidence files.
Use Python standard library hashlib.
DONE is invalid if required hashes are missing.
```

Evidence immutability rule:

```text
After final DONE or NOT DONE is recorded, final evidence files must not be modified without creating a new review report.
Changed evidence hashes invalidate the previous final verdict.
```

---

# 26. Integration Requirements

## 26.1 Tool / MCP Adapter Integration

Required:

```text
all tool calls go through execute_tool_call
ToolCall includes session_id and run_id
ToolResult is validated before step continues
ToolResult evidence_refs are attached to step evidence
BLOCKED and INVALID results stop or pause step
```

Forbidden:

```text
calling tool wrapper modules directly from orchestrator
raw subprocess calls
raw file writes for source mutation
raw Git commands
```

## 26.2 Policy / Capability Registry Integration

Required:

```text
orchestration task checked before planning
execution step checked before execution
tool invocation checked before tool call
model invocation checked before model call
approval and promotion requirements derived from policy
policy-denied result blocks or pauses orchestration
```

Fallback:

```text
if policy layer is unavailable, orchestrator runs in restricted mode
restricted mode allows planning and read-only evidence only
restricted mode blocks mutation, patch, Git write, network, and promotion
```

## 26.3 Security Sandbox Integration

Required:

```text
orchestrator must rely on Tool / MCP Adapter and Security Sandbox for file/path/command operations
orchestrator may only write its own runtime artifacts under .agentx-init/orchestrator/
orchestrator must not perform direct source writes
```

## 26.4 Governed Patch Execution Integration

Required:

```text
orchestrator may request patch precheck
orchestrator may request patch apply only through governed patch layer
orchestrator may request rollback only through governed patch layer
orchestrator cannot apply patches itself
patch result evidence must be attached to run ledger
```

## 26.5 Model Adapter Integration

Required:

```text
all model calls go through Model Adapter
model profile must be policy-approved
hosted/local mode must obey policy
model output contract must be validated
model output cannot directly mutate source
```

## 26.6 Prompt Contract / Prompt Versioning Integration

Required:

```text
every model step must bind a prompt contract version
prompt input contract must validate before model call
prompt output contract must validate after model call
prompt provenance must be recorded
prompt migration/diff rules must be obeyed where applicable
```

## 26.7 Human Review / Approval Interface Integration

Required:

```text
human approval must be represented as gate records
missing approval pauses or blocks
approval cannot override non-overridable policy/sandbox blocks
approval evidence must be linked in ledger
```

## 26.8 Promotion / Release Gate Integration

Required:

```text
orchestrator may request promotion readiness check
orchestrator cannot promote directly
promotion requires validation evidence
promotion requires review evidence
promotion requires no unresolved blockers
promotion decision must be recorded
```

---

# 27. File-by-File Implementation Details

## 27.1 `__init__.py`

Expose public orchestrator API:

```python
from .orchestrator_models import *
from .session_manager import create_orchestration_session, load_orchestration_session, resume_orchestration_session
from .task_decomposer import decompose_task
from .execution_planner import build_execution_steps
from .step_executor import execute_step
from .orchestrator_dispatcher import run_orchestration
```

Must not:

```text
start a run on import
write files on import
load model clients on import
load MCP server on import
```

## 27.2 `orchestrator_dispatcher.py`

Required public functions:

```python
run_orchestration(task: OrchestrationTask, context: dict, repo_root: Path) -> RunLedger
resume_orchestration(run_id: str, context: dict, repo_root: Path) -> RunLedger
```

Required full flow:

```text
1. resolve dependency bindings
2. create or resume session
3. validate task
4. acquire run lock
5. transition CREATED -> PLANNING if new run
6. decompose task
7. build execution steps
8. transition PLANNING -> PLAN_READY
9. check approval requirements
10. execute steps in order
11. route blocked/failed steps
12. run validation step if applicable
13. check promotion gate if applicable
14. write run ledger
15. write evidence manifest
16. write review report
17. write completion record
18. close session
19. release run lock
20. return RunLedger
```

Must fail closed if any required adapter is unavailable.

---

# 28. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/orchestrator/__init__.py
2. tools/agentx_evolve/orchestrator/orchestrator_models.py
3. schema files
4. tools/agentx_evolve/orchestrator/orchestrator_logger.py
5. tools/agentx_evolve/orchestrator/orchestrator_locks.py
6. tools/agentx_evolve/orchestrator/dependency_bindings.py
7. tools/agentx_evolve/orchestrator/orchestrator_state.py
8. tools/agentx_evolve/orchestrator/session_manager.py
9. tools/agentx_evolve/orchestrator/task_decomposer.py
10. tools/agentx_evolve/orchestrator/execution_planner.py
11. tools/agentx_evolve/orchestrator/tool_invoker.py
12. tools/agentx_evolve/orchestrator/model_invoker.py
13. tools/agentx_evolve/orchestrator/approval_gate.py
14. tools/agentx_evolve/orchestrator/promotion_gate.py
15. tools/agentx_evolve/orchestrator/recovery_manager.py
16. tools/agentx_evolve/orchestrator/step_executor.py
17. tools/agentx_evolve/orchestrator/run_ledger.py
18. tools/agentx_evolve/orchestrator/evidence_manifest.py
19. tools/agentx_evolve/orchestrator/orchestrator_dispatcher.py
20. tests
21. schema validation utility
22. validation run
```

Rationale:

```text
models first
schemas second
logger before state/session writes
locks before sessions
bindings before invokers
state before sessions
sessions before planning
planning before execution
invokers before executor
approval/recovery before dispatcher
ledger and evidence manifest after execution surfaces exist
dispatcher last
```

---

# 29. Required Test Cases

## 29.1 Model and Schema Tests

```text
test_orchestration_session_instantiates
test_orchestration_state_instantiates
test_orchestration_task_instantiates
test_task_plan_instantiates
test_execution_step_instantiates
test_tool_invocation_binding_instantiates
test_model_invocation_binding_instantiates
test_prompt_binding_instantiates
test_approval_gate_record_instantiates
test_promotion_gate_record_instantiates
test_recovery_action_instantiates
test_orchestrator_evidence_event_instantiates
test_run_ledger_instantiates
test_evidence_manifest_instantiates
test_completion_record_instantiates
test_orchestrator_schemas_accept_valid_examples
test_orchestrator_schemas_reject_missing_required_fields
test_orchestrator_schemas_reject_invalid_enums
test_orchestrator_schemas_reject_invalid_hashes
```

## 29.2 Dependency Binding Tests

```text
test_real_dependency_binding_loads_when_available
test_missing_tool_adapter_blocks_tool_steps
test_missing_policy_enters_restricted_mode
test_fake_test_adapter_is_explicit_only
test_fake_adapter_never_executes_shell_or_network
test_restricted_mode_blocks_mutation_patch_git_network_promotion
```

## 29.3 State Machine Tests

```text
test_created_can_transition_to_planning
test_planning_can_transition_to_plan_ready
test_running_can_transition_to_validating
test_terminal_state_cannot_transition
test_invalid_transition_blocks_and_writes_evidence
test_state_version_increments
test_stale_state_update_fails_closed
```

## 29.4 Locking and Resume Tests

```text
test_acquire_run_lock_writes_lock_artifact
test_second_active_writer_blocks
test_same_idempotency_key_does_not_duplicate_run
test_resume_loads_existing_state_plan_steps_and_ledger
test_resume_does_not_rerun_completed_side_effecting_step
```

## 29.5 Session Lifecycle Tests

```text
test_create_orchestration_session_writes_session_artifact
test_create_orchestration_session_writes_latest_session_atomically
test_session_cannot_complete_without_ledger
test_close_session_writes_final_status
test_resume_orchestration_session_loads_state
```

## 29.6 Task Decomposition and Planning Tests

```text
test_decompose_task_creates_task_plan
test_decompose_high_risk_task_requires_approval
test_decompose_source_mutation_task_requires_governance
test_execution_planner_builds_ordered_steps
test_execution_planner_blocks_unknown_role
test_execution_planner_blocks_unknown_tool
test_model_step_requires_prompt_contract
```

## 29.7 Tool Invocation Tests

```text
test_tool_invoker_uses_tool_adapter_execute_tool_call
test_tool_invoker_rejects_tool_not_allowed_for_step
test_tool_invoker_blocks_invalid_tool_result_schema
test_tool_invoker_records_tool_invocation_binding
test_tool_blocked_result_blocks_step
test_tool_invoker_never_calls_wrapper_module_directly
```

## 29.8 Model Invocation Tests

```text
test_model_invoker_uses_model_adapter
test_model_invoker_requires_prompt_contract
test_model_invoker_blocks_unapproved_model_profile
test_model_invoker_blocks_invalid_prompt_output
test_model_invoker_records_model_invocation_binding
test_model_invoker_never_calls_llm_client_directly
```

## 29.9 Approval and Promotion Gate Tests

```text
test_approval_required_step_pauses
test_missing_approval_does_not_allow_execution
test_approval_record_written
test_approval_cannot_override_policy_block
test_promotion_gate_blocks_missing_validation
test_promotion_gate_blocks_missing_review
test_promotion_gate_blocks_unresolved_blockers
test_orchestrator_does_not_promote_directly
```

## 29.10 Recovery Tests

```text
test_known_failure_maps_to_recovery_action
test_unknown_failure_fails_closed
test_retry_count_is_bounded
test_recovery_does_not_bypass_policy
test_recovery_does_not_bypass_sandbox
test_recovery_action_written
```

## 29.11 Evidence Tests

```text
test_orchestrator_event_written
test_latest_state_written_atomically
test_run_ledger_written
test_evidence_manifest_written
test_review_report_written
test_completion_record_written
test_final_evidence_hashes_written
test_secret_and_raw_prompt_redaction
```

## 29.12 Dispatcher Tests

```text
test_run_orchestration_creates_session_plan_steps_and_ledger
test_run_orchestration_blocks_when_policy_unavailable_for_mutation
test_run_orchestration_blocks_when_tool_adapter_unavailable
test_run_orchestration_blocks_when_model_adapter_unavailable_for_model_step
test_run_orchestration_writes_completion_record
test_run_orchestration_returns_not_done_when_dependency_blocks
test_run_orchestration_releases_lock_on_failure
```

## 29.13 Negative Tests

```text
test_orchestrator_does_not_write_source_directly
test_orchestrator_does_not_execute_raw_shell
test_orchestrator_does_not_call_git_directly
test_orchestrator_does_not_call_model_client_directly
test_orchestrator_does_not_bypass_tool_adapter
test_orchestrator_does_not_bypass_policy_for_mutation
test_orchestrator_does_not_bypass_human_approval
test_orchestrator_does_not_bypass_promotion_gate
test_orchestrator_invalid_state_transition_fails_closed
test_orchestrator_unknown_failure_has_no_unbounded_retry
test_orchestrator_does_not_log_raw_prompt_payload
test_orchestrator_does_not_mark_done_when_required_dependency_missing
```

---

# 30. Acceptance Criteria

The implementation is acceptable only if:

```text
all target files exist
all schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
session lifecycle works
state machine rejects invalid transitions
run locking prevents duplicate active writers
idempotency prevents duplicate mutating runs
resume works from persisted state
dependency binding supports REAL, FAKE_FOR_TEST, RESTRICTED, and UNAVAILABLE modes
task decomposition produces schema-valid plans
execution planning produces schema-valid steps
tool invocation goes only through Tool / MCP Adapter
model invocation goes only through Model Adapter
prompt contract is required for model steps
approval gates pause or block when approval is missing
promotion gate blocks without validation and review evidence
failure recovery is bounded and fail-closed
runtime evidence is written under .agentx-init/orchestrator/
run ledger is written
evidence manifest is written
review report is written
completion record is written
final evidence hashes are written
no direct source mutation occurs
no raw shell is executed
no direct Git write occurs
no direct model client is called
```

---

# 31. Manual Validation Commands

Run from repository root:

```bash
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_orchestrator_schemas.py
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_orchestrator_models.py \
  tools/agentx_evolve/tests/test_orchestrator_state.py \
  tools/agentx_evolve/tests/test_orchestrator_session_manager.py \
  tools/agentx_evolve/tests/test_task_decomposer.py \
  tools/agentx_evolve/tests/test_execution_planner.py \
  tools/agentx_evolve/tests/test_step_executor.py \
  tools/agentx_evolve/tests/test_tool_invoker.py \
  tools/agentx_evolve/tests/test_model_invoker.py \
  tools/agentx_evolve/tests/test_approval_gate.py \
  tools/agentx_evolve/tests/test_promotion_gate.py \
  tools/agentx_evolve/tests/test_recovery_manager.py \
  tools/agentx_evolve/tests/test_orchestrator_logger.py \
  tools/agentx_evolve/tests/test_run_ledger.py \
  tools/agentx_evolve/tests/test_orchestrator_dispatcher.py \
  tools/agentx_evolve/tests/test_orchestrator_dependency_bindings.py \
  tools/agentx_evolve/tests/test_orchestrator_locks.py \
  tools/agentx_evolve/tests/test_orchestrator_evidence_manifest.py \
  tools/agentx_evolve/tests/test_orchestrator_schema_validation.py \
  tools/agentx_evolve/tests/test_orchestrator_negative_cases.py
git status --short
```

Required result:

```text
initial git status CLEAN or expected runtime artifacts only
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
scoped orchestrator pytest PASS, exit_code 0
final git status CLEAN or only expected runtime artifacts
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
manual human input
```

---

# 32. Completion Evidence

After implementation, write:

```text
.agentx-init/orchestrator/runs/<run_id>/orchestrator_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestrator_completion_record.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "component_name": "Self-Evolution Orchestrator",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/orchestrator/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/orchestrator/",
  "basis_documents": [
    "SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "integration_verified": {
    "tool_mcp_adapter": false,
    "policy_capability_registry": false,
    "security_sandbox": false,
    "governed_patch_execution": false,
    "model_adapter": false,
    "prompt_contract_versioning": false,
    "human_review_approval": false,
    "promotion_release_gate": false
  },
  "negative_tests_verified": [],
  "runtime_artifacts_generated": [],
  "evidence_manifest_path": ".agentx-init/orchestrator/runs/<run_id>/orchestrator_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/orchestrator/runs/<run_id>/orchestrator_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 33. Implementation Drift Blockers

Reject the implementation if it:

```text
places orchestrator files outside tools/agentx_evolve/orchestrator/ without recorded deviation
writes runtime artifacts outside .agentx-init/orchestrator/ without recorded deviation
executes raw shell
calls Git directly
calls model clients directly
calls tool wrappers directly instead of Tool / MCP Adapter
writes source files directly
applies patches directly
bypasses Policy / Capability Registry
bypasses Security Sandbox for path/file/command operations
bypasses Prompt Contract for model calls
bypasses Human Review / Approval for approval-required steps
bypasses Promotion / Release Gate
performs unbounded retry
continues after schema-invalid model output
continues after BLOCKED tool result without recovery evidence
logs secrets or raw prompt payloads durably
marks DONE when required dependencies are missing
adds OpenCode/Bun/Node runtime dependency
requires network, hosted model, or running MCP server for tests
```

---

# 34. Conditional Implementation Rules

Some dependent layers may not be fully implemented. The orchestrator may still be implemented in restricted mode.

## 34.1 Allowed Restricted Mode Behavior

```text
create sessions
validate schemas
build task plans
build execution steps
write evidence
use read-only tool calls if Tool / MCP Adapter permits them
simulate model calls with explicit fake model adapter in tests
pause on missing approvals
block promotion
produce NOT DONE ledger when dependencies are missing
```

## 34.2 Blocked in Restricted Mode

```text
source mutation
patch application
rollback
Git write
network call
hosted model call
promotion
approval override
policy override
sandbox override
```

## 34.3 Restricted Mode DONE Rule

Restricted mode may pass unit tests for the orchestrator package, but it cannot produce a final implementation `DONE` verdict for a full self-evolution run that requires missing dependencies.

A restricted-mode run must end as:

```text
NOT DONE
BLOCKED
DEFERRED SAFELY
```

not as:

```text
DONE
```

---

# 35. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and files | 1.0 | All package files, schemas, tests, and runtime artifact paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full and scoped test suites pass with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass for every orchestrator schema. |
| State/session/locking | 1.0 | State machine, session lifecycle, locks, idempotency, and resume pass. |
| Planning/execution | 1.0 | Task decomposition, step planning, dispatcher flow, and ledgers pass. |
| Adapter boundaries | 1.0 | Tool, model, prompt, policy, approval, promotion, and patch integrations do not bypass authority. |
| Failure recovery | 1.0 | Failure taxonomy, bounded retry, blocked/invalid paths, and NOT DONE behavior pass. |
| Evidence/audit | 1.0 | JSONL evidence, latest artifacts, manifest, review report, hashes, redaction, completion record pass. |
| Safety negative tests | 1.0 | No direct source mutation, raw shell, Git, model client, approval bypass, promotion bypass, or unbounded retry. |

Hard caps:

```text
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
missing state/session tests caps score at 7.0
missing adapter-boundary tests caps score at 7.0
direct source mutation caps score at 4.0
raw shell execution caps score at 4.0
direct model client call caps score at 4.0
direct Git mutation caps score at 4.0
approval or promotion bypass caps score at 4.0
unbounded retry caps score at 5.0
missing evidence manifest caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing evidence hashes caps score at 8.0
any required command NOT RUN caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

---

# 36. Definition of Done

The Self-Evolution Orchestrator is done when:

```text
all target package files exist
all schema files exist
all test files exist
orchestration dataclasses instantiate
schemas validate valid examples
schemas reject invalid examples
state machine enforces allowed transitions
state versioning prevents stale updates
run locking prevents duplicate active writers
idempotency prevents duplicate mutating runs
resume works from persisted state
session lifecycle writes valid artifacts
task decomposition produces valid task plans
execution planning produces valid steps
tool invocation uses Tool / MCP Adapter only
model invocation uses Model Adapter only
prompt contract binding is required for model steps
approval gate blocks or pauses missing approval
promotion gate blocks missing validation/review evidence
failure recovery is bounded and fail-closed
run ledger is written
evidence manifest is written
review report is written
completion record is written
final evidence hashes are written
runtime evidence is written under .agentx-init/orchestrator/
compileall passes
pytest passes
schema validation passes
no direct source mutation occurs
no raw shell is executed
no direct Git operation occurs
no direct model client call occurs
no approval or promotion gate is bypassed
restricted-mode runs cannot claim DONE for missing required dependencies
```

Command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_orchestrator_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 37. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/orchestrator/ package.
2. Create orchestrator_models.py with all dataclasses and helpers.
3. Create orchestrator schemas.
4. Create orchestrator_logger.py.
5. Create orchestrator_locks.py.
6. Create dependency_bindings.py.
7. Create orchestrator_state.py.
8. Create session_manager.py.
9. Create task_decomposer.py.
10. Create execution_planner.py.
11. Create tool_invoker.py.
12. Create model_invoker.py and prompt binding helpers.
13. Create approval_gate.py.
14. Create promotion_gate.py.
15. Create recovery_manager.py.
16. Create step_executor.py.
17. Create run_ledger.py.
18. Create evidence_manifest.py.
19. Create orchestrator_dispatcher.py.
20. Create tests.
21. Create validate_orchestrator_schemas.py.
22. Run compileall.
23. Run pytest.
24. Run schema validation utility.
25. Verify git status.
26. Write evidence manifest, review report, and completion record.
```

Do not reorder unless real import dependencies require it.

---

# 38. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The orchestrator package must live under tools/agentx_evolve/orchestrator/.
[ ] Runtime artifacts must go under .agentx-init/orchestrator/.
[ ] The orchestrator coordinates; it does not directly mutate source.
[ ] Tool calls must go through Tool / MCP Adapter.
[ ] Model calls must go through Model Adapter.
[ ] Prompt contracts must be bound for model calls.
[ ] Policy / Capability Registry is authoritative for permissions.
[ ] Security Sandbox is authoritative for file/path/command operations.
[ ] Governed Patch Execution is authoritative for patch apply and rollback.
[ ] Human Review / Approval is authoritative for approval-required steps.
[ ] Promotion / Release Gate is authoritative for promotion.
[ ] Missing dependencies force restricted mode or BLOCKED / NOT DONE results.
[ ] Fake adapters are allowed only as explicit test fixtures.
[ ] Evidence manifest, review report, completion record, and hashes are required.
[ ] Tests must run without GPU, network, hosted model, LLM, Bun, Node, OpenCode runtime, running MCP server, or manual human input.
```

---

# 39. Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Package files | All orchestrator files exist under `tools/agentx_evolve/orchestrator/`. |
| Schemas | All orchestrator schemas exist and validate valid/invalid examples. |
| Tests | All required test files exist and pass. |
| State machine | Valid transitions pass; invalid transitions fail closed. |
| Sessions | Create, update, close, and resume work with evidence. |
| Locking | Duplicate active writers block. |
| Idempotency | Duplicate mutating run requests do not start conflicting runs. |
| Planning | Task plan and execution steps are deterministic and schema-valid. |
| Tool calls | Only through Tool / MCP Adapter. |
| Model calls | Only through Model Adapter with prompt contract binding. |
| Approval | Missing approval pauses or blocks. |
| Promotion | Missing validation/review/blocker clearance blocks. |
| Recovery | Bounded, evidenced, fail-closed. |
| Evidence | JSONL histories, latest artifacts, ledger, manifest, report, completion record, hashes. |
| Safety | No source mutation, raw shell, direct Git, direct model client, approval bypass, or promotion bypass. |
| Validation | compileall, pytest, schema validation, and git status pass. |

---

# 40. v3 Review and Upgrade Summary

## 40.1 v2 Rating

The v2 implementation spec was very strong and close to final. On stricter review, I would rate it:

```text
9.8/10
```

It already covered exact subdirectories, files, schemas, dataclasses, runtime artifacts, state machine, sessions, task decomposition, step execution, tool/model invocation, approval, promotion, recovery, dependency modes, evidence, hashes, validation commands, scoring caps, and Definition of Done.

## 40.2 Why v2 Was Not Fully 10/10

The remaining gaps were not broad structural gaps. They were final production-control details that matter for a self-evolution coordinator:

```text
1. It did not explicitly define orchestrator run modes such as PLAN_ONLY, DRY_RUN, EXECUTE_CONTROLLED, RESUME, VALIDATE_ONLY, and REVIEW_ONLY.
2. It did not define task/step dependency graph validation, cycle rejection, and dependency-ready checks.
3. It did not define source snapshot / repository state preconditions to prevent time-of-check/time-of-use drift.
4. It did not define per-run and per-step budgets for time, retries, model calls, tool calls, and evidence size.
5. It did not define cancellation / abort semantics strongly enough.
6. It did not define prompt-injection and model-output quarantine rules for proposed tool calls or patch requests.
7. It did not require authority rechecks immediately before every delegated side-effecting step.
8. It did not define step input/output artifact hashing and provenance propagation.
9. It did not define deterministic replay / dry-run replay expectations.
10. It did not define explicit stale-plan invalidation when policy, prompt contract, model profile, tool registry, source snapshot, or dependency mode changes after planning.
```

## 40.3 v3 Improvements

This v3 adds:

```text
orchestrator run modes
dependency graph validation
source snapshot and TOCTOU protections
per-run and per-step budgets
cancellation and abort semantics
prompt-injection and model-output quarantine
pre-execution authority rechecks
artifact hashing and provenance propagation
deterministic replay expectations
stale-plan invalidation rules
```

---

# 41. Orchestrator Run Modes

The orchestrator must support explicit run modes. Run mode must be recorded in `OrchestrationSession.orchestration_mode`, the run ledger, and evidence manifest.

Allowed run modes:

```text
PLAN_ONLY
DRY_RUN
EXECUTE_CONTROLLED
RESUME
VALIDATE_ONLY
REVIEW_ONLY
```

## 41.1 Run Mode Meanings

| Run mode | Meaning | Side effects allowed? | Final DONE allowed? |
|---|---|---|---|
| `PLAN_ONLY` | Create session, plan, steps, and evidence only. | Orchestrator runtime artifacts only. | No, unless task explicitly only requested a plan. |
| `DRY_RUN` | Validate authorities, bindings, tools, prompts, models, and gates without executing mutation. | Orchestrator runtime artifacts only. | No for mutating self-evolution tasks. |
| `EXECUTE_CONTROLLED` | Execute approved steps through delegated adapters only. | Only delegated, governed, evidenced effects. | Yes, if all gates pass. |
| `RESUME` | Resume existing run from persisted state. | Only incomplete safe steps; no completed side-effecting re-run. | Yes, if original run mode allowed it. |
| `VALIDATE_ONLY` | Run validation/review checks through approved tool path. | Validation artifacts only. | No, unless validation was the requested task. |
| `REVIEW_ONLY` | Produce review/ledger/evidence reports. | Report/evidence artifacts only. | No, unless review was the requested task. |

## 41.2 Run Mode Rules

```text
run mode must be explicit
missing run mode defaults to PLAN_ONLY, not EXECUTE_CONTROLLED
EXECUTE_CONTROLLED requires policy approval and dependency readiness
DRY_RUN must not call mutating tools
PLAN_ONLY must not call model adapter unless explicitly policy-approved for planning
RESUME must verify original run mode before continuing
VALIDATE_ONLY must not mutate source
REVIEW_ONLY must not run implementation steps
```

Acceptance tests:

```text
test_missing_run_mode_defaults_to_plan_only
test_plan_only_does_not_execute_tools_or_models_without_policy
test_dry_run_does_not_mutate
test_execute_controlled_requires_policy_and_dependencies
test_resume_preserves_original_run_mode
test_validate_only_blocks_mutation
test_review_only_blocks_execution_steps
```

---

# 42. Step Dependency Graph and Cycle Rules

Execution steps must form a deterministic directed acyclic graph. Linear order is acceptable as a special case, but dependencies must still be explicit or derivable.

Add fields to `ExecutionStep`:

```python
depends_on_step_ids: list[str]
blocks_step_ids: list[str]
step_input_hashes: list[str]
step_output_hashes: list[str]
```

Required public functions in `execution_planner.py`:

```python
validate_step_dependency_graph(steps: list[ExecutionStep]) -> dict
find_ready_steps(steps: list[ExecutionStep], completed_step_ids: list[str]) -> list[ExecutionStep]
mark_downstream_blocked(steps: list[ExecutionStep], blocked_step_id: str, reason: str) -> list[ExecutionStep]
```

Rules:

```text
cycle in step graph blocks planning
missing dependency step ID blocks planning
step cannot run until all dependencies are completed
blocked dependency blocks downstream dependent steps
failed dependency routes downstream steps to BLOCKED unless recovery creates a replacement step
step order must be stable across repeated runs with the same inputs
```

Acceptance tests:

```text
test_step_dependency_graph_accepts_valid_dag
test_step_dependency_graph_rejects_cycle
test_step_dependency_graph_rejects_missing_dependency
test_step_waits_for_dependencies
test_blocked_dependency_blocks_downstream_steps
test_step_order_is_deterministic
```

---

# 43. Source Snapshot and TOCTOU Protection

The orchestrator must record the source and authority snapshot used during planning. Before executing a side-effecting or promotion-relevant step, the orchestrator must recheck whether the snapshot is still valid.

Add fields to `OrchestrationSession`:

```python
source_snapshot_id: str | None
source_snapshot_hash: str | None
policy_snapshot_id: str | None
tool_registry_hash: str | None
prompt_registry_hash: str | None
model_registry_hash: str | None
dependency_snapshot_hash: str | None
```

Required source snapshot data:

```text
reviewed_commit or current_commit when available
working_tree_status
tracked_file_hash_summary if available
tool registry hash
policy registry hash or policy decision context hash
prompt registry hash if model calls are used
model registry/profile hash if model calls are used
dependency mode snapshot
```

Rules:

```text
planning records snapshot hashes
side-effecting steps recheck snapshot immediately before execution
policy changes after planning invalidate affected steps
tool registry changes after planning invalidate tool steps
prompt contract changes after planning invalidate model steps
model profile changes after planning invalidate model steps
source changes after planning block source-affecting steps unless a new plan is produced
stale plan cannot proceed to mutation, promotion, or DONE
```

Acceptance tests:

```text
test_planning_records_source_and_authority_snapshot
test_policy_change_invalidates_mutating_step
test_tool_registry_change_invalidates_tool_step
test_prompt_contract_change_invalidates_model_step
test_source_snapshot_change_blocks_source_affecting_step
test_stale_plan_cannot_claim_done
```

---

# 44. Budgets, Limits, and Bounded Execution

The orchestrator must enforce bounded execution. No run, step, retry, model call, tool call, or evidence write may be unbounded.

Add fields to `OrchestrationTask` or session context:

```python
max_steps: int
max_retries_total: int
max_retries_per_step: int
max_tool_calls: int
max_model_calls: int
max_run_seconds: int
max_step_seconds: int
max_evidence_bytes: int
```

Default limits:

```text
max_steps = 50
max_retries_total = 3
max_retries_per_step = 1
max_tool_calls = 100
max_model_calls = 20
max_run_seconds = 1800
max_step_seconds = 300
max_evidence_bytes = 50MB
```

Rules:

```text
missing limits use restrictive defaults
exceeding run budget returns NOT DONE
exceeding step budget blocks or fails the step
exceeding retry budget fails closed
exceeding model/tool call budget stops execution
evidence size overflow writes summary and blocks further large evidence writes
budget events must be recorded in evidence
```

Acceptance tests:

```text
test_missing_budgets_use_restrictive_defaults
test_max_steps_enforced
test_max_retries_enforced
test_max_tool_calls_enforced
test_max_model_calls_enforced
test_step_timeout_blocks_step
test_evidence_budget_overflow_summarizes_and_blocks
```

---

# 45. Cancellation and Abort Semantics

The orchestrator must support safe cancellation and abort. Cancellation is a requested stop. Abort is a safety stop caused by policy, invalid state, corruption, unsafe dependency, or unrecoverable failure.

Required public functions in `orchestrator_dispatcher.py` or `session_manager.py`:

```python
request_cancel_run(run_id: str, reason: str, repo_root: Path) -> dict
check_cancel_requested(run_id: str, repo_root: Path) -> bool
abort_run(run_id: str, reason: str, repo_root: Path) -> RunLedger
```

Required artifact:

```text\.agentx-init/orchestrator/runs/<run_id>/cancel_requested.json
```

Rules:

```text
cancel request must be written atomically
active step must finish only if safe or stop at next checkpoint
no new side-effecting step may start after cancel is requested
abort must write final state ABORTED
abort must write ledger with final_decision NOT DONE
abort must release run lock after final evidence is written
abort must not delete evidence
```

Acceptance tests:

```text
test_cancel_request_written_atomically
test_cancel_prevents_new_side_effecting_steps
test_abort_writes_aborted_state_and_not_done_ledger
test_abort_releases_lock_after_final_evidence
test_abort_does_not_delete_prior_evidence
```

---

# 46. Prompt-Injection and Model-Output Quarantine

Model output must be treated as untrusted. The orchestrator must never execute tool calls, patch requests, shell commands, Git commands, or approval claims directly from model output.

Required model-output quarantine rules:

```text
model output may propose actions only as data
proposed tool calls must be converted into planned steps and rechecked by policy
proposed patch content must go through Governed Patch Execution
proposed command text must go through Tool / MCP Adapter command policy
model claim of human approval is ignored unless Human Review adapter confirms approval
model claim of promotion readiness is ignored unless Promotion Gate confirms readiness
model-supplied paths must be sandbox-checked before use
model-supplied prompt changes must go through Prompt Contract / Prompt Versioning
```

Add fields to `ModelInvocationBinding`:

```python
output_quarantined: bool
proposed_actions_ref: str | None
quarantine_reason: str | None
```

Acceptance tests:

```text
test_model_output_tool_call_is_quarantined
test_model_output_patch_request_is_not_applied_directly
test_model_output_shell_command_is_not_executed
test_model_claimed_approval_is_ignored
test_model_claimed_promotion_readiness_is_ignored
test_model_supplied_path_requires_sandbox_check
```

---

# 47. Pre-Execution Authority Recheck

The orchestrator must recheck authorities immediately before every step that can affect tools, models, files, patches, validation, approval, promotion, or final DONE.

Required function in `step_executor.py`:

```python
pre_execution_authority_recheck(
    step: ExecutionStep,
    session: OrchestrationSession,
    dependency_context: dict,
    policy_context: dict,
    repo_root: Path,
) -> dict
```

Recheck must verify:

```text
session is not terminal
run lock is still held
run has not been cancelled
step dependencies are complete
step is still allowed by policy
tool registry snapshot is still valid for tool steps
prompt/model registry snapshot is still valid for model steps
source snapshot is still valid for source-affecting steps
approval is still valid for approval-required steps
promotion gate is still valid for promotion steps
dependency modes have not degraded unsafely
```

Rules:

```text
failed recheck blocks the step
failed recheck must be evidenced
failed recheck cannot be overridden by model output
failed recheck cannot be overridden by stale approval
```

Acceptance tests:

```text
test_pre_execution_recheck_required_for_tool_step
test_pre_execution_recheck_blocks_if_lock_missing
test_pre_execution_recheck_blocks_if_cancel_requested
test_pre_execution_recheck_blocks_if_dependency_degraded
test_pre_execution_recheck_blocks_if_approval_stale
```

---

# 48. Artifact Provenance and Hash Propagation

Every important input and output artifact must have provenance. The run ledger must make it possible to trace from final decision back to task, plan, step, tool/model calls, approvals, validations, and evidence.

Add fields where applicable:

```python
input_artifact_hashes: list[dict]
output_artifact_hashes: list[dict]
provenance_refs: list[str]
source_snapshot_ref: str | None
```

Required hash fields for artifact entries:

```json
{
  "path": "<path>",
  "sha256": "<sha256>",
  "created_by": "<component>",
  "created_at": "<UTC timestamp>",
  "artifact_type": "<type>",
  "redaction_applied": true
}
```

Rules:

```text
final ledger references evidence manifest
final evidence manifest references ledger, report, completion record, and key JSONL histories
every step output used by a later step must carry hash/provenance
missing provenance blocks promotion and DONE
changed hashes after final verdict invalidate previous verdict
```

Acceptance tests:

```text
test_step_output_hash_propagates_to_downstream_input
test_run_ledger_links_all_step_evidence
test_missing_provenance_blocks_promotion
test_changed_hash_invalidates_previous_final_verdict
```

---

# 49. Deterministic Replay and Dry-Run Replay

The orchestrator must support deterministic replay of planning and dry-run behavior for the same task, context, policy snapshot, registry snapshots, and dependency modes.

Required public functions:

```python
replay_plan(run_id: str, repo_root: Path) -> TaskPlan
replay_dry_run(run_id: str, repo_root: Path) -> RunLedger
compare_replay_to_original(run_id: str, replay_artifact: dict, repo_root: Path) -> dict
```

Rules:

```text
replay must not mutate source
replay must not call hosted models
replay must not execute side-effecting tools
replay uses recorded snapshots
replay mismatch must be evidenced
replay mismatch blocks reproducibility claim
```

Acceptance tests:

```text
test_replay_plan_is_deterministic_for_same_snapshot
test_dry_run_replay_does_not_mutate
test_replay_mismatch_blocks_reproducibility_claim
```

---

# 50. Stale Plan Invalidation Rules

A plan becomes stale if any authority or input that affected planning changes before execution. A stale plan cannot continue to side-effecting execution or final DONE.

Stale conditions:

```text
policy snapshot changed
tool registry hash changed
prompt registry hash changed
model registry/profile hash changed
source snapshot changed
dependency mode changed from REAL to RESTRICTED or UNAVAILABLE
approval record expired or no longer applies
promotion gate criteria changed
run budget changed below already-consumed amount
```

Required behavior:

```text
stale plan detection writes evidence
stale plan transitions to STEP_BLOCKED or FAILED depending on context
stale plan may be replanned only if policy permits
stale plan cannot proceed to mutation
stale plan cannot claim DONE
```

Acceptance tests:

```text
test_policy_snapshot_change_marks_plan_stale
test_dependency_mode_degradation_marks_plan_stale
test_expired_approval_marks_plan_stale
test_stale_plan_blocks_mutation
test_stale_plan_cannot_claim_done
```

---

# 51. Updated Implementation Order Addendum

The implementation order in Section 28 still applies, with these additions:

```text
1. Add run mode constants to orchestrator_models.py before session_manager.py.
2. Add dependency graph fields to ExecutionStep before execution_planner.py tests.
3. Add source snapshot fields to OrchestrationSession before task_decomposer.py.
4. Add budget fields to OrchestrationTask before dispatcher tests.
5. Add cancellation functions before long dispatcher-flow tests.
6. Add model-output quarantine fields before model_invoker.py tests.
7. Add pre_execution_authority_recheck before step execution is allowed.
8. Add artifact provenance/hash propagation before evidence manifest and ledger finalization.
9. Add replay helpers after ledger/evidence manifest exist.
10. Add stale-plan invalidation before any EXECUTE_CONTROLLED path is accepted.
```

---

# 52. Updated Final Frozen Acceptance Matrix

| Area | Required result |
|---|---|
| Run modes | Explicit mode recorded; missing mode defaults to PLAN_ONLY. |
| Dependency graph | Steps form a valid DAG; cycles and missing dependencies block. |
| Source snapshot | Planning records source and authority snapshots; side-effecting steps recheck them. |
| Budgets | Run, step, retry, tool, model, and evidence limits enforced. |
| Cancellation | Cancel/abort writes evidence, prevents new side effects, and releases locks safely. |
| Model output quarantine | Model output cannot directly trigger tools, patches, shell, Git, approval, or promotion. |
| Authority recheck | Every side-effecting or gate-relevant step rechecks authority immediately before execution. |
| Artifact provenance | Step inputs/outputs, ledger, manifest, report, and completion record have hashes/provenance. |
| Replay | Planning and dry-run replay are deterministic for the same snapshots. |
| Stale plans | Changed authority/input snapshots invalidate affected steps and block DONE. |
| Base v2 requirements | All v2 files, schemas, tests, artifacts, state/session/locking/planning/execution/evidence requirements still apply. |

---

# 53. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It preserves the complete v2 implementation-ready structure and adds the remaining production controls needed for a self-evolution coordinator: explicit run modes, dependency graph validation, source snapshot and TOCTOU protections, bounded execution budgets, cancellation and abort semantics, prompt-injection/model-output quarantine, pre-execution authority rechecks, artifact provenance and hash propagation, deterministic replay, and stale-plan invalidation.
```
