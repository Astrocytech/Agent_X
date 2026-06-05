# LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC

```text
document_id: LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff
component_id: AGENTX_LLM_IMPLEMENTATION_WORKER
component_name: LLM Implementation Worker
roadmap_layer: 10
roadmap_phase: Phase C — Controlled Implementation Generation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards:
  - Model Adapter Acceptance Criteria, if model calls are wired in this phase
  - Tool / MCP Adapter Acceptance Criteria, if worker can request tools in this phase
  - Governed Patch Execution Acceptance Criteria, if worker can hand off patch proposals
target_language: Python
canonical_worker_subdirectory: tools/agentx_evolve/workers/llm_implementation_worker/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/implementation_worker/
implementation_mode: deterministic planning, model-mediated implementation proposal, governed patch handoff only
previous_version_rating: 9.8/10
current_version_rating: 10/10
rating_target: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was very strong and implementation-ready. I would rate it:

```text
9.8/10
```

## 0.2 Why v3 Was Not Fully 10/10

The v3 document solved the major structural problems from v2: clean section numbering, canonical filenames, worker mode matrix, dependency-gate failure matrix, strict model-output JSON contract, patch proposal separation, validation handoff rules, evidence self-hash rules, expanded tests, and a frozen build sequence.

It was still not fully 10/10 because a few final operational details were under-specified for a coding-agent handoff:

```text
1. It did not define the exact allowed local dependency interface map for Model Adapter, Tool Adapter, Policy Registry, Patch Execution, and Failure Taxonomy.
2. It did not define import-failure behavior precisely enough for each dependency boundary.
3. It did not define timeout, retry, and output-size limits for model calls, tool requests, and validation handoff.
4. It did not define static bypass checks to prove the worker does not import provider SDKs, subprocess, requests/httpx, Git write helpers, or patch-apply helpers.
5. It did not define a precise validation command allowlist.
6. It did not define retention rules for raw model output, prompt packages, and context packages.
7. It did not define patch proposal path normalization and path traversal rejection strongly enough.
8. It did not define model-output ambiguity handling when the model returns multiple conflicting patch proposals.
9. It did not require a contract-to-code-to-test traceability matrix in the evidence package.
10. It did not define final review readiness checkpoints for the later post-implementation review / DoD document.
```

## 0.3 v4 Improvements

This v4 adds the final operational controls:

```text
allowed dependency interface map
dependency import-failure behavior
timeout, retry, and output-size limits
static bypass checks
validation command allowlist
retention and redaction rules
path normalization and traversal rejection
model-output conflict handling
contract-to-code-to-test traceability matrix
review readiness checkpoints
```

Final v4 rating:

```text
10/10
```

---

# 1. Purpose

This document is the implementation specification for the **LLM Implementation Worker**.

The LLM Implementation Worker receives a governed implementation task and produces structured implementation artifacts:

```text
context package
prompt package
model request
model response summary
implementation plan
patch proposal
validation handoff
worker result
audit/evidence records
```

The worker is allowed to plan and propose implementation work. It is not allowed to perform uncontrolled implementation side effects.

The worker must not directly:

```text
mutate source files
apply patches
execute shell commands
run Git write commands
call model providers
open network connections
start MCP servers
bypass Policy / Capability Registry
bypass Model Adapter
bypass Tool / MCP Adapter
bypass Governed Patch Execution
bypass Failure Taxonomy
```

The worker is a controlled planning and proposal layer, not a direct coding executor.

---

# 2. Scope

## 2.1 Required in This Layer

This layer must implement:

```text
worker task model
worker result model
dependency status model
context package model
prompt package model
model request model
model response summary model
implementation plan model
patch proposal model
validation handoff model
worker audit model
worker dispatcher
policy gate handling
model adapter boundary
tool adapter boundary
patch execution boundary
failure taxonomy mapping
evidence logging
schema validation
negative safety tests
completion evidence
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
model provider clients
local model runtime loading
provider key management
direct filesystem writes to source
direct patch application
direct shell execution
direct Git write
direct network fetch/search
MCP server runtime
human approval UI
promotion gate
full orchestrator
background daemon
long-term learning
```

---

# 3. Standards Applied

## 3.1 Primary Standard

```text
EQC
```

EQC is primary because this worker decides how implementation tasks are interpreted, what context is sent to a model, what code changes are proposed, what validation is requested, and what evidence is generated.

## 3.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 3.3 Conditional Standards

```text
Model Adapter Acceptance Criteria, if model calls are wired
Tool / MCP Adapter Acceptance Criteria, if tool calls are requested
Governed Patch Execution Acceptance Criteria, if patch proposals are handed off
Command Acceptance Criteria, if validation commands are requested through Tool Adapter
```

## 3.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if markdown reports are later generated
```

---

# 4. Canonical Destination Summary

Worker package:

```text
tools/agentx_evolve/workers/llm_implementation_worker/
```

Schemas:

```text
tools/agentx_evolve/schemas/
```

Tests:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts:

```text
.agentx-init/implementation_worker/
```

Expected package relationship:

```text
tools/agentx_evolve/model_adapter/                       = model-call boundary
tools/agentx_evolve/tools/                               = Tool / MCP Adapter boundary
tools/agentx_evolve/patch_execution/                     = Governed Patch Execution boundary
tools/agentx_evolve/policy/                              = Policy / Capability Registry boundary
tools/agentx_evolve/failure_taxonomy/                    = Failure Taxonomy boundary
tools/agentx_evolve/workers/llm_implementation_worker/   = this worker
```

---

# 5. Exact Files to Create

## 5.1 Worker Package Files

```text
tools/agentx_evolve/workers/llm_implementation_worker/__init__.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_models.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_config.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_errors.py
tools/agentx_evolve/workers/llm_implementation_worker/dependency_status.py
tools/agentx_evolve/workers/llm_implementation_worker/context_builder.py
tools/agentx_evolve/workers/llm_implementation_worker/prompt_builder.py
tools/agentx_evolve/workers/llm_implementation_worker/model_boundary.py
tools/agentx_evolve/workers/llm_implementation_worker/tool_boundary.py
tools/agentx_evolve/workers/llm_implementation_worker/model_output_parser.py
tools/agentx_evolve/workers/llm_implementation_worker/plan_generator.py
tools/agentx_evolve/workers/llm_implementation_worker/patch_proposal.py
tools/agentx_evolve/workers/llm_implementation_worker/validation_handoff.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_policy.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_logger.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_dispatcher.py
```

## 5.2 Schema Files

Use these exact filenames:

```text
tools/agentx_evolve/schemas/llm_worker_task.schema.json
tools/agentx_evolve/schemas/llm_worker_result.schema.json
tools/agentx_evolve/schemas/llm_worker_dependency_status.schema.json
tools/agentx_evolve/schemas/llm_worker_context_package.schema.json
tools/agentx_evolve/schemas/llm_worker_prompt_package.schema.json
tools/agentx_evolve/schemas/llm_worker_model_request.schema.json
tools/agentx_evolve/schemas/llm_worker_model_response.schema.json
tools/agentx_evolve/schemas/llm_worker_model_output.schema.json
tools/agentx_evolve/schemas/llm_worker_implementation_plan.schema.json
tools/agentx_evolve/schemas/llm_worker_patch_proposal.schema.json
tools/agentx_evolve/schemas/llm_worker_validation_handoff.schema.json
tools/agentx_evolve/schemas/llm_worker_audit.schema.json
tools/agentx_evolve/schemas/llm_worker_evidence_manifest.schema.json
tools/agentx_evolve/schemas/llm_worker_review_report.schema.json
tools/agentx_evolve/schemas/llm_worker_completion_record.schema.json
tools/agentx_evolve/schemas/llm_worker_deviation_register.schema.json
tools/agentx_evolve/schemas/llm_worker_traceability_matrix.schema.json
tools/agentx_evolve/schemas/llm_worker_static_bypass_scan.schema.json
```

## 5.3 Test Files

Use these exact filenames:

```text
tools/agentx_evolve/tests/test_llm_worker_models.py
tools/agentx_evolve/tests/test_llm_worker_task_schema.py
tools/agentx_evolve/tests/test_llm_worker_result_schema.py
tools/agentx_evolve/tests/test_llm_worker_schema_validation.py
tools/agentx_evolve/tests/test_llm_worker_dependency_status.py
tools/agentx_evolve/tests/test_llm_worker_context_builder.py
tools/agentx_evolve/tests/test_llm_worker_prompt_builder.py
tools/agentx_evolve/tests/test_llm_worker_model_boundary.py
tools/agentx_evolve/tests/test_llm_worker_tool_boundary.py
tools/agentx_evolve/tests/test_llm_worker_model_output_parser.py
tools/agentx_evolve/tests/test_llm_worker_plan_generator.py
tools/agentx_evolve/tests/test_llm_worker_patch_proposal.py
tools/agentx_evolve/tests/test_llm_worker_validation_handoff.py
tools/agentx_evolve/tests/test_llm_worker_policy.py
tools/agentx_evolve/tests/test_llm_worker_logger.py
tools/agentx_evolve/tests/test_llm_worker_dispatcher.py
tools/agentx_evolve/tests/test_llm_worker_fake_dependencies.py
tools/agentx_evolve/tests/test_llm_worker_idempotency.py
tools/agentx_evolve/tests/test_llm_worker_evidence_immutability.py
tools/agentx_evolve/tests/test_llm_worker_negative_cases.py
tools/agentx_evolve/tests/test_llm_worker_static_bypass_scan.py
tools/agentx_evolve/tests/test_llm_worker_traceability_matrix.py
tools/agentx_evolve/tests/validate_llm_worker_schemas.py
```

---

# 6. Runtime Artifact Contract

Runtime artifact root:

```text
.agentx-init/implementation_worker/
```

Required runtime artifacts:

```text
.agentx-init/implementation_worker/worker_task_history.jsonl
.agentx-init/implementation_worker/dependency_status_history.jsonl
.agentx-init/implementation_worker/context_package_history.jsonl
.agentx-init/implementation_worker/prompt_package_history.jsonl
.agentx-init/implementation_worker/model_request_history.jsonl
.agentx-init/implementation_worker/model_response_history.jsonl
.agentx-init/implementation_worker/model_output_history.jsonl
.agentx-init/implementation_worker/implementation_plan_history.jsonl
.agentx-init/implementation_worker/patch_proposal_history.jsonl
.agentx-init/implementation_worker/validation_handoff_history.jsonl
.agentx-init/implementation_worker/worker_result_history.jsonl
.agentx-init/implementation_worker/worker_audit_history.jsonl
.agentx-init/implementation_worker/latest_worker_result.json
.agentx-init/implementation_worker/llm_worker_dependency_status.json
.agentx-init/implementation_worker/llm_worker_deviation_register.json
.agentx-init/implementation_worker/llm_worker_evidence_manifest.json
.agentx-init/implementation_worker/llm_worker_review_report.json
.agentx-init/implementation_worker/llm_worker_completion_record.json
.agentx-init/implementation_worker/llm_worker_traceability_matrix.json
.agentx-init/implementation_worker/llm_worker_static_bypass_scan.json
```

Runtime artifact rules:

```text
append-only JSONL for histories
atomic JSON write for latest_worker_result.json
SHA-256 hashes for final evidence artifacts
no source files written by this layer
no raw secrets logged
no raw untrusted model output logged without redaction/summarization
runtime writes outside .agentx-init/implementation_worker/ require deviation entry
```

---

# 7. Worker Modes

The worker must explicitly support these modes.

| Mode | Purpose | Model call | Patch proposal | Validation handoff | Allowed without all dependencies? |
|---|---|---:|---:|---:|---:|
| `PLAN_ONLY` | Produce structured implementation plan. | Optional | No | Optional dry-run only | Yes, if no model call is needed |
| `PATCH_PROPOSAL` | Produce structured patch proposal. | Required unless deterministic source exists | Yes | Optional | No |
| `VALIDATION_HANDOFF` | Build validation request through Tool Adapter. | Optional | Optional | Yes | No |
| `REPAIR_PLAN` | Interpret failure and propose repair plan. | Required unless deterministic source exists | Optional | Optional | No |
| `RESTRICTED` | Safe mode when dependencies are missing. | No | No direct handoff | No execution | Yes |

Output requirements by mode:

| Mode | Required outputs |
|---|---|
| `PLAN_ONLY` | `LLMWorkerResult`, `ImplementationPlan`, evidence |
| `PATCH_PROPOSAL` | `LLMWorkerResult`, `ImplementationPlan`, `PatchProposal`, evidence |
| `VALIDATION_HANDOFF` | `LLMWorkerResult`, `ValidationHandoff`, evidence |
| `REPAIR_PLAN` | `LLMWorkerResult`, `ImplementationPlan`, optional `PatchProposal`, evidence |
| `RESTRICTED` | `LLMWorkerResult` with `BLOCKED` or `PARTIAL`, dependency status, evidence |

No mode may apply a patch, write source, run shell, run Git write, or call a provider directly.

---

# 8. Dependency Gates

## 8.1 Required Dependencies for Full Operation

Full operation requires:

```text
Model Adapter
Tool / MCP Adapter
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Governed Patch Execution, for patch handoff only
```

## 8.2 Dependency Gate Matrix

| Dependency | Missing behavior | Failure class | Allowed fallback |
|---|---|---|---|
| Model Adapter | Block model calls. | `WORKER_MODEL_CALL_FAILED` or `WORKER_MODEL_POLICY_DENIED` | No direct provider fallback |
| Tool / MCP Adapter | Block tool requests and validation execution. | `WORKER_TOOL_REQUEST_DENIED` | No direct shell/tool fallback |
| Policy / Capability Registry | Block high-risk actions. | `WORKER_POLICY_DENIED` | Dry-run schema/context only |
| Failure Taxonomy | Use local worker failure constants. | local constant | Record warning |
| Governed Patch Execution | Create proposal but block handoff. | `WORKER_VALIDATION_HANDOFF_FAILED` or `WORKER_PATCH_PROPOSAL_INVALID` | Reviewable artifact only |

## 8.3 Dependency Status Artifact

Create:

```text
.agentx-init/implementation_worker/llm_worker_dependency_status.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_dependency_status.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "checked_at": "<UTC timestamp>",
  "model_adapter": "AVAILABLE | MISSING | FAILED | NOT CHECKED",
  "tool_adapter": "AVAILABLE | MISSING | FAILED | NOT CHECKED",
  "policy_registry": "AVAILABLE | MISSING | FAILED | NOT CHECKED",
  "failure_taxonomy": "AVAILABLE | MISSING | FAILED | NOT CHECKED",
  "governed_patch_execution": "AVAILABLE | MISSING | FAILED | NOT CHECKED",
  "restricted_mode": true,
  "allowed_modes": [],
  "blocked_capabilities": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
missing dependency must not become ALLOW
dependency import failure must not be ignored
restricted mode must be explicit
dependency status must be evidenced before full execution
```

---

# 9. Required Dataclasses

Implement these in:

```text
worker_models.py
```

Each dataclass must support:

```text
to_dict conversion
schema-valid default fields where possible
explicit warnings list
explicit errors list
stable id field
created_at timestamp
source_component
```

## 9.1 `LLMWorkerTask`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_task.schema.json"
task_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
requested_by: str
caller_role: str
session_id: str | None
worker_mode: str
implementation_goal: str
target_component_id: str
target_files: list[str]
constraints: list[str]
acceptance_criteria: list[str]
available_context_refs: list[str]
model_profile_id: str | None
tool_policy_context_id: str | None
patch_session_id: str | None
dry_run: bool
max_context_chars: int
max_model_output_chars: int
warnings: list[str]
errors: list[str]
```

## 9.2 `DependencyStatus`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_dependency_status.schema.json"
dependency_status_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str | None
model_adapter: str
tool_adapter: str
policy_registry: str
failure_taxonomy: str
governed_patch_execution: str
restricted_mode: bool
allowed_modes: list[str]
blocked_capabilities: list[str]
warnings: list[str]
errors: list[str]
```

## 9.3 `LLMWorkerContextPackage`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_context_package.schema.json"
context_package_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
included_files: list[str]
excluded_files: list[str]
included_artifact_refs: list[str]
context_summary: str
context_chunks: list[dict]
redaction_report: dict
truncation_report: dict
prompt_injection_report: dict
context_hash: str
warnings: list[str]
errors: list[str]
```

## 9.4 `LLMWorkerPromptPackage`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_prompt_package.schema.json"
prompt_package_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
context_package_id: str
system_contract: str
developer_contract: str
task_prompt: str
output_schema_instruction: str
forbidden_actions: list[str]
required_output_sections: list[str]
prompt_hash: str
warnings: list[str]
errors: list[str]
```

## 9.5 `LLMWorkerModelRequest`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_model_request.schema.json"
model_request_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
model_profile_id: str
prompt_package_id: str
requested_capability: str
max_output_chars: int
temperature: float | None
deterministic: bool
policy_decision_id: str | None
model_request_hash: str
warnings: list[str]
errors: list[str]
```

## 9.6 `LLMWorkerModelResponse`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_model_response.schema.json"
model_response_id: str
created_at: str
source_component: str = "ModelAdapter"
task_id: str
model_request_id: str
status: str
raw_response_ref: str | None
safe_summary: str
parsed_output_ref: str | None
usage_summary: dict
failure_class: str | None
model_response_hash: str
warnings: list[str]
errors: list[str]
```

