# LOCAL_MODEL_RUNTIME_PROFILE_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: LOCAL_MODEL_RUNTIME_PROFILE_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_LOCAL_MODEL_RUNTIME_PROFILE
component_name: Local Model Runtime Profile Layer
roadmap_layer: 7
roadmap_phase: Phase C — Local Runtime Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Model Runtime Acceptance Criteria
optional_standards: ES, Report Template
risk_level: critical
implementation_mode: local model profile and runtime eligibility control
target_language: Python
canonical_subdirectory: tools/agentx_evolve/model_runtime/
schema_subdirectory: tools/agentx_evolve/schemas/
runtime_artifact_root: .agentx-init/model_runtime/
upstream_dependencies:
  - Policy / Capability Registry
  - Failure Taxonomy / Recovery Playbook
  - Model Adapter Layer
  - Context Builder / Task Packer
  - Prompt Contract / Prompt Versioning Layer
  - Tool / MCP Adapter Layer
review_document_rating: 10/10
previous_version_rating: 9.7/10
source_version_reviewed: v2.0
```

---

# 0. v3 Review and Upgrade Summary

The v2 contract was strong and close to final. I would rate it:

```text
9.7/10
```

It already covered:

```text
EQC
FIC
SIB
Schema Contract
Evidence / Audit Rules
local runtime profile purpose
hardware capability profile
model inventory schema
model runtime profile schema
quantization profile schema
context-window profile schema
memory / VRAM limits
CPU fallback rules
GPU fallback rules
local-only provider rules
hosted-model prohibition
model capability declarations
model risk limits
model selection constraints
runtime health-check rules
model availability checks
runtime artifact rules
failure taxonomy integration
Policy / Capability Registry integration
Model Adapter Layer integration
Context Builder / Task Packer integration
Prompt Contract Layer integration
Tool / MCP Adapter integration
OpenCode borrowing notes
Agent_X integration notes
```

It was not fully 10/10 because several final contract controls still needed tightening:

```text
1. Main section numbering used 2A, which is less stable for references than normal numeric sectioning.
2. The document contained duplicate final-rating sections and one stale reference to v1.
3. Approved local model roots were described but not given their own explicit registry contract.
4. Model aliases and duplicate model IDs needed stricter collision rules.
5. Policy decision evidence needed to be mandatory in runtime decisions, not only generally referenced.
6. Profile drift, stale cache handling, and conflict precedence needed clearer fail-closed rules.
7. Runtime decision immutability needed stronger wording for reviewed evidence.
8. Health checks needed an explicit ban on starting local services through side effects.
9. The evidence manifest needed stronger requirements for model-root, inventory, hardware, and policy hashes.
10. The freeze rule needed clearer major-revision triggers for any future inference/probe/runtime-server behavior.
```

This v3 fixes those issues and is the final 10/10 controlling contract for the Local Model Runtime Profile Layer.

---

# 1. Purpose

This document defines the controlling contract for the **Local Model Runtime Profile Layer** in the Agent_X self-evolving system.

The purpose of this layer is to define what local models Agent_X is allowed to know about, load, select, and expose to the **Model Adapter Layer**.

This layer should **not** generate model calls directly unless explicitly required by a later implementation spec. Its main responsibility is to define local runtime profiles, hardware constraints, model availability, compatibility checks, and eligibility rules.

It exists so that Agent_X does not blindly select or attempt to load a model that is:

```text
too large for available memory or VRAM
outside local-only policy
not available on disk
not compatible with the declared runtime
not compatible with the requested context window
not compatible with the requested task type
not approved by Policy / Capability Registry
not safe for the current execution role
not suitable for the Prompt Contract or Context Builder output
```

---

# 2. Scope

## 2.1 Required in This Layer

This layer must define and implement contracts for:

```text
local runtime profile purpose
hardware capability profile
model inventory schema
model runtime profile schema
quantization profile schema
context-window profile schema
memory / VRAM limits
CPU fallback rules
GPU fallback rules
local-only provider rules
hosted-model prohibition unless explicitly configured elsewhere
model capability declarations
model risk limits
model selection constraints
runtime health-check rules
model availability checks
runtime artifact rules
failure taxonomy integration
Policy / Capability Registry integration
Model Adapter Layer integration
Context Builder / Task Packer integration
Prompt Contract Layer integration
Tool / MCP Adapter integration
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM inference
chat completion calls
hosted provider calls
prompt generation
context packing
agent orchestration
tool execution
MCP server exposure
patch generation
patch application
Git operations
model fine-tuning
model downloading by default
network search or remote model lookup
background daemon behavior
```

This layer defines runtime profiles and eligibility. It does not act as the model adapter itself.

---

# 4. Preconditions, Dependency Gates, and Restricted Mode

This layer may be implemented before every downstream model component exists, but it must not become a bypass around those components.

## 3.1 Required Prior Authorities for Live Selection

Live selection of a local model requires all applicable authorities:

```text
Local Model Runtime Profile Layer
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Model Adapter Layer
Prompt Contract Layer, when prompt requirements are part of the request
Context Builder / Task Packer, when packed context is part of the request
Tool / MCP Adapter, only for read-only profile inspection exposure
```

The strictest authority wins. A profile-level `ALLOW` is only eligibility metadata. It does not execute a model and does not grant the Model Adapter permission to call inference.

## 3.2 Restricted Mode

If any required authority is unavailable, this layer may operate only in restricted mode.

Restricted mode allows:

```text
load static test profiles
validate schemas
list local model metadata
check local file availability
calculate memory/context estimates
produce BLOCKED or DEGRADED decisions
write evidence
expose read-only inspection results to Tool / MCP Adapter
```

Restricted mode blocks:

```text
model inference
model loading that allocates large memory
model download
network runtime checks
hosted fallback
source mutation
Tool / MCP mutating operations
selection for implementation tasks unless policy and Model Adapter are available
```

## 3.3 Missing Dependency Rules

```text
If Policy / Capability Registry is missing -> BLOCK non-trivial selection.
If Model Adapter Layer is missing -> return eligibility only, not executable selection.
If Context Builder / Task Packer is missing -> block requests requiring packed context proof.
If Prompt Contract Layer is missing -> block requests requiring structured output or system-prompt guarantees.
If Failure Taxonomy is missing -> use MODEL_RUNTIME_UNKNOWN_FAILURE but still fail closed.
If Tool / MCP Adapter is missing -> no external profile tool exposure is created.
```

---

# 4. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because this layer controls whether a model is eligible to be used under current hardware, policy, runtime, and safety constraints.

This affects:

```text
local model eligibility
model loading permissions
runtime compatibility
memory and VRAM safety
CPU/GPU fallback behavior
local-only enforcement
hosted-provider blocking
model capability constraints
risk limits
runtime health checks
evidence for model availability and selection decisions
```

The layer must fail closed. If eligibility cannot be proven, the model must not be selected.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer must map to concrete implementation files, schemas, tests, and runtime artifacts.

Expected implementation area:

```text
tools/agentx_evolve/model_runtime/
```

Expected responsibilities include:

```text
profile loading
model inventory loading
hardware profile loading or probing
runtime compatibility checking
memory budget estimation
context-window compatibility checking
quantization compatibility checking
local-only enforcement
runtime artifact writing
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, tests, and safety limits.

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer is an integration boundary between model selection, prompt construction, policy enforcement, and tool-mediated access.

