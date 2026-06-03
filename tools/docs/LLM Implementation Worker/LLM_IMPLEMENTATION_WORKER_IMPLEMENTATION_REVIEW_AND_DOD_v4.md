# LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_LLM_IMPLEMENTATION_WORKER
component_name: LLM Implementation Worker
roadmap_layer: 10
roadmap_phase: Phase C — Implementation Generation
review_use: use after code is committed
basis_documents:
  - LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC
  - LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v4
  - LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards:
  - Command Acceptance Criteria, if worker can request validation commands through tools
  - Model Adapter Acceptance Criteria, if model calls are wired in this phase
  - Tool / MCP Adapter Acceptance Criteria, if worker can call tools in this phase
  - Governed Patch Execution Acceptance Criteria, if worker can hand off patch proposals
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if it writes markdown reports
canonical_worker_subdirectory: tools/agentx_evolve/workers/llm_implementation_worker/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/implementation_worker/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was very strong. I would rate v3:

```text
9.8/10
```

It already covered the major 10/10 review requirements for the LLM Implementation Worker: validation commands, schema validation, model/tool/policy/sandbox/failure/patch integration, prompt/context safety, model-output schema gating, tool-request allowlisting, budget limits, idempotency, concurrency, negative tests, evidence manifests, review reports, scoring, GO / NO-GO rules, and final verdict structure.

It was not fully 10/10 because a final reviewer would still need several precision controls to prevent an implementation from passing with ambiguous or simulated proof:

```text
1. A stricter distinction between active integration tests and simulated/fake-adapter tests.
2. A formal fake-adapter contract for Model Adapter, Tool Adapter, Policy Registry, Sandbox, Failure Taxonomy, and Patch Handoff tests.
3. A no-live-model validation rule that also forbids accidental provider/network access during normal CI.
4. A basis-document hash and provenance matrix so the review can prove which contract/spec versions were applied.
5. A schema example corpus requirement, including valid and invalid examples for every worker schema.
6. A stricter evidence hash-closure rule so the manifest, review report, completion record, and command outputs agree.
7. A reviewer-independence rule requiring the review to distinguish document quality from implementation proof.
8. A freeze rule to stop further broad expansion unless trust boundaries or active runtime behavior change.
```

This v4 adds those controls and is the final frozen 10/10 review / DoD template.
---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **LLM Implementation Worker**.

Use this document after code is committed to determine whether the worker is complete, validated, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether Model Adapter integration works or is safely deferred
whether Tool / MCP Adapter integration works or is safely deferred
whether Policy / Capability Registry integration works
whether Security Sandbox integration works through the Tool Adapter boundary
whether Failure Taxonomy integration works
whether Governed Patch Execution handoff is safe or safely deferred
whether blocked actions fail closed
whether invalid tasks fail closed
whether prompt/context redaction works
whether prompt-injection attempts are blocked
whether repair loops are bounded
whether validation requests are routed safely
whether audit/evidence is written
whether evidence hashes are present
whether source mutation is prevented
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this document does not mean the implementation is done. The implementation is done only after validation commands and evidence checks pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because the LLM Implementation Worker is safety-critical. It interprets implementation requests, builds model-facing context, requests model output, proposes code changes, requests tool usage, and may trigger validation or repair flows.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if worker can request validation commands through tools
```

## 2.3 Conditional Standards

```text
Model Adapter Acceptance Criteria, if model calls are wired in this phase
Tool / MCP Adapter Acceptance Criteria, if worker can call tools in this phase
Governed Patch Execution Acceptance Criteria, if worker can hand off patch proposals
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The LLM Implementation Worker is safety-critical because it decides:

```text
how implementation tasks are interpreted
what context is sent to a model
which model profile is used
what prompts are constructed
what code changes are proposed
which tools are requested
whether patch proposals are produced
whether validation is requested
whether failures are repaired
whether evidence is written
```

It must not directly:

```text
mutate source files
run shell commands
apply patches
write Git commits
push to remote
open network connections directly
bypass Model Adapter
bypass Tool / MCP Adapter
bypass Policy / Capability Registry
bypass Security Sandbox
bypass Governed Patch Execution
```

The worker may propose changes, request safe tool calls, and hand off patch proposals. It must not become the component that directly mutates source, runs commands, talks to providers, or bypasses governance.

---

# 4. Review Target

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
[ ] every required command records command text, exit code, status, and summary
[ ] every command marked PASS has exit_code 0
[ ] every expected-failure negative test records the expected failure condition
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, bypass, call providers, request unsafe tools, or expose unsafe behavior. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, mutate, call a provider, request tools, hand off patches, or bypass policy/sandbox.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Model Adapter integration may be `DEFERRED SAFELY` only if:

```text
no model provider call can occur
no local model runtime can be invoked
model request functions return BLOCKED or DEFERRED SAFELY
prompt/context construction can still be validated without a model call
safe deferral is recorded in the deviation register
```

Tool Adapter integration may be `DEFERRED SAFELY` only if:

```text
no direct tool wrapper call occurs
no shell/filesystem/Git behavior occurs
worker tool-request functions return BLOCKED or DEFERRED SAFELY
safe deferral is recorded in the deviation register
```

Patch handoff may be `DEFERRED SAFELY` only if:

```text
patch proposals can be generated as non-applied artifacts or are blocked
no patch is applied
no source file is mutated
no rollback is performed
safe deferral is recorded in the deviation register
```

## 5.2 Active vs Simulated Integration Mode

The review must clearly label each integration proof as one of the following:

```text
ACTIVE_INTEGRATION:
  The real upstream Agent_X component is imported and used through its approved public API.

SIMULATED_INTEGRATION:
  A fake adapter is used only to prove worker behavior, fail-closed routing, schemas, and evidence.

DEFERRED_SAFELY:
  The integration entrypoint is absent or stubbed and cannot execute, mutate, call providers, call tools, or hand off patches.
```

Rules:

```text
ACTIVE_INTEGRATION may support DONE if all required checks pass.
SIMULATED_INTEGRATION may support DONE only for worker-layer correctness, not for claiming the upstream component itself is validated.
DEFERRED_SAFELY may support DONE only when the runtime path cannot perform the deferred behavior.
A review must not label simulated proof as active integration proof.
```

Blocking if:

```text
fake adapters are used but reported as real integration
real adapters are unavailable and the worker silently allows execution
integration status is ambiguous
```

## 5.3 Required Fake-Adapter Contract

If any upstream component is unavailable during tests, the fake adapter must be deterministic and must prove the same safety boundary expected from the real adapter.

Required fake adapters:

```text
FakeModelAdapter
FakeToolAdapter
FakePolicyRegistry
FakeSecuritySandbox
FakeFailureTaxonomy
FakePatchHandoff
```

Each fake adapter must support:

```text
ALLOW path
BLOCK path
INVALID path where applicable
FAIL path
timeout/error path where applicable
evidence reference emission
schema-valid request/result objects
no source mutation
no shell execution
no network/provider access
```

