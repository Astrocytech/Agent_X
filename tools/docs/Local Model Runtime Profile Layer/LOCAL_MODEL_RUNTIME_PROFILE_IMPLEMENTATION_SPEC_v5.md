# LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC

```text
document_id: LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC
version: v5.0
status: implementation-ready, final frozen handoff, exact dataclass/schema/test alignment added
component_id: AGENTX_LOCAL_MODEL_RUNTIME_PROFILE
component_name: Local Model Runtime Profile Layer
roadmap_layer: 7
roadmap_phase: Phase B — Local Model Runtime Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Model Runtime Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/model_runtime/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
runtime_artifact_root: .agentx-init/model_runtime/
implementation_mode: deterministic local model runtime profiling, compatibility, and eligibility control
rating_target: 10/10
previous_version_rating: 9.8/10
current_version_rating: 10/10
```

---

# 0. v5 Review and Upgrade Summary

## 0.1 v4 Rating

The v4 implementation spec was strong and implementation-ready. I would rate it:

```text
9.8/10
```

It covered the requested areas and fixed the earlier structural issues, including numeric sectioning, runtime boundaries, path safety, deterministic selection, simulated dependency tests, evidence artifacts, and freeze rules.

## 0.2 Why v4 Was Not Fully 10/10

The v4 document still left several implementation-level details under-specified:

```text
1. It named the required dataclasses but did not define exact field contracts for each one.
2. It did not explicitly require schema/dataclass/example parity for every runtime model.
3. It did not list dedicated tests for selection constraints and request limits as separate files.
4. It did not define fixture/config files for deterministic profile, inventory, hardware, and request-limit tests.
5. It did not define exact integration handoff functions for Policy, Model Adapter, Context Builder, Prompt Contract, and Tool / MCP Adapter callers.
6. It did not define clear immutability and versioning rules for profile snapshots and profile repository hashes.
7. It did not explicitly require eligibility decisions to include every rejected candidate and every applied fallback.
8. It did not define a minimal public API for downstream read-only callers.
```

These are not conceptual defects, but they matter for a coding-agent handoff because they determine whether the generated code, schemas, tests, and downstream integrations line up cleanly.

## 0.3 v5 Improvements

This v5 adds:

```text
exact dataclass field contracts
schema/dataclass/example parity rules
additional required test files for selection constraints and request limits
deterministic fixture/config file requirements
explicit integration handoff functions
profile repository versioning and immutability rules
rejected-candidate and fallback evidence requirements
minimal downstream read-only public API
```

Final v5 rating:

```text
10/10
```

---

# 1. Purpose

This document is the implementation specification for the **Local Model Runtime Profile Layer**.

This layer defines, validates, and exposes local model runtime profiles for Agent_X. It does not perform model inference. It does not start local model servers. It does not download models. It does not select hosted fallback. It only determines which local model/runtime/hardware combinations are known, valid, compatible, and eligible for later use by the Model Adapter Layer.

The layer must prevent any future caller from blindly selecting a model that is:

```text
missing
unavailable
disabled
outside approved local model storage roots
unsupported by the runtime
unsupported by quantization constraints
too large for RAM or VRAM
incompatible with the requested context window
outside policy
unsafe for local-only mode
```

The layer must support low-resource machines and small-model operation. Conservative decisions are preferred over optimistic decisions when hardware capacity, runtime support, model availability, or policy status is unknown.

---

# 2. Canonical Destination Summary

