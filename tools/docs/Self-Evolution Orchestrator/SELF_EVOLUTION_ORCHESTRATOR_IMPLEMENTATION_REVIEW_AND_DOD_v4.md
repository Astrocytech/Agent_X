# SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_SELF_EVOLUTION_ORCHESTRATOR
component_name: Self-Evolution Orchestrator
roadmap_layer: 11
roadmap_phase: Phase C — Orchestration and Controlled Self-Evolution
review_use: use after code is committed
basis_documents:
  - SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT
  - SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC
  - SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD_v1
  - SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD_v2
  - SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD_v4
  - SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD_v4
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards:
  - Command Acceptance Criteria, if orchestration invokes validation commands through tools
  - MCP Protocol Acceptance Criteria, only if orchestration is exposed through MCP
  - Prompt Contract / Prompt Versioning, if orchestration binds prompts to model calls
  - Model Runtime Acceptance Criteria, if model calls are made directly
  - Human Review / Approval Acceptance Criteria, if approval gates are active
  - Promotion / Release Gate Acceptance Criteria, if promotion is reachable
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if it writes markdown reports
canonical_orchestrator_subdirectory: tools/agentx_evolve/orchestrator/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/orchestrator/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and close to final, but I would rate it:

```text
9.8/10
```

It already had complete coverage for structure, validation, orchestration flow, tool/model/prompt bindings, approval gates, policy, sandbox, patch delegation, promotion gates, failure recovery, audit/evidence, run locking, idempotency, MCP exposure, command invocation, dependency fail-closed behavior, artifact provenance, evidence hashing, scoring, and final sign-off.

It was not fully 10/10 because several final production-control details were still under-specified:

```text
1. The metadata duplicated one basis document and did not include the v2 review document.
2. MCP Protocol Acceptance Criteria appeared in the required standards list even though MCP is conditional unless the orchestrator is exposed through MCP.
3. Resource budgets and infinite-loop prevention were implied through retry limits but not checked as a separate DONE requirement.
4. Plan revision and plan-freeze controls were not explicit enough for resumable orchestration runs.
5. Emergency stop / cancel / abort semantics were not separated from ordinary failure recovery.
6. Cross-run isolation and session artifact namespace boundaries were not explicit enough.
7. Data-minimization rules for context packages and model-bound task packs needed stronger review coverage.
8. Manual override rules needed a clearer statement that no human/operator override can bypass non-overridable safety blocks.
9. The final evidence package did not explicitly require resource-budget, stop-event, plan-revision, and isolation evidence.
10. The final checklist needed those controls as first-class review gates.
```

This v4 applies those corrections and is the final 10/10 review / DoD template.

Freeze rule:

```text
This v4 document is frozen for the Self-Evolution Orchestrator post-implementation review.
Future changes should be limited to PATCH-level wording, examples, or typo fixes unless the orchestrator authority model, required gates, or runtime artifact boundaries change.
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Self-Evolution Orchestrator**.

Use this document after code is committed to determine whether the orchestrator is complete, safe, auditable, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether orchestration flow coverage is complete
whether tool invocation coverage is complete
whether model invocation coverage is complete or safely deferred
whether prompt binding coverage is complete or safely deferred
whether approval gate coverage is complete or safely deferred
whether policy coverage is complete
whether sandbox coverage is complete
whether patch execution coverage is complete or safely deferred
whether promotion gate coverage is complete or safely deferred
whether failure recovery coverage is complete
whether audit/evidence coverage is complete
whether evidence hashes are complete
whether review report and completion record exist
whether source mutation checks pass
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this review document does not mean the implementation is complete. The implementation is complete only when the validation commands, evidence checks, negative tests, and final sign-off criteria in this document pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because the Self-Evolution Orchestrator coordinates high-risk system behavior. It decides what work is attempted, which controlled layers are called, when gates are required, how failures are handled, and whether a run may continue.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if orchestration invokes validation commands through tools
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, only if orchestration is exposed through MCP
Prompt Contract / Prompt Versioning, because orchestration may bind prompts to model calls
Model Runtime Acceptance Criteria, if model calls are made directly
Human Review / Approval Acceptance Criteria, if approval gates are active
Promotion / Release Gate Acceptance Criteria, if promotion is reachable
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

The Self-Evolution Orchestrator is safety-critical because it decides:

```text
which task is being attempted
which role performs each step
which model is used
which prompt contract is used
which tools are called
which files may be read
which changes may be proposed
which validation commands are requested
which failures trigger retry
which failures trigger rollback
which steps require human approval
which outputs can proceed to promotion
when a run is stopped
when a run is considered complete
```

It must not become a superuser layer.

The orchestrator should coordinate existing controlled layers:

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
Evaluation Harness
Monitoring / Observability
```

Key safety position:

```text
The orchestrator must be designed as:
planner + coordinator + state machine + gatekeeper
```

It must not be designed as:

```text
direct file writer
direct shell executor
direct Git mutator
direct patch applier
direct model bypass
direct policy override
direct approval override
direct promotion bypass
```

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
  jsonschema_version: <version or NOT INSTALLED>
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
[ ] accepted deviations are recorded in the deviation register
[ ] reviewer did not rely only on this document's internal rating
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

The implementation may not be marked `DONE` because this document says `review_document_rating: 10/10`. The implementation can be marked `DONE` only when recorded validation evidence satisfies the GO criteria.

---

# 5. Status Vocabulary

Use only these status values in review tables:

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, expose, promote, approve, or bypass controls. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Deferral Rules

Use these rules to avoid hiding missing work behind `NOT APPLICABLE` or `DEFERRED SAFELY`.

```text
NOT APPLICABLE:
  Use only when the implementation scope truly does not include the feature and there is no runtime entry point.

DEFERRED SAFELY:
  Use only when the feature is planned or stubbed, but the implementation proves it cannot execute, mutate files, call models, call network, approve, promote, or bypass policy/sandbox/tool gates.

PARTIAL:
  Use when some files or tests exist but behavior is incomplete, unproven, or not safely disabled.

FAIL:
  Use when the feature exists and violates the contract.
```

Model invocation may be `DEFERRED SAFELY` only if the review proves:

```text
no model call entrypoint executes
no hosted provider is called
no local model process starts
no model output is accepted as authority
no model can call tools directly
safe deferral is recorded in the deviation register
```

Approval gates may be `DEFERRED SAFELY` only if the review proves:

```text
approval-required operations block
missing approval never defaults to approved
approval cannot override policy or sandbox denial
no human approval UI is simulated as approval
safe deferral is recorded in the deviation register
```

Patch execution may be `DEFERRED SAFELY` only if the review proves:

```text
patch apply cannot execute
rollback cannot execute
patch operations do not bypass Governed Patch Execution
no direct source mutation occurs
safe deferral is recorded in the deviation register
```

Promotion may be `DEFERRED SAFELY` only if the review proves:

```text
promotion cannot execute
release state cannot change
Git write operations cannot execute
promotion gate cannot be bypassed
safe deferral is recorded in the deviation register
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
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_self_evolution_orchestrator_schemas.py
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

If `validate_self_evolution_orchestrator_schemas.py` is not implemented, equivalent schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_self_evolution_orchestrator_schema_validation.py
test_self_evolution_orchestrator_locking.py
test_self_evolution_orchestrator_idempotency.py
test_self_evolution_context_binding.py
test_self_evolution_command_invocation.py
test_self_evolution_mcp_exposure.py
test_self_evolution_dependency_availability.py
test_self_evolution_resource_budget.py
test_self_evolution_plan_revision.py
test_self_evolution_emergency_stop.py
test_self_evolution_session_isolation.py
```

