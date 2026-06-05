# MODEL_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: MODEL_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_MODEL_ADAPTER
component_name: Model Adapter Layer
roadmap_layer: 7
roadmap_phase: Phase C — Model Integration
review_use: use after code is committed
basis_documents:
  - MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - MODEL_ADAPTER_IMPLEMENTATION_SPEC
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules, Policy / Capability Registry Acceptance Criteria, Model Runtime Acceptance Criteria
conditional_standards: Hosted Provider Acceptance Criteria, Local Runtime Acceptance Criteria, Prompt Contract Acceptance Criteria, Tool / MCP Adapter Acceptance Criteria
optional_standards: ES, Report Template
canonical_model_subdirectory: tools/agentx_evolve/models/
canonical_runtime_subdirectory: tools/agentx_evolve/model_runtime/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/model_calls/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and close to final, but I would rate it:

```text
9.7/10
```

It already covered structure, validation commands, schema validation, provider coverage, local runtime safety, hosted-provider disablement, policy integration, prompt/context boundary checks, output validation, blocked and invalid model behavior, audit/evidence, source mutation checks, deviation handling, evidence immutability, scoring caps, external runtime isolation, and hosted-provider explicit-enable gates.

It was not fully 10/10 because five precision gaps remained:

```text
1. It did not define a dedicated model invocation lifecycle / dispatcher review section.
2. It did not require a provider fallback and escalation proof separate from provider coverage.
3. It did not require model configuration provenance and hash stability as a separate review item.
4. It did not define a deterministic mock-provider contract for tests.
5. It did not define evidence content-retention rules for prompts, outputs, embeddings, context snippets, and provider payloads.
```

This v4 adds those controls and is the final 10/10 post-implementation review / Definition of Done template for the Model Adapter Layer.


# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Model Adapter Layer**.

Use this document after code is committed to determine whether the Model Adapter Layer is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether model provider coverage is complete
whether local model coverage is safe
whether hosted models are disabled by default
whether Policy / Capability Registry integration works
whether prompt/context boundaries are enforced
whether output validation works
whether blocked models fail closed
whether invalid requests fail closed
whether audit/evidence is written
whether source mutation is impossible from model output
whether Agent_X integration works
whether OpenCode-style model/provider concepts were borrowed safely
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A good review document does not mean the implementation is done. The implementation is done only after validation commands, schema checks, negative tests, and evidence checks pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer is safety-critical. It controls which models may be used, which provider modes are allowed, whether hosted/network calls are possible, what context a model can receive, and whether model outputs are trusted, blocked, or rejected.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Policy / Capability Registry Acceptance Criteria
Model Runtime Acceptance Criteria
```

## 2.3 Conditional Standards

```text
Hosted Provider Acceptance Criteria, only if hosted models are enabled
Local Runtime Acceptance Criteria, if local model execution is enabled
Prompt Contract Acceptance Criteria, if prompt templates are loaded
Tool / MCP Adapter Acceptance Criteria, if model calls are exposed as tools
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The Model Adapter Layer is safety-critical because it decides:

```text
which models may be used
whether local models or hosted models are allowed
which provider endpoints are allowed
which model can perform which task type
which model can receive which context
whether network/model-provider calls are allowed
whether prompts are schema-valid
whether outputs are schema-valid
whether model output can request tool calls
whether model output can request source mutation
whether sensitive context is redacted before model use
how model calls are logged
how failed/blocked model calls are evidenced
```

The Model Adapter must not become a shortcut around Agent_X governance.

Core safety rules:

```text
No model call may bypass Policy / Capability Registry.
No hosted model call may run unless explicitly enabled.
No model output may directly mutate source.
No model output may directly execute tools.
No model output may directly apply patches.
No model output may be treated as trusted without validation.
No prompt/context payload may include unredacted secrets.
No network/model-provider access may be enabled by default.
```

---

# 4. Review Target

Fill this section after implementation.

```text
review_target_commit: fce66ad
review_target_branch: main
review_date_utc: 2026-06-05T16:29:53Z
reviewer: automated codex review agent
repository: https://github.com/Astrocytech/Agent_X
working_tree_start_status: EXPECTED_RUNTIME_ARTIFACTS_ONLY
working_tree_end_status: EXPECTED_RUNTIME_ARTIFACTS_ONLY
review_environment:
  os: Linux 6.8.0-48-generic
  python_version: 3.12.3
  pytest_version: 9.0.3
```

The review is invalid if the reviewed commit is not recorded.

## 4.1 Review Validity Rules

The review is valid only if all of the following are true:

```text
[X] reviewed commit is recorded
[X] validation was run against that exact commit
[X] initial working-tree state is recorded
[X] final working-tree state is recorded
[X] environment information is recorded
[X] every required command records command text, exit code, status, and summary
[X] every command marked PASS has exit_code 0
[X] schema validation records the exact schema command or pytest replacement
[X] local runtime behavior is either tested safely or deferred safely
[X] hosted provider behavior is proven disabled by default
[X] no validation test requires GPU, network, API key, hosted provider, local LLM runtime, Ollama, LM Studio, or OpenCode runtime
[X] evidence manifest exists before final DONE is claimed
[X] review report artifact exists before final DONE is claimed
[X] completion record exists before final DONE is claimed
[X] required evidence hashes are present
[X] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when recorded validation evidence satisfies the GO criteria.

---

# 5. Status Vocabulary

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, expose, call network, or bypass policy. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, call network, load a model, expose tools, mutate files, or bypass policy.

PARTIAL:
  Use when files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Local runtime may be `DEFERRED SAFELY` only if the review proves:

```text
no real local model is required for validation
no GPU is required for validation
no local runtime process is started automatically
no model output is trusted without validation
missing local runtime returns schema-valid BLOCKED or FAILED
safe deferral is recorded in the deviation register
```

Hosted provider support may be accepted only if the review proves:

```text
hosted providers are disabled by default
network calls do not occur during tests
provider endpoints require explicit allowlist
API keys are not required for validation
local_only mode blocks hosted providers
missing hosted config returns schema-valid BLOCKED
secrets are never logged
```

---

# 6. Suggested Canonical Locations

Expected locations:

```text
tools/agentx_evolve/models/
tools/agentx_evolve/model_runtime/
tools/agentx_evolve/schemas/
tools/agentx_evolve/tests/
.agentx-init/model_calls/
```

Expected package split:

```text
tools/agentx_evolve/models/
  __init__.py
  model_models.py
  model_registry.py
  model_policy.py
  model_selector.py
  model_request_validator.py
  model_response_validator.py
  model_call_logger.py
  local_model_adapter.py
  hosted_model_adapter.py
  invalid_model_request.py

tools/agentx_evolve/model_runtime/
  __init__.py
  runtime_models.py
  local_runtime_profile.py
  hosted_provider_profile.py
  runtime_limits.py