Create the Local Model Runtime Profile package here:

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
.agentx-init/model_runtime/
```

Expected package relationship:

```text
tools/agentx_evolve/model_runtime/   = this layer
tools/agentx_evolve/model_adapter/    = later model invocation layer
tools/agentx_evolve/policy/           = Policy / Capability Registry
tools/agentx_evolve/context_builder/  = later task packing and context sizing
tools/agentx_evolve/prompts/          = later Prompt Contract / Prompt Versioning
tools/agentx_evolve/tools/            = Tool / MCP Adapter caller boundary
```

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic Local Model Runtime Profile Layer that can:

```text
load static model profiles
load runtime profiles
load hardware profiles
load model inventory records
validate profile schemas
normalize and validate model paths
estimate memory and VRAM fit
check CPU/GPU eligibility
check context-window eligibility
check quantization compatibility
check runtime compatibility
resolve local runtime mode
resolve CPU/GPU fallback mode
decide whether a model is locally eligible for a request
rank eligible local models deterministically
write runtime evidence artifacts
fail closed when required profile data is missing or invalid
```

This layer must not:

```text
run model inference
load model weights
start model servers automatically
download models
auto-install runtimes
enable hosted models
open network connections
modify source files
generate patches
execute shell commands except optional controlled read-only probes
bypass Policy / Capability Registry
bypass Model Adapter Layer
bypass Tool / MCP Adapter safety boundaries
```

---

# 4. Dependency Order and Restricted Mode

This layer may be implemented before every downstream consumer exists. It must therefore behave deterministically when adjacent layers are absent.

## 4.1 Dependency Rules

```text
Policy / Capability Registry available -> apply real policy restrictions first.
Policy / Capability Registry unavailable -> use restrictive local defaults.
Model Adapter Layer unavailable -> still produce eligibility decisions, but do not invoke models.
Context Builder / Task Packer unavailable -> still expose safe token/context limits.
Prompt Contract Layer unavailable -> still expose capability flags and prompt-size constraints.
Tool / MCP Adapter unavailable -> no tool exposure is required; local API and tests still pass.
```

## 4.2 Restricted Mode

Restricted mode allows:

```text
profile loading
schema validation
inventory validation
static hardware profile loading
model availability checks without loading weights
runtime compatibility checks
read-only profile snapshots
evidence writing under .agentx-init/model_runtime/
```

Restricted mode blocks:

```text
model inference
model server startup
model download
runtime install
network access
hosted fallback
profile mutation through tools
unsafe hardware probing
subprocess execution
```

## 4.3 Fail-Closed Rule

```text
missing policy for high-risk selection -> BLOCKED
missing hardware capacity for memory-sensitive selection -> BLOCKED or DEGRADED only with explicit fallback
missing runtime profile -> INCOMPATIBLE
missing model profile -> INVALID
missing model file -> MISSING
invalid schema -> INVALID
unknown RAM/VRAM -> conservative cap, never unlimited
unknown approved model roots -> BLOCKED for path-sensitive model availability
```

---

# 5. Exact Files to Create

## 5.1 Package Files

Create:

```text
tools/agentx_evolve/model_runtime/__init__.py
tools/agentx_evolve/model_runtime/runtime_models.py
tools/agentx_evolve/model_runtime/profile_loader.py
tools/agentx_evolve/model_runtime/profile_repository.py
tools/agentx_evolve/model_runtime/runtime_registry.py
tools/agentx_evolve/model_runtime/hardware_profile.py
tools/agentx_evolve/model_runtime/model_inventory.py
tools/agentx_evolve/model_runtime/availability_checker.py
tools/agentx_evolve/model_runtime/compatibility_checker.py
tools/agentx_evolve/model_runtime/model_selector.py
tools/agentx_evolve/model_runtime/memory_budget.py
tools/agentx_evolve/model_runtime/runtime_mode.py
tools/agentx_evolve/model_runtime/profile_validator.py
tools/agentx_evolve/model_runtime/schema_validator.py
tools/agentx_evolve/model_runtime/runtime_artifacts.py
```

## 5.2 Schema Files

Create:

```text
tools/agentx_evolve/schemas/local_model_profile.schema.json
tools/agentx_evolve/schemas/local_runtime_profile.schema.json
tools/agentx_evolve/schemas/local_hardware_profile.schema.json
tools/agentx_evolve/schemas/local_model_inventory.schema.json
tools/agentx_evolve/schemas/local_model_availability.schema.json
tools/agentx_evolve/schemas/local_runtime_compatibility_decision.schema.json
tools/agentx_evolve/schemas/local_model_selection_constraints.schema.json
tools/agentx_evolve/schemas/local_runtime_request_limits.schema.json
tools/agentx_evolve/schemas/local_runtime_artifact.schema.json
tools/agentx_evolve/schemas/local_model_eligibility_decision.schema.json
tools/agentx_evolve/schemas/local_model_runtime_evidence_manifest.schema.json
tools/agentx_evolve/schemas/local_model_runtime_review_report.schema.json
tools/agentx_evolve/schemas/local_model_runtime_completion_record.schema.json
```

## 5.3 Test Files

Create:

```text
tools/agentx_evolve/tests/test_local_runtime_models.py
tools/agentx_evolve/tests/test_local_model_profile_schema.py
tools/agentx_evolve/tests/test_local_runtime_profile_schema.py
tools/agentx_evolve/tests/test_local_hardware_profile_schema.py
tools/agentx_evolve/tests/test_local_model_inventory.py
tools/agentx_evolve/tests/test_local_profile_loader.py
tools/agentx_evolve/tests/test_local_profile_repository.py
tools/agentx_evolve/tests/test_local_runtime_registry.py
tools/agentx_evolve/tests/test_local_hardware_profile.py
tools/agentx_evolve/tests/test_local_model_availability.py
tools/agentx_evolve/tests/test_local_runtime_compatibility.py
tools/agentx_evolve/tests/test_local_model_selector.py
tools/agentx_evolve/tests/test_local_quantization_compatibility.py
tools/agentx_evolve/tests/test_local_context_window_compatibility.py
tools/agentx_evolve/tests/test_local_memory_budget.py
tools/agentx_evolve/tests/test_local_runtime_mode.py
tools/agentx_evolve/tests/test_local_selection_constraints.py
tools/agentx_evolve/tests/test_local_request_limits.py
tools/agentx_evolve/tests/test_local_schema_validation.py
tools/agentx_evolve/tests/test_local_runtime_artifacts.py
tools/agentx_evolve/tests/test_local_model_runtime_negative_cases.py
```

## 5.4 Validation Utility File

Create:

```text
tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
```

Purpose:

```text
run deterministic schema validation for all Local Model Runtime Profile schemas
validate required valid examples
validate required invalid examples
exit 0 only when all schema checks pass
exit non-zero on any real schema failure
```

## 5.5 Required Test Fixture Files

Create deterministic fixtures under:

```text
tools/agentx_evolve/tests/fixtures/model_runtime/
```

Required fixture files:

```text
valid_model_profile_small_q4.json
valid_model_profile_small_q8.json
invalid_model_profile_missing_model_id.json
valid_runtime_profile_cpu.json
valid_runtime_profile_gpu_optional.json
invalid_runtime_profile_unknown_quantization.json
valid_static_hardware_profile_cpu_only.json
valid_static_hardware_profile_low_vram.json
valid_model_inventory.json
invalid_model_inventory_unknown_model.json
valid_selection_constraints_local_only.json
invalid_selection_constraints_unbounded.json
valid_request_limits_small_context.json
invalid_request_limits_unbounded.json
policy_allows_local_model.json
policy_denies_local_model.json
```

Fixture rules:

```text
fixtures must not reference real user model paths
fixtures must use temporary paths created by tests when file existence is required
fixtures must not require GPU, runtime installation, model server, network, or hosted credentials
fixtures must cover valid and invalid schema examples
fixtures must be deterministic across machines
```

---

# 6. Required Runtime Artifacts

Runtime artifacts must be written under:

```text
.agentx-init/model_runtime/
```

Required artifacts:

```text
.agentx-init/model_runtime/model_runtime_profile_snapshot.json
.agentx-init/model_runtime/model_inventory_snapshot.json
.agentx-init/model_runtime/hardware_profile_snapshot.json
.agentx-init/model_runtime/profile_repository_snapshot.json
.agentx-init/model_runtime/runtime_compatibility_history.jsonl
.agentx-init/model_runtime/model_availability_history.jsonl
.agentx-init/model_runtime/model_eligibility_history.jsonl
.agentx-init/model_runtime/latest_runtime_compatibility_decision.json
.agentx-init/model_runtime/latest_model_availability_decision.json
.agentx-init/model_runtime/latest_model_eligibility_decision.json
.agentx-init/model_runtime/local_model_runtime_evidence_manifest.json
.agentx-init/model_runtime/local_model_runtime_review_report.json
.agentx-init/model_runtime/local_model_runtime_completion_record.json
```

Rules:

```text
JSONL histories are append-only.
latest JSON files are written atomically.
artifacts must include timestamps.
artifacts must include schema_id and schema_version.
artifacts must not contain secrets.
artifacts must not contain full prompt text.
artifacts must not contain raw model outputs.
artifacts must not write outside .agentx-init/model_runtime/ unless recorded as a deviation.
final evidence artifacts require SHA-256 hashes.
```

---

# 7. File-by-File Implementation Spec

## 7.1 `__init__.py`

Purpose:

```text
Expose the public API for the Local Model Runtime Profile Layer.
```

Required exports:

```python
from .runtime_models import (
    LocalModelProfile,
    LocalRuntimeProfile,
    LocalHardwareProfile,
    LocalModelInventory,
    LocalModelAvailabilityDecision,
    LocalRuntimeCompatibilityDecision,
    LocalModelSelectionConstraints,
    LocalRuntimeRequestLimits,
    LocalModelEligibilityDecision,
)

from .profile_loader import load_model_profiles, load_runtime_profiles, load_hardware_profile
from .profile_repository import resolve_profile_sources, load_profile_repository, hash_profile_repository
from .runtime_registry import load_runtime_registry, get_runtime_profile
from .model_inventory import load_model_inventory
from .availability_checker import check_model_availability
from .compatibility_checker import check_runtime_compatibility
from .model_selector import check_model_eligibility, select_local_model, rank_eligible_models
from .memory_budget import estimate_memory_budget
from .runtime_mode import resolve_runtime_mode, resolve_cpu_gpu_fallback
from .profile_validator import validate_runtime_profiles
from .schema_validator import validate_local_model_runtime_schemas
from .runtime_artifacts import write_runtime_artifact
```

Must not do:

```text
no filesystem writes on import
no model loading on import
no runtime probing on import
no server startup
no network access
```

## 7.2 `runtime_models.py`

Purpose:

```text
Define shared dataclasses, constants, decision values, failure classes, and serialization helpers.
```

Required constants:

```python
RUNTIME_MODE_LOCAL_ONLY = "LOCAL_ONLY"
RUNTIME_MODE_LOCAL_PREFERRED = "LOCAL_PREFERRED"
RUNTIME_MODE_DISABLED = "DISABLED"

DEVICE_CPU = "CPU"
DEVICE_GPU = "GPU"
DEVICE_AUTO = "AUTO"

