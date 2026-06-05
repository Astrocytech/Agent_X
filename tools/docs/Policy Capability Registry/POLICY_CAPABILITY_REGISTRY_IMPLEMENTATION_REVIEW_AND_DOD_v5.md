# POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_REVIEW_AND_DOD
version: v5.0
status: final frozen post-implementation review template and Definition of Done
component_id: AGENTX_POLICY_CAPABILITY_REGISTRY
component_name: Policy / Capability Registry
roadmap_layer: 2
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
basis_documents:
  - POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT
  - POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC
primary_standard: EQC
supporting_standards:
  - FIC
  - SIB
  - Schema Contract
  - Evidence Rules
  - Audit Rules
conditional_standards:
  - MCP Protocol Acceptance Criteria, only if exposed through MCP
  - Initiator Integration Contract, if initiator_available is true
  - Sandbox Integration Contract, if sandbox check is requested
  - Human Review / Approval Acceptance Criteria, if approval gates are active
  - Promotion / Release Gate Acceptance Criteria, if promotion is reachable
optional_standards:
  - ES, only for ecosystem placement
  - Report Template, only if it writes markdown reports
canonical_subdirectory: tools/agentx_evolve/policy/
schema_subdirectory: tools/agentx_evolve/schemas/
test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/policies/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```

---

# 0. v5 Review and Upgrade Summary

This is the first post-implementation review / DoD document for the Policy / Capability Registry layer.

```text
Rating: 10/10
```

It covers:

```text
file and schema inventory
module-level verification (models, defaults, role matrix, capability, tool, model, decision, registry, evidence)
schema validation (capability, tool, model, role, decision, violation, audit, request, enforcement result)
policy decision correctness (unknown role/block, unknown tool/block, unknown model/block, etc.)
sandbox integration
initiator integration
negative test coverage
completion evidence
```

Freeze rule:

```text
This v5 document is frozen for the Policy / Capability Registry post-implementation review.
Future changes should be limited to PATCH-level wording, examples, or typo fixes unless the policy model, decision engine, evidence format, runtime artifact boundaries, or governing contract changes.
```

---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Policy / Capability Registry** layer (L2).

Use this document after code is committed to determine whether the policy layer is complete, deterministic, auditable, safe, and ready to mark as `DONE`.

The review must determine:

```text
what files exist
what schemas exist
what tests exist
whether compileall passes
whether pytest passes
whether schemas validate
whether models are correct (all constants, dataclasses, reason codes)
whether default policies are loadable and correct
whether role matrix is correct and role validation works
whether capability policy queries work (find, allow, block, approval, governance, sandbox)
whether tool policy queries work (find, blocked, allows effect, requires governance/approval/sandbox)
whether model policy queries work (find, task allowed, file write, command, tool, network)
whether the decision engine correctly evaluates tool requests and model requests
whether the PolicyRegistry orchestrates all sub-policies correctly
whether evidence writing works (decisions, violations, audit)
whether schema validation passes for all policy artifacts
whether unknown role/tool/model defaults to BLOCK
whether sandbox integration is wired
whether initiator integration is wired
whether negative tests confirm fail-closed behavior
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. A 10/10 rating for this review document does not mean the implementation is complete. The implementation is complete only when the validation commands, evidence checks, negative tests, and final sign-off criteria in this document pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because the Policy / Capability Registry is a deterministic control component that decides which actions are allowed, blocked, or gated. Every decision must be explicit, auditable, and repeatable.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if policy evaluates commands
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, only if exposed through MCP
Initiator Integration Contract, if initiator_available is true
Sandbox Integration Contract, if sandbox check is requested
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

The Policy / Capability Registry is safety-critical because it decides:

```text
which roles may call which tools
which effects each tool may request
which actions are blocked
which actions require governance, approval, or sandbox checks
which model profiles are authorised
which Git/network/command/source-write operations are forbidden by default
```

It is the deterministic gate between caller intent and allowed action. It must not have:

```text
implicit ALLOW on unknown roles
implicit ALLOW on unknown tools
implicit ALLOW on unknown models
missing evidence for policy decisions
bypassable policy checks
```

Key safety position:

```text
The Policy / Capability Registry must be designed as:
deterministic block-first authority + auditable evidence writer
```

It must not be designed as:

```text
best-effort permission checker
default-allow policy engine
silently bypassable gate
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

---

# 6. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy/
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_models.py tools/agentx_evolve/tests/test_policy_defaults.py tools/agentx_evolve/tests/test_role_matrix.py tools/agentx_evolve/tests/test_capability_policy.py tools/agentx_evolve/tests/test_tool_policy.py tools/agentx_evolve/tests/test_model_policy.py tools/agentx_evolve/tests/test_policy_decision.py tools/agentx_evolve/tests/test_policy_registry.py tools/agentx_evolve/tests/test_policy_evidence.py tools/agentx_evolve/tests/test_policy_schema.py tools/agentx_evolve/tests/test_policy_negative_cases.py tools/agentx_evolve/tests/test_policy_sandbox_integration.py tools/agentx_evolve/tests/test_policy_initiator_integration.py tools/agentx_evolve/tests/test_policy_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_capability_policy_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_tool_policy_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_model_policy_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_role_permission_matrix_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_policy_decision_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_policy_violation_schema -x
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py::test_policy_audit_schema -x
git status --short
```