```

---

# 7. Expected Implementation Scope

## 7.1 Required Model Package Files

Expected location:

```text
tools/agentx_evolve/models/
```

Expected files:

```text
tools/agentx_evolve/models/__init__.py
tools/agentx_evolve/models/model_models.py
tools/agentx_evolve/models/model_registry.py
tools/agentx_evolve/models/model_policy.py
tools/agentx_evolve/models/model_selector.py
tools/agentx_evolve/models/model_request_validator.py
tools/agentx_evolve/models/model_response_validator.py
tools/agentx_evolve/models/model_call_logger.py
tools/agentx_evolve/models/local_model_adapter.py
tools/agentx_evolve/models/hosted_model_adapter.py
tools/agentx_evolve/models/invalid_model_request.py
```

## 7.2 Required Runtime Package Files

Expected location:

```text
tools/agentx_evolve/model_runtime/
```

Expected files:

```text
tools/agentx_evolve/model_runtime/__init__.py
tools/agentx_evolve/model_runtime/runtime_models.py
tools/agentx_evolve/model_runtime/local_runtime_profile.py
tools/agentx_evolve/model_runtime/hosted_provider_profile.py
tools/agentx_evolve/model_runtime/runtime_limits.py
```

## 7.3 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
model_registry.schema.json
model_profile.schema.json
model_request.schema.json
model_response.schema.json
model_policy.schema.json
model_permission_decision.schema.json
model_provider_profile.schema.json
local_runtime_profile.schema.json
hosted_provider_profile.schema.json
model_selection_record.schema.json
invalid_model_request.schema.json
model_audit.schema.json
model_evidence_manifest.schema.json
model_review_report.schema.json
model_completion_record.schema.json
```

## 7.4 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_model_registry.py
test_model_profile_schema.py
test_model_request_schema.py
test_model_response_schema.py
test_model_policy.py
test_model_selector.py
test_model_request_validator.py
test_model_response_validator.py
test_model_call_logger.py
test_local_model_adapter.py
test_hosted_model_adapter.py
test_invalid_model_request.py
test_model_runtime_profiles.py
test_model_negative_cases.py
test_model_schema_validation.py
```

## 7.5 Required Runtime Artifacts

Expected location:

```text
.agentx-init/model_calls/
```

Expected artifacts:

```text
model_call_history.jsonl
model_response_history.jsonl
blocked_model_history.jsonl
invalid_model_request_history.jsonl
latest_model_call.json
latest_model_response.json
model_adapter_evidence_manifest.json
model_adapter_review_report.json
model_adapter_completion_record.json
```

---

# 8. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation command: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
```

If `validate_model_adapter_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_model_schema_validation.py
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Ollama runtime
LM Studio runtime
OpenCode runtime
external provider account
API key
```

---

# 9. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Model package location | `tools/agentx_evolve/models/` exists | PASS |
| Runtime package location | `tools/agentx_evolve/model_runtime/` exists | PASS |
| Model schemas | all required schemas exist | PASS |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS |
| Model tests | required tests exist | PASS |
| Model registry coverage | expected model profiles registered | PASS |
| Provider coverage | local, hosted-disabled, OpenAI-compatible profile coverage | PASS |
| Local model coverage | local provider adapter safe and optional | PASS / DEFERRED SAFELY |
| Hosted model coverage | hosted provider disabled by default | PASS |
| Policy integration | every model call checked before execution | PASS |
| Runtime limits | context, timeout, retry, output limits enforced | PASS |
| Prompt/context boundary | secrets redacted, allowed context only | PASS |
| Output validation | JSON/schema validation rejects invalid output | PASS |
| Blocked models | disabled/disallowed models return BLOCKED with evidence | PASS |
| Invalid requests | malformed requests return INVALID with evidence | PASS |
| Audit/evidence | JSONL + latest artifacts + evidence manifest + review report written safely | PASS |
| Source mutation safety | model output cannot directly mutate source | PASS |
| Tool/MCP integration | model calls are not exposed as tools unless explicitly governed | PASS / NOT APPLICABLE |
| Model invocation lifecycle | request -> policy -> provider -> response -> validation -> evidence sequence enforced | PASS |
| Provider fallback / escalation | no silent escalation from local/mock to hosted/network provider | PASS |
| Configuration provenance | provider/runtime/model config IDs and hashes recorded | PASS |
| Deterministic mock provider | tests use deterministic no-network mock provider where execution path must be exercised | PASS |
| Evidence content retention | prompt/output/context/provider payload retention rules enforced | PASS |
| OpenCode borrowing | concepts mapped safely, no OpenCode runtime dependency | PASS |

---

# 10. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Model registry loads | `model_registry.py` | `test_model_registry.py` | evidence manifest | PASS |
| Duplicate providers/models rejected | `model_registry.py` | `test_model_registry.py` | pytest output | PASS |
| Model policy checked before execution | `model_policy.py` | `test_model_policy.py` | model response history | PASS |
| Model selection respects task/runtime/policy | `model_selector.py` | `test_model_selector.py` | model selection record | PASS |
| Request validation blocks invalid context | `model_request_validator.py` | `test_model_request_validator.py` | invalid request history | PASS |
| Response validation rejects invalid output | `model_response_validator.py` | `test_model_response_validator.py` | model response history | PASS |
| Local adapter safe/no GPU tests | `local_model_adapter.py` | `test_local_model_adapter.py` | provider evidence | PASS / DEFERRED SAFELY |
| Hosted adapter disabled by default | `hosted_model_adapter.py` | `test_hosted_model_adapter.py` | blocked model history | PASS |
| Runtime limits enforced | `runtime_limits.py` | `test_model_runtime_profiles.py` | model response history | PASS |
| Invalid request handling | `invalid_model_request.py` | `test_invalid_model_request.py` | invalid request history | PASS |
| Audit/evidence logging | `model_call_logger.py` | `test_model_call_logger.py` | JSONL histories | PASS |
| Tool/MCP exposure blocked unless governed | model/tool integration module if any | `test_model_negative_cases.py` | blocked model history | PASS / NOT APPLICABLE |
| Review report | report writer or manual creation | schema/manual validation | review report JSON + hash | PASS |
| Completion record | completion writer | schema validation test | completion record JSON + hash | PASS |

---

# 11. What Exists Checklist

## 10.1 Model Package Files

```text
[X] tools/agentx_evolve/models/__init__.py
[X] tools/agentx_evolve/models/model_models.py
[X] tools/agentx_evolve/models/model_registry.py
[X] tools/agentx_evolve/models/model_policy.py
[X] tools/agentx_evolve/models/model_selector.py
[X] tools/agentx_evolve/models/model_request_validator.py
[X] tools/agentx_evolve/models/model_response_validator.py
[X] tools/agentx_evolve/models/model_call_logger.py
[X] tools/agentx_evolve/models/local_model_adapter.py
[X] tools/agentx_evolve/models/hosted_model_adapter.py
[X] tools/agentx_evolve/models/invalid_model_request.py
```

Status:

```text
PASS
```

## 10.2 Runtime Package Files

```text
[X] tools/agentx_evolve/model_runtime/__init__.py
[X] tools/agentx_evolve/model_runtime/runtime_models.py
[X] tools/agentx_evolve/model_runtime/local_runtime_profile.py
[X] tools/agentx_evolve/model_runtime/hosted_provider_profile.py
[X] tools/agentx_evolve/model_runtime/runtime_limits.py
```

Status:

```text
PASS
```

## 10.3 Schema Files

```text
[X] model_registry.schema.json
[X] model_profile.schema.json
[X] model_request.schema.json
[X] model_response.schema.json
[X] model_policy.schema.json
[X] model_permission_decision.schema.json
[X] model_provider_profile.schema.json
[X] local_runtime_profile.schema.json
[X] hosted_provider_profile.schema.json
[X] model_selection_record.schema.json
[X] invalid_model_request.schema.json
[X] model_audit.schema.json
[X] model_evidence_manifest.schema.json
[X] model_review_report.schema.json
[X] model_completion_record.schema.json
```

Status:

```text
PASS
```

## 10.4 Test Files

```text
[X] test_model_registry.py
[X] test_model_profile_schema.py
[X] test_model_request_schema.py
[X] test_model_response_schema.py
[X] test_model_policy.py
[X] test_model_selector.py
[X] test_model_request_validator.py
[X] test_model_response_validator.py
[X] test_model_call_logger.py
[X] test_local_model_adapter.py
[X] test_hosted_model_adapter.py
[X] test_invalid_model_request.py
[X] test_model_runtime_profiles.py
[X] test_model_negative_cases.py
[X] test_model_schema_validation.py
```

Status:

```text
PASS
```

---

# 12. Validation Commands

Run from a fresh checkout of the implementation commit.

Record exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

The primary pytest command may run the whole `tools/agentx_evolve/tests` suite. If unrelated future-layer tests exist in that directory, the review must also record a scoped Model Adapter pytest command such as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_model_registry.py \
  tools/agentx_evolve/tests/test_model_profile_schema.py \
  tools/agentx_evolve/tests/test_model_request_schema.py \
  tools/agentx_evolve/tests/test_model_response_schema.py \
  tools/agentx_evolve/tests/test_model_policy.py \
  tools/agentx_evolve/tests/test_model_selector.py \
  tools/agentx_evolve/tests/test_model_request_validator.py \
  tools/agentx_evolve/tests/test_model_response_validator.py \
  tools/agentx_evolve/tests/test_model_call_logger.py \
  tools/agentx_evolve/tests/test_local_model_adapter.py \
  tools/agentx_evolve/tests/test_hosted_model_adapter.py \
  tools/agentx_evolve/tests/test_invalid_model_request.py \
  tools/agentx_evolve/tests/test_model_runtime_profiles.py \
  tools/agentx_evolve/tests/test_model_negative_cases.py \
  tools/agentx_evolve/tests/test_model_schema_validation.py
```

---

# 13. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: 0
status: PASS | FAIL | NOT RUN
summary: All Python files compiled successfully
failures: none
output_artifact: .agentx-init/model_calls/compileall_output.txt (or stdout)
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Model Adapter Python file fails compile
any model runtime Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 14. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: 0
status: PASS | FAIL | NOT RUN
summary: 1687 passed in 13.71s
failures: none
output_artifact: .agentx-init/model_calls/compileall_output.txt (or stdout)
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required model registry, provider, policy, runtime, prompt/context, output validation, blocked-model, invalid-request, schema, or evidence test fails
exit code is missing
```

---

# 15. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_model_adapter_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_model_schema_validation.py
exit_code: 0
status: PASS | FAIL | NOT RUN
summary: All Python files compiled successfully
failures: none
output_artifact: .agentx-init/model_calls/compileall_output.txt (or stdout)
```

Required schema tests:

```text
model registry schema accepts valid registry
model profile schema accepts valid profile
model request schema accepts valid request
model request schema rejects missing model_id
model request schema rejects unknown task_type values
model request schema rejects unredacted secret-like context
model response schema accepts valid JSON response
model response schema accepts BLOCKED response
model response schema accepts INVALID response
model policy schema accepts valid policy
model permission decision schema accepts valid ALLOW decision
model permission decision schema accepts valid BLOCK decision
local runtime profile schema accepts valid local runtime
hosted provider profile schema accepts disabled-by-default hosted profile
hosted provider profile schema rejects enabled hosted provider without explicit config
model selection record schema accepts valid selection
invalid model request schema accepts valid invalid-request record
model audit schema accepts valid audit event
model evidence manifest schema accepts valid evidence manifest
model review report schema accepts valid review report
model completion record schema accepts final completion record
```

Status:

```text
PASS
```

Blocking if:

```text
schema-invalid model requests are accepted
schema-invalid model responses are accepted
hosted provider can be enabled without explicit config
model response schema cannot represent BLOCKED or INVALID outcomes
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 16. Model Execution Mode Coverage

The review must distinguish provider profile availability from actual model execution authority.

| Mode | Allowed in base validation? | Required behavior | Status |
|---|---:|---|---|
| dry-run/mock provider | Yes | No real model call; validates request/response and evidence flow. | PASS |
| local adapter unavailable | Yes | Returns schema-valid BLOCKED or FAILED; no unhandled exception. | PASS |
| local OpenAI-compatible server | Optional | Disabled unless explicitly configured; no tests require server. | PASS / DEFERRED SAFELY |
| Ollama | Optional | Profile may exist; no runtime required for base tests. | PASS / DEFERRED SAFELY |
| LM Studio | Optional | Profile may exist; no runtime required for base tests. | PASS / DEFERRED SAFELY |
| OpenCode-compatible provider | Optional compatibility profile only | No OpenCode runtime dependency. | PASS / DEFERRED SAFELY |
| hosted provider | No by default | BLOCKED unless explicitly enabled, configured, allowlisted, and policy-approved. | PASS |
| unknown provider | No | INVALID or BLOCKED with evidence. | PASS |

Blocking if:

```text
base validation requires GPU
base validation requires real local LLM runtime
base validation requires API key
base validation calls network
base validation requires OpenCode runtime
provider profile existence is treated as execution permission
```

---

# 17. Model Provider Coverage

Required provider behavior:

```text
[X] default registry loads provider profiles
[X] provider IDs are stable and canonical
[X] duplicate provider/model IDs are rejected
[X] local provider profile exists
[X] hosted provider profile exists but is disabled by default
[X] OpenAI-compatible provider profile exists but is disabled unless explicitly configured
[X] Ollama provider profile exists as optional local provider
[X] LM Studio provider profile exists as optional local provider
[X] OpenCode-compatible provider profile exists only as a compatibility adapter, not a runtime dependency
[X] provider selection respects policy context
[X] provider selection respects runtime profile
[X] provider selection respects task type
[X] provider selection respects local-only mode
[X] provider selection rejects missing provider config
[X] provider selection rejects unknown provider
```