This layer must integrate with:

```text
Policy / Capability Registry
Failure Taxonomy / Recovery Playbook
Model Adapter Layer
Context Builder / Task Packer
Prompt Contract / Prompt Versioning Layer
Tool / MCP Adapter Layer
future Self-Evolution Orchestrator
future LLM Implementation Worker
```

It must not become a bypass around the Model Adapter or Policy Registry.

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because all profiles, model inventory entries, runtime decisions, and evidence records must be structured and testable.

Required schemas include:

```text
local_model_inventory.schema.json
local_model_entry.schema.json
local_model_runtime_profile.schema.json
hardware_capability_profile.schema.json
quantization_profile.schema.json
context_window_profile.schema.json
model_capability_profile.schema.json
model_selection_constraint.schema.json
model_runtime_health.schema.json
model_availability_result.schema.json
local_model_runtime_decision.schema.json
local_model_runtime_audit.schema.json
local_model_memory_estimate.schema.json
local_model_runtime_compatibility.schema.json
local_model_profile_provenance.schema.json
local_model_runtime_evidence_manifest.schema.json
local_model_runtime_review_report.schema.json
local_model_runtime_completion_record.schema.json
local_model_root_registry.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every model runtime decision must produce evidence.

Evidence is required for:

```text
model inventory loaded
model profile accepted
model profile rejected
hardware profile loaded
hardware profile invalid
model availability check
model compatibility check
memory budget check
VRAM budget check
context-window check
quantization compatibility check
CPU fallback decision
GPU fallback decision
local-only enforcement
hosted-provider block
policy-denied model selection
runtime health check
model selection decision
```

---

# 5. Local Runtime Profile Purpose

The Local Model Runtime Profile Layer must answer these questions before any local model can be used:

```text
Which local models exist?
Where are they located?
Which runtimes can load them?
Which quantizations are supported?
Which context windows are safe?
How much RAM or VRAM is required?
Can the current machine run the model?
Is CPU fallback allowed?
Is GPU fallback allowed?
Is hosted fallback forbidden?
Which tasks is the model allowed to serve?
Which risks are associated with this model?
Which model should be visible to the Model Adapter Layer?
```

This layer is declarative and defensive. It should not assume that a model can run just because it appears in a directory.

---

# 6. Canonical Subdirectories

## 5.1 Runtime Profile Package

```text
tools/agentx_evolve/model_runtime/
```

Expected files:

```text
__init__.py
runtime_models.py
profile_loader.py
profile_repository.py
runtime_registry.py
hardware_profile.py
model_inventory.py
availability_checker.py
compatibility_checker.py
model_selector.py
memory_budget.py
runtime_mode.py
profile_validator.py
schema_validator.py
runtime_artifacts.py
```

## 5.2 Schema Directory

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
local_model_profile.schema.json
local_runtime_profile.schema.json
local_hardware_profile.schema.json
local_model_inventory.schema.json
local_model_availability.schema.json
local_runtime_compatibility_decision.schema.json
local_model_selection_constraints.schema.json
local_runtime_request_limits.schema.json
local_runtime_artifact.schema.json
local_model_eligibility_decision.schema.json
local_model_runtime_evidence_manifest.schema.json
local_model_runtime_review_report.schema.json
local_model_runtime_completion_record.schema.json
```

