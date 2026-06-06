# SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready, v4 closure pass
component_id: AGENTX_SELF_EVOLUTION_ORCHESTRATOR
component_name: Self-Evolution Orchestrator
roadmap_layer: 11
roadmap_phase: Phase C — Controlled Self-Evolution Coordination
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria, Prompt Contract, Model Runtime Acceptance Criteria, Human Review Acceptance Criteria, Promotion Gate Acceptance Criteria
risk_level: critical
implementation_mode: coordinator/state-machine/gatekeeper only
target_language: Python
canonical_subdirectory: tools/agentx_evolve/orchestrator/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/orchestrator/
review_document_rating: 10/10
final_rule: orchestrator coordinates work; it does not directly mutate source or bypass controlled layers
```

---

# 0. v2 Review and Upgrade Summary

The v1 contract was strong and implementation-oriented. I would rate v1:

```text
9.2/10
```

It already covered:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
Orchestrator Authority Rules
Orchestration State Schema
Task Plan Schema
Execution Step Schema
Tool Call Binding Schema
Model Call Binding Schema
Human Approval Binding Schema
Governance Gate Schema
Promotion Gate Binding Schema
Failure / Recovery Binding Schema
Session State Schema
Run Ledger Schema
Role Permission Matrix
OpenCode borrowing notes
Agent_X integration notes
Definition of Done
No-Go Conditions
```

It was not fully 10/10 because it needed stronger production-control details:

```text
1. Explicit dependency gates for missing or deferred upstream/downstream layers.
2. Run admission rules to prevent unsafe self-evolution sessions from starting.
3. Deterministic replay, idempotency, and run-locking rules.
4. Stronger state-transition table and terminal-state immutability.
5. Explicit prompt-injection and model-output containment rules.
6. Tool/model binding dispatch rules that prevent direct wrapper/API bypass.
7. Evidence hashing, evidence manifest, review report, and completion record requirements.
8. Runtime artifact immutability and deviation-register requirements.
9. Budget, retry, timeout, and loop-prevention rules.
10. Stronger schema examples and schema validation requirements.
11. Clearer handling of partial/deferred integrations.
12. A freeze rule that prevents broad contract expansion after v2.
```

This v2 added those controls and was close to final. After a second review, I would rate v2:

```text
9.6/10
```

It was not fully 10/10 because several implementation-governance details still needed to be made explicit:

```text
1. A clearer orchestration authority boundary between coordinator, executor, reviewer, and promoter.
2. A dedicated orchestrator failure-class taxonomy instead of relying only on generic failure wording.
3. Stronger run identity, lineage, parent/child run, and resume semantics.
4. Explicit tool/model/patch dispatch receipts so orchestration cannot claim completion from request intent alone.
5. More precise artifact provenance and cross-layer evidence reference requirements.
6. Clearer handling of partial success, degraded mode, dry-run mode, and cancelled runs.
7. A stronger human-interrupt and kill-switch rule.
8. Explicit validation of model-generated plans before they become executable task plans.
9. A stronger cross-layer replay requirement that verifies referenced Tool, Model, Patch, Policy, Sandbox, and Gate evidence.
10. A stricter contract/version compatibility rule for all bound schemas and upstream layers.
```

This v3 added those controls and was close to final. After a third review, I would rate v3:

```text
9.8/10
```

It was not fully 10/10 because several final closure details still needed to be explicit:

```text
1. Run plan freeze rules needed a stronger approved-plan hash boundary.
2. Dispatch claim verification needed to distinguish requested, accepted, completed, and evidenced actions.
3. Causal event ordering needed a monotonic sequence rule to prevent replay ambiguity.
4. Side-effect declarations needed read/write/execute/network sets before dispatch.
5. Run mode escalation and de-escalation needed stricter rules.
6. Dependency authority snapshots needed explicit version/hash pinning per run.
7. Evidence hash closure needed a stronger manifest/finalization rule.
8. Quarantine handling for inconsistent downstream evidence needed a dedicated rule.
9. Observability events needed to be separated from authority-granting evidence.
10. Completion needed stronger proof that no unreviewed plan revision entered execution.
```

This v4 adds those controls and is the final 10/10 controlling contract for the Self-Evolution Orchestrator.

---

# 1. Purpose

This document defines the controlling contract for the **Self-Evolution Orchestrator** in Agent_X.

The Self-Evolution Orchestrator coordinates governed self-evolution runs. It may decompose work, create task plans, bind steps to roles, request model calls, request tool calls, route failures, request approvals, request validation, collect evidence, and decide whether a run should continue, pause, retry, replan, request rollback, block, fail, or complete.

The orchestrator must not become a superuser layer.

Core rule:

```text
The Self-Evolution Orchestrator coordinates work.
It must not directly mutate source, bypass tools, bypass policy, bypass sandbox, bypass patch execution, bypass human approval, or bypass promotion gates.
```

The orchestrator is allowed to decide **what should be attempted next**. It is not allowed to directly perform unsafe actions.

---

# 2. Scope

## 2.1 Required in This Layer

The Self-Evolution Orchestrator must define and eventually implement contracts for:

```text
orchestration state
run admission
self-evolution session lifecycle
task plan structure
execution step structure
tool call binding
model call binding
prompt contract binding
human approval binding
governance gate binding
promotion gate binding
failure and recovery binding
run ledger
evidence manifest
review report
completion record
role permission matrix
stop / pause / retry / replan / rollback-request decision rules
integration with Agent_X controlled layers
deterministic replay and idempotency
run locking and concurrency control
runtime artifact immutability
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
file writing outside orchestrator runtime artifacts
source editing
patch application
raw shell execution
Git write operations
model runtime execution internals
prompt generation internals
human approval UI
promotion execution
network fetching
MCP server runtime
background daemon behavior
uncontrolled autonomous loops
```

The orchestrator coordinates these capabilities through controlled Agent_X layers only.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because the orchestrator is a high-authority coordination layer. It decides which controlled subsystem should be asked to act, in what order, with which role, and under which gates.

EQC applies to:

```text
run admission
role assignment
step sequencing
tool-call routing
model-call routing
policy gate enforcement
sandbox gate enforcement
patch gate enforcement
human approval gate enforcement
promotion gate enforcement
failure recovery decisions
retry limits
rollback requests
run stop decisions
run completion decisions
audit/evidence completeness
```

The orchestrator must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because the implementation must be file-specific and auditable.

Expected files include:

```text
tools/agentx_evolve/orchestrator/__init__.py
tools/agentx_evolve/orchestrator/orchestrator_models.py
tools/agentx_evolve/orchestrator/orchestrator_state.py
tools/agentx_evolve/orchestrator/run_admission.py
tools/agentx_evolve/orchestrator/task_planner.py
tools/agentx_evolve/orchestrator/execution_planner.py
tools/agentx_evolve/orchestrator/step_dispatcher.py
tools/agentx_evolve/orchestrator/tool_binding.py
tools/agentx_evolve/orchestrator/model_binding.py
tools/agentx_evolve/orchestrator/gate_controller.py
tools/agentx_evolve/orchestrator/failure_recovery.py
tools/agentx_evolve/orchestrator/run_ledger.py
tools/agentx_evolve/orchestrator/orchestrator_logger.py
tools/agentx_evolve/orchestrator/session_controller.py
tools/agentx_evolve/orchestrator/replay.py
tools/agentx_evolve/orchestrator/orchestrator_locks.py
```

Each file must have one clear responsibility, public API, safety invariants, tests, and evidence expectations.

## 3.3 Required Supporting Standard: SIB

SIB is required because the orchestrator connects controlled subsystems.

