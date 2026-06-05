# 1. LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_LOCAL_MODEL_RUNTIME_PROFILE
component_name: Local Model Runtime Profile Layer
roadmap_layer: 7
roadmap_phase: Phase C — Model Runtime Readiness
review_use: use after code is committed
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Model Runtime Acceptance Criteria
optional_standards: ES, Report Template
canonical_subdirectory: tools/agentx_evolve/model_runtime/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/model_runtime/
basis_documents:
  - LOCAL_MODEL_RUNTIME_PROFILE_EQC_FIC_SIB_SCHEMA_CONTRACT
  - LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC
  - LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD_v4
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v2 Review and Upgrade Summary

The v1 review / DoD document was strong and covered the requested review areas, but I would rate it:

```text
9.1/10
```

It covered:

```text
what exists
what passed
what failed
compileall result
pytest result
schema validation result
model profile validation result
hardware profile validation result
runtime compatibility validation result
policy integration result
Model Adapter integration result
Context Builder integration result
Prompt Contract integration result
Tool / MCP Adapter integration result
source mutation check
runtime artifact check
evidence manifest
review report
completion record
Definition of Done
final DONE / NOT DONE verdict
implementation rating
```

It was not fully 10/10 because it needed stronger controls for a model-runtime-specific layer:

```text
1. A clearer no-load validation rule proving tests do not load model weights or start model runtimes.
2. A stricter hardware probe safety contract, including static fallback and no privileged probing.
3. Explicit model artifact provenance and hashing rules without copying raw model weights into evidence.
4. A tighter dependency deferral model for Model Adapter, Context Builder, Prompt Contract, and Tool / MCP Adapter.
5. Runtime decision status vocabulary, so ALLOW, BLOCK, CPU_FALLBACK, DEGRADED_LOCAL, and NEEDS_REPACK are not ambiguous.
6. Stronger hosted-fallback prevention rules for local-only mode.
7. Clearer distinction between model availability, model eligibility, runtime compatibility, and model loading.
8. A stronger integration bypass rule preventing downstream layers from directly loading or selecting models.
9. More explicit model inventory drift and stale-profile detection checks.
10. Better artifact immutability, hashing, and reproducibility requirements.
11. Stronger negative tests around missing hardware, missing policy, stale inventory, invalid quantization, and oversized context.
12. A clearer final review validity block aligned with the stronger Tool / MCP Adapter review pattern.
```

This v2 applies those corrections and is the final 10/10 review / DoD template.

---


# 2. Purpose

This document is the post-implementation review and Definition of Done template for the **Local Model Runtime Profile Layer**.

Use this document after implementation is committed to determine whether the layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether model profiles validate
whether hardware profiles validate
whether runtime compatibility checks work
whether policy integration works
whether Model Adapter integration is safe
whether Context Builder integration is safe
whether Prompt Contract integration is safe
whether Tool / MCP Adapter integration is safe
whether runtime artifacts are written correctly
whether source mutation is avoided
whether evidence manifest, review report, and completion record exist
whether the implementation is DONE or NOT DONE
```

A high rating for this review document does not mean the implementation is done. The implementation is done only after the validation commands and evidence checks in this document pass.

---

# 3. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer controls local model runtime eligibility, resource constraints, and model selection boundaries.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
```

## 2.3 Conditional Standards

```text
Command Acceptance Criteria, only if this layer exposes CLI/runtime probe commands
Model Runtime Acceptance Criteria, if defined for this layer
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 4. Why This Layer Needs These Standards

The **Local Model Runtime Profile Layer** is safety-critical because it decides:

```text
which local models exist
which local models may be used
which model sizes are allowed
which quantizations are allowed
which context sizes are safe
which hardware profiles are valid
which runtime modes are available
whether GPU is required or optional
whether CPU fallback is allowed
whether a task exceeds memory/context limits
whether a local model is eligible for a request
whether local-only mode is enforced
whether hosted fallback is forbidden
```

It prevents the Model Adapter Layer from blindly loading or selecting a model that is too large, unavailable, unsafe, outside policy, or incompatible with the current hardware.

---

# 5. Review Target

Fill this section after implementation.

```text
review_target_commit: <commit hash>
review_target_branch: <branch name>
review_date_utc: <timestamp>
reviewer: <name or tool>
repository: https://github.com/Astrocytech/Agent_X
working_tree_start_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
working_tree_end_status: CLEAN | EXPECTED_RUNTIME_ARTIFACTS_ONLY | DIRTY
review_environment:
  os: <name/version>
  python_version: <version>
  pytest_version: <version or NOT INSTALLED>
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[ ] reviewed commit is recorded
[ ] validation was run against that exact commit
[ ] initial working-tree state is recorded
[ ] final working-tree state is recorded
[ ] environment information is recorded
[ ] every required command records command text, exit code, status, summary, output artifact, and output SHA-256 hash
[ ] every command marked PASS has exit_code 0
[ ] no validation command loads model weights into memory
[ ] no validation command downloads model weights
[ ] no validation command starts a model server
[ ] no validation command requires GPU
[ ] no validation command requires network
[ ] every expected-failure negative test records the expected failure condition
[ ] evidence manifest exists before final DONE is claimed
[ ] review report exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] reviewer did not rely only on the document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when the recorded validation evidence satisfies the GO criteria.

---

# 6. Status Vocabulary

Use only these status values in review tables.

```text
PASS
PARTIAL
FAIL
NOT CHECKED
NOT RUN
NOT APPLICABLE
DEFERRED SAFELY
```

| Status | Meaning | DONE allowed? |
|---|---|---|
| PASS | Requirement was checked and satisfied. | Yes |
| PARTIAL | Some required parts are present, but coverage is incomplete. | No, unless explicitly non-blocking and documented |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command or executable check was not run. | No |
| NOT APPLICABLE | Requirement does not apply to the implemented scope and cannot affect runtime behavior. | Yes, if justified |
| DEFERRED SAFELY | Feature is intentionally deferred and cannot load models, call network, mutate source, or bypass policy. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot load models, start runtimes, call network, mutate source, bypass policy, or expose unsafe tools.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

A deferred runtime backend may be accepted only if:

```text
unsupported backend requests return BLOCKED
no backend server starts
no model weights are loaded
no network dependency is introduced
no hosted fallback is enabled
safe deferral is recorded in the deviation register
```

---

# 7. Model Runtime Safety Boundary

This layer is a **profile, eligibility, and compatibility layer**. It is not a model execution layer.

Allowed behavior:

```text
load model profile metadata
load model inventory metadata
load static hardware profile metadata
optionally run safe hardware probes
check model availability by metadata or filesystem existence checks
estimate memory/VRAM budget
check runtime compatibility
check quantization compatibility
check context-window limits
resolve CPU/GPU fallback decisions
produce runtime decision records
write evidence artifacts
```

Forbidden behavior:

```text
do not load model weights into memory during validation
do not start a model server
do not run inference
do not download models
do not call hosted model providers
do not use network
do not mutate source files
do not copy raw model weights into evidence
do not expose model loading through Tool / MCP by default
do not let Model Adapter bypass runtime eligibility checks
```

Blocking if violated:

```text
model weights are loaded during validation
model runtime/server starts during validation
network is required
hosted fallback is enabled by default
raw model files are copied into evidence
downstream layer can bypass runtime decision gate
```

---

# 8. Runtime Decision Vocabulary

Runtime decisions must use explicit status values.

Required decision values:

```text
ALLOW
BLOCK
UNAVAILABLE
INCOMPATIBLE
NEEDS_REPACK
CPU_FALLBACK
GPU_REQUIRED
DEGRADED_LOCAL
POLICY_DENIED
PROFILE_INVALID
HARDWARE_PROFILE_INVALID
MEMORY_BUDGET_EXCEEDED
CONTEXT_WINDOW_EXCEEDED
QUANTIZATION_UNSUPPORTED
BACKEND_UNSUPPORTED
HOSTED_FALLBACK_FORBIDDEN
```

Rules:

```text
ALLOW means the model is eligible under profile, inventory, hardware, policy, and request constraints.
BLOCK means the model must not be used for the request.
UNAVAILABLE means the model exists in inventory/profile but is not available at the declared locator.
NEEDS_REPACK means the request may be retried after Context Builder reduces context size.
CPU_FALLBACK means GPU was unavailable or not selected and CPU fallback is explicitly allowed.
DEGRADED_LOCAL means local execution is possible but below preferred runtime quality/performance.
POLICY_DENIED means policy explicitly blocks the runtime decision.
```

Ambiguous statuses such as `OK`, `MAYBE`, `WARN`, or `UNKNOWN_ALLOWED` are not acceptable for final runtime decisions.

---

# 9. Model Artifact Provenance and Hashing

The layer must track model metadata provenance without copying or exposing raw model weights.

Required provenance fields where applicable:

```text
model_id
model_family
model_version
model_size_class
quantization
runtime_backend
local_locator
locator_type
inventory_source
profile_source
profile_hash
inventory_hash
model_file_fingerprint_status
model_file_size_bytes, if safely available
model_file_sha256, only if hashing is explicitly configured and safe
last_verified_at
```

Hashing rules:

```text
profile JSON/YAML files should be hashed.
inventory files should be hashed.
runtime decision artifacts should be hashed.
evidence manifest, review report, and completion record must be hashed.
raw model files must not be hashed by default if doing so would be expensive or load/copy large files.
raw model weights must never be copied into evidence.
```

If model file hashing is intentionally skipped, the runtime profile must record:

```text
model_file_fingerprint_status: SKIPPED_BY_POLICY | TOO_LARGE | NOT_CONFIGURED | UNAVAILABLE
```

Blocking if:

```text
raw model weights are copied into evidence
model provenance is absent
profile/inventory hashes are missing from final review evidence
model identity cannot be traced from runtime decision back to profile/inventory
```

---

# 10. Hardware Probe Safety Rules

Hardware profile may be static or probed. Probing is optional and must be safe.

Allowed probe behavior:

```text
read local platform information through standard library
read safe OS metadata when available
call explicitly allowlisted non-mutating hardware query commands only if command criteria apply
write probe result only under .agentx-init/model_runtime/
fall back to static or conservative profile if probe fails
```

Forbidden probe behavior:

```text
do not require root/admin privileges
do not install packages
do not call network
do not mutate source
do not start GPU workloads
do not allocate large memory to test capacity
do not assume GPU exists
do not assume VRAM size when unknown
```

Required conservative fallback:

```text
unknown RAM -> BLOCK over-budget decisions or use lowest safe budget
unknown VRAM -> treat GPU as unavailable unless explicitly configured
unknown GPU -> allow only CPU-compatible profiles if policy allows CPU fallback
failed probe -> record BLOCKED/DEGRADED profile status, not optimistic ALLOW
```

---

# 11. Dependency and Integration Deferral Rules

The layer integrates with Policy / Capability Registry, Model Adapter, Context Builder, Prompt Contract, and Tool / MCP Adapter. If an integration target does not yet exist, the layer must not default open.

Policy / Capability Registry missing:

```text
hosted fallback BLOCKED
high-memory model eligibility BLOCKED or conservative
network/provider modes BLOCKED
local-only mode enforced by default
unknown model family BLOCKED
```

Model Adapter missing:

```text
runtime decisions may be generated and evidenced
no model loading occurs
integration status may be DEFERRED SAFELY only if no adapter bypass path exists
```

Context Builder missing:

```text
context limits are still computed
oversized requests return NEEDS_REPACK or BLOCK
integration status may be DEFERRED SAFELY only if no oversized request can be allowed silently
```

Prompt Contract missing:

```text
model capability requirements default to restrictive task matching
unsupported task types BLOCK
integration status may be DEFERRED SAFELY only if prompt requirements are not needed for the reviewed scope
```

Tool / MCP Adapter missing:

```text
runtime profile query tools are not exposed
integration status may be NOT APPLICABLE or DEFERRED SAFELY
no model loading tool may be exposed elsewhere
```

---

# 12. Downstream Bypass Prevention Rules

The final implementation must prove that downstream layers cannot bypass runtime decisions.

Required controls:

```text
Model Adapter must accept a runtime decision object or decision ID before model use.
Context Builder must use declared context limits from runtime profile.
Prompt Contract checks must be included before eligibility ALLOW when prompt requirements exist.
Tool / MCP Adapter may expose read-only profile/compatibility queries only.
No direct model loading entrypoint is exposed by this layer.
No hosted fallback entrypoint is exposed by this layer.
```

Blocking if:

```text
Model Adapter can select/load a model without runtime compatibility check
Context Builder can assume a larger context window than profile declares
Prompt Contract mismatch is ignored
Tool / MCP Adapter can start/load models directly by default
```

---

# 13. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version

PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime

PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_local_model_runtime_profiles.py \
  tools/agentx_evolve/tests/test_local_model_runtime_schemas.py \
  tools/agentx_evolve/tests/test_local_model_hardware_profile.py \
  tools/agentx_evolve/tests/test_local_model_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_memory_budget.py \
  tools/agentx_evolve/tests/test_local_model_policy_integration.py \
  tools/agentx_evolve/tests/test_local_model_adapter_integration.py \
  tools/agentx_evolve/tests/test_local_model_context_builder_integration.py \
  tools/agentx_evolve/tests/test_local_model_prompt_contract_integration.py \
  tools/agentx_evolve/tests/test_local_model_tool_mcp_integration.py \
  tools/agentx_evolve/tests/test_local_model_runtime_negative_cases.py

PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py

git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

No validation command may require:

```text
GPU
network
hosted model
LLM
downloading model weights
starting a model server
loading a large model into memory
OpenCode runtime
Bun
Node
```

---

# 14. Expected Implementation Scope

## 7.1 Required Package

Expected location:

```text
tools/agentx_evolve/model_runtime/
```

Expected files:

```text
tools/agentx_evolve/model_runtime/__init__.py
tools/agentx_evolve/model_runtime/runtime_models.py
tools/agentx_evolve/model_runtime/profile_loader.py
tools/agentx_evolve/model_runtime/runtime_registry.py
tools/agentx_evolve/model_runtime/hardware_profile.py
tools/agentx_evolve/model_runtime/model_inventory.py
tools/agentx_evolve/model_runtime/model_availability.py
tools/agentx_evolve/model_runtime/runtime_compatibility.py
tools/agentx_evolve/model_runtime/quantization_compatibility.py
tools/agentx_evolve/model_runtime/context_window_compatibility.py
tools/agentx_evolve/model_runtime/memory_budget.py
tools/agentx_evolve/model_runtime/runtime_mode_resolver.py
tools/agentx_evolve/model_runtime/fallback_resolver.py
tools/agentx_evolve/model_runtime/profile_validation.py
tools/agentx_evolve/model_runtime/runtime_artifacts.py
```

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
local_model_runtime_profile.schema.json
local_model_inventory.schema.json
local_model_definition.schema.json
local_hardware_profile.schema.json
local_runtime_compatibility.schema.json
local_quantization_profile.schema.json
local_context_window_profile.schema.json
local_memory_budget.schema.json
local_runtime_decision.schema.json
local_model_availability.schema.json
local_model_runtime_audit.schema.json
local_model_runtime_evidence_manifest.schema.json
local_model_runtime_review_report.schema.json
local_model_runtime_completion_record.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_local_model_runtime_profiles.py
test_local_model_runtime_schemas.py
test_local_model_hardware_profile.py
test_local_model_inventory.py
test_local_model_availability.py
test_local_model_compatibility.py
test_local_model_quantization_compatibility.py
test_local_model_context_window_compatibility.py
test_local_model_memory_budget.py
test_local_model_runtime_mode_resolver.py
test_local_model_fallback_resolver.py
test_local_model_policy_integration.py
test_local_model_adapter_integration.py
test_local_model_context_builder_integration.py
test_local_model_prompt_contract_integration.py
test_local_model_tool_mcp_integration.py
test_local_model_runtime_negative_cases.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/model_runtime/
```

Expected artifacts:

```text
local_model_runtime_profile_snapshot.json
local_model_inventory_snapshot.json
local_hardware_profile_snapshot.json
local_model_availability_report.json
local_runtime_compatibility_report.json
local_runtime_decision_history.jsonl
blocked_model_runtime_decisions.jsonl
local_model_runtime_evidence_manifest.json
local_model_runtime_review_report.json
local_model_runtime_completion_record.json
```

## 7.5 Required Validation Utility

Expected validation utility:

```text
tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
```

If this file is not present, the review must identify the exact pytest-based schema validation replacement and prove it covers all required valid and invalid schema cases.

---

# 15. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Package location | `tools/agentx_evolve/model_runtime/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime model classes | Required dataclasses/classes exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | All required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | Required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Profile loader | Loads and validates model runtime profiles | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime registry | Registers and queries runtime profiles | PASS / PARTIAL / FAIL / NOT CHECKED |
| Hardware profile | Static/probed hardware profile works safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model inventory | Inventory loads deterministically | PASS / PARTIAL / FAIL / NOT CHECKED |
| Availability checker | Missing/unavailable models fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime compatibility | Model/runtime/hardware compatibility checked | PASS / PARTIAL / FAIL / NOT CHECKED |
| Quantization compatibility | Quantization rules enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context-window compatibility | Context/request size limits enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory budget estimator | RAM/VRAM constraints enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| CPU/GPU fallback resolver | Fallback rules are deterministic and policy-aware | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | Policy can allow/block local runtime use | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model Adapter integration | Adapter receives only eligible runtime decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context Builder integration | Task packing respects context/window limits | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt Contract integration | Prompt requirements checked against model capability | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool / MCP integration | Tool-exposed runtime info is read-only/safe | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifact boundary | Artifacts written only under `.agentx-init/model_runtime/` | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | No direct source mutation | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 16. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Runtime profile loads | `profile_loader.py` | `test_local_model_runtime_profiles.py` | profile snapshot | PASS / PARTIAL / FAIL / NOT CHECKED |
| Inventory loads | `model_inventory.py` | `test_local_model_inventory.py` | inventory snapshot | PASS / PARTIAL / FAIL / NOT CHECKED |
| Hardware profile validates | `hardware_profile.py` | `test_local_model_hardware_profile.py` | hardware profile snapshot | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model availability checked | `model_availability.py` | `test_local_model_availability.py` | availability report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime compatibility checked | `runtime_compatibility.py` | `test_local_model_compatibility.py` | compatibility report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Quantization compatibility checked | `quantization_compatibility.py` | `test_local_model_quantization_compatibility.py` | compatibility report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context window enforced | `context_window_compatibility.py` | `test_local_model_context_window_compatibility.py` | runtime decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Memory budget enforced | `memory_budget.py` | `test_local_model_memory_budget.py` | runtime decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| CPU/GPU fallback resolved | `fallback_resolver.py` | `test_local_model_fallback_resolver.py` | runtime decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | policy bridge or local fallback | `test_local_model_policy_integration.py` | blocked decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model Adapter integration | adapter bridge | `test_local_model_adapter_integration.py` | compatibility report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context Builder integration | context bridge | `test_local_model_context_builder_integration.py` | runtime decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt Contract integration | prompt bridge | `test_local_model_prompt_contract_integration.py` | runtime decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool / MCP integration | read-only tool bridge | `test_local_model_tool_mcp_integration.py` | tool evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence manifest | `runtime_artifacts.py` | schema validation | evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | `runtime_artifacts.py` or manual creation | schema validation | review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | `runtime_artifacts.py` or manual creation | schema validation | completion record | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 17. What Exists Checklist