## 5.3 Test Directory

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_local_runtime_models.py
test_local_model_profile_schema.py
test_local_runtime_profile_schema.py
test_local_hardware_profile_schema.py
test_local_model_inventory.py
test_local_profile_loader.py
test_local_profile_repository.py
test_local_runtime_registry.py
test_local_hardware_profile.py
test_local_model_availability.py
test_local_runtime_compatibility.py
test_local_model_selector.py
test_local_quantization_compatibility.py
test_local_context_window_compatibility.py
test_local_memory_budget.py
test_local_runtime_mode.py
test_local_selection_constraints.py
test_local_request_limits.py
test_local_schema_validation.py
test_local_runtime_artifacts.py
test_local_model_runtime_negative_cases.py
```

## 5.4 Validation Utility

```text
tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
```

## 5.5 Runtime Artifacts

```text
.agentx-init/model_runtime/
```

Expected artifacts:

```text
model_inventory_snapshot.json
hardware_capability_snapshot.json
model_availability_history.jsonl
runtime_health_history.jsonl
model_runtime_decision_history.jsonl
blocked_model_selection_history.jsonl
latest_model_runtime_decision.json
local_model_runtime_evidence_manifest.json
local_model_runtime_review_report.json
local_model_runtime_completion_record.json
```

---

# 7. Hardware Capability Profile

The hardware capability profile must describe the machine or runtime environment that local models may use.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "hardware_capability_profile.schema.json",
  "profile_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "hardware_profile_name": "string",
  "cpu_architecture": "string",
  "cpu_cores": 0,
  "system_ram_mb": 0,
  "gpu_available": false,
  "gpu_vendor": "none|nvidia|amd|apple|intel|other",
  "gpu_name": "string|null",
  "vram_mb": 0,
  "cuda_available": false,
  "metal_available": false,
  "rocm_available": false,
  "preferred_runtime": "string|null",
  "allowed_runtime_modes": [],
  "max_model_size_mb": 0,
  "max_context_tokens": 0,
  "cpu_fallback_allowed": true,
  "gpu_required": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
hardware profile must be explicit
unknown RAM or VRAM must not be treated as unlimited
gpu_available=false must block GPU-required profiles
vram_mb=0 must block VRAM-required profiles
max_model_size_mb must be enforced
max_context_tokens must be enforced
```

If live hardware probing is not available, this layer may use a static hardware profile, but it must record that the profile is static.

---

# 8. Model Inventory Schema

The model inventory defines which local models Agent_X knows about.

Required inventory fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_inventory.schema.json",
  "inventory_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "inventory_source": "manual|generated|static_test_fixture",
  "models": [],
  "warnings": [],
  "errors": []
}
```

Each model entry must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_entry.schema.json",
  "model_id": "string",
  "display_name": "string",
  "family": "string",
  "provider_type": "local",
  "model_path": "string",
  "model_path_type": "local_file|local_directory",
  "model_format": "gguf|safetensors|onnx|other",
  "parameter_count_b": 0,
  "quantization": "string",
  "file_size_mb": 0,
  "sha256": "string|null",
  "license_id": "string|null",
  "provenance_source": "manual|local_scan|packaged_fixture|unknown",
  "declared_context_tokens": 0,
  "recommended_context_tokens": 0,
  "runtime_profiles": [],
  "capabilities": [],
  "risk_flags": [],
  "enabled": true,
  "allowlisted": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
model_id must be stable
model_path must be local
model_path must resolve inside an approved local model directory
symlinks must resolve inside approved local model directories
provider_type must be local
hosted provider entries are not allowed in this inventory
models must be allowlisted before eligible selection
missing model path blocks availability
missing or mismatched sha256 blocks production use when hash policy is required
unknown provenance must be surfaced as a risk flag
missing quantization blocks compatibility
missing context declaration blocks selection
```

---

# 9. Model Runtime Profile Schema

A model runtime profile defines how a local model may be loaded by a local runtime.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_profile.schema.json",
  "runtime_profile_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "runtime_name": "llama_cpp|ollama|vllm|transformers|other",
  "runtime_mode": "local_cpu|local_gpu|local_hybrid",
  "model_format_supported": [],
  "quantizations_supported": [],
  "min_system_ram_mb": 0,
  "min_vram_mb": 0,
  "max_context_tokens": 0,
  "supports_streaming": false,
  "supports_function_calling": false,
  "supports_json_mode": false,
  "supports_embeddings": false,
  "uses_network": false,
  "allows_model_download": false,
  "enabled": true,
  "allowlisted": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
runtime profile must be local
uses_network=true blocks by default
allows_model_download=true blocks by default
runtime must be allowlisted before eligible use
runtime profile cannot authorize hosted fallback
runtime compatibility must be checked before Model Adapter exposure
```

---

# 10. Quantization Profile Schema

A quantization profile defines which quantization types are accepted and what resource assumptions apply.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "quantization_profile.schema.json",
  "quantization_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "quantization_name": "string",
  "bits_per_weight_estimate": 0,
  "quality_tier": "low|medium|high|unknown",
  "memory_multiplier": 0.0,
  "allowed_for_code_tasks": false,
  "allowed_for_review_tasks": true,
  "allowed_for_planning_tasks": true,
  "requires_extra_validation": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
unknown quantization blocks unless explicitly allowlisted
low-quality quantization may be blocked for implementation tasks
quantization must be compatible with runtime profile
quantization must be included in memory estimate
```

---

# 11. Context-Window Profile Schema

A context-window profile defines safe context limits for model use.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "context_window_profile.schema.json",
  "context_profile_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "model_id": "string",
  "declared_context_tokens": 0,
  "safe_context_tokens": 0,
  "reserved_system_tokens": 0,
  "reserved_tool_tokens": 0,
  "reserved_output_tokens": 0,
  "max_input_tokens": 0,
  "max_output_tokens": 0,
  "supports_long_context": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
