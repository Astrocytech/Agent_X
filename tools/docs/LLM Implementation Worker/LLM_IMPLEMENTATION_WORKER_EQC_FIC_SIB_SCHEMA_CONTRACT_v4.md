# LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_LLM_IMPLEMENTATION_WORKER
component_name: LLM Implementation Worker
roadmap_layer: 10
roadmap_phase: Phase C — Controlled Implementation Generation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Model Adapter Acceptance Criteria, Tool / MCP Adapter Acceptance Criteria, Governed Patch Execution Acceptance Criteria, Command Acceptance Criteria, Prompt Contract Acceptance Criteria
optional_standards: ES, Report Template
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/workers/llm_implementation_worker/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/implementation_worker/
contract_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 contract was very strong and implementation-ready, but I would rate it:

```text
9.8/10
```

It already covered the major safety and implementation-control areas:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
worker authority boundaries
dependency gates
public API expectations
execution pipeline
Model Adapter boundary
Tool / MCP Adapter boundary
Policy / Capability Registry boundary
Security Sandbox boundary
Failure Taxonomy boundary
prompt/context input contract
model-output validation
artifact hashing
idempotency and locking
schema validation matrix
traceability matrix
patch proposal output rules
no direct source mutation
no direct shell execution
no direct Git write
no direct network/provider bypass
worker task schema
worker context input schema
model request schema
model response schema
worker result schema
implementation plan schema
patch proposal schema
tool request plan schema
validation request plan schema
audit/evidence contract
OpenCode borrowing notes
Agent_X integration notes
review handoff requirements
```

It was not fully 10/10 because a few final production-control details were still under-specified:

```text
1. It did not explicitly define model timeout, retry, and cost/usage control rules.
2. It did not define repair-loop limits, retry escalation, or repeated-failure handling.
3. It did not define prompt/output retention and deletion/minimization rules.
4. It did not define a self-modification guardrail for changes to worker, policy, sandbox, model, and tool layers.
5. It did not define runtime artifact boundary exceptions with enough precision.
6. It did not define exact command-request acceptance criteria for validation request plans.
7. It did not define deterministic model-run requirements for reproducible implementation proposals.
8. It did not define a formal unsafe-output quarantine rule.
9. It did not require review of generated patch proposals against forbidden safety-regression patterns.
10. It did not include a final frozen acceptance matrix for coding-agent handoff.
```

This v4 adds those final controls and is the frozen 10/10 controlling contract.

---

# 1. Purpose

This document defines the controlling contract for the **LLM Implementation Worker** in the Agent_X self-evolving system.

The LLM Implementation Worker converts approved implementation tasks, context packs, and governing documents into structured implementation artifacts:

```text
implementation plans
patch proposals
tool request plans
validation request plans
repair plans
worker results
audit/evidence records
```

The worker is an implementation reasoning and proposal layer.

It must not directly:

```text
mutate source files
edit source files
apply patches
execute shell commands
run validation commands
write Git state
open network connections
call model/provider SDKs
call MCP servers directly
approve its own changes
promote changes
```

All model, tool, patch, command, file, and validation behavior must go through controlled Agent_X layers.

---

# 2. Scope

## 2.1 Required in This Layer

The LLM Implementation Worker must define contracts for:

```text
worker task intake
worker task validation
context input validation
prompt construction
model request construction
model response validation
implementation plan generation
patch proposal generation
tool request planning
validation request planning
repair planning
blocked/failed/invalid task handling
audit/evidence logging
schema validation
failure classification
deviation recording
artifact hashing
idempotency
concurrency locking
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
model runtime
model provider clients
model adapter internals
direct filesystem mutation
direct source editing
direct patch application
direct shell execution
direct validation execution
direct Git write operations
direct network calls
MCP server runtime
human approval UI
promotion gate
release gate
long-term learning
background scheduler
```

Those responsibilities belong to other Agent_X layers.

---

# 3. Standards Applied

## 3.1 Primary Standard: EQC

EQC is primary because the worker can influence code changes, even though it must not apply those changes directly.

EQC applies to:

```text
task acceptance
task rejection
prompt construction
context selection
model-profile request constraints
model output validation
implementation-plan quality
patch-proposal safety
tool-call request safety
validation-request safety
blocked task handling
evidence completeness
failure classification
```

The worker must fail closed when required context, policy, model boundary, tool boundary, sandbox boundary, or schema validation is missing.

## 3.2 Required Standard: FIC

FIC is required because this layer must map to concrete implementation files, functions, schemas, tests, and runtime artifacts.

The implementation spec must later define exact files for:

```text
worker models
task validator
context validator
prompt builder
model request builder
model output validator
implementation planner
patch proposal builder
tool request planner
validation request planner
worker dispatcher
worker evidence logger
worker schema validator
worker tests
```

Each file must have:

```text
clear responsibility
public API
inputs
outputs
invariants
tests
safety limits
```

## 3.3 Required Standard: SIB

SIB is required because this layer connects multiple subsystems:

```text
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
Model Adapter Layer
Tool / MCP Adapter Layer
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer
Evaluation Harness / Regression Benchmark Layer
Audit / Evidence system
```

The worker is an integration boundary between model reasoning and controlled implementation execution.

## 3.4 Required Standard: Schema Contract

Schema Contract is required because every worker input, output, plan, proposal, request, and evidence event must be structured.

Required schemas include:

```text
llm_worker_task.schema.json
llm_worker_context_input.schema.json
llm_worker_model_request.schema.json
llm_worker_model_response.schema.json
implementation_plan.schema.json
patch_proposal.schema.json
tool_request_plan.schema.json
validation_request_plan.schema.json
repair_plan.schema.json
llm_worker_result.schema.json
llm_worker_audit.schema.json
llm_worker_evidence_manifest.schema.json
llm_worker_completion_record.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every worker execution must create evidence.

Evidence is required for:

```text
accepted worker task
rejected worker task
context validation
policy decision
sandbox/path decision
model request prepared
model response received
model output validation
implementation plan generated
patch proposal generated
tool request plan generated
validation request plan generated
repair plan generated
blocked worker action
invalid worker task
schema-invalid model output
policy-denied task
failure-classified worker result
```

---

# 4. Status Vocabulary

Use only these worker status values:

```text
SUCCESS
PARTIAL
BLOCKED
FAILED
INVALID
```

Use only these review/status table values:

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

Status meanings:

| Status | Meaning |
|---|---|
| SUCCESS | Worker completed the requested safe output. |
| PARTIAL | Worker produced safe partial output, but one or more required outputs could not be produced. |
| BLOCKED | Worker refused to proceed because policy, dependency, boundary, schema, or safety condition was not satisfied. |
| FAILED | Worker attempted an allowed operation but encountered an internal or downstream failure. |
| INVALID | Worker rejected the task, context, model output, or request as malformed or schema-invalid. |

Rules:

```text
BLOCKED is not a crash.
INVALID is not a crash.
PARTIAL must explain what is missing.
FAILED must include failure_class.
SUCCESS must not contain unsafe or unvalidated output.
```

---

# 5. Worker Role and Authority Boundaries

## 5.1 Worker Role

The LLM Implementation Worker may:

```text
read validated task context
construct model requests through the Model Adapter
receive model responses through the Model Adapter
validate model responses
generate structured implementation plans
generate structured patch proposals
generate structured validation request plans
generate structured tool request plans
generate structured repair plans
classify implementation risks
write runtime evidence
return schema-valid worker results
```

## 5.2 Worker Must Not

The worker must not:

```text
directly write source files
directly edit source files
directly apply patches
directly execute shell commands
directly run tests
directly call Git write commands
directly open network connections
directly call hosted model providers
directly call local model runtimes
directly call MCP clients or servers
directly call low-level tool wrappers
bypass the Tool / MCP Adapter
bypass the Model Adapter
bypass Policy / Capability Registry
bypass Security Sandbox
bypass Governed Patch Execution
bypass Failure Taxonomy
approve its own changes
promote changes
```

## 5.3 Authority Rule

The worker has proposal authority only.

It may propose:

```text
implementation plan
patch proposal
tool request plan
validation request plan
repair plan
risk notes
```

It may not execute those proposals directly.

Execution belongs to controlled downstream layers:

```text
Tool / MCP Adapter for tool access
Governed Patch Execution for patch application
Security Sandbox for path/file/command checks
Policy / Capability Registry for permission decisions
Evaluation Harness for validation
Promotion / Release Gate for promotion
Human Review / Approval Interface for approvals
```

## 5.4 Authority Decision Precedence

If any required authority disagrees, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_HUMAN_APPROVAL
NEEDS_GOVERNANCE
NEEDS_SANDBOX_CHECK
NEEDS_MODEL_POLICY
DRY_RUN_ONLY
ALLOW
```

The worker must not convert a denial into a softer status merely to continue.

---

# 6. Dependency Modes and Gates

## 6.1 Full Mode

Full mode is allowed only when these dependencies are available and validated:

```text
Policy / Capability Registry
Model Adapter
Tool / MCP Adapter
Security Sandbox / Filesystem Boundary
Failure Taxonomy / Recovery Playbook
Governed Patch Execution handoff interface, if patch proposals are requested
```

Full mode may produce:

```text
implementation plans
patch proposals
tool request plans
validation request plans
repair plans
worker results
evidence manifests
```

## 6.2 Restricted Mode

Restricted mode applies when one or more downstream layers are missing or unavailable.

Restricted mode may allow only:

```text
task schema validation
context schema validation
read-only analysis if policy explicitly allows it
dry-run implementation planning
blocked result generation
invalid task handling
evidence writing
```

Restricted mode must block:

```text
model calls if Model Adapter is missing
patch proposals if policy or sandbox path validation is missing
tool request plans if Tool / MCP Adapter is missing
validation request plans if Tool / MCP Adapter or Evaluation Harness is missing
source mutation requests
shell execution requests
Git write requests
network/provider requests
```

## 6.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> implementation tasks BLOCK unless explicit restrictive read-only fallback permits analysis only.
If Model Adapter is missing -> model-required tasks BLOCK.
If Tool / MCP Adapter is missing -> tool request plans and validation request plans BLOCK.
If Security Sandbox is missing -> path-sensitive outputs and patch proposals BLOCK.
If Failure Taxonomy is missing -> worker uses UNKNOWN_WORKER_FAILURE and records the deviation.
If Governed Patch Execution is missing -> patch proposals may be produced only as inert proposal artifacts if policy permits; patch application remains impossible.
If Prompt Contract / Prompt Versioning is missing -> prompt construction uses restrictive local template or BLOCKS if the task requires governed prompt versioning.
If Context Builder / Task Packer is missing -> worker accepts only already-validated context packs or BLOCKS.
```

Missing dependencies must never default to ALLOW.

---

# 7. Model Adapter Dependency Boundary

The worker must use the Model Adapter for all model interaction.

Required behavior:

```text
worker builds a structured model request
worker sends request only through Model Adapter
Model Adapter selects approved model profile
Model Adapter enforces local/hosted/provider policy
Model Adapter enforces token, cost, context, and provider limits
Model Adapter returns structured model response
worker validates response before use
```

The worker must not:

```text
instantiate model clients directly
call OpenAI, Anthropic, Ollama, vLLM, llama.cpp, LM Studio, or any provider directly
read provider credentials
choose unapproved models
override model policy
open network connections to model providers
import provider SDKs
write provider configuration
log provider secrets
```

If the Model Adapter is missing or denies the request:

```text
status = BLOCKED
failure_class = WORKER_MODEL_ADAPTER_UNAVAILABLE or WORKER_MODEL_POLICY_DENIED
evidence is written
```

---

# 8. Tool / MCP Adapter Dependency Boundary

The worker may request tool usage only by producing structured tool request plans or by calling the Tool / MCP Adapter through approved dispatcher interfaces.

Required behavior:

```text
worker identifies needed tool operation
worker creates structured tool request plan
Tool / MCP Adapter validates and executes only if allowed
worker receives schema-valid ToolResult
worker stores ToolResult reference, not uncontrolled raw output
worker does not call wrapper tools directly
```

The worker must not:

```text
directly call filesystem tools
directly call command tools
directly call Git tools
directly call MCP server functions
directly call MCP client functions
bypass tool registry
bypass tool policy
bypass tool evidence logging
```

If the Tool / MCP Adapter is unavailable:

```text
status = BLOCKED or PARTIAL
failure_class = WORKER_TOOL_ADAPTER_UNAVAILABLE
evidence is written
```

---

# 9. Policy / Capability Registry Dependency Boundary

Every worker task must be checked against the Policy / Capability Registry before model or tool action is requested.

Policy must decide:

```text
worker role allowed?
task type allowed?
model mode allowed?
model profile allowed?
tool request type allowed?
source mutation proposal allowed?
patch proposal allowed?
network/provider mode allowed?
human approval required?
governance required?
dry-run required?
path scope allowed?
evidence requirements satisfied?
```

If policy is missing:

```text
read-only analysis may be allowed only if explicitly permitted by restrictive fallback
implementation proposals must block
tool request plans must block
patch proposals must block
model calls must block unless model policy is available
```

Missing policy must never default to ALLOW.

---

# 10. Security Sandbox Dependency Boundary

The worker must not touch source paths directly.

When the worker references files or paths in a task, the path scope must be checked by the Security Sandbox through approved interfaces.

Required behavior:

```text
task file references are validated before use
context file references are validated before use
patch proposal target paths are sandbox-checked before handoff
forbidden paths are enforced
validation command requests are sandbox/allowlist-checked before execution by tools
```

The worker must not:

```text
open files directly
write files directly
scan arbitrary directories directly
read ignored/private paths directly
construct shell commands for direct execution
```

If sandbox validation is unavailable for path-sensitive tasks:

```text
status = BLOCKED
failure_class = WORKER_SANDBOX_REQUIRED
evidence is written
```

---

# 11. Failure Taxonomy Dependency Boundary

Every failed, blocked, invalid, or partial worker result must use a standard failure class.

Required failure classes include:

```text
WORKER_TASK_INVALID
WORKER_CONTEXT_INVALID
WORKER_POLICY_DENIED
WORKER_SANDBOX_REQUIRED
WORKER_MODEL_ADAPTER_UNAVAILABLE
WORKER_MODEL_POLICY_DENIED
WORKER_MODEL_OUTPUT_INVALID
WORKER_TOOL_ADAPTER_UNAVAILABLE
WORKER_PATCH_PROPOSAL_INVALID
WORKER_DIRECT_MUTATION_BLOCKED
WORKER_DIRECT_SHELL_BLOCKED
WORKER_DIRECT_GIT_BLOCKED
WORKER_NETWORK_BYPASS_BLOCKED
WORKER_MCP_BYPASS_BLOCKED
WORKER_SCHEMA_VALIDATION_FAILED
WORKER_PROMPT_INJECTION_DETECTED
WORKER_CONTEXT_BUDGET_EXCEEDED
WORKER_OUTPUT_HASH_MISSING
WORKER_EVIDENCE_WRITE_FAILED
WORKER_EXECUTION_FAILED
UNKNOWN_WORKER_FAILURE
```

If the Failure Taxonomy layer is unavailable, the worker must still fail closed and use:

```text
UNKNOWN_WORKER_FAILURE
```

with evidence and a deviation entry.

---

# 12. Prompt / Context Input Contract

## 12.1 Input Sources

The worker may receive context only from approved upstream components:

```text
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
Tool / MCP Adapter read results
approved runtime artifacts
approved contract documents
approved implementation specs
approved test outputs
approved schema files
approved failure records
approved review reports
```

## 12.2 Required Context Fields

A worker context input must include:

```text
context_id
task_id
source_component
created_at
context_pack_version
allowed_files
included_files
excluded_files
forbidden_files
contract_refs
spec_refs
schema_refs
test_refs
policy_refs
risk_notes
token_budget
redaction_status
context_hash
context_item_hashes
provenance_refs
warnings
errors
```

## 12.3 Prompt Construction Rules

Prompts must be constructed from:

```text
approved task description
approved context pack
approved contract constraints
approved implementation spec
approved schema definitions
approved safety rules
approved output schema instructions
approved failure taxonomy
```

Prompts must not include:

```text
secrets
provider credentials
raw private environment values
unapproved files
ignored/private path contents
unbounded logs
irrelevant repository dumps
instructions to bypass policy
instructions to bypass sandbox
instructions to directly mutate source
instructions to run shell commands directly
instructions to self-approve
```