The orchestrator must integrate with:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Local Model Runtime Profile
Context Builder / Task Packer
Prompt Contract / Prompt Versioning
LLM Implementation Worker
Human Review / Approval Interface
Promotion / Release Gate
Git Integration Layer
Evaluation Harness / Regression Benchmark Layer
Monitoring / Observability Layer
Documentation Synchronization Layer
```

This layer is an integration boundary and state coordinator. It must not replace the authority of the layers it coordinates.

## 3.4 Required Schema Contract

Schema Contract is required because every orchestrator decision must be structured and reproducible.

Required schemas:

```text
run_admission.schema.json
orchestration_state.schema.json
task_plan.schema.json
execution_step.schema.json
orchestration_tool_binding.schema.json
orchestration_model_binding.schema.json
orchestration_approval_gate.schema.json
governance_gate.schema.json
orchestration_promotion_gate.schema.json
orchestration_recovery_action.schema.json
session_state.schema.json
run_ledger.schema.json
orchestrator_audit.schema.json
orchestrator_evidence_manifest.schema.json
orchestrator_review_report.schema.json
orchestrator_completion_record.schema.json
orchestrator_failure_class.schema.json
orchestrator_contract_compatibility.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every orchestrator decision must be evidenced.

Evidence is required for:

```text
run creation
run admission decision
task decomposition
step creation
state transition
step dispatch
tool-call request
model-call request
prompt-contract binding
policy gate result
sandbox gate result
patch gate result
human approval gate result
promotion gate result
failure classification
retry decision
replan decision
rollback request
pause decision
stop decision
completion decision
```

---

# 4. Dependency Gates and Restricted Mode

## 4.1 Required Controlled Layers

Before a live self-evolution run can perform non-read-only behavior, these layers must exist and be validated:

```text
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter
Model Adapter
Prompt Contract / Prompt Versioning
Human Review / Approval Interface, if approvals are required
Promotion / Release Gate, if promotion is reachable
```

## 4.2 Missing Dependency Behavior

If a dependency is missing, unavailable, schema-incompatible, or import-failing, the orchestrator must not bypass it.

Required behavior:

```text
missing Tool / MCP Adapter -> tool steps BLOCK
missing Policy / Capability Registry -> non-read-only steps BLOCK
missing Security Sandbox -> path/file/command steps BLOCK
missing Governed Patch Execution -> patch apply and rollback requests BLOCK
missing Failure Taxonomy -> failures are BLOCKED with ORCH_FAILURE_UNCLASSIFIED
missing Model Adapter -> model steps BLOCK
missing Prompt Contract -> model steps BLOCK
missing Human Approval Interface -> approval-required steps PAUSE or BLOCK
missing Promotion Gate -> promotion steps BLOCK
```

## 4.3 Restricted Mode

Restricted mode allows:

```text
schema validation
dry-run planning
run admission dry-run
task plan creation
step creation
read-only status inspection
evidence logging
run ledger creation
replay of existing evidence
```

Restricted mode blocks:

```text
source mutation requests
patch application requests
subprocess execution requests
Git write requests
network requests
promotion requests
approval overrides
MCP mutating exposure
```

## 4.4 Authority Rule

The orchestrator does not grant permission by itself.

A step may proceed only when all required authorities agree:

```text
Orchestrator state machine
Policy / Capability Registry
Security Sandbox, when paths/files/commands are involved
Tool / MCP Adapter, when tools are involved
Model Adapter, when models are involved
Prompt Contract / Prompt Versioning, when model prompts are involved
Governed Patch Execution, when patching or rollback is involved
Human Review / Approval Interface, when approval is required
Promotion / Release Gate, when promotion is requested
Failure Taxonomy, when failure recovery is involved
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
NEEDS_SANDBOX_CHECK
NEEDS_POLICY_CHECK
DRY_RUN_ONLY
ALLOW
```


## 4.5 Contract Compatibility Gate

A live run may proceed only when all bound layer contracts are compatible with the orchestrator contract.

Required compatibility checks:

```text
Tool / MCP Adapter contract version is recorded
Policy / Capability Registry contract version is recorded
Security Sandbox contract version is recorded
Governed Patch Execution contract version is recorded when patching or rollback is reachable
Model Adapter contract version is recorded when model calls are reachable
Prompt Contract / Prompt Versioning contract version is recorded when model calls are reachable
Human Review contract version is recorded when approval is reachable
Promotion Gate contract version is recorded when promotion is reachable
```

Compatibility result values:

```text
COMPATIBLE
INCOMPATIBLE
MISSING
DEFERRED_SAFELY
NOT_APPLICABLE
```

Rules:

```text
INCOMPATIBLE blocks live dispatch.
MISSING blocks any step requiring that layer.
DEFERRED_SAFELY allows dry-run or restricted behavior only.
NOT_APPLICABLE must be justified by run scope.
Compatibility evidence must be written before RUNNING state.
```

## 4.6 Cross-Layer Evidence Reference Rule

The orchestrator may not treat a delegated action as complete unless the owning layer returns evidence.

Required cross-layer evidence references:

```text
tool step -> ToolResult evidence ref from Tool / MCP Adapter
model step -> ModelCall result and output-validation evidence ref
policy gate -> PolicyDecision evidence ref
sandbox gate -> SandboxDecision evidence ref
patch request -> PatchSession / PatchResult evidence ref
human approval -> HumanApproval artifact ref
promotion request -> PromotionDecision evidence ref
failure handling -> Failure Taxonomy / Recovery evidence ref
```

Rules:

```text
request intent is not completion evidence
planned action is not completion evidence
model claim is not completion evidence
missing required downstream evidence blocks completion
cross-layer evidence refs must be hashable and replay-verifiable
```

---

# 5. Orchestrator Authority Rules

## 5.1 Authority Boundary

The orchestrator may coordinate:

```text
task planning
step sequencing
role assignment
model selection request
tool selection request
prompt contract binding request
policy decision request
sandbox decision request
patch session request
validation request
human approval request
promotion readiness request
failure recovery request
```

The orchestrator must not directly perform:

```text
source mutation
file writing outside approved runtime artifacts
patch application
shell command execution
Git branch/commit/push operations
network calls
model inference outside Model Adapter
prompt mutation outside Prompt Contract layer
approval override
promotion override
policy override
sandbox override
```

## 5.2 No Direct Mutation Rule

The orchestrator must not call:

```text
open(..., "w") for source files
Path.write_text for source files
Path.unlink for source files
subprocess for mutation
raw shell
Git write commands
patch apply libraries directly
network clients directly
```

Allowed writes are limited to orchestrator runtime artifacts under:

```text
.agentx-init/orchestrator/
```

## 5.3 No Bypass Rule

The orchestrator must not bypass:

```text
Tool / MCP Adapter for tool execution
Policy / Capability Registry for authorization
Security Sandbox for path/file/command checks
Governed Patch Execution for patch application
Model Adapter for model calls
Prompt Contract / Prompt Versioning for prompt bindings
Human Review / Approval Interface for approval-required decisions
Promotion / Release Gate for release decisions
Git Integration Layer for Git operations
```

## 5.4 Stop Authority

The orchestrator must stop, pause, or block a run when:

```text
policy blocks required action
sandbox blocks required action
patch layer blocks mutation
tool layer returns invalid or blocked result for required step
model output violates output contract
human approval is required but missing
promotion gate blocks release
retry limit is exceeded
failure taxonomy marks the issue as non-recoverable
run ledger becomes schema-invalid
evidence writing fails
source mutation is detected outside approved layers
runtime artifact hash validation fails
terminal state would be modified without new run_id
```


## 5.5 Coordinator / Executor / Reviewer Separation

The orchestrator is a coordinator. It must preserve separation between planning, execution, review, and promotion.

Rules:

```text
planner may create or revise TaskPlan
executor may dispatch only through controlled bindings
reviewer may inspect evidence and produce review decisions
promotion checker may request promotion evaluation only
no role may combine planning, mutation, approval, and promotion in one unchecked step
orchestrator cannot assign itself approval authority
orchestrator cannot mark its own unsafe output as reviewed
```

Required separation evidence:

```text
role assigned to each step
binding used for each external action
gate decision for each high-risk step
review evidence before completion or promotion
promotion evidence before promoted status
```

## 5.6 Human Interrupt and Kill-Switch Rule

A human or governance layer must be able to stop an active run through a controlled interrupt artifact.

Required behavior:

```text
interrupt request is recorded
active dispatch pauses before next step
already delegated external action is not repeated
state changes to PAUSED, CANCELLED, BLOCKED, or FAILED according to interrupt reason
interrupt cannot be ignored by retry/replan logic
interrupt evidence is included in the run ledger
```

The orchestrator must not continue a run after a valid cancellation or stop artifact.

---

# 6. Run Admission Rules