Required result:

```text
initial git status: clean or expected known runtime artifacts only
python version: recorded
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation tests: PASS, exit_code 0
final git status: clean or expected runtime artifacts only
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

## 7.1 Required Policy Package

Expected location:

```text
tools/agentx_evolve/policy/
```

Expected files:

```text
tools/agentx_evolve/policy/__init__.py
tools/agentx_evolve/policy/policy_models.py
tools/agentx_evolve/policy/policy_defaults.py
tools/agentx_evolve/policy/role_matrix.py
tools/agentx_evolve/policy/capability_policy.py
tools/agentx_evolve/policy/tool_policy.py
tools/agentx_evolve/policy/model_policy.py
tools/agentx_evolve/policy/policy_decision.py
tools/agentx_evolve/policy/policy_registry.py
tools/agentx_evolve/policy/policy_evidence.py
tools/agentx_evolve/policy/policy_request.py
tools/agentx_evolve/policy/policy_enforcer.py
tools/agentx_evolve/policy/policy_loader.py
tools/agentx_evolve/policy/capability_registry.py
tools/agentx_evolve/policy/initiator_policy_compat.py
tools/agentx_evolve/policy/sandbox_policy_compat.py
```

## 7.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
capability_policy.schema.json
tool_policy.schema.json
model_policy.schema.json
role_permission_matrix.schema.json
policy_decision.schema.json
policy_violation.schema.json
policy_audit.schema.json
policy_request.schema.json
policy_enforcement_result.schema.json
```

## 7.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_policy_models.py
test_policy_defaults.py
test_role_matrix.py
test_capability_policy.py
test_tool_policy.py
test_model_policy.py
test_policy_decision.py
test_policy_registry.py
test_policy_evidence.py
test_policy_schema.py
test_policy_negative_cases.py
test_policy_sandbox_integration.py
test_policy_initiator_integration.py
test_policy_integration.py
test_capability_registry.py
```

## 7.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/policies/
```

Expected artifacts:

```text
policy_decisions.jsonl
policy_violations.jsonl
latest_policy_decision.json
policy_evidence_manifest.json
policy_review_report.json
policy_completion_record.json
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Policy package location | `tools/agentx_evolve/policy/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation tests | pytest schema validation passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Models / constants | policy_models defines all constants, dataclasses, reason codes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Default policies | load_default_* functions produce valid policies | PASS / PARTIAL / FAIL / NOT CHECKED |
| Role matrix | role_exists, get_role_permissions, is_valid_role work | PASS / PARTIAL / FAIL / NOT CHECKED |
| Capability policy | find_capability, is_effect_allowed, is_effect_blocked | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool policy | find_tool, tool_is_blocked, tool_allows_effect | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model policy | find_model_profile, model_task_allowed, model_may_write_files | PASS / PARTIAL / FAIL / NOT CHECKED |
| Decision engine | evaluate_tool_request, evaluate_model_request, choose_strictest_decision | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy registry | PolicyRegistry aggregates all sub-policies | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence | append_policy_decision, append_policy_violation, build_policy_audit_event | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | all JSON schemas accept valid instances and reject invalid | PASS / PARTIAL / FAIL / NOT CHECKED |
| Unknown role / tool / model | defaults to BLOCK | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox integration | SandboxPolicyCompat available | PASS / PARTIAL / FAIL / NOT CHECKED |
| Initiator integration | InitiatorPolicyCompat with graceful degradation | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | all public surfaces fail closed | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 9. Traceability Matrix

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Model definitions | `policy_models.py` | `test_policy_models.py` | all constants and reason codes tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Default policies | `policy_defaults.py` | `test_policy_defaults.py` | default policies are schema-valid | PASS / PARTIAL / FAIL / NOT CHECKED |
| Role permission matrix | `role_matrix.py` | `test_role_matrix.py` | role validation and permissions tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Capability queries | `capability_policy.py` | `test_capability_policy.py` | capability allow/block decisions tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool policy queries | `tool_policy.py` | `test_tool_policy.py` | tool allow/block/gate decisions tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Model policy queries | `model_policy.py` | `test_model_policy.py` | model allow/block decisions tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Decision engine | `policy_decision.py` | `test_policy_decision.py` | full tool and model evaluation tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy registry | `policy_registry.py` | `test_policy_registry.py` | aggregated evaluation tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence writer | `policy_evidence.py` | `test_policy_evidence.py` | decision/violation/audit evidence tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation | schemas/ *.schema.json | `test_policy_schema.py` | each schema accept/reject tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Negative safety cases | all modules | `test_policy_negative_cases.py` | pytest output / review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Sandbox integration | `sandbox_policy_compat.py` | `test_policy_sandbox_integration.py` | sandbox check wiring tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Initiator integration | `initiator_policy_compat.py` | `test_policy_initiator_integration.py` | initiator compat with graceful fallback tested | PASS / PARTIAL / FAIL / NOT CHECKED |
| Integration | all modules | `test_policy_integration.py` | end-to-end policy flow tested | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. What Exists Checklist

## 10.1 Policy Package Files

