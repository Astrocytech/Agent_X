# MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_MODEL_ADAPTER
component_name: Model Adapter Layer
roadmap_layer: 6
roadmap_phase: Phase C — Model Integration
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Hosted Provider Acceptance Criteria, Local Runtime Acceptance Criteria, Prompt Contract Acceptance Criteria, Tool / MCP Adapter Acceptance Criteria
risk_level: critical
implementation_mode: governed model access layer for local and optional hosted LLM providers
target_language: Python
canonical_subdirectory: tools/agentx_evolve/models/
runtime_profile_subdirectory: tools/agentx_evolve/model_runtime/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/model_calls/
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 contract was strong and close to implementation-ready. I would rate it:

```text
9.7/10
```

It already covered the core safety architecture for local and hosted model use, schema-controlled model requests and responses, provider transport policy, credential-reference handling, deterministic test doubles, concurrency/idempotency, evidence hashing, OpenCode borrowing boundaries, Agent_X integration notes, and a precise Definition of Done.

## 0.2 Why v2 Was Not Fully 10/10

The remaining gaps were precision and implementation-handoff gaps:

```text
1. The contract listed a runtime profile subdirectory but did not clearly separate which runtime files belong in the Model Adapter layer versus the later Local Model Runtime Profile Layer.
2. The ModelDefinition, ModelProviderProfile, ModelPolicyDecision, ModelRetryRecord, InvalidModelRequestRecord, and ModelAuditEvent schemas were listed but not defined with enough required fields.
3. The provider adapter boundary needed a stricter rule that adapters return ModelResponse only and cannot leak provider-native objects, raw exceptions, credentials, or streamed chunks.
4. The contract needed a clearer capability-to-task matrix for small_fast, small_coder, medium_coder_optional, hosted_fallback_optional, and test_double profiles.
5. It needed stronger rules for model-output-to-tool-call suggestions so model output can contain proposals but never executable tool authority.
6. Evidence manifest and completion record requirements needed stricter required fields and SHA-256 hash coverage, aligned with the Tool / MCP Adapter review standard.
7. It needed a stricter validation/deviation vocabulary for real-provider deferral, hosted-provider deferral, and test-double-only base validation.
8. It needed a final frozen acceptance matrix to prevent the implementation spec from drifting into broad redesign.
```

## 0.3 v3 Improvements

This v3 adds:

```text
runtime boundary clarification
exact Model Adapter ownership rules
missing schema contracts for model/provider/policy/retry/audit records
provider adapter boundary rules
capability-to-task matrix
model-output-to-tool-call proposal rules
evidence manifest and completion record schema requirements
stricter real-provider deferral and test-double-only rules
final frozen acceptance matrix
```

Final v3 rating:

```text
10/10
```
---

# 1. Purpose

This document defines the controlling contract for the **Model Adapter Layer** in the Agent_X self-evolving system.

The Model Adapter Layer connects Agent_X to local or hosted language models through a replaceable, policy-controlled interface. It must allow the future Context Builder, LLM Implementation Worker, and Self-Evolution Orchestrator to request model output without giving the model direct authority over files, tools, commands, governance, approval, patch application, promotion, or network access.

This layer is safety-critical because it controls:

```text
which models may be used
which model providers may be used
which task types each model may handle
which context may be sent to a model
whether local-only mode is enforced
whether hosted fallback is allowed
whether prompt payloads are schema-valid
whether outputs are schema-valid
whether invalid output is retried or rejected
whether secrets are redacted before model use
whether model calls are evidenced
whether model output can request tool calls, patches, or source changes
```

The Model Adapter must not become a shortcut around Agent_X governance. It is a model-call boundary, not an implementation authority.

---

# 2. Scope

## 2.1 Required in This Layer

The Model Adapter Layer must define and implement contracts for:

```text
model registry
model provider profiles
model capability profiles
model runtime profiles
model request schema
model response schema
model selection policy
model permission matrix
local model provider adapters
hosted provider adapters, disabled by default
OpenAI-compatible local server adapter
Ollama adapter
LM Studio adapter
OpenCode-compatible provider adapter, if useful and safe
JSON-only prompt runner
output schema validator
retry policy for invalid structured output
prompt/context boundary checks
model call audit/evidence
invalid model request handling
blocked model request handling
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
Context Builder / Task Packer
LLM Implementation Worker
Self-Evolution Orchestrator
prompt template/version management beyond request validation
source mutation
patch generation authority
patch application
file writes
command execution
Git operations
tool execution
human approval UI
promotion gate
background daemon
model fine-tuning
training loop
```

The Model Adapter can return model output. It cannot decide whether that output should be applied.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because this layer controls access to model behavior that can influence future code changes.

EQC applies to:

```text
provider access
model selection
model permissions
prompt boundaries
context redaction
hosted-provider blocking
local runtime limits
structured-output validation
retry limits
evidence completeness
failure classification
unsafe output rejection
```

The layer must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete implementation files and public APIs.

Expected files include:

```text
tools/agentx_evolve/models/__init__.py
tools/agentx_evolve/models/model_models.py
tools/agentx_evolve/models/model_registry.py
tools/agentx_evolve/models/model_policy.py
tools/agentx_evolve/models/model_selector.py
tools/agentx_evolve/models/model_request_validator.py
tools/agentx_evolve/models/model_response_validator.py
tools/agentx_evolve/models/model_call_logger.py
tools/agentx_evolve/models/prompt_runner.py
tools/agentx_evolve/models/json_output_validator.py
tools/agentx_evolve/models/model_retry_policy.py
tools/agentx_evolve/models/local_provider_adapter.py
tools/agentx_evolve/models/ollama_adapter.py
tools/agentx_evolve/models/lmstudio_adapter.py
tools/agentx_evolve/models/openai_compatible_adapter.py
tools/agentx_evolve/models/opencode_provider_adapter.py
tools/agentx_evolve/models/hosted_model_adapter.py
tools/agentx_evolve/models/invalid_model_request.py
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, safety limits, and tests.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects multiple subsystems:

```text
Policy / Capability Registry
Tool / MCP Adapter Layer
Local Model Runtime Profile Layer
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
LLM Implementation Worker
Failure Taxonomy / Recovery Playbook
Security Sandbox / Filesystem Boundary Layer
Monitoring / Observability Layer
Self-Evolution Orchestrator
```

The Model Adapter is an integration boundary. It must not independently make governance, patch, tool, or promotion decisions.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because every model request and response must be structured.

Required schemas include:

```text
model_registry.schema.json
model_definition.schema.json
model_provider_profile.schema.json
model_capability_profile.schema.json
model_runtime_profile.schema.json
model_request.schema.json
model_response.schema.json
model_selection_decision.schema.json
model_policy_decision.schema.json
model_retry_record.schema.json
model_audit.schema.json
invalid_model_request.schema.json
model_call_evidence_manifest.schema.json
model_adapter_review_report.schema.json
model_adapter_completion_record.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every model call attempt must create evidence.

Evidence is required for:

```text
allowed model request
blocked model request
invalid model request
invalid model response
hosted-provider blocked request
local-runtime blocked request
policy-denied model call
context-boundary violation
secret-redaction event
retry after invalid JSON
final rejected output
provider execution failure
timeout
model selection decision
```

---

# 4. Why This Layer Needs These Standards

The Model Adapter Layer is safety-critical because a model may generate implementation suggestions, patch candidates, tests, explanations, or validation-repair proposals.

A model must be treated as an untrusted proposal generator.

The layer must enforce:

```text
model output is not authority
model output is not automatically trusted
model output cannot directly mutate files
model output cannot directly call tools
model output cannot directly execute commands
model output cannot approve governance
model output cannot approve itself
model output cannot promote changes
model output must match the requested schema
model output must stay within the requested task type
model context must be bounded and redacted
hosted model calls must be disabled unless explicitly enabled
network/provider access must be disabled by default
```

---

# 5. Preconditions and Dependency Gates

## 5.1 Required Prior Components

Before the Model Adapter is used in a self-evolution loop, these components should exist and be validated:

```text
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter Layer
Security Sandbox / Filesystem Boundary Layer
```

Before it is used with small local models in practice, this component should exist:

```text
Local Model Runtime Profile Layer
```

Before it receives real implementation tasks, these components should exist:

```text
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer, if prompt templates are externalized
```

## 5.2 Restricted Mode

If upstream dependencies are missing, the Model Adapter may run in restricted mode.

Restricted mode allows:

```text
model registry loading
model profile validation
model request schema validation
model response schema validation
local dry-run request validation
model selection simulation
JSON output validation using static examples
invalid request handling
evidence logging
```

Restricted mode blocks:

```text
hosted provider calls
network access
model calls requiring unavailable runtime profiles
tool-call generation as executable authority
source mutation
command execution
patch application
approval or promotion decisions
```

## 5.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> hosted and non-read-only generation tasks BLOCK.
If Local Model Runtime Profile is missing -> local model execution may BLOCK or run only with explicit test doubles.
If Context Builder is missing -> no whole-repo prompts; only supplied bounded task packets may be used.
If Prompt Contract is missing -> inline prompts must still be schema-validated and evidenced.
If Failure Taxonomy is missing -> failures use MODEL_FAILURE_UNCLASSIFIED but still BLOCK when safety is uncertain.
If hosted provider configuration is missing -> hosted calls BLOCK.
If network mode is disabled -> hosted calls BLOCK.
```

## 5.4 Authority Rule

Model selection does not grant execution authority.

A model request is allowed only when all required authorities agree:

```text
Model Registry
Policy / Capability Registry
Model Runtime Profile
Context Boundary Rules
Provider Policy
Prompt Contract, when applicable
Output Schema Contract
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_POLICY
NEEDS_RUNTIME_PROFILE
NEEDS_CONTEXT_BOUNDARY
NEEDS_HOSTED_PROVIDER_APPROVAL
ALLOW_LOCAL_ONLY
ALLOW
```

---

# 6. Model Provider Policy

## 6.1 Provider Types

The layer may support these provider types:

```text
LOCAL_IN_PROCESS
LOCAL_HTTP_OPENAI_COMPATIBLE
OLLAMA
LM_STUDIO
OPENCODE_COMPATIBLE
HOSTED_OPENAI_COMPATIBLE
HOSTED_PROVIDER_OTHER
TEST_DOUBLE
```

## 6.2 Default Provider Policy

Default provider mode:

```text
local_only
```

Default behavior:

```text
local providers may be configured
hosted providers are disabled
network calls are disabled
provider credentials are not required
no provider is called unless explicitly selected and policy-approved
```

## 6.3 Hosted Provider Policy

Hosted provider calls are allowed only if all are true:

```text
hosted providers are explicitly enabled
network mode is explicitly enabled
provider profile exists
provider endpoint is allowlisted
credential source is configured safely
request task type allows hosted provider use
context redaction passes
policy decision allows hosted use
evidence logging is active
```

Hosted provider calls must block if:

```text
network mode is local_only
provider endpoint is unknown
provider credentials would be logged
context includes unredacted secrets
policy decision is missing
hosted fallback is requested silently
```

## 6.4 OpenAI-Compatible Provider Policy

OpenAI-compatible providers may be local or hosted.

The adapter must distinguish:

```text
local OpenAI-compatible server, such as LM Studio or local llama.cpp-compatible server
hosted OpenAI-compatible endpoint
```

Local OpenAI-compatible servers may be allowed in local-only mode if endpoint policy allows loopback/local addresses.

Hosted OpenAI-compatible endpoints require hosted-provider approval.

## 6.5 OpenCode-Compatible Provider Policy

OpenCode-compatible provider ideas may be borrowed for adapter shape and provider abstraction.

The Model Adapter must not require:

```text
OpenCode runtime
Bun
Node
OpenCode provider registry as a runtime dependency
unbounded provider auto-discovery
network provider access by default
```

---

# 7. Local Model Policy

Local models are preferred for the first working version because Agent_X must support limited hardware.

Required local profiles:

```text
small_fast
small_coder
medium_coder_optional
hosted_fallback_optional
```

Recommended runtime capability classes:

```text
cpu_only_safe
small_gpu_8gb
balanced_local
hosted_fallback_optional
```

Local model policy must enforce:

```text
one active local model at a time unless explicitly configured otherwise
small bounded context packets
no whole-repo prompts
short JSON outputs
bounded retries
model timeout
max prompt tokens
max output tokens
VRAM-aware model selection when runtime profile exists
local model failure returns schema-valid FAILED or BLOCKED result
```

Local model calls must not:

```text
read files directly
write files directly
execute commands
load arbitrary local paths without policy
log raw prompts with secrets
log raw outputs if they contain secrets
```

---

# 8. Hosted Model Policy

Hosted models are optional and disabled by default.

Hosted fallback must be explicit.

Allowed hosted use cases, only with policy approval:

```text
large-context reasoning over already-redacted task packets
schema repair for invalid local output
complex explanation generation
optional review assistance
```

Forbidden hosted use cases by default:

```text
sending whole repository content
sending secrets or credentials
sending private runtime artifacts without redaction
using hosted model as default provider
using hosted model to approve changes
using hosted model to bypass small-local-model constraints
```

Hosted model response must be treated the same as local response:

```text
untrusted until schema-valid
not allowed to mutate files
not allowed to execute tools
not allowed to approve itself
not allowed to promote changes
```

---

# 9. Model Capability Profile Schema Contract

A model capability profile defines what a model is allowed to do.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_capability_profile.schema.json",
  "profile_id": "string",
  "model_id": "string",
  "provider_id": "string",
  "capability_class": "SMALL_FAST|SMALL_CODER|MEDIUM_CODER_OPTIONAL|HOSTED_FALLBACK_OPTIONAL|TEST_DOUBLE",
  "allowed_task_types": [],
  "blocked_task_types": [],
  "supports_json_mode": false,
  "supports_tool_call_format": false,
  "supports_streaming": false,
  "max_context_tokens": 0,
  "max_output_tokens": 0,
  "requires_local_runtime_profile": true,
  "allows_hosted_use": false,
  "allows_code_generation": false,
  "allows_test_generation": false,
  "allows_validation_repair": false,
  "allows_explanation": true,
  "writes_source": false,
  "runs_tools": false,
  "runs_commands": false,
  "uses_network": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
writes_source must always be false in this layer.
runs_tools must always be false in this layer.
runs_commands must always be false in this layer.
uses_network may be true only for hosted profiles and must require hosted-provider policy approval.
```

---

# 10. Model Runtime Profile Schema Contract

A model runtime profile defines what the current machine/provider can safely run.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_runtime_profile.schema.json",
  "runtime_profile_id": "string",
  "runtime_class": "CPU_ONLY_SAFE|SMALL_GPU_8GB|BALANCED_LOCAL|HOSTED_FALLBACK_OPTIONAL|TEST_RUNTIME",
  "provider_type": "LOCAL_IN_PROCESS|LOCAL_HTTP_OPENAI_COMPATIBLE|OLLAMA|LM_STUDIO|OPENCODE_COMPATIBLE|HOSTED_OPENAI_COMPATIBLE|TEST_DOUBLE",
  "local_only": true,
  "network_allowed": false,
  "max_loaded_models": 1,
  "max_context_tokens": 0,
  "max_output_tokens": 0,
  "timeout_seconds": 0,
  "max_retries": 0,
  "vram_budget_gb": null,
  "cpu_threads": null,
  "endpoint": null,
  "endpoint_allowlisted": false,
  "credential_ref": null,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