Blocking if:

```text
fake adapter always returns success
fake adapter lacks denied/failure cases
fake adapter mutates source or calls external services
fake adapter hides missing worker checks
```

## 5.4 No-Live-Model and No-Provider CI Rule

Normal validation must not require a live model, hosted provider, local model runtime, GPU, network, API key, MCP runtime, or interactive human input.

Required proof:

```text
[ ] tests pass with fake Model Adapter
[ ] no provider environment variable is required
[ ] no network socket or HTTP client is opened by the worker
[ ] model calls are represented as adapter requests, not direct provider calls
[ ] live-provider tests, if any, are isolated, optional, and excluded from required DONE validation
```

Blocking if:

```text
required tests need an API key
required tests need network
required tests need GPU or local model runtime
worker opens provider/network connection directly
```

## 5.5 Deterministic Fixture and Replay Rule

The worker review must prove deterministic behavior for validation fixtures.

Required behavior:

```text
[ ] fixed test task fixtures produce stable worker result shape
[ ] fake model outputs are fixture-controlled
[ ] repeated validation does not depend on wall-clock randomness except recorded timestamps/IDs
[ ] ID generation is test-controllable or evidence-tolerant
[ ] replayed task evidence remains attributable to the same task_id/session_id
```

Blocking if:

```text
same fixture randomly passes or fails
model output fixture cannot be reproduced
runtime artifacts become ambiguous after replay
```

---

# 6. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_implementation_worker_schemas.py
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

If `validate_llm_implementation_worker_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_llm_implementation_worker_schema_validation.py
```

No validation command may require:

```text
GPU
network
hosted model
LLM provider access
external MCP server
Git remote access
human interactive input
```

---

# 7. Expected Implementation Scope

## 7.1 Required Worker Package

Expected location:

```text
tools/agentx_evolve/workers/llm_implementation_worker/
```

Expected files:

```text
tools/agentx_evolve/workers/llm_implementation_worker/__init__.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_models.py
tools/agentx_evolve/workers/llm_implementation_worker/task_loader.py
tools/agentx_evolve/workers/llm_implementation_worker/context_builder_client.py
tools/agentx_evolve/workers/llm_implementation_worker/prompt_builder.py
tools/agentx_evolve/workers/llm_implementation_worker/model_client.py
tools/agentx_evolve/workers/llm_implementation_worker/tool_request_planner.py
tools/agentx_evolve/workers/llm_implementation_worker/patch_proposal_builder.py
tools/agentx_evolve/workers/llm_implementation_worker/validation_request_builder.py
tools/agentx_evolve/workers/llm_implementation_worker/repair_planner.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_dispatcher.py
tools/agentx_evolve/workers/llm_implementation_worker/worker_evidence.py
```