A self-evolution run may start only if a run admission decision is created.

Required run admission fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "run_admission.schema.json",
  "admission_id": "string",
  "run_id": "string",
  "requested_objective": "string",
  "requested_by": "string|null",
  "risk_level": "low|medium|high|critical",
  "allowed_mode": "DRY_RUN|RESTRICTED|GOVERNED_LIVE",
  "required_dependencies": [],
  "available_dependencies": [],
  "missing_dependencies": [],
  "decision": "ALLOW|BLOCK|DRY_RUN_ONLY|NEEDS_GOVERNANCE|NEEDS_HUMAN_APPROVAL",
  "reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Admission rules:

```text
unknown requester blocks
objective requesting direct mutation blocks
objective requesting policy/sandbox bypass blocks
missing Tool / MCP Adapter blocks live mode
missing Policy Registry blocks live non-read-only mode
missing Sandbox blocks path/file/command steps
missing Model Adapter blocks model steps
critical risk requires governance gate
approval-required objective pauses until approval exists
```


## 6.1 Run Identity, Lineage, Resume, and Fork Rules

Every run must have stable identity and lineage metadata.

Required fields:

```text
run_id
session_id
parent_run_id, nullable
forked_from_run_id, nullable
resume_of_run_id, nullable
objective_hash
contract_version_set
created_at
created_by
```

Rules:

```text
resume must reference a terminal or paused run and verify evidence hashes
fork creates a new run_id and cannot mutate prior run evidence
replan creates a new task_plan_version under the same run only if run is not terminal
terminal run cannot be resumed without creating a new run_id or explicit resume record
objective_hash must remain stable for the run unless a replan or fork records the change
```

## 6.2 Run Mode Semantics

Allowed modes:

```text
DRY_RUN
RESTRICTED
GOVERNED_LIVE
REPLAY
REVIEW_ONLY
```

Rules:

```text
DRY_RUN may validate plans and gates but must not dispatch side-effecting actions.
RESTRICTED may create plans and evidence but blocks missing-layer actions.
GOVERNED_LIVE may dispatch only through controlled bindings after all gates pass.
REPLAY reconstructs state from evidence and must not dispatch.
REVIEW_ONLY may inspect evidence and generate review artifacts only.
```

---

# 7. Agent_X Integration Notes

## 7.1 Tool / MCP Adapter Integration

All tool calls must go through the Tool / MCP Adapter.

Required behavior:

```text
orchestrator creates ToolCallBinding
ToolCallBinding references a registered tool
Tool / MCP Adapter validates tool call
Tool / MCP Adapter checks policy
Tool / MCP Adapter checks sandbox where required
Tool / MCP Adapter writes tool evidence
orchestrator records returned ToolResult reference
```

The orchestrator must not call internal wrapper tools directly unless explicitly executing unit tests for this layer.

## 7.2 Policy / Capability Registry Integration

The orchestrator must request policy decisions before dispatching steps that may read, write, execute, call models, request patching, or request promotion.

Required behavior:

```text
missing policy -> BLOCKED
policy denial -> BLOCKED
policy needs approval -> PAUSED_PENDING_APPROVAL
policy needs governance -> PAUSED_PENDING_GOVERNANCE
policy allow -> continue only if other gates also allow
```

## 7.3 Security Sandbox Integration

The orchestrator must not inspect or mutate paths directly.

All path/file/command checks must be routed through:

```text
Tool / MCP Adapter
Security Sandbox / Filesystem Boundary
```

## 7.4 Governed Patch Execution Integration

Patch application must be handled only by the Governed Patch Execution Layer.

The orchestrator may request:

```text
patch precheck
patch session status
patch apply request
rollback request
```

It may not perform patch application itself.

## 7.5 Failure Taxonomy / Recovery Playbook Integration

All failed, blocked, invalid, or partial steps must be classified.

The orchestrator must bind failures to:

```text
failure_class
failure_severity
recovery_action
retry_allowed
rollback_required
human_review_required
stop_required
```

## 7.6 Model Adapter Integration

The orchestrator may request model calls only through the Model Adapter.

It must not directly call:

```text
hosted model APIs
local model runtimes
LLM clients
embedding services
network providers
```

## 7.7 Prompt Contract / Prompt Versioning Integration

Every model call must reference a prompt contract and prompt version.

Required binding fields:

```text
prompt_contract_id
prompt_version_id
input_contract_id
output_contract_id
safety_rule_ids
provenance_ref
```

## 7.8 Human Review / Approval Interface Integration

The orchestrator may request approval, but cannot grant approval itself.

Approval-required steps must pause until a valid approval artifact exists.

## 7.9 Promotion / Release Gate Integration

The orchestrator may request promotion evaluation, but cannot promote directly.

Promotion requires:

```text
validation pass
review pass
evidence pass
policy pass
human approval if required
promotion gate allow
```

---

# 8. OpenCode Borrowing Notes

## 8.1 Concepts to Borrow

Borrow these OpenCode-style concepts:

```text
plan-first workflow
task decomposition
step-level tool calling
tool result feedback loop
invalid tool handling
question / human clarification concept
session state tracking
structured tool registry awareness
bounded retry behavior
summarized tool outputs
```

## 8.2 Concepts to Restrict

Do not copy these assumptions directly:

```text
agent can freely call shell
agent can directly edit files
agent can directly apply patches
agent can choose tools without policy
agent can keep retrying indefinitely
agent can use network by default
agent can run subagents without role permissions
agent can mutate prompts without prompt versioning
agent can proceed without evidence
```

## 8.3 Agent_X Mapping

| OpenCode concept | Agent_X orchestrator equivalent | Required control |
|---|---|---|
| plan mode | `TaskPlan` + `ExecutionStep` | policy + evidence |
| tool call loop | `ToolCallBinding` | Tool / MCP Adapter |
| edit/write/patch | patch request binding | Governed Patch Execution |
| shell tool | command tool request | Tool Adapter + Sandbox + Policy |
| question | human approval/request binding | Human Review Interface |
| subtask | execution step with role | Role Permission Matrix |
| retry | recovery binding | Failure Taxonomy |
| session | orchestrator session state | Run Ledger + evidence |
| invalid tool | blocked/invalid step result | Tool Adapter + Failure Taxonomy |

---

# 9. Role Permission Matrix

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
MCP_CLIENT
MODEL_WORKER
UNKNOWN_CALLER
```

| Role | May plan | May request tools | May request model | May request patch | May approve | May promote | Direct mutation allowed |
|---|---:|---:|---:|---:|---:|---:|---:|
| ORCHESTRATOR | Yes | Yes, through Tool Adapter | Yes, through Model Adapter | Yes, through Patch Layer | No | No | No |
| IMPLEMENTATION_WORKER | No | Limited through binding | Yes, through Model Adapter | Request only | No | No | No |
| VALIDATION_REPAIR_WORKER | Limited | Validation tools only | Yes, through Model Adapter | Request only | No | No | No |
| REVIEWER_ASSISTANT | Review only | Read-only tools | Optional review model | No | No | No | No |
| PROMOTION_CHECKER | No | Read-only validation/Git status | No or review-only | No | No | Request gate only | No |
| HUMAN_OPERATOR | No | Optional review tools | No | No | Yes, if valid authority | No direct promotion | No |
| MCP_CLIENT | No | Least-privilege tools only | No | No | No | No | No |
| MODEL_WORKER | No | No direct tools unless bound | Model call only | No | No | No | No |
| UNKNOWN_CALLER | No | No | No | No | No | No | No |

Rules:

```text
UNKNOWN_CALLER always blocks.
ORCHESTRATOR cannot override policy, sandbox, human approval, or promotion gate.
HUMAN_OPERATOR cannot override non-overridable safety blocks.
MCP_CLIENT is least privilege by default.
MODEL_WORKER cannot call tools directly unless a ToolCallBinding exists.
```

---

# 10. Schema Contracts

## 10.1 General Schema Rules

Every schema must:

```text
require schema_version
require schema_id
require run_id where run-scoped
require session_id where session-scoped
require timestamp or created_at where event-scoped
require evidence_refs
require warnings
require errors
define enum values for state, status, decision, role, and gate fields
reject missing required fields
reject invalid enum values
```

Every schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
unsafe direct-mutation instruction fails where applicable
```