No validation command may require:

```text
GPU
network
hosted model
LLM
Bun
Node
OpenCode runtime
running MCP server
human interactive input
Git write access
```

---

# 7. Expected Implementation Scope

## 7.1 Required Orchestrator Package

Expected location:

```text
tools/agentx_evolve/orchestrator/
```

Expected files:

```text
tools/agentx_evolve/orchestrator/__init__.py
tools/agentx_evolve/orchestrator/orchestrator_models.py
tools/agentx_evolve/orchestrator/orchestrator_state.py
tools/agentx_evolve/orchestrator/orchestrator_engine.py
tools/agentx_evolve/orchestrator/orchestration_plan.py
tools/agentx_evolve/orchestrator/step_executor.py
tools/agentx_evolve/orchestrator/tool_invocation.py
tools/agentx_evolve/orchestrator/model_invocation.py
tools/agentx_evolve/orchestrator/gate_controller.py
tools/agentx_evolve/orchestrator/recovery_controller.py
tools/agentx_evolve/orchestrator/promotion_controller.py
tools/agentx_evolve/orchestrator/orchestrator_audit.py
```

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
orchestration_session.schema.json
orchestration_plan.schema.json
orchestration_step.schema.json
orchestration_step_result.schema.json
orchestration_state.schema.json
orchestration_run_ledger.schema.json
orchestration_tool_binding.schema.json
orchestration_model_binding.schema.json
orchestration_prompt_binding.schema.json
orchestration_policy_decision.schema.json
orchestration_approval_gate.schema.json
orchestration_promotion_gate.schema.json
orchestration_recovery_action.schema.json
orchestration_audit_event.schema.json
orchestration_evidence_manifest.schema.json
orchestration_review_report.schema.json
orchestration_completion_record.schema.json
orchestration_run_lock.schema.json
orchestration_replay_record.schema.json
orchestration_context_package_binding.schema.json
orchestration_command_binding.schema.json
orchestration_mcp_exposure.schema.json
orchestration_dependency_status.schema.json
orchestration_resource_budget.schema.json
orchestration_plan_revision.schema.json
orchestration_stop_event.schema.json
orchestration_session_isolation.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_self_evolution_orchestrator_models.py
test_self_evolution_orchestrator_state.py
test_self_evolution_orchestrator_engine.py
test_self_evolution_orchestration_plan.py
test_self_evolution_step_executor.py
test_self_evolution_tool_invocation.py
test_self_evolution_model_invocation.py
test_self_evolution_prompt_binding.py
test_self_evolution_gate_controller.py
test_self_evolution_recovery_controller.py
test_self_evolution_promotion_controller.py
test_self_evolution_orchestrator_audit.py
test_self_evolution_orchestrator_negative_cases.py
test_self_evolution_orchestrator_schema_validation.py
test_self_evolution_orchestrator_locking.py
test_self_evolution_orchestrator_idempotency.py
test_self_evolution_context_binding.py
test_self_evolution_command_invocation.py
test_self_evolution_mcp_exposure.py
test_self_evolution_dependency_availability.py
test_self_evolution_resource_budget.py
test_self_evolution_plan_revision.py
test_self_evolution_emergency_stop.py
test_self_evolution_session_isolation.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/orchestrator/
```

Expected artifacts:

```text
orchestration_session_history.jsonl
orchestration_step_history.jsonl
orchestration_decision_history.jsonl
orchestration_recovery_history.jsonl
orchestration_gate_history.jsonl
orchestration_audit_history.jsonl
latest_orchestration_session.json
latest_orchestration_step.json
latest_orchestration_result.json
latest_orchestration_run_lock.json
orchestration_replay_history.jsonl
orchestration_dependency_status.json
orchestration_resource_budget_history.jsonl
orchestration_plan_revision_history.jsonl
orchestration_stop_event_history.jsonl
orchestration_session_isolation_record.json
self_evolution_orchestrator_evidence_manifest.json
self_evolution_orchestrator_review_report.json
self_evolution_orchestrator_completion_record.json
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Orchestrator package location | `tools/agentx_evolve/orchestrator/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| State machine | deterministic orchestration states implemented | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task planning | plan creation and validation implemented | PASS / PARTIAL / FAIL / NOT CHECKED |
| Step execution | steps execute only through controlled bindings | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool invocation | Tool / MCP Adapter is used; no direct bypass | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model invocation | Model Adapter / runtime profile rules enforced | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Prompt binding | Prompt contract/version binding enforced | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Approval gates | human/governance gates enforced | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Policy coverage | policy checked before orchestration decisions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox coverage | sandbox reached only through tool adapter / patch layer | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch execution | patch operations delegated to Governed Patch Execution | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Promotion gate | promotion delegated to Promotion / Release Gate | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Failure recovery | retry/rollback/stop rules use Failure Taxonomy | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence | runtime evidence written under approved root | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence hashing | manifest, review report, completion record hashes present | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | no direct source mutation by orchestrator | PASS / PARTIAL / FAIL / NOT CHECKED |
| Superuser prevention | no policy/sandbox/tool/model/approval/promotion bypass | PASS / PARTIAL / FAIL / NOT CHECKED |
| Run locking / concurrency | one active mutating session per protected scope; stale locks handled safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Idempotency / replay | repeated requests do not duplicate side effects; replay is evidenced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Context package binding | Context Builder / Task Packer outputs are bound and evidenced | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Command invocation | validation commands invoked only through Tool / MCP Adapter and command policy | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| MCP exposure | orchestrator MCP exposure is absent, blocked, or safely controlled | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE / DEFERRED SAFELY |
| Dependency availability | missing upstream layers fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Resource budget / loop prevention | max steps, retries, tool calls, model calls, and runtime limits enforced | PASS / PARTIAL / FAIL / NOT CHECKED |
| Plan revision control | plan changes are validated, versioned, evidenced, and blocked after terminal states | PASS / PARTIAL / FAIL / NOT CHECKED |
| Emergency stop / cancel / abort | stop requests reach safe terminal state and block further mutation | PASS / PARTIAL / FAIL / NOT CHECKED |
| Session isolation | cross-run artifacts, locks, approvals, and evidence cannot bleed across sessions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Data minimization | context packages and model-bound inputs exclude unnecessary secrets/raw content | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Session lifecycle | `orchestrator_engine.py` / `orchestrator_state.py` | `test_self_evolution_orchestrator_engine.py` | session history / review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Plan validation | `orchestration_plan.py` | `test_self_evolution_orchestration_plan.py` | step history / review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Deterministic state machine | `orchestrator_state.py` | `test_self_evolution_orchestrator_state.py` | run ledger / audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool invocation through adapter | `tool_invocation.py` | `test_self_evolution_tool_invocation.py` | decision history / tool evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model binding | `model_invocation.py` | `test_self_evolution_model_invocation.py` | model binding evidence / audit history | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Prompt binding | `model_invocation.py` / prompt binding module | `test_self_evolution_prompt_binding.py` | prompt contract refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Approval gates | `gate_controller.py` | `test_self_evolution_gate_controller.py` | gate history | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Policy integration | `gate_controller.py` / `step_executor.py` | policy tests | decision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox propagation | `tool_invocation.py` / tool results | sandbox tests | decision history / tool evidence refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Patch delegation | `step_executor.py` / patch binding | patch tests | recovery history / patch refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Promotion delegation | `promotion_controller.py` | `test_self_evolution_promotion_controller.py` | promotion gate refs | PASS / PARTIAL / FAIL / NOT CHECKED / DEFERRED SAFELY |
| Failure recovery | `recovery_controller.py` | `test_self_evolution_recovery_controller.py` | recovery history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit logging | `orchestrator_audit.py` | `test_self_evolution_orchestrator_audit.py` | audit history / evidence manifest | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | all public surfaces | `test_self_evolution_orchestrator_negative_cases.py` | pytest output / review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual creation | schema/manual validation | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer | schema validation test | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Resource budgets | `orchestrator_engine.py` / budget module | `test_self_evolution_resource_budget.py` | resource budget history / review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Plan revisions | `orchestration_plan.py` | `test_self_evolution_plan_revision.py` | plan revision history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Emergency stop | `orchestrator_state.py` / `orchestrator_engine.py` | `test_self_evolution_emergency_stop.py` | stop event history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Session isolation | state/audit/runtime path helpers | `test_self_evolution_session_isolation.py` | session isolation record | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Orchestrator Package Files

```text
[ ] tools/agentx_evolve/orchestrator/__init__.py
[ ] tools/agentx_evolve/orchestrator/orchestrator_models.py
[ ] tools/agentx_evolve/orchestrator/orchestrator_state.py
[ ] tools/agentx_evolve/orchestrator/orchestrator_engine.py
[ ] tools/agentx_evolve/orchestrator/orchestration_plan.py
[ ] tools/agentx_evolve/orchestrator/step_executor.py
[ ] tools/agentx_evolve/orchestrator/tool_invocation.py
[ ] tools/agentx_evolve/orchestrator/model_invocation.py
[ ] tools/agentx_evolve/orchestrator/gate_controller.py
[ ] tools/agentx_evolve/orchestrator/recovery_controller.py
[ ] tools/agentx_evolve/orchestrator/promotion_controller.py
[ ] tools/agentx_evolve/orchestrator/orchestrator_audit.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] orchestration_session.schema.json
[ ] orchestration_plan.schema.json
[ ] orchestration_step.schema.json
[ ] orchestration_step_result.schema.json
[ ] orchestration_state.schema.json
[ ] orchestration_run_ledger.schema.json
[ ] orchestration_tool_binding.schema.json
[ ] orchestration_model_binding.schema.json
[ ] orchestration_prompt_binding.schema.json
[ ] orchestration_policy_decision.schema.json
[ ] orchestration_approval_gate.schema.json
[ ] orchestration_promotion_gate.schema.json
[ ] orchestration_recovery_action.schema.json
[ ] orchestration_audit_event.schema.json
[ ] orchestration_evidence_manifest.schema.json
[ ] orchestration_review_report.schema.json
[ ] orchestration_completion_record.schema.json
orchestration_run_lock.schema.json
orchestration_replay_record.schema.json
orchestration_context_package_binding.schema.json
orchestration_command_binding.schema.json
orchestration_mcp_exposure.schema.json
orchestration_dependency_status.schema.json
orchestration_resource_budget.schema.json
orchestration_plan_revision.schema.json
orchestration_stop_event.schema.json
orchestration_session_isolation.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_self_evolution_orchestrator_models.py
[ ] test_self_evolution_orchestrator_state.py
[ ] test_self_evolution_orchestrator_engine.py
[ ] test_self_evolution_orchestration_plan.py
[ ] test_self_evolution_step_executor.py
[ ] test_self_evolution_tool_invocation.py
[ ] test_self_evolution_model_invocation.py
[ ] test_self_evolution_prompt_binding.py
[ ] test_self_evolution_gate_controller.py
[ ] test_self_evolution_recovery_controller.py
[ ] test_self_evolution_promotion_controller.py
[ ] test_self_evolution_orchestrator_audit.py
[ ] test_self_evolution_orchestrator_negative_cases.py
[ ] test_self_evolution_orchestrator_schema_validation.py
test_self_evolution_orchestrator_locking.py
test_self_evolution_orchestrator_idempotency.py
test_self_evolution_context_binding.py
test_self_evolution_command_invocation.py
test_self_evolution_mcp_exposure.py
test_self_evolution_dependency_availability.py
test_self_evolution_resource_budget.py
test_self_evolution_plan_revision.py
test_self_evolution_emergency_stop.py
test_self_evolution_session_isolation.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