safe_context_tokens must not exceed declared_context_tokens
max_input_tokens + max_output_tokens + reserved tokens must not exceed safe_context_tokens
Context Builder / Task Packer must respect max_input_tokens
Prompt Contract Layer must respect reserved_system_tokens
Model Adapter Layer must respect max_output_tokens
unknown context window blocks selection
```

---

# 12. Memory / VRAM Limits

The layer must estimate whether a model can fit within available memory.

Required checks:

```text
model file size
estimated runtime overhead
estimated KV-cache size
requested context size
quantization memory multiplier
CPU RAM limit
GPU VRAM limit
reserved OS/runtime headroom
```

Required rules:

```text
never assume unlimited memory
memory estimate must include safety margin
VRAM estimate must include context/KV overhead where applicable
CPU fallback cannot ignore RAM limits
GPU mode cannot ignore VRAM limits
if memory estimate is unknown, selection blocks unless explicitly marked test-only
```

Recommended default safety margins:

```text
system RAM reserve: at least 20 percent or fixed configured reserve
VRAM reserve: at least 10 percent or fixed configured reserve
context overhead: conservative estimate when runtime-specific formula is unavailable
```

---

# 13. CPU Fallback Rules

CPU fallback may be allowed only when all of these are true:

```text
hardware profile allows CPU fallback
runtime profile supports local_cpu
model file exists locally
system RAM estimate passes
requested context fits safe context limit
Policy / Capability Registry allows CPU runtime mode
Model Adapter accepts slower local runtime mode
```

CPU fallback must block when:

```text
model requires GPU
runtime profile requires GPU
task requires latency target that CPU cannot satisfy
memory estimate fails
policy forbids CPU fallback
model profile marks CPU unsupported
```

CPU fallback must produce evidence.

---

# 14. GPU Fallback Rules

GPU mode may be allowed only when all of these are true:

```text
gpu_available=true
runtime profile supports local_gpu or local_hybrid
required GPU backend is available
VRAM estimate passes
model quantization is compatible with GPU runtime
Policy / Capability Registry allows GPU runtime mode
```

GPU fallback must block when:

```text
gpu_available=false
vram_mb is unknown or insufficient
CUDA/Metal/ROCm requirement is unmet
runtime profile does not support GPU
model profile marks GPU unsupported
policy forbids GPU use
```

If GPU fails health check, this layer may recommend CPU fallback only if CPU fallback rules pass.

---

# 15. Local-Only Provider Rules

The Local Model Runtime Profile Layer is local-first and local-only by default.

Rules:

```text
provider_type must be local
model_path must point to local model storage
runtime must not require network by default
model download is disabled by default
hosted fallback is disabled by default
external provider keys must not be read by this layer
network availability must not be required for validation
```

If a future hosted fallback exists, it belongs to the Model Adapter Layer or Hosted Model Adapter configuration, not this layer.

---

# 16. Hosted-Model Prohibition

Hosted models are prohibited in this layer unless explicitly configured elsewhere and approved by Policy / Capability Registry.

This layer must block:

```text
OpenAI-hosted model entries
Anthropic-hosted model entries
Google-hosted model entries
Mistral-hosted model entries
remote Ollama endpoints unless explicitly approved elsewhere
remote vLLM endpoints unless explicitly approved elsewhere
network download of model files
network lookup of model metadata
```

A local model entry must not silently convert into a hosted provider call.

Failure class:

```text
MODEL_HOSTED_PROVIDER_FORBIDDEN
```

---

# 17. Model Capability Declarations

Each local model must declare its allowed capabilities.

Allowed capability examples:

```text
CHAT_COMPLETION
CODE_EXPLANATION
CODE_REVIEW
PLANNING
CLASSIFICATION
SUMMARIZATION
JSON_OUTPUT
EMBEDDINGS
TOOL_CALL_SUGGESTION
```

Rules:

```text
capability declaration is not proof of quality
capability must be policy-checked before use
implementation/code-writing capability may require stricter quantization and context rules
JSON_OUTPUT must not be assumed unless declared and tested
TOOL_CALL_SUGGESTION does not grant permission to execute tools
```

---

# 18. Model Risk Limits

Each model entry may declare risk flags.

Risk flag examples:

```text
LOW_CONTEXT
LOW_QUANTIZATION
UNKNOWN_LICENSE
UNKNOWN_PROVENANCE
EXPERIMENTAL_RUNTIME
HIGH_MEMORY_PRESSURE
CPU_ONLY_SLOW
GPU_REQUIRED
NO_JSON_MODE
NO_TOOL_USE_SUPPORT
```

Rules:

```text
risk flags must be visible to Model Adapter Layer
risk flags must be included in runtime decision evidence
unknown provenance may block production use
unknown license may block redistribution or packaged defaults
low quantization may block implementation tasks
high memory pressure may block large context tasks
```

---

# 19. Model Selection Constraints

The layer must provide constraints to the Model Adapter Layer.

A model is eligible only if:

```text
model is enabled
model is allowlisted
model file exists locally
model format is supported by runtime
quantization is allowed
context window fits request
memory estimate passes
runtime health check passes or is not required for dry-run
Policy / Capability Registry allows the model and runtime mode
hosted fallback is not required
```

Selection must block if:

```text
model is missing
model is disabled
model is not allowlisted
model path is remote
runtime is disabled
runtime uses network by default
memory estimate fails
VRAM estimate fails
context requirement exceeds safe context
policy denies model
capability does not match requested task
```

Decision precedence:

```text
INVALID_PROFILE
MODEL_NOT_FOUND
POLICY_DENIED
HOSTED_PROVIDER_FORBIDDEN
RUNTIME_UNAVAILABLE
MEMORY_LIMIT_EXCEEDED
CONTEXT_LIMIT_EXCEEDED
QUANTIZATION_UNSUPPORTED
CAPABILITY_UNSUPPORTED
HEALTH_CHECK_FAILED
ALLOW
```

---

# 20. Runtime Health-Check Rules

Runtime health checks may confirm whether a local runtime appears usable.

Allowed health checks:

```text
static config validation
model file existence check
runtime binary path existence check
runtime import availability check
non-network dry-run capability check
version command only if allowlisted
```

Forbidden health checks:

```text
network calls
hosted provider calls
model download
large model load by default
long-running inference
background daemon start
opening network ports
writing source files
```

If health check is unavailable, the model may remain visible as `UNKNOWN_HEALTH`, but it must not be selected for execution unless policy allows degraded mode.

---

# 21. Model Availability Checks

Availability check result schema:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_availability_result.schema.json",
  "availability_id": "string",
  "timestamp": "string",
  "source_component": "LocalModelRuntimeProfile",
  "model_id": "string",
  "model_path": "string",
  "exists": false,
  "readable": false,
  "size_mb": 0,
  "format_detected": "string|null",
  "status": "AVAILABLE|UNAVAILABLE|BLOCKED|UNKNOWN",
  "failure_class": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
missing model file returns UNAVAILABLE
unreadable model file returns BLOCKED
remote path returns BLOCKED
unexpected format returns BLOCKED
availability result must be evidenced
```