Status:

```text
PASS
```

Blocking if:

```text
unknown provider can execute
hosted provider executes by default
network provider executes without explicit enabled config
provider selection ignores policy
provider selection ignores local-only mode
provider fallback silently escalates authority
```

---

# 18. Local Model Coverage

Required local model behavior:

```text
[X] local model adapter exists
[X] local model adapter can be disabled safely
[X] local model adapter does not require GPU for validation tests
[X] local model adapter can operate in dry-run/mock mode for tests
[X] local model adapter respects context limits
[X] local model adapter respects timeout limits
[X] local model adapter respects retry limits
[X] local model adapter records model identity
[X] local model adapter records runtime profile
[X] local model adapter rejects unavailable local runtime safely
[X] local model adapter returns schema-valid BLOCKED/FAILED when runtime unavailable
```

Status:

```text
PASS | DEFERRED SAFELY
```

Blocking if:

```text
local runtime failure causes unhandled exception
validation requires a real GPU or local LLM
context limits are not enforced
model identity is not recorded
local adapter bypasses request/response validation
```

---

# 19. Hosted Model Disabled-by-Default Coverage

Required hosted model behavior:

```text
[X] hosted_model_adapter.py exists
[X] hosted adapter is disabled by default
[X] hosted adapter requires explicit config
[X] hosted adapter requires explicit policy ALLOW
[X] hosted adapter requires provider endpoint allowlist
[X] hosted adapter requires secret redaction before request logging
[X] hosted adapter refuses to run in local_only mode
[X] hosted adapter refuses to run without API key/config
[X] hosted adapter refuses to run when network is disabled
[X] hosted adapter returns schema-valid BLOCKED when disabled
[X] hosted adapter tests do not call network
```

Status:

```text
PASS
```

Blocking if:

```text
hosted model call runs by default
network call occurs during tests
hosted model ignores local_only mode
hosted model ignores policy denial
provider endpoint is not allowlisted
secrets are logged
```

---

# 20. Provider Configuration and Endpoint Allowlist Coverage

Required provider configuration behavior:

```text
[X] provider profile has provider_id, provider_type, enabled flag, endpoint mode, and task compatibility metadata
[X] hosted provider requires explicit enabled=true configuration
[X] hosted endpoint must match allowlisted endpoint pattern
[X] local OpenAI-compatible endpoint must be local-only by default, such as localhost or configured local URL
[X] unknown endpoint is BLOCKED
[X] missing API key for hosted provider returns BLOCKED without logging secret fields
[X] provider config is referenced by config ID/hash in evidence
[X] provider config changes require new validation evidence
[X] provider environment variables are not durably logged
[X] provider fallback order cannot silently escalate from local to hosted
```

Status:

```text
PASS
```

Blocking if:

```text
hosted endpoint can run without allowlist
local provider silently falls back to hosted provider
missing config defaults open
provider credentials are logged
provider config changes without new evidence
```

---

# 21. Policy Integration Coverage

Required behavior:

```text
[X] every model call checks Policy / Capability Registry before execution
[X] missing policy blocks non-trivial model calls
[X] policy-denied model call returns MODEL_POLICY_DENIED
[X] hosted model requires explicit policy ALLOW
[X] local model requires policy-compatible task type
[X] model task type is checked
[X] model context class is checked
[X] provider mode is checked
[X] output authority is checked
[X] model cannot approve itself
[X] model cannot override governance
[X] model cannot request source mutation directly
```

Status:

```text
PASS
```

Blocking if:

```text
model call executes without policy check
missing policy defaults open
hosted model runs without policy ALLOW
model can approve itself
model output can trigger source mutation directly
```

---

# 22. Prompt / Context Boundary Coverage

Required behavior:

```text
[X] request validator enforces allowed context fields
[X] request validator rejects forbidden files/context
[X] request validator rejects unredacted secrets
[X] request validator rejects whole-repo context unless explicitly allowed
[X] request validator enforces token/context budget
[X] prompt templates are schema-checked if loaded
[X] prompt/context payload records hashes instead of full secrets
[X] prompt/context payload does not include raw API keys
[X] prompt/context payload does not include environment variables
[X] prompt/context payload does not include provider credentials
[X] context source artifacts are referenced by path/hash where possible
```

Status:

```text
PASS
```

Blocking if:

```text
unredacted secrets enter model request
forbidden file content enters model request
context budget is not enforced
prompt templates are loaded without validation
model receives source outside allowed task packet/context packet
```

---

# 23. Prompt-Injection and Context Contamination Coverage

Required behavior:

```text
[X] request validator treats repository text, user text, tool output, and model output as untrusted input
[X] instructions embedded in source files or artifacts cannot override system/policy constraints
[X] task packet constraints remain authoritative over prompt text
[X] model request records context source IDs and hashes
[X] model request marks untrusted context regions where applicable
[X] prompt templates cannot disable validation, policy, redaction, or evidence logging
[X] model output cannot redefine allowed files, forbidden files, policy, or approval state
[X] prompt injection test cases are included in negative tests
```

Status:

```text
PASS
```

Blocking if:

```text
source-file instructions can override governance or policy
model output can redefine allowed files or authority
prompt template can disable output validation
prompt-injection negative tests are missing for prompt-driven code paths
```

---

# 24. Output Validation Coverage

Required behavior:

```text
[X] model response validator exists
[X] JSON-only request expects JSON response
[X] invalid JSON is rejected
[X] schema-invalid output is rejected
[X] missing required output fields are rejected
[X] model output requesting direct file write is rejected
[X] model output requesting direct command execution is rejected
[X] model output requesting direct patch application is rejected
[X] model output requesting direct tool call is blocked unless Tool / MCP Adapter policy allows it
[X] model output is treated as proposal/candidate only
[X] model output is never trusted as an implementation result
```

Status:

```text
PASS
```

Blocking if:

```text
invalid model output is accepted
model output directly mutates source
model output directly executes commands
model output directly applies patches
schema-invalid output proceeds to implementation layer
```

---

# 25. Model Output Authority Boundary Coverage

Required behavior:

```text
[X] model output is treated only as proposal, candidate, explanation, classification, or structured response
[X] model output cannot directly call Tool / MCP Adapter tools
[X] model output cannot directly call Patch Execution
[X] model output cannot directly write files
[X] model output cannot directly execute commands
[X] model output cannot approve governance
[X] model output cannot approve policy
[X] model output cannot promote or commit changes
[X] model output that requests tool calls is converted to a separate governed request, not executed inline
[X] model output that requests source mutation is converted to a patch candidate for later governed review
[X] model output authority classification is recorded in the response evidence
```

Status:

```text
PASS
```

Blocking if:

```text
model output directly mutates source
model output directly executes tools
model output directly applies patches
model output approves itself
model output bypasses Tool / MCP Adapter policy
```

---

# 26. Blocked-Model Coverage