local_only=true blocks hosted provider calls.
network_allowed=false blocks hosted provider calls.
max_loaded_models defaults to 1.
credential_ref must be a reference only, never a raw credential.
endpoint must be allowlisted before use.
```

---

# 11. Model Request Schema Contract

Every model request must be structured.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_request.schema.json",
  "model_request_id": "string",
  "timestamp": "string",
  "source_component": "ModelAdapter",
  "caller_role": "ORCHESTRATOR|LLM_IMPLEMENTATION_WORKER|REVIEWER_ASSISTANT|CONTEXT_BUILDER|UNKNOWN_CALLER",
  "caller_id": "string|null",
  "session_id": "string|null",
  "task_type": "IMPLEMENT_PATCH|FIX_VALIDATION|WRITE_TEST|EXPLAIN_FAILURE|SUMMARIZE_CONTEXT|REPAIR_JSON|CLASSIFY_FAILURE|REVIEW_OUTPUT|DRY_RUN",
  "model_id": "string|null",
  "provider_id": "string|null",
  "runtime_profile_id": "string|null",
  "prompt": "string",
  "context_packet_ref": "string|null",
  "context_summary": "string|null",
  "output_schema_id": "string|null",
  "json_only": true,
  "temperature": 0.0,
  "max_output_tokens": 0,
  "timeout_seconds": 0,
  "dry_run": false,
  "policy_decision_id": "string|null",
  "redaction_decision_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
model_request_id is required.
task_type is required.
prompt is required but must be redacted before durable logging.
UNKNOWN_CALLER blocks by default.
json_only=true is required for implementation-affecting task types.
context_packet_ref is preferred over embedding large context directly.
```

---

# 12. Model Response Schema Contract

Every model response must be structured.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_response.schema.json",
  "model_response_id": "string",
  "model_request_id": "string",
  "timestamp": "string",
  "source_component": "ModelAdapter",
  "model_id": "string",
  "provider_id": "string",
  "runtime_profile_id": "string|null",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "output_text": "string|null",
  "output_json": {},
  "output_schema_id": "string|null",
  "json_valid": false,
  "schema_valid": false,
  "retry_count": 0,
  "prompt_hash": "string|null",
  "output_hash": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
invalid JSON returns INVALID or FAILED, not SUCCESS.
schema-invalid output returns INVALID or FAILED, not SUCCESS.
model output that requests forbidden actions is rejected.
prompt_hash and output_hash are required for completed calls.
raw prompt and raw output may be omitted or redacted from durable evidence.
```

---

# 13. Model Registry Schema Contract

The model registry defines available model profiles.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_registry.schema.json",
  "registry_id": "string",
  "registry_version": "string",
  "created_at": "string",
  "source_component": "ModelRegistry",
  "models": [],
  "provider_profiles": [],
  "capability_profiles": [],
  "runtime_profiles": [],
  "warnings": [],
  "errors": []
}
```

Registry rules:

```text
model IDs must be unique.
provider IDs must be unique.
capability profiles must reference known model IDs.
runtime profiles must reference known provider types.
duplicate model IDs block registry loading.
hosted profiles must be disabled unless explicitly enabled by policy.
```

---

# 14. Model Selection Policy

The Model Adapter must choose a model deterministically from:

```text
task_type
caller_role
policy context
runtime profile
provider availability
model capability profile
context size
output schema requirement
local-only / hosted-allowed mode
```

Default selection order:

```text
1. Explicit model_id if policy-approved and compatible.
2. small_coder for implementation-related structured JSON tasks.
3. small_fast for classification, summary, and simple repair tasks.
4. medium_coder_optional if locally available and policy-approved.
5. hosted_fallback_optional only if explicitly enabled and policy-approved.
6. BLOCK if no safe model is available.
```

Model selection must return a structured decision:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_selection_decision.schema.json",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "ModelSelector",
  "task_type": "string",
  "selected_model_id": "string|null",
  "selected_provider_id": "string|null",
  "decision": "ALLOW|BLOCK|NEEDS_RUNTIME_PROFILE|NEEDS_HOSTED_PROVIDER_APPROVAL|NEEDS_CONTEXT_REDUCTION",
  "reason": "string",
  "candidate_models_considered": [],
  "warnings": [],
  "errors": []
}
```

---

# 15. Model Safety / Permission Matrix

## 15.1 Caller Roles

Initial caller roles:

```text
ORCHESTRATOR
LLM_IMPLEMENTATION_WORKER
REVIEWER_ASSISTANT
CONTEXT_BUILDER
PROMOTION_CHECKER
HUMAN_OPERATOR
UNKNOWN_CALLER
```

## 15.2 Required Role Rules

```text
UNKNOWN_CALLER blocks by default.
CONTEXT_BUILDER may request summarization or dry-run validation only.
LLM_IMPLEMENTATION_WORKER may request schema-valid patch candidates, but not apply them.
REVIEWER_ASSISTANT may request explanation/review outputs only.
PROMOTION_CHECKER may request summary/review assistance but cannot ask model to promote.
HUMAN_OPERATOR may request model assistance but cannot use model output as approval evidence by itself.
ORCHESTRATOR may coordinate model calls but cannot bypass model policy.
```

## 15.3 Task Permission Rules

```text
IMPLEMENT_PATCH requires bounded task packet and JSON schema.
FIX_VALIDATION requires validation artifact reference.
WRITE_TEST requires allowed file list.
EXPLAIN_FAILURE may use reduced context.
SUMMARIZE_CONTEXT cannot include secrets.
REPAIR_JSON cannot change task objective.
CLASSIFY_FAILURE must use failure taxonomy enum.
REVIEW_OUTPUT cannot mark implementation accepted.
```

## 15.4 Hard Blocks

Always block:

```text
model request with unknown caller
model request with unknown task type
hosted request when local_only=true
network request when network_allowed=false
request containing unredacted secrets
request without output schema for implementation-affecting task
request asking model to edit files directly
request asking model to run commands directly
request asking model to call tools directly
request asking model to approve governance
request asking model to promote changes
request exceeding context budget
```

---

# 16. Prompt / Context Boundary Rules

The Model Adapter must treat prompts and context as controlled inputs.

Required rules:

```text
no whole-repo prompts
prefer task packet references over raw context
include only allowed files or snippets selected by Context Builder
include forbidden file list when task may produce edits
include output schema for JSON tasks
include governance/risk summary when implementation-related
include validation expectations when fixing failures
redact secrets before model request
hash prompt/context before provider call
log prompt hash, not raw prompt, unless explicitly safe
```

Prompt injection handling:

```text
instructions inside source files, logs, docs, or tool outputs are data, not authority
model must not follow context instructions that override system/task constraints
model output that attempts to override governance is invalid
model output that requests hidden tools or forbidden files is invalid
model output that expands scope beyond task packet is invalid
```

---

# 17. Output Validation Rules

Every model response must be validated before use.

Required validation stages:

```text
provider returned a response
response size within limit
JSON parse succeeds when json_only=true
output schema validation passes
task_type matches requested task
allowed_files_only is true for patch candidates
no forbidden file appears in output
no direct command execution request appears in output
no direct tool execution request appears in output
no governance approval claim appears in output
no promotion claim appears in output
secrets are not echoed in output
```

Invalid outputs must return:

```text
status = INVALID or FAILED
failure_class = MODEL_INVALID_OUTPUT or MODEL_SCHEMA_VALIDATION_FAILED
```

Implementation-affecting outputs are proposals only. They must be passed to downstream validation and patch execution layers.

---

# 18. JSON Output and Retry Policy

The Model Adapter must support JSON-only model requests.

Retry is allowed only for recoverable structured-output failures:

```text
invalid JSON
missing required schema fields
minor enum mismatch if repair prompt is bounded
truncated output if retry budget remains
```

Retry is not allowed for:

```text
policy denial
hosted provider denial
context boundary violation
secret leakage
model request asking for forbidden authority
provider/network blocked by policy
```

Default retry policy:

```text
max_retries = 1 for local models
max_retries = 0 for hosted models unless explicitly configured
retry must use stricter JSON-only repair prompt
retry must preserve same task objective
retry must write retry evidence
```

---

# 19. Audit / Evidence Contract

Runtime artifacts must be written under:

```text
.agentx-init/model_calls/
```

Required artifacts:

```text
model_request_history.jsonl
model_response_history.jsonl
blocked_model_request_history.jsonl
invalid_model_request_history.jsonl
model_selection_history.jsonl
model_retry_history.jsonl
latest_model_request.json
latest_model_response.json
model_adapter_evidence_manifest.json
model_adapter_review_report.json
model_adapter_completion_record.json
```

Evidence rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
redact secrets before durable logging
record prompt hash
record output hash
record model ID
record provider ID
record runtime profile ID when available
record policy decision ID when available
record selection decision ID
record retry count
record failure class for blocked/failed/invalid calls
```