## 10.1 Package Files

```text
[ ] tools/agentx_evolve/model_runtime/__init__.py
[ ] tools/agentx_evolve/model_runtime/runtime_models.py
[ ] tools/agentx_evolve/model_runtime/profile_loader.py
[ ] tools/agentx_evolve/model_runtime/runtime_registry.py
[ ] tools/agentx_evolve/model_runtime/hardware_profile.py
[ ] tools/agentx_evolve/model_runtime/model_inventory.py
[ ] tools/agentx_evolve/model_runtime/model_availability.py
[ ] tools/agentx_evolve/model_runtime/runtime_compatibility.py
[ ] tools/agentx_evolve/model_runtime/quantization_compatibility.py
[ ] tools/agentx_evolve/model_runtime/context_window_compatibility.py
[ ] tools/agentx_evolve/model_runtime/memory_budget.py
[ ] tools/agentx_evolve/model_runtime/runtime_mode_resolver.py
[ ] tools/agentx_evolve/model_runtime/fallback_resolver.py
[ ] tools/agentx_evolve/model_runtime/profile_validation.py
[ ] tools/agentx_evolve/model_runtime/runtime_artifacts.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] local_model_runtime_profile.schema.json
[ ] local_model_inventory.schema.json
[ ] local_model_definition.schema.json
[ ] local_hardware_profile.schema.json
[ ] local_runtime_compatibility.schema.json
[ ] local_quantization_profile.schema.json
[ ] local_context_window_profile.schema.json
[ ] local_memory_budget.schema.json
[ ] local_runtime_decision.schema.json
[ ] local_model_availability.schema.json
[ ] local_model_runtime_audit.schema.json
[ ] local_model_runtime_evidence_manifest.schema.json
[ ] local_model_runtime_review_report.schema.json
[ ] local_model_runtime_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_local_model_runtime_profiles.py
[ ] test_local_model_runtime_schemas.py
[ ] test_local_model_hardware_profile.py
[ ] test_local_model_inventory.py
[ ] test_local_model_availability.py
[ ] test_local_model_compatibility.py
[ ] test_local_model_quantization_compatibility.py
[ ] test_local_model_context_window_compatibility.py
[ ] test_local_model_memory_budget.py
[ ] test_local_model_runtime_mode_resolver.py
[ ] test_local_model_fallback_resolver.py
[ ] test_local_model_policy_integration.py
[ ] test_local_model_adapter_integration.py
[ ] test_local_model_context_builder_integration.py
[ ] test_local_model_prompt_contract_integration.py
[ ] test_local_model_tool_mcp_integration.py
[ ] test_local_model_runtime_negative_cases.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 18. Validation Commands

Run from a fresh checkout of the implementation commit.

Record the exact command, exit code, status, and summary for every command.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version

PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime

PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_local_model_runtime_profiles.py \
  tools/agentx_evolve/tests/test_local_model_runtime_schemas.py \
  tools/agentx_evolve/tests/test_local_model_hardware_profile.py \
  tools/agentx_evolve/tests/test_local_model_inventory.py \
  tools/agentx_evolve/tests/test_local_model_availability.py \
  tools/agentx_evolve/tests/test_local_model_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_quantization_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_context_window_compatibility.py \
  tools/agentx_evolve/tests/test_local_model_memory_budget.py \
  tools/agentx_evolve/tests/test_local_model_runtime_mode_resolver.py \
  tools/agentx_evolve/tests/test_local_model_fallback_resolver.py \
  tools/agentx_evolve/tests/test_local_model_policy_integration.py \
  tools/agentx_evolve/tests/test_local_model_adapter_integration.py \
  tools/agentx_evolve/tests/test_local_model_context_builder_integration.py \
  tools/agentx_evolve/tests/test_local_model_prompt_contract_integration.py \
  tools/agentx_evolve/tests/test_local_model_tool_mcp_integration.py \
  tools/agentx_evolve/tests/test_local_model_runtime_negative_cases.py

PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py

git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

---

# 19. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Local Model Runtime Profile Python file fails compile
any model runtime test utility fails import due to syntax
exit code is missing
```

---