If names differ, the implementation must provide equivalent responsibilities and record the deviation.

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
llm_worker_task.schema.json
llm_worker_context_request.schema.json
llm_worker_prompt_plan.schema.json
llm_worker_model_request.schema.json
llm_worker_model_result.schema.json
llm_worker_tool_request.schema.json
llm_worker_patch_proposal.schema.json
llm_worker_validation_request.schema.json
llm_worker_repair_plan.schema.json
llm_worker_result.schema.json
llm_worker_audit.schema.json
llm_worker_evidence_manifest.schema.json
llm_worker_review_report.schema.json
llm_worker_completion_record.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_llm_worker_models.py
test_llm_worker_task_schema.py
test_llm_worker_prompt_builder.py
test_llm_worker_model_adapter_integration.py
test_llm_worker_tool_adapter_integration.py
test_llm_worker_policy_integration.py
test_llm_worker_sandbox_integration.py
test_llm_worker_failure_taxonomy_integration.py
test_llm_worker_patch_handoff.py
test_llm_worker_blocked_actions.py
test_llm_worker_invalid_tasks.py
test_llm_worker_evidence.py
test_llm_worker_negative_cases.py
test_llm_worker_repair_limits.py
test_llm_worker_prompt_injection.py
test_llm_worker_model_output_parser.py
test_llm_worker_context_provenance.py
test_llm_worker_idempotency.py
test_llm_worker_concurrency_locks.py
test_llm_worker_budget_limits.py
test_llm_worker_tool_request_allowlist.py
test_llm_implementation_worker_schema_validation.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/implementation_worker/
```

Expected artifacts:

```text
llm_worker_task_history.jsonl
llm_worker_result_history.jsonl
llm_worker_blocked_action_history.jsonl
llm_worker_invalid_task_history.jsonl
latest_llm_worker_task.json
latest_llm_worker_result.json
llm_worker_evidence_manifest.json
llm_worker_review_report.json
llm_worker_completion_record.json
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Worker package location | `tools/agentx_evolve/workers/llm_implementation_worker/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Worker schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Worker tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task loading | valid tasks accepted, invalid tasks rejected | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt/context handling | context is structured, bounded, redacted, and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt-injection handling | instructions attempting bypass are blocked or neutralized | PASS / PARTIAL / FAIL / NOT CHECKED |
| Instruction hierarchy | system/developer/policy/tool boundaries outrank task/model text | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context provenance and hashing | every context chunk has source, scope, reason, and hash/provenance metadata | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model output parsing | model output is schema-gated before any tool, patch, validation, or repair use | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool request allowlist | worker can request only approved Tool Adapter names/effects | PASS / PARTIAL / FAIL / NOT CHECKED |
| Budget limits | token/context/output/retry/timeout/model-call limits enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Idempotency | repeated same task does not duplicate unsafe side effects or evidence ambiguity | PASS / PARTIAL / FAIL / NOT CHECKED |
| Concurrency locks | concurrent worker runs cannot corrupt runtime artifacts or repair sessions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model Adapter integration | model calls go through Model Adapter only | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Tool Adapter integration | tool requests go through Tool / MCP Adapter only | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Policy integration | worker actions checked before request/execution | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox integration | source/path effects require sandbox through tools | PASS / PARTIAL / FAIL / NOT CHECKED |
| Failure Taxonomy integration | failures map to standard classes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch handoff | patch proposals handed to Governed Patch Execution only | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Repair loop limits | repair attempts are bounded and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Blocked actions | forbidden actions return BLOCKED with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid tasks | malformed/unsafe tasks return INVALID with evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence | JSONL + latest artifacts + manifest + report written safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | final evidence artifacts have SHA-256 hashes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | worker does not directly mutate source | PASS / PARTIAL / FAIL / NOT CHECKED |
| Command safety | worker does not directly run shell commands | PASS / PARTIAL / FAIL / NOT CHECKED |
| Network safety | worker does not directly open network/provider connections | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Valid task accepted | `task_loader.py` | `test_llm_worker_task_schema.py` | task history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Invalid task blocked | `task_loader.py` | `test_llm_worker_invalid_tasks.py` | invalid task history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context bounded/redacted | `context_builder_client.py` | `test_llm_worker_prompt_builder.py` | task/result evidence | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt plan structured | `prompt_builder.py` | `test_llm_worker_prompt_builder.py` | latest worker task/result | PASS / PARTIAL / FAIL / NOT CHECKED |
| Prompt-injection blocked | `prompt_builder.py` / `task_loader.py` | `test_llm_worker_prompt_injection.py` | blocked action history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model Adapter boundary | `model_client.py` | `test_llm_worker_model_adapter_integration.py` | model refs in result | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Tool Adapter boundary | `tool_request_planner.py` | `test_llm_worker_tool_adapter_integration.py` | tool refs in result | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Patch proposal only | `patch_proposal_builder.py` | `test_llm_worker_patch_handoff.py` | patch proposal refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Validation request safe | `validation_request_builder.py` | `test_llm_worker_blocked_actions.py` | tool request refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Repair loop bounded | `repair_planner.py` | `test_llm_worker_repair_limits.py` | repair plan refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Worker dispatcher fail-closed | `worker_dispatcher.py` | `test_llm_worker_negative_cases.py` | worker result history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence writer | `worker_evidence.py` | `test_llm_worker_evidence.py` | manifest/report/completion | PASS / PARTIAL / FAIL / NOT CHECKED |
| Failure classes | worker modules | `test_llm_worker_failure_taxonomy_integration.py` | failure refs | PASS / PARTIAL / FAIL / NOT CHECKED |

## 9.1 Basis Document and Contract Hash Matrix

The review must record the exact contract/spec/review documents used to judge the implementation.

| Basis artifact | Expected identifier | Version/hash required | Status |
|---|---|---|---|
| Controlling contract | `LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT` | version and SHA-256 | PASS / FAIL / NOT CHECKED |
| Implementation spec | `LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC` | version and SHA-256 | PASS / FAIL / NOT CHECKED |
| Review / DoD template | `LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v4` | version and SHA-256 | PASS / FAIL / NOT CHECKED |
| Related Model Adapter contract | if active model calls are wired | version and SHA-256 or DEFERRED SAFELY | PASS / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Related Tool / MCP Adapter contract | if active tool calls are wired | version and SHA-256 or DEFERRED SAFELY | PASS / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Related Patch Execution contract | if patch handoff is wired | version and SHA-256 or DEFERRED SAFELY | PASS / FAIL / NOT CHECKED / DEFERRED SAFELY |

Blocking if:

```text
review cannot identify which contract/spec version was applied
basis document hash is missing for final DONE
implementation is judged against stale or mixed requirements without a deviation entry
```

---

# 10. What Exists Checklist

## 10.1 Worker Package Files

```text
[ ] tools/agentx_evolve/workers/llm_implementation_worker/__init__.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/worker_models.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/task_loader.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/context_builder_client.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/prompt_builder.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/model_client.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/tool_request_planner.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/patch_proposal_builder.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/validation_request_builder.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/repair_planner.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/worker_dispatcher.py
[ ] tools/agentx_evolve/workers/llm_implementation_worker/worker_evidence.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] llm_worker_task.schema.json
[ ] llm_worker_context_request.schema.json
[ ] llm_worker_prompt_plan.schema.json
[ ] llm_worker_model_request.schema.json
[ ] llm_worker_model_result.schema.json
[ ] llm_worker_tool_request.schema.json
[ ] llm_worker_patch_proposal.schema.json
[ ] llm_worker_validation_request.schema.json
[ ] llm_worker_repair_plan.schema.json
[ ] llm_worker_result.schema.json
[ ] llm_worker_audit.schema.json
[ ] llm_worker_evidence_manifest.schema.json
[ ] llm_worker_review_report.schema.json
[ ] llm_worker_completion_record.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_llm_worker_models.py
[ ] test_llm_worker_task_schema.py
[ ] test_llm_worker_prompt_builder.py
[ ] test_llm_worker_model_adapter_integration.py
[ ] test_llm_worker_tool_adapter_integration.py
[ ] test_llm_worker_policy_integration.py
[ ] test_llm_worker_sandbox_integration.py
[ ] test_llm_worker_failure_taxonomy_integration.py
[ ] test_llm_worker_patch_handoff.py
[ ] test_llm_worker_blocked_actions.py
[ ] test_llm_worker_invalid_tasks.py
[ ] test_llm_worker_evidence.py
[ ] test_llm_worker_negative_cases.py
[ ] test_llm_worker_repair_limits.py
[ ] test_llm_worker_prompt_injection.py
[ ] test_llm_worker_model_output_parser.py
[ ] test_llm_worker_context_provenance.py
[ ] test_llm_worker_idempotency.py
[ ] test_llm_worker_concurrency_locks.py
[ ] test_llm_worker_budget_limits.py
[ ] test_llm_worker_tool_request_allowlist.py
[ ] test_llm_implementation_worker_schema_validation.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 11. Validation Commands

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_implementation_worker_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

If unrelated future-layer tests exist in the directory, the review must also record a scoped LLM Implementation Worker pytest command covering only relevant tests:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_llm_worker_models.py \
  tools/agentx_evolve/tests/test_llm_worker_task_schema.py \
  tools/agentx_evolve/tests/test_llm_worker_prompt_builder.py \
  tools/agentx_evolve/tests/test_llm_worker_model_adapter_integration.py \
  tools/agentx_evolve/tests/test_llm_worker_tool_adapter_integration.py \
  tools/agentx_evolve/tests/test_llm_worker_policy_integration.py \
  tools/agentx_evolve/tests/test_llm_worker_sandbox_integration.py \
  tools/agentx_evolve/tests/test_llm_worker_failure_taxonomy_integration.py \
  tools/agentx_evolve/tests/test_llm_worker_patch_handoff.py \
  tools/agentx_evolve/tests/test_llm_worker_blocked_actions.py \
  tools/agentx_evolve/tests/test_llm_worker_invalid_tasks.py \
  tools/agentx_evolve/tests/test_llm_worker_evidence.py \
  tools/agentx_evolve/tests/test_llm_worker_negative_cases.py \
  tools/agentx_evolve/tests/test_llm_worker_repair_limits.py \
  tools/agentx_evolve/tests/test_llm_worker_prompt_injection.py \
  tools/agentx_evolve/tests/test_llm_worker_model_output_parser.py \
  tools/agentx_evolve/tests/test_llm_worker_context_provenance.py \
  tools/agentx_evolve/tests/test_llm_worker_idempotency.py \
  tools/agentx_evolve/tests/test_llm_worker_concurrency_locks.py \
  tools/agentx_evolve/tests/test_llm_worker_budget_limits.py \
  tools/agentx_evolve/tests/test_llm_worker_tool_request_allowlist.py \
  tools/agentx_evolve/tests/test_llm_implementation_worker_schema_validation.py
```

---

# 12. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any LLM Implementation Worker Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output stored>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required worker, schema, integration, blocked-action, invalid-task, evidence, repair-limit, prompt-injection, or negative test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_implementation_worker_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_llm_implementation_worker_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256 if output stored>
```