AVAILABILITY_AVAILABLE = "AVAILABLE"
AVAILABILITY_MISSING = "MISSING"
AVAILABILITY_BLOCKED = "BLOCKED"

COMPATIBILITY_COMPATIBLE = "COMPATIBLE"
COMPATIBILITY_INCOMPATIBLE = "INCOMPATIBLE"
COMPATIBILITY_DEGRADED = "DEGRADED"

ELIGIBILITY_ELIGIBLE = "ELIGIBLE"
ELIGIBILITY_INELIGIBLE = "INELIGIBLE"
ELIGIBILITY_BLOCKED = "BLOCKED"
ELIGIBILITY_DEGRADED = "DEGRADED"

QUANT_F32 = "F32"
QUANT_F16 = "F16"
QUANT_Q8 = "Q8"
QUANT_Q6 = "Q6"
QUANT_Q5 = "Q5"
QUANT_Q4 = "Q4"
QUANT_UNKNOWN = "UNKNOWN"
```

Required dataclasses:

```text
LocalModelProfile
LocalRuntimeProfile
LocalHardwareProfile
LocalModelInventory
LocalModelAvailabilityDecision
LocalRuntimeCompatibilityDecision
LocalModelSelectionConstraints
LocalRuntimeRequestLimits
LocalModelEligibilityDecision
RuntimeArtifactRecord
LocalRuntimeEvidenceManifest
LocalRuntimeReviewReport
LocalRuntimeCompletionRecord
```

Required helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
stable_json_hash(data: dict) -> str
normalize_decision_status(value: str) -> str
```

Acceptance:

```text
dataclasses instantiate
constants match schema enums
to_dict serializes nested dataclasses
stable_json_hash returns deterministic hashes
no filesystem writes
no model runtime imports
```

## 7.2.1 Exact Dataclass Field Contracts

The dataclasses in `runtime_models.py` must align with the JSON schemas and test examples. A field required by a schema must exist in the matching dataclass. A field used by a test fixture must exist in both the dataclass and schema.

### `LocalModelProfile`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_model_profile.schema.json"
model_id: str
model_name: str
model_family: str
model_format: str
model_path: str | None
model_size_bytes: int | None
parameter_count: int | None
quantization: str
max_context_tokens: int
supported_task_types: list[str]
supported_output_modes: list[str]
supported_runtime_ids: list[str]
preferred_runtime_ids: list[str]
requires_gpu: bool
supports_cpu: bool
supports_gpu: bool
enabled: bool
priority: int
profile_source_path: str | None
profile_hash: str | None
warnings: list[str]
errors: list[str]
```

### `LocalRuntimeProfile`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_runtime_profile.schema.json"
runtime_id: str
runtime_name: str
runtime_kind: str
supported_model_formats: list[str]
supported_quantizations: list[str]
supported_devices: list[str]
max_context_tokens: int
requires_server: bool
can_start_server: bool
uses_network: bool
supports_cpu_fallback: bool
supports_gpu_fallback: bool
command_probe_allowed: bool
enabled: bool
priority: int
profile_source_path: str | None
profile_hash: str | None
warnings: list[str]
errors: list[str]
```

### `LocalHardwareProfile`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_hardware_profile.schema.json"
hardware_profile_id: str
probe_mode: str
cpu_arch: str | None
os_name: str | None
ram_total_bytes: int | None
ram_available_bytes: int | None
gpu_present: bool
gpu_name: str | None
gpu_vram_total_bytes: int | None
gpu_vram_available_bytes: int | None
conservative_ram_limit_bytes: int
conservative_vram_limit_bytes: int | None
probe_timestamp: str | None
warnings: list[str]
errors: list[str]
```

### `LocalModelInventory`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_model_inventory.schema.json"
inventory_id: str
created_at: str
approved_model_roots: list[str]
models: list[dict]
warnings: list[str]
errors: list[str]
```

Each inventory model record must include:

```text
model_id
model_path
enabled
expected_size_bytes
expected_sha256, optional
last_seen_at, optional
warnings
errors
```

### `LocalModelAvailabilityDecision`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_model_availability.schema.json"
decision_id: str
timestamp: str
model_id: str
availability: str
model_path: str | None
path_allowed: bool
file_present: bool
profile_repository_hash: str
failure_class: str | None
reason: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `LocalRuntimeCompatibilityDecision`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_runtime_compatibility_decision.schema.json"
decision_id: str
timestamp: str
model_id: str
runtime_id: str
compatibility: str
device: str
format_compatible: bool
quantization_compatible: bool
context_compatible: bool
memory_compatible: bool
policy_allowed: bool
fallback_applied: bool
fallback_reason: str | None
profile_repository_hash: str
failure_class: str | None
reason: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### `LocalModelSelectionConstraints`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_model_selection_constraints.schema.json"
allowed_model_ids: list[str]
blocked_model_ids: list[str]
allowed_runtime_ids: list[str]
blocked_runtime_ids: list[str]
allowed_quantizations: list[str]
blocked_quantizations: list[str]
allowed_devices: list[str]
max_model_size_bytes: int
max_context_tokens: int
max_estimated_memory_bytes: int
local_only: bool
network_allowed: bool
allow_model_download: bool
allow_server_start: bool
allow_cpu_fallback: bool
allow_gpu_fallback: bool
allow_hosted_fallback: bool
preferred_runtime_order: list[str]
preferred_quantization_order: list[str]
preferred_model_order: list[str]
warnings: list[str]
errors: list[str]
```

### `LocalRuntimeRequestLimits`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_runtime_request_limits.schema.json"
max_prompt_tokens: int
max_response_tokens: int
max_total_context_tokens: int
max_input_bytes: int
max_output_bytes: int
max_batch_size: int
max_concurrent_requests: int
reserved_response_tokens: int
safety_margin_tokens: int
warnings: list[str]
errors: list[str]
```

### `LocalModelEligibilityDecision`

Required fields:

```python
schema_version: str = "1.0"
schema_id: str = "local_model_eligibility_decision.schema.json"
decision_id: str
timestamp: str
request_id: str | None
selected_model_id: str | None
selected_runtime_id: str | None
eligibility: str
requested_task_type: str | None
requested_context_tokens: int
runtime_mode: str
device: str
availability_decision_id: str | None
compatibility_decision_id: str | None
estimated_memory: dict
ranking_score: dict
rejected_candidates: list[dict]
fallbacks_applied: list[dict]
profile_repository_hash: str
failure_class: str | None
reason: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### Evidence and completion dataclasses

`RuntimeArtifactRecord`, `LocalRuntimeEvidenceManifest`, `LocalRuntimeReviewReport`, and `LocalRuntimeCompletionRecord` must include:

```text
schema_version
schema_id
component_id
created_at or validated_at
validated_commit where final validation is claimed
artifact paths
artifact hashes
commands with command text, exit_code, status, summary
source_mutation_status
deviation_register
warnings
errors
```

## 7.2.2 Dataclass / Schema / Example Parity Rule

The implementation must enforce this parity rule:

```text
every dataclass has a matching schema
every schema has at least one valid fixture/example
every schema has at least one invalid fixture/example
every field required by schema exists in the dataclass
every evidence-producing dataclass includes evidence_refs or artifact_refs where applicable
every decision dataclass includes failure_class, reason, warnings, and errors
```

A mismatch between dataclass fields, schemas, and fixtures is a schema validation failure.

## 7.3 `profile_loader.py`

Purpose:

```text
Load model, runtime, and hardware profiles from approved static sources.
```

Required functions:

```python
load_model_profiles(profile_paths: list[Path]) -> list[LocalModelProfile]
load_runtime_profiles(profile_paths: list[Path]) -> list[LocalRuntimeProfile]
load_hardware_profile(profile_path: Path) -> LocalHardwareProfile
load_selection_constraints(path: Path) -> LocalModelSelectionConstraints
load_request_limits(path: Path) -> LocalRuntimeRequestLimits
```

Rules:

```text
load JSON only
reject missing required fields
reject unknown schema_id
reject profile files outside approved profile roots
preserve warnings/errors in returned objects
no model file loading
no network access
```

## 7.4 `profile_repository.py`

Purpose:

```text
Resolve profile sources, normalize approved roots, and create a deterministic profile repository snapshot.
```

Required functions:

```python
resolve_profile_sources(repo_root: Path, config: dict) -> dict
load_profile_repository(repo_root: Path, config: dict) -> dict
hash_profile_repository(repository: dict) -> str
validate_approved_model_roots(roots: list[Path], repo_root: Path) -> dict
normalize_model_path(path: Path, approved_model_roots: list[Path]) -> Path
```

Rules:

```text
profile repository hash must be deterministic
model paths must resolve under approved local model roots
relative paths must normalize before comparison
symlink escape must be blocked where detectable
unknown approved roots block path-sensitive availability checks
repository hash must be carried into availability, compatibility, and eligibility evidence
```

Profile repository versioning and immutability rules:

```text
repository snapshot must include repository_id, repository_version, created_at, profile_sources, approved_model_roots, model_profile_hashes, runtime_profile_hashes, inventory_hash, hardware_profile_hash, and repository_hash
repository_hash must be SHA-256 over stable JSON with sorted keys
repository snapshot must be immutable for a selection session
eligibility decisions must record the repository_hash used
if repository_hash changes, a new eligibility decision must be created
```

## 7.5 `runtime_registry.py`

Purpose:

```text
Provide a deterministic registry of known local runtimes.
```

Required functions:

```python
load_runtime_registry(runtime_profiles: list[LocalRuntimeProfile]) -> dict
get_runtime_profile(registry: dict, runtime_id: str) -> LocalRuntimeProfile | None
list_enabled_runtimes(registry: dict) -> list[LocalRuntimeProfile]
list_compatible_runtimes(registry: dict, model_profile: LocalModelProfile) -> list[LocalRuntimeProfile]
```

Rules:

```text
duplicate runtime IDs are rejected
disabled runtimes remain visible but ineligible
unknown runtime_id returns INCOMPATIBLE, not ALLOW
registry order must be deterministic
```

## 7.6 `hardware_profile.py`

Purpose:

```text
Load a static hardware profile and optionally perform safe read-only probes.
```

Required functions:

```python
load_static_hardware_profile(path: Path) -> LocalHardwareProfile
build_conservative_hardware_profile() -> LocalHardwareProfile
probe_hardware_safe(policy_context: dict) -> LocalHardwareProfile
validate_hardware_profile(profile: LocalHardwareProfile) -> dict
```

Hardware probe safety levels:

```text
STATIC_ONLY: use only profile file; default mode.
SAFE_READ_ONLY: allow standard-library or existing local read-only checks only if policy permits.
COMMAND_PROBE: allowed only if Policy and Tool / MCP command wrapper explicitly allow it.
DISABLED: return conservative profile.
```

Rules:

```text
STATIC_ONLY is default
no shell probe by default
no GPU probe required for validation tests
unknown VRAM is conservative, never unlimited
unknown RAM is conservative, never unlimited
probe failure returns conservative profile with warnings
```

## 7.7 `model_inventory.py`

Purpose:

```text
Load and validate the local model inventory.
```

Required functions:

```python
load_model_inventory(path: Path) -> LocalModelInventory
validate_model_inventory(inventory: LocalModelInventory, model_profiles: list[LocalModelProfile]) -> dict
get_inventory_record(inventory: LocalModelInventory, model_id: str) -> dict | None
list_inventory_models(inventory: LocalModelInventory) -> list[dict]
```

Rules:

```text
inventory references must point to known model profiles
inventory paths must be normalized through profile_repository
inventory must not cause model loading
missing model file is MISSING, not exception-only
```

## 7.8 `availability_checker.py`

Purpose:

```text
Check whether a local model is available without loading model weights.
```

Required functions:

```python
check_model_availability(model_id: str, inventory: LocalModelInventory, repository: dict) -> LocalModelAvailabilityDecision
check_model_path_allowed(path: Path, approved_model_roots: list[Path]) -> dict
check_model_file_present(path: Path) -> dict
```

Rules:

```text
availability checks filesystem presence only
never load model weights
never start runtime
never download missing models
model outside approved roots is BLOCKED
missing model path is MISSING
```

## 7.9 `compatibility_checker.py`

Purpose:

```text
Check model/runtime/hardware/request compatibility.
```

Required functions:

```python
check_runtime_compatibility(model_profile: LocalModelProfile, runtime_profile: LocalRuntimeProfile, hardware_profile: LocalHardwareProfile, request_limits: LocalRuntimeRequestLimits) -> LocalRuntimeCompatibilityDecision
check_quantization_compatibility(model_profile: LocalModelProfile, runtime_profile: LocalRuntimeProfile) -> dict
check_context_window_compatibility(model_profile: LocalModelProfile, requested_context_tokens: int) -> dict
check_runtime_format_compatibility(model_profile: LocalModelProfile, runtime_profile: LocalRuntimeProfile) -> dict
```

Decision precedence:

```text
INVALID profile beats all other decisions.
BLOCKED policy/path/server/network decision beats compatibility.
MISSING model file beats compatible runtime.
INCOMPATIBLE quantization/format/context/memory beats degraded fallback.
DEGRADED is allowed only when explicit CPU/GPU fallback is permitted.
COMPATIBLE requires all required checks to pass.
```

## 7.10 `model_selector.py`

Purpose:

```text
Determine model eligibility and rank eligible local models deterministically.
```

Required functions:

```python
check_model_eligibility(model_id: str, request: dict, repository: dict, policy_context: dict) -> LocalModelEligibilityDecision
select_local_model(request: dict, repository: dict, policy_context: dict) -> LocalModelEligibilityDecision
rank_eligible_models(decisions: list[LocalModelEligibilityDecision], constraints: LocalModelSelectionConstraints) -> list[LocalModelEligibilityDecision]
```

Required deterministic ranking order:

```text
1. eligible status before degraded status
2. policy-allowed before policy-warning
3. exact task capability match before generic capability
4. lower estimated memory pressure
5. larger safe context margin
6. preferred runtime priority
7. preferred quantization priority
8. model priority value from profile
9. lexical model_id tie-breaker
```

Rules:

```text
selection must not call inference
selection must not start runtime
selection must not choose hosted fallback
selection must carry repository_hash into evidence
selection must explain every rejected candidate
```

## 7.11 `memory_budget.py`

Purpose:

```text
Estimate whether a model fits within local RAM/VRAM budgets.
```

Required functions:

```python
estimate_memory_budget(model_profile: LocalModelProfile, hardware_profile: LocalHardwareProfile, request_limits: LocalRuntimeRequestLimits) -> dict
estimate_model_memory_bytes(model_profile: LocalModelProfile) -> int
estimate_context_memory_bytes(model_profile: LocalModelProfile, requested_context_tokens: int) -> int
check_memory_fit(estimated: dict, hardware_profile: LocalHardwareProfile) -> dict
```

Rules:

```text
unknown memory values are conservative
memory estimate must include margin
VRAM fit must not assume full device memory is available
CPU fallback must include RAM budget check
```

## 7.12 `runtime_mode.py`

Purpose:

```text
Resolve local runtime mode and CPU/GPU fallback behavior.
```

Required functions:

```python
resolve_runtime_mode(policy_context: dict, config: dict) -> dict
resolve_cpu_gpu_fallback(model_profile: LocalModelProfile, runtime_profile: LocalRuntimeProfile, hardware_profile: LocalHardwareProfile, policy_context: dict) -> dict
is_hosted_fallback_allowed(policy_context: dict) -> bool
```

Rules:

```text
hosted fallback is false by default
local-only mode blocks hosted provider use
CPU fallback must be explicitly allowed
GPU fallback must be explicitly allowed
network/provider mode cannot be enabled here
```

## 7.13 `profile_validator.py`

Purpose:

```text
Validate cross-profile consistency.
```

Required functions:

```python
validate_runtime_profiles(model_profiles: list[LocalModelProfile], runtime_profiles: list[LocalRuntimeProfile], hardware_profile: LocalHardwareProfile, inventory: LocalModelInventory) -> dict
validate_profile_references(repository: dict) -> dict
validate_selection_constraints(constraints: LocalModelSelectionConstraints) -> dict
validate_request_limits(limits: LocalRuntimeRequestLimits) -> dict
```

Rules:

```text
invalid cross-reference blocks validation
unknown runtime referenced by model is invalid
unknown model referenced by inventory is invalid
request limits must be bounded
```

## 7.14 `schema_validator.py`

Purpose:

```text
Validate Local Model Runtime Profile schemas and examples.
```

Required function:

```python
validate_local_model_runtime_schemas(schema_dir: Path, examples: dict) -> dict
```

Rules:

```text
valid examples must pass
missing required fields must fail
invalid enum values must fail
schema validation summary must be evidence-ready
```

## 7.15 `runtime_artifacts.py`

Purpose:

```text
Write runtime evidence artifacts safely.
```

Required functions:

```python
write_profile_snapshot(repository: dict, repo_root: Path) -> dict
write_inventory_snapshot(inventory: LocalModelInventory, repo_root: Path) -> dict
write_hardware_snapshot(hardware_profile: LocalHardwareProfile, repo_root: Path) -> dict
append_runtime_compatibility(decision: LocalRuntimeCompatibilityDecision, repo_root: Path) -> dict
append_model_availability(decision: LocalModelAvailabilityDecision, repo_root: Path) -> dict
append_model_eligibility(decision: LocalModelEligibilityDecision, repo_root: Path) -> dict
write_latest_runtime_compatibility(decision: LocalRuntimeCompatibilityDecision, repo_root: Path) -> dict
write_latest_model_availability(decision: LocalModelAvailabilityDecision, repo_root: Path) -> dict
write_latest_model_eligibility(decision: LocalModelEligibilityDecision, repo_root: Path) -> dict
write_evidence_manifest(manifest: dict, repo_root: Path) -> dict
write_review_report(report: dict, repo_root: Path) -> dict
write_completion_record(record: dict, repo_root: Path) -> dict
calculate_sha256(path: Path) -> str
```

Rules:

```text
create .agentx-init/model_runtime/ if needed
append JSONL for histories
write latest JSON atomically
redact secrets before persistence
include SHA-256 hashes where applicable
include reviewed commit in completion record when available
include command text and exit code in review artifacts
```

---

# 8. Failure Classes

The implementation must use stable failure classes in decision records and evidence.

Required failure classes:

```text
LOCAL_MODEL_PROFILE_INVALID
LOCAL_RUNTIME_PROFILE_INVALID
LOCAL_HARDWARE_PROFILE_INVALID
LOCAL_MODEL_INVENTORY_INVALID
LOCAL_MODEL_NOT_FOUND
LOCAL_MODEL_PATH_MISSING
LOCAL_MODEL_PATH_OUTSIDE_BOUNDARY
LOCAL_MODEL_DISABLED
LOCAL_RUNTIME_DISABLED
LOCAL_RUNTIME_NOT_FOUND
LOCAL_FORMAT_UNSUPPORTED
LOCAL_QUANTIZATION_UNSUPPORTED
LOCAL_CONTEXT_LIMIT_EXCEEDED
LOCAL_REQUEST_LIMIT_EXCEEDED
LOCAL_MEMORY_LIMIT_EXCEEDED
LOCAL_GPU_UNAVAILABLE
LOCAL_CPU_FALLBACK_DISABLED
LOCAL_GPU_FALLBACK_DISABLED
LOCAL_POLICY_DENIED
LOCAL_HOSTED_FALLBACK_BLOCKED
LOCAL_NETWORK_BLOCKED
LOCAL_SERVER_START_BLOCKED
LOCAL_PROBE_BLOCKED
LOCAL_SCHEMA_VALIDATION_FAILED
LOCAL_UNKNOWN_RUNTIME_FAILURE
```

Rules:

```text
every BLOCKED / INCOMPATIBLE / INVALID decision must include a failure class
MISSING decisions must explain whether path, runtime, or model profile is missing
DEGRADED decisions must include fallback reason
UNKNOWN must not be used when a more specific failure class applies
```

---

# 9. Schema Requirements

Each schema must:

```text
require schema_version
require schema_id
require warnings
require errors
reject missing required fields
define enum values for runtime_mode, device, availability, compatibility, eligibility, quantization
allow evidence_refs where decisions are produced
allow profile_repository_hash where a decision depends on repository state
```

Required valid examples in tests:

```text
valid_local_model_profile
valid_local_runtime_profile
valid_local_hardware_profile
valid_local_model_inventory
valid_local_model_availability_decision
valid_local_runtime_compatibility_decision
valid_local_model_selection_constraints
valid_local_runtime_request_limits
valid_local_runtime_artifact
valid_local_model_eligibility_decision
valid_local_model_runtime_evidence_manifest
valid_local_model_runtime_review_report
valid_local_model_runtime_completion_record
```

Required invalid examples:

```text
missing schema_id
missing model_id
unknown runtime_mode
unknown device
unknown quantization
negative context limit
unbounded request limit
model path outside approved root
missing reviewed commit in completion record
missing command exit code in review report
```

---

# 10. Model Profile Loader

The model profile loader must:

```text
load one or more profile files
validate each profile against local_model_profile.schema.json
reject duplicate model_id values
preserve profile source path
attach profile hash
return deterministic order by model_id
```

No profile loader function may load model weights or infer model capabilities from network sources.

---

# 11. Runtime Profile Registry

The runtime registry must:

```text
load runtime profiles
reject duplicate runtime_id values
preserve disabled runtime records
filter enabled runtimes deterministically
return INCOMPATIBLE for unknown runtime references
record registry hash
```

---

# 12. Hardware Probe / Static Hardware Profile

The default implementation must use static hardware profile mode.

Acceptable modes:

```text
STATIC_ONLY
SAFE_READ_ONLY
COMMAND_PROBE
DISABLED
```

Default:

```text
STATIC_ONLY
```

No tests may require real GPU, CUDA, ROCm, Metal, Ollama, llama.cpp, or any installed local runtime.

---

# 13. Model Inventory Loader

The inventory loader must:

```text
load local_model_inventory.schema.json records
validate that each inventory item references a known model profile
normalize paths through approved local model roots
preserve disabled inventory entries
not load model weights
not download missing models
```

---

# 14. Model Availability Checker

The availability checker must return structured decisions:

```text
AVAILABLE
MISSING
BLOCKED
```

It must check:

```text
model profile exists
inventory record exists
model is enabled
runtime is not required to be running
path is under approved model root
file exists where availability requires file presence
```

A missing file is not a crash. It is a schema-valid `MISSING` decision.

---

# 15. Runtime Compatibility Checker

The runtime compatibility checker must verify:

```text
runtime exists
runtime is enabled
model format supported
quantization supported
requested context size fits model profile
request limits fit runtime profile
memory estimate fits hardware profile
server startup is not required
network is not required
```

It returns:

```text
COMPATIBLE
INCOMPATIBLE
DEGRADED
BLOCKED
INVALID
```

---

# 16. Quantization Compatibility Checker

The quantization checker must:

```text
compare model quantization against runtime supported_quantizations
block UNKNOWN quantization unless runtime explicitly permits unknown
prefer smaller quantizations only when allowed by selection constraints
not infer quantization from filename unless explicitly configured
```

---

# 17. Context-Window Compatibility Checker

The context-window checker must:

```text
compare requested_context_tokens against model max_context_tokens
compare requested_context_tokens against runtime max_context_tokens
apply request_size_limits
reserve response token margin
return LOCAL_CONTEXT_LIMIT_EXCEEDED when too large
```

---

# 18. Memory Budget Estimator

The memory estimator must:

```text
estimate model memory
estimate context/KV memory when enough metadata exists
apply safety margin
compare against available RAM/VRAM
support CPU-only conservative checks
support GPU checks without requiring GPU in tests
return LOCAL_MEMORY_LIMIT_EXCEEDED when unsafe
```

---

# 19. Local Runtime Mode Resolver

The resolver must:

```text
resolve LOCAL_ONLY / LOCAL_PREFERRED / DISABLED
block hosted fallback by default
block network by default
not start runtime servers
not install runtime packages
return policy-denied decision when policy forbids local runtime
```

---

# 20. CPU/GPU Fallback Resolver

The fallback resolver must:

```text
prefer requested device when compatible
allow CPU fallback only if explicitly allowed
allow GPU fallback only if explicitly allowed
record fallback reason
return DEGRADED only when fallback is safe and allowed
block when fallback is required but disabled
```

---

# 21. Model Selection Constraints

Model selection constraints must support:

```text
allowed_model_ids
blocked_model_ids
allowed_runtime_ids
blocked_runtime_ids
allowed_quantizations
blocked_quantizations
allowed_devices
max_model_size_bytes
max_context_tokens
max_estimated_memory_bytes
local_only
allow_cpu_fallback
allow_gpu_fallback
allow_hosted_fallback
preferred_runtime_order
preferred_quantization_order
preferred_model_order
```

Default constraints:

```text
local_only = true
allow_hosted_fallback = false
network_allowed = false
allow_model_download = false
allow_server_start = false
```

---

# 22. Request Size Limits

Request limits must define:

```text
max_prompt_tokens
max_response_tokens
max_total_context_tokens
max_input_bytes
max_output_bytes
max_batch_size
max_concurrent_requests
```

Rules:

```text
missing request limits block high-risk selection
negative or zero limits are invalid
unbounded limits are invalid
requested context = prompt tokens + reserved response tokens + safety margin
```

---

# 23. Profile Validation

Profile validation must prove:

```text
schemas validate
cross-references are valid
inventory references known models
runtime references known runtimes
model paths are within approved roots
request limits are bounded
selection constraints are bounded
hardware profile is conservative when unknown
```

---

# 24. Runtime Artifact Writer

The artifact writer must:

```text
write snapshots
append histories
write latest decisions atomically
write evidence manifest
write review report
write completion record
calculate SHA-256 hashes
redact secrets
avoid prompt/model-output logging
```

---

# 25. Integration Requirements

## 25.1 Policy / Capability Registry Integration

Required behavior:

```text
check model-use policy before declaring a model eligible
respect local_only mode
respect network/provider restrictions
respect model allow/block lists
respect runtime allow/block lists
policy missing -> restrictive defaults
policy denied -> LOCAL_POLICY_DENIED
```

## 25.2 Model Adapter Layer Integration

Required behavior:

```text
provide eligibility decisions to Model Adapter
provide runtime profile metadata
provide request limits
provide no direct inference function
provide no model server startup function
```

## 25.3 Context Builder / Task Packer Integration

Required behavior:

```text
expose max safe context tokens
expose prompt/response token budget
return context-limit exceeded before model invocation
support conservative estimates when tokenizer is unavailable
```

## 25.4 Prompt Contract Layer Integration

Required behavior:

```text
expose model capability flags
expose output-format constraints
expose prompt-size limits
no prompt text is durably logged
```

## 25.5 Tool / MCP Adapter Integration

Required behavior:

```text
Tool / MCP Adapter may call read-only profile/eligibility functions.
Tool / MCP Adapter must not use this layer to start inference.
MCP exposure, if any, is read-only profile inspection only.
No model loading, server start, download, or hosted fallback tool is exposed by this layer.
```

## 25.6 Required Integration Handoff Functions

The layer must expose read-only handoff functions for adjacent layers. These functions must return dictionaries or dataclasses that can be schema-validated and logged without loading model weights.

Required functions:

```python
build_policy_model_use_request(model_id: str, runtime_id: str, request: dict, repository: dict) -> dict
apply_policy_model_use_decision(eligibility_decision: LocalModelEligibilityDecision, policy_decision: dict) -> LocalModelEligibilityDecision
build_model_adapter_handoff(eligibility_decision: LocalModelEligibilityDecision, repository: dict) -> dict
build_context_budget_contract(model_id: str, runtime_id: str, request_limits: LocalRuntimeRequestLimits) -> dict
build_prompt_runtime_contract(model_id: str, repository: dict) -> dict
build_tool_mcp_readonly_summary(repository: dict) -> dict
```

Rules:

```text
handoff functions are read-only
handoff functions must not start inference
handoff functions must not reveal raw prompt text
handoff functions must not expose model file contents
handoff functions must preserve profile_repository_hash
handoff functions must include enough IDs for downstream evidence correlation
```

---

# 26. Simulated Dependency Test Contract

Tests must include simulated or fake dependency states.

Required cases:

```text
Policy present and allows local model -> eligible if all local checks pass
Policy present and denies model -> BLOCKED / LOCAL_POLICY_DENIED
Policy missing -> restrictive defaults
Model Adapter missing -> eligibility still returns handoff decision
Context Builder missing -> static request limits still apply
Prompt Contract missing -> capability flags still returned from profile
Tool / MCP Adapter missing -> local API tests still pass
Runtime missing -> INCOMPATIBLE
Hardware unknown -> conservative profile used
```

No test may require external runtime installation, GPU availability, model server startup, network, or hosted provider credentials.

---

# 27. Test Implementation Plan

Required tests:

```text
test_runtime_models_dataclasses_instantiate
test_local_model_profile_schema_valid_and_invalid
test_local_runtime_profile_schema_valid_and_invalid
test_local_hardware_profile_schema_valid_and_invalid
test_inventory_loads_and_rejects_unknown_model_reference
test_profile_loader_rejects_duplicate_model_id
test_profile_repository_hash_is_deterministic
test_model_path_outside_approved_root_blocks
test_runtime_registry_rejects_duplicate_runtime_id
test_static_hardware_profile_loads
test_safe_probe_disabled_by_default
test_model_availability_available_missing_blocked
test_runtime_compatibility_checks_format_quant_context_memory
test_quantization_unsupported_blocks
test_context_window_exceeded_blocks
test_memory_budget_uses_conservative_unknowns
test_runtime_mode_blocks_hosted_fallback_by_default
test_cpu_fallback_requires_explicit_allow
test_gpu_fallback_requires_explicit_allow
test_model_selector_ranking_is_deterministic
test_selection_constraints_reject_unbounded_values
test_request_limits_reject_zero_negative_or_unbounded_values
test_integration_handoff_functions_are_read_only
test_schema_validation_command_covers_all_schemas
test_runtime_artifacts_written_under_runtime_root
test_evidence_manifest_review_report_completion_record_hashes
```

---

# 28. Negative Tests

Required negative tests:

```text
missing model profile -> INVALID
missing runtime profile -> INCOMPATIBLE
missing inventory record -> MISSING
model path outside approved root -> BLOCKED
symlink/path escape attempt -> BLOCKED where detectable
unknown quantization -> INCOMPATIBLE unless explicitly allowed
context request exceeds model limit -> INCOMPATIBLE
request limit unbounded -> INVALID
memory estimate exceeds RAM/VRAM -> INCOMPATIBLE
GPU requested but unavailable -> INCOMPATIBLE or DEGRADED only if CPU fallback allowed
CPU fallback disabled -> BLOCKED
hosted fallback requested -> BLOCKED
network required by runtime -> BLOCKED
server start requested -> BLOCKED
model download requested -> BLOCKED
policy denies model -> BLOCKED
schema-invalid profile -> INVALID
artifact write outside runtime root -> BLOCKED or deviation-required
```

---

# 29. Implementation Order

Implement in this exact order:

```text
1. Create tools/agentx_evolve/model_runtime/ package.
2. Implement runtime_models.py.
3. Create schemas.
4. Implement schema_validator.py.
5. Implement tests/validate_local_model_runtime_schemas.py.
6. Implement profile_repository.py.
7. Implement profile_loader.py.
8. Implement runtime_registry.py.
9. Implement hardware_profile.py.
10. Implement model_inventory.py.
11. Implement availability_checker.py.
12. Implement memory_budget.py.
13. Implement runtime_mode.py.
14. Implement compatibility_checker.py.
15. Implement model_selector.py.
16. Implement profile_validator.py.
17. Implement runtime_artifacts.py.
18. Add tests.
19. Run compileall.
20. Run pytest.
21. Validate schemas.
22. Verify git status.
23. Write evidence manifest, review report, and completion record.
```

Do not reorder unless required by actual import dependencies.

---

# 30. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_local_runtime_models.py \
  tools/agentx_evolve/tests/test_local_model_profile_schema.py \
  tools/agentx_evolve/tests/test_local_runtime_profile_schema.py \
  tools/agentx_evolve/tests/test_local_hardware_profile_schema.py \
  tools/agentx_evolve/tests/test_local_model_inventory.py \
  tools/agentx_evolve/tests/test_local_profile_loader.py \
  tools/agentx_evolve/tests/test_local_profile_repository.py \
  tools/agentx_evolve/tests/test_local_runtime_registry.py \
  tools/agentx_evolve/tests/test_local_hardware_profile.py \
  tools/agentx_evolve/tests/test_local_model_availability.py \
  tools/agentx_evolve/tests/test_local_runtime_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_selector.py \
  tools/agentx_evolve/tests/test_local_quantization_compatibility.py \
  tools/agentx_evolve/tests/test_local_context_window_compatibility.py \
  tools/agentx_evolve/tests/test_local_memory_budget.py \
  tools/agentx_evolve/tests/test_local_runtime_mode.py \
  tools/agentx_evolve/tests/test_local_selection_constraints.py \
  tools/agentx_evolve/tests/test_local_request_limits.py \
  tools/agentx_evolve/tests/test_local_schema_validation.py \
  tools/agentx_evolve/tests/test_local_runtime_artifacts.py \
  tools/agentx_evolve/tests/test_local_model_runtime_negative_cases.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
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
network
hosted model
LLM
model download
model server
Bun
Node
OpenCode runtime
external MCP server
```