```text
[ ] tools/agentx_evolve/policy/__init__.py
[ ] tools/agentx_evolve/policy/policy_models.py
[ ] tools/agentx_evolve/policy/policy_defaults.py
[ ] tools/agentx_evolve/policy/role_matrix.py
[ ] tools/agentx_evolve/policy/capability_policy.py
[ ] tools/agentx_evolve/policy/tool_policy.py
[ ] tools/agentx_evolve/policy/model_policy.py
[ ] tools/agentx_evolve/policy/policy_decision.py
[ ] tools/agentx_evolve/policy/policy_registry.py
[ ] tools/agentx_evolve/policy/policy_evidence.py
[ ] tools/agentx_evolve/policy/policy_request.py
[ ] tools/agentx_evolve/policy/policy_enforcer.py
[ ] tools/agentx_evolve/policy/policy_loader.py
[ ] tools/agentx_evolve/policy/capability_registry.py
[ ] tools/agentx_evolve/policy/initiator_policy_compat.py
[ ] tools/agentx_evolve/policy/sandbox_policy_compat.py
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.2 Schema Files

```text
[ ] capability_policy.schema.json
[ ] tool_policy.schema.json
[ ] model_policy.schema.json
[ ] role_permission_matrix.schema.json
[ ] policy_decision.schema.json
[ ] policy_violation.schema.json
[ ] policy_audit.schema.json
[ ] policy_request.schema.json
[ ] policy_enforcement_result.schema.json
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

## 10.3 Test Files

```text
[ ] test_policy_models.py
[ ] test_policy_defaults.py
[ ] test_role_matrix.py
[ ] test_capability_policy.py
[ ] test_tool_policy.py
[ ] test_model_policy.py
[ ] test_policy_decision.py
[ ] test_policy_registry.py
[ ] test_policy_evidence.py
[ ] test_policy_schema.py
[ ] test_policy_negative_cases.py
[ ] test_policy_sandbox_integration.py
[ ] test_policy_initiator_integration.py
[ ] test_policy_integration.py
[ ] test_capability_registry.py
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
PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy/
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_models.py tools/agentx_evolve/tests/test_policy_defaults.py tools/agentx_evolve/tests/test_role_matrix.py tools/agentx_evolve/tests/test_capability_policy.py tools/agentx_evolve/tests/test_tool_policy.py tools/agentx_evolve/tests/test_model_policy.py tools/agentx_evolve/tests/test_policy_decision.py tools/agentx_evolve/tests/test_policy_registry.py tools/agentx_evolve/tests/test_policy_evidence.py tools/agentx_evolve/tests/test_policy_schema.py tools/agentx_evolve/tests/test_policy_negative_cases.py tools/agentx_evolve/tests/test_policy_sandbox_integration.py tools/agentx_evolve/tests/test_policy_initiator_integration.py tools/agentx_evolve/tests/test_policy_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py -v
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

# 12. Compileall Result

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy/
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
any policy Python file fails compile
any test module fails import due to syntax
exit code is missing
```

---

# 13. Pytest Result

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_models.py tools/agentx_evolve/tests/test_policy_defaults.py tools/agentx_evolve/tests/test_role_matrix.py tools/agentx_evolve/tests/test_capability_policy.py tools/agentx_evolve/tests/test_tool_policy.py tools/agentx_evolve/tests/test_model_policy.py tools/agentx_evolve/tests/test_policy_decision.py tools/agentx_evolve/tests/test_policy_registry.py tools/agentx_evolve/tests/test_policy_evidence.py tools/agentx_evolve/tests/test_policy_schema.py tools/agentx_evolve/tests/test_policy_negative_cases.py tools/agentx_evolve/tests/test_policy_sandbox_integration.py tools/agentx_evolve/tests/test_policy_initiator_integration.py tools/agentx_evolve/tests/test_policy_integration.py
scoped_command: <optional scoped pytest command>
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
any required policy module, model, decision, evidence, schema, negative, sandbox, initiator, or integration test fails
exit code is missing
```

---

# 14. Schema Validation Result

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py -v
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
output_sha256: <sha256>
```

Required schema tests:

```text
capability_policy schema accepts valid capability policy
capability_policy schema rejects missing policy_id
tool_policy schema accepts valid tool policy
tool_policy schema rejects missing policy_id
model_policy schema accepts valid model policy
model_policy schema rejects invalid model mode
role_permission_matrix schema accepts valid matrix
role_permission_matrix schema rejects missing roles
policy_decision schema accepts ALLOW / BLOCK / NEEDS_APPROVAL / UNKNOWN_ROLE / UNKNOWN_TOOL / UNKNOWN_MODEL decisions
policy_decision schema rejects missing decision_id
policy_violation schema accepts HIGH / MEDIUM / LOW severity
policy_violation schema rejects missing violation_type
policy_audit schema accepts valid audit event
policy_audit schema rejects missing event_type
policy_request schema accepts valid request
policy_enforcement_result schema accepts valid enforcement result
```

Blocking if:

```text
schema-invalid capability policies are accepted
schema-invalid tool policies are accepted
schema-invalid model policies are accepted
schema-invalid role matrices are accepted
schema-invalid decisions are accepted
schema-invalid violations are accepted
schema-invalid audit events are accepted
schema validation exit code is missing
```