Required schema tests:

```text
llm worker task schema accepts valid task
llm worker task schema rejects missing task_id
llm worker task schema rejects unsafe direct mutation request
context request schema accepts bounded context request
context request schema rejects unbounded context request
prompt plan schema accepts valid prompt plan
prompt plan schema rejects unsafe bypass instructions as authority
model request schema accepts valid Model Adapter request
model result schema accepts valid Model Adapter result reference
tool request schema accepts valid Tool Adapter request
patch proposal schema accepts valid non-applied patch proposal
validation request schema accepts valid validation request
repair plan schema accepts valid bounded repair plan
worker result schema accepts SUCCESS, BLOCKED, FAILED, and INVALID outcomes
audit schema accepts valid audit event
evidence manifest schema accepts valid evidence manifest
review report schema accepts valid review report
completion record schema accepts final completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid tasks are accepted
unsafe direct-mutation requests are accepted
worker result schema cannot represent BLOCKED or INVALID outcomes
patch proposal schema cannot represent non-applied proposals
repair plan schema cannot represent bounded attempts
evidence manifest cannot be schema-validated
review report cannot be schema-validated
completion record cannot be schema-validated
schema validation exit code is missing
```

## 14.1 Schema Example Corpus Requirement

The implementation must include or generate a schema example corpus for review.

Required valid examples:

```text
valid_llm_worker_task
valid_llm_worker_context_request
valid_llm_worker_prompt_plan
valid_llm_worker_model_request
valid_llm_worker_model_result
valid_llm_worker_tool_request
valid_llm_worker_patch_proposal_non_applied
valid_llm_worker_validation_request
valid_llm_worker_repair_plan_bounded
valid_llm_worker_result_success
valid_llm_worker_result_blocked
valid_llm_worker_result_invalid
valid_llm_worker_audit
valid_llm_worker_evidence_manifest
valid_llm_worker_review_report
valid_llm_worker_completion_record
```

Required invalid examples:

```text
missing task_id
unsafe direct source mutation request
unsafe direct shell request
unbounded context request
unknown model profile
unknown tool name
forbidden tool effect
applied patch proposal inside worker
repair plan without max_attempts
worker result with unknown status
manifest missing reviewed commit
completion record missing final decision
```

Blocking if:

```text
schemas are listed but not exercised by valid and invalid examples
schema tests only verify happy paths
unsafe examples are accepted
```

---

# 15. Model Adapter Integration Result

The worker must use the Model Adapter for model calls. It must not call hosted providers, local runtimes, HTTP clients, or model libraries directly unless this is explicitly the Model Adapter boundary.

Required behavior:

```text
[ ] model profile selection goes through Model Adapter or approved model profile registry
[ ] model request is schema-valid before dispatch
[ ] model result is schema-valid before use
[ ] model call failure maps to standard failure class
[ ] model output is treated as untrusted until validated
[ ] model output cannot directly mutate source
[ ] provider/network access is not opened directly by worker
[ ] prompt/context payload is bounded and redacted
[ ] model request and result references are evidenced
[ ] safe fake Model Adapter is used for tests if real adapter is unavailable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
worker directly calls provider/network outside Model Adapter
worker treats model output as executable authority
worker uses model output to mutate source directly
model request/result evidence is missing for an active model path
```

---

# 16. Tool Adapter Integration Result

The worker must use the Tool / MCP Adapter for tool requests. It must not call filesystem, shell, Git, validation, or patch tools directly.

Required behavior:

```text
[ ] tool requests are represented as schema-valid worker tool requests
[ ] worker requests tools through Tool / MCP Adapter
[ ] worker does not call tool wrappers directly outside approved dispatcher
[ ] worker does not bypass Tool Adapter policy checks
[ ] worker does not bypass Tool Adapter sandbox checks
[ ] tool result is schema-valid before worker uses it
[ ] failed/blocked tool result halts or redirects safely
[ ] tool request/result references are evidenced
[ ] safe fake Tool Adapter is used for tests if real adapter is unavailable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
worker directly runs shell
worker directly reads/writes source files
worker directly calls Git write behavior
worker bypasses Tool Adapter dispatcher
```

---

# 17. Policy Integration Result

The worker must respect Policy / Capability Registry decisions before model calls, tool requests, patch handoff, validation requests, and repair attempts.

Required behavior:

```text
[ ] implementation task is checked against policy
[ ] selected model profile is policy-permitted
[ ] requested tool effects are policy-checked
[ ] patch proposal handoff is policy-checked
[ ] validation request is policy-checked
[ ] repair loop limits are policy-checked
[ ] missing policy fails closed or uses restrictive fallback
[ ] policy-denied action returns BLOCKED with evidence
[ ] policy decision references are propagated into worker result evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
policy missing results in ALLOW for non-trivial action
policy-denied action proceeds
worker selects unapproved model profile
worker requests unapproved tool effects
```

---

# 18. Sandbox Integration Result

The worker must not perform direct filesystem/path/command actions. Any such effect must go through Tool Adapter and Security Sandbox.

Required behavior:

```text
[ ] worker does not call open/write/path mutation directly for source files
[ ] worker does not run subprocess directly
[ ] worker does not apply patches directly
[ ] worker does not write Git state directly
[ ] any path/file/command request is routed through Tool Adapter
[ ] sandbox-denied request returns BLOCKED or FAILED safely
[ ] sandbox decision references are propagated where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
worker mutates source directly
worker executes subprocess directly
worker bypasses sandbox for path/file/command effects
```

---

# 19. Failure Taxonomy Integration Result

Every failed, blocked, invalid, timed-out, or unsafe worker outcome must map to a standard failure class.

Required failure classes include:

```text
LLM_WORKER_TASK_INVALID
LLM_WORKER_POLICY_DENIED
LLM_WORKER_MODEL_DENIED
LLM_WORKER_MODEL_FAILED
LLM_WORKER_TOOL_DENIED
LLM_WORKER_TOOL_FAILED
LLM_WORKER_PATCH_HANDOFF_DENIED
LLM_WORKER_PATCH_HANDOFF_FAILED
LLM_WORKER_VALIDATION_DENIED
LLM_WORKER_REPAIR_LIMIT_EXCEEDED
LLM_WORKER_OUTPUT_SCHEMA_INVALID
LLM_WORKER_SOURCE_MUTATION_BLOCKED
LLM_WORKER_PROMPT_INJECTION_BLOCKED
UNKNOWN_LLM_WORKER_FAILURE
```

Required behavior:

```text
[ ] invalid tasks have failure_class
[ ] blocked actions have failure_class
[ ] prompt-injection attempts have failure_class
[ ] model failures have failure_class
[ ] tool failures have failure_class
[ ] patch handoff failures have failure_class
[ ] validation request failures have failure_class
[ ] repair limit failures have failure_class
[ ] unknown exceptions map to UNKNOWN_LLM_WORKER_FAILURE
[ ] failure records are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
failures are unclassified
exceptions escape without schema-valid result
blocked/invalid outcomes lack evidence
```