Each command recorded in evidence must include:

```text
command text
exit code
status
summary
output artifact path, if output is saved
SHA-256 hash, if output artifact is saved
```

---

# 31. Acceptance Criteria

The layer may be marked implemented only if:

```text
canonical package exists
all required files exist
all schemas exist
all tests exist
schema validation utility exists
test fixtures exist
model profile loader works
profile repository hashes are deterministic
runtime profile registry works
hardware static profile works
hardware probe is disabled by default
model inventory validates profiles
availability checker works without loading weights
runtime compatibility checker works
quantization compatibility checker works
context-window compatibility checker works
memory budget estimator is conservative
local runtime mode resolver blocks hosted fallback by default
CPU/GPU fallback resolver requires explicit fallback permission
model selection constraints are bounded
request size limits are bounded
profile validation catches cross-reference errors
dataclass/schema/example parity is enforced
integration handoff functions are read-only and evidence-ready
runtime artifact writer writes under .agentx-init/model_runtime/
Policy integration is restrictive when missing
Model Adapter integration is handoff-only
Context Builder integration exposes safe limits
Prompt Contract integration exposes capability/limit metadata
Tool / MCP Adapter integration is read-only profile/eligibility inspection
negative tests pass
```

---

# 32. No-Go Conditions

The implementation is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
dataclass/schema/example fields drift
model inference is implemented in this layer
model server starts automatically
model download is possible
network is enabled by default
hosted fallback is enabled by default
model path outside approved roots is accepted
unknown RAM/VRAM is treated as unlimited
unbounded context/request limits are accepted
missing policy allows high-risk model selection
runtime command probe runs by default
GPU is required for validation tests
model weights are loaded during availability checks
Tool / MCP exposes model loading or inference through this layer
artifacts write outside .agentx-init/model_runtime/ without deviation
secrets, prompt text, or model outputs are durably logged
```

---

# 33. Evidence Manifest and Review Report

Create:

```text
.agentx-init/model_runtime/local_model_runtime_evidence_manifest.json
.agentx-init/model_runtime/local_model_runtime_review_report.json
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
  "runtime_artifacts": [],
  "artifact_hashes": [],
  "profile_repository_hash": "<sha256>",
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "deviation_register": [],
  "final_decision": "DONE"
}
```

Review report required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_review_report.schema.json",
  "component_id": "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE",
  "review_document_id": "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC",
  "review_document_version": "v5.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_at": "<UTC timestamp>",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "evidence_manifest_path": ".agentx-init/model_runtime/local_model_runtime_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

Evidence immutability rule:

```text
after final DONE, evidence files must not be modified without a new review report
changed hashes invalidate the previous DONE verdict
manual edits after sign-off require deviation entries
```

---

# 34. Completion Evidence

Create:

```text
.agentx-init/model_runtime/local_model_runtime_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_completion_record.schema.json",
  "component_id": "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE",
  "component_name": "Local Model Runtime Profile Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/model_runtime/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "runtime_artifact_root": ".agentx-init/model_runtime/",
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "integration_verified": {
    "policy_capability_registry": "PASS",
    "model_adapter": "HANDOFF_ONLY",
    "context_builder": "LIMITS_EXPOSED",
    "prompt_contract": "CAPABILITY_FLAGS_EXPOSED",
    "tool_mcp_adapter": "READ_ONLY_PROFILE_ELIGIBILITY"
  },
  "profile_repository_hash": "<sha256>",
  "evidence_manifest_path": ".agentx-init/model_runtime/local_model_runtime_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/model_runtime/local_model_runtime_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 35. Definition of Done