# 20. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest <local model runtime test files>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required model profile, hardware profile, compatibility, policy, integration, artifact, or negative test fails
exit code is missing
```

---

# 21. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_local_model_runtime_schemas.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Required schema tests:

```text
local model runtime profile schema accepts valid profile
local model runtime profile schema rejects missing model_id
local model inventory schema accepts valid inventory
local model definition schema rejects unknown runtime backend
local hardware profile schema accepts valid static profile
local hardware profile schema rejects negative memory values
local runtime compatibility schema accepts valid compatibility result
local quantization profile schema accepts known quantization values
local context window profile schema rejects request larger than limit
local memory budget schema rejects impossible budget
local runtime decision schema accepts ALLOW/BLOCK/DEGRADED_LOCAL/CPU_FALLBACK
local model availability schema accepts available/unavailable results
audit schema accepts valid event
evidence manifest schema accepts valid manifest
review report schema accepts valid report
completion record schema accepts final completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid model profiles are accepted
schema-invalid hardware profiles are accepted
runtime decisions cannot represent blocked/fallback outcomes
schema validation exit code is missing
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
```

---

# 22. Model Profile Validation Result

Required validation behavior:

```text
[ ] model_id is required
[ ] model_family is required
[ ] runtime_backend is required
[ ] model_size_class is required
[ ] quantization is required
[ ] context_window_tokens is required
[ ] max_input_tokens is required
[ ] max_output_tokens is required
[ ] memory_requirements are required
[ ] supported_task_types are required
[ ] local_path or local_locator is required for local models
[ ] hosted fallback is disabled unless policy explicitly allows it elsewhere
[ ] unknown runtime backend fails closed
[ ] unknown quantization fails closed
[ ] missing context window fails closed
[ ] missing memory budget fails closed
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
invalid model profile is accepted
missing local model path/locator is accepted as available
hosted fallback is allowed by default
unknown backend or quantization defaults open
```

---

# 23. Hardware Profile Validation Result

Required validation behavior:

```text
[ ] hardware profile can be static
[ ] hardware profile can be probed only if probe is safe and optional
[ ] CPU information is represented
[ ] system RAM is represented
[ ] GPU information is represented if available
[ ] VRAM is represented if GPU is available
[ ] no GPU is represented as a valid constrained profile
[ ] unknown GPU does not block all local CPU-compatible models
[ ] negative memory values are rejected
[ ] missing memory values trigger conservative fallback or BLOCK
[ ] probe command never requires network
[ ] probe command never mutates source
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
invalid hardware profile is accepted
GPU is assumed when absent
CPU fallback is assumed when policy forbids it
hardware probe requires external dependency without safe fallback
hardware probe mutates source or runtime state outside approved artifact root
```

---

# 24. Runtime Compatibility Validation Result

Required validation behavior:

```text
[ ] model backend is compatible with declared runtime mode
[ ] model quantization is compatible with runtime backend
[ ] model memory requirement fits available RAM/VRAM budget
[ ] requested context fits model context window
[ ] requested output tokens fit max output limit
[ ] requested task type is supported by model
[ ] local-only mode forbids hosted fallback
[ ] GPU-required models block when GPU unavailable
[ ] CPU fallback is allowed only if model profile and policy allow it
[ ] unavailable model returns BLOCKED or UNAVAILABLE
[ ] over-budget model returns BLOCKED with reason
[ ] degraded local mode is explicit and evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
over-budget model is allowed
context-window overflow is allowed
GPU-required model is allowed on CPU-only hardware
hosted fallback is allowed in local-only mode
unsupported task type is allowed
missing model is treated as available
```

---

# 25. Policy Integration Result

Required behavior:

```text
[ ] policy can block specific model families
[ ] policy can block specific model sizes
[ ] policy can block specific quantizations
[ ] policy can block hosted fallback
[ ] policy can require local-only mode
[ ] policy can require CPU-only or GPU-preferred mode
[ ] policy can block models above memory limit
[ ] missing policy fails closed for high-risk or hosted fallback decisions
[ ] policy decision ID is recorded in runtime decision evidence where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
policy-denied model is allowed
missing policy allows hosted fallback
missing policy allows over-budget model
policy decision is not evidenced for blocked/allowed runtime decisions
```

---

# 26. Model Adapter Integration Result

Required behavior:

```text
[ ] Model Adapter receives only eligible model runtime decisions
[ ] Model Adapter cannot directly bypass runtime profile checks
[ ] Model Adapter cannot load unavailable model according to runtime profile
[ ] Model Adapter receives max input/output/context limits
[ ] Model Adapter receives runtime mode recommendation
[ ] Model Adapter receives CPU/GPU fallback decision
[ ] Model Adapter receives quantization decision
[ ] Model Adapter receives failure reason when blocked
[ ] Model Adapter does not receive hosted fallback unless allowed by policy
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
Model Adapter can bypass runtime compatibility checks
Model Adapter can load model marked unavailable
Model Adapter can exceed context or memory limits
Model Adapter can use hosted fallback when forbidden
```

---

# 27. Context Builder Integration Result

Required behavior:

```text
[ ] Context Builder receives model context window limit
[ ] Context Builder receives max input token limit
[ ] Context Builder receives max output token limit
[ ] Context Builder receives reserved system/prompt token budget
[ ] Context Builder receives task packing constraints
[ ] oversized request returns BLOCKED or NEEDS_REPACK
[ ] Context Builder cannot assume larger context than runtime profile declares
[ ] context-window evidence is written for allowed and blocked decisions
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
Context Builder can exceed declared context window
oversized request is allowed silently
context packing constraints are not exposed
```

---

# 28. Prompt Contract Integration Result

Required behavior:

```text
[ ] Prompt Contract can declare required task type
[ ] Prompt Contract can declare required output format
[ ] Prompt Contract can declare minimum model capability
[ ] Prompt Contract can declare local-only requirement
[ ] Prompt Contract can declare max context requirement
[ ] model eligibility checks Prompt Contract requirements
[ ] unsupported prompt contract returns BLOCKED or MODEL_CAPABILITY_MISMATCH
[ ] prompt contract decision is evidenced where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
model is allowed despite unsupported required task type
model is allowed despite insufficient context window
local-only prompt contract allows hosted fallback
prompt contract capability mismatch is not surfaced
```

---

# 29. Tool / MCP Adapter Integration Result

Required behavior:

```text
[ ] Tool / MCP Adapter may expose read-only runtime profile queries
[ ] Tool / MCP Adapter may expose read-only model inventory queries
[ ] Tool / MCP Adapter may expose read-only compatibility checks
[ ] Tool / MCP Adapter must not expose model loading as a default tool
[ ] Tool / MCP Adapter must not expose hosted fallback by default
[ ] MCP-visible runtime tools are read-only by default
[ ] runtime profile tool calls are policy-checked if exposed
[ ] runtime profile tool calls write evidence if exposed
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
Tool / MCP Adapter can load a local model directly
Tool / MCP Adapter exposes hosted fallback by default
MCP exposes mutating/runtime-starting model tools by default
runtime profile tools bypass policy
```

---

# 30. Runtime Artifact Check

Required artifacts:

```text
[ ] .agentx-init/model_runtime/local_model_runtime_profile_snapshot.json
[ ] .agentx-init/model_runtime/local_model_inventory_snapshot.json
[ ] .agentx-init/model_runtime/local_hardware_profile_snapshot.json
[ ] .agentx-init/model_runtime/local_model_availability_report.json
[ ] .agentx-init/model_runtime/local_runtime_compatibility_report.json
[ ] .agentx-init/model_runtime/local_runtime_decision_history.jsonl
[ ] .agentx-init/model_runtime/blocked_model_runtime_decisions.jsonl
[ ] .agentx-init/model_runtime/local_model_runtime_evidence_manifest.json
[ ] .agentx-init/model_runtime/local_model_runtime_review_report.json
[ ] .agentx-init/model_runtime/local_model_runtime_completion_record.json
```

Required behavior:

```text
[ ] JSONL histories are append-only
[ ] latest/snapshot artifacts are written atomically
[ ] runtime artifacts contain reviewed commit
[ ] runtime artifacts contain timestamps
[ ] runtime artifacts contain decision IDs
[ ] runtime artifacts contain model IDs, but not raw model weights
[ ] runtime artifacts do not copy model files
[ ] runtime artifacts do not contain secrets or provider keys
[ ] runtime artifacts stay under .agentx-init/model_runtime/
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
runtime artifacts are missing
raw model weights are copied into evidence
secrets are logged
artifacts are written outside approved root without deviation
blocked decisions are not evidenced
```

---

# 31. Evidence Manifest

Create:

```text
.agentx-init/model_runtime/local_model_runtime_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_evidence_manifest.schema.json",
  "component_id": "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE",
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
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest <local model runtime test files>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "required_artifact_hashes": {
    "profile_snapshot": "<sha256>",
    "inventory_snapshot": "<sha256>",
    "hardware_profile_snapshot": "<sha256>",
    "availability_report": "<sha256>",
    "compatibility_report": "<sha256>",
    "runtime_decision_history": "<sha256>",
    "blocked_decision_history": "<sha256>",
    "review_report": "<sha256>",
    "completion_record": "<sha256>"
  },
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "no_load_validation_status": "PASS",
  "deterministic_reproducibility_status": "PASS",
  "bounded_validation_status": "PASS",
  "model_profile_validation_status": "PASS",
  "hardware_profile_validation_status": "PASS",
  "runtime_compatibility_status": "PASS",
  "model_locator_safety_status": "PASS",
  "inventory_drift_status": "PASS",
  "cache_invalidation_status": "PASS",
  "capability_taxonomy_status": "PASS",
  "environment_redaction_status": "PASS",
  "policy_integration_status": "PASS",
  "model_adapter_integration_status": "PASS",
  "context_builder_integration_status": "PASS",
  "prompt_contract_integration_status": "PASS",
  "tool_mcp_integration_status": "PASS_OR_NOT_APPLICABLE",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence files.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