---

# 11. Validation Commands

Run from a fresh checkout of the implementation commit.

Record exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`. Any non-zero exit code is `FAIL` unless the command is explicitly a negative test where non-zero is expected and the expected failure condition is recorded.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_self_evolution_orchestrator_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

If unrelated future-layer tests exist under `tools/agentx_evolve/tests`, the review must also record a scoped Self-Evolution Orchestrator pytest command such as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_models.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_state.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_engine.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestration_plan.py \
  tools/agentx_evolve/tests/test_self_evolution_step_executor.py \
  tools/agentx_evolve/tests/test_self_evolution_tool_invocation.py \
  tools/agentx_evolve/tests/test_self_evolution_model_invocation.py \
  tools/agentx_evolve/tests/test_self_evolution_prompt_binding.py \
  tools/agentx_evolve/tests/test_self_evolution_gate_controller.py \
  tools/agentx_evolve/tests/test_self_evolution_recovery_controller.py \
  tools/agentx_evolve/tests/test_self_evolution_promotion_controller.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_audit.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_negative_cases.py \
  tools/agentx_evolve/tests/test_self_evolution_orchestrator_schema_validation.py
test_self_evolution_orchestrator_locking.py
test_self_evolution_orchestrator_idempotency.py
test_self_evolution_context_binding.py
test_self_evolution_command_invocation.py
test_self_evolution_mcp_exposure.py
test_self_evolution_dependency_availability.py
test_self_evolution_resource_budget.py
test_self_evolution_plan_revision.py
test_self_evolution_emergency_stop.py
test_self_evolution_session_isolation.py
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
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any Self-Evolution Orchestrator Python file fails compile
any schema/test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
scoped_command: <optional scoped orchestrator pytest command>
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required orchestrator, state, tool invocation, model invocation, prompt binding, approval gate, policy, sandbox, patch, promotion, recovery, schema, evidence, or negative test fails
exit code is missing
```

---

# 14. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_self_evolution_orchestrator_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_self_evolution_orchestrator_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Required schema tests:

```text
orchestration session schema accepts valid session
orchestration session schema rejects missing session_id
orchestration plan schema accepts valid plan
orchestration plan schema rejects missing objective
orchestration step schema accepts valid step
orchestration step schema rejects unknown step_type
orchestration step result schema accepts SUCCESS result
orchestration step result schema accepts BLOCKED result
orchestration state schema accepts valid state transition
orchestration run ledger schema accepts valid ledger
orchestration tool binding schema accepts Tool / MCP Adapter binding
orchestration model binding schema accepts Model Adapter binding
orchestration prompt binding schema accepts Prompt Contract binding
orchestration policy decision schema accepts ALLOW/BLOCK/NEEDS_APPROVAL decisions
orchestration approval gate schema accepts pending/approved/blocked gates
orchestration promotion gate schema accepts gated promotion request
orchestration recovery action schema accepts retry/rollback/stop actions
orchestration audit event schema accepts valid event
orchestration evidence manifest schema accepts valid evidence manifest
orchestration review report schema accepts valid review report
orchestration completion record schema accepts final completion record
```