The Local Model Runtime Profile Layer is done when it proves:

```text
all package files exist
all schemas exist
all tests exist
schema validation utility exists
test fixtures exist
compileall passes
pytest passes
schema validation passes
model profiles load and validate
runtime profiles load and validate
hardware profile loads conservatively
model inventory validates references
model availability checks do not load weights
runtime compatibility checks format, quantization, context, memory, and policy
model eligibility decisions are deterministic and evidence-backed
model selection ranking is deterministic
local-only mode blocks hosted fallback by default
CPU/GPU fallback requires explicit permission
model paths outside approved roots block
unbounded request limits block
runtime artifacts are written under .agentx-init/model_runtime/
evidence manifest exists
review report exists
completion record exists
SHA-256 hashes are recorded
no model inference exists in this layer
no server starts automatically
no network is enabled by default
no model download exists
no GPU is required for validation tests
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_local_runtime_models.py \
  tools/agentx_evolve/tests/test_local_model_profile_schema.py \
  tools/agentx_evolve/tests/test_local_runtime_profile_schema.py \
  tools/agentx_evolve/tests/test_local_hardware_profile_schema.py \
  tools/agentx_evolve/tests/test_local_model_inventory.py \
  tools/agentx_evolve/tests/test_local_profile_loader.py \
  tools/agentx_evolve/tests/test_local_profile_repository.py \
  tools/agentx_evolve/tests/test_local_runtime_registry.py \
  tools/agentx_evolve/tests/test_local_hardware_profile.py \
  tools/agentx_evolve/tests/test_local_model_availability.py \
  tools/agentx_evolve/tests/test_local_runtime_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_selector.py \
  tools/agentx_evolve/tests/test_local_quantization_compatibility.py \
  tools/agentx_evolve/tests/test_local_context_window_compatibility.py \
  tools/agentx_evolve/tests/test_local_memory_budget.py \
  tools/agentx_evolve/tests/test_local_runtime_mode.py \
  tools/agentx_evolve/tests/test_local_selection_constraints.py \
  tools/agentx_evolve/tests/test_local_request_limits.py \
  tools/agentx_evolve/tests/test_local_schema_validation.py \
  tools/agentx_evolve/tests/test_local_runtime_artifacts.py \
  tools/agentx_evolve/tests/test_local_model_runtime_negative_cases.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or expected runtime artifacts only
```