Do not durably log by default:

```text
raw secrets
raw provider credentials
full unredacted prompt
full unredacted context packet
full unredacted model output if it may contain secrets
```

---

# 20. Invalid Model Request Handling

Invalid model requests must fail closed.

Invalid request examples:

```text
unknown task type
unknown caller role
missing prompt
missing output schema for implementation task
requested hosted model while hosted disabled
requested provider not in registry
requested model not in registry
context exceeds budget
prompt contains unredacted secret
request asks model to mutate files
request asks model to execute command
request asks model to approve/promote changes
```

Required result:

```text
status = INVALID or BLOCKED
failure_class = MODEL_REQUEST_INVALID, MODEL_POLICY_DENIED, MODEL_CONTEXT_BOUNDARY_DENIED, or MODEL_PROVIDER_BLOCKED
evidence is written
no provider call occurs
```

Must not:

```text
attempt provider call anyway
guess replacement model without policy
silently downgrade to hosted fallback
log raw unsafe prompt
raise unhandled exception
```

---

# 21. Failure Taxonomy Integration

Model failures must map to standard failure classes.

Required failure classes:

```text
MODEL_NOT_FOUND
MODEL_PROVIDER_NOT_FOUND
MODEL_REQUEST_INVALID
MODEL_POLICY_DENIED
MODEL_PROVIDER_BLOCKED
MODEL_HOSTED_PROVIDER_DISABLED
MODEL_CONTEXT_BOUNDARY_DENIED
MODEL_CONTEXT_TOO_LARGE
MODEL_SECRET_DETECTED
MODEL_RUNTIME_UNAVAILABLE
MODEL_PROVIDER_CALL_FAILED
MODEL_TIMEOUT
MODEL_INVALID_JSON
MODEL_SCHEMA_VALIDATION_FAILED
MODEL_INVALID_OUTPUT
MODEL_RETRY_EXHAUSTED
MODEL_OUTPUT_FORBIDDEN_ACTION
UNKNOWN_MODEL_FAILURE
```

Recovery hints:

```text
MODEL_INVALID_JSON -> retry with stricter JSON-only prompt if retry budget remains
MODEL_CONTEXT_TOO_LARGE -> rebuild smaller task packet
MODEL_RUNTIME_UNAVAILABLE -> select another local-compatible profile or block
MODEL_HOSTED_PROVIDER_DISABLED -> block; do not fallback silently
MODEL_OUTPUT_FORBIDDEN_ACTION -> reject output and audit
MODEL_POLICY_DENIED -> block and audit
MODEL_SECRET_DETECTED -> block and require redaction
```

---

# 22. OpenCode Borrowing Notes

## 22.1 Concepts to Borrow

Borrow these OpenCode-style concepts:

```text
provider abstraction
model registry / provider registry idea
OpenAI-compatible provider shape
model-specific configuration
JSON-oriented agent output expectations
provider fallback concept, but only with policy approval
separation between model provider and tool execution
session-level model metadata
```

## 22.2 Concepts to Restrict

Do not copy these assumptions directly:

```text
broad provider auto-discovery
network/provider access by default
hosted fallback without explicit approval
model-selected tools without Agent_X policy
provider plugins loaded without governance
model output treated as executable action
OpenCode runtime dependency
Bun or Node runtime dependency
```

## 22.3 Agent_X Mapping

| OpenCode concept | Agent_X equivalent | Required control |
|---|---|---|
| Provider abstraction | Model provider adapter | Policy + runtime profile |
| OpenAI-compatible providers | `openai_compatible_adapter.py` | local/hosted distinction |
| Local model routing | `model_selector.py` | runtime budget + capability profile |
| JSON agent output | `json_output_validator.py` | schema validation |
| Provider fallback | hosted fallback optional | explicit policy approval |
| Model/tool loop | downstream orchestrator only | no direct tool execution in this layer |
| Model config | model registry/profile schemas | evidence + validation |

OpenCode may be used as a design reference only. Do not copy OpenCode source code.

---

# 23. Agent_X Integration Notes

## 23.1 Policy / Capability Registry Integration

The Model Adapter must check policy before model use.

Policy must decide:

```text
caller role allowed?
task type allowed?
model allowed?
provider allowed?
hosted use allowed?
network use allowed?
context class allowed?
output schema required?
retry allowed?
```

Missing policy must block hosted and implementation-affecting calls.

## 23.2 Tool / MCP Adapter Integration

If model calls are exposed as tools, Tool / MCP Adapter must remain the outer control boundary.

Model Adapter must not:

```text
call tools directly
execute MCP tools directly
return executable tool calls as trusted actions
bypass tool policy
```

Model outputs that contain suggested tool calls must be treated as data for the orchestrator to inspect.

## 23.3 Context Builder / Task Packer Integration

The Model Adapter should prefer bounded task packets from Context Builder.

Required task packet expectations:

```text
objective
allowed files
forbidden files
source snippets
relevant artifacts
output schema
constraints
validation plan
token budget
```

If no bounded task packet exists for implementation-affecting tasks, the request must block.

## 23.4 Local Model Runtime Profile Integration

Model selection must use runtime profile constraints when available.

Required constraints:

```text
max loaded models
context budget
output budget
timeout
local-only mode
network permission
VRAM/CPU budget when available
```

## 23.5 Prompt Contract / Prompt Versioning Integration

If prompt templates are externalized, prompt contract rules must validate:

```text
prompt template ID
template version
allowed task type
required output schema
required context fields
forbidden instructions
```

If Prompt Contract layer is not implemented yet, inline prompts are allowed only if request schema, context boundary, and output schema are enforced.

## 23.6 LLM Implementation Worker Integration

The LLM Implementation Worker may call the Model Adapter to request patch candidates.

The Model Adapter returns only model output. It does not:

```text
create implementation sessions
apply patches
write files
run validation
approve output
```

## 23.7 Failure Taxonomy Integration

Every failed, blocked, or invalid model request must produce a failure class from the model failure taxonomy.

## 23.8 Monitoring / Observability Integration

Model evidence must allow a session to reconstruct:

```text
which model was selected
which provider was used
which runtime profile was used
which task type was requested
whether JSON/schema validation passed
whether retry occurred
why a request was blocked or failed
```

---

# 24. Runtime Artifact Rules

All Model Adapter runtime artifacts must be under:

```text
.agentx-init/model_calls/
```

No Model Adapter artifact may be written outside this root unless the review document records the exception in a deviation register.

The Model Adapter must not write source files directly.

---

# 25. Public API Contract

Expected classes:

```text
ModelDefinition
ModelRegistry
ModelProviderProfile
ModelCapabilityProfile
ModelRuntimeProfile
ModelRequest
ModelResponse
ModelSelectionDecision
ModelPolicyDecision
ModelRetryRecord
InvalidModelRequestRecord
ModelAuditEvent
```

Expected public functions:

```python
load_default_model_registry() -> ModelRegistry

register_model(
    registry: ModelRegistry,
    model_definition: ModelDefinition
) -> ModelRegistry

get_model_definition(
    registry: ModelRegistry,
    model_id: str
) -> ModelDefinition | None

select_model(
    model_request: ModelRequest,
    registry: ModelRegistry,
    policy_context: dict,
    runtime_context: dict
) -> ModelSelectionDecision

check_model_permission(
    model_request: ModelRequest,
    selected_model: ModelDefinition,
    policy_context: dict
) -> ModelPolicyDecision

validate_model_request(
    model_request: ModelRequest,
    registry: ModelRegistry
) -> ModelResponse | None

run_model_request(
    model_request: ModelRequest,
    registry: ModelRegistry,
    policy_context: dict,
    runtime_context: dict
) -> ModelResponse

validate_model_response(
    model_response: ModelResponse,
    output_schema: dict | None
) -> ModelResponse

handle_invalid_model_request(
    model_request: ModelRequest | dict
) -> ModelResponse

write_model_call_evidence(
    model_request: ModelRequest,
    model_response: ModelResponse
) -> dict
```

Provider adapter functions:

```python
run_local_model_request(arguments: dict, context: dict) -> ModelResponse
run_ollama_request(arguments: dict, context: dict) -> ModelResponse
run_lmstudio_request(arguments: dict, context: dict) -> ModelResponse
run_openai_compatible_request(arguments: dict, context: dict) -> ModelResponse
run_hosted_model_request(arguments: dict, context: dict) -> ModelResponse
```

---

# 26. Model Request Execution Pipeline

Every model request must follow this sequence:

```text
1. Receive raw model request.
2. Normalize caller context.
3. Build ModelRequest object.
4. Validate ModelRequest schema.
5. Load or receive ModelRegistry.
6. Check requested model/provider exists, if specified.
7. Check caller role and task type.
8. Check Policy / Capability Registry.
9. Check runtime profile constraints.
10. Check provider policy.
11. Check prompt/context boundary.
12. Redact prompt/context.
13. Hash prompt/context.
14. Select model deterministically.
15. If dry_run=true, return dry-run response without provider call.
16. Call provider adapter only if all gates allow.
17. Enforce timeout and output-size limits.
18. Parse JSON if json_only=true.
19. Validate output schema.
20. Check forbidden-action output rules.
21. Retry only if retry policy allows.
22. Hash final output.
23. Write request/response evidence.
24. Return schema-valid ModelResponse.
```

Rules:

```text
No skipped stage is allowed unless the model request explicitly marks it not applicable and policy agrees.
Any failed stage returns schema-valid BLOCKED, FAILED, or INVALID response.
Exceptions must be converted to schema-valid ModelResponse records.
```


---

# 27. Provider Transport and Endpoint Policy

The Model Adapter must define exactly how provider calls may occur. Provider transport is part of the safety boundary.

## 27.1 Allowed Transport Modes

Allowed transport modes in this layer:

```text
NONE
TEST_DOUBLE
LOCAL_IN_PROCESS
LOCAL_HTTP_LOOPBACK
HOSTED_HTTPS_APPROVED
```

Default transport mode:

```text
NONE or TEST_DOUBLE during validation
LOCAL_HTTP_LOOPBACK only when explicitly configured
HOSTED_HTTPS_APPROVED only when hosted policy explicitly allows it
```

## 27.2 Loopback Rule

Local HTTP providers such as Ollama, LM Studio, or OpenAI-compatible local servers may be treated as local only when the endpoint is explicitly loopback or local-machine scoped.

Allowed local endpoint examples:

```text
http://127.0.0.1:<port>
http://localhost:<port>
http://[::1]:<port>
```

Blocked unless hosted policy approves:

```text
public IP endpoints
LAN endpoints
remote hostnames
HTTPS provider APIs
provider URLs from environment variables without allowlist validation
```

## 27.3 Hosted Endpoint Rule

Hosted provider endpoints must be:

```text
explicitly configured
explicitly allowlisted
explicitly policy-approved
network-approved
credential-reference approved
evidence-logged
redaction-checked before request
```

Hosted calls must not be created by fallback, provider auto-discovery, environment auto-detection, or model suggestion.

## 27.4 Streaming Rule

Streaming is optional and disabled by default.

If streaming is later enabled:

```text
streamed chunks must be bounded
streamed chunks must not be durably logged raw by default
final assembled output must still pass JSON/schema validation
stream cancellation must produce schema-valid FAILED or BLOCKED response
streaming must not bypass timeout, output-size, redaction, or evidence rules
```

Base validation must not require streaming support.

## 27.5 Provider Dependency Rule

Base tests must not require:

```text
GPU
network
hosted provider account
provider API key
Ollama running
LM Studio running
OpenCode runtime
Bun
Node
external MCP server
```

Provider-specific integration tests may exist later, but they must be optional and skipped unless explicitly enabled.

---

# 28. Credential and Secret-Reference Policy

The Model Adapter must treat credentials as references, never as model context.

Allowed credential representation:

```json
{
  "credential_ref": "MODEL_PROVIDER_CREDENTIAL_REF"
}
```

Forbidden credential behavior:

```text
raw API key in registry
raw API key in runtime profile
raw API key in prompt
raw API key in context packet
raw API key in evidence
raw API key in error message
raw API key in model response
provider environment dump in logs
```

Credential lookup, if implemented later, must happen inside a provider adapter boundary and must not expose the secret to:

```text
model prompt
model output
JSONL evidence
latest artifacts
review reports
completion records
error messages
```

If redaction cannot prove a payload is safe, the request must block.

---

# 29. Deterministic Test-Double Provider Contract

A deterministic test-double provider is required so this layer can be validated without real model infrastructure.

Required test-double behavior:

```text
accepts schema-valid ModelRequest
returns schema-valid ModelResponse
can return valid JSON output for success tests
can return invalid JSON output for retry tests
can return schema-invalid JSON for rejection tests
can simulate timeout/failure without sleeping for long periods
never calls network
never reads source files directly
never writes files
never executes commands
never invokes real model runtime
```

Required test-double profile:

```json
{
  "provider_type": "TEST_DOUBLE",
  "local_only": true,
  "network_allowed": false,
  "max_loaded_models": 1,
  "timeout_seconds": 5,
  "max_retries": 1
}
```

The test-double provider is sufficient for base acceptance of:

```text
registry loading
model selection
request validation
response validation
retry behavior
blocked hosted calls
evidence writing
prompt/output hashing
forbidden-output rejection
```

A real local model call can be required by a later Local Runtime Profile acceptance pass, not by this controlling contract alone.

---

# 30. Concurrency, Locking, and Idempotency Rules

Model calls can be expensive, stateful, and provider-dependent. This layer must avoid uncontrolled duplicate calls and evidence races.

## 30.1 Locking Rules

Runtime evidence writes under `.agentx-init/model_calls/` must be safe for repeated local execution.

Required behavior:

```text
append JSONL atomically or with a local file lock
write latest artifacts atomically through temp-file then replace
never interleave partial JSON objects
never corrupt existing JSONL history
if lock acquisition fails, return BLOCKED or FAILED with evidence when possible
```

## 30.2 Idempotency Rules

Every `ModelRequest` must have a stable `model_request_id`.

Repeated calls with the same finalized `model_request_id` must not silently create a second provider call unless one of these is true:

```text
request explicitly sets force_rerun=true
prior response status was FAILED and retry policy allows retry
prior response status was INVALID and retry policy allows repair
caller provides a new model_request_id
```

Required idempotency evidence:

```text
original request ID
request hash
provider selected
whether provider was called
whether cached/finalized response was reused
reason for rerun, if any
```

## 30.3 One-Model-at-a-Time Rule

For local limited-hardware profiles, default behavior is:

```text
max_loaded_models = 1
no parallel local model execution
no automatic multi-model race
no ensemble calls unless a later policy explicitly enables them
```

This keeps the Model Adapter compatible with small local machines.

---

# 31. Evidence Hashing and Provenance Requirements

The Model Adapter must prove what was requested, what was selected, what was returned, and what was validated without leaking sensitive content.

Required hashes:

```text
prompt_hash
context_packet_hash, when context_packet_ref is used
redacted_prompt_hash
redacted_context_hash, when context is materialized
output_hash
output_json_hash, when JSON output exists
model_registry_hash
model_profile_hash
provider_profile_hash
runtime_profile_hash
policy_decision_hash or policy_decision_id
evidence_manifest_hash
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard-library hashlib if no project helper exists.
Do not use hashes as a substitute for schema validation.
Do not hash raw secrets into public evidence when the hash itself would become a stable secret fingerprint.
```

Required provenance fields in completed evidence:

```text
model_request_id
model_response_id
session_id
caller_role
task_type
selected_model_id
selected_provider_id
runtime_profile_id
selection_decision_id
policy_decision_id, when available
redaction_decision_id, when available
retry_count
status
failure_class, if not SUCCESS
```

---

# 32. Deferral and Status Vocabulary

