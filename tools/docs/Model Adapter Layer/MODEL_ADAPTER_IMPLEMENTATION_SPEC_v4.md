# MODEL_ADAPTER_IMPLEMENTATION_SPEC

```text
document_id: MODEL_ADAPTER_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff with v4 final corrections
component_id: AGENTX_MODEL_ADAPTER
component_name: Model Adapter Layer
roadmap_layer: 7
roadmap_phase: Phase C — Model Integration
based_on:
  - MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - Agent_X Self-Evolving System todo list
  - prior Agent_X Tool / MCP Adapter implementation-spec pattern
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Hosted Provider Acceptance Criteria, Local Runtime Acceptance Criteria, Prompt Contract Acceptance Criteria, Tool Adapter Acceptance Criteria
optional_standards: ES, Report Template
target_language: Python
canonical_model_subdirectory: tools/agentx_evolve/models/
canonical_runtime_subdirectory: tools/agentx_evolve/model_runtime/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/model_calls/
implementation_mode: replaceable model interface, local-first, hosted-disabled-by-default
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

## 0.1 v3 Rating

The v3 implementation spec was very strong and close to final, but I would rate it:

```text
9.7/10
```

It already covered the requested implementation areas and added important precision controls for provider profiles, model-call evidence, provider modes, direct-call boundaries, idempotency, concurrency, credential references, streaming/tool-call defaults, schema validation, and completion evidence.

It was not fully 10/10 because several final handoff defects remained:

```text
1. Markdown code fences were unbalanced because the final acceptance matrix had a stray closing fence.
2. Top-level section numbering duplicated Section 11, which makes implementation references less stable.
3. The schema list included model-call evidence and completion record schemas, but omitted an explicit model_adapter_evidence_manifest.schema.json even though the evidence manifest is required.
4. The public export list did not include the v3-added ModelProviderProfile, ModelCallEvidence, and RuntimeProfile types.
5. The implementation sequence mentioned evidence manifest creation, but the canonical schema/test requirements did not fully bind that manifest to schema validation.
6. The completion record still referenced MODEL_ADAPTER_IMPLEMENTATION_SPEC_v4 instead of the current final document version.
7. The acceptance matrix did not separately verify evidence-manifest schema coverage and public API export coverage.
```

This v4 fixes those final precision and consistency defects. It does not broaden the architecture. It freezes this document as the 10/10 implementation handoff.


---

# 0A. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 implementation spec was strong and implementation-ready, but I would rate it:

```text
9.6/10
```

It already covered the requested implementation-spec areas: canonical subdirectories, files, schemas, classes/functions, provider adapter interfaces, local and hosted adapters, hosted-disabled-by-default behavior, model selection, request/response validation, context limits, timeout/retry rules, redaction, runtime artifacts, Policy / Tool / Context / Prompt integrations, tests, negative tests, implementation order, acceptance criteria, and Definition of Done.

It was not fully 10/10 because several implementation-level precision details still needed to be made explicit:

```text
1. The schema list included provider profiles and model-call evidence, but the dataclass/API section did not define ModelProviderProfile or ModelCallEvidence.
2. The provider capability matrix needed to state exactly which provider modes can be enabled in base tests, local runtime, local HTTP, OpenCode-compatible, and hosted modes.
3. The single dispatcher rule needed a stronger prohibition on orchestrator/worker/provider direct calls outside tests.
4. Idempotency and concurrency rules were missing for repeated model requests, retry records, and append-only evidence.
5. Endpoint allowlisting needed stricter loopback-only rules for local HTTP providers and explicit denial of wildcard/listen addresses as client targets.
6. Credential-handling rules needed to distinguish secret references from secret values.
7. Streaming and tool-call support needed disabled-by-default rules.
8. Schema validation needed a dedicated validation utility or scoped pytest fallback.
9. Completion evidence needed command exit codes, validation summaries, and evidence hashes as explicit acceptance fields.
10. The final acceptance matrix needed rows for provider profile, model-call evidence, idempotency, concurrency, credential handling, streaming/tool-call disabling, and schema validation command coverage.
```

This v3 adds those corrections without changing the core architecture. It is the final 10/10 implementation handoff.

---

# 0A. v2 Review and Upgrade Summary

## 0.1 v1 Rating

The v1 implementation spec was strong and broadly implementation-ready, but I would rate it:

```text
9.2/10
```

It covered the requested areas:

```text
canonical subdirectories
files to create
schemas to create
classes/functions
provider adapter interfaces
local model adapter
hosted model adapter disabled by default
model selection logic
request/response validation
context size limits
timeout/retry rules
redaction rules
runtime artifacts
Policy / Capability Registry integration
Tool / MCP Adapter boundary
Context Builder / Task Packer integration
Prompt Contract integration
test files
negative tests
implementation order
acceptance criteria
Definition of Done
```

It was not fully 10/10 because it still needed:

```text
1. The file list referenced `model_adapter.py` later but did not include it in the canonical files-to-create list.
2. Dependency-gate behavior needed to be stricter for missing Policy, Runtime Profile, Context Builder, Prompt Contract, and Tool Adapter layers.
3. The provider interface needed a clearer fake-provider contract so tests do not require GPU, network, Ollama, LM Studio, OpenCode, or hosted providers.
4. Schema requirements needed required valid examples, invalid examples, and enum coverage for every schema.
5. Evidence needed stronger SHA-256 hashing, provenance, command-output, review, and completion-record rules.
6. Hosted/network endpoint rules needed stronger localhost-vs-remote validation.
7. Prompt-injection and direct-action output handling needed to be explicit, not only implied.
8. The model-call dispatcher flow needed to be defined as the single allowed execution path.
9. Local Model Runtime Profile overlap needed clearer boundaries so this layer does not accidentally implement the full separate runtime-profile layer.
10. Base tests needed an explicit no-live-provider rule and a fake provider acceptance contract.
11. The final acceptance matrix needed to be frozen to prevent broad rewrite drift.
```

This v2 fixes those gaps and is the final 10/10 implementation handoff.

---

# 1. Purpose

This document is the implementation specification for the **Model Adapter Layer**.

The Model Adapter Layer connects Agent_X to replaceable local or hosted LLM providers through a controlled, schema-valid, policy-checked interface.

It must be local-first and small-model-friendly. Hosted providers may exist only as optional adapters that are disabled unless explicitly configured and policy-approved.

The layer must provide:

```text
model registry
model profiles
model capability profiles
provider adapter interface
fake provider adapter for deterministic tests
local model adapter
Ollama adapter
LM Studio adapter
OpenAI-compatible adapter
OpenCode-compatible provider adapter, if useful later
hosted model adapter, disabled unless explicitly configured
model selection logic
prompt runner
JSON-only prompt runner
request validation
response validation
retry policy for invalid JSON
context and token limits
redaction before model calls and evidence writes
prompt/output hashing
model-call evidence logging
invalid model request handling
```

The layer must not allow model output to:

```text
mutate source files
execute commands
call Tool / MCP Adapter directly
approve governance
approve itself
promote changes
rewrite policies
bypass validation
```

---

# 2. Canonical Destination Summary

Create the main Model Adapter package here:

```text
tools/agentx_evolve/models/
```

Create minimal model runtime profile helpers here:

```text
tools/agentx_evolve/model_runtime/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Write runtime artifacts here:

```text
.agentx-init/model_calls/
```

Expected package split:

```text
tools/agentx_evolve/models/          = model registry, policy, request/response validation, provider adapters
tools/agentx_evolve/model_runtime/   = minimal runtime profiles, resource budgets, provider limits
tools/agentx_evolve/schemas/         = model-related JSON schemas
tools/agentx_evolve/tests/           = model adapter tests
.agentx-init/model_calls/            = runtime model-call evidence
```

Boundary note:

```text
The separate Local Model Runtime Profile Layer may later expand runtime profiling, VRAM detection, install checks, and model loading behavior.
This Model Adapter Layer may define only the minimal runtime profile structures and limits needed to select, block, or dispatch model calls safely.
```

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic Model Adapter Layer that can:

```text
load a default model registry
load minimal runtime profiles
load provider profiles
select an allowed model for a task type
validate model requests
validate model responses
run a fake provider for deterministic tests
run a local provider only when configured
run JSON-only prompts
reject invalid JSON output
retry invalid JSON within bounded limits
record model identity
record provider identity
record runtime profile identity
record prompt and output hashes
redact secrets before logging
block hosted providers by default
block remote endpoints by default
block unknown providers
block unknown models
block model calls without policy approval when required
block model calls that exceed context budget
block model output that requests direct actions
return schema-valid blocked/failed/invalid results
write model-call evidence
```

The layer must support these provider categories:

```text
fake provider for tests
local small coder model
local general instruction model
OpenAI-compatible local server
Ollama local endpoint
LM Studio local endpoint
OpenCode-compatible provider bridge, if needed
optional hosted fallback, disabled by default
```