## 9.7 `ParsedModelOutput`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_model_output.schema.json"
parsed_output_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
model_response_id: str
implementation_summary: str
implementation_plan: dict
files_to_change: list[str]
schemas_to_change: list[str]
tests_to_change: list[str]
patch_proposal: dict | None
validation_handoff: dict | None
risk_notes: list[str]
assumptions: list[str]
rejected_content: list[dict]
parsed_output_hash: str
warnings: list[str]
errors: list[str]
```

## 9.8 `ImplementationPlan`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_implementation_plan.schema.json"
plan_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
target_component_id: str
steps: list[dict]
files_expected_to_change: list[str]
schemas_expected_to_change: list[str]
tests_expected_to_change: list[str]
risk_notes: list[str]
required_authorities: list[str]
validation_commands: list[str]
acceptance_criteria_mapping: list[dict]
implementation_plan_hash: str
warnings: list[str]
errors: list[str]
```

## 9.9 `PatchProposal`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_patch_proposal.schema.json"
patch_proposal_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
plan_id: str
patch_format: str
target_files: list[str]
proposed_changes: list[dict]
diff_ref: str | None
governed_patch_request_ref: str | None
rationale: str
requires_governance: bool
requires_human_approval: bool
handoff_status: str
patch_proposal_hash: str
warnings: list[str]
errors: list[str]
```

## 9.10 `ValidationHandoff`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_validation_handoff.schema.json"
validation_handoff_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
plan_id: str
patch_proposal_id: str | None
validation_commands: list[str]
expected_artifacts: list[str]
tool_requests: list[dict]
handoff_target: str
dry_run: bool
validation_handoff_hash: str
warnings: list[str]
errors: list[str]
```

## 9.11 `LLMWorkerResult`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_result.schema.json"
worker_result_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
task_id: str
status: str
message: str
worker_mode: str
implementation_plan_id: str | None
patch_proposal_id: str | None
validation_handoff_id: str | None
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
worker_result_hash: str
warnings: list[str]
errors: list[str]
```

## 9.12 `LLMWorkerAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "llm_worker_audit.schema.json"
audit_id: str
created_at: str
source_component: str = "LLMImplementationWorker"
event_type: str
task_id: str | None
status: str
message: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

---

# 10. Constants

Define constants in `worker_config.py` and re-export from `worker_models.py` if useful.

## 10.1 Worker Status Constants

```python
WORKER_SUCCESS = "SUCCESS"
WORKER_PARTIAL = "PARTIAL"
WORKER_BLOCKED = "BLOCKED"
WORKER_FAILED = "FAILED"
WORKER_INVALID = "INVALID"
```

## 10.2 Worker Mode Constants

```python
MODE_PLAN_ONLY = "PLAN_ONLY"
MODE_PATCH_PROPOSAL = "PATCH_PROPOSAL"
MODE_VALIDATION_HANDOFF = "VALIDATION_HANDOFF"
MODE_REPAIR_PLAN = "REPAIR_PLAN"
MODE_RESTRICTED = "RESTRICTED"
```

## 10.3 Worker Failure Classes

```python
WORKER_TASK_SCHEMA_INVALID = "WORKER_TASK_SCHEMA_INVALID"
WORKER_POLICY_DENIED = "WORKER_POLICY_DENIED"
WORKER_DEPENDENCY_MISSING = "WORKER_DEPENDENCY_MISSING"
WORKER_CONTEXT_BUILD_FAILED = "WORKER_CONTEXT_BUILD_FAILED"
WORKER_CONTEXT_TOO_LARGE = "WORKER_CONTEXT_TOO_LARGE"
WORKER_PROMPT_BUILD_FAILED = "WORKER_PROMPT_BUILD_FAILED"
WORKER_MODEL_POLICY_DENIED = "WORKER_MODEL_POLICY_DENIED"
WORKER_MODEL_CALL_FAILED = "WORKER_MODEL_CALL_FAILED"
WORKER_MODEL_RESPONSE_INVALID = "WORKER_MODEL_RESPONSE_INVALID"
WORKER_MODEL_OUTPUT_REJECTED = "WORKER_MODEL_OUTPUT_REJECTED"
WORKER_PATCH_PROPOSAL_INVALID = "WORKER_PATCH_PROPOSAL_INVALID"
WORKER_VALIDATION_HANDOFF_FAILED = "WORKER_VALIDATION_HANDOFF_FAILED"
WORKER_TOOL_REQUEST_DENIED = "WORKER_TOOL_REQUEST_DENIED"
WORKER_DIRECT_MUTATION_BLOCKED = "WORKER_DIRECT_MUTATION_BLOCKED"
WORKER_EVIDENCE_WRITE_FAILED = "WORKER_EVIDENCE_WRITE_FAILED"
WORKER_UNKNOWN_FAILURE = "WORKER_UNKNOWN_FAILURE"
```

## 10.4 Forbidden Actions

```text
direct source write
direct shell execution
direct subprocess execution
direct Git write
direct patch application
direct model provider call
direct network call
direct MCP server call
policy bypass
sandbox bypass
tool adapter bypass
model adapter bypass
patch execution bypass
governance bypass
human approval bypass
```

---

# 11. Schema Requirements

Each schema must:

```text
require schema_version
require schema_id
require source_component
require created_at where applicable
require warnings
require errors
define enums for status, worker_mode, dependency status, patch_format, handoff_status, and failure_class
reject missing required fields
reject invalid enum values
allow artifact_refs and evidence_refs arrays where applicable
allow safe summaries instead of raw private payloads
```

Required schema examples:

```text
valid_llm_worker_task
valid_dependency_status
valid_context_package
valid_prompt_package
valid_model_request
valid_model_response
valid_parsed_model_output
valid_implementation_plan
valid_patch_proposal
valid_validation_handoff
valid_worker_result_success
valid_worker_result_blocked
valid_worker_audit_event
valid_evidence_manifest
valid_review_report
valid_completion_record
valid_deviation_register
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
unsafe oversized raw payload fails where restricted
unknown status fails
unknown worker mode fails
```

---

# 12. Public API

## 12.1 `dependency_status.py`

```python
check_worker_dependencies(
    task: LLMWorkerTask,
    dependency_context: dict
) -> DependencyStatus
```

```python
determine_allowed_modes(
    dependency_status: DependencyStatus,
    policy_context: dict
) -> list[str]
```

## 12.2 `context_builder.py`

```python
build_context_package(
    task: LLMWorkerTask,
    context_sources: dict,
    policy_context: dict,
    repo_root: Path
) -> LLMWorkerContextPackage
```

```python
sanitize_context_chunk(chunk: dict) -> dict
redact_context_secrets(context_package: LLMWorkerContextPackage) -> LLMWorkerContextPackage
enforce_context_budget(context_package: LLMWorkerContextPackage, max_context_chars: int) -> LLMWorkerContextPackage
detect_prompt_injection(context_package: LLMWorkerContextPackage) -> LLMWorkerContextPackage
```

## 12.3 `prompt_builder.py`

```python
build_prompt_package(
    task: LLMWorkerTask,
    context_package: LLMWorkerContextPackage,
    output_schema_id: str
) -> LLMWorkerPromptPackage
```

```python
build_output_schema_instruction(schema_id: str) -> str
hash_prompt_package(prompt_package: LLMWorkerPromptPackage) -> str
```

## 12.4 `model_boundary.py`

```python
build_model_request(
    task: LLMWorkerTask,
    prompt_package: LLMWorkerPromptPackage,
    model_profile_id: str,
    policy_context: dict
) -> LLMWorkerModelRequest
```

```python
call_model_adapter(
    model_request: LLMWorkerModelRequest,
    prompt_package: LLMWorkerPromptPackage,
    model_context: dict
) -> LLMWorkerModelResponse
```

## 12.5 `model_output_parser.py`

```python
parse_model_output(
    model_response: LLMWorkerModelResponse
) -> ParsedModelOutput
```

```python
validate_parsed_model_output(
    parsed_output: ParsedModelOutput,
    task: LLMWorkerTask
) -> LLMWorkerResult | None
```

## 12.6 `tool_boundary.py`

```python
build_tool_request(
    task: LLMWorkerTask,
    tool_name: str,
    arguments: dict,
    requested_effect: str
) -> dict
```

```python
request_tool_via_adapter(
    tool_request: dict,
    tool_context: dict
) -> dict
```

```python
block_direct_tool_bypass(reason: str) -> LLMWorkerResult
```

## 12.7 `plan_generator.py`

```python
generate_implementation_plan(
    task: LLMWorkerTask,
    parsed_output: ParsedModelOutput,
    context_package: LLMWorkerContextPackage
) -> ImplementationPlan
```