## 10.2 Orchestration State Schema

Purpose: captures the current state of a self-evolution run.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_state.schema.json",
  "run_id": "string",
  "session_id": "string",
  "state": "CREATED|ADMISSION_CHECK|PLANNING|WAITING_FOR_GATE|RUNNING|PAUSED|RECOVERING|REPLANNING|ROLLING_BACK|VALIDATING|PROMOTION_CHECK|COMPLETED|FAILED|BLOCKED|CANCELLED",
  "current_step_id": "string|null",
  "task_plan_id": "string|null",
  "active_role": "string|null",
  "blocked_reason": "string|null",
  "last_decision_id": "string|null",
  "state_version": 1,
  "state_hash": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
state is required
run_id is required
invalid state transitions must block
state transitions must be logged
terminal states are immutable without new run_id
```

## 10.3 Task Plan Schema

Purpose: defines the high-level task plan for a run.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_plan.schema.json",
  "task_plan_id": "string",
  "task_plan_version": 1,
  "run_id": "string",
  "created_at": "string",
  "objective": "string",
  "scope": "string",
  "non_goals": [],
  "required_roles": [],
  "steps": [],
  "risk_level": "low|medium|high|critical",
  "required_gates": [],
  "plan_hash": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
task plan must not include direct source mutation instructions
each step must have an execution_step_id
each risky step must list required gates
replan creates a new task_plan_version
```

## 10.4 Execution Step Schema

Purpose: defines one executable orchestration step.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "execution_step.schema.json",
  "execution_step_id": "string",
  "run_id": "string",
  "task_plan_id": "string",
  "step_index": 0,
  "step_type": "PLAN|MODEL_CALL|TOOL_CALL|PATCH_REQUEST|VALIDATION_REQUEST|REVIEW_REQUEST|PROMOTION_REQUEST|RECOVERY_ACTION|STOP",
  "assigned_role": "string",
  "description": "string",
  "status": "PENDING|READY|RUNNING|SUCCESS|PARTIAL|BLOCKED|FAILED|SKIPPED|CANCELLED",
  "required_gates": [],
  "binding_refs": [],
  "input_refs": [],
  "output_refs": [],
  "idempotency_key": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
execution steps must be deterministic
step_index must be stable
required gates must pass before dispatch
failed required step blocks run unless recovery is allowed
idempotency_key prevents duplicate dispatch
```

## 10.5 Tool Call Binding Schema

Purpose: binds an execution step to a Tool / MCP Adapter call.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_tool_binding.schema.json",
  "binding_id": "string",
  "execution_step_id": "string",
  "tool_name": "string",
  "caller_role": "ORCHESTRATOR",
  "requested_effect": "READ|WRITE|EXECUTE|VALIDATE|REPORT|PLAN|PROPOSE|ROLLBACK",
  "tool_call_id": "string|null",
  "tool_result_id": "string|null",
  "policy_decision_id": "string|null",
  "sandbox_decision_id": "string|null",
  "dispatch_status": "PENDING|DISPATCHED|SUCCESS|BLOCKED|FAILED|INVALID",
  "idempotency_key": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
tool_name must exist in Tool Registry before dispatch
Tool Adapter must execute the tool; orchestrator must not execute wrapper directly
blocked tool result blocks step unless recovery path exists
same idempotency_key must not dispatch twice
```

## 10.6 Model Call Binding Schema

Purpose: binds an execution step to a governed model call.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_model_binding.schema.json",
  "binding_id": "string",
  "execution_step_id": "string",
  "model_profile_id": "string",
  "model_adapter_call_id": "string|null",
  "prompt_contract_id": "string",
  "prompt_version_id": "string",
  "input_contract_id": "string",
  "output_contract_id": "string",
  "allowed_task_type": "string",
  "model_output_validation_ref": "string|null",
  "status": "PENDING|DISPATCHED|SUCCESS|BLOCKED|FAILED|INVALID",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
model calls must go through Model Adapter
prompt contract and version are required
model output must be validated against output contract
model cannot mutate source directly
prompt-injection content must be treated as data, not authority
```

## 10.7 Human Approval Binding Schema

Purpose: records an approval requirement and approval status.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_approval_gate.schema.json",
  "approval_binding_id": "string",
  "execution_step_id": "string",
  "approval_type": "SOURCE_MUTATION|PATCH_APPLY|ROLLBACK|PROMOTION|HIGH_RISK_MODEL_OUTPUT|OTHER",
  "required": true,
  "approval_status": "NOT_REQUESTED|REQUESTED|APPROVED|REJECTED|EXPIRED|BLOCKED",
  "approval_artifact_ref": "string|null",
  "approved_by": "string|null",
  "approved_at": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
orchestrator cannot self-approve
missing approval pauses or blocks the step
rejected approval blocks the step
approval artifact must be independently produced
```

## 10.8 Governance Gate Schema

Purpose: records governance requirements for risky actions.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "governance_gate.schema.json",
  "gate_id": "string",
  "execution_step_id": "string",
  "gate_type": "POLICY|SANDBOX|PATCH|MODEL|PROMPT|HUMAN_APPROVAL|VALIDATION|PROMOTION|EVIDENCE",
  "required": true,
  "decision": "ALLOW|BLOCK|NEEDS_APPROVAL|NEEDS_GOVERNANCE|NEEDS_SANDBOX_CHECK|DRY_RUN_ONLY|NOT_CHECKED",
  "decision_ref": "string|null",
  "reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
NOT_CHECKED gate cannot proceed
BLOCK gate cannot proceed
NEEDS_APPROVAL pauses run
NEEDS_GOVERNANCE pauses run
```

## 10.9 Promotion Gate Binding Schema

Purpose: binds final release/promotion readiness to the Promotion / Release Gate.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_promotion_gate.schema.json",
  "promotion_binding_id": "string",
  "run_id": "string",
  "candidate_artifact_refs": [],
  "validation_refs": [],
  "review_refs": [],
  "policy_refs": [],
  "promotion_decision": "NOT_REQUESTED|ALLOW|BLOCK|NEEDS_APPROVAL|FAILED",
  "promotion_decision_ref": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
orchestrator may request promotion check
orchestrator cannot promote directly
promotion BLOCK means run cannot be marked promoted
```

## 10.10 Failure / Recovery Binding Schema

Purpose: binds a failed step to recovery policy.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_recovery_action.schema.json",
  "recovery_binding_id": "string",
  "execution_step_id": "string",
  "failure_class": "string",
  "failure_severity": "low|medium|high|critical",
  "retry_allowed": false,
  "retry_count": 0,
  "max_retries": 0,
  "recovery_action": "NONE|RETRY|REPLAN|ROLLBACK_REQUEST|HUMAN_REVIEW|STOP_RUN",
  "rollback_required": false,
  "status": "PENDING|RUNNING|SUCCESS|BLOCKED|FAILED",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
retry_count cannot exceed max_retries
critical failures default to STOP_RUN unless recovery playbook explicitly allows otherwise
rollback must be requested through Governed Patch Execution
```

## 10.11 Session State Schema

Purpose: captures durable session-level state.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "session_state.schema.json",
  "session_id": "string",
  "run_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "status": "ACTIVE|PAUSED|BLOCKED|COMPLETED|FAILED|CANCELLED",
  "current_state_ref": "string",
  "task_plan_ref": "string|null",
  "ledger_ref": "string|null",
  "lock_ref": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
session state must be written atomically
schema-invalid state must not replace valid latest state
only one active writer may own a run lock
```

## 10.12 Run Ledger Schema

Purpose: append-only record of orchestration events.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "run_ledger.schema.json",
  "ledger_id": "string",
  "run_id": "string",
  "created_at": "string",
  "events": [],
  "event_count": 0,
  "ledger_hash": "string|null",
  "previous_ledger_hash": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Each ledger event must include:

```json
{
  "event_id": "string",
  "timestamp": "string",
  "event_type": "string",
  "step_id": "string|null",
  "state_before": "string|null",
  "state_after": "string|null",
  "status": "string",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": []
}
```

Rules:

```text
ledger history is append-only
ledger hash must be updated when finalized
manual edits invalidate prior completion evidence
```