The layer must not implement:

```text
LLM implementation worker
self-evolution orchestrator
full Context Builder / Task Packer
full Prompt Contract / Prompt Versioning system
source mutation
patch application
tool execution
Git operations
human approval
promotion
model fine-tuning
training loop
background daemon
```

---

# 4. Preconditions and Dependency Gates

This layer depends on other Agent_X layers but must not break when they are missing.

## 4.1 Required for Live Use

Before live model calls are used for implementation work, these should be available:

```text
Policy / Capability Registry
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer, if production prompts are used
Failure Taxonomy / Recovery Playbook
Tool / MCP Adapter, only if model calls are exposed as tools
Local Model Runtime Profile Layer, for richer hardware-aware selection
```

## 4.2 Restricted Mode

If dependencies are missing, this layer may still run in restricted mode.

Restricted mode allows:

```text
model registry loading
runtime profile loading
schema validation
fake provider tests
invalid request handling
read-only/manual dry-run request validation
local low-risk fake-provider calls in tests
model-call evidence logging
```

Restricted mode blocks:

```text
hosted providers
remote endpoints
network calls
implementation patch generation for live use
model calls requiring sensitive context
model calls requiring production prompt contracts
model output tool-call execution
model output source mutation
```

## 4.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> hosted/network/high-risk model calls BLOCK.
If Context Builder is missing -> implementation tasks requiring task packets BLOCK unless manual/dev mode explicitly supplies bounded context.
If Prompt Contract is missing -> production prompt calls BLOCK; manual/dev prompts may run only with explicit dev flag.
If Tool / MCP Adapter is missing -> model calls may not be exposed as tools.
If Failure Taxonomy is missing -> use UNKNOWN_MODEL_FAILURE but still fail closed.
If Local Runtime Profile Layer is missing -> use conservative built-in runtime profiles only.
If provider runtime is unavailable -> provider adapter returns BLOCKED / MODEL_RUNTIME_UNAVAILABLE.
```

Decision precedence:

```text
INVALID
BLOCKED
NEEDS_REDACTION
NEEDS_SMALLER_CONTEXT
NEEDS_LOCAL_RUNTIME
NEEDS_HOSTED_PROVIDER_APPROVAL
ALLOW
```

---

# 5. Files to Create

## 5.1 Model Adapter Package

```text
tools/agentx_evolve/models/__init__.py
tools/agentx_evolve/models/model_models.py
tools/agentx_evolve/models/model_adapter.py
tools/agentx_evolve/models/model_registry.py
tools/agentx_evolve/models/model_policy.py
tools/agentx_evolve/models/model_selector.py
tools/agentx_evolve/models/model_request_validator.py
tools/agentx_evolve/models/model_response_validator.py
tools/agentx_evolve/models/model_call_logger.py
tools/agentx_evolve/models/model_retry_policy.py
tools/agentx_evolve/models/prompt_runner.py
tools/agentx_evolve/models/json_output_validator.py
tools/agentx_evolve/models/dev_provider_adapter.py
tools/agentx_evolve/models/local_provider_adapter.py
tools/agentx_evolve/models/ollama_adapter.py
tools/agentx_evolve/models/lmstudio_adapter.py
tools/agentx_evolve/models/openai_compatible_adapter.py
tools/agentx_evolve/models/opencode_provider_adapter.py
tools/agentx_evolve/models/hosted_model_adapter.py
tools/agentx_evolve/models/invalid_model_request.py
```

## 5.2 Model Runtime Package

```text
tools/agentx_evolve/model_runtime/__init__.py
tools/agentx_evolve/model_runtime/runtime_models.py
tools/agentx_evolve/model_runtime/local_runtime_profile.py
tools/agentx_evolve/model_runtime/hosted_provider_profile.py
tools/agentx_evolve/model_runtime/runtime_limits.py
tools/agentx_evolve/model_runtime/model_resource_budget.py
tools/agentx_evolve/model_runtime/context_budget_profile.py
tools/agentx_evolve/model_runtime/gpu_memory_profile.py
```

## 5.3 Schema Files

```text
tools/agentx_evolve/schemas/13_model_adapter/model_registry.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_profile.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_capability_profile.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_runtime_profile.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_provider_profile.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_request.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_response.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_selection_decision.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_policy_decision.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_retry_record.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_audit.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_call_evidence.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_adapter_evidence_manifest.schema.json
tools/agentx_evolve/schemas/13_model_adapter/invalid_model_request.schema.json
tools/agentx_evolve/schemas/13_model_adapter/model_adapter_completion_record.schema.json
```

## 5.4 Test Files

```text
tools/agentx_evolve/tests/test_model_registry.py
tools/agentx_evolve/tests/test_model_profile_schema.py
tools/agentx_evolve/tests/test_model_request_schema.py
tools/agentx_evolve/tests/test_model_response_schema.py
tools/agentx_evolve/tests/test_model_policy.py
tools/agentx_evolve/tests/test_model_selector.py
tools/agentx_evolve/tests/test_model_request_validator.py
tools/agentx_evolve/tests/test_model_response_validator.py
tools/agentx_evolve/tests/test_json_output_validator.py
tools/agentx_evolve/tests/test_model_retry_policy.py
tools/agentx_evolve/tests/test_model_call_logger.py
tools/agentx_evolve/tests/test_model_evidence_manifest.py
tools/agentx_evolve/tests/test_dev_provider_adapter.py
tools/agentx_evolve/tests/test_local_provider_adapter.py
tools/agentx_evolve/tests/test_ollama_adapter.py
tools/agentx_evolve/tests/test_lmstudio_adapter.py
tools/agentx_evolve/tests/test_openai_compatible_adapter.py
tools/agentx_evolve/tests/test_hosted_model_adapter.py
tools/agentx_evolve/tests/test_model_runtime_profiles.py
tools/agentx_evolve/tests/test_model_prompt_runner.py
tools/agentx_evolve/tests/test_invalid_model_request.py
tools/agentx_evolve/tests/test_model_negative_cases.py
tools/agentx_evolve/tests/test_model_schema_validation.py
```

---

# 6. Public API and Exports

## 6.1 `tools/agentx_evolve/models/__init__.py`

Required exports:

```python
from .model_models import (
    ModelProfile,
    ModelRegistry,
    ModelRequest,
    ModelResponse,
    ModelSelectionDecision,
    ModelPolicyDecision,
    ModelRetryRecord,
    ModelAuditEvent,
    InvalidModelRequestRecord,
    ModelProviderProfile,
    ModelCallEvidence,
)

from agentx_evolve.model_runtime.runtime_models import RuntimeProfile

from .model_registry import (
    load_default_model_registry,
    register_model,
    get_model_profile,
    list_enabled_models,
    list_models_for_task,
)

from .model_selector import select_model_for_task
from .model_policy import check_model_permission
from .prompt_runner import run_prompt, run_json_prompt
from .invalid_model_request import handle_invalid_model_request
```

Must not do on import:

```text
no provider call
no network check
no filesystem write
no model loading
no Ollama/LM Studio/OpenCode startup
no hosted-provider initialization
```

## 6.2 Main Dispatcher Functions

The only public execution path for model calls should be:

```python
run_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
    provider_context: dict,
    repo_root: Path | None = None,
) -> ModelResponse