---

# 20. Patch Handoff Coverage

The worker may generate patch proposals, but must not apply them directly.

Required behavior:

```text
[ ] patch proposal is schema-valid
[ ] patch proposal is non-applied by default
[ ] patch proposal includes target files, summary, risk notes, and evidence refs
[ ] patch proposal excludes direct source mutation
[ ] patch handoff goes through Governed Patch Execution
[ ] patch handoff requires policy approval
[ ] patch handoff requires sandbox/governance where applicable
[ ] patch apply is not performed inside worker
[ ] rollback is not performed inside worker
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
worker applies patch directly
worker writes source directly
worker bypasses Governed Patch Execution
worker emits unstructured patch proposal that cannot be reviewed
```

---

# 21. Validation Request and Repair Loop Coverage

The worker may request validation and repair, but must not directly execute validation commands or run unbounded repair loops.

Required behavior:

```text
[ ] validation request is schema-valid
[ ] validation request goes through Tool / MCP Adapter or approved validation interface
[ ] validation command is allowlisted by policy/tool layer
[ ] validation result is schema-valid before use
[ ] repair plan is schema-valid
[ ] repair loop has max_attempts
[ ] repair loop has stop conditions
[ ] repair loop records each attempt
[ ] repair loop stops on policy denial
[ ] repair loop stops on repeated identical failure unless policy allows retry
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
worker directly executes validation command
repair loop is unbounded
repair loop bypasses policy after failure
repair loop mutates source directly
```

---

# 22. Prompt / Context Safety Coverage

The worker may construct prompts and model context, but must treat all task text, repository text, model output, and tool output as untrusted data.

Required behavior:

```text
[ ] prompt plan separates system/developer/task/context sections
[ ] context payload has size bounds
[ ] context payload has source provenance
[ ] context payload excludes secrets
[ ] context payload excludes unneeded raw source dumps
[ ] prompt-injection instructions cannot override policy/sandbox/tool rules
[ ] model output is parsed into schema-valid structures before use
[ ] model output cannot become shell/code execution authority
[ ] prompt and context evidence is summarized or redacted before durable logging
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
prompt-injection instruction can bypass policy
unbounded raw context is sent or logged
secrets are included in prompt/context evidence
model output is used as direct execution authority
```

---

## 22.1 Instruction Hierarchy and Prompt-Injection Precedence

The review must prove that the worker enforces instruction hierarchy. Task text, repository text, retrieved context, tool output, model output, comments in source files, and generated patches are untrusted data.

Required behavior:

```text
[ ] system/developer/policy constraints cannot be overridden by task text
[ ] repository text cannot override policy/sandbox/tool boundaries
[ ] model output cannot redefine worker permissions
[ ] model output cannot authorize direct source mutation
[ ] model output cannot authorize direct shell, Git, network, or provider calls
[ ] prompt-injection attempts are recorded as blocked/invalid when they request boundary bypass
[ ] prompt-injection handling is covered by explicit negative tests
```

Blocking if:

```text
any untrusted text can override policy, sandbox, adapter boundaries, or evidence rules
```

## 22.2 Context Provenance, Hashing, and Prompt Versioning

The review must prove that model-facing context is bounded, explainable, and reproducible.

Required behavior:

```text
[ ] every context item has source_path or source_ref
[ ] every context item records why it was included
[ ] every context item records scope and extraction method
[ ] every context item has content hash or source artifact hash where practical
[ ] prompt template has prompt_template_id
[ ] prompt template has prompt_template_version
[ ] prompt plan records context budget and truncation decisions
[ ] prompt plan records redaction decisions
[ ] prompt/context evidence is summarized, not raw-unbounded
```

Blocking if:

```text
model-facing context cannot be traced back to source/provenance
prompt template version is missing for active model path
unbounded context is passed or durably logged
```

## 22.3 Model Output Parser and Schema-Gating Coverage

The review must prove that model output is not trusted until parsed and validated.

Required behavior:

```text
[ ] raw model output is stored only as bounded/redacted evidence or safe artifact
[ ] model output is parsed into a schema-valid worker result, patch proposal, tool request, validation request, or repair plan
[ ] malformed model output returns FAILED or INVALID with failure_class
[ ] model output cannot trigger tool execution before Tool Adapter request validation
[ ] model output cannot trigger patch handoff before patch proposal validation
[ ] model output cannot trigger validation request before validation request schema checks
[ ] parsed output records parser version
[ ] parsed output records model result reference
```

Blocking if:

```text
raw model text is treated as executable instruction
malformed model output proceeds to tool, patch, validation, or repair flow
```

## 22.4 Tool-Request Allowlist Coverage

The review must prove that worker-requested tools are limited to allowed Tool Adapter names and effects.

Required behavior:

```text
[ ] worker has an explicit allowed_tool_names list or policy-derived allowlist
[ ] worker has an explicit allowed_effects list or policy-derived effect set
[ ] worker cannot request raw shell tools directly
[ ] worker cannot request Git write tools directly
[ ] worker cannot request network tools directly
[ ] worker cannot request patch_apply_guarded unless Governed Patch Execution handoff allows it
[ ] forbidden tool request returns BLOCKED with evidence
[ ] tool request allowlist is tested with negative cases
```

Blocking if:

```text
worker can ask for arbitrary tool names/effects
worker can route around Tool Adapter policy by selecting unsafe tool names
```

## 22.5 Budget, Timeout, Retry, and Resource Limit Coverage

The review must prove that the worker is bounded.

Required behavior:

```text
[ ] max_context_chars or max_context_tokens is enforced
[ ] max_prompt_chars or max_prompt_tokens is enforced
[ ] max_model_output_chars or max_model_output_tokens is enforced
[ ] max_model_calls_per_task is enforced
[ ] max_tool_requests_per_task is enforced
[ ] max_validation_requests_per_task is enforced
[ ] max_repair_attempts is enforced
[ ] timeout_seconds is enforced or delegated to adapters
[ ] retry policy is explicit and defaults to conservative
[ ] budget exhaustion returns schema-valid BLOCKED or FAILED result
```

Blocking if:

```text
worker can loop indefinitely
worker can request unbounded model/tool/validation calls
worker can emit unbounded prompt/context/model output evidence
```

## 22.6 Idempotency and Concurrency Coverage

The review must prove that repeated or concurrent worker runs do not corrupt evidence or create ambiguous handoffs.

Required behavior:

```text
[ ] worker task has stable task_id or derived idempotency key
[ ] repeated same task records separate evidence or safely reuses prior result with provenance
[ ] duplicate patch proposal handoffs are detected or clearly versioned
[ ] runtime artifact writes are atomic where applicable
[ ] concurrent runs cannot corrupt JSONL/latest artifacts
[ ] repair sessions have session_id and attempt index
[ ] concurrent repair sessions cannot overwrite each other
[ ] lock failure returns schema-valid BLOCKED or FAILED result
```