## 10.13 Orchestrator Failure Class Schema

Purpose: defines the orchestrator-specific failure classes used by recovery logic.

Required failure classes:

```text
ORCH_RUN_ADMISSION_DENIED
ORCH_DEPENDENCY_MISSING
ORCH_CONTRACT_INCOMPATIBLE
ORCH_INVALID_STATE_TRANSITION
ORCH_TERMINAL_STATE_IMMUTABLE
ORCH_GATE_NOT_CHECKED
ORCH_GATE_BLOCKED
ORCH_TOOL_BINDING_INVALID
ORCH_TOOL_RESULT_MISSING
ORCH_MODEL_BINDING_INVALID
ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION
ORCH_PROMPT_CONTRACT_MISSING
ORCH_POLICY_DENIED
ORCH_SANDBOX_DENIED
ORCH_PATCH_LAYER_DENIED
ORCH_HUMAN_APPROVAL_MISSING
ORCH_PROMOTION_DENIED
ORCH_RETRY_LIMIT_EXCEEDED
ORCH_BUDGET_EXCEEDED
ORCH_EVIDENCE_MISSING
ORCH_EVIDENCE_HASH_MISMATCH
ORCH_REPLAY_MISMATCH
ORCH_INTERRUPT_REQUESTED
ORCH_FAILURE_UNCLASSIFIED
ORCH_APPROVED_PLAN_HASH_MISMATCH
ORCH_SIDE_EFFECT_MISMATCH
ORCH_AUTHORITY_SNAPSHOT_MISSING
ORCH_LEDGER_SEQUENCE_INVALID
ORCH_EVIDENCE_QUARANTINED
```

Rules:

```text
every BLOCKED, FAILED, or INVALID step must include a failure_class
unclassified critical failure stops the run
failure_class must map to an allowed recovery action
unknown failure class blocks recovery automation
```

## 10.14 Contract Compatibility Schema

Purpose: records compatibility between the orchestrator and the layers it coordinates.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestrator_contract_compatibility.schema.json",
  "compatibility_id": "string",
  "run_id": "string",
  "checked_at": "string",
  "layer_contracts": [],
  "compatibility_status": "COMPATIBLE|INCOMPATIBLE|MISSING|DEFERRED_SAFELY|NOT_APPLICABLE",
  "blocking_reasons": [],
  "deviation_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Each layer contract entry must include:

```text
layer_name
component_id
contract_document_id
contract_version
required_for_run
status
reason
```

Rules:

```text
required layer with MISSING status blocks live mode
required layer with INCOMPATIBLE status blocks live mode
DEFERRED_SAFELY must restrict the affected steps
compatibility evidence is required before first dispatch
```

---

# 11. Runtime Artifact Rules

Runtime artifacts must be written under:

```text
.agentx-init/orchestrator/
```

Required artifacts:

```text
.agentx-init/orchestrator/run_admission_history.jsonl
.agentx-init/orchestrator/orchestration_state_history.jsonl
.agentx-init/orchestrator/execution_step_history.jsonl
.agentx-init/orchestrator/tool_binding_history.jsonl
.agentx-init/orchestrator/model_binding_history.jsonl
.agentx-init/orchestrator/gate_history.jsonl
.agentx-init/orchestrator/run_ledger.jsonl
.agentx-init/orchestrator/failure_recovery_history.jsonl
.agentx-init/orchestrator/latest_orchestration_state.json
.agentx-init/orchestrator/latest_session_state.json
.agentx-init/orchestrator/latest_task_plan.json
.agentx-init/orchestrator/orchestrator_evidence_manifest.json
.agentx-init/orchestrator/orchestrator_review_report.json
.agentx-init/orchestrator/orchestrator_completion_record.json
```

Rules:

```text
history files are append-only JSONL
latest artifacts are written atomically
secrets and raw prompt contents are redacted
raw model outputs are summarized unless contract allows durable storage
source files are never written by this layer
runtime artifact writes outside approved root require deviation record
```

---

# 12. Locking, Concurrency, Idempotency, and Replay

## 12.1 Run Locking

Only one active orchestrator writer may own a run at a time.

Required behavior:

```text
run lock acquired before state mutation
lock contains run_id, session_id, owner_id, created_at, expires_at
expired lock may be recovered only with evidence
lock conflict pauses or blocks the run
lock release is evidenced
```

## 12.2 Idempotency

Every dispatchable step must have an idempotency key.

Required behavior:

```text
same idempotency key cannot dispatch the same external action twice
repeated read-only step may reuse cached result if evidence hash matches
repeated mutating request must block unless owning layer confirms idempotent safety
```

## 12.3 Deterministic Replay

The orchestrator must support replay from evidence without performing side effects.

Replay mode may:

```text
read orchestrator ledger
validate state transitions
validate evidence hashes
reconstruct final state
report missing evidence
```

Replay mode must not:

```text
dispatch tools
call models
request patches
request approvals
write source
execute commands
```


## 12.4 Dispatch Receipt Rule

Every delegated action must produce a dispatch receipt before the orchestrator advances the step.

Required receipt fields:

```text
dispatch_receipt_id
run_id
execution_step_id
binding_id
owning_layer
request_id
result_id, nullable until completed
idempotency_key
status
artifact_refs
evidence_refs
created_at
completed_at, nullable
```

Rules:

```text
dispatch receipt is required for tool, model, patch, approval, validation, and promotion requests
a step cannot be SUCCESS without a result receipt or accepted skipped/deferred status
orchestrator cannot invent downstream result IDs
duplicate dispatch receipt with same idempotency_key must resolve to same result or block
```

## 12.5 Partial Success and Degraded Mode

Partial success must be explicit and cannot silently become completion.

Rules:

```text
PARTIAL step status requires a reason and recovery decision
DEGRADED mode requires a dependency/deviation record
run can complete in DEGRADED mode only if all missing items are non-safety and explicitly accepted
safety-critical missing layer cannot be degraded for live side effects
```

## 12.6 Approved Plan Freeze and Plan Hash Rule

A task plan must be frozen before any live dispatch.

Required behavior:

```text
planner creates draft TaskPlan
validator checks schema, policy compatibility, role permissions, and prohibited directives
approved plan receives plan_hash
execution steps bind to approved plan_hash
any plan revision creates a new plan_version and new plan_hash
live dispatch is blocked if step.plan_hash does not match active approved plan_hash
```

Rules:

```text
model-generated plan text is not executable until normalized and validated
manual edits to a plan after approval invalidate the previous plan_hash
replan after failure requires new plan_version and evidence link to the recovery decision
COMPLETED state is invalid if any executed step references an unapproved or superseded plan_hash
```

## 12.7 Causal Event Ordering Rule

Every run ledger event must have deterministic ordering.

Required fields:

```text
ledger_sequence
causal_parent_event_ids
state_before
state_after
event_hash
previous_event_hash
```

Rules:

```text
ledger_sequence must be monotonic per run
previous_event_hash must match the prior accepted event
out-of-order event append blocks replay validation
conflicting state transitions with the same sequence number block the run
replay must reconstruct the same terminal state from ordered ledger events
```

## 12.8 Side-Effect Declaration Rule

Every dispatchable step must declare its intended side effects before dispatch.

Required fields:

```text
read_set
write_set
execute_set
network_set
runtime_artifact_set
expected_downstream_layer
expected_gate_ids
```

Rules:

```text
empty declaration is allowed only for pure planning/ledger steps
source write_set requires patch/governance path, not orchestrator direct write
execute_set requires Tool Adapter and policy/command gate
network_set blocks by default unless explicit provider/network policy allows it
actual downstream result must not exceed declared side-effect set
side-effect mismatch blocks completion and triggers recovery classification
```

## 12.9 Dispatch Claim Verification Rule

The orchestrator must distinguish request, acceptance, execution, result, and evidence.

Required statuses:

```text
REQUESTED
ACCEPTED_BY_OWNER
REJECTED_BY_OWNER
RUNNING_IN_OWNER
COMPLETED_BY_OWNER
FAILED_BY_OWNER
EVIDENCE_RECORDED
VERIFIED_BY_ORCHESTRATOR
```

Rules:

```text
REQUESTED is not success
ACCEPTED_BY_OWNER is not success
COMPLETED_BY_OWNER requires downstream result evidence
VERIFIED_BY_ORCHESTRATOR requires schema-valid result, hashable evidence, and expected side-effect match
step SUCCESS requires VERIFIED_BY_ORCHESTRATOR or explicitly accepted skip/deferred status
```

## 12.10 Quarantine Rule for Inconsistent Evidence

If downstream evidence is missing, hash-mismatched, schema-invalid, or inconsistent with declared side effects, the orchestrator must quarantine the affected step.

Required behavior:

```text
mark step BLOCKED or FAILED
record ORCH_EVIDENCE_HASH_MISMATCH, ORCH_REPLAY_MISMATCH, or ORCH_SIDE_EFFECT_MISMATCH
pause further dependent steps
write quarantine evidence
require human/governance review before resume or fork
```

The orchestrator must not repair inconsistent evidence by rewriting history.

---

# 13. State Machine Contract

Allowed states:

```text
CREATED
ADMISSION_CHECK
PLANNING
WAITING_FOR_GATE
RUNNING
PAUSED
RECOVERING
REPLANNING
ROLLING_BACK
VALIDATING
PROMOTION_CHECK
COMPLETED
FAILED
BLOCKED
CANCELLED
```

Allowed transition examples:

```text
CREATED -> ADMISSION_CHECK
ADMISSION_CHECK -> PLANNING
ADMISSION_CHECK -> BLOCKED
PLANNING -> WAITING_FOR_GATE
WAITING_FOR_GATE -> RUNNING
RUNNING -> VALIDATING
RUNNING -> RECOVERING
RECOVERING -> RUNNING
RECOVERING -> REPLANNING
REPLANNING -> WAITING_FOR_GATE
RECOVERING -> ROLLING_BACK
ROLLING_BACK -> VALIDATING
VALIDATING -> PROMOTION_CHECK
VALIDATING -> COMPLETED
PROMOTION_CHECK -> COMPLETED
any active state -> PAUSED
any active state -> BLOCKED
any active state -> FAILED
any active state -> CANCELLED
```

Forbidden transitions:

```text
COMPLETED -> RUNNING
FAILED -> RUNNING without new run_id
BLOCKED -> RUNNING without resolved gate evidence
CANCELLED -> RUNNING
PROMOTION_CHECK -> COMPLETED without promotion gate evidence
RUNNING -> COMPLETED without validation evidence
any terminal state -> active state without new run_id
```

Terminal states:

```text
COMPLETED
FAILED
BLOCKED
CANCELLED
```

Terminal state artifacts are immutable unless a new run is created.

---

# 14. Evidence / Audit Contract

Every orchestrator event must create evidence.

Required evidence fields:

```text
schema_version
schema_id
event_id
timestamp
run_id
session_id
source_component
state_before
state_after
decision
reason
step_id
binding_refs
artifact_refs
evidence_refs
warnings
errors
```

Evidence must prove:

```text
who/what made the decision
which gates were checked
which controlled layer was called
which result was returned
why the run proceeded, paused, retried, replanned, rolled back, blocked, or completed
```

A final `COMPLETED` run is invalid without:

```text
run admission evidence
task plan evidence
step execution evidence
tool/model binding evidence where applicable
gate evidence
validation evidence
failure/recovery evidence if failures occurred
promotion evidence if promotion was requested
completion record
```

## 14.1 Evidence Manifest

Create:

```text
.agentx-init/orchestrator/orchestrator_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestrator_evidence_manifest.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "run_id": "string",
  "session_id": "string",
  "validated_commit": "string",
  "validated_at": "string",
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "replay_status": "PASS|FAIL|NOT_RUN",
  "final_decision": "DONE|NOT_DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence artifacts.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required hashes are missing.
```

## 14.2 Review Report

Create:

```text
.agentx-init/orchestrator/orchestrator_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestrator_review_report.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "review_document_id": "SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT",
  "review_document_version": "v4.0",
  "reviewed_commit": "string",
  "reviewed_branch": "string",
  "reviewed_at": "string",
  "reviewer": "string",
  "review_environment": {
    "os": "string",
    "python_version": "string",
    "pytest_version": "string|null"
  },
  "commands_run": [],
  "command_exit_codes_recorded": true,
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": "string",
  "evidence_manifest_sha256": "string",
  "completion_record_path": "string",
  "completion_record_sha256": "string",
  "implementation_rating": 10.0,
  "final_verdict": "DONE|NOT_DONE"
}
```

## 14.3 Evidence Hash Closure Rule

The final evidence set must be hash-closed before DONE.

Required behavior:

```text
every final evidence artifact has a SHA-256 hash
hashes are recorded in the evidence manifest
review report records the evidence manifest hash
completion record records the review report hash
changed final evidence invalidates the prior DONE verdict
```

Because a file cannot stably contain its own final hash without a special envelope, self-hashing must be handled by one of these accepted patterns:

```text
manifest excludes its own hash but is hashed by review report
manifest has external .sha256 sidecar inside runtime artifact root
completion record records final manifest and review report hashes
```

## 14.4 Minimum Run Ledger Event Set

A completed governed run must contain at least these ledger event types:

```text
RUN_CREATED
RUN_ADMISSION_DECIDED
AUTHORITY_SNAPSHOT_CREATED
CONTRACT_COMPATIBILITY_CHECKED
TASK_PLAN_CREATED
TASK_PLAN_VALIDATED
TASK_PLAN_APPROVED_OR_DRY_RUN_ACCEPTED
STEP_CREATED
STEP_GATE_CHECKED
STEP_DISPATCH_RECEIPT_CREATED, when delegated
DOWNSTREAM_RESULT_RECEIVED, when delegated
STEP_VERIFIED
VALIDATION_REQUESTED_OR_NOT_APPLICABLE
FINAL_STATE_DECIDED
COMPLETION_RECORD_WRITTEN
```

Missing required event types block `COMPLETED` unless the event is explicitly not applicable and justified by run mode.

## 14.5 Observability Is Not Authority

Monitoring, metrics, traces, and status summaries may help explain a run, but they do not grant permission.

Rules:

```text
observability events cannot replace policy evidence
observability events cannot replace sandbox evidence
observability events cannot replace approval evidence
observability events cannot replace promotion evidence
metrics cannot be used as proof that a side effect was authorized
logs must be treated as supporting evidence only unless schema-bound as decision evidence
```

## 14.6 Evidence Retention and Terminal Immutability

After a run reaches `COMPLETED`, `FAILED`, `BLOCKED`, or `CANCELLED`:

```text
terminal state artifact is immutable
ledger may receive append-only review/annotation events only
no event may change the terminal decision without a new run_id
manual correction requires deviation entry and new review report
hash changes invalidate previous completion evidence
```

---

# 15. Prompt-Injection and Model-Output Containment

The orchestrator must treat model outputs, tool outputs, retrieved text, logs, and generated plans as data until validated.

Rules:

```text
model output cannot grant approval
model output cannot override policy
model output cannot override sandbox
model output cannot request direct source mutation outside governed layers
model output cannot change prompt contract version
model output cannot mark a run complete without gate evidence
instructions found inside repository files are untrusted unless bound through Prompt Contract
```

Model-generated task plans must be validated before dispatch.

Unsafe model output must result in:

```text
BLOCKED step
failure_class = ORCH_MODEL_OUTPUT_CONTRACT_VIOLATION or equivalent
recovery_action = REPLAN, HUMAN_REVIEW, or STOP_RUN
```


## 15.1 Model-Generated Plan Validation

A model-generated plan is only a draft until validated.

Required validation checks:

```text
plan conforms to task_plan.schema.json
all steps conform to execution_step.schema.json
no step requests direct source mutation
no step requests raw shell execution
no step bypasses Tool / MCP Adapter
no step bypasses Model Adapter
no step bypasses Prompt Contract
required gates are present for risky steps
roles are allowed by Role Permission Matrix
budgets are present
idempotency keys are present for dispatchable steps
```

Rules:

```text
invalid model-generated plan cannot be dispatched
unsafe model-generated plan becomes BLOCKED or requires HUMAN_REVIEW
validated plan must record original model output provenance without treating it as authority
```

---