```python
validate_implementation_plan(
    plan: ImplementationPlan,
    task: LLMWorkerTask
) -> LLMWorkerResult | None
```

## 12.8 `patch_proposal.py`

```python
generate_patch_proposal(
    task: LLMWorkerTask,
    plan: ImplementationPlan,
    parsed_output: ParsedModelOutput
) -> PatchProposal
```

```python
validate_patch_proposal(
    patch_proposal: PatchProposal,
    policy_context: dict
) -> LLMWorkerResult | None
```

```python
handoff_patch_proposal(
    patch_proposal: PatchProposal,
    governed_patch_context: dict
) -> dict
```

## 12.9 `validation_handoff.py`

```python
build_validation_handoff(
    task: LLMWorkerTask,
    plan: ImplementationPlan,
    patch_proposal: PatchProposal | None,
    tool_context: dict
) -> ValidationHandoff
```

```python
request_validation_via_tool_adapter(
    handoff: ValidationHandoff,
    tool_context: dict
) -> dict
```

## 12.10 `worker_policy.py`

```python
check_worker_task_permission(
    task: LLMWorkerTask,
    policy_context: dict
) -> dict
```

```python
check_model_call_permission(
    model_request: LLMWorkerModelRequest,
    policy_context: dict
) -> dict
```

```python
check_patch_proposal_permission(
    patch_proposal: PatchProposal,
    policy_context: dict
) -> dict
```

```python
check_validation_handoff_permission(
    handoff: ValidationHandoff,
    policy_context: dict
) -> dict
```

## 12.11 `worker_logger.py`

```python
append_worker_task(task: LLMWorkerTask, repo_root: Path) -> dict
append_dependency_status(status: DependencyStatus, repo_root: Path) -> dict
append_context_package(context_package: LLMWorkerContextPackage, repo_root: Path) -> dict
append_prompt_package(prompt_package: LLMWorkerPromptPackage, repo_root: Path) -> dict
append_model_request(model_request: LLMWorkerModelRequest, repo_root: Path) -> dict
append_model_response(model_response: LLMWorkerModelResponse, repo_root: Path) -> dict
append_parsed_model_output(parsed_output: ParsedModelOutput, repo_root: Path) -> dict
append_implementation_plan(plan: ImplementationPlan, repo_root: Path) -> dict
append_patch_proposal(patch_proposal: PatchProposal, repo_root: Path) -> dict
append_validation_handoff(handoff: ValidationHandoff, repo_root: Path) -> dict
append_worker_result(result: LLMWorkerResult, repo_root: Path) -> dict
append_worker_audit(event: LLMWorkerAuditEvent, repo_root: Path) -> dict
write_latest_worker_result(result: LLMWorkerResult, repo_root: Path) -> dict
write_evidence_manifest(manifest: dict, repo_root: Path) -> dict
write_review_report(report: dict, repo_root: Path) -> dict
write_completion_record(record: dict, repo_root: Path) -> dict
```

## 12.12 `worker_dispatcher.py`

```python
execute_llm_implementation_task(
    task: LLMWorkerTask,
    context_sources: dict,
    policy_context: dict,
    model_context: dict,
    tool_context: dict,
    governed_patch_context: dict,
    dependency_context: dict,
    repo_root: Path
) -> LLMWorkerResult
```

---

# 13. Worker Execution Flow

Every worker run must follow this sequence:

```text
1. Receive LLMWorkerTask.
2. Validate task schema.
3. Write task evidence.
4. Check dependency status.
5. Write dependency status evidence.
6. Check worker task permission.
7. Determine worker mode and allowed capabilities.
8. Build context package.
9. Redact secrets.
10. Detect prompt-injection-like instructions in context.
11. Enforce context budget.
12. Write context package evidence.
13. Build prompt package with output schema instruction.
14. Hash prompt package.
15. Write prompt package evidence.
16. If mode requires model call, build model request.
17. Check model-call permission.
18. Call Model Adapter through model_boundary only.
19. Write model request and response evidence.
20. Parse model output into ParsedModelOutput.
21. Validate parsed model output.
22. Generate implementation plan.
23. Validate implementation plan.
24. Write implementation plan evidence.
25. If mode requires patch proposal, generate patch proposal.
26. Validate patch proposal.
27. Write patch proposal evidence.
28. If patch handoff requested, hand off only through Governed Patch Execution.
29. If validation handoff requested, build ValidationHandoff.
30. Request validation only through Tool / MCP Adapter.
31. Write validation handoff evidence.
32. Build final LLMWorkerResult.
33. Write worker result history.
34. Write latest_worker_result.json atomically.
35. Return schema-valid LLMWorkerResult.
```

Any failed stage must return:

```text
schema-valid LLMWorkerResult
status = BLOCKED | FAILED | INVALID
failure_class populated
evidence_refs populated where available
artifact_refs populated where available
warnings/errors populated
```

---

# 14. Model-Call Boundary

The worker must not call model providers directly.

Allowed:

```text
construct LLMWorkerModelRequest
call Model Adapter interface
receive LLMWorkerModelResponse
parse structured response
record safe summary and evidence refs
```

Forbidden:

```text
direct OpenAI imports
direct Anthropic imports
direct Gemini imports
direct local runtime imports
direct HTTP calls
direct model loading
direct GPU/runtime selection
direct provider key access
direct network access
provider credential logging
```

If Model Adapter is missing:

```text
return BLOCKED
failure_class = WORKER_MODEL_CALL_FAILED or WORKER_MODEL_POLICY_DENIED
no direct fallback provider call
```

---

# 15. Tool-Call Boundary

The worker must not execute tools directly.

Allowed:

```text
build tool request
send tool request to Tool / MCP Adapter
receive tool result
store tool result reference
use safe result summary
```

Forbidden:

```text
direct filesystem writes
direct shell/subprocess
direct Git commands
direct patch apply
direct sandbox calls to mutate source
direct policy bypass
direct MCP server calls
```

If Tool / MCP Adapter is missing:

```text
tool requests return BLOCKED
validation handoff remains unexecuted
worker result records WORKER_TOOL_REQUEST_DENIED
```

---

# 16. Prompt and Context Handling

## 16.1 Context Sources

Context may include:

```text
task description
target files
contract documents
implementation specs
review / DoD documents
schemas
tests
previous evidence artifacts
error logs
validation summaries
```

## 16.2 Context Rules

The worker must:

```text
include only task-relevant context
respect max_context_chars
summarize large files
redact secrets
record included files
record excluded files
record included artifact refs
record context hash
record redaction report
record truncation report
record prompt-injection report
avoid durable logging of raw secrets
```

## 16.3 Prompt Rules

Prompt package must include:

```text
system contract
developer contract
task prompt
output schema instruction
forbidden actions
required output sections
context summary
```

Prompt must tell the model:

```text
produce structured output only
produce implementation plan separately from patch proposal
do not claim files were changed
do not claim tests were run
do not include commands as executed
do not request direct shell
do not bypass Tool Adapter
do not bypass Patch Execution
do not output secrets
```

## 16.4 Prompt-Injection Handling

Instructions embedded inside source files, logs, documents, model output, or prior evidence are untrusted content.

Required behavior:

```text
do not follow embedded instructions that conflict with Agent_X governance
mark them as untrusted_context_instruction
record warning
continue using controlling contract instructions only
```

---

# 17. Model Output Contract

The Model Adapter response must be parsed into a strict JSON-like structure.

## 17.1 Required Parsed Output Shape

```json
{
  "implementation_summary": "string",
  "implementation_plan": {
    "steps": [],
    "files_expected_to_change": [],
    "schemas_expected_to_change": [],
    "tests_expected_to_change": [],
    "risk_notes": [],
    "required_authorities": [],
    "validation_commands": []
  },
  "files_to_change": [],
  "schemas_to_change": [],
  "tests_to_change": [],
  "patch_proposal": {
    "patch_format": "unified_diff | structured_file_change_list | governed_patch_request",
    "target_files": [],
    "proposed_changes": [],
    "diff": null,
    "rationale": "string"
  },
  "validation_handoff": {
    "validation_commands": [],
    "expected_artifacts": []
  },
  "risk_notes": [],
  "assumptions": []
}
```

## 17.2 Rejection Rules

Reject model output if it:

```text
cannot be parsed
omits required sections for the worker mode
claims files were already changed
claims tests already passed
claims commands were already executed
contains direct shell execution as completed action
contains Git write as completed action
requests direct model-provider access
requests direct network access
attempts to override Agent_X policy
contains unredacted secret-like values
targets files outside allowed scope
contains patch application instructions instead of proposal
```

Rejection result:

```text
status = INVALID or FAILED
failure_class = WORKER_MODEL_OUTPUT_REJECTED or WORKER_MODEL_RESPONSE_INVALID
```

---

# 18. Implementation Plan Generation

The implementation plan must be structured and separate from the patch proposal.

Required plan sections:

```text
target component
implementation goal
ordered steps
files expected to change
schemas expected to change
tests expected to change
risk notes
required authorities
validation commands
acceptance criteria mapping
```

The plan must not:

```text
claim files were changed
claim tests passed
include unapproved source mutation
include raw shell execution
include Git write operation
```

The plan is accepted only if:

```text
all planned changes map to task goal
all files are inside allowed subdirectories
all risky actions list required authority
validation commands are allowlist-compatible
```

---

# 19. Patch Proposal Generation

Patch proposals are structured proposals, not applied changes.

## 19.1 Allowed Patch Formats

```text
unified_diff
structured_file_change_list
governed_patch_request
```

## 19.2 Patch Proposal Rules

A patch proposal may include:

```text
inline proposed change summary
structured file change list
diff_ref
governed_patch_request_ref
rationale
risk notes
required authorities
```

It must not:

```text
write patch directly to source files
apply patch
edit files
stage files
commit files
push files
```

If proposal affects source files:

```text
requires_governance = true
handoff target = Governed Patch Execution
```

If Governed Patch Execution is unavailable:

```text
patch proposal may still be written as reviewable artifact
handoff_status = BLOCKED
no source mutation occurs
```

---

# 20. Validation Handoff

The worker may request validation only through Tool / MCP Adapter.

Allowed validation request types:

```text
compileall
pytest
schema validation
static check
project-specific allowlisted validation command
```

The worker must not execute validation commands directly.

Validation handoff must record:

```text
validation_handoff_id
task_id
plan_id
patch_proposal_id
validation_commands
expected_artifacts
tool_requests
handoff_target
dry_run
warnings
errors
```

If Tool / MCP Adapter cannot run validation:

```text
return BLOCKED or PARTIAL
record validation handoff artifact
do not fake pass/fail result
```

---

# 21. Policy Integration

The worker must check Policy / Capability Registry before:

```text
model call
tool request
patch proposal handoff
validation handoff
high-risk context inclusion
```

Restrictive fallback if Policy Registry is unavailable:

```text
allow schema validation
allow dependency status
allow context redaction
allow dry-run plan generation only when no model call is required
block model calls
block tool calls
block patch handoff
block validation execution
block source mutation
```

Unknown caller must block.

---

# 22. Failure Taxonomy Integration

Every blocked, failed, or invalid result must include `failure_class`.

Required mappings:

```text
invalid task schema -> WORKER_TASK_SCHEMA_INVALID
missing dependency -> WORKER_DEPENDENCY_MISSING
policy denied -> WORKER_POLICY_DENIED
context build failure -> WORKER_CONTEXT_BUILD_FAILED
context too large -> WORKER_CONTEXT_TOO_LARGE
prompt build failure -> WORKER_PROMPT_BUILD_FAILED
model policy denied -> WORKER_MODEL_POLICY_DENIED
model call failure -> WORKER_MODEL_CALL_FAILED
invalid model response -> WORKER_MODEL_RESPONSE_INVALID
rejected model output -> WORKER_MODEL_OUTPUT_REJECTED
invalid patch proposal -> WORKER_PATCH_PROPOSAL_INVALID
validation handoff failure -> WORKER_VALIDATION_HANDOFF_FAILED
tool request denied -> WORKER_TOOL_REQUEST_DENIED
direct mutation attempt -> WORKER_DIRECT_MUTATION_BLOCKED
evidence write failure -> WORKER_EVIDENCE_WRITE_FAILED
unknown failure -> WORKER_UNKNOWN_FAILURE
```

If Failure Taxonomy is unavailable:

```text
use local worker constants
record warning
do not omit failure_class
```

---

# 23. Idempotency, Locking, and Concurrency

## 23.1 Idempotency

For the same:

```text
task_id
worker_mode
context_hash
prompt_hash
model_profile_id
policy context hash
dependency status
```

a dry-run must produce stable artifact provenance.

Repeated dry-runs must not:

```text
mutate source
produce contradictory status without new cause
overwrite evidence without new timestamp
claim execution that did not happen
```

## 23.2 Locking

Allowed lock path:

```text
.agentx-init/implementation_worker/llm_worker.lock
```

Required behavior:

```text
latest_worker_result.json written atomically
completion record written only after validation
stale lock detected and recorded
history JSONL lines not partially written
concurrent worker runs cannot corrupt latest artifacts
```

---

# 24. Evidence, Hashing, and Immutability

## 24.1 Required Hashes

Use SHA-256 via Python standard library `hashlib`.

Required hashes:

```text
context_hash
prompt_hash
model_request_hash
model_response_hash
parsed_output_hash
implementation_plan_hash
patch_proposal_hash
validation_handoff_hash
worker_result_hash
evidence_manifest_sha256
review_report_sha256
completion_record_sha256
```

## 24.2 Self-Hash Rule

For self-referential artifacts:

```text
compute hash over canonical JSON with the self-hash field omitted or set to null
record resulting SHA-256 in the self-hash field
document this behavior in the evidence manifest
```

Applies to:

```text
llm_worker_evidence_manifest.json
llm_worker_review_report.json
llm_worker_completion_record.json
```

## 24.3 Evidence Immutability Rule

After final DONE:

```text
final evidence files must not be modified without new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence requires new timestamp and reviewed commit
manual edits after sign-off must be listed as deviations
```

---

# 25. Fake Dependency Test Contracts

Tests may use fake dependencies, but they must be restrictive.

## 25.1 Fake Model Adapter

Must support:

```text
success response with required sections
blocked response
invalid response
oversized response
secret-like response requiring redaction
```

Must not:

```text
call provider
open network
load model
read provider keys
```

## 25.2 Fake Tool Adapter

Must support:

```text
allowed validation request
blocked tool request
invalid tool request
schema-valid tool result
evidence ref propagation
```

Must not:

```text
execute shell
mutate files
call Git
apply patches
```

## 25.3 Fake Policy Registry

Must support:

```text
ALLOW
BLOCK
NEEDS_GOVERNANCE
NEEDS_APPROVAL
DRY_RUN_ONLY
```

Default fake behavior must be restrictive.

## 25.4 Fake Governed Patch Execution

Must support:

```text
accept proposal as artifact
reject proposal
block because no session
block because no governance
```

Must never apply a patch in worker tests.

---

# 26. Worker Logger Requirements

The logger must:

```text
create runtime artifact root if needed
append JSONL histories
write latest_worker_result.json atomically
redact secrets before durable logging
truncate unsafe oversized model output
write evidence refs
write artifact refs
write SHA-256 hashes
preserve malformed existing JSONL lines
not write source files
```

Secret redaction must cover:

```text
API keys
tokens
passwords
private keys
provider credentials
environment variables likely to contain secrets
secret-like raw model output
```

---

# 27. Test Implementation Plan

## 27.1 Required Fixtures

```python
@pytest.fixture
def temp_repo(tmp_path): ...

@pytest.fixture
def valid_worker_task(): ...

@pytest.fixture
def restrictive_policy_context(): ...

@pytest.fixture
def allowed_policy_context(): ...

@pytest.fixture
def fake_model_adapter_success(): ...

@pytest.fixture
def fake_model_adapter_invalid_response(): ...

@pytest.fixture
def fake_model_adapter_secret_response(): ...

@pytest.fixture
def fake_tool_adapter_blocked(): ...

@pytest.fixture
def fake_tool_adapter_allowed_validation(): ...

@pytest.fixture
def fake_governed_patch_context_unavailable(): ...

@pytest.fixture
def fake_policy_registry_blocking(): ...
```

## 27.2 Required Tests