---

# 36. Implementation Scoring Rubric

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schemas, tests, validation utility, artifacts exist. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Required scoped test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass. |
| Profile loading and repository | 1.0 | Profiles load, duplicate IDs reject, repository hashes are deterministic. |
| Availability and compatibility | 1.0 | Model availability, runtime, quantization, context, and memory checks work. |
| Eligibility and selection | 1.0 | Eligibility decisions and model ranking are deterministic and fail closed. |
| Runtime safety | 1.0 | No inference, server start, download, hosted fallback, network, or unsafe probe. |
| Evidence and artifacts | 1.0 | JSONL/latest artifacts, evidence manifest, review report, completion record, hashes. |
| Integration and negative tests | 1.0 | Policy, Model Adapter handoff, Context Builder, Prompt Contract, Tool/MCP read-only, negative tests. |

Hard caps:

```text
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
model inference implemented here caps score at 4.0
server starts automatically caps score at 4.0
network enabled by default caps score at 4.0
hosted fallback enabled by default caps score at 4.0
model download exists caps score at 4.0
model path outside root accepted caps score at 5.0
unknown memory treated as unlimited caps score at 6.0
missing evidence manifest caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
missing hashes caps score at 8.0
any required area NOT CHECKED caps score at 8.0
```

---

# 37. Final Frozen Acceptance Matrix