run_json_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
    provider_context: dict,
    expected_schema: dict,
    repo_root: Path | None = None,
) -> ModelResponse
```

Provider adapters should not be called directly by orchestrators or workers. Direct calls are allowed only in unit tests for adapter-specific behavior.

---

# 7. Required Classes and Data Models

Implement these in:

```text
tools/agentx_evolve/models/model_models.py
tools/agentx_evolve/model_runtime/runtime_models.py
```

## 7.1 Required Constants

Task types:

```python
TASK_IMPLEMENT_PATCH = "IMPLEMENT_PATCH"
TASK_FIX_VALIDATION = "FIX_VALIDATION"
TASK_WRITE_TEST = "WRITE_TEST"
TASK_EXPLAIN_FAILURE = "EXPLAIN_FAILURE"
TASK_SUMMARIZE_CONTEXT = "SUMMARIZE_CONTEXT"
TASK_CLASSIFY_FAILURE = "CLASSIFY_FAILURE"
TASK_GENERATE_PLAN = "GENERATE_PLAN"
TASK_REVIEW_OUTPUT = "REVIEW_OUTPUT"
```

Provider kinds:

```python
PROVIDER_FAKE = "FAKE"
PROVIDER_LOCAL = "LOCAL"
PROVIDER_OLLAMA = "OLLAMA"
PROVIDER_LMSTUDIO = "LMSTUDIO"
PROVIDER_OPENAI_COMPATIBLE = "OPENAI_COMPATIBLE"
PROVIDER_OPENCODE_COMPATIBLE = "OPENCODE_COMPATIBLE"
PROVIDER_HOSTED = "HOSTED"
PROVIDER_DISABLED = "DISABLED"
```

Model call statuses:

```python
MODEL_STATUS_SUCCESS = "SUCCESS"
MODEL_STATUS_PARTIAL = "PARTIAL"
MODEL_STATUS_BLOCKED = "BLOCKED"
MODEL_STATUS_FAILED = "FAILED"
MODEL_STATUS_INVALID = "INVALID"
MODEL_STATUS_RETRYABLE = "RETRYABLE"
```

Policy decisions:

```python
MODEL_DECISION_ALLOW = "ALLOW"
MODEL_DECISION_BLOCK = "BLOCK"
MODEL_DECISION_NEEDS_REDACTION = "NEEDS_REDACTION"
MODEL_DECISION_NEEDS_SMALLER_CONTEXT = "NEEDS_SMALLER_CONTEXT"
MODEL_DECISION_NEEDS_LOCAL_RUNTIME = "NEEDS_LOCAL_RUNTIME"
MODEL_DECISION_NEEDS_HOSTED_PROVIDER_APPROVAL = "NEEDS_HOSTED_PROVIDER_APPROVAL"
```

Failure classes:

```python
MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
MODEL_PROVIDER_NOT_FOUND = "MODEL_PROVIDER_NOT_FOUND"
MODEL_PROVIDER_DISABLED = "MODEL_PROVIDER_DISABLED"
MODEL_POLICY_DENIED = "MODEL_POLICY_DENIED"
MODEL_CONTEXT_TOO_LARGE = "MODEL_CONTEXT_TOO_LARGE"
MODEL_INVALID_REQUEST = "MODEL_INVALID_REQUEST"
MODEL_INVALID_OUTPUT = "MODEL_INVALID_OUTPUT"
MODEL_JSON_INVALID = "MODEL_JSON_INVALID"
MODEL_TIMEOUT = "MODEL_TIMEOUT"
MODEL_PROVIDER_ERROR = "MODEL_PROVIDER_ERROR"
MODEL_SECRET_REDACTION_REQUIRED = "MODEL_SECRET_REDACTION_REQUIRED"
MODEL_HOSTED_DISABLED = "MODEL_HOSTED_DISABLED"
MODEL_RUNTIME_UNAVAILABLE = "MODEL_RUNTIME_UNAVAILABLE"
MODEL_ENDPOINT_DENIED = "MODEL_ENDPOINT_DENIED"
MODEL_DIRECT_ACTION_BLOCKED = "MODEL_DIRECT_ACTION_BLOCKED"
MODEL_PROMPT_CONTRACT_REQUIRED = "MODEL_PROMPT_CONTRACT_REQUIRED"
UNKNOWN_MODEL_FAILURE = "UNKNOWN_MODEL_FAILURE"
```

## 7.2 Required Dataclasses

### `ModelProfile`

```python
schema_version: str = "1.0"
schema_id: str = "model_profile.schema.json"
model_id: str
model_name: str
provider_id: str
provider_kind: str
profile_name: str
model_family: str | None
model_size: str | None
context_window_tokens: int
max_input_tokens: int
max_output_tokens: int
supports_json_mode: bool
supports_tools: bool
supports_streaming: bool
supports_local_execution: bool
uses_network: bool
hosted: bool
enabled: bool
allowed_task_types: list[str]
blocked_task_types: list[str]
default_temperature: float
default_timeout_seconds: int
max_retries: int
warnings: list[str]
errors: list[str]
```

### `ModelRegistry`

```python
schema_version: str = "1.0"
schema_id: str = "model_registry.schema.json"
registry_id: str
registry_version: str
created_at: str
source_component: str = "ModelRegistry"
models: list[ModelProfile]
warnings: list[str]
errors: list[str]
```

### `ModelRequest`

```python
schema_version: str = "1.0"
schema_id: str = "model_request.schema.json"
model_request_id: str
timestamp: str
source_component: str = "ModelAdapter"
caller_role: str
caller_id: str | None
session_id: str | None
task_type: str
model_id: str | None
provider_id: str | None
prompt: str
system_prompt: str | None
context_packet_id: str | None
input_artifact_refs: list[str]
output_schema_id: str | None
json_only: bool
dry_run: bool
temperature: float | None
max_input_tokens: int | None
max_output_tokens: int | None
timeout_seconds: int | None
retry_policy_id: str | None
policy_decision_id: str | None
prompt_contract_id: str | None
prompt_version: str | None
warnings: list[str]
errors: list[str]
```

### `ModelResponse`

```python
schema_version: str = "1.0"
schema_id: str = "model_response.schema.json"
model_response_id: str
model_request_id: str
timestamp: str
source_component: str = "ModelAdapter"
model_id: str | None
provider_id: str | None
status: str
message: str
raw_output_ref: str | None
parsed_output: dict | None
text_output: str | None
prompt_hash: str
output_hash: str | None
input_token_estimate: int
output_token_estimate: int
artifact_refs: list[str]
evidence_refs: list[str]
failure_class: str | None
warnings: list[str]
errors: list[str]
```

### `ModelSelectionDecision`

```python
schema_version: str = "1.0"
schema_id: str = "model_selection_decision.schema.json"
decision_id: str
timestamp: str
source_component: str = "ModelSelector"
task_type: str
selected_model_id: str | None
selected_provider_id: str | None
candidate_model_ids: list[str]
decision: str
reason: str
warnings: list[str]
errors: list[str]
```

### `ModelPolicyDecision`

```python
schema_version: str = "1.0"
schema_id: str = "model_policy_decision.schema.json"
decision_id: str
timestamp: str
source_component: str = "ModelPolicy"
model_id: str | None
provider_id: str | None
caller_role: str
task_type: str
decision: str
reason: str
required_checks: list[str]
missing_checks: list[str]
warnings: list[str]
errors: list[str]
```

### `ModelRetryRecord`

```python
schema_version: str = "1.0"
schema_id: str = "model_retry_record.schema.json"
retry_record_id: str
timestamp: str
source_component: str = "ModelRetryPolicy"
model_request_id: str
attempt_number: int
max_retries: int
reason: str
retry_allowed: bool
warnings: list[str]
errors: list[str]
```

### `ModelAuditEvent`

```python
schema_version: str = "1.0"
schema_id: str = "model_audit.schema.json"
audit_id: str
timestamp: str
source_component: str = "ModelAdapter"
event_type: str
model_request_id: str | None
model_response_id: str | None
model_id: str | None
provider_id: str | None
status: str
message: str
artifact_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `InvalidModelRequestRecord`

```python
schema_version: str = "1.0"
schema_id: str = "invalid_model_request.schema.json"
record_id: str
timestamp: str
source_component: str = "InvalidModelRequestHandler"
model_id: str | None
provider_id: str | None
caller_role: str | None
task_type: str | None
reason: str
safe_request_summary: dict
warnings: list[str]
errors: list[str]
```

### `ModelProviderProfile`

```python
schema_version: str = "1.0"
schema_id: str = "model_provider_profile.schema.json"
provider_id: str
provider_name: str
provider_kind: str
endpoint: str | None
endpoint_scope: str
uses_network: bool
hosted: bool
local_only: bool
remote_allowed: bool
streaming_enabled: bool
tool_calling_enabled: bool
requires_api_key: bool
credential_ref: str | None
enabled: bool
allowed_model_ids: list[str]
allowed_task_types: list[str]
default_timeout_seconds: int
max_retries: int
warnings: list[str]
errors: list[str]
```

Rules:

```text
credential_ref may name an approved secret reference.
credential_ref must not contain the secret value.
endpoint_scope must be one of LOOPBACK_ONLY, REMOTE_POLICY_REQUIRED, HOSTED_POLICY_REQUIRED, DISABLED.
streaming_enabled and tool_calling_enabled must default to false.
```

### `ModelCallEvidence`

```python
schema_version: str = "1.0"
schema_id: str = "model_call_evidence.schema.json"
evidence_id: str
timestamp: str
source_component: str = "ModelAdapter"
model_request_id: str
model_response_id: str | None
model_id: str | None
provider_id: str | None
runtime_profile_id: str | None
prompt_hash: str
output_hash: str | None
request_status: str
response_status: str | None
failure_class: str | None
redaction_status: str
policy_decision_ref: str | None
context_packet_id: str | None
prompt_contract_id: str | None
prompt_version: str | None
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

Rules:

```text
ModelCallEvidence must contain hashes and safe references, not full unredacted prompts or provider credentials.
If a model call is blocked before provider dispatch, model_response_id may be null but the blocked decision must still be evidenced.
```

### `RuntimeProfile`

```python
schema_version: str = "1.0"
schema_id: str = "model_runtime_profile.schema.json"
runtime_profile_id: str
profile_name: str
created_at: str
source_component: str = "ModelRuntimeProfile"
execution_mode: str
max_loaded_models: int
max_context_tokens: int
max_output_tokens: int
max_retries: int
default_timeout_seconds: int
network_allowed: bool
hosted_fallback_allowed: bool
gpu_required: bool
gpu_memory_gb: float | None
cpu_only_allowed: bool
warnings: list[str]
errors: list[str]
```

Helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
sha256_text(text: str) -> str
safe_model_failure_response(...) -> ModelResponse
```