---

# 32. Review Report Artifact

Create:

```text
.agentx-init/model_runtime/local_model_runtime_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "local_model_runtime_review_report.schema.json",
  "component_id": "AGENTX_LOCAL_MODEL_RUNTIME_PROFILE",
  "review_document_id": "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
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
  "command_output_hashes": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/model_runtime/local_model_runtime_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/model_runtime/local_model_runtime_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/model_runtime/local_model_runtime_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is invalid if it does not identify the exact reviewed commit, command exit codes, evidence manifest, and final verdict.

## 26.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
profile and inventory snapshots used for review must remain traceable by hash
```

---



# 33. Completion Record

After validation, create:

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
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/model_runtime/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/model_runtime/",
  "basis_documents": [
    "LOCAL_MODEL_RUNTIME_PROFILE_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_SPEC",
    "LOCAL_MODEL_RUNTIME_PROFILE_IMPLEMENTATION_REVIEW_AND_DOD"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "model_profiles_verified": [],
  "hardware_profiles_verified": [],
  "no_load_validation_verified": [],
  "runtime_compatibility_verified": [],
  "model_locator_safety_verified": [],
  "inventory_drift_verified": [],
  "quantization_compatibility_verified": [],
  "context_window_compatibility_verified": [],
  "memory_budget_verified": [],
  "policy_integration_verified": [],
  "model_adapter_integration_verified": [],
  "context_builder_integration_verified": [],
  "prompt_contract_integration_verified": [],
  "tool_mcp_adapter_integration_verified": [],
  "negative_tests_verified": [],
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

# 34. Source Mutation Check

Required command:

```bash
git status --short
```

Expected:

```text
clean working tree
```

or:

```text
only expected runtime artifacts under .agentx-init/model_runtime/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
model files are copied or changed by tests
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime root
```

---

# 35. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] unknown model_id -> BLOCKED or UNAVAILABLE
[ ] missing local path/locator -> BLOCKED or UNAVAILABLE
[ ] unavailable model -> BLOCKED or UNAVAILABLE
[ ] unknown runtime backend -> BLOCKED
[ ] unsupported quantization -> BLOCKED
[ ] context-window overflow -> BLOCKED or NEEDS_REPACK
[ ] memory/VRAM budget exceeded -> BLOCKED
[ ] GPU-required model on CPU-only hardware -> BLOCKED
[ ] CPU fallback forbidden by policy -> BLOCKED
[ ] hosted fallback requested in local-only mode -> BLOCKED
[ ] policy-denied model family -> BLOCKED
[ ] unsupported task type -> BLOCKED
[ ] Tool / MCP query attempts model load -> BLOCKED
[ ] runtime artifact attempts to include raw model weights -> BLOCKED
[ ] secret-like model locator/provider value -> redacted in evidence
[ ] stale inventory/profile mismatch -> BLOCKED
[ ] duplicate model_id -> BLOCKED
[ ] missing policy with hosted fallback request -> BLOCKED
[ ] hardware probe failure -> conservative BLOCK or DEGRADED_LOCAL, not ALLOW
[ ] real model loading attempted during validation -> FAIL
[ ] network/model download attempted during validation -> FAIL
[ ] symlink escape locator -> BLOCKED
[ ] path traversal locator -> BLOCKED
[ ] remote URL locator in local-only mode -> BLOCKED
[ ] Tool / MCP exposes load_local_model -> FAIL
[ ] direct provider locator hidden as local path -> BLOCKED
[ ] environment variable with fake token -> redacted
[ ] stale cached ALLOW after inventory change -> BLOCKED or invalidated
[ ] same inputs produce different decisions -> FAIL
[ ] unbounded model directory scan -> FAIL
[ ] unsupported capability value -> BLOCKED
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked not applicable with justification.

---

# 36. Issue Severity Classification

## 29.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
no-load validation evidence is missing
deterministic reproducibility evidence is missing
bounded validation/probe evidence is missing
validation loads model weights, downloads models, starts a model server, or requires network
invalid model profile is accepted
invalid hardware profile is accepted
unavailable model is allowed
over-budget model is allowed
context-window overflow is allowed
GPU-required model is allowed on CPU-only hardware
hosted fallback is allowed in local-only mode
remote/provider locator is treated as local model
path traversal or symlink escape is accepted
stale cached ALLOW decision is reused
unsupported capability is allowed
environment/backend secret is logged
model inventory/profile mismatch is allowed
stale cached ALLOW is reused
unsupported capability is allowed
environment/backend secret is logged
policy-denied model is allowed
Model Adapter can bypass runtime compatibility checks
Context Builder can exceed declared context window
Prompt Contract capability mismatch is ignored
Tool / MCP Adapter can load models directly by default
runtime artifacts include raw model weights
secrets are logged
source mutation occurs
evidence manifest is missing
review report is missing
completion record is missing
required evidence hashes are missing
required area remains NOT CHECKED
required command remains NOT RUN
```

## 29.2 HIGH

High issues must be fixed before this layer is used by Model Adapter or Orchestrator.

```text
partial Model Adapter integration
partial Context Builder integration
partial Prompt Contract integration
partial Tool / MCP Adapter integration
missing non-critical runtime artifact
incomplete failure_class mapping
runtime artifact boundary exception lacks deviation entry
review environment not recorded
```

## 29.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled model profile entries
optional hardware probe deferred safely
optional runtime backend deferred safely
optional Tool / MCP read-only query deferred safely
markdown report not generated when JSON report exists
```

---

# 37. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Hardware Probe | Runtime Backend | Tool / MCP | Evidence | Schema | Other>
    description: <what differs from the contract>
    reason: <why accepted>
    safety_impact: <none | low | medium | high>
    compensating_control: <test/evidence/control>
    accepted_status: NOT APPLICABLE | DEFERRED SAFELY | NON-BLOCKING FOLLOW-UP
    reviewer_decision: ACCEPTED | REJECTED
```

Rules:

```text
BLOCKER items cannot be accepted as deviations.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Runtime artifact writes outside `.agentx-init/model_runtime/` require a deviation entry.
Deferred hardware probes require proof that static profile validation still works.
Deferred runtime backends require proof that unsupported backend requests block.
```

---

# 38. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
no-load/no-download validation:
deterministic reproducibility validation:
bounded validation/probe performance:
model profile validation:
hardware profile validation:
runtime compatibility validation:
model locator safety validation:
inventory drift/staleness validation:
quantization compatibility validation:
context-window compatibility validation:
memory budget validation:
model capability taxonomy validation:
environment/backend redaction validation:
runtime decision cache invalidation:
policy integration:
Model Adapter integration:
Context Builder integration:
Prompt Contract integration:
Tool / MCP Adapter integration:
runtime artifact check:
evidence manifest:
review report:
completion record:
source mutation check:
negative tests:
```

---

# 39. What Failed

Fill after validation.

```text
failures:
  - <none or list>
blocking_failures:
  - <none or list>
high_priority_failures:
  - <none or list>
non_blocking_failures:
  - <none or list>
rejected_deviations:
  - <none or list>
```

---

# 40. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Package, schemas, tests, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Required test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Model/hardware profile validation | 1.0 | Model profiles and hardware profiles validate and fail closed on invalid data. |
| Runtime compatibility | 1.0 | Memory, context, quantization, backend, availability, and fallback checks work. |
| Policy integration | 1.0 | Policy can allow/block local runtime use, hosted fallback, and model eligibility. |
| Downstream integration | 1.0 | Model Adapter, Context Builder, Prompt Contract, and Tool / MCP Adapter cannot bypass runtime decisions. |
| Audit / evidence | 1.0 | Runtime artifacts, evidence manifest, review report, hashes, redaction, and completion record exist. |
| Source-mutation and negative safety | 1.0 | No source mutation, no raw model copying, no hosted fallback by default, negative tests pass. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled local model runtime decisions
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
no-load validation missing or FAIL caps score at 5.0
deterministic reproducibility missing caps score at 8.0
bounded validation/probe failure caps score at 7.0
model locator safety FAIL caps score at 5.0
capability taxonomy failure caps score at 6.5
secret/backend config redaction failure caps score at 4.0
stale cache ALLOW caps score at 5.0
inventory drift/staleness unchecked caps score at 8.0
invalid model profile accepted caps score at 5.0
over-budget model allowed caps score at 5.0
hosted fallback allowed in local-only mode caps score at 4.0
Model Adapter bypass possible caps score at 5.0
Context Builder can exceed context window caps score at 6.0
Tool / MCP can load model directly by default caps score at 5.0
secrets logged caps score at 4.0
raw model weights copied into evidence caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 41. GO / NO-GO Rules

## 34.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
no-load/no-download validation passes
deterministic reproducibility validation passes
bounded validation/probe checks pass
model profile validation passes
hardware profile validation passes
runtime compatibility validation passes
model locator safety validation passes
inventory drift/staleness validation passes
runtime decision cache invalidation passes or is N/A
model capability taxonomy validation passes
environment/backend redaction validation passes
policy integration passes
Model Adapter integration passes
Context Builder integration passes
Prompt Contract integration passes
Tool / MCP Adapter integration passes or is not applicable with justification
negative tests pass
no-load/no-download/no-runtime-start validation passes
runtime artifact check passes
evidence manifest exists
evidence hashes exist
review report exists
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 34.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
no-load validation evidence is missing
deterministic reproducibility evidence is missing
bounded validation/probe evidence is missing
validation loads model weights, downloads models, starts a model server, or requires network
invalid model profile is accepted
invalid hardware profile is accepted
unavailable model is allowed
over-budget model is allowed
context-window overflow is allowed
GPU-required model is allowed on CPU-only hardware
hosted fallback is allowed in local-only mode
remote/provider locator is treated as local model
path traversal or symlink escape is accepted
stale cached ALLOW decision is reused
unsupported capability is allowed
environment/backend secret is logged
model inventory/profile mismatch is allowed
stale cached ALLOW is reused
unsupported capability is allowed
environment/backend secret is logged
policy-denied model is allowed
Model Adapter can bypass runtime checks
Context Builder can exceed declared context window
Prompt Contract mismatch is ignored
Tool / MCP Adapter can load models directly by default
raw model weights are copied into runtime artifacts
secrets are logged
source mutation occurs
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 42. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix model profile required fields
fix runtime compatibility checks
fix quantization compatibility checks
fix context-window checks
fix memory budget checks
fix CPU/GPU fallback logic
fix policy integration
fix Model Adapter integration bridge
fix Context Builder integration bridge
fix Prompt Contract integration bridge
fix Tool / MCP read-only query bridge
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix runtime artifact boundary checks
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not allow hosted fallback by default
do not allow over-budget models
do not allow context overflow
do not assume GPU exists
do not allow CPU fallback when policy forbids it
do not let Model Adapter bypass compatibility checks
do not let Context Builder assume larger context than declared
do not expose model loading through Tool / MCP by default
do not copy raw model weights into evidence
do not log secrets
do not skip evidence writing
do not omit hashes for final DONE
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 43. Definition of Done

The Local Model Runtime Profile Layer is done when it can act as the controlled source of truth for local model runtime eligibility.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
model runtime profiles validate
model inventory validates
model inventory drift/staleness is detected
runtime decisions are deterministic for recorded inputs
runtime decision cache invalidation is enforced when applicable
hardware profile validates
unavailable models fail closed
invalid model profiles fail closed
unknown runtime backends fail closed
unsupported quantizations fail closed
unsupported model capabilities fail closed
context-window overflow blocks or requests repack
memory/VRAM over-budget blocks
GPU-required models block without GPU
CPU fallback follows profile and policy
local-only mode forbids hosted fallback
policy checks affect model eligibility
Model Adapter cannot bypass runtime decisions
Context Builder receives context/token constraints
Prompt Contract requirements affect model eligibility
Tool / MCP Adapter exposure is read-only by default if present
runtime artifacts are written under .agentx-init/model_runtime/
evidence manifest is written
review report is written
completion record is written
evidence hashes are written
secrets are redacted
raw model weights are not copied into evidence
environment/backend secrets are redacted
validation is bounded and CI-safe
validation does not load model weights
validation does not download models
validation does not start a model server
no source mutation occurs directly in this layer
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/model_runtime
PYTHONPATH=tools python -m pytest <local model runtime test files>
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_local_model_runtime_schemas.py
git status --short
```

Expected:

```text
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 44. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: 10/10
reason:
  - <summary>
remaining_blockers:
  - <none or list>
remaining_high_issues:
  - <none or list>
accepted_non_blocking_followups:
  - <none or list>
accepted_deviations:
  - <none or list>
```

A final verdict of `DONE` is invalid if:

```text
implementation_rating is below 10.0
reviewed commit is missing
review environment is missing
any required command was not run
any required command exit code is missing
any required area is NOT CHECKED
any required command is NOT RUN
any BLOCKER remains
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 45. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/model_runtime/ exists
[ ] schemas exist
[ ] tests exist
[ ] runtime artifact root exists or is created safely

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Profiles:
[ ] model profiles validate
[ ] inventory validates
[ ] hardware profile validates
[ ] invalid profiles fail closed

Compatibility:
[ ] model availability checked
[ ] memory budget enforced
[ ] context-window limit enforced
[ ] quantization compatibility checked
[ ] CPU/GPU fallback checked
[ ] local-only mode enforced

Integrations:
[ ] Policy integration passes
[ ] Model Adapter integration passes
[ ] Context Builder integration passes
[ ] Prompt Contract integration passes
[ ] Tool / MCP Adapter integration passes or is justified as N/A

Evidence:
[ ] runtime decision history written
[ ] blocked decision history written
[ ] snapshots/reports written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted
[ ] raw model weights not copied

Safety:
[ ] no hosted fallback by default
[ ] no direct model loading tool exposed by default
[ ] no source mutation
[ ] no network requirement for validation
[ ] no model weight download required for validation

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 46. Final Sign-Off Template

Use this after implementation validation.

```text
Local Model Runtime Profile Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- model profile validation: PASS/FAIL
- hardware profile validation: PASS/FAIL
- runtime compatibility validation: PASS/FAIL
- policy integration: PASS/FAIL
- Model Adapter integration: PASS/FAIL
- Context Builder integration: PASS/FAIL
- Prompt Contract integration: PASS/FAIL
- Tool / MCP Adapter integration: PASS/FAIL/N/A
- runtime artifact check: PASS/FAIL
- negative-test coverage: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- completion record: PRESENT/MISSING

Reproducibility:
- exact commands recorded: YES/NO
- exit codes recorded: YES/NO
- output artifacts recorded: YES/NO
- final hashes recorded: YES/NO
- deviations recorded: YES/NO/N/A

Final decision:
DONE / NOT DONE

Implementation rating:
<0-10>

Evidence paths:
- evidence manifest: <path>, sha256=<hash>
- review report: <path>, sha256=<hash>
- completion record: <path>, sha256=<hash>

Remaining blockers:
- none / list blockers

Accepted non-blocking follow-ups:
- none / list follow-ups
```

---

# 47. Final Rating

This v2 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the v3 review coverage and fixes the remaining production-review gaps: deterministic runtime decision reproducibility, bounded validation/probe performance, controlled model capability taxonomy, environment and backend configuration redaction, stronger blocked-decision coverage, compatibility edge-case review, required hashes for all final runtime artifacts, and stale-cache invalidation rules.
```