---

# 15. Module Verification Checklist

## 15.1 Model Definitions (policy_models.py)

Required coverage:

```text
[ ] DECISION_ALLOW, DECISION_BLOCK, DECISION_WARN, DECISION_NEEDS_APPROVAL, DECISION_NEEDS_GOVERNANCE, DECISION_NEEDS_SANDBOX_CHECK, DECISION_NEEDS_RISK_REVIEW, DECISION_NEEDS_VALIDATION, DECISION_UNKNOWN_ROLE, DECISION_UNKNOWN_TOOL, DECISION_UNKNOWN_MODEL, DECISION_INVALID_POLICY exist
[ ] ROLE_ORCHESTRATOR, ROLE_IMPLEMENTATION_WORKER, ROLE_VALIDATION_REPAIR_WORKER, ROLE_REVIEWER_ASSISTANT, ROLE_PROMOTION_CHECKER, ROLE_PATCH_EXECUTOR, ROLE_TOOL_ADAPTER, ROLE_MODEL_ADAPTER, ROLE_HUMAN_OPERATOR exist
[ ] ALL_ROLES list contains all 9 roles
[ ] EFFECT_READ, EFFECT_WRITE_RUNTIME, EFFECT_WRITE_SOURCE, EFFECT_EDIT_SOURCE, EFFECT_PATCH_PRECHECK, EFFECT_PATCH_APPLY, EFFECT_EXECUTE_COMMAND, EFFECT_USE_MODEL, EFFECT_USE_NETWORK, EFFECT_READ_GIT, EFFECT_WRITE_GIT, EFFECT_REQUEST_APPROVAL, EFFECT_PROMOTE, EFFECT_ROLLBACK, EFFECT_AUDIT_WRITE, EFFECT_GRAPH_WRITE, EFFECT_MEMORY_WRITE exist
[ ] TRUST_TIER_0 through TRUST_TIER_6 constants exist
[ ] NON_OVERRIDABLE_BLOCKS list is defined
[ ] REASON constants exist for all allow/block/unknown/required decisions
[ ] CapabilityEntry, CapabilityPolicy, ToolEntry, ToolPolicy, ModelProfile, ModelPolicy, RolePermissionMatrix, PolicyDecision, PolicyViolation, PolicyAudit dataclasses exist
[ ] CapabilityEntry has all required fields (capability_id, role, tool_name, allowed_effects, blocked_effects, requires_approval, requires_governance, requires_sandbox, requires_risk_review, allowed_paths, blocked_paths, allowed_commands, allowed_model_profiles)
[ ] PolicyDecision has all required fields (decision_id, timestamp, source_component, caller_role, tool_name, requested_effect, target, decision, reason, applied_policy_ids, required_followups, evidence_ids)
[ ] PolicyViolation has all required fields (violation_id, timestamp, source_component, caller_role, tool_name, requested_effect, target, violation_type, severity, reason, decision_id)
[ ] PolicyAudit has all required fields (audit_id, timestamp, source_component, event_type, decision_id, caller_role, tool_name, requested_effect, decision, reason, success)
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
any required decision constant is missing
any required role constant is missing
any required effect constant is missing
any required reason constant is missing
any required dataclass is missing or missing required fields
```

## 15.2 Default Policy Checks (policy_defaults.py)

Required coverage:

```text
[ ] load_default_capability_policy returns valid CapabilityPolicy with default_decision = DECISION_BLOCK
[ ] load_default_tool_policy returns valid ToolPolicy with tools list
[ ] load_default_model_policy returns valid ModelPolicy with default_model_mode = "local_only"
[ ] load_default_role_permission_matrix returns valid RolePermissionMatrix with all roles and non_overridable_blocks
[ ] each default policy is schema-valid
[ ] load_default_role_matrix exists and returns a matrix
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
any load_default_ function raises an exception
any default policy has invalid schema
default policy has default_decision = DECISION_ALLOW
```

## 15.3 Role Matrix Checks (role_matrix.py)

Required coverage:

```text
[ ] role_exists returns True for known roles
[ ] role_exists returns False for unknown roles
[ ] is_valid_role returns True for known roles
[ ] is_valid_role returns False for unknown roles
[ ] get_role_permissions returns dict for existing roles
[ ] build_default_role_permission_matrix creates a valid matrix
[ ] check_role_permission returns False for unknown roles
[ ] is_non_overridable_block returns True for known blocks
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown role is treated as valid
role permissions return mutable defaults that allow instead of block
```

## 15.4 Capability Policy Checks (capability_policy.py)

Required coverage:

```text
[ ] find_capability returns matching CapabilityEntry for role+tool
[ ] find_capability returns None for unknown role+tool
[ ] is_effect_allowed returns True when effect is in allowed_effects and not blocked
[ ] is_effect_allowed returns False when effect is in blocked_effects
[ ] is_effect_allowed returns False when effect is not in allowed_effects and default is BLOCK
[ ] is_effect_blocked returns True when effect is blocked
[ ] is_effect_blocked returns False when effect is allowed
[ ] capability_requires_approval checks both policy-level and entry-level flags
[ ] capability_requires_governance checks both policy-level and entry-level flags
[ ] capability_requires_sandbox checks both policy-level and entry-level flags
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
blocked effect is allowed
unknown capability defaults to ALLOW
capability_requires_* return incorrect values
```