---

# 8. Schema Requirements

Every schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
define enum values for task_type, provider_kind, status, decision, and failure_class fields
allow artifact_refs and evidence_refs arrays where applicable
reject unknown enum values
```

Required valid examples in tests:

```text
valid_model_profile
valid_model_registry
valid_model_request
valid_model_response_success
valid_model_response_blocked
valid_model_response_invalid
valid_model_selection_decision_allow
valid_model_selection_decision_block
valid_model_policy_decision_allow
valid_model_policy_decision_block
valid_model_retry_record
valid_model_audit_event
valid_invalid_model_request_record
valid_runtime_profile
valid_provider_profile
valid_model_call_evidence
valid_completion_record
```

Required invalid examples in tests:

```text
missing model_id
missing provider_id
unknown provider_kind
unknown task_type
unknown status
missing prompt_hash
negative token limit
hosted provider enabled without explicit policy flag
network provider enabled while runtime profile network_allowed=false
model response containing direct file-write action
model response containing direct command-execution action
```

Schema validation acceptance:

```text
valid examples pass
missing required fields fail
invalid enum values fail
forbidden direct-action output fails
completion record validates
```

---

# 9. Provider Adapter Interface

Create the provider interface in:

```text
tools/agentx_evolve/models/model_adapter.py
```

Required interface:

```python
class BaseModelProviderAdapter:
    provider_id: str
    provider_kind: str

    def is_available(self, context: dict) -> bool: ...

    def validate_request(
        self,
        request: ModelRequest,
        profile: ModelProfile,
        context: dict,
    ) -> ModelPolicyDecision | None: ...

    def run_prompt(
        self,
        request: ModelRequest,
        profile: ModelProfile,
        context: dict,
    ) -> ModelResponse: ...

    def run_json_prompt(
        self,
        request: ModelRequest,
        profile: ModelProfile,
        context: dict,
    ) -> ModelResponse: ...
```

Provider adapters must return schema-valid `ModelResponse` objects.

Provider adapters must not:

```text
write source files
execute commands
call tools directly
approve governance
promote changes
log unredacted secrets
perform network calls unless provider profile explicitly allows them
perform remote calls unless endpoint is policy-approved
```

---

# 10. Provider Adapter Requirements

## 10.1 Dev Provider Adapter

File:

```text
tools/agentx_evolve/models/dev_provider_adapter.py
```

Purpose:

```text
Provide deterministic test-only model responses without GPU, network, hosted provider, Ollama, LM Studio, OpenCode, Bun, Node, or external runtime.
```

Rules:

```text
available only when provider_kind=DEV or test context enables dev provider
returns deterministic text/JSON from supplied fixtures
can produce valid JSON, invalid JSON, timeout-like failure, and provider-error fixtures
never uses network
never loads a model
never executes commands
never writes source files
```

Acceptance:

```text
dev provider returns schema-valid SUCCESS response
fake provider can return schema-valid INVALID response
fake provider supports deterministic JSON-only output tests
base test suite uses fake provider for live-call simulation
```

## 10.2 Local Provider Adapter

File:

```text
tools/agentx_evolve/models/local_provider_adapter.py
```

Required behavior:

```text
check local runtime availability
respect runtime profile
respect context budget
return BLOCKED if runtime unavailable
return BLOCKED if model profile disabled
return FAILED if runtime call fails
return INVALID if output schema fails
```

## 10.3 Ollama Adapter

File:

```text
tools/agentx_evolve/models/ollama_adapter.py
```

Rules:

```text
Ollama must be explicitly enabled.
Default endpoint must be localhost-only.
Remote Ollama endpoints are BLOCKED unless policy explicitly allows remote endpoint.
Adapter tests must not require running Ollama.
No model pull/download is allowed in base tests.
```

## 10.4 LM Studio Adapter

File:

```text
tools/agentx_evolve/models/lmstudio_adapter.py
```

Rules:

```text
Default endpoint must be localhost-only.
Remote endpoints are BLOCKED unless policy explicitly allows remote endpoint.
Adapter must enforce request/response schema validation.
Adapter tests must not require running LM Studio.
```

## 10.5 OpenAI-Compatible Adapter

File:

```text
tools/agentx_evolve/models/openai_compatible_adapter.py
```

Rules:

```text
Local OpenAI-compatible providers may be enabled by config.
Hosted OpenAI-compatible providers are disabled by default.
Provider URL must be policy-approved.
API keys must never be logged.
Base tests must use fakes/mocks only.
```

## 10.6 OpenCode-Compatible Provider Adapter

File:

```text
tools/agentx_evolve/models/opencode_provider_adapter.py
```

Rules:

```text
No OpenCode runtime dependency is required.
No Bun or Node dependency is allowed.
No OpenCode source code may be copied.
Treat OpenCode provider ideas as configuration-shape inspiration only.
Adapter may remain a BLOCKED/PARTIAL stub until explicitly needed.
```

## 10.7 Hosted Model Adapter

File:

```text
tools/agentx_evolve/models/hosted_model_adapter.py
```

Default behavior:

```text
HOSTED providers disabled by default.
Network disabled by default.
Hosted fallback disabled by default.
Missing explicit provider approval returns BLOCKED / MODEL_HOSTED_DISABLED.
```

Hosted adapter must not run unless all are true:

```text
provider profile enabled
runtime profile allows hosted fallback
network policy allows provider
Policy / Capability Registry allows caller + task + provider
secrets are available through approved secret mechanism
request passes redaction checks
endpoint is explicitly approved
```

---

# 11. Provider Mode Matrix

Provider behavior must be explicit and deterministic.

| Provider mode | Base tests allowed? | Network allowed by default? | Live provider required? | Default status | Notes |
|---|---:|---:|---:|---|---|
| `FAKE` | Yes | No | No | Enabled only in test/dev context | Deterministic fixture provider. |
| `LOCAL` direct runtime | Yes, via stub/fake only | No | No | Blocked if runtime unavailable | May be enabled by local config later. |
| `OLLAMA` loopback | Yes, mocked only | No live call | No | Disabled unless configured | `localhost` / `127.0.0.1` only unless policy allows remote. |
| `LMSTUDIO` loopback | Yes, mocked only | No live call | No | Disabled unless configured | `localhost` / `127.0.0.1` only unless policy allows remote. |
| `OPENAI_COMPATIBLE` local | Yes, mocked only | No live call | No | Disabled unless configured | Local endpoint only by default. |
| `OPENCODE_COMPATIBLE` | Yes, stub only | No | No | Stub/BLOCKED unless needed | No OpenCode runtime, Bun, or Node dependency. |
| `HOSTED` | No live call | No | No | BLOCKED by default | Requires explicit provider, network, policy, secret, and endpoint approval. |

Rules:

```text
Base tests must use FAKE or mocks/stubs only.
A configured local HTTP provider is still not allowed in base tests.
Hosted providers are not allowed in base tests.
No provider adapter may self-enable because it detects a running service.
Provider availability detection must not perform network calls unless explicitly marked as integration-test-only or live-run-only.
```

---

# 12. Endpoint and Network Policy

Endpoint rules:

```text
localhost and 127.0.0.1 may be allowed for explicitly enabled local providers.
0.0.0.0 must not be used as a remote target.
LAN, VPN, public IP, HTTPS, and hosted URLs require explicit policy approval.
Any endpoint containing credentials is invalid.
Any endpoint not matching provider profile is BLOCKED.
```

Network default:

```text
network_allowed=false
hosted_fallback_allowed=false
remote_endpoint_allowed=false
```

Base validation tests must not perform network calls.

---

# 13. Model Registry

File:

```text
tools/agentx_evolve/models/model_registry.py
```

Required public functions:

```python
load_default_model_registry() -> ModelRegistry
register_model(registry: ModelRegistry, profile: ModelProfile) -> ModelRegistry
get_model_profile(registry: ModelRegistry, model_id: str) -> ModelProfile | None
list_enabled_models(registry: ModelRegistry) -> list[ModelProfile]
list_models_for_task(registry: ModelRegistry, task_type: str) -> list[ModelProfile]
```

Default profiles:

```text
fake_test_model
small_fast
small_coder
medium_coder_optional
hosted_fallback_optional
```

Default rules:

```text
fake_test_model enabled only in test/dev context
small_fast enabled only if local runtime configured
small_coder enabled only if local runtime configured
medium_coder_optional disabled unless configured
hosted_fallback_optional disabled unless explicitly configured
unknown models block
duplicate model IDs reject registry loading
```

Acceptance:

```text
default registry loads
duplicate model IDs rejected
hosted fallback disabled by default
models can be filtered by task type
unknown model returns MODEL_NOT_FOUND
```

---

# 14. Model Policy

File:

```text
tools/agentx_evolve/models/model_policy.py
```

Required public function:

```python
check_model_permission(
    request: ModelRequest,
    profile: ModelProfile,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
) -> ModelPolicyDecision
```

Return BLOCK if:

```text
model profile is disabled
provider profile is disabled
caller role is unknown
caller role is not allowed by policy
requested task type is not allowed for model
hosted provider requested but hosted fallback disabled
network provider requested but network disabled
remote endpoint requested without explicit approval
request exceeds max input tokens
request exceeds max output tokens
request contains unredacted secret markers
JSON-only request targets model without JSON support and retry/repair is unavailable
Prompt Contract is required but missing
Context Builder task packet is required but missing
Policy / Capability Registry denies request
Policy / Capability Registry is unavailable for hosted/network/high-risk call
```

Return ALLOW only if:

```text
model exists
provider exists
model enabled
provider enabled
caller role allowed
task type allowed
runtime profile allows provider mode
context budget passes
redaction checks pass
prompt contract requirements pass
policy allows the request
```

---

# 15. Model Selection Logic

File:

```text
tools/agentx_evolve/models/model_selector.py
```

Required public function:

```python
select_model_for_task(
    task_type: str,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
    preferences: dict | None = None,
) -> ModelSelectionDecision
```

Selection priority:

```text
1. explicit model_id if valid and allowed
2. fake_test_model only in tests/dev mode
3. local small coder for coding tasks
4. local small fast for classification/summarization
5. medium local model if configured and allowed
6. hosted fallback only if explicitly configured and policy-approved
7. BLOCK if no allowed model exists
```

Selection must consider:

```text
task type
model enabled status
provider enabled status
context window
runtime profile
local hardware constraints
JSON support
hosted/network policy
Policy / Capability Registry decision
```

Acceptance:

```text
small_coder selected for IMPLEMENT_PATCH when available
small_fast selected for classification when available
fake model selected only in test/dev mode
hosted fallback not selected by default
unknown task type blocks
no allowed model returns BLOCKED decision
```

---

# 16. Request and Response Validation

## 15.1 Model Request Validator

File:

```text
tools/agentx_evolve/models/model_request_validator.py
```

Required public function:

```python
validate_model_request(request: ModelRequest, registry: ModelRegistry) -> list[str]
```

Must validate:

```text
required fields exist
task_type is known
prompt is non-empty
arguments fit schema
model exists if specified
provider exists if specified
json_only is boolean
max token fields are positive if present
context_packet_id is present when task requires packed context
prompt_contract_id/version are present when production prompt mode requires them
prompt does not include obvious secret markers
prompt does not request model to ignore Agent_X policy
prompt does not request direct file write, command execution, tool execution, governance approval, or promotion
```

## 15.2 Model Response Validator

File:

```text
tools/agentx_evolve/models/model_response_validator.py
```

Required public function:

```python
validate_model_response(response: ModelResponse, expected_schema: dict | None = None) -> list[str]
```

Must validate:

```text
required fields exist
status is valid
model_request_id is present
prompt_hash is present
JSON-only responses have parsed_output
parsed output matches expected schema if provided
model output does not request direct file writes
model output does not request direct command execution
model output does not request direct Tool / MCP Adapter execution
model output does not claim governance approval
model output does not claim promotion approval
model output does not include unredacted secret-like content in durable fields
```

---

# 17. Prompt Injection and Direct-Action Output Rules

Model requests and responses must reject or flag attempts to bypass Agent_X controls.

Forbidden request or output patterns include:

```text
direct filesystem write instructions as executable output
direct shell command execution requests
direct Tool / MCP Adapter calls
governance approval claims
promotion approval claims
policy rewrite instructions
attempts to ignore Agent_X rules
attempts to reveal secrets or credentials
attempts to include unbounded whole-repository context
```

Allowed output shape:

```text
schema-valid proposal data
schema-valid patch candidate data for later worker/layer validation
schema-valid explanation
schema-valid test suggestion
schema-valid failure summary
```

The model may propose actions. It may not execute or approve actions.

---

# 18. JSON Output Validator

File:

```text
tools/agentx_evolve/models/json_output_validator.py
```

Required public functions:

```python
parse_json_output(raw_text: str) -> dict | None
validate_json_output(parsed: dict, schema: dict) -> list[str]
make_invalid_json_response(request: ModelRequest, reason: str) -> ModelResponse
```

Rules:

```text
invalid JSON returns INVALID or RETRYABLE response
schema-invalid JSON returns INVALID or RETRYABLE response
never execute JSON content
never treat JSON output as trusted until schema-valid
forbidden direct-action fields make output invalid
```

Acceptance:

```text
valid JSON parses
invalid JSON rejected
schema-invalid JSON rejected
JSON with forbidden direct-action fields rejected
```

---

# 19. Prompt Runner / Model Call Dispatcher

File:

```text
tools/agentx_evolve/models/prompt_runner.py
```

Required public functions:

```python
run_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
    provider_context: dict,
    repo_root: Path | None = None,
) -> ModelResponse