Blocking if:

```text
concurrent runs can corrupt evidence
repeated tasks can duplicate unsafe handoff without detection
latest artifacts are written non-atomically
```

---

# 23. Blocked Action Coverage

Required blocked-action behavior:

```text
[ ] direct source mutation request returns BLOCKED
[ ] direct shell request returns BLOCKED
[ ] direct Git write request returns BLOCKED
[ ] direct network/provider request returns BLOCKED
[ ] direct patch apply request returns BLOCKED
[ ] direct validation command execution returns BLOCKED unless routed through Tool Adapter
[ ] policy-denied model profile returns BLOCKED
[ ] policy-denied tool request returns BLOCKED
[ ] missing required dependency returns BLOCKED or DEFERRED SAFELY
[ ] blocked actions write evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
blocked action executes
blocked action silently does nothing without evidence
blocked action raises unhandled exception instead of schema-valid result
```

---

# 24. Invalid Task Coverage

Required invalid-task behavior:

```text
[ ] missing task_id returns INVALID
[ ] missing task objective returns INVALID
[ ] malformed task payload returns INVALID
[ ] unknown task type returns INVALID or BLOCKED
[ ] unsafe direct-mutation instruction returns BLOCKED or INVALID
[ ] prompt-injection instruction attempting to bypass policy returns BLOCKED or INVALID
[ ] invalid task result validates against worker result schema
[ ] invalid task writes to invalid task history
[ ] invalid task does not call model
[ ] invalid task does not request tools
[ ] invalid task does not produce patch handoff
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
invalid task calls model
invalid task requests tools
invalid task generates patch handoff
invalid task lacks evidence
```

---

# 25. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] missing task_id -> INVALID
[ ] malformed task payload -> INVALID
[ ] prompt injection asking to ignore policy -> BLOCKED or INVALID
[ ] task requests direct source write -> BLOCKED
[ ] task requests direct shell -> BLOCKED
[ ] task requests direct Git write -> BLOCKED
[ ] task requests direct network/provider call -> BLOCKED
[ ] model output contains shell command -> not executed
[ ] model output contains patch text -> proposal only, not applied
[ ] model output asks to bypass Tool Adapter -> BLOCKED
[ ] model output asks to bypass Model Adapter -> BLOCKED
[ ] policy-denied model profile -> BLOCKED
[ ] policy-denied tool effect -> BLOCKED
[ ] missing Model Adapter with active model path -> BLOCKED or DEFERRED SAFELY
[ ] missing Tool Adapter with active tool path -> BLOCKED or DEFERRED SAFELY
[ ] missing Governed Patch Execution with patch handoff path -> BLOCKED or DEFERRED SAFELY
[ ] repair loop max attempts exceeded -> BLOCKED/FAILED with failure_class
[ ] secret-like payload -> redacted in evidence
[ ] malformed model output -> INVALID/FAILED before tool or patch handoff
[ ] arbitrary tool name requested by model -> BLOCKED
[ ] repeated identical task -> idempotent evidence behavior
[ ] concurrent worker writes -> no corrupted runtime artifact
[ ] model-call budget exceeded -> BLOCKED/FAILED with failure_class
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 26. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] llm_worker_task_history.jsonl is written
[ ] llm_worker_result_history.jsonl is written
[ ] llm_worker_blocked_action_history.jsonl is written for blocked actions
[ ] llm_worker_invalid_task_history.jsonl is written for invalid tasks
[ ] latest_llm_worker_task.json is written atomically
[ ] latest_llm_worker_result.json is written atomically
[ ] llm_worker_evidence_manifest.json is written
[ ] llm_worker_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes command text, exit codes, statuses, and summaries
[ ] evidence includes schema validation summary
[ ] evidence includes model request/result refs where applicable
[ ] evidence includes tool request/result refs where applicable
[ ] evidence includes patch proposal/handoff refs where applicable
[ ] evidence includes repair attempt refs where applicable
[ ] evidence includes prompt_template_id and prompt_template_version where model path is active
[ ] evidence includes context source/provenance/hash refs where applicable
[ ] evidence includes parser version for parsed model outputs
[ ] evidence includes idempotency key and worker session_id where applicable
[ ] evidence includes SHA-256 hashes for final artifacts
[ ] secrets are redacted before logging
[ ] prompt/context payloads are bounded and redacted
[ ] raw source content is not durably logged unless explicitly approved and redacted
[ ] schema-invalid result does not replace valid latest result
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
worker tasks are not logged
worker results are not logged
blocked/invalid outcomes are not evidenced
secrets are logged
raw unbounded prompt/context is logged
required evidence lacks reviewed commit reference
required evidence hashes are missing for DONE
```

---

# 27. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/implementation_worker/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by tests
worker directly modifies source
worker writes unapproved files outside runtime artifact paths
runtime artifacts are written outside approved runtime roots without recorded deviation
```

---

# 28. Evidence Manifest

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
      "command": "PYTHONPATH=tools python -m compileall tools/agentx_evolve",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>",
      "output_sha256": "<sha256>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
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
  "known_expected_runtime_artifacts": [],
  "model_adapter_status": "PASS_OR_DEFERRED_SAFELY",
  "tool_adapter_status": "PASS_OR_DEFERRED_SAFELY",
  "policy_integration_status": "PASS",
  "sandbox_integration_status": "PASS",
  "failure_taxonomy_status": "PASS",
  "patch_handoff_status": "PASS_OR_DEFERRED_SAFELY",
  "blocked_invalid_status": "PASS",
  "prompt_context_redaction_status": "PASS",
  "repair_limit_status": "PASS",
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "context_provenance_status": "PASS",
  "model_output_parser_status": "PASS_OR_DEFERRED_SAFELY",
  "tool_request_allowlist_status": "PASS_OR_DEFERRED_SAFELY",
  "budget_limit_status": "PASS",
  "idempotency_status": "PASS",
  "concurrency_lock_status": "PASS",
  "deviation_register": [],
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
llm_worker_evidence_manifest.json
llm_worker_review_report.json
llm_worker_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_llm_worker_task.json, if used by the review
latest_llm_worker_result.json, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

---

# 29. Review Report Artifact

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
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/implementation_worker/llm_worker_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/implementation_worker/llm_worker_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/implementation_worker/llm_worker_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is invalid if it does not identify the exact reviewed commit or if it lacks command exit codes.

## 29.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

## 29.2 Evidence Hash-Closure Rule

The evidence manifest, review report, completion record, command-output artifacts, and final runtime evidence referenced by the review must form a closed evidence set.

Required behavior:

```text
[ ] evidence manifest lists every evidence file used by the review
[ ] review report references the evidence manifest path and SHA-256
[ ] completion record references the evidence manifest path and SHA-256
[ ] command output artifacts have SHA-256 hashes if stored
[ ] JSONL evidence histories used by the review have SHA-256 hashes
[ ] latest task/result artifacts used by the review have SHA-256 hashes
[ ] basis documents have SHA-256 hashes or immutable commit references
[ ] hash calculation uses Python standard library hashlib if no project helper exists
```