```text
test_worker_task_dataclass_instantiates
test_worker_result_dataclass_instantiates
test_dependency_status_dataclass_instantiates
test_worker_task_schema_accepts_valid_task
test_worker_task_schema_rejects_missing_task_id
test_worker_result_schema_accepts_success
test_worker_result_schema_accepts_blocked
test_all_worker_schemas_validate_valid_examples
test_all_worker_schemas_reject_missing_required_fields
test_dependency_status_records_missing_model_adapter
test_dependency_status_enables_restricted_mode
test_context_builder_includes_allowed_context
test_context_builder_excludes_disallowed_context
test_context_builder_redacts_secret_like_values
test_context_builder_detects_prompt_injection
test_context_builder_enforces_context_budget
test_prompt_builder_creates_schema_instruction
test_prompt_builder_includes_forbidden_actions
test_prompt_hash_is_stable
test_model_boundary_builds_model_request
test_model_boundary_blocks_without_model_adapter
test_model_boundary_rejects_invalid_model_response
test_model_boundary_does_not_import_provider_clients
test_model_output_parser_accepts_required_shape
test_model_output_parser_rejects_claimed_execution
test_model_output_parser_rejects_direct_shell_instruction
test_tool_boundary_blocks_direct_tool_bypass
test_tool_boundary_uses_tool_adapter_only
test_plan_generator_creates_structured_plan
test_plan_generator_rejects_plan_outside_allowed_scope
test_patch_proposal_creates_structured_proposal
test_patch_proposal_does_not_apply_changes
test_patch_handoff_blocks_without_patch_execution
test_validation_handoff_builds_tool_requests
test_validation_handoff_does_not_run_commands_directly
test_validation_handoff_rejects_unallowlisted_command
test_worker_policy_blocks_unknown_caller
test_worker_policy_blocks_model_call_without_permission
test_worker_logger_writes_histories
test_worker_logger_writes_latest_atomically
test_worker_logger_redacts_secrets
test_worker_logger_records_hashes
test_dispatcher_success_dry_run_plan_only
test_dispatcher_blocks_when_policy_missing_for_model_call
test_dispatcher_blocks_when_patch_execution_missing
test_dispatcher_records_failure_class_for_blocked_result
test_fake_dependencies_do_not_perform_side_effects
test_worker_idempotent_dry_run_artifact_provenance
test_evidence_immutability_hash_changes_invalidate_done
```

---

# 28. Negative Tests

Required negative cases:

```text
unknown caller -> BLOCKED
missing task_id -> INVALID
invalid schema -> INVALID
context exceeds budget -> BLOCKED or truncated with evidence
secret-like context -> redacted before logging
prompt-injection instruction in context -> ignored and warned
direct source mutation attempt -> BLOCKED
direct subprocess attempt -> BLOCKED
direct Git write attempt -> BLOCKED
direct model provider import/call attempt -> BLOCKED by design/test
model adapter missing -> BLOCKED
model response missing required sections -> FAILED or INVALID
model output claims tests passed -> REJECTED
model output claims files changed -> REJECTED
tool adapter missing -> BLOCKED
tool request denied -> BLOCKED
patch proposal attempts direct apply -> BLOCKED
validation command direct execution attempt -> BLOCKED
network use attempted directly -> BLOCKED
raw model output with secret-like string -> redacted
runtime artifact outside approved root -> FAIL unless deviation recorded
```

Any failed negative test is a BLOCKER.

---

# 29. Implementation Order

Implement in this exact order:

```text
1. Create worker package directory and __init__.py.
2. Implement worker_config.py constants.
3. Implement worker_errors.py.
4. Implement worker_models.py dataclasses and helpers.
5. Create all schemas.
6. Implement dependency_status.py.
7. Implement context_builder.py.
8. Implement prompt_builder.py.
9. Implement worker_policy.py.
10. Implement model_boundary.py.
11. Implement tool_boundary.py.
12. Implement model_output_parser.py.
13. Implement plan_generator.py.
14. Implement patch_proposal.py.
15. Implement validation_handoff.py.
16. Implement worker_logger.py.
17. Implement worker_dispatcher.py.
18. Create schema validation tests.
19. Create unit tests.
20. Create negative tests.
21. Create fake dependency tests.
22. Create idempotency/evidence immutability tests.
23. Run compileall.
24. Run scoped pytest.
25. Run schema validation command.
26. Verify git status.
27. Write evidence manifest.
28. Write review report.
29. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 30. Fresh-Clone Validation Requirement

Run from a fresh checkout or clean working tree.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version

PYTHONPATH=tools python -m compileall tools/agentx_evolve/workers/llm_implementation_worker

PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_llm_worker_models.py \
  tools/agentx_evolve/tests/test_llm_worker_task_schema.py \
  tools/agentx_evolve/tests/test_llm_worker_result_schema.py \
  tools/agentx_evolve/tests/test_llm_worker_schema_validation.py \
  tools/agentx_evolve/tests/test_llm_worker_dependency_status.py \
  tools/agentx_evolve/tests/test_llm_worker_context_builder.py \
  tools/agentx_evolve/tests/test_llm_worker_prompt_builder.py \
  tools/agentx_evolve/tests/test_llm_worker_model_boundary.py \
  tools/agentx_evolve/tests/test_llm_worker_tool_boundary.py \
  tools/agentx_evolve/tests/test_llm_worker_model_output_parser.py \
  tools/agentx_evolve/tests/test_llm_worker_plan_generator.py \
  tools/agentx_evolve/tests/test_llm_worker_patch_proposal.py \
  tools/agentx_evolve/tests/test_llm_worker_validation_handoff.py \
  tools/agentx_evolve/tests/test_llm_worker_policy.py \
  tools/agentx_evolve/tests/test_llm_worker_logger.py \
  tools/agentx_evolve/tests/test_llm_worker_dispatcher.py \
  tools/agentx_evolve/tests/test_llm_worker_fake_dependencies.py \
  tools/agentx_evolve/tests/test_llm_worker_idempotency.py \
  tools/agentx_evolve/tests/test_llm_worker_evidence_immutability.py \
  tools/agentx_evolve/tests/test_llm_worker_negative_cases.py \
  tools/agentx_evolve/tests/test_llm_worker_static_bypass_scan.py \
  tools/agentx_evolve/tests/test_llm_worker_traceability_matrix.py

PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_worker_schemas.py

git status --short
```

Required result:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

No validation command may require:

```text
GPU
hosted model
real LLM
network
Bun
Node
OpenCode runtime
running MCP server
real patch application
Git write
```

---