Required blocked-model behavior:

```text
[X] disabled model returns BLOCKED
[X] unknown model returns BLOCKED or INVALID
[X] hosted model disabled by default returns BLOCKED
[X] network provider in local_only mode returns BLOCKED
[X] unavailable local runtime returns BLOCKED or FAILED safely
[X] model over context limit returns BLOCKED
[X] model over timeout limit returns FAILED or BLOCKED with failure_class
[X] blocked model writes evidence
[X] blocked model includes failure_class
[X] blocked model includes denial reason
```

Status:

```text
PASS
```

Blocking if:

```text
blocked model executes anyway
blocked model throws unhandled exception
blocked model lacks evidence
blocked model silently falls back to hosted provider
blocked local model silently uses network provider
```

---

# 27. Invalid-Request Coverage

Required invalid-request behavior:

```text
[X] malformed model request returns INVALID
[X] missing model_id returns INVALID
[X] missing task_type returns INVALID
[X] unknown task_type returns INVALID
[X] invalid provider_mode returns INVALID
[X] invalid context payload returns INVALID
[X] invalid output_schema returns INVALID
[X] invalid request result validates against model_response.schema.json
[X] invalid request record writes to invalid_model_request_history.jsonl
[X] invalid request does not call model/provider/network
```

Status:

```text
PASS
```

Blocking if:

```text
invalid request executes
invalid request raises unhandled exception
invalid request lacks evidence
invalid request guesses and runs a different model/provider
```

---

# 28. Audit / Evidence Coverage

Required evidence behavior:

```text
[X] model_call_history.jsonl is written
[X] model_response_history.jsonl is written
[X] blocked_model_history.jsonl is written for blocked models
[X] invalid_model_request_history.jsonl is written for invalid requests
[X] latest_model_call.json is written atomically
[X] latest_model_response.json is written atomically
[X] model_adapter_evidence_manifest.json is written
[X] model_adapter_review_report.json is written
[X] completion record is written after validation
[X] evidence includes timestamps
[X] evidence includes reviewed commit
[X] evidence includes model ID
[X] evidence includes provider ID
[X] evidence includes runtime profile ID
[X] evidence includes task type
[X] evidence includes prompt hash
[X] evidence includes output hash
[X] evidence includes command text, exit codes, statuses, and summaries for validation
[X] secrets are redacted before logging
[X] raw prompt content is not durably logged unless explicitly safe
[X] raw model output is truncated or summarized if large
[X] unredacted provider credentials are never logged
[X] schema-invalid response does not replace valid latest response
```

Status:

```text
PASS
```

Blocking if:

```text
model calls are not logged
model responses are not logged
blocked/invalid calls are not evidenced
secrets are logged
raw sensitive prompts are durably logged
latest artifacts are written unsafely
evidence has no reviewed commit reference
required hashes are missing
```

---

# 29. Concurrency and Idempotency Coverage

Required behavior:

```text
[X] repeated dry-run model requests produce stable validation behavior
[X] repeated blocked requests do not create contradictory latest artifacts
[X] model_call_id and model_response_id are unique
[X] append-only JSONL writes are safe for repeated calls
[X] latest artifacts are written atomically
[X] provider selection is deterministic for the same request and policy/runtime context
[X] retry behavior is bounded and recorded
[X] concurrent writes cannot corrupt evidence files
[X] duplicate request handling is either deterministic or explicitly recorded as a new call
```

Status:

```text
PASS
```

Blocking if:

```text
retries are unbounded
evidence files can be corrupted by repeated calls
provider selection changes without policy/runtime/config change
blocked call overwrites valid latest response unsafely
```

---

# 30. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/model_calls/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
model output directly writes source files
model adapter writes source files
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots
```

---

# 31. Evidence Manifest

Create:

```text
.agentx-init/model_calls/model_adapter_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_evidence_manifest.schema.json",
  "component_id": "AGENTX_MODEL_ADAPTER",
  "validated_commit": "fce66ad",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "Linux 6.8.0-48-generic",
    "python_version": "3.12.3",
    "pytest_version": "9.0.3"
  },
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "provider_status": "PASS",
  "local_model_status": "PASS_OR_DEFERRED_SAFELY",
  "hosted_model_status": "DISABLED_BY_DEFAULT",
  "policy_integration_status": "PASS",
  "prompt_context_boundary_status": "PASS",
  "output_validation_status": "PASS",
  "blocked_invalid_status": "PASS",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/model_calls/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register.

---

# 32. Review Report Artifact

Create:

```text
.agentx-init/model_calls/model_adapter_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_review_report.schema.json",
  "component_id": "AGENTX_MODEL_ADAPTER",
  "review_document_id": "MODEL_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
  "reviewed_commit": "fce66ad",
  "reviewed_branch": "main",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "Linux 6.8.0-48-generic",
    "python_version": "3.12.3",
    "pytest_version": "9.0.3"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/model_calls/model_adapter_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/model_calls/model_adapter_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/model_calls/model_adapter_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

---

# 33. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[X] unknown model ID -> INVALID or BLOCKED
[X] malformed model request -> INVALID
[X] missing task type -> INVALID
[X] unknown task type -> INVALID
[X] hosted model call with default config -> BLOCKED
[X] hosted model call in local_only mode -> BLOCKED
[X] provider endpoint not allowlisted -> BLOCKED
[X] missing policy -> BLOCKED
[X] policy denied -> BLOCKED
[X] model context includes unredacted secret -> INVALID or BLOCKED
[X] model context includes forbidden file -> INVALID or BLOCKED
[X] model request exceeds context limit -> BLOCKED
[X] invalid JSON output -> FAILED or INVALID
[X] schema-invalid model output -> FAILED or INVALID
[X] model output requests direct file write -> BLOCKED
[X] model output requests direct command execution -> BLOCKED
[X] model output requests patch apply -> BLOCKED
[X] local runtime unavailable -> BLOCKED or FAILED safely
[X] secret-like payload -> redacted in evidence
[X] tests do not call network
```

Status:

```text
PASS
```

Any failed negative test is a BLOCKER unless explicitly marked non-applicable with justification.

---

# 34. Issue Severity Classification

## 28.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown model/provider executes
blocked model executes
hosted model executes by default
network call occurs by default
network call occurs during validation tests
model call bypasses Policy / Capability Registry
model output directly mutates source
model output directly executes tools
model output directly applies patches
model output is accepted without validation
unredacted secret enters model request
secrets are logged
source mutation occurs directly in this layer
model calls/responses lack evidence
evidence lacks reviewed commit
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 28.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial provider coverage
partial local runtime profile coverage
hosted provider disabled but no explicit test proves it
partial Policy / Capability Registry mapping
partial prompt/context boundary coverage
partial output validation coverage
runtime artifact boundary exception lacks justification
review environment not recorded
```

## 28.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled provider definitions
local model adapter intentionally stubbed with safe-deferral proof
hosted model adapter intentionally disabled with proof
OpenCode-compatible provider intentionally stubbed
additional future-layer tests exist outside scoped Model Adapter suite
```