Blocking if:

```text
review cites evidence not listed in the manifest
manifest/report/completion hashes disagree
basis documents cannot be tied to the reviewed implementation
```

## 29.3 Reviewer Independence and Reproducibility Rule

The reviewer must not rely on this document's self-rating as proof of implementation readiness.

Required behavior:

```text
[ ] reviewer records exact commit, branch, environment, and commands
[ ] reviewer records active vs simulated vs deferred integration mode
[ ] reviewer records any fake adapters used
[ ] reviewer records exact evidence paths and hashes
[ ] another reviewer can rerun the same commands from the same commit
```

Blocking if:

```text
implementation is marked DONE because the review template is rated 10/10
commands or evidence are not reproducible
fake adapters are not disclosed
```

---

# 30. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Model Adapter | Tool Adapter | Policy | Sandbox | Failure Taxonomy | Patch Handoff | Evidence | Schema | Runtime Artifact Boundary | Other>
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
HIGH items cannot be accepted for DONE unless the review proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/implementation_worker/` require a deviation entry.
Model Adapter deferral requires a deviation entry.
Tool Adapter deferral requires a deviation entry.
Patch handoff deferral requires a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 31. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
model adapter integration:
tool adapter integration:
policy integration:
sandbox integration:
failure taxonomy integration:
patch handoff coverage:
validation request coverage:
repair loop coverage:
prompt/context safety:
prompt-injection handling:
blocked action coverage:
invalid task coverage:
negative tests:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
source mutation check:
completion record:
```

---

# 32. What Failed

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

# 33. Issue Severity Classification

## 33.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
worker directly mutates source
worker directly executes shell
worker directly applies patch
worker writes Git state
worker opens network/provider connection directly
worker bypasses Model Adapter
worker bypasses Tool / MCP Adapter
worker bypasses Policy / Capability Registry
worker bypasses Security Sandbox
worker bypasses Governed Patch Execution
invalid task calls model or tools
blocked action executes
policy-denied action proceeds
model output directly mutates source
model output is treated as execution authority
prompt-injection bypasses policy/sandbox/tool boundaries
patch proposal is applied inside worker
repair loop is unbounded
model output parser is bypassed
worker can request arbitrary tool names or effects
worker lacks active budget limits
worker concurrency corrupts evidence
validation command is executed directly by worker
secrets are logged
raw unbounded prompt/context is logged
worker tasks/results lack evidence
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 33.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
partial Model Adapter integration
partial Tool Adapter integration
partial Failure Taxonomy mapping
patch handoff deferred without explicit deviation entry
model calls deferred without explicit deviation entry
tool calls deferred without explicit deviation entry
some expected worker files missing but behavior exists elsewhere
runtime artifact boundary exception lacks justification
review environment not recorded
prompt/context redaction is incomplete
repair loop limits are incomplete
```

## 33.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled worker functions
model calls intentionally deferred with safe-deferral proof
tool calls intentionally deferred with safe-deferral proof
patch handoff intentionally deferred with safe-deferral proof
additional future-layer tests exist outside scoped worker suite
```

---

# 34. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Worker, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Model / Tool Adapter boundaries | 1.0 | Model calls and tool requests go only through approved adapters or are safely deferred. |
| Policy / Sandbox / Failure integration | 1.0 | Policy checks, sandbox routing, and failure classes are enforced. |
| Patch / validation / repair safety | 1.0 | Patch proposals are non-applied, validation is routed safely, and repair loops are bounded. |
| Parser/provenance/idempotency/budget controls | included across categories | Model output is schema-gated, context is provenance-backed, retries are bounded, and concurrent runs are safe. |
| Blocked / invalid / prompt-injection behavior | 1.0 | Unsafe tasks/actions fail closed with schema-valid evidence. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, completion record. |
| Source-mutation and side-effect safety | 1.0 | No direct source mutation, shell, Git write, patch apply, or direct provider/network call. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for implementation generation
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
worker directly mutates source caps score at 4.0
worker directly executes shell caps score at 4.0
worker directly applies patch caps score at 4.0
worker directly opens provider/network connection caps score at 4.0
adapter bypass caps score at 4.0
policy or sandbox bypass caps score at 4.0
prompt-injection bypass caps score at 4.0
unbounded repair loop caps score at 6.0
missing active budget limits caps score at 7.0
missing model output parser/schema gate caps score at 7.0
missing tool-request allowlist caps score at 7.0
evidence corruption under concurrency caps score at 7.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 35. GO / NO-GO Rules

## 35.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
worker package exists or equivalent deviation is accepted
required schemas exist
required tests exist
task loading tests pass
model adapter integration passes or is deferred safely
tool adapter integration passes or is deferred safely
policy integration passes
sandbox integration passes
failure taxonomy integration passes
patch handoff passes or is deferred safely
validation request tests pass or are safely deferred
repair loop tests pass
prompt/context safety tests pass
prompt-injection tests pass
context provenance/hash tests pass
model output parser/schema-gating tests pass or model path is deferred safely
tool-request allowlist tests pass or tool path is deferred safely
budget limit tests pass
idempotency tests pass
concurrency/lock tests pass
blocked action tests pass
invalid task tests pass
negative tests pass
audit/evidence tests pass
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

## 35.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
worker directly mutates source
worker directly executes shell
worker directly applies patches
worker writes Git state
worker opens network/provider connection directly
worker bypasses Model Adapter
worker bypasses Tool / MCP Adapter
worker bypasses Policy / Capability Registry
worker bypasses Security Sandbox
worker bypasses Governed Patch Execution
invalid task calls model/tools
blocked action executes
policy-denied action proceeds
model output is treated as direct execution authority
prompt injection bypasses policy/sandbox/tool boundaries
patch proposal is applied inside worker
validation command is executed directly by worker
repair loop is unbounded
tool calls/results lack evidence
worker evidence is missing
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
fix task validation
fix prompt/context bounds
fix prompt-injection filtering/neutralization
fix model adapter request formatting
fix tool adapter request formatting
fix policy checks
fix sandbox routing through tools
fix patch handoff formatting
fix validation request formatting
fix repair loop limits
fix blocked-action result formatting
fix invalid-task result formatting
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix failure_class mapping
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not let worker directly mutate source to pass tests
do not let worker directly run shell to pass tests
do not let worker directly apply patches
do not let worker write Git state
do not let worker call model providers directly
do not bypass Model Adapter
do not bypass Tool / MCP Adapter
do not bypass Policy / Capability Registry
do not bypass Security Sandbox
do not bypass Governed Patch Execution
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not log raw unbounded prompt/context
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 37. Definition of Done

The LLM Implementation Worker is done when it can safely transform an implementation task into validated model/tool/patch-handoff outputs without direct unsafe side effects.