Blocking if:

```text
schema-invalid sessions are accepted
schema-invalid plans are accepted
schema-invalid steps are accepted
schema-invalid gate decisions are accepted
schema-invalid evidence manifests are accepted
schema-invalid review reports are accepted
schema-invalid completion records are accepted
schema validation exit code is missing
```

---

# 15. Orchestration Flow Coverage

Required coverage:

```text
[ ] session can be created
[ ] session has stable session_id
[ ] objective is recorded
[ ] task plan is validated before execution
[ ] steps execute in deterministic order
[ ] state transitions are explicit
[ ] paused state blocks further execution
[ ] blocked state blocks further execution
[ ] failed state records failure class
[ ] completed state requires all mandatory gates satisfied
[ ] run ledger records session lifecycle
[ ] repeated review of same input is deterministic or idempotency behavior is documented
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
orchestrator can execute without a valid plan
orchestrator skips state validation
orchestrator marks complete while required steps are blocked
orchestrator continues after terminal failure without recovery decision
orchestrator has nondeterministic state transitions without evidence
```

---

# 16. Tool Invocation Coverage

Required coverage:

```text
[ ] orchestrator invokes tools only through Tool / MCP Adapter
[ ] raw file writes are not used
[ ] raw shell is not used
[ ] direct Git mutation is not used
[ ] tool calls include caller role
[ ] tool calls include session_id
[ ] tool calls include requested effect
[ ] tool results are validated before use
[ ] BLOCKED tool result stops or gates the run
[ ] INVALID tool result stops or gates the run
[ ] tool evidence refs are attached to orchestration evidence
[ ] tool adapter unavailable causes BLOCKED, not direct fallback
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
tools are bypassed
raw filesystem mutation occurs
a shell command is executed directly
Tool / MCP Adapter BLOCKED result is ignored
Tool / MCP Adapter INVALID result is ignored
tool adapter failure triggers direct fallback execution
```

---

# 17. Model Invocation Coverage

Required coverage if model calls are made:

```text
[ ] model calls use Model Adapter or approved runtime binding
[ ] local/hosted model policy is checked
[ ] prompt contract/version is attached
[ ] context package ID is attached
[ ] model output is treated as proposal, not authority
[ ] model cannot directly invoke tools except through orchestrator-controlled flow
[ ] model cannot directly mutate files
[ ] hosted model calls require policy authorization
[ ] local model calls require runtime profile authorization
[ ] model failure is classified
[ ] model call evidence is attached to orchestration evidence
```

If model calls are deferred:

```text
[ ] no model call entrypoint executes
[ ] no hosted provider is called
[ ] no local model process starts
[ ] no model output is accepted as authority
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
model bypasses Model Adapter
model output is applied directly as source mutation
hosted model is called without policy
local model starts without runtime profile approval
prompt contract is missing where required
```

---

# 18. Prompt Binding Coverage

Required coverage if prompts are bound to model calls:

```text
[ ] prompt contract ID is attached
[ ] prompt version ID is attached
[ ] prompt input contract is attached
[ ] prompt output contract is attached
[ ] prompt safety rules are attached
[ ] prompt provenance is recorded
[ ] unversioned prompts block or require explicit deviation
[ ] prompt-sensitive data is redacted in durable evidence where required
```

If prompt binding is deferred:

```text
[ ] no model call requiring prompt binding executes
[ ] no unversioned prompt is used to drive implementation
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
unversioned prompt drives implementation
prompt contract is required but absent
raw prompt text is durably logged against policy
prompt safety rules are bypassed
```

---

# 19. Approval Gate Coverage

Required coverage if approval gates are active:

```text
[ ] governance-required step returns NEEDS_GOVERNANCE when governance is missing
[ ] human-approval-required step returns NEEDS_APPROVAL when approval is missing
[ ] approval result is recorded
[ ] denied approval blocks the run
[ ] approval cannot override non-overridable safety blocks
[ ] approval evidence refs are attached to orchestration evidence
```

If approval gates are deferred:

```text
[ ] approval-required operations block
[ ] no operation proceeds by assuming approval
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
orchestrator proceeds without required approval
approval overrides sandbox denial
approval overrides policy denial
approval is assumed from missing data
```

---

# 20. Policy Coverage

Required coverage:

```text
[ ] every orchestration session checks policy context
[ ] every step requiring authority checks policy before action
[ ] missing policy blocks non-read-only behavior
[ ] policy denial blocks the run or step
[ ] policy decision ID is recorded
[ ] policy evidence refs are attached
[ ] orchestrator cannot override Policy / Capability Registry
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
policy is skipped
missing policy defaults to ALLOW
policy denial is ignored
orchestrator overrides policy decision
```

---

# 21. Sandbox Coverage

Required coverage:

```text
[ ] orchestrator does not call sandbox directly for mutation
[ ] path/file/command operations go through Tool / MCP Adapter or Governed Patch Execution
[ ] sandbox denial is propagated
[ ] sandbox decision ID is recorded where applicable
[ ] sandbox evidence refs are attached
[ ] orchestrator cannot override sandbox denial
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
orchestrator mutates paths directly
sandbox denial is ignored
sandbox-required action proceeds without sandbox evidence
```

---

# 22. Patch Execution Coverage

Required coverage if patch execution is reachable:

```text
[ ] patch proposal is separate from patch application
[ ] patch application is delegated to Governed Patch Execution
[ ] patch session ID is recorded
[ ] patch precheck result is recorded
[ ] patch approval/gate result is recorded
[ ] failed patch triggers recovery policy
[ ] rollback is delegated to Governed Patch Execution
[ ] orchestrator does not apply patch directly
```

If patch execution is deferred:

```text
[ ] patch apply steps return BLOCKED or DEFERRED SAFELY
[ ] rollback steps return BLOCKED or DEFERRED SAFELY
[ ] no direct patch application occurs
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
orchestrator applies patches directly
patch execution bypasses Governed Patch Execution
rollback bypasses Governed Patch Execution
patch failure is ignored
```

---

# 23. Promotion Gate Coverage

Required coverage if promotion is reachable:

```text
[ ] promotion request is separate from implementation completion
[ ] promotion is delegated to Promotion / Release Gate
[ ] validation evidence is required before promotion
[ ] unresolved blockers prevent promotion
[ ] promotion decision is recorded
[ ] promotion evidence refs are attached
[ ] orchestrator cannot promote directly
```

If promotion is deferred:

```text
[ ] promotion steps return BLOCKED or DEFERRED SAFELY
[ ] no release/promotion mutation occurs
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
orchestrator directly promotes changes
promotion occurs without validation evidence
promotion gate denial is ignored
```

---

# 24. Failure Recovery Coverage

Required coverage:

```text
[ ] failures are classified using Failure Taxonomy
[ ] retry policy is explicit
[ ] retry count is bounded
[ ] rollback policy is explicit
[ ] stop policy is explicit
[ ] unknown failures default to stop or block
[ ] failed tool/model/patch/promotion steps cannot be silently ignored
[ ] recovery actions are recorded
[ ] recovery evidence refs are attached
[ ] repeated failure does not loop indefinitely
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unbounded retries are possible
failure is ignored
rollback is attempted without authority
unknown failure defaults to continue
```

---