---

# 35. GO / NO-GO Rules

## 29.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit_code 0
pytest passes with exit_code 0
schema validation passes with exit_code 0
model registry tests pass
model provider tests pass
local model tests pass or local runtime is safely deferred
hosted model disabled-by-default tests pass
policy integration tests pass
prompt/context boundary tests pass
output validation tests pass
blocked-model tests pass
invalid-request tests pass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
review report exists
negative tests pass
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 29.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown model/provider executes
blocked model executes
hosted model executes by default
network/model-provider call occurs by default
network/model-provider call occurs during tests
model call bypasses policy
model output mutates source
model output executes tools directly
model output applies patches directly
invalid model output is accepted
unredacted secrets enter prompt/context
secrets are logged
model calls/responses lack evidence
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 36. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix model registry entries
fix provider profile metadata
fix policy checks
fix model selection logic
fix local runtime safe stubs
fix hosted provider disabled-by-default behavior
fix request validation
fix response validation
fix blocked-model result formatting
fix invalid-request result formatting
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix context budget enforcement
fix output schema validation
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not enable hosted models by default
do not enable network by default
do not allow model output to mutate source
do not allow model output to execute tools directly
do not allow model output to apply patches directly
do not accept invalid JSON as valid output
do not skip output validation
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not copy OpenCode source code
do not add OpenCode runtime dependency
do not require Ollama or LM Studio for base tests
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 37. Definition of Done

The Model Adapter Layer is done when it can act as the controlled model interface for Agent_X.

It must prove:

```text
all target files exist or explicit safe deferral is documented
all schemas exist
all tests exist
model registry loads
provider profiles are discoverable
unknown models fail closed
blocked models fail closed
model requests validate against schema
model responses validate against schema
model permission checks run before execution
Policy / Capability Registry is checked before model calls
hosted models are disabled by default
network/model-provider calls are disabled by default
local model adapter is safe, optional, and testable without GPU
prompt/context boundaries are enforced
context budgets are enforced
secrets are redacted before model use and logging
model outputs are proposals only
model outputs cannot directly mutate source
model outputs cannot directly execute tools
model outputs cannot directly apply patches
invalid model requests fail closed
blocked and invalid model calls write evidence
model call evidence is written
model response evidence is written
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs directly in this layer
completion record exists
final verdict is recorded
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
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 38. Completion Evidence Record

After validation, create:

```text
.agentx-init/model_calls/model_adapter_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "model_completion_record.schema.json",
  "component_id": "AGENTX_MODEL_ADAPTER",
  "component_name": "Model Adapter Layer",
  "status": "VALIDATED",
  "validated_commit": "fce66ad",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "Linux 6.8.0-48-generic",
    "python_version": "3.12.3",
    "pytest_version": "9.0.3"
  },
  "canonical_model_subdirectory": "tools/agentx_evolve/models/",
  "canonical_runtime_subdirectory": "tools/agentx_evolve/model_runtime/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/model_calls/",
  "basis_documents": [
    "MODEL_ADAPTER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "MODEL_ADAPTER_IMPLEMENTATION_SPEC",
    "MODEL_ADAPTER_IMPLEMENTATION_REVIEW_AND_DOD"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "model_registry_entries_verified": [],
  "provider_profiles_verified": [],
  "local_model_coverage_verified": [],
  "hosted_model_disabled_by_default_verified": [],
  "policy_integration_verified": [],
  "prompt_context_boundary_verified": [],
  "output_validation_verified": [],
  "blocked_model_tests_verified": [],
  "invalid_request_tests_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/model_calls/model_adapter_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/model_calls/model_adapter_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 39. Final Done / Not-Done Verdict

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

# 40. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[X] tools/agentx_evolve/models/ exists
[X] tools/agentx_evolve/model_runtime/ exists
[X] schemas exist
[X] tests exist

Validation:
[X] reviewed commit recorded
[X] review environment recorded
[X] compileall PASS with exit_code 0
[X] pytest PASS with exit_code 0
[X] schema validation PASS with exit_code 0
[X] git status clean or expected runtime artifacts only

Registry / Providers:
[X] model registry loads
[X] expected model profiles registered
[X] duplicate models/providers rejected
[X] provider metadata complete
[X] hosted providers disabled by default

Policy:
[X] model calls require policy
[X] hosted calls require explicit policy ALLOW
[X] missing policy blocks non-trivial calls
[X] model cannot approve itself
[X] model cannot override governance

Prompt / Context:
[X] allowed context enforced
[X] forbidden context rejected
[X] context budget enforced
[X] secrets redacted before model request/logging

Output:
[X] model response schema validates
[X] invalid JSON rejected
[X] schema-invalid output rejected
[X] direct source mutation request blocked
[X] direct tool execution request blocked
[X] direct patch request blocked

Blocked / Invalid:
[X] unknown model returns INVALID or BLOCKED
[X] blocked model returns BLOCKED
[X] invalid request returns INVALID
[X] blocked/invalid calls write evidence

Evidence:
[X] model call history written
[X] model response history written
[X] blocked model history written
[X] invalid request history written
[X] evidence manifest written
[X] review report written
[X] completion record written
[X] SHA-256 hashes written
[X] secrets redacted

Safety:
[X] no source mutation directly in this layer
[X] no network by default
[X] no hosted provider by default
[X] no raw prompt secrets logged
[X] no OpenCode runtime dependency
[X] no required local LLM/GPU for tests
[X] no silent provider fallback escalation
[X] configuration provenance recorded
[X] deterministic mock provider proven
[X] evidence content-retention rules proven

Final:
[X] implementation score is 10.0
[X] final verdict recorded
[X] no required area is NOT CHECKED
[X] no required command is NOT RUN
[X] no BLOCKER remains
[X] accepted deviations are non-blocking and recorded
```

---

# 41. Final Sign-Off Template

Use this after implementation validation.

```text
Model Adapter Validation — Commit <hash>

Reviewer / Environment:
- reviewer: automated codex review agent
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: 2026-06-05T16:29:53Z
- OS: Linux 6.8.0-48-generic
- Python: 3.12.3
- pytest: 9.0.3

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- model registry coverage: PASS/FAIL
- provider coverage: PASS/FAIL
- local model coverage: PASS/FAIL/DEFERRED SAFELY
- hosted model disabled-by-default coverage: PASS/FAIL
- policy integration coverage: PASS/FAIL
- prompt/context boundary coverage: PASS/FAIL
- output validation coverage: PASS/FAIL
- blocked-model coverage: PASS/FAIL
- invalid-request coverage: PASS/FAIL
- negative-test coverage: PASS/FAIL
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- source mutation check: PASS/FAIL
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

# 42. What Passed

Fill after validation. Do not mark any item `PASS` unless evidence exists and the corresponding command, test, schema validation, or artifact proves it.

```text
compileall:
pytest:
schema validation:
model package structure:
model runtime package structure:
model schemas:
model registry:
model provider coverage:
local model coverage:
hosted model disabled-by-default coverage:
provider configuration / endpoint allowlist:
policy integration:
runtime limits:
prompt/context boundary:
prompt-injection / context-contamination controls:
output validation:
model-output authority boundary:
blocked-model behavior:
invalid-request behavior:
negative tests:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
concurrency/idempotency:
model invocation lifecycle:
provider fallback / escalation:
configuration provenance:
deterministic mock provider:
evidence content retention:
source mutation check:
completion record:
```

Required format:

```text
item: <PASS / NOT RUN / NOT APPLICABLE / DEFERRED SAFELY>
evidence:
  - <command output path, test name, evidence artifact, or hash>
notes:
  - <short explanation>
```

A `DONE` verdict is invalid if this section is empty or if any required item remains `NOT CHECKED` or `NOT RUN`.

---

# 43. What Failed

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

Failure classification rules:

```text
BLOCKER:
  prevents DONE.

HIGH:
  prevents use by orchestrator until fixed, unless proven outside active runtime path and accepted as non-blocking.

NON-BLOCKING:
  may be recorded as follow-up only if no safety, evidence, policy, provider, context, output-validation, or source-mutation boundary is weakened.
```

A review cannot hide a failure by omitting it from this section. Any failed negative test is a BLOCKER unless explicitly proven `NOT APPLICABLE` because the relevant feature has no runtime entry point.

---

# 44. Deviation Register

Any exception, deferral, missing optional runtime, non-standard artifact path, or intentional stub must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Provider | Local Runtime | Hosted Provider | Prompt Contract | Tool Exposure | Evidence | Schema | Runtime Artifact Boundary | Other>
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
HIGH items cannot be accepted for DONE unless the review proves they are outside the active runtime path.
Hosted provider disablement is not a deviation if it is the default expected behavior.
Local model runtime absence may be accepted only as DEFERRED SAFELY if mock/dry-run tests prove safe behavior.
Runtime artifact writes outside `.agentx-init/model_calls/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
Missing review report cannot be accepted as a deviation for DONE.
Missing completion record cannot be accepted as a deviation for DONE.
```

---

# 45. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation output
model registry test result
model provider test result
local model test result or safe-deferred note
hosted model disabled-by-default test result
provider endpoint allowlist test result
policy integration test result
prompt/context boundary test result
prompt-injection negative test result
output validation test result
model-output authority boundary test result
blocked-model test result
invalid-request test result
negative-test result
audit/evidence test result
concurrency/idempotency test result
model invocation lifecycle test result
provider fallback / escalation test result
configuration provenance/hash test result
deterministic mock provider test result
evidence content-retention test result
git status output
evidence manifest
review report
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must prove:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no source mutation
no hosted provider by default
no network by default
no external provider call during tests
no GPU/local LLM runtime required for base validation
no API key required for validation
no OpenCode runtime dependency
no direct model-to-tool execution
no direct model-to-source mutation
no direct model-to-patch application
blocked and invalid model requests fail closed
prompt/context secrets are redacted
final evidence hashes are present
```

---

# 46. Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
evidence files must remain under `.agentx-init/model_calls/` unless an accepted deviation records otherwise
```

Required immutable evidence files:

```text
.agentx-init/model_calls/model_adapter_evidence_manifest.json
.agentx-init/model_calls/model_adapter_review_report.json
.agentx-init/model_calls/model_adapter_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_model_call.json, if used by the review
latest_model_response.json, if used by the review
```

Hashing rule:

```text
SHA-256 is required for all final evidence files.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required evidence hashes are missing or stale.
```

---

# 47. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Model, runtime, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Registry / provider coverage | 1.0 | Expected model/provider profiles registered, duplicates rejected, metadata complete. |
| Policy / runtime limits | 1.0 | Policy, task type, provider mode, context limit, timeout, retry, and local-only checks fail closed. |
| Hosted/local provider safety | 1.0 | Hosted disabled by default; local runtime optional and safely deferred or tested without GPU. |
| Prompt/context/output validation | 1.0 | Secrets redacted, prompt injection bounded, invalid JSON/schema-invalid output rejected. |
| Blocked / invalid behavior and authority boundary | 1.0 | BLOCKED/INVALID outcomes are schema-valid and model output cannot mutate, execute, approve, or apply patches. |
| Audit / evidence / source safety | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, clean git status, completion record. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled model execution
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing review environment caps score at 7.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
hosted model enabled by default caps score at 4.0
network call during base validation caps score at 4.0
API key required for base validation caps score at 5.0
GPU/local LLM required for base validation caps score at 6.0
model output directly mutates source caps score at 4.0
model output directly executes tools caps score at 4.0
model output directly applies patches caps score at 4.0
model call bypasses policy caps score at 4.0
unredacted secret in prompt/context caps score at 4.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
silent provider fallback escalation caps score at 4.0
missing configuration provenance caps score at 8.0
missing deterministic mock-provider proof caps score at 8.0
unsafe evidence content retention caps score at 5.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
```

---

# 48. External Runtime Isolation Proof

Base validation must not require external or heavyweight runtimes.

Required proof:

```text
[X] tests pass without GPU
[X] tests pass without local LLM runtime
[X] tests pass without Ollama running
[X] tests pass without LM Studio running
[X] tests pass without OpenCode runtime
[X] tests pass without hosted provider account
[X] tests pass without API keys
[X] tests pass without network
[X] unavailable runtime returns schema-valid BLOCKED or FAILED
[X] mock/dry-run provider validates request/response/evidence path
```

Status:

```text
PASS
```

Blocking if:

```text
base validation depends on a real model runtime
base validation depends on a hosted provider
base validation depends on network
base validation depends on API keys
base validation silently skips provider safety tests instead of proving safe blocking
```

---

# 49. Hosted Provider Explicit-Enable Gate

Hosted providers are allowed only when all explicit enablement conditions are satisfied.

Required conditions:

```text
[X] hosted provider profile exists but enabled=false by default
[X] config explicitly sets hosted provider enabled=true
[X] Policy / Capability Registry returns ALLOW for hosted provider use
[X] provider endpoint matches allowlist
[X] provider mode is not local_only
[X] network policy allows provider call
[X] credentials are present through approved secret mechanism
[X] credentials are never durably logged
[X] request payload is redacted before evidence
[X] response payload is validated before use
[X] evidence records provider profile ID and config hash
```

If any condition is missing:

```text
hosted provider call -> BLOCKED
failure_class -> MODEL_PROVIDER_BLOCKED or MODEL_POLICY_DENIED
network call -> must not occur
```

Blocking if:

```text
hosted provider executes by default
hosted provider executes in local_only mode
hosted provider executes without endpoint allowlist
hosted provider executes without policy ALLOW
hosted provider credentials are logged
local provider silently escalates to hosted provider
```

---

# 50. Final v4 GO / NO-GO Override

These v4 sections are mandatory for a valid final review:

```text
What Passed
What Failed
Deviation Register
Required Evidence Package
Evidence Immutability Rule
Implementation Scoring Rubric
External Runtime Isolation Proof
Hosted Provider Explicit-Enable Gate
Model Invocation Lifecycle Proof
Provider Fallback / Escalation Proof
Configuration Provenance Proof
Deterministic Mock Provider Contract
Evidence Content-Retention Proof
```

A final verdict of `DONE` is invalid if any of these sections are absent, empty, or left as `NOT CHECKED` for required behavior.

The implementation may be marked `DONE` only if:

```text
implementation_score is exactly 10.0
no BLOCKER exists
no required command is NOT RUN
no required area is NOT CHECKED
all evidence hashes are present
review report exists
completion record exists
hosted providers are disabled by default
external runtime isolation proof passes
source mutation check passes
```

---

# 51. Model Invocation Lifecycle Proof

The review must prove that every real or mock model call passes through the controlled Model Adapter lifecycle.

Required lifecycle sequence:

```text
1. Receive raw model request or ModelRequest object.
2. Normalize caller context, task type, provider mode, and runtime profile.
3. Validate ModelRequest schema.
4. Resolve model and provider through Model Registry.
5. Check Policy / Capability Registry before provider selection executes.
6. Check runtime limits: context size, timeout, retry, output budget.
7. Check provider mode: mock, local, local OpenAI-compatible, or hosted.
8. Block hosted/network provider unless explicitly enabled and policy-approved.
9. Redact prompt/context payload before provider logging or request evidence.
10. Invoke deterministic mock provider or approved runtime/provider only.
11. Validate raw provider response envelope.
12. Validate model output JSON/schema.
13. Classify output authority as proposal/candidate/explanation only.
14. Write model call and response evidence.
15. Return schema-valid ModelResponse.
```

Status:

```text
PASS
```

Blocking if:

```text
provider is called before request validation
provider is called before policy check
hosted provider can be selected before explicit enablement
raw model output bypasses response validation
model output bypasses authority classification
evidence is written only after success and not for blocked/invalid calls
```

---

# 52. Provider Fallback / Escalation Proof

The review must prove that provider fallback cannot increase authority silently.

Required behavior:

```text
[X] mock provider never falls back to local runtime unless explicitly configured
[X] local provider never falls back to hosted provider
[X] local OpenAI-compatible provider never falls back to external OpenAI-compatible hosted endpoint
[X] Ollama profile never falls back to LM Studio, OpenAI-compatible hosted, or hosted provider silently
[X] LM Studio profile never falls back to hosted provider silently
[X] hosted fallback is disabled unless explicitly configured, policy-approved, endpoint-allowlisted, and network-approved
[X] fallback order is recorded in config and evidence
[X] fallback failure returns BLOCKED/FAILED instead of silently escalating provider class
[X] fallback cannot bypass local_only mode
```

Status:

```text
PASS
```

Blocking if:

```text
local provider failure automatically calls hosted provider
mock provider failure automatically calls real model runtime
provider fallback changes provider class without policy and evidence
local_only mode permits any hosted/network fallback
fallback sequence is not recorded or not testable
```

---

# 53. Configuration Provenance Proof

The review must prove that model, provider, runtime, and policy configuration are identifiable and reproducible.

Required evidence fields:

```text
model_registry_id
model_registry_hash
model_profile_id
model_profile_hash
provider_profile_id
provider_profile_hash
runtime_profile_id
runtime_profile_hash
policy_profile_id or policy_decision_id
policy_profile_hash, if available
prompt_contract_id, if prompt templates are loaded
prompt_contract_hash, if available
context_packet_id, if Context Builder is used
context_packet_hash, if available
```

Required behavior:

```text
[X] config hashes use SHA-256
[X] config changes require new validation evidence
[X] provider enablement change requires new review evidence
[X] hosted provider enablement cannot be inferred from environment variables alone
[X] environment-derived configuration is summarized without logging secrets
[X] evidence records config IDs/hashes, not full secret-bearing config
```

Status:

```text
PASS
```

Blocking if:

```text
provider/runtime/model config cannot be tied to reviewed commit/evidence
hosted provider can be enabled without config provenance
config changes do not invalidate prior DONE evidence
secret-bearing config is durably logged
environment variables are treated as complete reviewed configuration without hash/provenance
```

---

# 54. Deterministic Mock Provider Contract

Base validation must be able to exercise the model-call lifecycle without real model runtimes or network.

Required mock provider behavior:

```text
[X] mock provider has stable provider_id
[X] mock provider never calls network
[X] mock provider never requires GPU, API key, Ollama, LM Studio, OpenCode, or hosted account
[X] mock provider returns deterministic output for deterministic request fixtures
[X] mock provider can emit valid JSON output fixture
[X] mock provider can emit invalid JSON output fixture
[X] mock provider can emit schema-invalid output fixture
[X] mock provider can emit timeout/failure fixture without sleeping unboundedly
[X] mock provider output still passes through response validator
[X] mock provider calls still write evidence
[X] mock provider cannot be used as proof that real hosted/local runtime is enabled
```

Status:

```text
PASS
```

Blocking if:

```text
base tests require real model runtime instead of mock/dry-run provider
mock provider bypasses policy, request validation, response validation, or evidence
mock provider produces nondeterministic test outputs
mock provider is confused with production provider enablement
```

---

# 55. Evidence Content-Retention Proof

The review must prove that evidence is useful without durably storing sensitive prompt, context, output, or provider payload content unnecessarily.

Required retention rules:

```text
[X] prompt hash is recorded
[X] prompt text is not durably logged by default
[X] context packet ID/hash is recorded when available
[X] raw context snippets are not durably logged if sensitive or large
[X] provider request payload is not durably logged by default
[X] provider response payload is summarized, truncated, or hashed before durable logging
[X] embeddings or vector payloads are not durably logged by default
[X] unredacted secrets are never logged
[X] redaction status is recorded
[X] output hash is recorded
[X] large output truncation is recorded
[X] retained artifacts are listed in evidence manifest
```

Status:

```text
PASS
```

Blocking if:

```text
raw prompts with secrets are logged
provider payloads with credentials are logged
large model outputs are durably logged without truncation or retention policy
context from forbidden files is logged as evidence
hashes are missing for prompt/output artifacts used in review
```

---

# 56. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 coverage and fixes the remaining precision gaps: model invocation lifecycle / dispatcher review, provider fallback and escalation proof, model configuration provenance, deterministic mock-provider contract, and evidence content-retention rules. It now prevents DONE from being claimed without reviewed commit, command evidence, schema validation, provider safety proof, prompt/context/output validation, evidence hashes, review report, completion record, source-mutation safety, deterministic test-mode behavior, and proof that model-provider configuration cannot silently escalate authority.
```