Use only these status values for review and implementation status tables:

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
TEST_DOUBLE_ONLY
```

Meaning:

| Status | Meaning | DONE allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some pieces exist but behavior is incomplete or unproven. | No for required safety areas |
| FAIL | Checked and failed. | No |
| NOT CHECKED | Not validated. | No |
| NOT RUN | Required command/test not run. | No |
| NOT APPLICABLE | Truly outside implemented scope and no runtime path exists. | Yes, if justified |
| DEFERRED SAFELY | Planned/runtime feature cannot execute or affect safety yet. | Yes, if tested and recorded |
| TEST_DOUBLE_ONLY | Base validation uses deterministic test double; real provider acceptance deferred. | Yes for base contract; real runtime requires later pass |

Local runtime provider execution may be `TEST_DOUBLE_ONLY` for this layer if:

```text
test-double provider passes
real provider calls are not required by base tests
no hosted/network calls occur
local runtime deferral is recorded
Local Model Runtime Profile layer will validate real local execution later
```

Hosted provider execution may be `DEFERRED SAFELY` only if:

```text
hosted providers are disabled
network is disabled
no hosted endpoint is called
no hosted credential is required
hosted fallback cannot occur silently
```

---

# 33. Runtime Boundary Clarification

The Model Adapter Layer may define model runtime profile schemas and lightweight runtime constraints, but it must not absorb the full **Local Model Runtime Profile Layer**.

## 33.1 Owned by Model Adapter

The Model Adapter owns:

```text
model registry
provider profiles
capability profiles
runtime profile references
request validation
response validation
provider adapter interface
provider selection
prompt/context boundary checks
JSON output validation
retry policy
model-call evidence
invalid/blocked model request handling
```

## 33.2 Owned by Later Local Model Runtime Profile Layer

The later Local Model Runtime Profile Layer owns deeper runtime management:

```text
GPU/CPU probing
VRAM measurement
model loading strategy
quantization profile selection
one-model-loaded enforcement across processes
runtime health checks
provider process lifecycle
local model installation checks
local model benchmark records
```

## 33.3 Boundary Rule

The Model Adapter may consume a runtime profile and enforce its limits, but it must not start managing local runtime infrastructure as a side effect.

Allowed in this layer:

```text
read runtime profile
validate runtime profile
select compatible model
block if profile is missing or incompatible
call already-running local provider if explicitly configured
use deterministic test double for base validation
```

Forbidden in this layer:

```text
auto-install model runtime
auto-download model weights
auto-start Ollama, LM Studio, or OpenCode
auto-probe GPU by default
auto-load multiple models
auto-switch to hosted fallback
```

---

# 34. Additional Schema Contracts

The following schemas are required because the Model Adapter must be implementation-ready, not only conceptually specified.

## 34.1 Model Definition Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_definition.schema.json",
  "model_id": "string",
  "display_name": "string",
  "provider_id": "string",
  "capability_profile_id": "string",
  "runtime_profile_id": "string|null",
  "model_family": "SMALL_FAST|SMALL_CODER|MEDIUM_CODER_OPTIONAL|HOSTED_FALLBACK_OPTIONAL|TEST_DOUBLE|UNKNOWN",
  "enabled": true,
  "allowlisted": true,
  "local_only": true,
  "hosted": false,
  "supports_json_mode": false,
  "max_context_tokens": 0,
  "max_output_tokens": 0,
  "default_temperature": 0.0,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
model_id must be unique.
provider_id must reference a known provider profile.
hosted=true requires local_only=false and explicit hosted policy approval before use.
enabled=false models remain visible but return BLOCKED if requested.
allowlisted=false models cannot be selected automatically.
```

## 34.2 Model Provider Profile Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_provider_profile.schema.json",
  "provider_id": "string",
  "provider_type": "LOCAL_IN_PROCESS|LOCAL_HTTP_OPENAI_COMPATIBLE|OLLAMA|LM_STUDIO|OPENCODE_COMPATIBLE|HOSTED_OPENAI_COMPATIBLE|HOSTED_PROVIDER_OTHER|TEST_DOUBLE",
  "transport_mode": "NONE|TEST_DOUBLE|LOCAL_IN_PROCESS|LOCAL_HTTP_LOOPBACK|HOSTED_HTTPS_APPROVED",
  "endpoint": "string|null",
  "endpoint_allowlisted": false,
  "credential_ref": "string|null",
  "network_required": false,
  "hosted": false,
  "enabled": true,
  "allowlisted": true,
  "timeout_seconds": 30,
  "max_retries": 0,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
TEST_DOUBLE provider must not use network or credentials.
LOCAL_HTTP_LOOPBACK requires localhost/127.0.0.1/[::1] endpoint.
HOSTED_HTTPS_APPROVED requires hosted policy approval and credential_ref.
credential_ref is a reference only, never a raw secret.
```

## 34.3 Model Policy Decision Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_policy_decision.schema.json",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "ModelPolicy",
  "model_request_id": "string",
  "caller_role": "string",
  "task_type": "string",
  "model_id": "string|null",
  "provider_id": "string|null",
  "decision": "ALLOW|BLOCK|NEEDS_POLICY|NEEDS_RUNTIME_PROFILE|NEEDS_CONTEXT_BOUNDARY|NEEDS_HOSTED_PROVIDER_APPROVAL|ALLOW_LOCAL_ONLY",
  "reason": "string",
  "required_checks": [],
  "missing_checks": [],
  "warnings": [],
  "errors": []
}
```

## 34.4 Model Retry Record Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_retry_record.schema.json",
  "retry_record_id": "string",
  "timestamp": "string",
  "model_request_id": "string",
  "previous_response_id": "string|null",
  "retry_index": 0,
  "retry_reason": "MODEL_INVALID_JSON|MODEL_SCHEMA_VALIDATION_FAILED|MODEL_OUTPUT_TRUNCATED",
  "retry_allowed": false,
  "decision": "RETRY|BLOCK|FAIL",
  "same_task_objective": true,
  "warnings": [],
  "errors": []
}
```

## 34.5 Invalid Model Request Record Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "invalid_model_request.schema.json",
  "record_id": "string",
  "timestamp": "string",
  "source_component": "InvalidModelRequestHandler",
  "model_request_id": "string|null",
  "caller_role": "string|null",
  "task_type": "string|null",
  "reason": "string",
  "safe_request_summary": {},
  "failure_class": "string",
  "warnings": [],
  "errors": []
}
```

## 34.6 Model Audit Event Schema

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "ModelAdapter",
  "event_type": "REQUEST|RESPONSE|BLOCKED|INVALID|RETRY|SELECTION|REDACTION|PROVIDER_FAILURE",
  "model_request_id": "string|null",
  "model_response_id": "string|null",
  "model_id": "string|null",
  "provider_id": "string|null",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 35. Provider Adapter Boundary Rules

Provider adapters are translation boundaries only. They convert a policy-approved ModelRequest into one provider call and convert the provider result into a ModelResponse.

Provider adapters must return only:

```text
ModelResponse
```

or a schema-valid blocked/failed response object that can be converted to ModelResponse.

Provider adapters must not return or leak:

```text
provider-native response objects
raw HTTP client objects
raw exceptions containing credentials
raw environment variables
raw streamed chunks
raw unredacted prompt/context
raw provider debug traces
```

Provider adapters must not:

```text
select a different model without selector approval
change provider endpoint without policy approval
retry outside ModelRetryPolicy
execute tools
read source files directly
write source files
run commands
open network connections unless provider transport policy already allowed it
```

If a provider adapter fails, the response must be schema-valid:

```text
status = FAILED or BLOCKED
failure_class = MODEL_PROVIDER_CALL_FAILED, MODEL_TIMEOUT, MODEL_PROVIDER_BLOCKED, or UNKNOWN_MODEL_FAILURE
```

---

# 36. Capability-to-Task Matrix

Use this default matrix unless Policy / Capability Registry narrows it further.

| Capability profile | Allowed default task types | Blocked default task types | Notes |
|---|---|---|---|
| `SMALL_FAST` | `SUMMARIZE_CONTEXT`, `CLASSIFY_FAILURE`, `REPAIR_JSON`, `EXPLAIN_FAILURE` | broad `IMPLEMENT_PATCH` | Fast helper profile for bounded outputs. |
| `SMALL_CODER` | `IMPLEMENT_PATCH`, `FIX_VALIDATION`, `WRITE_TEST`, `REPAIR_JSON` | promotion, governance approval, direct tools | Main local coding profile, output must be JSON/schema-valid. |
| `MEDIUM_CODER_OPTIONAL` | same as `SMALL_CODER`, plus harder validation repair | hosted-only or unbounded tasks | Optional local profile, still governed. |
| `HOSTED_FALLBACK_OPTIONAL` | explicitly approved review/explanation or redacted difficult task | default coding, whole repo, secrets, promotion | Disabled unless hosted policy explicitly allows it. |
| `TEST_DOUBLE` | all schema/test paths needed for base validation | real provider behavior claims | Deterministic validation provider only. |