It must prove:

```text
all target files exist or explicit safe deviation is documented
all schemas exist
all tests exist
valid tasks are accepted
invalid tasks fail closed
prompt/context construction is bounded, redacted, provenance-backed, and versioned
prompt-injection attempts cannot bypass safety rules
model output is parsed and schema-gated before any downstream use
worker tool requests are allowlisted by name/effect
budget, timeout, retry, and repair limits are enforced
worker task idempotency and concurrent runtime artifact writes are safe
model calls go through Model Adapter or are safely deferred
tool requests go through Tool / MCP Adapter or are safely deferred
policy checks run before model/tool/patch/validation actions
sandbox-sensitive effects are routed through Tool Adapter and Security Sandbox
failure classes are populated
patch proposals are non-applied and handed off only through Governed Patch Execution
validation requests are routed safely
repair loops are bounded and evidenced
blocked actions fail closed
worker tasks are evidenced
worker results are evidenced
blocked actions are evidenced
invalid tasks are evidenced
evidence manifest is written
review report is written
evidence hashes are written
review environment is recorded
no source mutation occurs directly in this layer
no shell command is executed directly in this layer
no patch is applied directly in this layer
no Git write occurs directly in this layer
no network/provider connection is opened directly in this layer
completion record exists
final verdict is recorded
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_llm_implementation_worker_schemas.py
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
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_worker_subdirectory": "tools/agentx_evolve/workers/llm_implementation_worker/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/implementation_worker/",
  "basis_documents": [
    "LLM_IMPLEMENTATION_WORKER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_SPEC",
    "LLM_IMPLEMENTATION_WORKER_IMPLEMENTATION_REVIEW_AND_DOD_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "model_adapter_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "patch_handoff_verified": [],
  "validation_requests_verified": [],
  "repair_limits_verified": [],
  "prompt_context_safety_verified": [],
  "prompt_injection_tests_verified": [],
  "context_provenance_verified": [],
  "model_output_parser_verified": [],
  "tool_request_allowlist_verified": [],
  "budget_limits_verified": [],
  "idempotency_verified": [],
  "concurrency_locks_verified": [],
  "blocked_actions_verified": [],
  "invalid_tasks_verified": [],
  "evidence_manifest_path": ".agentx-init/implementation_worker/llm_worker_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/implementation_worker/llm_worker_review_report.json",
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
[ ] worker package exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Worker behavior:
[ ] valid tasks accepted
[ ] invalid tasks rejected
[ ] prompt/context bounded and redacted
[ ] prompt-injection attempts blocked or neutralized
[ ] context provenance/hashing recorded
[ ] prompt template id/version recorded
[ ] model output treated as untrusted
[ ] model output schema-gated before downstream use
[ ] worker tool requests are allowlisted
[ ] budgets/timeouts/retry limits enforced
[ ] idempotency behavior verified
[ ] concurrency/lock behavior verified
[ ] patch proposals are non-applied
[ ] validation requests routed safely
[ ] repair loops bounded

Integration:
[ ] Model Adapter used or safely deferred
[ ] Tool / MCP Adapter used or safely deferred
[ ] Policy / Capability Registry used
[ ] Security Sandbox reached through Tool Adapter for path/file/command effects
[ ] Failure Taxonomy used
[ ] Governed Patch Execution used for patch handoff or safely deferred

Blocked / Invalid:
[ ] direct source mutation blocked
[ ] direct shell blocked
[ ] direct patch apply blocked
[ ] direct Git write blocked
[ ] direct network/provider access blocked
[ ] blocked/invalid outcomes are schema-valid
[ ] blocked/invalid outcomes write evidence

Evidence:
[ ] task history written
[ ] result history written
[ ] blocked action history written
[ ] invalid task history written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Safety:
[ ] no source mutation directly in this layer
[ ] no shell execution directly in this layer
[ ] no patch application directly in this layer
[ ] no Git write directly in this layer
[ ] no network/provider connection directly in this layer

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 41. Final Sign-Off Template

Use this after implementation validation.

```text
LLM Implementation Worker Validation — Commit <hash>

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
- model adapter integration: PASS/FAIL/DEFERRED SAFELY
- tool adapter integration: PASS/FAIL/DEFERRED SAFELY
- policy integration: PASS/FAIL
- sandbox integration: PASS/FAIL
- failure taxonomy integration: PASS/FAIL
- patch handoff coverage: PASS/FAIL/DEFERRED SAFELY
- validation request coverage: PASS/FAIL/DEFERRED SAFELY
- repair loop coverage: PASS/FAIL
- prompt/context safety: PASS/FAIL
- prompt-injection handling: PASS/FAIL
- context provenance/hashing: PASS/FAIL
- model output parser/schema-gating: PASS/FAIL/DEFERRED SAFELY
- tool-request allowlist: PASS/FAIL/DEFERRED SAFELY
- budget limits: PASS/FAIL
- idempotency: PASS/FAIL
- concurrency/locking: PASS/FAIL
- blocked action coverage: PASS/FAIL
- invalid task coverage: PASS/FAIL
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

# 42. Final Freeze Rule

This v4 document is frozen as the final review / DoD template for the LLM Implementation Worker.

Allowed future changes:

```text
PATCH: typo fixes, wording clarifications, example formatting, non-normative notes
MINOR: optional additional examples that do not change GO / NO-GO criteria
MAJOR: any change to trust boundaries, adapter bypass rules, live model requirements, direct mutation rules, evidence requirements, or DONE criteria
```

Blocked without a major revision:

```text
allowing direct source mutation
allowing direct shell execution
allowing direct patch application
allowing direct Git writes
allowing direct provider/network access
allowing model output to become execution authority
removing Model Adapter boundary
removing Tool / MCP Adapter boundary
removing Policy / Capability Registry checks
removing Security Sandbox routing for path/file/command effects
removing Governed Patch Execution handoff for patch application
removing evidence hashes or reviewed-commit requirements
marking simulated integration as active integration
requiring live model/provider access for normal DONE validation
```

---

# 43. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It covers expected files, standards, fresh-clone validation, compileall, pytest, schema validation, model adapter integration, tool adapter integration, policy integration, sandbox integration, failure taxonomy integration, patch handoff coverage, validation request coverage, repair loop limits, prompt/context safety, prompt-injection blocking, context provenance and hashing, prompt template versioning, model-output schema-gating, tool-request allowlisting, budget limits, idempotency, concurrency locking, blocked actions, invalid tasks, negative tests, audit/evidence coverage, source mutation checks, evidence manifest, review report, SHA-256 evidence hashes, evidence immutability, deviation rules, implementation scoring, GO/NO-GO rules, remediation rules, Definition of Done, completion record, final checklist, and final DONE / NOT DONE verdict, active-vs-simulated integration classification, fake-adapter contracts, no-live-model CI proof, basis-document hashing, schema example corpus requirements, evidence hash closure, reviewer independence, and final freeze rules.
```