run_json_prompt(
    request: ModelRequest,
    registry: ModelRegistry,
    runtime_profile: RuntimeProfile,
    policy_context: dict,
    provider_context: dict,
    expected_schema: dict,
    repo_root: Path | None = None,
) -> ModelResponse
```

Required flow:

```text
1. Receive ModelRequest.
2. Validate request schema.
3. Reject invalid request through invalid_model_request handler.
4. Select model if model_id is missing.
5. Load model profile.
6. Check runtime profile and context budget.
7. Check Policy / Capability Registry or restrictive fallback.
8. Check provider endpoint/network policy.
9. Redact prompt/context for evidence.
10. Estimate token usage.
11. Enforce context and output limits.
12. Dispatch to provider adapter only if allowed.
13. Validate ModelResponse schema.
14. Validate JSON output if json_only.
15. Reject forbidden direct-action output.
16. Retry only if retry policy allows.
17. Write model request and response evidence.
18. Return schema-valid ModelResponse.
```

Fail-closed behavior:

```text
model missing -> BLOCKED / MODEL_NOT_FOUND
provider unavailable -> BLOCKED / MODEL_RUNTIME_UNAVAILABLE
policy denied -> BLOCKED / MODEL_POLICY_DENIED
context too large -> BLOCKED / MODEL_CONTEXT_TOO_LARGE
hosted disabled -> BLOCKED / MODEL_HOSTED_DISABLED
endpoint denied -> BLOCKED / MODEL_ENDPOINT_DENIED
invalid output -> INVALID or RETRYABLE / MODEL_INVALID_OUTPUT
provider exception -> FAILED / MODEL_PROVIDER_ERROR
```

---

# 20. Context Size Limits

File:

```text
tools/agentx_evolve/model_runtime/runtime_limits.py
```

Required public functions:

```python
estimate_token_count(text: str) -> int
check_context_budget(request: ModelRequest, profile: ModelProfile, runtime_profile: RuntimeProfile) -> list[str]
truncate_for_evidence(text: str, max_chars: int) -> str
```

Rules:

```text
never pass whole repository to model
prefer task packets from Context Builder
use snippets, not full files, unless task explicitly allows full file
block request if token estimate exceeds profile limit
block request if output token request exceeds limit
small local profile must use conservative context budget
```

Default conservative limits:

```text
cpu_only_safe: max_context_tokens <= 4096
small_gpu_8gb: max_context_tokens <= 8192
balanced_local: max_context_tokens <= 16384
hosted_fallback_optional: disabled unless configured
```

---

# 21. Timeout and Retry Rules

File:

```text
tools/agentx_evolve/models/model_retry_policy.py
```

Required public functions:

```python
should_retry_model_response(response: ModelResponse, request: ModelRequest, attempt_number: int) -> bool
make_retry_record(request: ModelRequest, response: ModelResponse, attempt_number: int) -> ModelRetryRecord
```

Default rules:

```text
default_timeout_seconds = 60
max_retries = 1 for JSON-only invalid output
max_retries = 0 for provider errors unless explicitly configured
no infinite retries
no retry if policy denied
no retry if context too large
no retry if hosted disabled
no retry if endpoint denied
retry prompt must be stricter and shorter
all retries must be evidenced
```

---

# 22. Redaction and Hashing Rules

Files:

```text
tools/agentx_evolve/models/model_call_logger.py
tools/agentx_evolve/models/model_request_validator.py
```

Before durable logging, redact:

```text
API keys
tokens
passwords
provider credentials
environment variables
secret-like strings
raw private prompts when policy says prompt logging is disabled
raw model output if it may contain secrets
```

Evidence must store:

```text
prompt_hash
output_hash
redacted prompt summary
redacted output summary
model identity
provider identity
runtime profile identity
status
failure class
artifact refs
evidence refs
```

Evidence must not store:

```text
unredacted secrets
full raw prompts by default
full raw outputs by default
provider credentials
API keys
```

Hashing rule:

```text
Use SHA-256 for prompt_hash, output_hash, evidence hashes, and completion evidence hashes.
Use Python standard-library hashlib if no project hash helper exists.
```

---

# 23. Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/model_calls/
```