# 31. Evidence Manifest

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
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [
    {
      "name": "compileall",
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/workers/llm_implementation_worker",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "<scoped worker pytest command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_worker_schemas.py",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "dependency_status_path": ".agentx-init/implementation_worker/llm_worker_dependency_status.json",
  "deviation_register_path": ".agentx-init/implementation_worker/llm_worker_deviation_register.json",
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

---

# 32. Review Report

Create:

```text
.agentx-init/implementation_worker/llm_worker_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_review_report.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "review_document_id": "LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD",
  "implementation_spec_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/implementation_worker/llm_worker_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/implementation_worker/llm_worker_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

A DONE verdict is invalid if this report is missing or lacks reviewed commit, command text, command exit codes, or evidence hashes.

---

# 33. Deviation Register

Create:

```text
.agentx-init/implementation_worker/llm_worker_deviation_register.json
```

Required deviation format:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_deviation_register.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "deviations": [
    {
      "id": "DEV-001",
      "area": "Dependency | Evidence | Schema | Runtime Artifact Boundary | Test Fake | Other",
      "description": "<what differs from the contract>",
      "reason": "<why accepted>",
      "safety_impact": "none | low | medium | high",
      "compensating_control": "<test/evidence/control>",
      "accepted_status": "NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP",
      "reviewer_decision": "ACCEPTED | REJECTED"
    }
  ]
}
```

Rules:

```text
BLOCKER items cannot be accepted as deviations
missing evidence hashes cannot be accepted as deviations for DONE
runtime artifacts outside .agentx-init/implementation_worker/ require deviation entry
fake dependency behavior must be listed if it limits validation scope
```

---

# 34. Completion Record

Create:

```text
.agentx-init/implementation_worker/llm_worker_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_completion_record.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "component_name": "LLM Implementation Worker",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_worker_subdirectory": "tools/agentx_evolve/workers/llm_implementation_worker/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/implementation_worker/",
  "basis_documents": [
    "LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "model_adapter_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "governed_patch_integration_verified": [],
  "policy_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/implementation_worker/llm_worker_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/implementation_worker/llm_worker_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 35. Acceptance Criteria

The layer is acceptable only if:

```text
all target package files exist
all required schemas exist
all required tests exist
dataclasses instantiate
schemas validate valid examples
schemas reject invalid examples
dependency status is recorded
worker task permission is checked
context package is redacted and budgeted
prompt package contains output schema instructions
model calls go only through Model Adapter
tool calls go only through Tool / MCP Adapter
patch proposals are not applied directly
validation handoff does not run commands directly
model output parser rejects unsafe claims
failure_class is populated for blocked/failed/invalid results
evidence histories are written
latest worker result is written atomically
evidence hashes are written
static bypass scan passes
traceability matrix exists
secrets are redacted before logging
negative tests pass
compileall passes
pytest passes
schema validation passes
git status is clean or only expected runtime artifacts
completion record exists
```

---

# 36. GO / NO-GO Rules

## 36.1 GO Criteria

The worker may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
all required files exist
all required schemas exist
all required tests exist
dependency status artifact exists
context redaction tests pass
prompt package tests pass
model boundary tests pass
tool boundary tests pass
model output parser tests pass
patch proposal tests pass
validation handoff tests pass
fake dependency tests pass
idempotency tests pass
evidence immutability tests pass
negative tests pass
static bypass scan passes
traceability matrix exists
evidence manifest exists
review report exists
completion record exists
required hashes exist
source mutation check passes
no direct provider call exists
no direct shell execution exists
no direct source mutation exists
no direct patch apply exists
no direct Git write exists
no direct network call exists
no BLOCKER remains
```

## 36.2 NO-GO Criteria

The worker must remain NOT DONE if any are true:

```text
reviewed commit is missing
required command exit code is missing
compileall fails
pytest fails
schema validation fails
worker directly writes source files
worker directly applies patches
worker directly executes shell commands
worker directly runs Git write commands
worker directly imports provider clients
worker directly opens network connections
worker bypasses Model Adapter
worker bypasses Tool / MCP Adapter
worker bypasses Governed Patch Execution
worker bypasses Policy / Capability Registry
worker logs unredacted secrets
worker stores unsafe raw model output as durable evidence
worker claims tests passed without tool-validated evidence
worker claims patches were applied
worker evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any BLOCKER remains
```

---

# 37. Implementation Scoring Rubric

Use this only after validation.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Worker package, schemas, tests, runtime paths exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Scoped worker tests pass with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass. |
| Context/prompt handling | 1.0 | Context is scoped, redacted, budgeted, hashed; prompt has output schema. |
| Model boundary | 1.0 | Model Adapter only; no direct provider calls. |
| Tool/patch/validation boundaries | 1.0 | Tool Adapter and Patch Execution boundaries enforced. |
| Policy/failure taxonomy | 1.0 | Policy gates run; failure_class populated. |
| Negative safety coverage | 1.0 | Direct mutation, shell, provider, patch, Git, network bypasses blocked. |
| Evidence/reproducibility | 1.0 | Histories, manifest, review report, hashes, completion record. |

Hard caps:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
direct source mutation caps score at 4.0
direct shell execution caps score at 4.0
direct model provider call caps score at 4.0
direct patch apply caps score at 4.0
unredacted secrets logged caps score at 4.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
any NOT CHECKED required area caps score at 8.0
```

---

# 38. Definition of Done

The LLM Implementation Worker is done when it can safely convert a governed implementation task into a structured implementation plan, patch proposal, and validation handoff without bypassing Agent_X safety layers.

Definition of Done:

```text
worker package exists under canonical subdirectory
all required files exist
all required schemas exist
all required tests exist
task/result/dependency/context/prompt/model/output/plan/patch/handoff schemas validate
worker dispatcher enforces execution flow
dependency status is recorded
Policy / Capability Registry is checked before high-risk actions
Model Adapter is the only model-call path
Tool / MCP Adapter is the only tool-call path
Governed Patch Execution is the only patch-apply path
Failure Taxonomy is used for blocked/failed/invalid results
context is redacted and budgeted
prompt package records output schema instruction
model output is parsed and validated before use
implementation plan is structured and reviewable
patch proposal is structured and not applied directly
validation handoff is structured and not executed directly
runtime evidence is written under .agentx-init/implementation_worker/
evidence hashes are recorded
static bypass scan passes
traceability matrix exists
no direct source mutation occurs
no direct shell execution occurs
no direct Git write occurs
no direct network/provider call occurs
no raw secrets are logged
compileall passes
pytest passes
schema validation passes
review report exists
completion record exists
```

---

# 39. Final Frozen Acceptance Matrix

| Area | Required Result |
|---|---|
| Package location | `tools/agentx_evolve/workers/llm_implementation_worker/` exists |
| Schemas | all required worker schemas exist and validate |
| Tests | all required worker tests exist |
| Worker task | schema-valid and policy-checked |
| Dependency status | recorded before full execution |
| Context handling | relevant, budgeted, redacted, hashed |
| Prompt handling | explicit output schema and forbidden actions |
| Model boundary | Model Adapter only, no direct provider calls |
| Tool boundary | Tool / MCP Adapter only, no direct tool execution |
| Model output | parsed, validated, unsafe claims rejected |
| Patch proposal | structured proposal, not applied directly |
| Validation handoff | structured handoff, no direct command execution |
| Policy integration | blocks unsafe or unauthorized actions |
| Failure taxonomy | failure_class populated |
| Evidence | histories, latest result, manifest, review report, completion record |
| Hashing | SHA-256 hashes present |
| Negative tests | direct mutation, shell, provider, patch, Git, network bypasses blocked |
| Validation | compileall PASS, pytest PASS, schema validation PASS |
| Final state | clean git status or expected runtime artifacts only |

---

# 40. Final Coding-Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] Target repository is Agent_X.
[ ] Worker lives only under tools/agentx_evolve/workers/llm_implementation_worker/.
[ ] Schemas are added under tools/agentx_evolve/schemas/.
[ ] Tests are added under tools/agentx_evolve/tests/.
[ ] Runtime artifacts are written only under .agentx-init/implementation_worker/.
[ ] Worker does not call model providers directly.
[ ] Worker does not execute tools directly.
[ ] Worker does not apply patches directly.
[ ] Worker does not run shell commands directly.
[ ] Worker does not write Git commits, branches, merges, rebases, or pushes.
[ ] Worker does not open network connections.
[ ] Model calls go only through Model Adapter.
[ ] Tool and validation requests go only through Tool / MCP Adapter.
[ ] Patch proposals go only through Governed Patch Execution for handoff/apply.
[ ] Policy Registry blocks unsafe or unauthorized actions.
[ ] Failure classes are populated for every blocked, failed, or invalid result.
[ ] Fake dependencies are restrictive and do not perform real side effects.
[ ] Evidence is append-only, redacted, hashed, and reproducible.
[ ] Validation requires compileall, pytest, schema validation, and clean git status.
```

---

# 41. Final Freeze Rule

This v4 implementation spec is frozen as the implementation-ready handoff for the LLM Implementation Worker.

Allowed future changes:

```text
PATCH: typo fixes, wording improvements, example clarification
MINOR: additive optional tests or optional fields
MAJOR: changed worker authority, changed model-call boundary, changed patch-apply behavior, new required dependency, new runtime artifact root
```

Blocked without major revision:

```text
allowing direct model provider calls
allowing direct source mutation
allowing direct patch application
allowing direct shell execution
allowing direct Git writes
allowing direct network calls
removing Model Adapter boundary
removing Tool / MCP Adapter boundary
removing Policy Registry checks
removing evidence logging
removing hash requirements
```

---

# 42. Allowed Dependency Interface Map

The worker may integrate only through approved local interfaces.

## 42.1 Model Adapter Interface

Allowed dependency names:

```text
tools/agentx_evolve/model_adapter/
agentx_evolve.model_adapter
```

Allowed interaction:

```text
build model request object
call a local Model Adapter function or class that accepts structured request/context
receive structured model response
receive evidence refs where available
```

Forbidden interaction:

```text
direct provider SDK import
direct HTTP call
direct local model runtime import
direct provider key lookup
direct environment credential lookup
direct GPU/runtime selection
```

Import failure behavior:

```text
return BLOCKED
failure_class = WORKER_MODEL_CALL_FAILED or WORKER_MODEL_POLICY_DENIED
record dependency_status.model_adapter = FAILED or MISSING
do not call any fallback provider
```

## 42.2 Tool / MCP Adapter Interface

Allowed dependency names:

```text
tools/agentx_evolve/tools/
agentx_evolve.tools
```

Allowed interaction:

```text
construct ToolCall-compatible request
submit request to Tool / MCP Adapter dispatcher
receive schema-valid ToolResult
store evidence refs
```

Forbidden interaction:

```text
direct wrapper import to execute a tool
direct filesystem mutation
direct subprocess execution
direct Git command
direct MCP server call
```

Import failure behavior:

```text
return BLOCKED
failure_class = WORKER_TOOL_REQUEST_DENIED
record dependency_status.tool_adapter = FAILED or MISSING
do not execute fallback commands
```

## 42.3 Policy / Capability Registry Interface

Allowed dependency names:

```text
tools/agentx_evolve/policy/
agentx_evolve.policy
```

Allowed interaction:

```text
check worker task permission
check model call permission
check patch proposal permission
check validation handoff permission
receive ALLOW / BLOCK / NEEDS_GOVERNANCE / NEEDS_APPROVAL / DRY_RUN_ONLY
```

Import failure behavior:

```text
enter restricted mode
block model calls
block tool calls
block patch handoff
block validation execution
allow schema/context-only dry-run behavior
```

## 42.4 Governed Patch Execution Interface

Allowed dependency names:

```text
tools/agentx_evolve/patch_execution/
agentx_evolve.patch_execution
```

Allowed interaction:

```text
submit structured patch proposal or governed patch request
receive accepted/rejected/blocked handoff result
store evidence refs
```

Forbidden interaction:

```text
apply patch directly
write diff to source path directly
call git apply
call patch command
edit target file directly
```

Import failure behavior:

```text
patch proposal may be written as reviewable artifact
patch handoff BLOCKS
source mutation remains impossible
```

## 42.5 Failure Taxonomy Interface

Allowed dependency names:

```text
tools/agentx_evolve/failure_taxonomy/
agentx_evolve.failure_taxonomy
```

Allowed interaction:

```text
map worker failure to standard failure class
retrieve recovery hint
attach failure_class to result
```

Import failure behavior:

```text
use local worker failure constants
record warning
do not omit failure_class
```

---

# 43. Timeout, Retry, and Output-Size Limits

The implementation must define hard limits in `worker_config.py`.

Required defaults:

```text
MODEL_CALL_TIMEOUT_SECONDS = 120
MODEL_CALL_MAX_RETRIES = 0
TOOL_REQUEST_TIMEOUT_SECONDS = 60
TOOL_REQUEST_MAX_RETRIES = 0
PATCH_HANDOFF_TIMEOUT_SECONDS = 60
PATCH_HANDOFF_MAX_RETRIES = 0
VALIDATION_HANDOFF_TIMEOUT_SECONDS = 60
VALIDATION_HANDOFF_MAX_RETRIES = 0
MAX_CONTEXT_CHARS_DEFAULT = 120000
MAX_PROMPT_CHARS_DEFAULT = 140000
MAX_MODEL_OUTPUT_CHARS_DEFAULT = 80000
MAX_SAFE_SUMMARY_CHARS = 12000
MAX_EVIDENCE_FIELD_CHARS = 20000
```

Rules:

```text
retries default to zero
retry requires explicit policy approval
timeout must produce schema-valid FAILED or BLOCKED result
oversized output must be summarized, truncated, or rejected
truncation must be recorded in evidence
unbounded model output is forbidden
unbounded tool output is forbidden
```

---

# 44. Static Bypass Scan Requirement

The worker implementation must include a static bypass scan test.

Required artifact:

```text
.agentx-init/implementation_worker/llm_worker_static_bypass_scan.json
```

Required scan coverage:

```text
worker package source files
worker tests
worker helper modules
```

The scan must reject direct use of:

```text
openai
anthropic
google.generativeai
google.genai
requests
httpx
urllib.request
socket
subprocess
os.system
pty
pexpect
git push
git commit
git merge
git rebase
git reset
git clean
git apply
patch -p
shutil.copy into source paths
Path.write_text into source paths
Path.write_bytes into source paths
open(..., "w") into source paths
```

Allowed exceptions:

```text
test fixtures may contain forbidden strings only as inert strings used to prove rejection
worker_logger may write only under .agentx-init/implementation_worker/
schema files may contain examples of forbidden text only as test data
```

Any exception must be recorded in:

```text
llm_worker_deviation_register.json
```

A failed static bypass scan is a BLOCKER.

---

# 45. Validation Command Allowlist

Validation handoff may request only allowlisted commands.

Allowed base commands:

```text
python -m compileall
python -m pytest
python <schema validation script>
git status --short
```

Allowed scoped command examples:

```text
PYTHONPATH=tools python -m compileall tools/agentx_evolve/workers/llm_implementation_worker
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_llm_worker_models.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_worker_schemas.py
git status --short
```

Forbidden validation commands:

```text
shell pipelines
command chaining
curl
wget
ssh
scp
rm
mv into source paths
chmod
sudo
git add
git commit
git push
git merge
git rebase
git reset
git clean
python -c with arbitrary code
bash -c
sh -c
node
bun
npm
npx
```

Rules:

```text
validation handoff builds requests only
Tool / MCP Adapter decides execution
worker must not execute validation itself
unknown validation command returns BLOCKED
command with shell metacharacters returns BLOCKED
```

---

# 46. Retention, Redaction, and Raw Payload Rules

The worker must avoid durable storage of unsafe raw payloads.

## 46.1 Context Package Retention

Allowed:

```text
context summary
redacted context chunks
file refs
artifact refs
context hash
truncation report
redaction report
prompt-injection report
```

Forbidden:

```text
unredacted secrets
full raw private credentials
raw environment variables
unbounded full file dumps
```

## 46.2 Prompt Package Retention

Allowed:

```text
prompt hash
safe prompt summary
output schema instruction
forbidden action list
required section list
context package ref
```

Allowed only if redacted:

```text
full prompt text
task prompt
developer contract
system contract
```

Forbidden:

```text
prompt text containing secrets
prompt text containing provider credentials
unbounded prompt storage
```

## 46.3 Model Response Retention

Allowed:

```text
safe summary
parsed structured output
raw_response_ref only if stored by Model Adapter under its own rules
model_response_hash
usage summary
warnings/errors
```

Forbidden:

```text
unredacted raw model output containing secrets
raw model output treated as executable instruction
raw provider response durably copied into worker logs without redaction
```

---

# 47. Path Normalization and Target Scope Rules

Every target path in plan, patch proposal, and validation handoff must be normalized and checked.

Required path checks:

```text
reject absolute paths unless explicitly approved by policy
reject ../ traversal
reject symlink escape if path resolution is available
reject paths outside repository root
reject paths outside task target scope unless policy allows
reject writes to L0 unless explicit governance exists
reject writes to .git
reject writes to .venv, node_modules, cache, build output, or ignored runtime folders unless explicitly allowed
```

Patch proposal must record:

```text
original_path
normalized_path
path_decision
path_decision_reason
```

If any target path is invalid:

```text
PatchProposal status or worker result must be BLOCKED / INVALID
failure_class = WORKER_PATCH_PROPOSAL_INVALID
```

---

# 48. Model Output Conflict and Ambiguity Rules

The model output parser must reject ambiguous or conflicting implementation instructions.

Reject if model output contains:

```text
multiple incompatible patch proposals
files_to_change contradicts patch_proposal.target_files
validation commands contradict allowed command list
implementation plan says no source change but patch proposal changes source
patch proposal targets files outside task target scope
model says tests passed but no validation evidence exists
model says patch applied but no patch execution evidence exists
```

Allowed behavior:

```text
return INVALID / FAILED
record rejected_content entries
ask orchestrator for a new task or cleaner model output later
do not guess which conflicting patch proposal is correct
```

---

# 49. Contract-to-Code-to-Test Traceability Matrix

Create:

```text
.agentx-init/implementation_worker/llm_worker_traceability_matrix.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "llm_worker_traceability_matrix.schema.json",
  "component_id": "AGENTX_LLM_IMPLEMENTATION_WORKER",
  "created_at": "<UTC timestamp>",
  "rows": [
    {
      "requirement_id": "REQ-001",
      "requirement": "Model calls go only through Model Adapter.",
      "implementation_files": [],
      "test_files": [],
      "evidence_refs": [],
      "status": "PASS | PARTIAL | FAIL | NOT CHECKED"
    }
  ],
  "warnings": [],
  "errors": []
}
```

Minimum required traceability rows:

```text
worker package exists
schemas exist
tests exist
dependency status recorded
context redacted
prompt schema instruction present
model adapter boundary enforced
tool adapter boundary enforced
patch execution boundary enforced
validation command allowlist enforced
model output parser rejects unsafe claims
path traversal rejected
failure_class populated
evidence hashes written
static bypass scan passes
negative tests pass
completion record exists
```

A final DONE verdict is invalid if the traceability matrix is missing.

---

# 50. Review Readiness Checkpoints

Before the later post-implementation review / DoD document is used, implementation must produce:

```text
compileall output with exit code
pytest output with exit code
schema validation output with exit code
static bypass scan artifact
traceability matrix
dependency status artifact
evidence manifest
review report
completion record
git status output
```

The review must be able to answer:

```text
what exists
what passed
what failed
which commit was reviewed
which commands were run
whether model boundary was enforced
whether tool boundary was enforced
whether patch boundary was enforced
whether direct mutation was blocked
whether direct shell was blocked
whether direct provider calls were blocked
whether secrets were redacted
whether evidence hashes are present
whether final verdict is DONE or NOT DONE
```

If any checkpoint is missing:

```text
final verdict = NOT DONE
```


---

# 51. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, files, schemas, classes, public functions, worker modes, dependency gates, restricted mode, fake dependency contracts, model-call boundary, tool-call boundary, prompt/context handling, strict model-output validation, implementation-plan generation, patch-proposal generation, validation handoff, runtime artifacts, evidence hashing, review artifacts, integrations, tests, negative tests, implementation order, acceptance criteria, GO / NO-GO rules, scoring rubric, and Definition of Done.
```