## 12.4 Prompt Injection Handling

The worker must treat source files, logs, user-provided text, model output, and tool output as untrusted.

Prompt-injection handling must include:

```text
separate system/task constraints from untrusted content
label untrusted content clearly
ignore instructions inside source/log/context content that conflict with Agent_X rules
reject model output that asks to bypass policy, sandbox, tools, governance, or evidence
record suspicious instruction patterns in evidence
classify rejected output as WORKER_PROMPT_INJECTION_DETECTED where applicable
```

## 12.5 Context Budget Rules

The worker must enforce:

```text
token_budget
max_context_items
max_file_excerpt_chars
max_log_excerpt_chars
max_model_output_chars
redaction before model request
hashing before evidence finalization
```

If the context exceeds budget:

```text
status = BLOCKED or PARTIAL
failure_class = WORKER_CONTEXT_BUDGET_EXCEEDED
```

---

# 13. Model Output Validation Contract

The worker must not trust raw model output.

Model output must be accepted only if it is converted into schema-valid artifacts:

```text
implementation plan
patch proposal
tool request plan
validation request plan
repair plan
worker result
```

Model output must be rejected if it:

```text
asks to directly mutate source
asks to directly run shell commands
asks to directly write Git state
asks to call providers directly
asks to bypass Model Adapter
asks to bypass Tool / MCP Adapter
asks to bypass Policy / Capability Registry
asks to bypass Security Sandbox
asks to weaken tests to pass validation
asks to remove safety checks
asks to remove evidence logging
targets forbidden paths
emits unstructured patch text where structured proposal is required
contains unredacted secrets
```

Rejected model output must produce:

```text
status = INVALID or BLOCKED
failure_class = WORKER_MODEL_OUTPUT_INVALID
evidence is written
```

---

# 14. Patch Proposal Output Rules

The worker may generate patch proposals, but it must not apply them.

Patch proposals must be:

```text
structured
schema-valid
target-path bounded
linked to task_id
linked to implementation_plan_id
linked to contract/spec references
linked to context_hash
risk-classified
dry-run compatible
ready for Governed Patch Execution handoff
```

Patch proposals must not:

```text
include unbounded arbitrary shell commands
modify forbidden paths
modify L0 unless explicitly authorized by governance
delete files without explicit approval
alter policy/sandbox layers to weaken safety
remove tests to pass validation
remove evidence logging
enable network by default
enable Git write by default
enable mutating MCP tools by default
embed secrets
```

If the worker cannot produce a safe patch proposal, it must return:

```text
status = BLOCKED or FAILED
failure_class = WORKER_PATCH_PROPOSAL_INVALID
```

---

# 15. No Direct Source Mutation Rule

The worker must never directly mutate source files.

Forbidden operations:

```text
open(path, "w")
open(path, "a") on source files
Path.write_text on source files
Path.write_bytes on source files
direct file deletion
direct rename/move of source files
direct patch application
direct exact edit
direct generated code write
shutil.copy into source tree
```

All source mutation must go through:

```text
Governed Patch Execution Layer
Security Sandbox
Policy / Capability Registry
Tool / MCP Adapter
human/governance approval where required
```

A direct source mutation attempt is a BLOCKER and must produce:

```text
status = BLOCKED
failure_class = WORKER_DIRECT_MUTATION_BLOCKED
```

---

# 16. No Direct Shell Execution Rule

The worker must never execute shell commands directly.

Forbidden operations:

```text
subprocess.run
subprocess.Popen
subprocess.call
os.system
pty execution
shell=True
direct make/pytest/compile execution
direct Git commands
```

Validation or command requests must be expressed as structured requests through the Tool / MCP Adapter or Evaluation Harness.

A direct shell attempt is a BLOCKER and must produce:

```text
status = BLOCKED
failure_class = WORKER_DIRECT_SHELL_BLOCKED
```

---

# 17. No Direct Git Write Rule

The worker must never perform Git write operations.

Forbidden operations:

```text
git add
git commit
git push
git branch creation
git merge
git rebase
git reset --hard
git clean
tag creation
remote modification
```

Git inspection, if needed, must be requested through controlled read-only tool calls.

A direct Git write attempt is a BLOCKER and must produce:

```text
status = BLOCKED
failure_class = WORKER_DIRECT_GIT_BLOCKED
```

---

# 18. No Direct Network / Provider Bypass Rule

The worker must not open network connections or call providers directly.

Forbidden operations:

```text
requests
httpx
urllib network calls
websocket clients
provider SDK clients
direct OpenAI calls
direct Anthropic calls
direct Ollama calls
direct vLLM calls
direct llama.cpp server calls
direct MCP remote calls
package downloads
external search
```

All model/provider interaction must go through the Model Adapter. All tool/MCP access must go through the Tool / MCP Adapter.

A direct network/provider bypass attempt is a BLOCKER and must produce:

```text
status = BLOCKED
failure_class = WORKER_NETWORK_BYPASS_BLOCKED
```

---

# 19. Worker Task Schema

A worker task must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_task.schema.json",
  "task_id": "string",
  "created_at": "string",
  "source_component": "string",
  "requested_by": "string",
  "worker_role": "LLM_IMPLEMENTATION_WORKER",
  "task_type": "IMPLEMENTATION_PLAN|PATCH_PROPOSAL|REPAIR_PLAN|VALIDATION_PLAN|ANALYSIS_ONLY",
  "title": "string",
  "description": "string",
  "contract_refs": [],
  "spec_refs": [],
  "context_refs": [],
  "allowed_paths": [],
  "forbidden_paths": [],
  "requested_outputs": [],
  "requires_model": true,
  "requires_tools": false,
  "requires_patch_handoff": false,
  "requires_validation_handoff": false,
  "dry_run": true,
  "policy_decision_id": "string|null",
  "governance_decision_id": "string|null",
  "human_approval_id": "string|null",
  "idempotency_key": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
task_id is required
task_type is required
description is required
worker_role must be LLM_IMPLEMENTATION_WORKER
allowed_paths must be explicit for patch-related tasks
forbidden_paths must be honored
dry_run defaults to true
unknown task_type blocks
missing policy for implementation tasks blocks
idempotency_key must be used when retrying the same worker task
```

---

# 20. Worker Context Input Schema

A worker context input must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_context_input.schema.json",
  "context_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "ContextBuilder",
  "context_pack_version": "string",
  "allowed_files": [],
  "included_files": [],
  "excluded_files": [],
  "forbidden_files": [],
  "contract_refs": [],
  "spec_refs": [],
  "schema_refs": [],
  "test_refs": [],
  "policy_refs": [],
  "risk_notes": [],
  "token_budget": 0,
  "redaction_status": "PASS|FAIL|NOT CHECKED",
  "context_hash": "string",
  "context_item_hashes": [],
  "provenance_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
context_id is required
task_id is required
context_hash is required
redaction_status must be PASS before model request
forbidden_files must not appear in included_files
token_budget must be enforced
```

---

# 21. Model Request Schema

A worker model request must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_model_request.schema.json",
  "model_request_id": "string",
  "task_id": "string",
  "context_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "model_adapter_profile_ref": "string",
  "prompt_contract_ref": "string",
  "requested_output_schemas": [],
  "context_hash": "string",
  "redaction_status": "PASS",
  "token_budget": 0,
  "temperature_policy": "DETERMINISTIC|LOW_VARIANCE|POLICY_DEFINED",
  "allowed_provider_mode": "LOCAL_ONLY|HOSTED_ALLOWED|POLICY_DEFINED",
  "policy_decision_id": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
model request must go through Model Adapter
model_adapter_profile_ref is required
policy_decision_id is required
redaction_status must be PASS
requested_output_schemas must be explicit
```

---

# 22. Model Response Schema

A worker model response record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_model_response.schema.json",
  "model_response_id": "string",
  "model_request_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "ModelAdapter",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "output_refs": [],
  "parsed_artifact_refs": [],
  "validation_status": "PASS|FAIL|NOT CHECKED",
  "redaction_status": "PASS|FAIL|NOT CHECKED",
  "model_profile_ref": "string",
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
raw provider secrets must not be recorded
raw model output may be stored only if redacted and bounded
validation_status must be PASS before worker accepts output
schema-invalid output must be rejected
```