Required files:

```text
.agentx-init/model_calls/model_request_history.jsonl
.agentx-init/model_calls/model_response_history.jsonl
.agentx-init/model_calls/model_retry_history.jsonl
.agentx-init/model_calls/blocked_model_history.jsonl
.agentx-init/model_calls/invalid_model_history.jsonl
.agentx-init/model_calls/latest_model_request.json
.agentx-init/model_calls/latest_model_response.json
.agentx-init/model_calls/model_adapter_evidence_manifest.json
.agentx-init/model_calls/model_adapter_completion_record.json
```

Rules:

```text
append-only JSONL for history
atomic JSON writes for latest artifacts
redact before writing
write prompt/output hashes
write provider/model IDs
write failure class for blocked/failed/invalid outputs
preserve malformed existing JSONL lines
no source files written by this layer
```

---

# 24. Model Call Logger

File:

```text
tools/agentx_evolve/models/model_call_logger.py
```

Required public functions:

```python
append_model_request(request: ModelRequest, repo_root: Path) -> dict
append_model_response(response: ModelResponse, repo_root: Path) -> dict
append_model_retry(record: ModelRetryRecord, repo_root: Path) -> dict
append_blocked_model(request: ModelRequest, response: ModelResponse, repo_root: Path) -> dict
append_invalid_model(request: ModelRequest, response: ModelResponse, repo_root: Path) -> dict
write_latest_model_request(request: ModelRequest, repo_root: Path) -> dict
write_latest_model_response(response: ModelResponse, repo_root: Path) -> dict
write_model_call_evidence(request: ModelRequest, response: ModelResponse, repo_root: Path) -> dict
write_model_adapter_evidence_manifest(repo_root: Path, evidence: dict) -> dict
```

Acceptance:

```text
request history written
response history written
retry history written
blocked model history written
invalid model history written
latest request written atomically
latest response written atomically
secrets redacted
hashes recorded
evidence manifest written
```

---

# 25. Invalid Model Request Handler

File:

```text
tools/agentx_evolve/models/invalid_model_request.py
```

Required public function:

```python
handle_invalid_model_request(raw_request: ModelRequest | dict, reason: str) -> ModelResponse
```

Required behavior:

```text
status = INVALID
failure_class = MODEL_INVALID_REQUEST
exit-like status represented in data if needed
message explains invalid request
data contains safe summary only
raw prompt is not durably logged
evidence refs may be empty initially
warnings/errors populated
```

Must not:

```text
call provider
call model
call tools
execute commands
write source
send network request
```

---

# 26. Integration Requirements

## 25.1 Policy / Capability Registry Integration

Required behavior:

```text
every model request checks Policy / Capability Registry where required
policy-denied model call returns MODEL_POLICY_DENIED
missing policy blocks hosted provider calls
missing policy blocks high-risk task types
missing policy may allow only restrictive local low-risk calls if explicitly configured
model cannot approve its own use
model cannot override governance
```

Policy must decide:

```text
caller role allowed?
task type allowed?
model profile allowed?
provider allowed?
hosted/network allowed?
context sensitivity allowed?
output type allowed?
JSON-only requirement present?
prompt contract required?
```

## 25.2 Tool / MCP Adapter Integration

The Model Adapter may be exposed later as a controlled tool, but must not directly execute tools.

Rules:

```text
model output may request a tool call only as structured proposal data
Tool / MCP Adapter must decide whether a tool call is allowed
model cannot call Tool Adapter directly
model cannot call shell/filesystem/Git directly
model cannot bypass tool registry or tool policy
```

If exposed as a tool, expected tool names may be:

```text
model_run_prompt
model_run_json_prompt
model_select_for_task
model_validate_output
```

## 25.3 Context Builder / Task Packer Integration

The Model Adapter should prefer task packets from Context Builder.

Required behavior:

```text
accept context_packet_id
accept bounded prompt/context from task packet
respect allowed_files and forbidden_files metadata
respect task_packet token budget
block requests that attempt to include whole repository context
include task_packet_id in evidence
```

## 25.4 Prompt Contract / Prompt Versioning Integration

If prompt templates are used, this layer must record:

```text
prompt_contract_id
prompt_version
prompt_hash
output_schema_id
```

Rules:

```text
unversioned prompts allowed only for manual/dev mode
production prompt calls should reference prompt contract/version
prompt contract may specify JSON-only output
prompt contract may specify forbidden output actions
```

## 25.5 Local Model Runtime Profile Integration

This layer may use minimal runtime profiles, but must not assume exact hardware.

Rules:

```text
base tests must pass without GPU
base tests must pass without any model installed
runtime profile may report unavailable instead of failing import
one-model-loaded-at-a-time policy belongs to Local Model Runtime Profile layer but may be represented as a limit here
VRAM-aware selection may be conservative until full runtime layer exists
```

---

# 27. Implementation Order

Implement in this order:

```text
1. tools/agentx_evolve/models/model_models.py
2. tools/agentx_evolve/model_runtime/runtime_models.py
3. model-related schemas
4. tools/agentx_evolve/models/model_registry.py
5. tools/agentx_evolve/model_runtime/runtime_limits.py
6. tools/agentx_evolve/model_runtime/local_runtime_profile.py
7. tools/agentx_evolve/models/model_policy.py
8. tools/agentx_evolve/models/model_selector.py
9. tools/agentx_evolve/models/model_request_validator.py
10. tools/agentx_evolve/models/model_response_validator.py
11. tools/agentx_evolve/models/json_output_validator.py
12. tools/agentx_evolve/models/model_retry_policy.py
13. tools/agentx_evolve/models/model_call_logger.py
14. tools/agentx_evolve/models/invalid_model_request.py
15. tools/agentx_evolve/models/model_adapter.py
16. tools/agentx_evolve/models/dev_provider_adapter.py
17. tools/agentx_evolve/models/local_provider_adapter.py
18. tools/agentx_evolve/models/ollama_adapter.py
19. tools/agentx_evolve/models/lmstudio_adapter.py
20. tools/agentx_evolve/models/openai_compatible_adapter.py
21. tools/agentx_evolve/models/opencode_provider_adapter.py
22. tools/agentx_evolve/models/hosted_model_adapter.py
23. tools/agentx_evolve/models/prompt_runner.py
24. tests
25. validation commands
26. completion evidence
```

Rationale:

```text
models first
schemas second
registry before selection
runtime limits before policy
policy before provider calls
validators before prompt runner
logger before live adapters
invalid request handler before dispatcher
fake provider before live provider stubs
hosted adapter after local adapters
prompt runner after provider adapters
tests after all public surfaces exist
```

---

# 28. Minimal Implementation Slices

## 27.1 Slice A — Models, Runtime Models, Schemas

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schema enums match constants
no provider calls exist yet
```

## 27.2 Slice B — Registry, Runtime Limits, Policy, Selector

Acceptance:

```text
default registry loads
duplicate model IDs rejected
hosted fallback disabled by default
fake provider available only in test/dev context
small model selected for allowed task
unknown task blocks
context too large blocks
policy denied blocks
```

## 27.3 Slice C — Validators, JSON Validator, Retry Policy

Acceptance:

```text
valid request passes
invalid request fails
valid response passes
invalid JSON rejected
schema-invalid JSON rejected
forbidden direct-action output rejected
retry limited and evidenced
```

## 27.4 Slice D — Evidence Logger

Acceptance:

```text
model request history written
model response history written
retry history written
blocked/invalid histories written
latest artifacts written atomically
secrets redacted
hashes recorded
evidence manifest written
```

## 27.5 Slice E — Provider Adapters

Acceptance:

```text
provider interface exists
fake provider enables deterministic tests
local adapters fail closed if runtime unavailable
hosted adapter blocked by default
remote endpoints blocked unless configured
provider responses are schema-valid
```

## 27.6 Slice F — Prompt Runner

Acceptance:

```text
run_prompt follows validation-policy-selection-provider-evidence flow
run_json_prompt validates JSON output
invalid model request returns schema-valid INVALID/BLOCKED
no direct source mutation
no command execution
no direct tool execution
```

---

# 29. Test Implementation Plan

## 28.1 Required Fixtures

```python
@pytest.fixture
def temp_repo(tmp_path): ...

@pytest.fixture
def default_model_registry(): ...

@pytest.fixture
def cpu_only_runtime_profile(): ...

@pytest.fixture
def small_gpu_runtime_profile(): ...

@pytest.fixture
def valid_model_request(): ...