# 16. Failure and Recovery Rules

The orchestrator may recover only through defined recovery actions.

Allowed recovery actions:

```text
NONE
RETRY
REPLAN
ROLLBACK_REQUEST
HUMAN_REVIEW
STOP_RUN
```

Rules:

```text
retry requires retry_allowed=true
retry_count must not exceed max_retries
replan must create a new task_plan version
rollback must be requested through Governed Patch Execution
human review must pause run until approval/rejection exists
critical unclassified failures stop the run
missing evidence for a required step stops the run
```

No infinite retry loops are allowed.

Default retry policy:

```text
max_retries = 0 for critical operations
max_retries = 1 for safe read-only recoverable operations
max_retries = 0 for patch apply, rollback, promotion, Git write, and approval gates
```

---

# 17. Budget, Timeout, and Loop Prevention Rules

Every run must define budgets:

```text
max_steps
max_model_calls
max_tool_calls
max_retries_per_step
max_total_runtime_seconds
max_replans
max_recovery_actions
```

Default safety limits:

```text
max_retries_per_step = 0 unless explicitly allowed
max_replans = 1 unless explicitly allowed
approval wait cannot block active execution indefinitely
terminal state must stop dispatch
```

If a budget is exceeded:

```text
state = BLOCKED or FAILED
failure_class = ORCH_BUDGET_EXCEEDED
evidence must be written
```


## 17.1 Output and Artifact Boundary Rules

The orchestrator may persist only bounded, redacted, contract-relevant data.

Rules:

```text
raw prompts are not durably logged unless the Prompt Contract permits it
raw model outputs are summarized or stored as approved artifacts with hashes
large tool results are referenced, not copied into orchestrator ledger
secret-like values are redacted before persistence
artifact refs must include owning layer and hash when available
artifact provenance must identify source layer, schema_id, created_at, and run_id/session_id
```

Required provenance fields for persisted orchestrator artifacts:

```text
artifact_id
artifact_type
owning_component
schema_id
run_id
session_id
created_at
source_ref
sha256, where file-backed
redaction_status
```

---

# 18. Security Rules

This layer must enforce:

```text
no direct source mutation
no direct patch application
no raw shell
no Git write
no network by default
no model call bypass
no prompt contract bypass
no policy bypass
no sandbox bypass
no human approval bypass
no promotion gate bypass
no MCP exposure bypass
no unbounded autonomous loop
no silent failure
no unevidenced decision
no terminal-state mutation without new run_id
no missing evidence hashes for final DONE
```

---

# 19. Public API Contract

Expected classes:

```text
RunAdmissionDecision
OrchestrationState
TaskPlan
ExecutionStep
ToolCallBinding
ModelCallBinding
HumanApprovalBinding
GovernanceGate
PromotionGateBinding
FailureRecoveryBinding
SessionState
RunLedger
OrchestratorAuditEvent
OrchestratorEvidenceManifest
OrchestratorReviewReport
OrchestratorCompletionRecord
```

Expected public functions:

```python
create_orchestration_run(objective: str, context: dict) -> OrchestrationState
create_run_admission_decision(run_id: str, objective: str, context: dict) -> RunAdmissionDecision
create_task_plan(run_id: str, objective: str, constraints: dict) -> TaskPlan
validate_task_plan(task_plan: TaskPlan) -> list[str]
create_execution_steps(task_plan: TaskPlan) -> list[ExecutionStep]
check_step_gates(step: ExecutionStep, context: dict) -> list[GovernanceGate]
dispatch_execution_step(step: ExecutionStep, context: dict) -> ExecutionStep
bind_tool_call(step: ExecutionStep, tool_name: str, arguments: dict) -> ToolCallBinding
bind_model_call(step: ExecutionStep, model_profile_id: str, prompt_contract_id: str) -> ModelCallBinding
request_human_approval(step: ExecutionStep, approval_type: str) -> HumanApprovalBinding
handle_step_failure(step: ExecutionStep, failure: dict) -> FailureRecoveryBinding
update_orchestration_state(state: OrchestrationState, event: dict) -> OrchestrationState
append_run_ledger_event(run_id: str, event: dict) -> dict
write_orchestrator_evidence(event: dict, repo_root: Path) -> dict
replay_orchestrator_run(run_id: str, repo_root: Path) -> dict
acquire_run_lock(run_id: str, session_id: str, repo_root: Path) -> dict
release_run_lock(run_id: str, session_id: str, repo_root: Path) -> dict
```

Must not expose public functions that directly mutate source, execute shell, apply patches, call models directly, or promote releases.

---

# 20. Test Acceptance Criteria

Required tests:

```text
test_run_admission_blocks_direct_mutation_objective
test_run_admission_blocks_missing_tool_adapter_for_live_mode
test_orchestration_state_schema_accepts_valid_state
test_orchestration_state_schema_rejects_invalid_transition
test_terminal_state_is_immutable_without_new_run_id
test_task_plan_schema_accepts_valid_plan
test_task_plan_rejects_direct_mutation_instruction
test_execution_step_schema_accepts_valid_step
test_execution_step_requires_idempotency_key_for_dispatch
test_tool_call_binding_requires_tool_adapter
test_tool_call_binding_does_not_dispatch_duplicate_idempotency_key
test_model_call_binding_requires_prompt_contract
test_model_output_cannot_override_policy
test_human_approval_binding_cannot_self_approve
test_governance_gate_blocks_not_checked_gate
test_promotion_gate_cannot_complete_without_decision
test_failure_recovery_blocks_retry_over_limit
test_run_ledger_appends_events
test_ledger_hash_changes_on_append
test_latest_state_written_atomically
test_orchestrator_never_writes_source_files
test_orchestrator_never_executes_raw_shell
test_policy_block_pauses_or_blocks_run
test_sandbox_block_pauses_or_blocks_run
test_patch_apply_requested_through_patch_layer_only
test_missing_evidence_blocks_completion
test_evidence_manifest_requires_hashes
test_replay_does_not_dispatch_side_effects
test_completed_run_requires_completion_record
test_contract_compatibility_blocks_incompatible_layer
test_cross_layer_evidence_refs_required_for_completion
test_dispatch_receipt_required_before_step_success
test_human_interrupt_stops_next_dispatch
test_replay_verifies_cross_layer_evidence_hashes
test_partial_success_cannot_complete_without_accepted_deviation
test_model_generated_plan_validated_before_dispatch
test_approved_plan_hash_required_before_live_dispatch
test_plan_revision_invalidates_previous_plan_hash
test_authority_snapshot_required_before_running
test_authority_snapshot_mismatch_blocks_replay
test_ledger_sequence_must_be_monotonic
test_previous_event_hash_must_match
test_side_effect_declaration_required_for_dispatch
test_downstream_result_cannot_exceed_side_effect_declaration
test_dispatch_requested_is_not_success
test_completed_by_owner_requires_evidence
test_inconsistent_downstream_evidence_quarantines_step
test_observability_event_cannot_replace_gate_evidence
test_terminal_annotation_cannot_change_final_state
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
state-machine tests PASS
gate tests PASS
negative safety tests PASS
evidence tests PASS
replay tests PASS
no source mutation
completion record exists
```

---

# 21. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] orchestrator authority boundary is defined
[ ] dependency gates are defined
[ ] run admission schema is defined
[ ] state machine is defined
[ ] schema contracts are defined
[ ] role permission matrix is defined
[ ] integration boundaries are defined
[ ] Tool / MCP Adapter dependency is defined
[ ] Policy / Capability Registry dependency is defined
[ ] Security Sandbox dependency is defined
[ ] Governed Patch Execution dependency is defined
[ ] Model Adapter dependency is defined
[ ] Prompt Contract dependency is defined
[ ] Human Approval dependency is defined
[ ] Promotion Gate dependency is defined
[ ] evidence paths are defined
[ ] evidence hashing is defined
[ ] replay/idempotency/locking rules are defined
[ ] approved plan hash and authority snapshot rules are defined
[ ] side-effect declaration and dispatch verification rules are defined
[ ] evidence quarantine rule is defined
[ ] no-direct-mutation rule is defined
```

---

# 22. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] state transitions are enforced
[ ] terminal-state immutability is enforced
[ ] gates are enforced
[ ] tool calls go through Tool Adapter
[ ] model calls go through Model Adapter
[ ] patch requests go through Governed Patch Execution
[ ] human approval cannot be self-granted
[ ] promotion cannot be self-granted
[ ] evidence records are written
[ ] evidence hashes are written
[ ] replay is side-effect free
[ ] approved plan hash is enforced before live dispatch
[ ] authority snapshot is enforced before live dispatch
[ ] dispatch claim verification is enforced
[ ] inconsistent downstream evidence is quarantined
[ ] no source mutation occurs directly in this layer
[ ] completion record exists
```