## 15.5 Tool Policy Checks (tool_policy.py)

Required coverage:

```text
[ ] find_tool returns matching ToolEntry
[ ] find_tool returns None for unknown tool
[ ] tool_exists returns True/False correctly
[ ] tool_is_blocked returns True for unknown tool
[ ] tool_is_blocked returns True when entry.blocked is True
[ ] tool_allows_effect returns True when effect is in requested_effects
[ ] tool_allows_effect returns False for unknown tool
[ ] tool_requires_governance reads entry.requires_governance
[ ] tool_requires_sandbox reads entry.requires_sandbox
[ ] tool_requires_human_approval reads entry.requires_human_approval
[ ] tool_uses_network reads entry.uses_network
[ ] tool_executes_command reads entry.executes_command
[ ] tool_writes_source reads entry.writes_source
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown tool is allowed
blocked tool is treated as allowed
tool_allows_effect returns True for unknown tool
```

## 15.6 Model Policy Checks (model_policy.py)

Required coverage:

```text
[ ] find_model_profile returns matching ModelProfile
[ ] find_model_profile returns None for unknown profile
[ ] model_profile_exists returns True/False correctly
[ ] model_task_allowed returns True when task in allowed_task_types
[ ] model_task_allowed returns False when task in blocked_task_types
[ ] model_task_allowed returns False for unknown profile
[ ] model_may_read_source reads profile flag
[ ] model_may_write_files reads profile flag
[ ] model_may_execute_tools reads profile flag
[ ] model_may_execute_commands reads profile flag
[ ] model_may_use_network reads profile flag
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown model profile is treated as allowed
blocked task type is allowed
model_may_write_files returns True for unknown profile
```

## 15.7 Decision Engine Checks (policy_decision.py)

Required coverage:

```text
[ ] evaluate_tool_request returns ALLOW when all gates pass
[ ] evaluate_tool_request returns UNKNOWN_ROLE for invalid role
[ ] evaluate_tool_request returns UNKNOWN_TOOL for unknown tool
[ ] evaluate_tool_request returns BLOCK for blocked tool
[ ] evaluate_tool_request returns BLOCK for blocked effect
[ ] evaluate_tool_request returns NEEDS_APPROVAL when approval required
[ ] evaluate_tool_request returns NEEDS_GOVERNANCE when governance required
[ ] evaluate_tool_request returns NEEDS_SANDBOX_CHECK when sandbox required
[ ] evaluate_tool_request returns BLOCK for network effect on non-network tool
[ ] evaluate_tool_request returns BLOCK for git write on non-git tool
[ ] evaluate_model_request returns ALLOW for valid model + task
[ ] evaluate_model_request returns UNKNOWN_ROLE for invalid role
[ ] evaluate_model_request returns UNKNOWN_MODEL for unknown profile
[ ] evaluate_model_request returns BLOCK for blocked task type
[ ] evaluate_model_request returns BLOCK when model cannot write files and effect is WRITE_SOURCE
[ ] choose_strictest_decision returns the strictest (lowest priority) decision
[ ] choose_strictest_decision returns DECISION_BLOCK over DECISION_ALLOW
[ ] choose_strictest_decision returns DECISION_INVALID_POLICY when present
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown role results in ALLOW
unknown tool results in ALLOW
unknown model results in ALLOW
blocked tool results in ALLOW
strictest decision is not chosen correctly
```

## 15.8 Registry Checks (policy_registry.py)

Required coverage:

```text
[ ] PolicyRegistry creates with defaults when no policy provided
[ ] PolicyRegistry evaluates tool request through evaluate_tool_request
[ ] PolicyRegistry evaluates model request through evaluate_model_request
[ ] PolicyRegistry writes decisions
[ ] PolicyRegistry.get_role_matrix returns the role matrix
[ ] PolicyRegistry.get_tool_policy returns the tool policy
[ ] PolicyRegistry.get_model_policy returns the model policy
[ ] PolicyRegistry.get_capability_policy returns the capability policy
[ ] PolicyRegistry.set_capability_policy replaces the capability policy
[ ] PolicyRegistry.set_tool_policy replaces the tool policy
[ ] PolicyRegistry.set_model_policy replaces the model policy
[ ] PolicyRegistry.set_role_matrix replaces the role matrix
[ ] PolicyRegistry.reload_defaults reloads all default policies
[ ] PolicyRegistry.choose_strictest_decision delegates correctly
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
PolicyRegistry uses hardcoded policies instead of constructor arguments
PolicyRegistry.evaluate_* returns incorrect decisions
PolicyRegistry.write_decision fails silently
```

## 15.9 Evidence Checks (policy_evidence.py)

Required coverage:

```text
[ ] append_policy_decision writes to .agentx-init/policies/policy_decisions.jsonl
[ ] append_policy_violation writes to .agentx-init/policies/policy_violations.jsonl
[ ] write_latest_policy_decision writes atomic latest_policy_decision.json
[ ] build_policy_audit_event creates valid PolicyAudit from PolicyDecision
[ ] backward-compat aliases exist (append_decision_to_evidence, write_decision_evidence, create_audit_entry)
[ ] evidence writing handles missing parent directory (creates it)
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
evidence writing fails silently
evidence is written to wrong path
audit event is missing required fields
```