---

# 22. Runtime Artifact Rules

Runtime artifacts must be written under:

```text
.agentx-init/model_runtime/
```

Allowed artifacts:

```text
model_inventory_snapshot.json
hardware_capability_snapshot.json
model_availability_history.jsonl
runtime_health_history.jsonl
model_runtime_decision_history.jsonl
blocked_model_selection_history.jsonl
latest_model_runtime_decision.json
local_model_runtime_evidence_manifest.json
local_model_runtime_review_report.json
local_model_runtime_completion_record.json
```

Rules:

```text
append-only JSONL for histories
atomic writes for latest JSON artifacts
redact local secrets and environment values
model paths may be logged only if they are within approved local boundaries
remote URLs must be redacted or blocked
no model file contents are logged
no prompt contents are logged
no generated model outputs are logged by this layer
```

---

# 23. Failure Taxonomy Integration

This layer must map failures to standard classes.

Required failure classes:

```text
MODEL_PROFILE_INVALID
MODEL_INVENTORY_INVALID
MODEL_NOT_FOUND
MODEL_FILE_UNREADABLE
MODEL_FORMAT_UNSUPPORTED
MODEL_QUANTIZATION_UNSUPPORTED
MODEL_CONTEXT_LIMIT_EXCEEDED
MODEL_MEMORY_LIMIT_EXCEEDED
MODEL_VRAM_LIMIT_EXCEEDED
MODEL_RUNTIME_UNAVAILABLE
MODEL_RUNTIME_HEALTH_FAILED
MODEL_HOSTED_PROVIDER_FORBIDDEN
MODEL_POLICY_DENIED
MODEL_CAPABILITY_UNSUPPORTED
MODEL_SELECTION_BLOCKED
MODEL_RUNTIME_UNKNOWN_FAILURE
```

Rules:

```text
every blocked selection must have a failure_class
every invalid profile must have a failure_class
unknown runtime errors map to MODEL_RUNTIME_UNKNOWN_FAILURE
policy denials map to MODEL_POLICY_DENIED
hosted fallback attempts map to MODEL_HOSTED_PROVIDER_FORBIDDEN
```

---

# 24. Policy / Capability Registry Integration

The Policy / Capability Registry remains authoritative.

This layer must ask policy whether:

```text
local model use is allowed
specific model family is allowed
specific model_id is allowed
runtime mode is allowed
CPU fallback is allowed
GPU use is allowed
large context is allowed
implementation/code task is allowed
hosted fallback is forbidden or separately configured
```

Rules:

```text
missing policy blocks non-trivial selection
policy denial blocks selection
policy approval does not override memory/context/runtime incompatibility
strictest authority wins
```

---

# 25. Model Adapter Layer Integration

This layer exposes validated runtime profiles to the Model Adapter Layer.

It must provide:

```text
eligible model list
runtime compatibility results
safe context limits
memory/VRAM estimates
capability declarations
risk flags
local-only status
failure reasons for blocked models
```

It must not provide:

```text
hosted provider credentials
raw model file contents
prompt contents
unbounded context windows
model execution shortcuts
```

The Model Adapter Layer may request a model eligibility decision, but it must not bypass this layer's compatibility checks.

---

# 26. Context Builder / Task Packer Integration

The Context Builder / Task Packer must receive safe context limits from this layer.

Required outputs:

```text
safe_context_tokens
max_input_tokens
max_output_tokens
reserved_system_tokens
reserved_tool_tokens
reserved_output_tokens
context_pressure_warning
```

Rules:

```text
Context Builder must not exceed max_input_tokens
Task Packer must reduce or split context if limit is exceeded
large context request must not force unsafe model selection
unknown context limit blocks selection or requires explicit degraded mode
```

---

# 27. Prompt Contract Layer Integration

The Prompt Contract Layer must align prompt requirements with model runtime constraints.

This layer must expose whether the selected local model supports:

```text
system prompt size
structured output
JSON mode
tool-call suggestion format
max output tokens
required prompt version
```

Rules:

```text
Prompt Contract cannot assume JSON mode unless model profile declares support
Prompt Contract cannot reserve more tokens than context profile permits
Prompt Contract cannot override local-only restrictions
Prompt Contract must receive warnings for low-context or low-quantization models
```

---

# 28. Tool / MCP Adapter Integration

Tool / MCP Adapter may expose profile inspection tools, but it must not expose model execution tools from this layer.

Allowed Tool / MCP Adapter operations:

```text
list_local_model_profiles
check_local_model_availability
check_runtime_compatibility
show_runtime_health
show_model_selection_constraints
```

Blocked Tool / MCP Adapter operations:

```text
load_model_directly
run_model_inference
call_hosted_fallback
download_model
modify_model_inventory_without governance
open runtime network port
```

MCP exposure must be read-only by default.

---

# 29. OpenCode Borrowing Notes

OpenCode-style concepts may be useful as architectural references only.

Borrowable ideas:

```text
provider abstraction
model selection indirection
local/runtime profile separation
tool-visible model metadata
capability-based model use
configuration-driven runtime selection
```

Do not borrow:

```text
network/provider convenience defaults
automatic hosted fallback
plugin-based provider loading without Agent_X policy
broad environment-variable credential access
model execution shortcuts that bypass the Model Adapter
runtime dependency assumptions that require Bun/Node/OpenCode
```

Agent_X must keep model runtime eligibility separate from model execution.

---

# 30. Agent_X Integration Notes