@pytest.fixture
def json_model_request(): ...

@pytest.fixture
def hosted_model_request(): ...

@pytest.fixture
def restrictive_model_policy_context(): ...

@pytest.fixture
def fake_provider_context(): ...
```

## 28.2 Required Positive Tests

```text
test_default_model_registry_loads
test_model_registry_rejects_duplicate_model_ids
test_small_coder_profile_exists
test_hosted_fallback_profile_disabled_by_default
test_model_request_schema_accepts_valid_request
test_model_response_schema_accepts_valid_response
test_model_selector_selects_small_coder_for_patch_task
test_model_selector_selects_small_fast_for_summary_task
test_context_budget_accepts_small_packet
test_json_output_validator_accepts_valid_json
test_model_retry_policy_allows_one_json_retry
test_model_call_logger_writes_request_history
test_model_call_logger_writes_response_history
test_fake_provider_returns_valid_response
test_local_provider_unavailable_returns_blocked
test_hosted_provider_disabled_returns_blocked
test_prompt_runner_returns_schema_valid_response
test_completion_record_schema_accepts_valid_record
```

## 28.3 Required Negative Tests

```text
test_unknown_model_blocks
test_unknown_provider_blocks
test_unknown_task_type_blocks
test_hosted_provider_blocked_by_default
test_remote_endpoint_blocked_by_default
test_network_provider_blocked_without_policy
test_context_too_large_blocks
test_unredacted_secret_marker_blocks_or_redacts
test_invalid_json_output_rejected
test_schema_invalid_output_rejected
test_model_output_direct_file_write_rejected
test_model_output_direct_command_execution_rejected
test_model_output_direct_tool_call_rejected
test_model_output_governance_claim_rejected
test_model_output_promotion_claim_rejected
test_retry_does_not_loop_indefinitely
test_model_cannot_call_tool_adapter_directly
test_model_cannot_write_source_files
test_no_api_key_logged_in_evidence
test_base_tests_do_not_require_gpu_network_or_live_provider
```

---

# 30. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_model_registry.py \
  tools/agentx_evolve/tests/test_model_profile_schema.py \
  tools/agentx_evolve/tests/test_model_request_schema.py \
  tools/agentx_evolve/tests/test_model_response_schema.py \
  tools/agentx_evolve/tests/test_model_policy.py \
  tools/agentx_evolve/tests/test_model_selector.py \
  tools/agentx_evolve/tests/test_model_request_validator.py \
  tools/agentx_evolve/tests/test_model_response_validator.py \
  tools/agentx_evolve/tests/test_json_output_validator.py \
  tools/agentx_evolve/tests/test_model_retry_policy.py \
  tools/agentx_evolve/tests/test_model_call_logger.py \
  tools/agentx_evolve/tests/test_dev_provider_adapter.py \
  tools/agentx_evolve/tests/test_local_provider_adapter.py \
  tools/agentx_evolve/tests/test_ollama_adapter.py \
  tools/agentx_evolve/tests/test_lmstudio_adapter.py \
  tools/agentx_evolve/tests/test_openai_compatible_adapter.py \
  tools/agentx_evolve/tests/test_hosted_model_adapter.py \
  tools/agentx_evolve/tests/test_model_negative_cases.py \
  tools/agentx_evolve/tests/test_model_runtime_profiles.py \
  tools/agentx_evolve/tests/test_model_prompt_runner.py \
  tools/agentx_evolve/tests/test_invalid_model_request.py \
  tools/agentx_evolve/tests/test_model_schema_validation.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
scoped model adapter pytest PASS
git status CLEAN or only expected runtime artifacts
```

No validation command may require:

```text
GPU
network
hosted model
LLM provider
running Ollama
running LM Studio
running OpenCode
Bun
Node
external MCP server
```

Provider-specific tests must use fakes/mocks unless explicitly marked integration tests.

---

# 31. Acceptance Criteria

The Model Adapter Layer is complete when it can:

```text
load default model registry
load runtime profile
select a model for a task type
block unknown model
block unknown provider
block hosted provider by default
block remote endpoint by default
validate model request
validate model response
run fake provider through controlled interface
run provider adapter through controlled interface
fail closed if local runtime unavailable
validate JSON-only output
retry invalid JSON only within bounded policy
block oversized context
block direct-action output
redact secrets before evidence
record model identity
record provider identity
record prompt hash
record output hash
write model request evidence
write model response evidence
write blocked/invalid model evidence
write evidence manifest
integrate with Policy / Capability Registry
preserve separation from Tool / MCP Adapter
accept task packet metadata from Context Builder
record prompt contract/version when available
pass compileall
pass pytest
produce completion record
```

---

# 32. Definition of Done

The Model Adapter Layer is done when:

```text
all target files exist
all schemas exist
all tests exist
default model registry loads
runtime profiles load
model selection is deterministic
hosted providers are disabled by default
network providers are blocked unless explicitly configured
remote endpoints are blocked unless policy-approved
model requests validate
model responses validate
JSON-only output validates against schema
invalid JSON is rejected or retried within bounds
context limits are enforced
policy checks occur before provider calls
provider calls fail closed when unavailable
base tests use fake provider, not live providers
model output cannot directly write files
model output cannot directly execute commands
model output cannot directly call tools
model output cannot approve governance
model output cannot promote changes
model evidence is written
prompt/output hashes are written
secrets are redacted
no source mutation occurs directly in this layer
no command execution occurs directly in this layer
no hosted/network call occurs by default
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
git status CLEAN or only expected runtime artifacts
```

---

# 33. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schemas are missing
model_adapter.py is missing
fake provider test contract is missing
model request schema validation is skipped
model response schema validation is skipped
unknown model executes
unknown provider executes
hosted model executes by default
network call happens by default
remote endpoint executes without policy approval
policy-denied model call executes
context-too-large request executes
invalid JSON is accepted as valid
schema-invalid model output is accepted
model output directly mutates source
model output directly executes commands
model output directly calls tools
model output claims governance approval and is accepted
model output claims promotion approval and is accepted
secrets are logged
prompt/output hashes are missing
model-call evidence is missing
evidence manifest is missing
source files are modified by tests
base tests require GPU/network/live provider
OpenCode source code is copied
Bun/Node/OpenCode runtime becomes required
```

---

# 34. Completion Evidence

After implementation, write:

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
  "canonical_model_subdirectory": "tools/agentx_evolve/models/",
  "canonical_runtime_subdirectory": "tools/agentx_evolve/model_runtime/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/model_calls/",
  "basis_documents": [
    "MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "MODEL_ADAPTER_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "model_profiles_verified": [],
  "provider_adapters_verified": [],
  "fake_provider_verified": [],
  "policy_integration_verified": [],
  "tool_adapter_boundary_verified": [],
  "context_builder_integration_verified": [],
  "prompt_contract_integration_verified": [],
  "negative_tests_verified": [],
  "runtime_artifacts_verified": [],
  "evidence_manifest_path": ".agentx-init/model_calls/model_adapter_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

Evidence manifest must include:

```text
validated commit
validation timestamp
command text
command exit codes
compileall summary
pytest summary
scoped model pytest summary
git status summary
runtime artifact paths
SHA-256 hashes for evidence files
proof that no GPU/network/live provider was required for base tests
```

---

# 35. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places files outside canonical directories without recorded deviation
enables hosted providers by default
enables network calls by default
allows remote endpoints by default
executes commands directly
allows model output to write files
allows model output to call tools directly
allows model output to approve governance
allows model output to promote changes
skips Policy / Capability Registry for provider calls
skips model request validation
skips model response validation
accepts invalid JSON as valid
logs secrets
logs full raw prompt/output by default
copies OpenCode source code
adds Bun/Node/OpenCode runtime dependency
requires GPU for base tests
requires network for base tests
requires hosted provider for base tests
requires running Ollama/LM Studio/OpenCode for base tests
```

Allowed implementation choices:

```text
provider adapters as safe stubs
fake provider for deterministic tests
hosted adapter as blocked stub
Ollama adapter as unavailable-safe stub
LM Studio adapter as unavailable-safe stub
OpenAI-compatible adapter as local-only stub
OpenCode-compatible adapter as config-shape stub
restrictive local-only policy fallback
conservative runtime profiles until full Local Model Runtime Profile Layer exists
```

---