---

# 23. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  schema_version: "1.0"
  schema_id: "orchestrator_completion_record.schema.json"
  component_id: "AGENTX_SELF_EVOLUTION_ORCHESTRATOR"
  component_name: "Self-Evolution Orchestrator"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  review_document_id: "SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT"
  review_document_version: "v4.0"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  run_admission_verified: []
  state_machine_transitions_verified: []
  terminal_state_immutability_verified: []
  gate_checks_verified: []
  tool_adapter_integration_verified: []
  model_adapter_integration_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  patch_integration_verified: []
  human_approval_integration_verified: []
  promotion_gate_integration_verified: []
  failure_recovery_verified: []
  locking_idempotency_replay_verified: []
  authority_snapshot_verified: []
  approved_plan_hash_verified: []
  dispatch_claim_verification_verified: []
  side_effect_declaration_verified: []
  evidence_quarantine_verified: []
  evidence_refs: []
  evidence_hashes: []
  deviations_from_contract: []
  unresolved_risks: []
  final_decision: "DONE|NOT_DONE"
```

A final `DONE` decision is invalid if:

```text
reviewed commit is missing
compileall was not run
pytest was not run
schema validation was not run
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any BLOCKER remains
```

---

# 24. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded.

```yaml
deviations:
  - id: "DEV-001"
    area: "Dependency|Runtime Artifact|Schema|Evidence|Integration|Other"
    description: "what differs from the contract"
    reason: "why accepted"
    safety_impact: "none|low|medium|high|critical"
    compensating_control: "test/evidence/control"
    accepted_status: "NOT_APPLICABLE|DEFERRED_SAFELY|NON_BLOCKING_FOLLOWUP"
    reviewer_decision: "ACCEPTED|REJECTED"
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Runtime artifacts outside `.agentx-init/orchestrator/` require a deviation entry.
Deferred dependencies require a deviation entry and safe restricted behavior.
```

---

# 25. Residual Risks

```yaml
residual_risks:
  - id: "ORCH-RISK-001"
    description: "The orchestrator could become a bypass around controlled tool execution."
    severity: "critical"
    mitigation: "All tool calls must go through Tool / MCP Adapter; tests must prove no direct wrapper execution."
  - id: "ORCH-RISK-002"
    description: "The orchestrator could directly mutate source files."
    severity: "critical"
    mitigation: "No direct source write APIs; source mutation only through Governed Patch Execution."
  - id: "ORCH-RISK-003"
    description: "The orchestrator could continue after a blocked gate."
    severity: "critical"
    mitigation: "Strictest-authority-wins rule; NOT_CHECKED and BLOCK gates prevent dispatch."
  - id: "ORCH-RISK-004"
    description: "The orchestrator could enter an unbounded retry loop."
    severity: "high"
    mitigation: "FailureRecoveryBinding enforces retry_count and max_retries."
  - id: "ORCH-RISK-005"
    description: "Model calls could bypass prompt/version contracts."
    severity: "high"
    mitigation: "ModelCallBinding requires prompt_contract_id and prompt_version_id."
  - id: "ORCH-RISK-006"
    description: "Completion could be claimed without sufficient evidence."
    severity: "high"
    mitigation: "Completion requires admission, task, step, gate, validation, ledger, hashes, and completion evidence."
  - id: "ORCH-RISK-007"
    description: "Repeated dispatch could duplicate an unsafe external action."
    severity: "high"
    mitigation: "Every dispatchable step requires an idempotency key and dispatch history check."
  - id: "ORCH-RISK-008"
    description: "A model output could inject instructions that override governance."
    severity: "high"
    mitigation: "Model output is treated as data until validated against prompt/output contracts and policy gates."
```

---

# 26. Definition of Done

The Self-Evolution Orchestrator is done when it can coordinate a governed self-evolution run without bypassing controlled Agent_X layers.

It must prove:

```text
run admission validates against schema
orchestration state validates against schema
task plan validates against schema
execution steps validate against schema
tool call bindings require Tool / MCP Adapter
model call bindings require Model Adapter and Prompt Contract
human approval bindings cannot self-approve
governance gates block when not checked
promotion gate cannot be bypassed
failure recovery enforces retry limits
run ledger is append-only
ledger hashes are written
evidence is written for every decision
evidence manifest is written
evidence hashes are written
state transitions are valid
terminal states are immutable
replay is side-effect free
completion requires required evidence
cross-layer evidence refs are present and replay-verifiable
dispatch receipts are present for delegated actions
contract compatibility is checked before live dispatch
authority snapshot is recorded and hash-pinned before live dispatch
approved plan hash is required before live dispatch
plan revisions create new plan_version and plan_hash
side-effect declarations are checked against downstream results
dispatch request/acceptance/completion/evidence statuses are distinguished
inconsistent evidence is quarantined and cannot be rewritten
human interrupt/cancellation is honored
partial/degraded completion requires accepted non-safety deviation
no source mutation occurs directly in this layer
no raw shell executes
no patch application occurs directly in this layer
no Git write occurs directly in this layer
no network is enabled by default
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_self_evolution_orchestrator_schemas.py
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

# 27. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
invalid state transition is allowed
terminal state can become active without new run_id
orchestrator directly writes source
orchestrator directly applies patch
orchestrator directly executes shell
orchestrator directly performs Git write
orchestrator directly calls model runtime
orchestrator bypasses Tool / MCP Adapter
orchestrator bypasses Policy / Capability Registry
orchestrator bypasses Security Sandbox
orchestrator bypasses Governed Patch Execution
orchestrator bypasses Model Adapter
orchestrator bypasses Prompt Contract / Prompt Versioning
orchestrator self-approves human approval
orchestrator self-promotes release
blocked gate can proceed
NOT_CHECKED gate can proceed
retry limit can be exceeded
duplicate idempotency key can dispatch duplicate action
replay mode dispatches side effects
completion can be claimed without evidence
cross-layer evidence reference is missing for required delegated action
dispatch receipt is missing before step success
incompatible required contract is allowed in live mode
human interrupt is ignored
authority snapshot is missing before live dispatch
approved plan hash is missing before live dispatch
executed step references superseded plan_hash
ledger sequence or previous hash is invalid
downstream result exceeds declared side-effect set
inconsistent evidence is not quarantined
observability event replaces authority evidence
partial/degraded result is treated as full success without accepted deviation
evidence is missing
evidence hashes are missing
completion record is missing
```

---

# 28. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Self-Evolution Orchestrator.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional fields or non-safety clarifications
MAJOR: changed authority model, changed gate behavior, changed role permissions, changed default safety behavior, new direct execution capability
```

Blocked without major revision:

```text
allowing direct source mutation
allowing direct patch application
allowing raw shell execution
allowing Git write directly from orchestrator
allowing policy bypass
allowing sandbox bypass
allowing human approval bypass
allowing promotion bypass
allowing model calls outside Model Adapter
allowing prompt calls outside Prompt Contract / Prompt Versioning
removing evidence logging
removing evidence hashing
removing retry limits
allowing completion without evidence
allowing replay mode to dispatch side effects
```

The next document should be:

```text
SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC.md
```

---

# 29. Final Rating

This v4 controlling contract is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 structure and closes the remaining production-control gaps: approved plan hashing, authority snapshots, run-mode escalation limits, causal ledger ordering, side-effect declarations, dispatch claim verification, evidence quarantine, evidence hash closure, observability/authority separation, and stricter completion/no-go rules. The contract now defines what the orchestrator may coordinate, what it must not directly do, how every run is admitted, gated, dispatched, evidenced, replayed, interrupted, quarantined, completed, and reviewed.
```