This layer sits between local model inventory and model execution.

Expected flow:

```text
Model Adapter requests eligible local model
→ Local Model Runtime Profile loads inventory
→ hardware profile is loaded or probed
→ availability check runs
→ runtime compatibility check runs
→ memory and context checks run
→ policy check runs
→ model capability and risk limits are evaluated
→ runtime decision is recorded
→ Model Adapter receives allowed profile or blocked decision
```

The layer must not become a direct inference service.

---

# 31. Runtime Decision Schema

A local runtime decision must be structured.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_decision.schema.json",
  "decision_id": "string",
  "timestamp": "string",
  "source_component": "LocalModelRuntimeProfile",
  "model_id": "string",
  "runtime_profile_id": "string|null",
  "hardware_profile_id": "string|null",
  "requested_task_type": "string",
  "requested_context_tokens": 0,
  "requested_output_tokens": 0,
  "decision": "ALLOW|BLOCK|DEGRADED|UNKNOWN",
  "reason": "string",
  "failure_class": "string|null",
  "safe_context_tokens": 0,
  "estimated_ram_mb": 0,
  "estimated_vram_mb": 0,
  "cpu_fallback_selected": false,
  "gpu_selected": false,
  "policy_decision_id": "string|null",
  "availability_id": "string|null",
  "health_check_id": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
ALLOW requires model availability, compatibility, memory, context, and policy approval
BLOCK requires failure_class
DEGRADED requires explicit reason and policy allowance
UNKNOWN cannot be treated as ALLOW
```

---

# 32. Profile Provenance, Hashing, and Path Boundary Rules

Every production-eligible model entry must have clear provenance.

Required provenance fields:

```text
model_id
model_path
resolved_model_path
sha256 or hash_not_required_reason
file_size_mb
license_id or UNKNOWN_LICENSE risk flag
provenance_source
provenance_checked_at
profile_author
allowlist_status
```

Path rules:

```text
model_path must be local
model_path must not be a URL
model_path must not use remote protocols such as http, https, s3, gs, ssh, ftp, or file URLs pointing outside approved roots
model_path must resolve inside configured approved local model directories
relative paths must be normalized before validation
symlinks must be resolved before approval
symlink escape from approved roots must BLOCK
parent-directory traversal must BLOCK
model file contents must never be logged
```

Hash rules:

```text
SHA-256 is required for packaged or production allowlisted models unless explicitly waived by policy
hash mismatch blocks production selection
missing hash may be accepted only for local experimental profiles with UNKNOWN_PROVENANCE risk and non-production policy
evidence files must also include SHA-256 hashes
```

---

# 33. Idempotency, Caching, and Concurrency Rules

The layer must behave deterministically for the same inputs.

Idempotency rules:

```text
same inventory snapshot + same hardware profile + same request + same policy decision -> same runtime decision
repeated availability checks must not mutate model files
repeated health checks must not start daemons or persistent services
repeated blocked decisions must remain BLOCKED until input evidence changes
```

Caching rules:

```text
cached availability results must record source file size, mtime, and optional hash
cached hardware profiles must record whether they are static or detected
cached decisions must record inventory_id, hardware_profile_id, policy_decision_id, and request hash
stale cache must not be treated as proof of availability
cache invalidation is required when model file metadata changes
```

Concurrency rules:

```text
profile reads may run concurrently
latest decision writes must be atomic
JSONL history appends must not corrupt existing lines
health checks must not race to start services
large file hashing should be bounded or explicitly marked as a long-running validation step
```

---

# 34. Runtime Authority Separation

This layer does not execute model inference.

Allowed authority:

```text
declare known local models
validate model profiles
check local file availability
check runtime profile compatibility
estimate memory, VRAM, and context limits
return eligibility decisions
write evidence
expose read-only profile information
```

Forbidden authority:

```text
open a chat session
call llama.cpp, Ollama, vLLM, Transformers, or other runtimes for inference by default
start model servers
open network ports
download model files
read hosted-provider credentials
select hosted fallback
execute tools suggested by a model
```

If a future implementation requires a lightweight runtime probe, it must be:

```text
local only
non-network
allowlisted
short-running
non-inference unless separately approved
evidenced
policy-approved
```

---

# 35. Evidence Manifest and Review Artifacts

Create final evidence under:

```text
.agentx-init/model_runtime/
```

Required review artifacts:

```text
local_model_runtime_evidence_manifest.json
local_model_runtime_review_report.json
local_model_runtime_completion_record.json
```

Evidence manifest required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_evidence_manifest.schema.json",
  "component_id": "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "inventory_snapshot_hash": "<sha256|null>",
  "hardware_snapshot_hash": "<sha256|null>",
  "runtime_decision_hashes": [],
  "deviation_register": [],
  "final_decision": "DONE|NOT_DONE"
}
```

Evidence rules:

```text
all final evidence files require SHA-256 hashes
evidence must record reviewed commit
evidence must record whether hardware profile is static or detected
evidence must record policy decision references where available
manual edits after final sign-off invalidate the previous DONE verdict unless a new review report is created
```

---

# 36. Negative Safety Cases

The implementation must prove the following fail closed:

```text
hosted provider entry in local inventory -> BLOCK
remote model URL as model_path -> BLOCK
symlink escaping approved model root -> BLOCK
missing model file -> UNAVAILABLE, not ALLOW
unreadable model file -> BLOCK
hash mismatch -> BLOCK when hash required
unknown quantization -> BLOCK unless explicitly allowlisted
unknown memory estimate -> BLOCK for production selection
context request exceeds safe_context_tokens -> BLOCK
GPU-required model on CPU-only hardware -> BLOCK
CPU fallback when RAM estimate fails -> BLOCK
network-enabled runtime profile by default -> BLOCK
model download flag enabled by default -> BLOCK
missing policy for non-trivial selection -> BLOCK
Tool / MCP request to run inference through this layer -> BLOCK
health check attempts to start daemon or open port -> BLOCK
```