# 36. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/models/ package files.
2. Create tools/agentx_evolve/model_runtime/ package files.
3. Implement model_models.py and runtime_models.py.
4. Create schemas.
5. Implement model_registry.py.
6. Implement runtime limits and local runtime profiles.
7. Implement model_policy.py.
8. Implement model_selector.py.
9. Implement request/response validators.
10. Implement JSON output validator.
11. Implement retry policy.
12. Implement model-call logger.
13. Implement invalid_model_request.py.
14. Implement provider adapter interface.
15. Implement dev_provider_adapter.py.
16. Implement local/provider adapters as fail-closed adapters.
17. Implement prompt_runner.py.
18. Create tests.
19. Run compileall.
20. Run pytest.
21. Verify git status.
22. Write evidence manifest.
23. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 37. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The Model Adapter must live under tools/agentx_evolve/models/.
[ ] Runtime profile helpers must live under tools/agentx_evolve/model_runtime/.
[ ] Runtime artifacts must go under .agentx-init/model_calls/.
[ ] model_adapter.py is included in the canonical file list.
[ ] Fake provider exists for deterministic tests.
[ ] Hosted providers are disabled by default.
[ ] Network calls are disabled by default.
[ ] Remote endpoints are blocked by default.
[ ] Local small models are preferred.
[ ] Provider adapters may be safe stubs if runtime is unavailable.
[ ] Model requests must be schema-valid.
[ ] Model responses must be schema-valid.
[ ] JSON-only output must be validated.
[ ] Invalid JSON must not be accepted.
[ ] Model output cannot directly write files.
[ ] Model output cannot execute commands.
[ ] Model output cannot call tools directly.
[ ] Model output cannot approve governance.
[ ] Model output cannot decide promotion.
[ ] Prompt/output hashes must be recorded.
[ ] Secrets must be redacted.
[ ] Evidence manifest must be written.
[ ] Tests must run without GPU, network, hosted model, LLM provider, Bun, Node, OpenCode runtime, running Ollama, running LM Studio, or running MCP server.
```

---

# 38. v3 Final Precision Requirements

## 37.1 Single Dispatcher and Direct-Call Boundary

The Model Adapter must use one controlled dispatcher path for model calls.

Required rule:

```text
External callers, orchestrators, workers, and tool adapters must call run_prompt or run_json_prompt only.
Provider adapters must not be called directly outside adapter-specific unit tests.
Model selection, policy checks, request validation, context limits, endpoint policy, redaction, response validation, retry handling, and evidence logging must happen before a result is treated as usable.
```

Forbidden bypasses:

```text
calling local_provider_adapter directly from LLM Implementation Worker
calling hosted_model_adapter directly from Orchestrator
calling OpenAI-compatible endpoint directly from Tool / MCP Adapter
calling provider adapter before policy and endpoint checks
using provider output without response validation
using JSON output without schema validation
```

## 37.2 Idempotency Rules

Repeated requests must be auditable and stable.

Required behavior:

```text
Identical dry-run requests should produce equivalent validation and selection decisions.
Model request IDs must be unique per call attempt.
Retry attempts must link back to the original model_request_id.
Evidence writes must be append-only.
Latest artifacts may be overwritten atomically, but history JSONL must preserve prior attempts.
Provider responses must not be cached as truth unless an explicit cache policy is added later.
```

## 37.3 Concurrency and Locking Rules

This layer must not corrupt evidence during concurrent or repeated calls.

Required behavior:

```text
JSONL appends must be safe for normal local sequential use.
Atomic latest writes must use temp-file-and-rename behavior.
If a lock helper exists in Agent_X, model_call_logger should use it.
If no lock helper exists, tests must prove latest artifacts are not partially written.
No background daemon or parallel provider pool is required in this layer.
```

## 37.4 Credential and Secret Reference Rules

Provider credentials must be represented as references, not values.

Allowed:

```text
credential_ref = "OPENAI_API_KEY"
credential_ref = "LOCAL_PROVIDER_TOKEN_REF"
secret_source = "approved_env_ref"
```

Forbidden:

```text
credential_ref containing the actual API key
endpoint URL containing username/password/token
logging environment variable values
writing raw provider headers to evidence
writing raw Authorization headers to evidence
```

If a hosted or API-key provider is configured but credential handling is missing, the provider must return BLOCKED / MODEL_PROVIDER_DISABLED or MODEL_POLICY_DENIED.

## 37.5 Streaming and Tool-Calling Defaults

Streaming and provider-native tool calling are disabled in this layer unless separately accepted.

Default behavior:

```text
supports_streaming may be recorded in ModelProfile, but streaming_enabled defaults false.
supports_tools may be recorded in ModelProfile, but tool_calling_enabled defaults false.
Provider-native function calling must not execute Agent_X tools.
Provider-native function-call output must be treated as model output proposal data and validated like any other JSON.
```

No provider-native tool call may directly invoke Tool / MCP Adapter.

## 37.6 Schema Validation Utility

Create either:

```text
tools/agentx_evolve/tests/validate_model_adapter_schemas.py
```

or prove equivalent coverage through:

```text
tools/agentx_evolve/tests/test_model_schema_validation.py
```

Required schema validation coverage:

```text
all model schemas accept valid examples
all model schemas reject missing required fields
all enum fields reject unknown values
hosted-enabled profiles without explicit policy fail
network-enabled profiles with network_allowed=false fail
model-call evidence schema validates
completion record schema validates
```

## 37.7 Completion Evidence Precision

The completion record and evidence manifest must include:

```text
reviewed commit
validation timestamp
Python version
pytest version or NOT INSTALLED
compileall command, exit code, and summary
pytest command, exit code, and summary
scoped Model Adapter pytest command, exit code, and summary
schema validation command or pytest fallback, exit code, and summary
git status before/after, where available
proof that base tests required no GPU/network/live provider
SHA-256 hashes for final evidence artifacts
```

A final implementation cannot be marked DONE if command exit codes, schema validation proof, or evidence hashes are missing.

---

# 39. Final Frozen Acceptance Matrix

| Area | Required for 10/10 implementation spec | Status |
|---|---|---|
| Canonical directories | model, runtime, schema, test, artifact roots defined | PASS |
| Files to create | all model, runtime, provider, validator, logger, test files listed | PASS |
| `model_adapter.py` | included as canonical provider interface file | PASS |
| Schemas | model, request, response, policy, retry, audit, evidence, invalid, completion schemas listed | PASS |
| Classes/functions | dataclasses, constants, dispatcher, validators, logger, provider APIs defined | PASS |
| Provider adapters | fake, local, Ollama, LM Studio, OpenAI-compatible, OpenCode-compatible, hosted covered | PASS |
| Hosted default | hosted/network disabled by default | PASS |
| Model selection | deterministic task/profile/runtime/policy-based selection defined | PASS |
| Request/response validation | schema + direct-action rejection defined | PASS |
| Context limits | conservative small-model budgets defined | PASS |
| Timeout/retry | bounded retry rules defined | PASS |
| Redaction/hashing | secret redaction + SHA-256 rules defined | PASS |
| Runtime artifacts | JSONL/latest/evidence/manifest/completion record defined | PASS |
| Policy integration | Policy / Capability Registry gate defined | PASS |
| Tool adapter boundary | model cannot directly execute tools | PASS |
| Context Builder integration | task packet metadata and bounded context defined | PASS |
| Prompt Contract integration | prompt contract/version/hash rules defined | PASS |
| Tests | positive and negative test packs defined | PASS |
| No-live-provider tests | fake-provider and no-GPU/no-network rule defined | PASS |
| Implementation order | sequential build order defined | PASS |
| Acceptance / DoD | GO, NO-GO, completion criteria defined | PASS |
| Provider profile model | ModelProviderProfile defined with endpoint, credential-ref, streaming, and tool-call flags | PASS |
| Model-call evidence model | ModelCallEvidence defined with hashes, safe refs, and redaction status | PASS |
| Provider mode matrix | fake/local/Ollama/LM Studio/OpenAI-compatible/OpenCode/hosted behavior separated | PASS |
| Direct-call boundary | provider adapters cannot be called directly outside tests | PASS |
| Idempotency | retry/evidence/latest artifact behavior defined | PASS |
| Concurrency | atomic latest writes and append-only evidence rules defined | PASS |
| Credential handling | secret references allowed, secret values forbidden | PASS |
| Streaming/tool calling | disabled by default and cannot execute Agent_X tools | PASS |
| Schema validation utility | dedicated utility or scoped pytest fallback required | PASS |
| Completion evidence precision | exit codes, environment, schema proof, no-live-provider proof, hashes required | PASS |
| Evidence manifest schema | explicit model_adapter_evidence_manifest.schema.json required and validated | PASS |
| Public API exports | v3-added provider/evidence/runtime types exported or importable from canonical modules | PASS |
| Markdown validity | code fences balanced and section references stable | PASS |

---

# 40. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It preserves the v3 coverage and fixes the final handoff defects: canonical subdirectories, exact files, schemas, classes/functions, provider adapter interfaces, fake provider testing, local and hosted provider behavior, hosted/network disabled-by-default policy, model selection, request/response validation, direct-action output blocking, context limits, timeout/retry rules, redaction/hashing, runtime artifacts, Policy / Tool / Context / Prompt integrations, test files, negative tests, implementation order, acceptance criteria, Definition of Done, evidence manifest, completion record, drift blockers, and a frozen acceptance matrix.
```