---

# 16. Policy Decision Correctness

The decision engine must apply these rules deterministically:

```text
[ ] unknown role → DECISION_UNKNOWN_ROLE (BLOCK)
[ ] unknown tool → DECISION_UNKNOWN_TOOL (BLOCK)
[ ] unknown model → DECISION_UNKNOWN_MODEL (BLOCK)
[ ] blocked tool → DECISION_BLOCK
[ ] blocked effect → DECISION_BLOCK
[ ] requires approval → DECISION_NEEDS_APPROVAL
[ ] requires governance → DECISION_NEEDS_GOVERNANCE
[ ] requires sandbox → DECISION_NEEDS_SANDBOX_CHECK
[ ] network effect, tool does not use network → DECISION_BLOCK
[ ] git write effect, tool does not write git → DECISION_BLOCK
[ ] model cannot write files + WRITE_SOURCE effect → DECISION_BLOCK
[ ] model cannot execute commands + EXECUTE_COMMAND effect → DECISION_BLOCK
[ ] model cannot execute tools + tool use by model → DECISION_BLOCK
[ ] known role + known tool + allowed effect + no gate → DECISION_ALLOW
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
unknown role defaults to ALLOW
unknown tool defaults to ALLOW
unknown model defaults to ALLOW
blocked tool returns ALLOW
any decision returns unexpected value
```

---

# 17. Sandbox Integration Checklist

Required coverage:

```text
[ ] SandboxPolicyCompat class exists in sandbox_policy_compat.py
[ ] SandboxPolicyCompat.is_available returns True
[ ] SandboxPolicyCompat.request_sandbox_check returns expected structure
[ ] SandboxPolicyCompat does not depend on sandbox package being installed
[ ] test_policy_sandbox_integration.py tests exist
[ ] sandbox check is referenced in capability_requires_sandbox
[ ] sandbox check is referenced in tool_requires_sandbox
[ ] sandbox check is referenced in policy_decision evaluate_tool_request
[ ] sandbox block is authoritative and non-overridable
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
sandbox integration fails call
sandbox block is ignored
sandbox integration import crashes the module
```

---

# 18. Initiator Integration Checklist

Required coverage:

```text
[ ] InitiatorPolicyCompat class exists in initiator_policy_compat.py
[ ] InitiatorPolicyCompat has graceful degradation when agentx_initiator is not available (_INITIATOR_AVAILABLE = False)
[ ] InitiatorPolicyCompat.validate_schema exists
[ ] InitiatorPolicyCompat.write_artifact exists
[ ] InitiatorPolicyCompat.append_audit_event exists
[ ] InitiatorPolicyCompat.get_repo_root returns path
[ ] InitiatorPolicyCompat.get_policy_runtime_root returns .agentx-init/policies/
[ ] test_policy_initiator_integration.py tests exist
[ ] missing initiator does not cause import errors
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
missing agentx_initiator causes import failure
InitiatorPolicyCompat raises instead of graceful degradation
```

---

# 19. Negative Test Checklist

The review must prove that forbidden actions fail closed.

Required negative cases:

```text
[ ] unknown role is blocked
[ ] unknown tool is blocked
[ ] unknown model is blocked
[ ] blocked tool is blocked
[ ] blocked effect is blocked
[ ] missing capability defaults to block
[ ] network effect blocked by default
[ ] git write blocked by default
[ ] hosted model blocked by default if local_only
[ ] model cannot execute commands
[ ] model cannot write files
[ ] model cannot execute tools
[ ] human operator cannot override hard blocks
[ ] sandbox block is authoritative
[ ] missing policy blocks
[ ] invalid policy blocks (DECISION_INVALID_POLICY)
[ ] strictest decision wins over weaker decisions
[ ] empty decisions list returns BLOCK
[ ] evidence writing does not raise on missing directory
[ ] policy registry without policies uses defaults
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 20. Completion Evidence Checklist

## 20.1 Evidence Files

```text
[ ] .agentx-init/policies/policy_decisions.jsonl is written
[ ] .agentx-init/policies/policy_violations.jsonl is written
[ ] .agentx-init/policies/latest_policy_decision.json is written atomically
[ ] .agentx-init/policies/policy_evidence_manifest.json is written
[ ] .agentx-init/policies/policy_review_report.json is written
[ ] .agentx-init/policies/policy_completion_record.json is written
```

## 20.2 Evidence Includes

```text
[ ] timestamps
[ ] reviewed commit
[ ] decision IDs
[ ] caller role
[ ] tool name
[ ] requested effect
[ ] decision value
[ ] reason code
[ ] applied policy IDs
[ ] required follow-ups
[ ] evidence IDs
```

## 20.3 Evidence Provenance

```text
[ ] SHA-256 hashes are generated for final evidence artifacts
[ ] evidence manifest references all final evidence files with hashes
[ ] review report references evidence manifest with hash
[ ] completion record references review report and evidence manifest with hashes
[ ] evidence files are written under .agentx-init/policies/
[ ] no evidence written outside runtime artifact root without deviation
```

---

# 21. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Model | Tool | Evidence | Schema | Runtime Artifact Boundary | Other>
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
Runtime artifact writes outside `.agentx-init/policies/` require a deviation entry.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 22. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
module verification (models):
default policy checks:
role matrix checks:
capability policy checks:
tool policy checks:
model policy checks:
decision engine checks:
registry checks:
evidence checks:
policy decision correctness:
sandbox integration:
initiator integration:
negative tests:
completion evidence:
source mutation check:
```