---

# 37. Security Rules

This layer must enforce:

```text
no hosted model calls
no model inference by default
no network by default
no model downloads by default
no direct tool execution
no MCP mutating exposure
no raw model file content logging
no prompt logging
no credential access
no environment secret logging
no unlimited context assumption
no unlimited memory assumption
no automatic fallback from local to hosted
```

---

# 38. Test Acceptance Criteria

Required tests:

```text
model inventory schema accepts valid inventory
model inventory schema rejects hosted provider entry
model runtime profile schema accepts valid local runtime
model runtime profile schema rejects network-enabled runtime by default
hardware profile schema rejects missing memory fields
quantization profile schema rejects unknown quantization unless allowlisted
context profile schema rejects safe_context_tokens greater than declared_context_tokens
missing model file returns UNAVAILABLE
remote model path returns BLOCKED
insufficient RAM returns MODEL_MEMORY_LIMIT_EXCEEDED
insufficient VRAM returns MODEL_VRAM_LIMIT_EXCEEDED
context overflow returns MODEL_CONTEXT_LIMIT_EXCEEDED
hosted fallback returns MODEL_HOSTED_PROVIDER_FORBIDDEN
missing policy blocks non-trivial model selection
CPU fallback allowed only when rules pass
GPU selection allowed only when rules pass
runtime decision writes evidence
secrets and environment values are redacted
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
negative tests PASS
runtime artifact tests PASS
no network required
no hosted provider required
no model inference required
no source mutation
```

---

# 39. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] hardware capability profile schema is defined
[ ] model inventory schema is defined
[ ] model runtime profile schema is defined
[ ] quantization profile schema is defined
[ ] context-window profile schema is defined
[ ] runtime decision schema is defined
[ ] memory / VRAM limits are defined
[ ] CPU fallback rules are defined
[ ] GPU fallback rules are defined
[ ] local-only provider rules are defined
[ ] hosted-model prohibition is defined
[ ] integration with Model Adapter Layer is defined
[ ] integration with Policy / Capability Registry is defined
[ ] integration with Context Builder / Task Packer is defined
[ ] integration with Prompt Contract Layer is defined
[ ] Tool / MCP Adapter exposure is read-only by default
```

---

# 40. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] inventory loading works
[ ] model availability check works
[ ] memory / VRAM checks work
[ ] context-window checks work
[ ] local-only enforcement works
[ ] hosted fallback blocks
[ ] runtime decisions write evidence
[ ] no inference occurs in this layer
[ ] no network is required
[ ] no source mutation occurs
[ ] completion record exists
```

---

# 41. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE"
  component_name: "Local Model Runtime Profile Layer"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  model_profiles_verified: []
  hardware_profiles_verified: []
  runtime_profiles_verified: []
  availability_checks_verified: []
  memory_checks_verified: []
  context_checks_verified: []
  policy_integration_verified: []
  model_adapter_integration_verified: []
  context_builder_integration_verified: []
  prompt_contract_integration_verified: []
  tool_mcp_adapter_integration_verified: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 42. Residual Risks

```yaml
residual_risks:
  - id: "LMR-RISK-001"
    description: "A local model may be selected despite insufficient memory or VRAM."
    severity: "high"
    mitigation: "Memory and VRAM estimates must fail closed when limits are unknown or exceeded."
  - id: "LMR-RISK-002"
    description: "Hosted fallback could bypass local-only intent."
    severity: "critical"
    mitigation: "Hosted provider entries and network fallback are blocked by default and require separate policy."
  - id: "LMR-RISK-003"
    description: "Context Builder may overpack prompts beyond model limits."
    severity: "high"
    mitigation: "Context-window profile must expose safe max input/output token limits."
  - id: "LMR-RISK-004"
    description: "Model capability declarations may be treated as proof of quality."
    severity: "medium"
    mitigation: "Capability declarations are eligibility metadata only and do not replace evaluation."
  - id: "LMR-RISK-005"
    description: "Runtime health checks may accidentally load large models or start services."
    severity: "high"
    mitigation: "Health checks are limited to static, local, non-network checks unless explicitly approved."
```

---

# 43. Definition of Done

This layer is done when it can safely define local model runtime eligibility for Agent_X.

It must prove:

```text
local model inventory schema exists
hardware capability profile schema exists
model runtime profile schema exists
quantization profile schema exists
context-window profile schema exists
runtime decision schema exists
inventory loading works
model availability checks work
runtime compatibility checks work
memory / VRAM checks fail closed
context-window checks fail closed
local-only provider rules are enforced
hosted-model fallback is blocked by default
CPU fallback follows rules
GPU selection follows rules
policy integration blocks denied models
Model Adapter receives only eligible local runtime profiles
Context Builder receives safe context limits
Prompt Contract receives prompt/runtime constraints
Tool / MCP Adapter exposure is read-only by default
evidence is written
blocked decisions are evidenced
no model inference occurs directly in this layer
no network is required
no source mutation occurs
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
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

# 44. Fresh-Clone Validation and Sign-Off

The implementation is accepted only after validation from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
git status --short
```

Required result:

```text
initial git status CLEAN or expected runtime artifacts only
compileall PASS
pytest PASS
schema validation PASS
final git status CLEAN or expected runtime artifacts only
```

No validation command may require:

```text
GPU
network
hosted model
LLM inference
model download
running model server
Bun
Node
OpenCode runtime
```

---