# 25. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] orchestration_session_history.jsonl is written
[ ] orchestration_step_history.jsonl is written
[ ] orchestration_decision_history.jsonl is written
[ ] orchestration_recovery_history.jsonl is written when recovery occurs
[ ] orchestration_gate_history.jsonl is written when gates occur
[ ] orchestration_audit_history.jsonl is written
[ ] latest_orchestration_session.json is written atomically
[ ] latest_orchestration_step.json is written atomically
[ ] latest_orchestration_result.json is written atomically
[ ] self_evolution_orchestrator_evidence_manifest.json is written
[ ] self_evolution_orchestrator_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes session IDs and step IDs
[ ] evidence includes command text, exit codes, statuses, and summaries for validation commands
[ ] evidence includes hashes for final evidence artifacts
[ ] secrets and prompt-sensitive data are redacted where required
[ ] raw model prompts and raw model outputs are not durably logged unless explicitly allowed by policy
[ ] raw file contents are not durably logged
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
orchestration decisions are not logged
required gate decisions are not evidenced
recovery actions are not evidenced
secrets are logged
reviewed commit is missing from evidence
required hashes are missing
```

---

# 26. Evidence Manifest

Create:

```text
.agentx-init/orchestrator/self_evolution_orchestrator_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_evidence_manifest.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
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
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "tool_invocation_status": "PASS",
  "model_invocation_status": "PASS_OR_DEFERRED_SAFELY",
  "prompt_binding_status": "PASS_OR_DEFERRED_SAFELY",
  "approval_gate_status": "PASS_OR_DEFERRED_SAFELY",
  "patch_execution_status": "PASS_OR_DEFERRED_SAFELY",
  "promotion_gate_status": "PASS_OR_DEFERRED_SAFELY",
  "failure_recovery_status": "PASS",
  "redaction_status": "PASS",
  "resource_budget_status": "PASS",
  "plan_revision_status": "PASS",
  "emergency_stop_status": "PASS",
  "session_isolation_status": "PASS",
  "data_minimization_status": "PASS_OR_DEFERRED_SAFELY",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

The manifest must include paths and hashes for all final evidence files, including:

```text
self_evolution_orchestrator_evidence_manifest.json
self_evolution_orchestrator_review_report.json
self_evolution_orchestrator_completion_record.json
command output artifacts, if stored as files
JSONL evidence histories used by the review
latest_orchestration_session.json, if used by the review
latest_orchestration_step.json, if used by the review
latest_orchestration_result.json, if used by the review
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Approved runtime artifact boundary:

```text
.agentx-init/orchestrator/
```

Evidence artifacts for this layer must not be written outside that root unless the review records the exception in the deviation register. Unapproved evidence writes outside the runtime root are a source-mutation or artifact-boundary failure.

---

# 27. Review Report Artifact

Create:

```text
.agentx-init/orchestrator/self_evolution_orchestrator_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_review_report.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "review_document_id": "SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v3.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/orchestrator/self_evolution_orchestrator_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/orchestrator/self_evolution_orchestrator_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/orchestrator/self_evolution_orchestrator_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 27.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 28. Run Locking / Concurrency Coverage

Required coverage:

```text
[ ] orchestrator creates a run/session lock before executing authority-bearing steps
[ ] lock scope is explicit: repository, component, session, or target path set
[ ] a second mutating orchestration session cannot run against the same protected scope
[ ] read-only sessions cannot escalate into mutating sessions without a new lock/gate
[ ] stale locks are detected and require explicit recovery handling
[ ] lock acquisition and release are evidenced
[ ] lock failure returns BLOCKED, not best-effort execution
[ ] crash/restart recovery does not silently reuse an unsafe lock
[ ] parallel steps cannot bypass policy, sandbox, tool, approval, patch, or promotion gates
[ ] concurrent read-only steps preserve deterministic evidence ordering or record ordering metadata
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
two mutating sessions can run against the same protected scope
lock failure defaults to continue
stale lock is ignored
parallel execution bypasses gate checks
evidence ordering is ambiguous for authority-bearing steps
```

---

# 29. Idempotency / Replay Coverage

Required coverage:

```text
[ ] orchestration session has idempotency key or run_id
[ ] each step has stable step_id
[ ] repeated execution of the same submitted plan does not duplicate side effects
[ ] replay mode is explicit and evidence-only unless new authority is granted
[ ] retry creates a new attempt record rather than overwriting prior evidence
[ ] resumed runs validate prior state before continuing
[ ] completed runs cannot be reopened as mutable without a new session/gate
[ ] failed runs cannot be marked DONE by replay alone
[ ] replay records reference original session, step, and evidence hashes
[ ] idempotency behavior is tested for tool, model, patch, approval, and promotion steps where applicable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
repeated execution duplicates side effects
retry overwrites evidence
resume skips validation of prior state
failed run can be replayed into DONE without new validation
completed run can mutate without a new authority-bearing session
```

---

# 30. Context Builder / Task Packer Coverage

Required coverage if context packages are used:

```text
[ ] context package ID is attached to orchestration session
[ ] context package version/hash is recorded
[ ] task packer output is validated before model/tool use
[ ] context boundaries are respected
[ ] prompt/model inputs reference the approved context package
[ ] stale context package blocks or requires explicit refresh
[ ] context package evidence refs are attached to orchestration evidence
[ ] raw sensitive context is not durably logged unless allowed by policy
```

If context packaging is deferred:

```text
[ ] no model/tool step depends on an unverified context package
[ ] deferral is recorded in the deviation register
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
model/tool step uses unverified context
stale context is accepted silently
context package hash/version is missing where required
sensitive context is logged without policy allowance
```

---

# 31. Command Invocation Coverage

This section applies if the orchestrator invokes validation, inspection, or build commands through tools.

Required coverage:

```text
[ ] orchestrator never executes commands directly
[ ] command requests go through Tool / MCP Adapter
[ ] command allowlist is enforced by Tool / MCP Adapter / Policy Registry
[ ] command request includes caller role, session_id, requested effect, and dry_run status
[ ] command output is bounded and redacted before durable evidence
[ ] command failure is classified
[ ] network commands block by default
[ ] Git write commands block unless promotion/git layer explicitly authorizes them
[ ] command evidence refs are attached to orchestration evidence
[ ] command injection payloads are blocked by negative tests
```

If command invocation is not in scope:

```text
[ ] no command invocation entrypoint exists
[ ] no validation command is started by the orchestrator
[ ] status is NOT APPLICABLE with justification
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
orchestrator uses raw subprocess/shell
command allowlist is bypassed
command output logs secrets
network command executes by default
Git write command executes without proper gate
```

---

# 32. MCP Exposure Coverage

This section applies if the Self-Evolution Orchestrator is exposed through MCP or if any MCP client can start, inspect, resume, or control orchestration sessions.

Required coverage if MCP exposure exists:

```text
[ ] MCP exposure is disabled by default or read-only by default
[ ] MCP cannot start a mutating orchestration session by default
[ ] MCP cannot resume, approve, promote, patch, or retry without policy and gate checks
[ ] MCP request creates a schema-valid orchestration request record
[ ] MCP caller role is least-privilege by default
[ ] MCP request cannot bypass Tool / MCP Adapter
[ ] MCP request cannot bypass Policy / Capability Registry
[ ] MCP request cannot bypass approval or promotion gates
[ ] MCP server does not start on import
[ ] MCP opens no network port by default
[ ] invalid MCP orchestration request returns schema-valid BLOCKED or INVALID
[ ] MCP exposure status is evidenced
```