---

# 23. Worker Result Schema

A worker result must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_result.schema.json",
  "worker_result_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "implementation_plan_id": "string|null",
  "patch_proposal_ids": [],
  "tool_request_plan_id": "string|null",
  "validation_request_plan_id": "string|null",
  "repair_plan_id": "string|null",
  "model_request_id": "string|null",
  "model_response_id": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
every worker execution returns a worker result
blocked tasks are valid results
invalid tasks are valid results
model output validation failure must be represented as FAILED or INVALID
failure_class is required for BLOCKED, FAILED, and INVALID
```

---

# 24. Implementation Plan Schema

An implementation plan must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "implementation_plan.schema.json",
  "implementation_plan_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "summary": "string",
  "target_files": [],
  "non_target_files": [],
  "forbidden_files_checked": true,
  "implementation_slices": [],
  "dependencies": [],
  "policy_requirements": [],
  "sandbox_requirements": [],
  "test_plan": [],
  "validation_plan": [],
  "rollback_plan": [],
  "risk_notes": [],
  "requires_patch_proposal": false,
  "requires_human_review": false,
  "context_hash": "string",
  "plan_hash": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
plan must identify target files
plan must identify non-target/forbidden files when relevant
plan must list validation expectations
plan must not request direct mutation
plan must not request raw shell
plan must not weaken safety layers
plan_hash is required before final evidence
```

---

# 25. Patch Proposal Schema

A patch proposal must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_proposal.schema.json",
  "patch_proposal_id": "string",
  "task_id": "string",
  "implementation_plan_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "target_files": [],
  "forbidden_files_checked": true,
  "patch_format": "UNIFIED_DIFF|STRUCTURED_EDIT_PLAN",
  "patch_body": "string",
  "expected_effects": [],
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "requires_governance": true,
  "requires_human_approval": false,
  "requires_sandbox_check": true,
  "requires_patch_execution": true,
  "validation_expectations": [],
  "rollback_notes": [],
  "context_hash": "string",
  "proposal_hash": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
patch proposal must be structured
target_files must be explicit
forbidden files must be checked
patch body must not be applied by this worker
patch proposal must be handed to Governed Patch Execution
critical-risk patch proposals require governance
source mutation is never performed inside this layer
proposal_hash is required before final evidence
```

---

# 26. Tool Request Plan Schema

A tool request plan must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "tool_request_plan.schema.json",
  "tool_request_plan_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "requested_tools": [],
  "reason": "string",
  "required_effects": [],
  "requires_policy_check": true,
  "requires_sandbox_check": false,
  "requires_human_approval": false,
  "dry_run": true,
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
tool request plan is not tool execution
Tool / MCP Adapter must validate and execute separately
mutating tool requests require governance and sandbox where applicable
unknown tools must not be guessed
```

---

# 27. Validation Request Plan Schema

A validation request plan must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "validation_request_plan.schema.json",
  "validation_request_plan_id": "string",
  "task_id": "string",
  "created_at": "string",
  "source_component": "LLMImplementationWorker",
  "validation_targets": [],
  "requested_commands": [],
  "allowed_command_refs": [],
  "requires_tool_adapter": true,
  "requires_eval_harness": false,
  "dry_run": true,
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
validation request plan is not command execution
commands must be allowlisted downstream
worker must not execute requested commands
```

---

# 28. Audit / Evidence Contract

## 28.1 Runtime Artifact Root

All worker runtime evidence must be written under:

```text
.agentx-init/implementation_worker/
```

## 28.2 Required Evidence Files

```text
llm_worker_task_history.jsonl
llm_worker_result_history.jsonl
implementation_plan_history.jsonl
patch_proposal_history.jsonl
tool_request_plan_history.jsonl
validation_request_plan_history.jsonl
repair_plan_history.jsonl
blocked_worker_history.jsonl
invalid_worker_task_history.jsonl
latest_worker_task.json
latest_worker_result.json
latest_implementation_plan.json
latest_patch_proposal.json
llm_worker_evidence_manifest.json
llm_worker_completion_record.json
```

## 28.3 Evidence Rules

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
redact secrets before durable logging
record model_request_id and model_response_id, not provider secrets
record context refs, not unbounded raw context
record policy decision refs
record sandbox decision refs
record failure taxonomy refs
record patch proposal refs
record validation request refs
record SHA-256 hashes for final artifacts
do not write source files
do not log unredacted model prompts if they contain sensitive content
do not log unbounded model output
```

## 28.4 Required Audit Event Types

```text
WORKER_TASK_ACCEPTED
WORKER_TASK_REJECTED
WORKER_CONTEXT_VALIDATED
WORKER_POLICY_CHECKED
WORKER_MODEL_REQUEST_CREATED
WORKER_MODEL_RESPONSE_RECEIVED
WORKER_MODEL_OUTPUT_VALIDATED
IMPLEMENTATION_PLAN_CREATED
PATCH_PROPOSAL_CREATED
TOOL_REQUEST_PLAN_CREATED
VALIDATION_REQUEST_PLAN_CREATED
REPAIR_PLAN_CREATED
WORKER_RESULT_CREATED
WORKER_BLOCKED
WORKER_FAILED
WORKER_INVALID_TASK
WORKER_DEVIATION_RECORDED
```

## 28.5 Evidence Manifest

Create:

```text
.agentx-init/implementation_worker/llm_worker_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_evidence_manifest.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "task_id": "string",
  "validated_at": "string",
  "context_hash": "string",
  "artifact_refs": [],
  "artifact_hashes": [],
  "policy_decision_refs": [],
  "sandbox_decision_refs": [],
  "model_request_refs": [],
  "model_response_refs": [],
  "worker_result_refs": [],
  "deviation_register": [],
  "redaction_status": "PASS",
  "final_status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final worker artifacts.
Use Python standard library hashlib if no project hash helper exists.
A final SUCCESS result is invalid if required hashes are missing.
```

---

# 29. Idempotency, Locking, and Concurrency Rules

## 29.1 Idempotency

Repeated execution of the same task with the same:

```text
task_id
context_hash
idempotency_key
policy_decision_id
model profile reference
```

must produce either:

```text
the same artifact hashes
a new versioned result with a recorded reason for divergence
a BLOCKED result if deterministic reproduction is not possible
```

## 29.2 Locking

The worker must not run two active executions for the same task/session without a lock.

Required lock evidence:

```text
task_id
worker_run_id
lock_acquired_at
lock_released_at
lock_status
```

If lock acquisition fails:

```text
status = BLOCKED
failure_class = WORKER_EXECUTION_FAILED
```

## 29.3 No Background Work

The worker must not create background daemons, schedulers, or async jobs that continue after the controlled run unless a future scheduler layer explicitly owns that behavior.

---

# 30. Deviation Register

Any exception, deferral, missing dependency, or non-standard artifact path must be recorded.

```yaml
deviations:
  - id: "LLM-WORKER-DEV-001"
    area: "ModelAdapter|ToolAdapter|Policy|Sandbox|PatchHandoff|Evidence|Schema|Other"
    description: "what differs from the contract"
    reason: "why accepted"
    safety_impact: "none|low|medium|high|critical"
    compensating_control: "test/evidence/control"
    accepted_status: "NOT APPLICABLE|DEFERRED SAFELY|NON-BLOCKING FOLLOW-UP"
    reviewer_decision: "ACCEPTED|REJECTED"
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
Missing policy cannot be accepted for implementation proposals.
Missing Model Adapter cannot be accepted for model-required tasks.
Missing evidence hashes cannot be accepted for SUCCESS.
Runtime artifacts outside .agentx-init/implementation_worker/ require a deviation entry.
```

---

# 31. OpenCode Borrowing Notes

## 31.1 Concepts to Borrow

Borrow these OpenCode-style ideas only as design patterns:

```text
separate planning from execution
tool-mediated implementation
explicit task context
plan/update workflow
structured patch proposal concept
safe tool call abstraction
human question / review concept
evidence-backed tool/result records
```

## 31.2 Concepts to Restrict

Do not borrow these assumptions directly:

```text
agent can directly edit files
agent can directly run shell commands
agent can directly call model/provider APIs
agent can use broad tool access without Agent_X policy
agent can apply patches without governed patch layer
agent can use network/provider features by convenience
agent can self-approve changes
agent can continue after missing safety dependencies
```