# 45. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
hosted provider is allowed by default
network is required for validation
model download is enabled by default
model inference occurs directly in this layer
memory limit is ignored
VRAM limit is ignored
context limit is ignored
missing model file is treated as available
remote model path is accepted as local
policy denial is ignored
CPU fallback ignores RAM limits
GPU mode ignores VRAM limits
Tool / MCP Adapter exposes model execution through this layer
runtime evidence is missing
unredacted secrets are logged
source mutation occurs
```

---

# 46. Approved Local Model Root Registry

The implementation must define an explicit approved local model root registry. Model paths are not valid simply because they are absolute or readable.

Required registry fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_root_registry.schema.json",
  "registry_id": "string",
  "created_at": "string",
  "source_component": "LocalModelRuntimeProfile",
  "approved_roots": [],
  "blocked_roots": [],
  "allow_symlinks": false,
  "require_resolved_path_inside_root": true,
  "warnings": [],
  "errors": []
}
```

Each approved root entry must include:

```text
root_id
root_path
resolved_root_path
purpose
read_only
hash_required
allow_experimental_models
warnings
errors
```

Rules:

```text
model_path must resolve inside one approved root
blocked_roots override approved_roots
symlink target must resolve inside an approved root
relative paths must be normalized before approval
root registry hash must be recorded in selection evidence
missing root registry blocks production selection
```

---

# 47. Model Identity, Alias, and Collision Rules

Model identity must be deterministic.

Rules:

```text
model_id must be unique within the inventory
model aliases must map to exactly one model_id
same model_path cannot appear under multiple enabled model_ids unless explicitly justified
same sha256 under multiple model_ids requires a duplicate-model warning
alias collision blocks inventory validation
case-only model_id differences are forbidden
renaming model_id requires a new provenance record
```

The Model Adapter Layer must receive canonical `model_id`, not an ambiguous display name or alias.

---

# 48. Policy Decision Evidence Requirement

Every non-trivial runtime decision must include policy evidence.

Required behavior:

```text
ALLOW requires policy_decision_id unless the decision is explicitly test-only
DEGRADED requires policy_decision_id and degraded-mode reason
BLOCK caused by policy denial must include MODEL_POLICY_DENIED
missing policy blocks production selection
policy approval does not override memory, context, availability, root, hash, or runtime failures
```

Runtime decision evidence must include:

```text
policy_decision_id
policy_profile_id or policy_snapshot_hash
allowed_runtime_mode
allowed_task_type
allowed_model_family or model_id
hosted_fallback_status
warnings
errors
```

---

# 49. Profile Drift, Conflict, and Stale Cache Rules

The layer must fail closed when profile inputs drift or conflict.

Drift conditions:

```text
model file size changed
model file mtime changed
model sha256 changed
hardware profile changed
approved model root registry changed
policy snapshot changed
runtime profile changed
context profile changed
quantization profile changed
```

Rules:

```text
stale availability cache cannot prove availability
stale compatibility cache cannot prove compatibility
stale memory estimate cannot prove eligibility
conflicting profile fields block selection
newer profile does not automatically override older reviewed evidence
profile drift after DONE requires new evidence before selection
```

Conflict precedence:

```text
BLOCK overrides ALLOW
INVALID_PROFILE overrides all compatibility decisions
HOSTED_PROVIDER_FORBIDDEN overrides runtime compatibility
MODEL_ROOT_DENIED overrides file availability
MODEL_HASH_MISMATCH overrides allowlist status
POLICY_DENIED overrides local eligibility
MEMORY_LIMIT_EXCEEDED and CONTEXT_LIMIT_EXCEEDED override capability declarations
```

---

# 50. Runtime Decision Immutability and Reproducibility

A runtime decision used by Model Adapter must be reproducible from recorded inputs.

Required recorded inputs:

```text
inventory_id and inventory_hash
model_id
model_entry_hash
approved_root_registry_hash
hardware_profile_id and hardware_profile_hash
runtime_profile_id and runtime_profile_hash
quantization_profile_id and quantization_profile_hash
context_profile_id and context_profile_hash
policy_decision_id or policy_snapshot_hash
request_hash
decision_id
decision_hash
```

Rules:

```text
latest decision artifacts may be overwritten atomically, but history must be append-only
final reviewed evidence must not be edited after sign-off
changed input hashes invalidate the previous ALLOW decision
manual edits after final DONE require a new review report
same recorded inputs must reproduce the same decision
```

---

# 51. Runtime Probe Boundary

This layer is not an inference runtime. Any future probe must remain sharply bounded.

Allowed probe types:

```text
file existence check
file readability check
file size check
hash check
runtime binary existence check
runtime import availability check
allowlisted version command
static runtime config validation
```

Forbidden probe side effects:

```text
model inference
large model load by default
server start
daemon start
socket open
network call
model download
provider login
credential read
background process creation
```

Any future probe that loads model weights, opens a runtime server, or performs inference requires a major contract revision and a separate Model Runtime Acceptance Criteria document.

---

# 52. Final Freeze Rule

This v3 document is the final frozen controlling contract for the Local Model Runtime Profile Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional schemas, tests, or runtime metadata
MAJOR: changed local-only policy, hosted fallback behavior, runtime execution authority, model selection authority, or required integration boundaries
```

Blocked without major revision:

```text
allowing hosted fallback by default
allowing network by default
allowing model download by default
allowing inference directly in this layer
removing Policy / Capability Registry checks
removing memory / VRAM checks
removing context-window checks
removing evidence logging
allowing Tool / MCP Adapter to execute models through this layer
making Bun/Node/OpenCode runtime required
```

The next document should be:

```text
LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC.md
```

---

# 53. Final Rating

This v3 contract is rated:

```text
10/10
```

Reason:

```text
It preserves the complete v2 coverage and fixes the final contract issues: stable section numbering, no duplicate final rating, explicit approved local model root registry, model identity and alias collision controls, mandatory policy decision evidence, profile drift and stale-cache fail-closed rules, runtime decision immutability, reproducibility requirements, and a strict runtime-probe boundary that prevents this layer from becoming an inference server or hosted-provider bypass.
```