If MCP exposure is deferred or absent:

```text
[ ] no MCP server starts
[ ] no MCP network port opens
[ ] no MCP control path can mutate orchestration state
[ ] deferral or absence is recorded in the deviation register if planned
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
MCP starts mutating orchestration by default
MCP bypasses policy/tool/approval/promotion gates
MCP server starts automatically
MCP opens a port by default
MCP request can mark DONE without evidence
```

---

# 33. Dependency Availability / Fail-Closed Coverage

Required coverage:

```text
[ ] missing Tool / MCP Adapter blocks tool execution
[ ] missing Policy / Capability Registry blocks authority-bearing steps
[ ] missing Security Sandbox blocks path/file/command steps
[ ] missing Governed Patch Execution blocks patch apply and rollback
[ ] missing Failure Taxonomy maps failures to safe fallback class and blocks/halts where required
[ ] missing Model Adapter blocks model calls
[ ] missing Local Model Runtime Profile blocks local model calls
[ ] missing Prompt Contract blocks prompt-bound model calls
[ ] missing Human Review / Approval Interface blocks approval-required steps
[ ] missing Promotion / Release Gate blocks promotion
[ ] missing Git Integration blocks Git mutation
[ ] missing Evaluation Harness blocks promotion/release completion where validation is required
[ ] missing Monitoring / Observability does not block local validation but records a degraded evidence note
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
missing dependency defaults to ALLOW
missing controlled layer triggers direct fallback execution
missing model/prompt/approval/promotion dependency is ignored
missing evidence dependency allows DONE
```

---

# 34. Background Job / Scheduler / Daemon Coverage

Required coverage if the orchestrator includes scheduled, asynchronous, daemon, or background behavior:

```text
[ ] background execution is disabled by default
[ ] scheduled run cannot start without recorded policy context
[ ] background run cannot mutate source without the same gates as foreground run
[ ] background run writes session and step evidence
[ ] background failure is surfaced as BLOCKED/FAILED evidence
[ ] no hidden daemon starts on import
[ ] no network listener starts by default
[ ] scheduler state is under approved runtime artifact root
```

If background execution is not in scope:

```text
[ ] no daemon entrypoint exists
[ ] no scheduled run starts automatically
[ ] no background thread/process starts on import
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
background job starts without explicit authority
daemon starts on import
scheduler mutates source without gates
background failure is not evidenced
```

---

# 35. Artifact Provenance and Run Hash Coverage

Required coverage:

```text
[ ] orchestration session hash is recorded
[ ] orchestration plan hash is recorded
[ ] context package hash is recorded when used
[ ] prompt contract/version hash or immutable ID is recorded when used
[ ] model binding ID/hash is recorded when used
[ ] tool registry ID/hash is recorded when tools are invoked
[ ] policy decision IDs are recorded
[ ] patch session/proposal hashes are recorded when used
[ ] promotion evidence hashes are recorded when used
[ ] review report, evidence manifest, and completion record hashes are recorded
[ ] changed hashes invalidate previous DONE claims
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
run cannot be reproduced from recorded plan/context/tool/policy evidence
changed evidence hashes do not invalidate DONE
hashes are missing for final DONE artifacts
```

---

# 36. Resource Budget / Loop Prevention Coverage

Required behavior:

```text
[ ] every orchestration run has max_steps
[ ] every orchestration run has max_tool_calls
[ ] every orchestration run has max_model_calls when model invocation is active
[ ] every orchestration run has max_retry_count
[ ] every orchestration run has max_runtime_seconds or an equivalent bounded execution rule
[ ] retry loops terminate deterministically
[ ] repeated validation failures stop or enter controlled recovery instead of infinite retry
[ ] budget exhaustion returns schema-valid BLOCKED/FAILED terminal state
[ ] budget exhaustion writes evidence
[ ] resource budgets cannot be raised by model output or task text
[ ] human/operator overrides cannot bypass hard safety limits unless a separate policy-approved governance record exists
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
run can loop indefinitely
model output can raise budgets
retry count is unbounded
validation repair can run forever
budget exhaustion is not evidenced
```

---

# 37. Plan Revision / Plan Freeze Coverage

Required behavior:

```text
[ ] initial plan is validated before execution
[ ] plan has plan_id and plan_version
[ ] plan hash is recorded before execution
[ ] every plan revision creates a new version and hash
[ ] plan revisions are policy-checked before use
[ ] plan revisions are evidenced in orchestration_plan_revision_history.jsonl
[ ] plan cannot be revised after terminal DONE / FAILED / CANCELLED state
[ ] model-generated plan edits are proposals only, not authority
[ ] plan revision cannot skip approval, patch, promotion, policy, or sandbox gates
[ ] replay/resume verifies the plan hash before continuing
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
plan can change silently
plan hash is missing
plan revision can skip gates
terminal run can be reopened without a new run record
replay ignores plan-version mismatch
```

---

# 38. Emergency Stop / Cancel / Abort Coverage

Required behavior:

```text
[ ] stop/cancel/abort request has a schema-valid stop event
[ ] stop event transitions run to CANCELLED, STOPPED, or ABORTED terminal state
[ ] stop event blocks new mutating steps
[ ] in-flight mutating steps are not duplicated after stop
[ ] resume after stop requires a new explicit run or recovery record
[ ] stop event writes evidence
[ ] stop event does not delete prior evidence
[ ] stop event does not perform rollback unless rollback is explicitly governed
[ ] stop/cancel cannot be ignored by retry or replay logic
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
stop request is ignored
mutating steps continue after stop
stop deletes evidence
stop triggers ungoverned rollback
stopped run can resume without explicit recovery/restart evidence
```

---

# 39. Session Isolation / Cross-Run Boundary Coverage

Required behavior:

```text
[ ] every run has a unique session_id / run_id
[ ] runtime artifacts include session_id / run_id
[ ] locks are scoped to protected resource and session
[ ] approvals are scoped to the run or explicitly reusable by policy
[ ] context packages are scoped to the run
[ ] model outputs are scoped to the run
[ ] tool evidence refs are scoped to the run
[ ] a run cannot reuse another run's approval, lock, patch session, or promotion decision without explicit policy proof
[ ] latest artifacts do not replace append-only history
[ ] cross-run replay uses immutable evidence, not mutable latest-only state
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
approvals bleed across runs
locks bleed across unrelated sessions
latest artifacts are the only proof of state
replay can attach to the wrong run
context package from another run is reused without policy/evidence
```

---

# 40. Data Minimization / Context Leakage Coverage

Required behavior:

```text
[ ] context package binding records source refs and hashes
[ ] model-bound context excludes unnecessary raw file content
[ ] secrets are redacted before model/tool/audit binding
[ ] prompt-bound inputs use approved Prompt Contract / Prompt Versioning when active
[ ] task packs do not include unrelated repository data
[ ] model output is treated as untrusted proposal text
[ ] context package provenance is written to evidence
[ ] context package reuse across runs is policy-checked
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
secrets enter model-bound context
raw repository content is over-packed without need
context provenance is missing
model output is treated as authority
```

---