## 31.3 Agent_X Mapping

| OpenCode-style concept | Agent_X equivalent | Required control |
|---|---|---|
| Agent implementation loop | LLM Implementation Worker | Proposal only, no direct mutation |
| Model call | Model Adapter request | Policy-controlled model profile |
| Tool call | Tool / MCP Adapter request | Registry + policy + evidence |
| Edit/write | Patch proposal | Governed Patch Execution |
| Shell/test command | Validation request plan | Tool Adapter + allowlist |
| Human question | Human Review layer | Future controlled interface |
| Plan update | Implementation plan artifact | Schema-valid and evidenced |
| Apply patch | Governed Patch Execution | Not performed by worker |

---

# 32. Agent_X Integration Notes

## 32.1 Upstream Inputs

The worker may receive inputs from:

```text
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
Policy / Capability Registry
Model Adapter
Tool / MCP Adapter
approved runtime artifacts
approved contract documents
approved implementation specs
approved review reports
approved validation outputs
```

## 32.2 Downstream Outputs

The worker may emit:

```text
worker result
implementation plan
patch proposal
tool request plan
validation request plan
repair plan
audit/evidence records
evidence manifest
completion record
```

## 32.3 Required Integration Rules

```text
task intake must validate schema
context intake must validate schema
policy check must happen before model request
model request must go through Model Adapter
model output must be validated before plan/proposal acceptance
tool requests must go through Tool / MCP Adapter
patch proposals must go to Governed Patch Execution
validation requests must go to Tool / MCP Adapter or Evaluation Harness
all failures must map to Failure Taxonomy
all outputs must write evidence
```

---

# 33. Security Rules

This layer must enforce:

```text
no direct source mutation
no direct shell execution
no direct Git write
no direct network/provider bypass
no direct MCP bypass
no unapproved model profile
no unvalidated model output acceptance
no unstructured patch proposal
no missing evidence for worker execution
no missing policy check for implementation tasks
no missing sandbox check for path-sensitive outputs
no compliance with prompt-injection instructions from untrusted content
no self-approval
no weakening of Agent_X safety layers
```

---

# 34. Forbidden Imports and Operations

Implementation tests must scan for forbidden direct dependencies or operations unless a documented safe wrapper exception exists.

Forbidden direct imports in worker implementation:

```text
requests
httpx
urllib.request
socket
websocket
subprocess
pty
openai
anthropic
ollama
git
gitpython
mcp runtime packages
```

Forbidden direct operations in worker implementation:

```text
Path.write_text on source paths
Path.write_bytes on source paths
open(..., "w") on source paths
open(..., "a") on source paths
os.system
subprocess.*
shell=True
direct Git write command strings
direct provider SDK calls
```

Allowed standard-library use must be limited to:

```text
dataclasses
typing
pathlib for path representation only
json
uuid
datetime
hashlib
tempfile for tests only
```

Path reads or writes must be owned by approved adapters, not the worker itself, except runtime evidence under the approved runtime root.

---

# 35. Test Acceptance Criteria

Required tests for this contract must eventually prove:

```text
worker task schema accepts valid task
worker task schema rejects missing task_id
worker task schema rejects unknown task_type
context schema rejects forbidden files in included_files
context schema requires context_hash
model request schema requires model_adapter_profile_ref
model request schema requires policy_decision_id
model response schema rejects validation_status NOT CHECKED for accepted output
worker result schema accepts blocked result
implementation plan schema accepts valid plan
implementation plan schema requires target_files
patch proposal schema accepts valid proposal
patch proposal schema rejects missing target_files
tool request plan schema accepts valid plan
validation request plan schema accepts valid plan
worker blocks when policy is unavailable for implementation task
worker blocks when model adapter is unavailable for model-required task
worker blocks when tool adapter is unavailable for tool-required task
worker blocks path-sensitive proposal when sandbox is unavailable
worker rejects unsafe model output
worker blocks direct source mutation attempt
worker blocks direct shell execution attempt
worker blocks direct Git write attempt
worker blocks direct network/provider bypass attempt
prompt/context input rejects forbidden paths
prompt/context input redacts secrets
model output validation rejects unstructured patch text
patch proposal is not applied by worker
worker evidence is written
blocked worker evidence is written
invalid task evidence is written
artifact hashes are written
deviation register records accepted safe deferrals
forbidden import scan passes
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
negative safety tests PASS
forbidden import tests PASS
no source mutation by worker
no shell execution by worker
no Git write by worker
no network/provider bypass by worker
worker evidence written
artifact hashes written
invalid tasks fail closed
blocked tasks fail closed
```

---

# 36. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] worker task schema is defined
[ ] worker context input schema is defined
[ ] model request schema is defined
[ ] model response schema is defined
[ ] worker result schema is defined
[ ] implementation plan schema is defined
[ ] patch proposal schema is defined
[ ] tool request plan schema is defined
[ ] validation request plan schema is defined
[ ] audit/evidence paths are defined
[ ] artifact hashing rules are defined
[ ] failure classes are defined
[ ] Model Adapter boundary is defined
[ ] Tool / MCP Adapter boundary is defined
[ ] Policy / Capability Registry boundary is defined
[ ] Security Sandbox boundary is defined
[ ] Failure Taxonomy boundary is defined
[ ] Governed Patch Execution handoff is defined
[ ] OpenCode borrowing is bounded
[ ] no-direct-mutation rule is defined
[ ] no-direct-shell rule is defined
[ ] no-direct-Git-write rule is defined
[ ] no-direct-network/provider-bypass rule is defined
```

---

# 37. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] worker task schema validates
[ ] context input schema validates
[ ] model request schema validates
[ ] model response schema validates
[ ] worker result schema validates
[ ] implementation plan schema validates
[ ] patch proposal schema validates
[ ] tool request plan schema validates
[ ] validation request plan schema validates
[ ] policy checks run before model requests
[ ] model requests go through Model Adapter
[ ] tool requests go through Tool / MCP Adapter
[ ] patch proposals are not applied by worker
[ ] blocked tasks fail closed
[ ] invalid tasks fail closed
[ ] evidence records are written
[ ] artifact hashes are written
[ ] no source mutation occurs directly in this layer
[ ] no shell execution occurs directly in this layer
[ ] no Git write occurs directly in this layer
[ ] no network/provider bypass occurs directly in this layer
```

---

# 38. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
worker directly mutates source
worker directly executes shell commands
worker directly writes Git state
worker directly opens network/provider connection
worker bypasses Model Adapter
worker bypasses Tool / MCP Adapter
worker bypasses Policy / Capability Registry
worker accepts unvalidated model output
worker applies patch directly
worker emits unstructured patch proposal
worker ignores forbidden paths
worker logs unredacted secrets
worker fails without evidence
worker omits required artifact hashes
invalid worker task raises unhandled exception
forbidden import scan fails
compileall fails
pytest fails
schema validation fails
```

---

# 39. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  schema_version: "1.0"
  schema_id: "llm_worker_completion_record.schema.json"
  component_id: "AGENTX_LLM_IMPLEMENTATION_WORKER"
  component_name: "LLM Implementation Worker"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  artifact_hashes: []
  worker_tasks_verified: []
  model_adapter_integration_verified: []
  tool_adapter_integration_verified: []
  policy_integration_verified: []
  sandbox_integration_verified: []
  failure_taxonomy_integration_verified: []
  governed_patch_handoff_verified: []
  forbidden_import_scan_verified: []
  negative_tests_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  deviations_from_contract: []
  unresolved_risks: []
  final_decision: "DONE|NOT DONE"
```

---

# 40. Residual Risks