```text
Structure:
[ ] tools/agentx_evolve/model_runtime/ exists
[ ] schemas exist
[ ] tests exist
[ ] validation utility exists

Validation:
[ ] compileall PASS
[ ] pytest PASS
[ ] schema validation PASS
[ ] git status clean or expected runtime artifacts only

Runtime Profile:
[ ] model profiles load
[ ] runtime profiles load
[ ] hardware profile loads conservatively
[ ] inventory validates references
[ ] profile repository hash deterministic

Compatibility:
[ ] model availability checked without loading weights
[ ] quantization checked
[ ] context window checked
[ ] memory budget checked conservatively
[ ] CPU/GPU fallback checked

Safety:
[ ] no inference
[ ] no model server auto-start
[ ] no model download
[ ] no network by default
[ ] hosted fallback blocked by default
[ ] model paths limited to approved roots

Evidence:
[ ] snapshots written
[ ] histories written
[ ] latest decisions written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written

Final:
[ ] no blockers remain
[ ] implementation score is 10.0
[ ] final decision recorded
```

---

# 38. Final Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] Target repository is Agent_X.
[ ] This layer goes under tools/agentx_evolve/model_runtime/.
[ ] Schemas go under tools/agentx_evolve/schemas/.
[ ] Runtime artifacts go under .agentx-init/model_runtime/.
[ ] This layer does not run inference.
[ ] This layer does not start servers.
[ ] This layer does not download models.
[ ] This layer does not enable hosted fallback.
[ ] This layer does not require GPU for tests.
[ ] Policy missing means restrictive defaults.
[ ] Model Adapter integration is handoff-only.
[ ] Tool / MCP exposure is read-only profile/eligibility inspection only.
[ ] Validation must run without GPU, network, hosted model, LLM, model server, Bun, Node, OpenCode runtime, or external MCP server.
```

---

# 39. Final Freeze Rule

This v5 document is frozen as the implementation spec for the Local Model Runtime Profile Layer.

Allowed future changes:

```text
PATCH: typo fixes, wording corrections, additional examples that do not alter requirements.
MINOR: additive optional tests or optional helper functions that do not change safety behavior.
MAJOR: any change that enables inference, server startup, model downloads, hosted fallback, network access, unsafe hardware probes, or different eligibility decision precedence.
```

Blocked without major revision:

```text
enabling hosted fallback by default
enabling model download
enabling model server startup
enabling network by default
allowing inference in this layer
allowing unbounded memory/context limits
allowing model paths outside approved roots
removing evidence artifacts
removing Policy integration
making GPU required for validation tests
```

---

# 40. Final Rating

This v5 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines the canonical package, exact files, schemas, exact dataclass field contracts, functions, fixtures, runtime artifacts, validation utility, model profile loading, runtime registry, hardware profile behavior, inventory loading, availability checking, compatibility checking, quantization/context/memory checks, runtime-mode and CPU/GPU fallback resolution, model selection constraints, request-size limits, profile validation, read-only integration handoffs, artifact writing, negative tests, implementation order, validation commands, acceptance criteria, scoring rubric, Definition of Done, and final freeze rule.
```