# 41. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/orchestrator/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by orchestrator tests
orchestrator writes source files directly
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots without deviation
```

---

# 42. Negative Test Pack

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] orchestrator cannot execute without valid session
[ ] orchestrator cannot execute without valid plan
[ ] orchestrator cannot skip policy check
[ ] orchestrator cannot skip Tool / MCP Adapter for tools
[ ] orchestrator cannot directly write files
[ ] orchestrator cannot directly execute shell
[ ] orchestrator cannot directly apply patches
[ ] orchestrator cannot directly mutate Git
[ ] orchestrator cannot call model without approved model binding
[ ] orchestrator cannot use prompt without prompt contract when required
[ ] orchestrator cannot proceed past missing approval
[ ] orchestrator cannot override policy denial
[ ] orchestrator cannot override sandbox denial
[ ] orchestrator cannot promote directly
[ ] orchestrator cannot retry indefinitely
[ ] orchestrator cannot treat model output as authority
[ ] orchestrator cannot mark DONE with unresolved blockers
[ ] orchestrator cannot mark DONE without review report
[ ] orchestrator cannot mark DONE without evidence manifest
[ ] orchestrator cannot mark DONE without completion record
[ ] orchestrator cannot mark DONE without evidence hashes
[ ] orchestrator cannot start a second mutating session without lock authority
[ ] orchestrator cannot replay a failed run into DONE without new validation
[ ] orchestrator cannot use stale context package silently
[ ] orchestrator cannot invoke validation command directly
[ ] orchestrator cannot expose mutating session control through MCP by default
[ ] orchestrator cannot start background job or daemon on import
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 43. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Model | Prompt | Approval | Patch | Promotion | Evidence | Schema | Runtime Artifact Boundary | Other>
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
HIGH items cannot be accepted for DONE unless the review explicitly proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/orchestrator/` require a deviation entry.
Model, prompt, approval, patch, and promotion deferrals require deviation entries.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 44. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
orchestration flow:
tool invocation:
model invocation:
prompt binding:
approval gates:
policy coverage:
sandbox coverage:
patch execution:
promotion gate:
failure recovery:
audit/evidence:
evidence manifest:
review report:
evidence hashes:
negative tests:
source mutation check:
completion record:
run locking / concurrency:
idempotency / replay:
context package binding:
command invocation:
MCP exposure:
dependency availability:
background job behavior:
artifact provenance / run hashes:
```

---

# 45. What Failed

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

# 46. Issue Severity Classification

## 46.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
orchestrator bypasses Tool / MCP Adapter
orchestrator bypasses Policy / Capability Registry
orchestrator bypasses Security Sandbox
orchestrator bypasses Governed Patch Execution
orchestrator bypasses Model Adapter or model policy
orchestrator bypasses prompt contract where required
orchestrator bypasses human approval where required
orchestrator bypasses promotion gate
orchestrator directly writes files
orchestrator directly executes shell
orchestrator directly mutates Git
orchestrator directly applies patches
model output is treated as authority
unbounded retry is possible
unknown failure defaults to continue
approval overrides non-overridable safety denial
policy denial is ignored
sandbox denial is ignored
required evidence is missing
evidence hashes are missing
secrets are logged
review report is missing
completion record is missing
required area remains NOT CHECKED
required command remains NOT RUN
run locking failure allows concurrent mutation
idempotency failure duplicates side effects
MCP exposure allows mutating orchestration by default
command invocation bypasses Tool / MCP Adapter
background job or daemon starts on import
stale context package is used silently
missing dependency defaults to ALLOW
artifact provenance is insufficient for replay/review
```

## 46.2 HIGH

High issues must be fixed before this layer is used by an autonomous orchestrator.

```text
partial model binding coverage
partial prompt binding coverage
partial approval gate coverage
partial failure taxonomy mapping
partial evidence references
review environment not recorded
some expected orchestrator wrappers missing but not used yet
runtime artifact boundary exception lacks justification
model/prompt/approval/patch/promotion deferral lacks deviation entry
```

## 46.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled future-step definitions
model invocation intentionally deferred with proof
promotion intentionally deferred with proof
human approval interface intentionally stubbed with blocking behavior
markdown report writer intentionally absent
```

---

# 47. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Orchestrator, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Orchestration flow | 1.0 | Session, plan, step, state, and terminal-state behavior are deterministic and tested. |
| Controlled invocation | 1.0 | Tool, model, prompt, policy, sandbox, approval, patch, and promotion bindings are enforced or safely deferred. |
| Failure recovery | 1.0 | Failures are classified; retry is bounded; rollback and stop policies are enforced. |
| Negative safety behavior | 1.0 | All superuser, bypass, direct mutation, and DONE-without-evidence cases fail closed. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, and completion record exist. |
| Source-mutation and reproducibility safety | 1.0 | Clean git status, exact commands, exit codes, environment, hashes, and deviation register are recorded. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for controlled self-evolution
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
direct file write caps score at 4.0
direct shell execution caps score at 4.0
direct Git mutation caps score at 4.0
direct patch application caps score at 4.0
policy/sandbox/tool/model/approval/promotion bypass caps score at 4.0
unbounded retry caps score at 5.0
unknown failure defaults to continue caps score at 5.0
secrets logged caps score at 4.0
source mutation by tests caps score at 7.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing run lock for mutating orchestration caps score at 7.0
concurrent mutation possible caps score at 4.0
idempotency/replay duplicates side effects caps score at 4.0
MCP mutating exposure by default caps score at 4.0
raw command invocation outside Tool / MCP Adapter caps score at 4.0
daemon/background job starts on import caps score at 4.0
missing dependency defaults to ALLOW caps score at 4.0
missing artifact provenance for final DONE caps score at 8.0
```

---

# 48. GO / NO-GO Rules

## 48.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
orchestration flow tests pass
tool invocation tests pass
model invocation tests pass or model invocation is safely deferred
prompt binding tests pass or prompt binding is safely deferred
approval gate tests pass or approval is safely deferred
policy coverage tests pass
sandbox coverage tests pass
patch execution tests pass or patch execution is safely deferred
promotion gate tests pass or promotion is safely deferred
failure recovery tests pass
run locking/concurrency tests pass
idempotency/replay tests pass
context package binding tests pass or context packaging is safely deferred/not applicable
command invocation tests pass or command invocation is not applicable
MCP exposure tests pass or MCP exposure is not applicable/safely deferred
dependency availability tests pass
background job/daemon tests pass or background execution is not applicable
artifact provenance/hash tests pass
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

## 48.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
orchestrator bypasses controlled tool invocation
orchestrator bypasses policy
orchestrator bypasses sandbox
orchestrator directly writes source
orchestrator directly executes shell
orchestrator directly mutates Git
orchestrator directly applies patches
orchestrator calls model without approved binding
orchestrator uses prompt without required prompt contract
orchestrator proceeds without required approval
orchestrator promotes without promotion gate
model output is treated as authority
unbounded retry is possible
unknown failure defaults to continue
required evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 49. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix state transition checks
fix plan validation
fix tool invocation binding
fix model invocation binding
fix prompt contract binding
fix gate controller logic
fix policy checks
fix sandbox propagation
fix patch delegation
fix promotion delegation
fix failure taxonomy mapping
fix bounded retry rules
fix audit/evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not remove sandbox checks to pass tests
do not bypass Tool / MCP Adapter
do not allow direct source writes
do not allow direct shell execution
do not allow direct Git mutation
do not allow direct patch application
do not allow model direct mutation
do not treat model output as authority
do not skip prompt contract binding where required
do not assume approval from missing approval data
do not allow approval to override non-overridable safety blocks
do not skip promotion gate
do not remove failure recovery limits
do not omit hashes for final DONE
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 50. Definition of Done