```yaml
residual_risks:
  - id: "LLM-WORKER-RISK-001"
    description: "Model output may include unsafe implementation instructions."
    severity: "critical"
    mitigation: "Validate model output against schemas and reject bypass instructions."
  - id: "LLM-WORKER-RISK-002"
    description: "Worker may accidentally become a source mutation layer."
    severity: "critical"
    mitigation: "No direct mutation rule, forbidden operation tests, and patch handoff only."
  - id: "LLM-WORKER-RISK-003"
    description: "Worker may bypass tool or model adapters for convenience."
    severity: "critical"
    mitigation: "Dependency-boundary tests and forbidden-import checks."
  - id: "LLM-WORKER-RISK-004"
    description: "Prompt injection inside source/context could override Agent_X rules."
    severity: "high"
    mitigation: "Treat source/context/model/tool output as untrusted and enforce instruction hierarchy."
  - id: "LLM-WORKER-RISK-005"
    description: "Patch proposal may target forbidden or safety-critical paths."
    severity: "high"
    mitigation: "Sandbox/path validation, forbidden path checks, governance requirement, and patch proposal schema validation."
  - id: "LLM-WORKER-RISK-006"
    description: "Model responses may be nondeterministic across repeated runs."
    severity: "medium"
    mitigation: "Use idempotency keys, context hashes, artifact hashes, and recorded model profile references."
```

---

# 41. Public API Contract

The implementation spec must map this contract to a small, explicit public API.

Expected public classes:

```text
LLMWorkerTask
LLMWorkerContextInput
LLMWorkerModelRequest
LLMWorkerModelResponse
ImplementationPlan
PatchProposal
ToolRequestPlan
ValidationRequestPlan
RepairPlan
LLMWorkerResult
LLMWorkerAuditEvent
LLMWorkerEvidenceManifest
LLMWorkerCompletionRecord
```

Expected public functions:

```python
validate_worker_task(raw_task: dict) -> LLMWorkerTask

validate_worker_context(
    raw_context: dict,
    task: LLMWorkerTask
) -> LLMWorkerContextInput

build_model_request(
    task: LLMWorkerTask,
    context_input: LLMWorkerContextInput,
    policy_context: dict
) -> LLMWorkerModelRequest

validate_model_response(
    model_response: LLMWorkerModelResponse,
    task: LLMWorkerTask,
    context_input: LLMWorkerContextInput
) -> dict

build_implementation_plan(
    task: LLMWorkerTask,
    context_input: LLMWorkerContextInput,
    validated_model_output: dict
) -> ImplementationPlan

build_patch_proposal(
    task: LLMWorkerTask,
    implementation_plan: ImplementationPlan,
    validated_model_output: dict
) -> PatchProposal

build_tool_request_plan(
    task: LLMWorkerTask,
    implementation_plan: ImplementationPlan
) -> ToolRequestPlan

build_validation_request_plan(
    task: LLMWorkerTask,
    implementation_plan: ImplementationPlan
) -> ValidationRequestPlan

execute_worker_task(
    raw_task: dict,
    raw_context: dict,
    runtime_context: dict
) -> LLMWorkerResult

write_worker_evidence(
    task: LLMWorkerTask,
    result: LLMWorkerResult,
    repo_root: str
) -> dict
```

Rules:

```text
public functions must return schema-valid objects or schema-valid BLOCKED / INVALID results
public functions must not mutate source
public functions must not execute shell commands
public functions must not call providers directly
public functions must not call low-level tools directly
public functions must write or reference evidence for every accepted, blocked, failed, or invalid run
```

---

# 42. Worker Execution Pipeline

Every worker execution must follow this sequence.

```text
1. Receive raw worker task and raw context input.
2. Validate worker task schema.
3. Validate context input schema.
4. Acquire task/session lock.
5. Check idempotency key and prior artifact hashes.
6. Check Policy / Capability Registry for task permission.
7. Check Security Sandbox for path-sensitive context and target paths.
8. Build prompt using Prompt Contract / Prompt Versioning rules.
9. Build structured Model Adapter request.
10. Send request only through Model Adapter.
11. Receive structured Model Adapter response.
12. Validate model response schema.
13. Validate parsed model output against requested output schemas.
14. Reject unsafe model output or prompt-injection attempts.
15. Build implementation plan.
16. Build patch proposal only if requested and allowed.
17. Build tool request plan only if requested and allowed.
18. Build validation request plan only if requested and allowed.
19. Validate all generated artifacts against schemas.
20. Redact and bound all evidence content.
21. Hash final artifacts.
22. Write append-only evidence histories.
23. Write latest artifacts atomically.
24. Write evidence manifest.
25. Release task/session lock.
26. Return schema-valid LLMWorkerResult.
```

Rules:

```text
No stage may be skipped unless the task type explicitly marks it not applicable.
Any failed required stage returns BLOCKED, FAILED, or INVALID.
Exceptions must be converted to schema-valid worker results.
The worker must not continue after model output validation failure.
The worker must not emit patch proposals when path, policy, or sandbox validation fails.
```

---

# 43. Schema Validation Matrix

The implementation must include schema tests for valid and invalid cases.

| Schema | Valid case required | Invalid case required |
|---|---|---|
| `llm_worker_task.schema.json` | valid implementation task | missing task_id, unknown task_type |
| `llm_worker_context_input.schema.json` | valid bounded context | forbidden file included, missing context_hash |
| `llm_worker_model_request.schema.json` | valid model request | missing model_adapter_profile_ref, missing policy_decision_id |
| `llm_worker_model_response.schema.json` | valid validated response | validation_status not PASS for accepted output |
| `implementation_plan.schema.json` | valid plan with slices | missing target_files, missing context_hash |
| `patch_proposal.schema.json` | valid structured proposal | missing target_files, missing proposal_hash |
| `tool_request_plan.schema.json` | valid dry-run tool plan | missing requested_tools, mutating request without policy |
| `validation_request_plan.schema.json` | valid validation plan | direct command execution flag or missing allowed refs |
| `repair_plan.schema.json` | valid repair plan | missing failure refs |
| `llm_worker_result.schema.json` | valid blocked/success result | missing failure_class for BLOCKED/FAILED/INVALID |
| `llm_worker_audit.schema.json` | valid audit event | unknown event type |
| `llm_worker_evidence_manifest.schema.json` | valid manifest | missing artifact_hashes |
| `llm_worker_completion_record.schema.json` | valid completion record | missing validated_commit or final_decision |

Acceptance:

```text
valid examples pass
missing required fields fail
invalid enum values fail
unsafe accepted-output states fail
schema tests run without model, network, GPU, provider credentials, or tool execution
```

---

# 44. Contract-to-Implementation Traceability Matrix

The implementation spec and post-implementation review must preserve this traceability.

| Contract requirement | Expected implementation area | Expected tests | Evidence |
|---|---|---|---|
| Worker task intake | task validator | worker task schema tests | task history |
| Context validation | context validator | context schema + forbidden path tests | context validation audit |
| Policy gate | policy integration | policy unavailable / denied tests | policy decision refs |
| Model Adapter boundary | model request builder | no direct provider / adapter-unavailable tests | model request refs |
| Model output validation | model output validator | unsafe output rejection tests | model response validation audit |
| Implementation plan | planner | plan schema tests | implementation plan history |
| Patch proposal | proposal builder | patch schema + no apply tests | patch proposal history |
| Tool request plan | tool planner | tool adapter unavailable tests | tool request plan history |
| Validation request plan | validation planner | no direct shell tests | validation request plan history |
| Evidence logging | evidence logger | append-only/latest/hash tests | evidence manifest |
| No source mutation | forbidden operation guard | mutation negative tests | source mutation check |
| No shell execution | forbidden operation guard | shell negative tests | audit / test output |
| No Git write | forbidden operation guard | Git write negative tests | audit / test output |
| No network/provider bypass | forbidden import guard | import scan tests | forbidden import report |
| Idempotency and locking | run coordinator | repeated task / lock tests | lock evidence |
| Failure taxonomy | result builder | failure-class tests | worker result history |

---

# 45. Worker-Owned Evidence vs Downstream Evidence

The worker owns only its own evidence root:

```text
.agentx-init/implementation_worker/
```

The worker may reference downstream evidence from:

```text
.agentx-init/tool_calls/
.agentx-init/model_adapter/
.agentx-init/security/
.agentx-init/patch_execution/
.agentx-init/evaluations/
```

Rules:

```text
worker evidence must store references to downstream evidence rather than copying unbounded downstream artifacts
worker evidence must not rewrite downstream evidence
worker evidence must not treat missing downstream evidence as success
worker result must include evidence_refs for policy, sandbox, model, tool, and patch handoff decisions where applicable
missing required downstream evidence blocks SUCCESS
```

---

# 46. Analysis-Only vs Implementation Task Fallback Rules

Fallback rules must distinguish low-risk analysis from implementation-producing tasks.