---

# 23. What Failed

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

# 24. Issue Severity Classification

## 24.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown role defaults to ALLOW
unknown tool defaults to ALLOW
unknown model defaults to ALLOW
blocked tool returns ALLOW
blocked effect returns ALLOW
missing capability defaults to ALLOW
strictest decision is wrong
required evidence is missing
evidence hashes are missing
secrets are logged
review report is missing
completion record is missing
required area remains NOT CHECKED
required command remains NOT RUN
initiator integration fails on import
sandbox block is ignored
```

## 24.2 HIGH

High issues must be fixed before this layer is used by an autonomous orchestrator.

```text
partial default policy coverage
partial capability policy test coverage
partial tool policy test coverage
partial model policy test coverage
partial decision engine test coverage
partial evidence test coverage
partial schema validation test coverage
review environment not recorded
some expected policy wrappers missing but not used yet
runtime artifact boundary exception lacks justification
```

## 24.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled future-policy definitions
future expansion placeholder code
```

---

# 25. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---|---:|---|
| Structure and expected files | 1.0 | Policy, schema, test, and runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full policy test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass for all 9 policy schemas. |
| Module correctness | 1.0 | Models, defaults, role matrix, capability, tool, model policies are correct and complete. |
| Decision engine | 1.0 | evaluate_tool_request, evaluate_model_request, choose_strictest_decision are correct. |
| Policy registry | 1.0 | PolicyRegistry aggregates and delegates correctly. |
| Evidence | 1.0 | Decision, violation, and audit evidence are written to correct paths. |
| Negative safety behavior | 1.0 | All unknown/blocked/forbidden cases fail closed. |
| Source-mutation and reproducibility safety | 1.0 | Clean git status, exact commands, exit codes, environment, hashes, and deviation register are recorded. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not safety-complete
below 7.0 = not acceptable for deterministic safety layer
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
unknown role defaults to ALLOW caps score at 4.0
unknown tool defaults to ALLOW caps score at 4.0
unknown model defaults to ALLOW caps score at 4.0
blocked tool returns ALLOW caps score at 4.0
evidence not written caps score at 7.0
missing evidence hashes caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
```

---

# 26. GO / NO-GO Rules

## 26.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
module verification tests pass
default policy tests pass
role matrix tests pass
capability policy tests pass
tool policy tests pass
model policy tests pass
decision engine tests pass
registry tests pass
evidence tests pass
policy decision correctness tests pass
sandbox integration tests pass
initiator integration tests pass
negative tests pass
source mutation check passes
evidence files exist
evidence hashes exist
review report exists
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 26.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
unknown role is treated as ALLOW
unknown tool is treated as ALLOW
unknown model is treated as ALLOW
blocked tool is treated as ALLOW
blocked effect is treated as ALLOW
required evidence is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 27. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix policy query logic
fix decision engine rules
fix evidence writing paths
fix atomic write patterns
fix test assertions
fix default policy values
```

Forbidden fixes:

```text
do not change unknown role to default ALLOW
do not change unknown tool to default ALLOW
do not change unknown model to default ALLOW
do not remove blocked effect checks
do not remove blocked tool checks
do not remove capability missing checks
do not skip sandbox check integration
do not skip initiator integration
do not remove evidence writing
do not accept a BLOCKER as a deviation
```

---

# 28. Definition of Done

The Policy / Capability Registry is done when it is a deterministic block-first authority that decides which roles, tools, effects, and models are allowed, blocked, or gated.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
models define all required constants, dataclasses, and reason codes
default policies load correctly and are schema-valid
role matrix validates roles correctly
capability policy allows/block effects correctly
tool policy allows/blocks tools and effects correctly
model policy allows/blocks models and tasks correctly
decision engine evaluates tool and model requests correctly
policy registry orchestrates all sub-policies correctly
evidence is written to the correct runtime paths
validation commands pass
pytest passes
schema validation passes
no unknown role is treated as ALLOW
no unknown tool is treated as ALLOW
no unknown model is treated as ALLOW
no blocked tool is treated as ALLOW
sandbox integration is wired
initiator integration handles absence gracefully
negative tests confirm fail-closed behavior
git status is clean or only expected runtime artifacts
evidence manifest, review report, and completion record exist with hashes
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/policy/
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_models.py tools/agentx_evolve/tests/test_policy_defaults.py tools/agentx_evolve/tests/test_role_matrix.py tools/agentx_evolve/tests/test_capability_policy.py tools/agentx_evolve/tests/test_tool_policy.py tools/agentx_evolve/tests/test_model_policy.py tools/agentx_evolve/tests/test_policy_decision.py tools/agentx_evolve/tests/test_policy_registry.py tools/agentx_evolve/tests/test_policy_evidence.py tools/agentx_evolve/tests/test_policy_schema.py tools/agentx_evolve/tests/test_policy_negative_cases.py tools/agentx_evolve/tests/test_policy_sandbox_integration.py tools/agentx_evolve/tests/test_policy_initiator_integration.py tools/agentx_evolve/tests/test_policy_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_policy_schema.py -v
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