Rules:

```text
Policy may narrow allowed tasks but may not allow forbidden authority.
No capability profile may directly write files, run commands, call tools, approve governance, or promote changes.
Implementation-affecting task types require output_schema_id and bounded task packet/context reference.
```

---

# 37. Model Output to Tool-Call Proposal Rules

The Model Adapter must distinguish between a model suggesting an action and Agent_X executing an action.

Allowed model output:

```text
schema-valid patch candidate data
schema-valid test candidate data
schema-valid validation-fix proposal
schema-valid explanation
schema-valid suggested next tool name as inert data, if the output schema permits it
```

Forbidden model output treatment:

```text
model output becomes an executed ToolCall directly
model output bypasses Tool / MCP Adapter
model output bypasses Policy / Capability Registry
model output bypasses Security Sandbox
model output applies a patch directly
model output runs validation directly
model output approves its own changes
```

If model output contains suggested tool calls, they must be treated as data and passed to the Self-Evolution Orchestrator or another controlling layer. Any actual tool execution must go through the Tool / MCP Adapter and its own policy/sandbox checks.

---

# 38. Evidence Manifest and Completion Record Requirements

In addition to JSONL histories, the implementation must be able to produce final validation evidence artifacts.

## 38.1 Evidence Manifest

Create after validation:

```text
.agentx-init/model_calls/model_adapter_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_call_evidence_manifest.schema.json",
  "component_id": "AGENTX_MODEL_ADAPTER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "model_registry_hash": "<sha256>",
  "provider_profile_hashes": [],
  "runtime_profile_hashes": [],
  "prompt_output_hash_status": "PASS|FAIL|NOT CHECKED",
  "hosted_disabled_status": "PASS|FAIL|NOT CHECKED",
  "network_disabled_status": "PASS|FAIL|NOT CHECKED",
  "test_double_status": "PASS|FAIL|NOT CHECKED",
  "real_provider_status": "PASS|DEFERRED SAFELY|TEST_DOUBLE_ONLY|NOT APPLICABLE",
  "deviation_register": [],
  "final_decision": "DONE|NOT DONE"
}
```

## 38.2 Completion Record

Create after validation:

```text
.agentx-init/model_calls/model_adapter_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_adapter_completion_record.schema.json",
  "component_id": "AGENTX_MODEL_ADAPTER",
  "component_name": "Model Adapter Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/models/",
  "runtime_artifact_root": ".agentx-init/model_calls/",
  "basis_documents": [
    "MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "model_registry_entries_verified": [],
  "provider_profiles_verified": [],
  "capability_profiles_verified": [],
  "runtime_profiles_verified": [],
  "selection_policy_verified": [],
  "hosted_disabled_verified": [],
  "network_disabled_verified": [],
  "test_double_verified": [],
  "context_boundary_verified": [],
  "output_validation_verified": [],
  "policy_integration_verified": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence manifest, completion record, registry/profile snapshots, and command output artifacts used for final validation.
A DONE verdict is invalid if required final evidence hashes are missing.
```

---

# 39. Real-Provider Deferral Rules

The base Model Adapter contract may be completed with `TEST_DOUBLE_ONLY` real-provider status if all safety behavior is proven without relying on external runtime.

`TEST_DOUBLE_ONLY` is acceptable only if:

```text
test-double provider is deterministic
test-double provider validates request/response/retry/evidence behavior
hosted providers are disabled
network is disabled
no real provider is required for base tests
real local provider validation is assigned to Local Model Runtime Profile Layer or a later provider integration pass
```

`DEFERRED SAFELY` is acceptable for hosted providers only if:

```text
hosted providers cannot be selected by default
hosted endpoints are not configured by default
network is disabled by default
credential_ref is absent or inert by default
hosted fallback cannot occur silently
tests prove hosted requests return BLOCKED unless all explicit approvals exist
```

`NOT APPLICABLE` may be used only when there is no runtime entry point for that provider category.

`PARTIAL` must be used when a provider adapter exists but behavior is incomplete, untested, or not safely disabled.

---

# 40. Final Frozen Acceptance Matrix

| Area | Required 10/10 state |
|---|---|
| Contract scope | Model access only; no patch, tool, command, file, approval, or promotion authority. |
| Provider policy | Local/test-double first; hosted/network disabled by default. |
| Runtime boundary | Consumes runtime profiles; does not manage model infrastructure lifecycle. |
| Schemas | Registry, model, provider, capability, runtime, request, response, selection, policy, retry, invalid, audit, evidence, completion schemas defined. |
| Selection | Deterministic and policy-aware. |
| Prompt/context | Bounded, redacted, hash-evidenced, no whole-repo prompts. |
| Output validation | JSON/schema validation required for implementation-affecting tasks. |
| Forbidden actions | Model output cannot execute tools, commands, patches, source writes, approval, or promotion. |
| Test double | Deterministic provider supports base validation without GPU/network/provider accounts. |
| Evidence | JSONL histories, latest artifacts, hashes, evidence manifest, completion record. |
| OpenCode borrowing | Provider abstraction only; no OpenCode runtime, Bun, Node, or default network. |
| Validation | compileall, pytest, schema validation, clean git status. |

A future implementation spec should fill exact files, functions, tests, examples, and build order without changing these safety boundaries.

---

# 49. Security Rules

This layer must enforce:

```text
no model direct file writes
no model direct command execution
no model direct tool execution
no model direct patch application
no model governance approval
no model promotion decision
no hosted provider use by default
no network by default
no whole-repo prompts
no unredacted secret logging
no provider credential logging
no silent hosted fallback
no unbounded retries
no unbounded context
no unbounded output
no OpenCode runtime dependency
no Bun/Node dependency
```

---

# 50. Test Acceptance Criteria

Required tests:

```text
test_model_registry_loads_default_profiles
test_model_registry_rejects_duplicate_model_ids
test_model_request_schema_accepts_valid_request
test_model_request_schema_rejects_missing_task_type
test_model_response_schema_accepts_success_response
test_model_response_schema_accepts_blocked_response
test_unknown_model_returns_invalid_or_blocked
test_unknown_caller_blocks
test_hosted_provider_disabled_by_default
test_network_disabled_by_default
test_local_model_profile_can_be_selected
test_model_selection_is_deterministic
test_implementation_task_requires_output_schema
test_context_too_large_blocks
test_secret_in_prompt_blocks_or_redacts
test_invalid_json_output_retries_once_when_allowed
test_invalid_json_output_rejected_when_retry_exhausted
test_schema_invalid_output_rejected
test_model_output_cannot_request_file_write
test_model_output_cannot_request_command_execution
test_model_output_cannot_claim_governance_approval
test_model_request_history_written
test_model_response_history_written
test_blocked_model_request_history_written
test_invalid_model_request_history_written
test_prompt_and_output_hashes_recorded
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
negative safety tests PASS
hosted-disabled tests PASS
local runtime selection tests PASS or safely deferred
evidence tests PASS
no source mutation
no network by default
invalid model requests fail closed
```

---

# 51. Implementation Slices

Build this layer in small slices.

## 51.1 Slice A — Models and Schemas

Implement:

```text
model_models.py
model_registry.schema.json
model_definition.schema.json
model_provider_profile.schema.json
model_capability_profile.schema.json
model_runtime_profile.schema.json
model_request.schema.json
model_response.schema.json
model_selection_decision.schema.json
model_policy_decision.schema.json
invalid_model_request.schema.json
model_audit.schema.json
```

Acceptance:

```text
schemas validate
dataclasses instantiate
model request/response serialize
invalid model response can be created
```

## 51.2 Slice B — Registry, Selection, and Policy

Implement:

```text
model_registry.py
model_selector.py
model_policy.py
invalid_model_request.py
```