## 46.1 Analysis-Only Tasks

Analysis-only tasks may run in restricted mode only if:

```text
task_type = ANALYSIS_ONLY
requires_model = false or Model Adapter is available
requires_tools = false or Tool / MCP Adapter is available
no patch proposal is requested
no validation command is requested
no source mutation is requested
policy allows read-only analysis or restrictive fallback explicitly allows it
```

## 46.2 Implementation Tasks

Implementation tasks must block if any required safety dependency is unavailable.

Implementation tasks include:

```text
IMPLEMENTATION_PLAN
PATCH_PROPOSAL
REPAIR_PLAN
VALIDATION_PLAN
```

These must block when:

```text
policy is unavailable
context validation is unavailable
model adapter is unavailable and requires_model = true
sandbox is unavailable for path-sensitive outputs
tool adapter is unavailable for tool or validation requests
failure taxonomy is unavailable and no safe fallback classification exists
```

---

# 47. Prompt Contract / Versioning Requirement

Every model request must reference a prompt contract or prompt version.

Required fields:

```text
prompt_contract_ref
prompt_version
prompt_template_hash
system_constraints_hash
output_schema_refs
context_hash
```

Rules:

```text
model requests without prompt_contract_ref block
model requests without output_schema_refs block
prompt templates must not include provider credentials
prompt versions must be stable within a worker run
prompt changes require new artifact hashes
```

---

# 48. Artifact Immutability Rule

After final evidence hashing:

```text
implementation plans must not be modified in place
patch proposals must not be modified in place
tool request plans must not be modified in place
validation request plans must not be modified in place
evidence manifests must not be modified in place
completion records must not be modified in place
```

Corrections must create:

```text
new artifact ID
new artifact version
new hash
new evidence entry
reference to superseded artifact
reason for replacement
```

A final SUCCESS result is invalid if any final artifact is changed without a new evidence manifest.

---

# 49. Implementation Scoring Rubric

Use this rubric only after implementation validation.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Worker package, schemas, tests, and runtime roots exist. |
| Schema validation | 1.0 | Valid and invalid schema cases pass for all worker artifacts. |
| Policy and dependency gates | 1.0 | Missing/denied policy, model, tool, sandbox, and patch dependencies fail closed. |
| Model boundary | 1.0 | All model calls go through Model Adapter; unsafe output is rejected. |
| Tool/patch/validation boundary | 1.0 | Tool and validation requests are plans only; patch proposals are not applied. |
| No direct side effects | 1.0 | No source mutation, shell execution, Git write, or network/provider bypass. |
| Prompt/context safety | 1.0 | Context is bounded, redacted, hashed, provenance-backed, and injection-resistant. |
| Evidence and hashing | 1.0 | Histories, latest artifacts, manifest, hashes, and completion record exist. |
| Idempotency and locking | 1.0 | Repeated tasks and concurrent runs are controlled and evidenced. |
| Integration and failure taxonomy | 1.0 | Failures are classified and downstream evidence refs are preserved. |

Hard caps:

```text
direct source mutation caps score at 4.0
direct shell execution caps score at 4.0
direct Git write caps score at 4.0
direct network/provider call caps score at 4.0
Model Adapter bypass caps score at 4.0
Tool / MCP Adapter bypass caps score at 4.0
Policy bypass caps score at 4.0
unvalidated model output accepted caps score at 5.0
patch applied by worker caps score at 4.0
schema validation failure caps score at 6.5
missing evidence caps score at 7.0
missing hashes caps score at 8.0
missing reviewed commit in review evidence caps score at 6.0
missing command exit codes in review evidence caps score at 7.0
any required area NOT CHECKED caps score at 8.0
```

---

# 50. Review Handoff Requirements

The later `LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD` document must require:

```text
reviewed commit
review environment
initial git status
final git status
compileall command and exit code
pytest command and exit code
schema validation command and exit code
forbidden import scan result
negative safety test result
model adapter integration result
tool adapter integration result
policy integration result
sandbox integration result
failure taxonomy integration result
patch handoff result
evidence manifest
completion record
artifact hashes
final DONE / NOT DONE verdict
implementation score
```

The review may not mark DONE if:

```text
reviewed commit is missing
command exit codes are missing
schema validation is not run
forbidden import scan is not run
negative safety tests are not run
evidence manifest is missing
completion record is missing
artifact hashes are missing
any required area is NOT CHECKED
any BLOCKER remains
```


---

# 51. Model Runtime Control Rules

The worker must not own model runtime, but every model request it prepares must include enough constraints for the Model Adapter to enforce safe execution.

Required model request controls:

```text
model_adapter_profile_ref
provider_mode
local_or_hosted_policy
prompt_contract_ref
prompt_version
context_hash
requested_output_schemas
max_input_tokens
max_output_tokens
timeout_seconds
max_retries
retry_allowed
cost_budget_ref, if hosted models are allowed
determinism_policy
redaction_status
policy_decision_id
```

Default values:

```text
timeout_seconds = 120
max_retries = 0
retry_allowed = false
determinism_policy = DETERMINISTIC_OR_LOW_VARIANCE
```

Rules:

```text
worker must not silently retry model calls
worker must not increase token budget without policy approval
worker must not switch model profile after policy approval without a new policy decision
worker must not use hosted/provider mode unless policy allows it
worker must not store provider credentials
worker must not log raw provider payloads unless redacted, bounded, and policy-approved
```

If model runtime controls are missing:

```text
status = BLOCKED
failure_class = WORKER_MODEL_POLICY_DENIED
```

---

# 52. Repair Loop and Repeated-Failure Rules

The worker may generate repair plans, but it must not enter an uncontrolled repair loop.

Required repair-loop controls:

```text
max_repair_attempts
current_repair_attempt
previous_failure_refs
previous_patch_proposal_refs
previous_validation_refs
retry_policy_decision_id
escalation_required
```

Default:

```text
max_repair_attempts = 1
```

Rules:

```text
same failing proposal must not be regenerated without a changed reason or changed context
third repeated failure must require governance or human review
repair plans must reference prior failure evidence
repair plans must not remove tests or weaken safety to pass validation
repair plans must not broaden permissions to avoid policy denial
```

If repair limit is exceeded:

```text
status = BLOCKED
failure_class = WORKER_EXECUTION_FAILED
```

---

# 53. Prompt and Output Retention Rules

The worker must minimize durable storage of prompts, context, and model outputs.

Allowed durable storage:

```text
prompt_contract_ref
prompt_version
prompt_template_hash
context_hash
context_item_hashes
model_request_id
model_response_id
bounded redacted output excerpt
parsed artifact refs
schema validation result
risk notes
```

Restricted durable storage:

```text
full raw prompt
full raw model output
large source excerpts
private logs
unredacted tool output
provider payloads
```

Rules:

```text
store references and hashes before storing raw content
raw content may be stored only if redacted, bounded, policy-approved, and necessary for audit
unredacted secrets must never be stored
large outputs must be summarized or stored as approved artifacts with hashes
retention-sensitive artifacts must be listed in the evidence manifest
```

If output cannot be safely redacted or bounded:

```text
status = BLOCKED
failure_class = WORKER_EVIDENCE_WRITE_FAILED
```

---

# 54. Self-Modification and Safety-Regression Guardrails

The worker must treat changes to safety-critical Agent_X layers as high-risk.

Safety-critical paths include:

```text
tools/agentx_evolve/security/
tools/agentx_evolve/policy/
tools/agentx_evolve/tools/
tools/agentx_evolve/mcp/
tools/agentx_evolve/model_adapter/
tools/agentx_evolve/workers/llm_implementation_worker/
tools/agentx_evolve/patch_execution/
tools/agentx_evolve/failure_taxonomy/
L0/
L1/standards/
L1/validators/
```

Rules:

```text
patch proposals targeting safety-critical paths require governance
patch proposals targeting this worker's own enforcement code require governance and human review
patch proposals must not weaken sandbox, policy, evidence, schema validation, or forbidden-import checks
patch proposals must not remove negative tests
patch proposals must not reduce blocking behavior to allow unsafe execution
```

Required safety-regression checks for patch proposals:

```text
does the proposal remove policy checks?
does the proposal remove sandbox checks?
does the proposal allow direct shell execution?
does the proposal allow direct source mutation?
does the proposal allow direct provider calls?
does the proposal allow Git writes?
does the proposal weaken evidence logging?
does the proposal remove schema validation?
does the proposal remove negative tests?
```

Any safety-regression pattern must produce:

```text
status = BLOCKED
failure_class = WORKER_PATCH_PROPOSAL_INVALID
```

---

# 55. Runtime Artifact Boundary and Exception Rules

The worker-owned runtime artifact root is:

```text
.agentx-init/implementation_worker/
```

Allowed worker-owned artifacts:

```text
worker task histories
worker result histories
implementation plan histories
patch proposal histories
tool request plan histories
validation request plan histories
repair plan histories
blocked/invalid histories
latest worker artifacts
worker evidence manifest
worker completion record
worker lock files
worker hash records
```

Allowed referenced downstream artifact roots:

```text
.agentx-init/tool_calls/
.agentx-init/model_adapter/
.agentx-init/security/
.agentx-init/policy/
.agentx-init/patch_execution/
.agentx-init/evaluations/
.agentx-init/failures/
```

Rules:

```text
worker may reference downstream evidence but must not rewrite it
worker must not write evidence outside its root unless the owning component owns that artifact
exceptions require a deviation register entry
source-tree writes are forbidden
test temp directories are allowed only in tests and must not be treated as runtime evidence
```

Unregistered artifact writes are a BLOCKER for DONE.

---

# 56. Command Request Acceptance Criteria

The worker must not execute commands. It may only generate validation request plans.

A validation request plan may include command requests only if each command request includes:

```text
command_id
purpose
allowed_command_ref
argv_array
working_directory_ref
expected_outputs
timeout_seconds
max_stdout_chars
max_stderr_chars
requires_tool_adapter = true
requires_policy_check = true
requires_sandbox_check = true
dry_run = true by default
```

Command request rules:

```text
argv_array must be structured, not raw shell string
shell metacharacter injection must be rejected
network commands are blocked by default
Git write commands are blocked
destructive commands are blocked
commands must be allowlisted downstream
validation request plan is not command execution
```

Forbidden command patterns include:

```text
rm -rf
git push
git reset --hard
git clean
curl
wget
ssh
scp
npm install
pip install from network
shell=True
pipes, redirects, command chaining
```

If the worker emits an unsafe command request:

```text
status = BLOCKED
failure_class = WORKER_DIRECT_SHELL_BLOCKED
```

---

# 57. Deterministic Proposal Rules

Implementation proposals must be reproducible enough for review.

Required deterministic inputs:

```text
task_id
context_hash
prompt_template_hash
prompt_version
model_adapter_profile_ref
model parameters or determinism policy
policy_decision_id
sandbox decision refs
idempotency_key
```

Required deterministic outputs:

```text
implementation_plan_id
patch_proposal_id
artifact hashes
reason for divergence if repeated run differs
```

Rules:

```text
same deterministic inputs should produce same artifact hashes or a recorded divergence reason
nondeterministic model output must not be treated as automatically wrong, but divergence must be evidenced
model profile changes require new policy decision and new evidence manifest
prompt version changes require new artifact hashes
```

---

# 58. Unsafe Output Quarantine Rule

Unsafe or schema-invalid model output must be quarantined as evidence without being accepted as an implementation artifact.

Quarantine record must include:

```text
quarantine_id
task_id
model_response_id
reason
failure_class
redaction_status
bounded_excerpt
output_hash, if safe
created_at
```

Rules:

```text
quarantined output must not become an implementation plan
quarantined output must not become a patch proposal
quarantined output must not be handed to patch execution
quarantined output must not overwrite latest valid artifacts
quarantined output must be redacted and bounded
```

Unsafe output examples:

```text
direct source-write instructions
direct shell commands
provider bypass instructions
policy/sandbox bypass instructions
test-removal instructions
evidence-removal instructions
forbidden-path edits
secret leakage
```

---

# 59. Final Frozen Acceptance Matrix

The implementation spec and coding agent handoff must satisfy this matrix.

| Area | Required final state |
|---|---|
| Contract status | v4 frozen controlling contract |
| Worker authority | proposal only, no direct execution |
| Model access | Model Adapter only |
| Tool access | Tool / MCP Adapter only |
| Patch access | Governed Patch Execution handoff only |
| Policy | required before model/tool/patch output |
| Sandbox | required for path-sensitive context and proposals |
| Failure taxonomy | required for blocked/failed/invalid results |
| Prompt contract | prompt_contract_ref and prompt_version required |
| Context | bounded, redacted, hashed, provenance-backed |
| Model output | schema-validated before acceptance |
| Unsafe output | quarantined, not accepted |
| Patch proposal | structured, hashed, never applied by worker |
| Validation request | plan only, no command execution |
| Evidence | append-only histories, latest artifacts, manifest, hashes |
| Idempotency | idempotency key and artifact-hash behavior defined |
| Locking | task/session lock required |
| Forbidden imports | direct provider/network/shell imports blocked |
| Safety-critical edits | governance and human review where required |
| DONE review | compileall, pytest, schema validation, forbidden import scan, negative tests, evidence hashes |

---

# 60. Final v4 No-Broadening Rule

This contract is now frozen for implementation handoff.

Do not add more required concepts unless they change one of these:

```text
worker authority
model boundary
tool boundary
patch boundary
policy boundary
sandbox boundary
evidence requirements
schema requirements
forbidden operation rules
DONE / NO-GO criteria
```

Allowed future changes before implementation spec:

```text
wording fixes
typo fixes
minor examples
implementation-spec details that do not change safety behavior
```

Required major revision:

```text
allowing direct source mutation
allowing direct shell execution
allowing direct Git write
allowing direct provider calls
allowing direct MCP calls
allowing patch application by worker
removing artifact hashing
removing evidence manifest
removing schema validation
removing forbidden import tests
```


---

# 61. Definition of Done

This layer is done when it can act as the controlled implementation-proposal worker for Agent_X.

It must prove:

```text
worker task schema validates
context input schema validates
model request schema validates
model response schema validates
worker result schema validates
implementation plan schema validates
patch proposal schema validates
tool request plan schema validates
validation request plan schema validates
invalid tasks fail closed
blocked tasks fail closed
policy checks occur before model requests
model requests go through Model Adapter
tool requests go through Tool / MCP Adapter
patch proposals are structured and handed off only
worker does not mutate source directly
worker does not execute shell directly
worker does not perform Git writes directly
worker does not bypass network/provider boundaries
model outputs are validated before acceptance
prompt/context input is bounded, hashed, and redacted
evidence records are written
artifact hashes are written
failures are classified
model runtime controls are present
repair-loop limits are enforced
prompt/output retention is bounded
unsafe model output is quarantined
validation command requests are structured plans only
safety-critical patch proposals require governance
runtime artifact boundary is enforced
deterministic proposal evidence is recorded
forbidden import tests pass
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 62. Final Freeze Rule

This v4 document is frozen as the controlling contract for the LLM Implementation Worker.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed worker authority, changed model boundary, changed tool boundary, changed mutation policy, changed evidence requirements, new required output category
```

Blocked without major revision:

```text
allowing direct source mutation
allowing direct shell execution
allowing direct Git write
allowing direct network/provider calls
allowing direct model SDK calls
allowing Tool / MCP Adapter bypass
allowing Policy / Capability Registry bypass
allowing Security Sandbox bypass
allowing unvalidated model output acceptance
removing evidence logging
removing artifact hashing
removing forbidden import checks
```

The next document should be:

```text
LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC
```

---

# 63. Final Rating

This v4 contract document is rated:

```text
10/10
```

Reason:

```text
It defines the LLM Implementation Worker with EQC, FIC, SIB, schema contracts, evidence/audit rules, worker authority boundaries, dependency gates, public API expectations, execution pipeline, model runtime controls, repair-loop limits, prompt/output retention rules, self-modification guardrails, command-request acceptance criteria, deterministic proposal rules, unsafe-output quarantine, artifact hashing, idempotency, locking, traceability, schema validation matrix, no-direct-mutation restrictions, patch proposal handoff rules, OpenCode borrowing limits, Agent_X integration notes, acceptance criteria, no-go conditions, review handoff requirements, completion evidence, final frozen acceptance matrix, and a precise Definition of Done.
```