# 29. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
model verification test result
default policy test result
role matrix test result
capability policy test result
tool policy test result
model policy test result
decision engine test result
registry test result
evidence test result
policy decision correctness test result
sandbox integration test result
initiator integration test result
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
decision IDs and role/tool/effect
no unknown-role ALLOW
no unknown-tool ALLOW
no unknown-model ALLOW
no blocked-tool ALLOW
evidence is written to correct runtime paths
```

---

# 30. Completion Evidence Record

After validation, create:

```text
.agentx-init/policies/policy_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "policy_completion_record.schema.json",
  "component_id": "AGENTX_POLICY_CAPABILITY_REGISTRY",
  "component_name": "Policy / Capability Registry",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>",
    "jsonschema_version": "<version or NOT INSTALLED>"
  },
  "canonical_subdirectory": "tools/agentx_evolve/policy/",
  "schema_subdirectory": "tools/agentx_evolve/schemas/",
  "test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/policies/",
  "basis_documents": [
    "POLICY_CAPABILITY_REGISTRY_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_SPEC",
    "POLICY_CAPABILITY_REGISTRY_IMPLEMENTATION_REVIEW_AND_DOD_v5"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "module_verification_verified": [],
  "default_policy_verified": [],
  "role_matrix_verified": [],
  "capability_policy_verified": [],
  "tool_policy_verified": [],
  "model_policy_verified": [],
  "decision_engine_verified": [],
  "registry_verified": [],
  "evidence_verified": [],
  "schema_validation_verified": [],
  "sandbox_integration_verified": [],
  "initiator_integration_verified": [],
  "negative_tests_verified": [],
  "policy_decision_correctness_verified": [],
  "evidence_manifest_path": ".agentx-init/policies/policy_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/policies/policy_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 31. Final Done / Not-Done Verdict

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

# 32. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/policy/ exists
[ ] schemas exist
[ ] tests exist

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Module Verification:
[ ] policy_models defines all constants, dataclasses, reason codes
[ ] policy_defaults produces valid default policies
[ ] role_matrix validates roles correctly
[ ] capability_policy allows/blocks effects correctly
[ ] tool_policy allows/blocks tools correctly
[ ] model_policy allows/blocks models correctly
[ ] policy_decision evaluates tool and model requests correctly
[ ] policy_registry orchestrates all sub-policies correctly
[ ] policy_evidence writes to correct runtime paths

Policy Decision Correctness:
[ ] unknown role → BLOCK
[ ] unknown tool → BLOCK
[ ] unknown model → BLOCK
[ ] blocked tool → BLOCK
[ ] blocked effect → BLOCK
[ ] requires approval → NEEDS_APPROVAL
[ ] requires governance → NEEDS_GOVERNANCE
[ ] requires sandbox → NEEDS_SANDBOX_CHECK
[ ] known role + known tool + allowed effect + no gate → ALLOW

Integration:
[ ] sandbox integration wired
[ ] initiator integration handles absence gracefully

Negative:
[ ] unknown role blocked
[ ] unknown tool blocked
[ ] unknown model blocked
[ ] blocked tool blocked
[ ] blocked effect blocked
[ ] missing capability blocked
[ ] network blocked by default
[ ] git write blocked by default
[ ] hosted model blocked by default
[ ] model cannot command/tool/write

Evidence:
[ ] policy_decisions.jsonl written
[ ] policy_violations.jsonl written
[ ] latest_policy_decision.json written
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 33. Final Sign-Off Template

Use this after implementation validation.

```text
Policy / Capability Registry Validation — Commit <hash>

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
- module verification (models): PASS/FAIL
- default policy checks: PASS/FAIL
- role matrix checks: PASS/FAIL
- capability policy checks: PASS/FAIL
- tool policy checks: PASS/FAIL
- model policy checks: PASS/FAIL
- decision engine checks: PASS/FAIL
- registry checks: PASS/FAIL
- evidence checks: PASS/FAIL
- policy decision correctness: PASS/FAIL
- sandbox integration: PASS/FAIL
- initiator integration: PASS/FAIL
- negative-test coverage: PASS/FAIL
- source mutation check: PASS/FAIL

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

# 34. Final Rating

This v5 review / DoD document is rated:

```text
10/10
```

Reason:

```text
Complete post-implementation review and Definition of Done for the Policy / Capability Registry layer.
Covers all 16 Python source files, 9 JSON schemas, 15 test files, and runtime artifacts under .agentx-init/policies/.
Includes full module verification checklists for models, defaults, role matrix, capability policy, tool policy, model policy,
decision engine, registry, and evidence. Includes schema validation checklists, policy decision correctness checks,
sandbox and initiator integration checklists, negative test checklists, completion evidence checklist, deviation register,
scoring rubric, GO/NO-GO rules, remediation rules, final frozen checklist, and sign-off template.
```