Acceptance:

```text
default model registry loads
duplicates block
unknown model blocks or returns invalid
hosted provider disabled by default
small local model selected for allowed local task
```

## 51.3 Slice C — Validation and Retry

Implement:

```text
model_request_validator.py
model_response_validator.py
json_output_validator.py
model_retry_policy.py
```

Acceptance:

```text
request schema validates
invalid request fails closed
invalid JSON is rejected or retried within budget
schema-invalid output is rejected
forbidden-action output is rejected
```

## 51.4 Slice D — Evidence Logger

Implement:

```text
model_call_logger.py
```

Acceptance:

```text
model_request_history.jsonl appended
model_response_history.jsonl appended
blocked_model_request_history.jsonl appended
invalid_model_request_history.jsonl appended
latest_model_request.json written atomically
latest_model_response.json written atomically
prompt/output hashes recorded
secrets redacted
```

## 51.5 Slice E — Provider Adapters

Implement:

```text
local_provider_adapter.py
ollama_adapter.py
lmstudio_adapter.py
openai_compatible_adapter.py
opencode_provider_adapter.py
hosted_model_adapter.py
prompt_runner.py
```

Acceptance:

```text
test-double provider works without network
local provider adapter can be selected
hosted provider blocks by default
provider failure returns schema-valid FAILED/BLOCKED response
no direct file/tool/command execution occurs
```

---

# 52. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] model registry schema is defined
[ ] model definition schema is defined
[ ] provider profile schema is defined
[ ] capability profile schema is defined
[ ] runtime profile schema is defined
[ ] model request schema is defined
[ ] model response schema is defined
[ ] model selection policy is defined
[ ] hosted-disabled default is defined
[ ] local-only default is defined
[ ] context boundary rules are defined
[ ] output validation rules are defined
[ ] audit/evidence paths are defined
[ ] failure classes are defined
[ ] OpenCode borrowing is bounded
[ ] Agent_X integration boundaries are defined
```

---

# 45. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] model registry loads
[ ] duplicate model IDs block
[ ] unknown model fails closed
[ ] unknown caller fails closed
[ ] hosted provider disabled by default
[ ] network disabled by default
[ ] local model profile can be selected or safely deferred
[ ] invalid JSON output is rejected or retried within limits
[ ] schema-invalid output is rejected
[ ] model output cannot directly request forbidden actions
[ ] evidence records are written
[ ] prompt/output hashes are recorded
[ ] no source mutation occurs
[ ] no commands execute
[ ] no tools execute directly
```

---

# 46. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_MODEL_ADAPTER"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  model_registry_entries_verified: []
  provider_profiles_verified: []
  capability_profiles_verified: []
  runtime_profiles_verified: []
  selection_policy_verified: []
  hosted_disabled_verified: []
  local_runtime_verified: []
  context_boundary_verified: []
  output_validation_verified: []
  policy_integration_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 47. Residual Risks

```yaml
residual_risks:
  - id: "MODEL-RISK-001"
    description: "Hosted provider could accidentally receive sensitive context."
    severity: "critical"
    mitigation: "Hosted providers disabled by default; redaction and policy checks required."
  - id: "MODEL-RISK-002"
    description: "Small local model may produce invalid or incomplete JSON."
    severity: "medium"
    mitigation: "JSON-only validation, bounded retry, schema rejection."
  - id: "MODEL-RISK-003"
    description: "Model output may request forbidden actions such as file writes or command execution."
    severity: "critical"
    mitigation: "Output validation rejects forbidden-action requests; model output is proposal only."
  - id: "MODEL-RISK-004"
    description: "Model selection could silently fall back to hosted provider."
    severity: "critical"
    mitigation: "No silent hosted fallback; hosted use requires explicit policy approval."
  - id: "MODEL-RISK-005"
    description: "Provider abstraction may over-copy OpenCode assumptions."
    severity: "high"
    mitigation: "Borrow provider shape only; no OpenCode runtime, Bun, Node, or default network access."
```

---

# 48. Definition of Done

This layer is done when it can act as the governed model access boundary for Agent_X.

It must prove:

```text
model registry loads
model profiles validate
provider profiles validate
runtime profiles validate
model requests validate against schema
model responses validate against schema
unknown model fails closed
unknown caller fails closed
hosted provider disabled by default
network disabled by default
local model or test-double provider can be selected safely
implementation-affecting tasks require output schema
context boundary is enforced
secret redaction is enforced
invalid JSON output is rejected or retried within limits
schema-invalid output is rejected
model output cannot directly request source mutation
model output cannot directly request command execution
model output cannot directly request tool execution
model output cannot claim governance approval
model call evidence is written
model response evidence is written
blocked/invalid model request evidence is written
prompt/output hashes are recorded
no source mutation occurs directly in this layer
no command execution occurs directly in this layer
no tool execution occurs directly in this layer
no hosted provider call occurs unless explicitly enabled and policy-approved
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py
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

# 49. Fresh-Clone Validation and Sign-Off

The implementation is accepted only after validation from a fresh checkout or clean working tree.

Required command sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_model_adapter_check
cd Agent_X_model_adapter_check
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected ignored runtime artifacts
```

## 49.1 Final Sign-Off Checklist

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] default model registry loads
[ ] duplicate model IDs block
[ ] unknown model fails closed
[ ] unknown caller fails closed
[ ] hosted providers disabled by default
[ ] network disabled by default
[ ] local/test-double provider can be selected
[ ] implementation tasks require output schema
[ ] context boundary enforced
[ ] invalid JSON rejected or retried within limit
[ ] schema-invalid output rejected
[ ] forbidden-action output rejected
[ ] model request history written
[ ] model response history written
[ ] blocked model request history written
[ ] invalid model request history written
[ ] prompt/output hashes recorded
[ ] secrets redacted before evidence
[ ] no source mutation
[ ] no command execution
[ ] no direct tool execution
[ ] no hosted call without explicit approval
[ ] completion record exists
```

---

# 50. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
unknown model raises unhandled exception instead of INVALID/BLOCKED response
unknown caller is allowed
hosted provider enabled by default
network enabled by default
silent hosted fallback occurs
model request bypasses Policy / Capability Registry
implementation task proceeds without output schema
whole-repo prompt is allowed by default
prompt with unredacted secret is sent to provider
provider credential is logged
model output directly writes files
model output directly executes commands
model output directly executes tools
model output claims governance approval and is accepted
model output claims promotion and is accepted
invalid JSON is accepted as SUCCESS
schema-invalid output is accepted as SUCCESS
model evidence is not written
prompt/output hashes are missing for completed calls
source mutation occurs directly in model adapter
OpenCode source code is copied
Bun/Node/OpenCode runtime becomes required
```

---

# 51. Final Freeze Rule

This v3 document is the frozen controlling contract for the Model Adapter Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional details for implementation spec
MAJOR: changed provider default policy, changed hosted fallback rule, changed model authority boundary, new required provider category, new required runtime mode
```

Blocked without major revision:

```text
allowing hosted providers by default
allowing network by default
allowing model output to directly mutate source
allowing model output to directly execute tools
allowing model output to directly execute commands
allowing model output to approve governance
allowing model output to promote changes
removing output schema validation
removing context boundary checks
removing evidence logging
making Bun/Node/OpenCode runtime required
copying OpenCode source code
```

The next document should be:

```text
MODEL_ADAPTER_IMPLEMENTATION_SPEC.md
```

---

# 52. Final Rating

This v3 contract is rated:

```text
10/10
```

Reason:

```text
It defines the Model Adapter Layer with EQC, FIC, SIB, schemas, provider policy, local model policy, hosted model policy, request/response contracts, capability/runtime profiles, model selection policy, permission matrix, prompt/context boundaries, output validation, audit/evidence, OpenCode borrowing boundaries, Agent_X integration points, test acceptance criteria, no-go conditions, provider transport policy, credential rules, deterministic test-double requirements, concurrency/idempotency controls, evidence hashing/provenance, runtime boundary clarification, provider adapter boundary rules, capability-to-task mapping, model-output-to-tool-call proposal rules, evidence manifest/completion record requirements, real-provider deferral rules, and a precise Definition of Done.
```