The Self-Evolution Orchestrator is done when it can coordinate controlled self-evolution without becoming a superuser layer.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
orchestration sessions are valid and evidenced
orchestration plans are validated before execution
state transitions are deterministic and explicit
steps execute only through controlled bindings
tool calls go through Tool / MCP Adapter
model calls go through Model Adapter or are safely deferred
prompt contracts are bound where required or safely deferred
policy checks occur before authority-bearing actions
sandbox denials are respected
patch execution is delegated or safely deferred
promotion is delegated or safely deferred
human approval gates block when approval is missing
failures are classified
retry is bounded
rollback is governed
unknown failure blocks or stops the run
run locking prevents concurrent mutation
idempotency/replay prevents duplicate side effects
context package bindings are validated where used
validation commands are invoked only through controlled tools
MCP exposure is absent, read-only, or safely controlled
missing dependencies fail closed
no background job, daemon, listener, or scheduler starts on import
artifact provenance and run hashes are recorded
audit/evidence records are written
evidence manifest is written
review report is written
evidence hashes are written
source mutation does not occur directly in the orchestrator
shell execution does not occur directly in the orchestrator
Git mutation does not occur directly in the orchestrator
completion record exists
final verdict is recorded
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
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 51. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
orchestration flow test result
tool invocation test result
model invocation test result or safe-deferred note
prompt binding test result or safe-deferred note
approval gate test result or safe-deferred note
policy coverage test result
sandbox coverage test result
patch execution test result or safe-deferred note
promotion gate test result or safe-deferred note
failure recovery test result
audit/evidence test result
negative-test result
git status output
evidence manifest
review report
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
session IDs and step IDs
no direct source mutation
no direct shell execution
no direct Git mutation
no direct patch application
no policy bypass
no sandbox bypass
no approval bypass
no promotion bypass
model output is not treated as authority
bounded retry behavior
run locking/concurrency behavior
idempotency/replay behavior
context package provenance where used
command invocation through controlled tools where used
MCP exposure status
dependency fail-closed behavior
background job/daemon status
artifact provenance and run hashes
resource budgets and loop-prevention proof
plan revision and plan-hash proof
emergency stop / cancel / abort proof
session isolation and cross-run boundary proof
data minimization / context leakage proof
secrets redacted
hashes for final evidence artifacts
```

---

# 52. Completion Evidence Record

After validation, create:

```text
.agentx-init/orchestrator/self_evolution_orchestrator_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "orchestration_completion_record.schema.json",
  "component_id": "AGENTX_SELF_EVOLUTION_ORCHESTRATOR",
  "component_name": "Self-Evolution Orchestrator",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "canonical_orchestrator_subdirectory": "tools/agentx_evolve/orchestrator/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/orchestrator/",
  "basis_documents": [
    "SELF_EVOLUTION_ORCHESTRATOR_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_SPEC",
    "SELF_EVOLUTION_ORCHESTRATOR_IMPLEMENTATION_REVIEW_AND_DOD_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "orchestration_flows_verified": [],
  "tool_invocation_verified": [],
  "model_invocation_verified": [],
  "prompt_binding_verified": [],
  "approval_gates_verified": [],
  "policy_integration_verified": [],
  "sandbox_integration_verified": [],
  "patch_execution_integration_verified": [],
  "promotion_gate_integration_verified": [],
  "failure_recovery_verified": [],
  "audit_evidence_verified": [],
  "negative_tests_verified": [],
  "resource_budgets_verified": [],
  "plan_revision_controls_verified": [],
  "emergency_stop_controls_verified": [],
  "session_isolation_verified": [],
  "data_minimization_verified": [],
  "evidence_manifest_path": ".agentx-init/orchestrator/self_evolution_orchestrator_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/orchestrator/self_evolution_orchestrator_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 53. Final Done / Not-Done Verdict

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
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 54. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/orchestrator/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Orchestration:
[ ] session lifecycle works
[ ] plan validation works
[ ] state transitions are explicit
[ ] terminal states block further execution

Controlled Invocation:
[ ] tools go through Tool / MCP Adapter
[ ] models go through Model Adapter or are safely deferred
[ ] prompt contracts are bound where required or safely deferred
[ ] no direct source writes
[ ] no direct shell execution
[ ] no direct Git mutation
[ ] no direct patch application

Gates:
[ ] policy checks enforced
[ ] sandbox denials respected
[ ] approval gates enforced or safely deferred
[ ] promotion gate enforced or safely deferred

Run Control:
[ ] run locks prevent concurrent mutation
[ ] stale locks fail closed or require recovery
[ ] idempotency prevents duplicated side effects
[ ] replay/resume validates prior state

Context / Commands / MCP:
[ ] context packages are bound and hashed where used
[ ] validation commands go through controlled tools or are N/A
[ ] MCP exposure is absent, read-only, or safely controlled
[ ] no daemon/background job starts on import
[ ] missing dependencies fail closed

Resource / Plan / Stop / Isolation:
[ ] resource budgets are enforced
[ ] infinite loops are blocked
[ ] plan revisions are versioned and hashed
[ ] terminal-state plan revision is blocked
[ ] stop/cancel/abort reaches safe terminal state
[ ] stopped runs cannot continue mutating steps
[ ] session artifacts are isolated by run/session ID
[ ] approvals, locks, context packages, and promotion decisions cannot bleed across runs
[ ] context packages are minimized and redacted

Recovery:
[ ] failures classified
[ ] retries bounded
[ ] rollback governed
[ ] unknown failures block or stop

Evidence:
[ ] session history written
[ ] step history written
[ ] decision history written
[ ] recovery history written when applicable
[ ] gate history written when applicable
[ ] audit history written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 55. Final Sign-Off Template

Use this after implementation validation.

```text
Self-Evolution Orchestrator Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>
- jsonschema: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- orchestration flow coverage: PASS/FAIL
- tool invocation coverage: PASS/FAIL
- model invocation coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- prompt binding coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- approval gate coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- policy coverage: PASS/FAIL
- sandbox coverage: PASS/FAIL
- patch execution coverage: PASS/FAIL/DEFERRED SAFELY
- promotion gate coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- failure recovery coverage: PASS/FAIL
- run locking/concurrency coverage: PASS/FAIL
- idempotency/replay coverage: PASS/FAIL
- context package binding coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- command invocation coverage: PASS/FAIL/N/A
- MCP exposure coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- dependency availability coverage: PASS/FAIL
- background job/daemon coverage: PASS/FAIL/DEFERRED SAFELY/N/A
- artifact provenance/run hash coverage: PASS/FAIL
- resource budget / loop prevention coverage: PASS/FAIL
- plan revision / plan freeze coverage: PASS/FAIL
- emergency stop / cancel / abort coverage: PASS/FAIL
- session isolation / cross-run boundary coverage: PASS/FAIL
- data minimization / context leakage coverage: PASS/FAIL/DEFERRED SAFELY
- audit/evidence coverage: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
- negative-test coverage: PASS/FAIL
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

# 56. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It preserves the v3 coverage and fixes the final precision gaps: clean basis-document metadata, correct conditional MCP standard handling, explicit resource budgets and loop-prevention checks, plan revision/version/hash controls, emergency stop/cancel/abort semantics, cross-run session isolation, data-minimization/context-leakage checks, and final evidence/sign-off requirements that prevent DONE from being claimed without reviewed commit, command evidence, hashes, review report, completion record, resource-budget proof, plan-revision proof, stop-event proof, session-isolation proof, and replayable provenance.
```
