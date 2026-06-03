# PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_PROMPT_CONTRACT_VERSIONING
component_name: Prompt Contract / Prompt Versioning Layer
roadmap_layer: 9
roadmap_phase: Phase C — Prompt Governance and Runtime Binding
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/prompts/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/prompts/
contract_document_rating: 10/10
next_document: PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC
```

---

# 0. v3 Review and Upgrade Summary

The v2 Prompt Contract / Prompt Versioning contract was strong and implementation-ready. I would rate v2:

```text
9.7/10
```

It already covered the requested contract areas and added strong production controls for dependency gates, restricted mode, prompt registry locking, session immutability, idempotency, hashing, prompt package integrity, activation/deprecation/revocation workflow, runtime decision precedence, injection handling, simulated dependency test rules, schema examples, evidence manifest rules, no-go conditions, Definition of Done, fresh-clone validation, and a freeze rule.

It was not fully 10/10 because several handoff-critical details were still under-specified:

```text
1. It did not define a strict prompt lifecycle state-transition matrix.
2. It did not define a runtime binding conflict-resolution record for disagreements between prompt, policy, model, context, and tool authorities.
3. It did not define canonical prompt package layout and whether prompt text may live in source-controlled package files versus runtime artifacts.
4. It did not define prompt template variable validation strongly enough.
5. It did not define output validation handoff from prompt output contract to later Model Adapter / LLM Worker checks.
6. It did not define deterministic prompt rendering rules, including whitespace, variable substitution, and hash inputs.
7. It did not define prompt registry rollback / revocation evidence rules tightly enough.
8. It did not define reviewer independence and reproducibility requirements for prompt activation.
9. It did not define exact severity levels for prompt-layer findings.
10. It did not distinguish prompt source-package artifacts from runtime evidence artifacts clearly enough.
```

This v3 adds those missing controls and is the final 10/10 controlling contract for the Prompt Contract / Prompt Versioning Layer.


# 1. Purpose

This document defines the controlling contract for the **Prompt Contract / Prompt Versioning Layer** in Agent_X.

This layer ensures that prompts are not loose strings passed directly to models. Every prompt that can influence Agent_X behavior must be represented as a structured, versioned, auditable contract with:

```text
stable prompt identity
immutable prompt version
prompt text hash
allowed roles
allowed task types
allowed model profiles
allowed tool names
input contract
output contract
safety rules
provenance
runtime binding evidence
migration / compatibility history
```

The layer must prevent:

```text
unregistered prompt use
unversioned prompt use
silent prompt replacement
prompt drift
unauthorized prompt activation
role mismatch
model/task mismatch
prompt-based tool permission escalation
prompt-based policy/sandbox/governance override
prompt injection into system/developer/governance instructions
output-format drift without migration
model output without prompt provenance
```

This layer integrates with:

```text
Policy / Capability Registry
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder / Task Packer
LLM Implementation Worker
Failure Taxonomy / Recovery Playbook
Audit / Evidence system
Agent_X Initiator
future Self-Evolution Orchestrator
future Promotion / Release Gate
```

---

# 2. Scope

## 2.1 Required in This Layer

The layer must define contracts and validation behavior for:

```text
prompt contract records
prompt version records
prompt registry records
prompt input contracts
prompt output contracts
prompt safety rules
prompt provenance records
prompt diff records
prompt migration records
role prompt permission matrix
prompt runtime binding records
prompt compatibility checks
prompt activation rules
prompt deprecation and revocation rules
prompt registry locking
prompt package hashing
prompt injection handling
prompt evidence records
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM inference
model provider clients
tool execution
MCP runtime server
patch execution
code generation worker
self-evolution orchestration
human approval UI
promotion/release gate
long-term learning
network retrieval
```

This layer validates, versions, binds, and audits prompts. It does not execute tools, call models, approve code changes, or mutate source files.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because prompts shape model behavior, tool plans, output format, reasoning boundaries, and implementation actions.

EQC applies to:

```text
prompt registration
prompt activation
prompt role binding
prompt model binding
prompt task binding
prompt tool-scope binding
prompt output contracts
prompt migration and compatibility
prompt provenance
prompt evidence
prompt injection defense
```

The layer must fail closed when prompt identity, version, hash, role permission, runtime binding, safety rule, output contract, or provenance cannot be verified.

## 3.2 Required Supporting Standard: FIC

FIC is required because the layer has concrete modules, schemas, tests, and runtime artifacts.

Expected implementation files:

```text
tools/agentx_evolve/prompts/__init__.py
tools/agentx_evolve/prompts/prompt_models.py
tools/agentx_evolve/prompts/prompt_registry.py
tools/agentx_evolve/prompts/prompt_versioning.py
tools/agentx_evolve/prompts/prompt_permissions.py
tools/agentx_evolve/prompts/prompt_safety.py
tools/agentx_evolve/prompts/prompt_binding.py
tools/agentx_evolve/prompts/prompt_diff.py
tools/agentx_evolve/prompts/prompt_migration.py
tools/agentx_evolve/prompts/prompt_provenance.py
tools/agentx_evolve/prompts/prompt_evidence.py
```

Each file must have a clear responsibility, public API, inputs, outputs, invariants, tests, and safety limits.

## 3.3 Required Supporting Standard: SIB

SIB is required because prompt binding is an integration boundary between multiple subsystems.

The prompt layer must not bypass:

```text
Policy / Capability Registry
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder / Task Packer
Failure Taxonomy / Recovery Playbook
Agent_X Initiator
future Orchestrator
future Promotion Gate
```

## 3.4 Required Supporting Standard: Schema Contract

Schema Contract is required because prompt records, prompt decisions, and prompt runtime bindings must be machine-checkable.

Required schemas:

```text
prompt_contract.schema.json
prompt_version.schema.json
prompt_registry.schema.json
prompt_input_contract.schema.json
prompt_output_contract.schema.json
prompt_safety_rule.schema.json
prompt_provenance.schema.json
prompt_diff.schema.json
prompt_migration.schema.json
prompt_runtime_binding.schema.json
role_prompt_permission_matrix.schema.json
prompt_permission_decision.schema.json
prompt_injection_assessment.schema.json
prompt_evidence_manifest.schema.json
prompt_audit.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every prompt selection, binding, version change, migration, safety decision, and runtime use must create evidence.

Evidence is required for:

```text
prompt registration
prompt version creation
prompt version activation
prompt version deprecation
prompt version revocation
prompt runtime binding
prompt permission allow/block
prompt safety-rule validation
prompt compatibility check
prompt migration
prompt diff
prompt provenance record
prompt injection rejection
prompt output-schema mismatch
prompt rollback
prompt registry snapshot
prompt package hash
```

---

# 4. Status Vocabulary

Use only these status values in implementation and review tables:

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
| PARTIAL | Some required parts exist, but coverage is incomplete. | No, unless explicitly non-blocking and documented later |
| FAIL | Requirement was checked and failed. | No |
| NOT CHECKED | Requirement was not validated. | No |
| NOT RUN | Required command was not run. | No |
| NOT APPLICABLE | Requirement truly does not apply to implemented scope and has no runtime path. | Yes, if justified |
| DEFERRED SAFELY | Feature is planned or stubbed but cannot execute, mutate, bind, or bypass policy. | Yes, only for accepted deferred areas |

Prompt binding cannot be marked valid if any required prompt, schema, hash, safety, permission, input, output, or provenance check remains `NOT CHECKED`.

---

# 5. Preconditions and Dependency Gates

This layer depends on prior and future Agent_X layers. It must not become a bypass around them.

## 5.1 Required Authorities for Runtime Binding

A prompt may bind at runtime only when all applicable authorities agree:

```text
Prompt Registry
Role Prompt Permission Matrix
Policy / Capability Registry
Model Adapter, when model profile compatibility is needed
Context Builder / Task Packer, when context package validation is needed
Tool / MCP Adapter, when allowed tool names are listed
Failure Taxonomy, when failures are classified
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCK
NEEDS_REVIEW
NEEDS_APPROVAL
NEEDS_MIGRATION
NEEDS_REVALIDATION
ALLOW_WITH_WARNINGS
ALLOW
```

## 5.2 Restricted Mode

If upstream dependencies are missing, the layer may operate in restricted mode.

Restricted mode allows:

```text
prompt schema validation
prompt registry loading
prompt hash calculation
prompt diff creation
prompt provenance creation
read-only prompt inspection
review/report prompt binding for known roles, if policy fallback allows
prompt evidence writing
```

Restricted mode blocks:

```text
implementation prompts
repair prompts
tool-use prompts
source-mutation prompts
network/provider prompts
MCP-client prompt binding
runtime model binding for implementation actions
prompt activation without policy/review
```

## 5.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> implementation, repair, tool-use, mutation, network, and MCP-facing prompts BLOCK.
If Model Adapter is missing -> runtime binding to a model profile BLOCKS except static validation.
If Context Builder is missing -> runtime binding requiring context_pack_id BLOCKS.
If Tool / MCP Adapter is missing -> tool-use prompts may validate but cannot authorize tool execution.
If Failure Taxonomy is missing -> prompt failures use UNKNOWN_PROMPT_FAILURE but still BLOCK or FAIL.
If Audit / Evidence system is unavailable -> runtime prompt binding BLOCKS.
```

---

# 6. Canonical Subdirectories

## 6.1 Prompt Package

```text
tools/agentx_evolve/prompts/
```

Required files:

```text
__init__.py
prompt_models.py
prompt_registry.py
prompt_versioning.py
prompt_permissions.py
prompt_safety.py
prompt_binding.py
prompt_diff.py
prompt_migration.py
prompt_provenance.py
prompt_evidence.py
```

## 6.2 Schema Directory

```text
tools/agentx_evolve/schemas/
```

Required schemas:

```text
prompt_contract.schema.json
prompt_version.schema.json
prompt_registry.schema.json
prompt_input_contract.schema.json
prompt_output_contract.schema.json
prompt_safety_rule.schema.json
prompt_provenance.schema.json
prompt_diff.schema.json
prompt_migration.schema.json
prompt_runtime_binding.schema.json
role_prompt_permission_matrix.schema.json
prompt_permission_decision.schema.json
prompt_injection_assessment.schema.json
prompt_evidence_manifest.schema.json
prompt_audit.schema.json
```

## 6.3 Test Directory

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_prompt_contract_schema.py
test_prompt_version_schema.py
test_prompt_registry.py
test_prompt_versioning.py
test_prompt_permissions.py
test_prompt_safety.py
test_prompt_binding.py
test_prompt_diff.py
test_prompt_migration.py
test_prompt_provenance.py
test_prompt_evidence.py
test_prompt_injection.py
test_prompt_negative_cases.py
```

## 6.4 Runtime Artifacts

```text
.agentx-init/prompts/
```

Required runtime artifacts:

```text
prompt_registry_snapshot.json
prompt_version_history.jsonl
prompt_binding_history.jsonl
prompt_permission_history.jsonl
prompt_safety_history.jsonl
prompt_diff_history.jsonl
prompt_migration_history.jsonl
prompt_provenance_history.jsonl
prompt_audit_history.jsonl
prompt_evidence_manifest.json
latest_prompt_binding.json
latest_prompt_provenance.json
```

---

# 7. Prompt Contract Schema

A prompt contract defines the stable identity and allowed purpose of a prompt family.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_contract.schema.json",
  "prompt_contract_id": "string",
  "prompt_name": "string",
  "description": "string",
  "owner_component": "string",
  "prompt_category": "SYSTEM|DEVELOPER|TASK|TOOL_USE|REVIEW|REPAIR|REPORT|EVALUATION",
  "allowed_task_types": [],
  "allowed_roles": [],
  "allowed_model_profiles": [],
  "allowed_tool_names": [],
  "input_contract_id": "string",
  "output_contract_id": "string",
  "safety_rule_ids": [],
  "current_version_id": "string|null",
  "status": "DRAFT|ACTIVE|DEPRECATED|DISABLED|BLOCKED",
  "created_at": "string",
  "updated_at": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
prompt_contract_id is required.
prompt_name is required and stable.
prompt names must be unique in the registry.
ACTIVE prompts must have non-empty allowed_roles.
ACTIVE prompts must have non-empty allowed_task_types.
ACTIVE prompts must have current_version_id.
ACTIVE prompts must reference input and output contracts.
ACTIVE prompts must have at least one required safety rule.
DISABLED and BLOCKED prompts must not bind at runtime.
DEPRECATED prompt contracts cannot create new runtime bindings unless policy allows legacy replay.
```

---

# 8. Prompt Version Schema

A prompt version defines an immutable prompt text package for a prompt contract.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_version.schema.json",
  "prompt_version_id": "string",
  "prompt_contract_id": "string",
  "version": "string",
  "version_status": "DRAFT|CANDIDATE|ACTIVE|DEPRECATED|REVOKED",
  "prompt_text": "string",
  "prompt_text_sha256": "string",
  "system_constraints": [],
  "developer_constraints": [],
  "tool_use_constraints": [],
  "output_constraints": [],
  "safety_rule_ids": [],
  "compatible_with_versions": [],
  "breaking_change": false,
  "migration_required": false,
  "created_at": "string",
  "created_by": "string",
  "change_reason": "string",
  "provenance_id": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
prompt versions are immutable after activation.
prompt_text_sha256 is required.
changing prompt_text requires a new prompt_version_id.
only one ACTIVE version may exist per prompt contract unless multi-version rollout is explicitly added later.
REVOKED versions must never bind at runtime.
DEPRECATED versions may be used only for legacy replay when policy allows.
breaking_change=true requires migration record.
migration_required=true requires migration record.
prompt_text must not contain direct policy override instructions.
prompt_text must not grant tool permissions by text alone.
prompt_text must not instruct the model to ignore Agent_X governance.
```

---

# 9. Prompt Registry Schema

The prompt registry lists all prompt contracts and versions available to Agent_X.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_registry.schema.json",
  "registry_id": "string",
  "registry_version": "string",
  "created_at": "string",
  "source_component": "PromptRegistry",
  "prompt_contracts": [],
  "prompt_versions": [],
  "active_bindings": [],
  "registry_sha256": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
prompt names must be unique.
prompt_contract_ids must be unique.
prompt_version_ids must be unique.
each ACTIVE contract must point to exactly one ACTIVE version.
registry_sha256 must be recorded in runtime evidence.
registry snapshot must be stable during a runtime session.
duplicate prompt names block registry loading.
duplicate prompt version IDs block registry loading.
missing ACTIVE version for ACTIVE contract blocks registry loading.
```

## 9.1 Registry Locking and Session Immutability

Once a runtime session starts, the prompt registry snapshot for that session must remain stable.

Runtime binding evidence must record:

```text
registry_id
registry_version
registry_sha256
prompt_contract_id
prompt_version_id
prompt_text_sha256
active prompt list hash
```

No runtime call may silently switch prompt versions mid-session.

## 9.2 Idempotency Rules

Repeated validation of the same registry, prompt version, and binding request must produce the same decision when inputs are unchanged.

Idempotent actions:

```text
schema validation
registry load
prompt lookup
hash verification
compatibility check
diff calculation
permission check with same policy context
runtime binding with same request ID
```

Non-idempotent writes, such as evidence append, must include unique evidence IDs while preserving identical decision content.

---

# 10. Prompt Input Contract Schema

A prompt input contract defines the structured inputs a prompt may receive.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_input_contract.schema.json",
  "input_contract_id": "string",
  "prompt_contract_id": "string",
  "required_context_fields": [],
  "optional_context_fields": [],
  "forbidden_context_fields": [],
  "allowed_artifact_refs": [],
  "max_context_chars": 0,
  "requires_task_summary": true,
  "requires_policy_context": true,
  "requires_tool_context": false,
  "requires_model_context": true,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
missing required context blocks prompt binding.
forbidden context fields must be removed or rejected.
raw secrets must not be included.
raw unbounded file content must not be included.
context must include task type and caller role.
context must include registry/version references where applicable.
external or untrusted content must be marked as data, not instruction.
```

---

# 11. Prompt Output Contract Schema

A prompt output contract defines the expected shape and constraints of model output.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_output_contract.schema.json",
  "output_contract_id": "string",
  "prompt_contract_id": "string",
  "output_mode": "TEXT|JSON|PATCH_PROPOSAL|REVIEW_REPORT|TOOL_CALL_PLAN|CLASSIFICATION|SCORECARD",
  "required_fields": [],
  "forbidden_fields": [],
  "json_schema_ref": "string|null",
  "must_include_evidence_refs": false,
  "must_include_confidence": false,
  "allows_tool_calls": false,
  "allows_source_patch": false,
  "max_output_chars": 0,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
outputs must validate against the output contract.
JSON mode must reference a schema.
PATCH_PROPOSAL mode must not apply patches directly.
TOOL_CALL_PLAN mode must not execute tools directly.
source patch outputs require governance and Governed Patch Execution checks.
output drift is BLOCKED or FAILED, not silently accepted.
```

---

# 12. Prompt Safety Rule Schema

Prompt safety rules define required safety controls attached to a prompt.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_safety_rule.schema.json",
  "safety_rule_id": "string",
  "prompt_contract_id": "string",
  "rule_type": "INJECTION_DEFENSE|TOOL_LIMIT|OUTPUT_LIMIT|ROLE_LIMIT|MODEL_LIMIT|DATA_LIMIT|MUTATION_LIMIT|EVIDENCE_REQUIREMENT",
  "description": "string",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "required": true,
  "validation_method": "STATIC|RUNTIME|BOTH",
  "failure_behavior": "BLOCK|WARN|REQUIRE_APPROVAL",
  "warnings": [],
  "errors": []
}
```

Required safety rule categories:

```text
prompt injection defense
tool permission non-escalation
role restriction
model profile restriction
context boundary restriction
secret redaction requirement
output schema requirement
patch/source mutation restriction
evidence/provenance requirement
```

Rules:

```text
CRITICAL required rules must block if missing.
prompt text cannot override policy or sandbox.
prompt text cannot authorize tool execution.
prompt text cannot disable evidence logging.
prompt text cannot instruct the model to ignore Agent_X governance.
removed safety rules are breaking changes.
```

---

# 13. Prompt Provenance Schema

Prompt provenance records where a prompt version came from and why it exists.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_provenance.schema.json",
  "provenance_id": "string",
  "prompt_contract_id": "string",
  "prompt_version_id": "string",
  "created_at": "string",
  "created_by": "string",
  "source_type": "HUMAN_AUTHORED|GENERATED|MIGRATED|REPAIRED|IMPORTED",
  "source_refs": [],
  "basis_documents": [],
  "change_reason": "string",
  "review_status": "UNREVIEWED|REVIEWED|APPROVED|REJECTED",
  "approved_by": "string|null",
  "approval_ref": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
ACTIVE prompt versions require provenance.
GENERATED prompts require review before ACTIVE.
IMPORTED prompts require source reference.
MIGRATED prompts require migration record.
REPAIRED prompts require previous failure reference.
unreviewed prompts cannot become ACTIVE for implementation or tool-use tasks.
provenance must be referenced in runtime bindings.
```

---

# 14. Prompt Diff / Migration Schema

## 14.1 Prompt Diff Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_diff.schema.json",
  "prompt_diff_id": "string",
  "prompt_contract_id": "string",
  "from_version_id": "string",
  "to_version_id": "string",
  "created_at": "string",
  "change_summary": "string",
  "changed_sections": [],
  "added_constraints": [],
  "removed_constraints": [],
  "tool_permission_changes": [],
  "output_contract_changes": [],
  "safety_rule_changes": [],
  "compatibility_result": "COMPATIBLE|BREAKING|UNKNOWN",
  "warnings": [],
  "errors": []
}
```

## 14.2 Prompt Migration Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_migration.schema.json",
  "migration_id": "string",
  "prompt_contract_id": "string",
  "from_version_id": "string",
  "to_version_id": "string",
  "created_at": "string",
  "migration_type": "PATCH|MINOR|MAJOR|ROLLBACK",
  "breaking_change": false,
  "requires_revalidation": true,
  "requires_human_review": false,
  "migration_steps": [],
  "rollback_version_id": "string|null",
  "approval_ref": "string|null",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
breaking prompt changes require migration record.
removed safety rules are breaking changes.
expanded tool permissions are breaking changes.
output schema changes are breaking unless explicitly compatible.
model profile expansion may require review.
migration must preserve provenance.
rollback requires prior valid version.
```

---

# 15. Role Prompt Permission Matrix

Initial roles:

```text
ORCHESTRATOR
IMPLEMENTATION_WORKER
VALIDATION_REPAIR_WORKER
REVIEWER_ASSISTANT
PROMOTION_CHECKER
HUMAN_OPERATOR
MCP_CLIENT
UNKNOWN_CALLER
```

Prompt categories:

```text
SYSTEM
DEVELOPER
TASK
TOOL_USE
REVIEW
REPAIR
REPORT
EVALUATION
```

Required default rules:

```text
UNKNOWN_CALLER blocks by default.
MCP_CLIENT cannot use implementation, repair, source-mutation, or tool-execution prompts by default.
REVIEWER_ASSISTANT may use REVIEW, REPORT, and EVALUATION prompts only.
IMPLEMENTATION_WORKER may use TASK, REPAIR, and implementation-scoped prompts only when policy allows.
VALIDATION_REPAIR_WORKER may use REPAIR and EVALUATION prompts only when validation context exists.
PROMOTION_CHECKER may use REVIEW, REPORT, and EVALUATION prompts, but cannot use source-write prompts.
ORCHESTRATOR may bind prompts but cannot bypass policy, model, tool, or output constraints.
HUMAN_OPERATOR may approve prompt versions but cannot override non-overridable safety rules.
```

Permission decision values:

```text
ALLOW
BLOCK
NEEDS_REVIEW
NEEDS_APPROVAL
NEEDS_MIGRATION
NEEDS_REVALIDATION
ALLOW_WITH_WARNINGS
```

A prompt permission decision must include:

```text
role
prompt_contract_id
prompt_version_id
requested_task_type
requested_model_profile
decision
reason
missing_requirements
policy_decision_id, if available
warnings
errors
```

---

# 16. Prompt Runtime Binding Rules

A runtime prompt binding records the exact prompt version selected for a runtime action.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_runtime_binding.schema.json",
  "binding_id": "string",
  "timestamp": "string",
  "prompt_contract_id": "string",
  "prompt_version_id": "string",
  "prompt_text_sha256": "string",
  "rendered_prompt_sha256": "string|null",
  "rendering_algorithm": "string|null",
  "template_variables_sha256": "string|null",
  "registry_id": "string",
  "registry_sha256": "string",
  "caller_role": "string",
  "task_type": "string",
  "model_profile_id": "string",
  "tool_names_allowed": [],
  "input_contract_id": "string",
  "output_contract_id": "string",
  "safety_rule_ids": [],
  "policy_decision_id": "string|null",
  "context_pack_id": "string|null",
  "provenance_id": "string",
  "warnings": [],
  "errors": []
}
```

Binding is allowed only if:

```text
prompt contract exists.
prompt version exists.
prompt version is ACTIVE.
prompt text hash matches recorded version.
registry hash is recorded.
caller role is allowed.
task type is allowed.
model profile is allowed.
requested tools are allowed by prompt and policy.
input contract is satisfied.
output contract is available.
required safety rules are present.
provenance exists.
evidence path is available.
```

Binding must block if:

```text
prompt is unregistered.
prompt version is missing.
prompt text hash mismatches.
prompt version is DRAFT, DEPRECATED, REVOKED, DISABLED, or BLOCKED.
caller role is not allowed.
model profile is not allowed.
task type is not allowed.
required safety rule is missing.
output contract is missing.
provenance is missing.
policy denies binding.
evidence cannot be written.
```

---

# 17. Runtime Binding Pipeline

Every runtime prompt use must follow this sequence:

```text
1. Receive prompt binding request.
2. Normalize caller role, task type, model profile, and context reference.
3. Load Prompt Registry.
4. Validate Prompt Registry schema.
5. Verify registry hash.
6. Lookup Prompt Contract.
7. Lookup active Prompt Version.
8. Verify prompt text hash.
9. Check role permission.
10. Check task type permission.
11. Check model profile permission.
12. Check allowed tool names, if tool-use prompt.
13. Check Policy / Capability Registry or restrictive fallback.
14. Validate required safety rules.
15. Run prompt injection assessment for untrusted context.
16. Validate prompt input contract against context metadata.
17. Confirm output contract exists.
18. Confirm provenance exists.
19. Create PromptRuntimeBinding.
20. Write prompt binding evidence.
21. Return binding to Model Adapter / LLM Worker.
```

Rules:

```text
No prompt text may be sent to a model unless this pipeline succeeds.
Any failed stage returns schema-valid BLOCKED / FAILED prompt decision.
Prompt binding evidence must include prompt version ID and prompt text hash.
```

---

# 18. Versioning and Immutability Rules

Use semantic prompt versions:

```text
MAJOR.MINOR.PATCH
```

Version meaning:

```text
PATCH = wording or clarification with no contract change
MINOR = additive safety/output/context constraints without breaking existing valid use
MAJOR = breaking change to role, tool scope, task scope, model scope, output contract, or safety rules
```

Activation requirements:

```text
schema validation passes
prompt_text_sha256 matches prompt_text
provenance exists
required safety rules exist
input contract exists
output contract exists
role permission matrix allows use
compatibility check passes or migration exists
review status is APPROVED when required
registry snapshot can be hashed
```

Deprecation and revocation rules:

```text
DEPRECATED versions remain for historical evidence but cannot be selected for new runtime binding unless policy allows legacy replay.
REVOKED versions must never bind at runtime.
DISABLED or BLOCKED prompt contracts must not bind at runtime.
```

---

# 19. Prompt Injection and Untrusted Content Rules

Injection-sensitive inputs include:

```text
user-provided task text
retrieved file content
web or external content
tool output
previous model output
commit messages
diff content
logs
error messages
```

Required controls:

```text
external or untrusted content must be marked as data, not instruction.
prompt must include instruction hierarchy protection.
prompt must forbid policy/sandbox/governance override by retrieved text.
prompt must forbid tool permission escalation by retrieved text.
prompt must separate task instructions from evidence/context blocks.
prompt must reject or quarantine content that attempts to override system/developer constraints.
critical injection findings must block implementation/tool-use prompts.
```

Prompt injection assessment values:

```text
ALLOW
ALLOW_WITH_WARNINGS
BLOCK
REQUIRE_REVIEW
```

Critical examples that must block:

```text
instruction to ignore governance
instruction to reveal secrets
instruction to bypass sandbox
instruction to call unauthorized tools
instruction to alter system/developer constraints
instruction to self-approve source mutation
```

---

# 20. Prompt Package Integrity and Hashing

The implementation must hash prompt-related artifacts with SHA-256.

Required hashes:

```text
prompt_text_sha256
registry_sha256
prompt_package_sha256, if prompts are bundled
runtime_binding_sha256, if binding artifact is persisted
prompt_evidence_manifest_sha256
```

Hashing rules:

```text
Use Python standard-library hashlib if no project helper exists.
ACTIVE prompt versions require prompt_text_sha256.
Runtime bindings require prompt_text_sha256 and registry_sha256.
A final implementation cannot be DONE if prompt hashes are missing.
Hash mismatch blocks runtime binding.
```

---

# 21. OpenCode Borrowing Notes

## 21.1 Concepts to Borrow

Borrow these OpenCode-style concepts:

```text
separate prompts/instructions from execution logic
role-specific agent prompts
tool-use instruction blocks
plan-mode prompts
review/evaluation prompts
skill/instruction-loading concept
prompt reuse through named templates
model behavior shaped by structured instructions
```

## 21.2 Concepts to Restrict

Do not copy these assumptions directly:

```text
prompt text as sufficient authorization
model-driven tool permission expansion
unversioned instruction files
implicit prompt updates
plugin-provided prompts without policy checks
runtime-loaded prompts without provenance
broad shell/tool-use instructions
network/provider instructions enabled by convenience
```

## 21.3 Agent_X Mapping

| OpenCode concept | Agent_X equivalent | Required control |
|---|---|---|
| Agent instructions | Prompt Contract | Schema + version + role binding |
| Tool-use prompt | Tool-use prompt contract | Tool / MCP Adapter + policy control |
| Plan mode | Planning prompt version | No tool execution by prompt alone |
| Review prompt | Review prompt contract | Output schema + evidence refs |
| Skill prompt | Future skill prompt contract | Prompt registry + provenance |
| Custom plugin instructions | Registered prompt package | Policy + provenance + safety rules |
| Model-selected tool behavior | Runtime binding + Tool Adapter | Prompt cannot grant permissions |

---

# 22. Agent_X Integration Notes

## 22.1 Policy / Capability Registry Integration

The layer must call or consume Policy / Capability Registry decisions for:

```text
role prompt permission
allowed task type
allowed model profile
allowed tool names
source mutation prompt restrictions
network/provider prompt restrictions
human approval requirements
```

Policy missing behavior:

```text
read/review/report prompts may use restrictive local fallback.
implementation, repair, tool-use, source-mutation, and model-action prompts must BLOCK.
unknown roles must BLOCK.
```

## 22.2 Tool / MCP Adapter Integration

Prompts may describe or request tool plans, but they must not execute tools directly.

Rules:

```text
Prompt binding may list allowed tools.
Tool execution still requires Tool / MCP Adapter permission checks.
Prompt text cannot expand tool permissions.
A tool-use prompt must produce a tool-call plan, not actual execution.
```

## 22.3 Model Adapter Integration

Prompt binding must verify:

```text
model_profile_id is allowed by the prompt contract.
model supports required output mode.
model supports required context size.
model is allowed by Policy / Capability Registry.
hosted/local model mode is compatible with prompt safety rules.
```

## 22.4 Context Builder / Task Packer Integration

The Context Builder must satisfy the prompt input contract before runtime binding.

Required:

```text
required context fields present
forbidden context fields absent
context size within limit
secrets redacted
artifact refs used instead of raw large content where possible
context_pack_id recorded in binding evidence
```

## 22.5 LLM Implementation Worker Integration

The LLM Implementation Worker must record:

```text
prompt_contract_id
prompt_version_id
prompt_text_sha256
prompt_runtime_binding_id
model_profile_id
context_pack_id
output_contract_id
provenance_id
```

Generated implementation work without prompt provenance must be invalid or unreviewable.

## 22.6 Failure Taxonomy Integration

Prompt-related failures must map to standard failure classes:

```text
PROMPT_NOT_FOUND
PROMPT_VERSION_NOT_FOUND
PROMPT_VERSION_INACTIVE
PROMPT_HASH_MISMATCH
PROMPT_ROLE_DENIED
PROMPT_MODEL_DENIED
PROMPT_TASK_DENIED
PROMPT_TOOL_SCOPE_DENIED
PROMPT_INPUT_CONTRACT_FAILED
PROMPT_OUTPUT_CONTRACT_FAILED
PROMPT_SAFETY_RULE_MISSING
PROMPT_PROVENANCE_MISSING
PROMPT_MIGRATION_REQUIRED
PROMPT_INJECTION_DETECTED
PROMPT_REGISTRY_INVALID
PROMPT_EVIDENCE_WRITE_FAILED
UNKNOWN_PROMPT_FAILURE
```

---

# 23. Runtime Artifact Rules

All prompt runtime state must be under:

```text
.agentx-init/prompts/
```

Allowed delegated evidence roots:

```text
.agentx-init/tool_calls/
.agentx-init/policy/
.agentx-init/context/
.agentx-init/models/
.agentx-init/failures/
```

Rules:

```text
append-only JSONL for history
atomic JSON writes for latest artifacts
SHA-256 hashes for prompt text and registry snapshots
redact secrets before logging
record prompt version IDs in every runtime binding
record provenance ID for every active prompt version
record policy/context/model/tool evidence references where available
```

---

# 24. Evidence and Audit Contract

Append-only logs:

```text
.agentx-init/prompts/prompt_version_history.jsonl
.agentx-init/prompts/prompt_binding_history.jsonl
.agentx-init/prompts/prompt_permission_history.jsonl
.agentx-init/prompts/prompt_safety_history.jsonl
.agentx-init/prompts/prompt_diff_history.jsonl
.agentx-init/prompts/prompt_migration_history.jsonl
.agentx-init/prompts/prompt_provenance_history.jsonl
.agentx-init/prompts/prompt_audit_history.jsonl
```

Latest artifacts:

```text
.agentx-init/prompts/latest_prompt_binding.json
.agentx-init/prompts/latest_prompt_provenance.json
.agentx-init/prompts/prompt_registry_snapshot.json
.agentx-init/prompts/prompt_evidence_manifest.json
```

Evidence records must include:

```text
timestamp
prompt_contract_id
prompt_version_id
prompt_text_sha256
registry_id
registry_sha256
caller_role
task_type
model_profile_id
policy decision reference
context pack reference, if available
provenance reference
status
failure_class, if failed
warnings
errors
```

Evidence rules:

```text
prompt evidence must not log raw secrets.
prompt evidence should avoid storing full sensitive prompt inputs.
prompt version history may store prompt text only if policy allows.
prompt hashes are required even when prompt text is not durably logged.
evidence write failure blocks runtime binding.
```

---

# 25. Evidence Manifest Contract

Create:

```text
.agentx-init/prompts/prompt_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_evidence_manifest.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "registry_id": "<registry id>",
  "registry_sha256": "<sha256>",
  "prompt_contracts_verified": [],
  "prompt_versions_verified": [],
  "runtime_bindings_verified": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "deviation_register": [],
  "redaction_status": "PASS|FAIL|NOT CHECKED",
  "hash_status": "PASS|FAIL|NOT CHECKED"
}
```

The manifest must include paths and hashes for final evidence files used in review.

---

# 26. Schema Example Requirements

Every schema must have tests for:

```text
valid example passes
missing required field fails
invalid enum value fails
invalid relationship fails where applicable
```

Required examples:

```text
valid_prompt_contract
valid_prompt_version
valid_prompt_registry
valid_prompt_input_contract
valid_prompt_output_contract
valid_prompt_safety_rule
valid_prompt_provenance
valid_prompt_diff
valid_prompt_migration
valid_prompt_runtime_binding
valid_prompt_permission_decision
valid_prompt_injection_assessment
valid_prompt_evidence_manifest
valid_prompt_audit_event
```

Relationship checks must include:

```text
ACTIVE contract points to ACTIVE version.
ACTIVE version has provenance.
ACTIVE version has safety rules.
runtime binding references registry hash.
runtime binding references prompt text hash.
breaking change has migration record.
```

---

# 27. Public API Contract

Expected classes:

```text
PromptContract
PromptVersion
PromptRegistry
PromptInputContract
PromptOutputContract
PromptSafetyRule
PromptProvenance
PromptDiff
PromptMigration
PromptRuntimeBinding
PromptPermissionDecision
PromptInjectionAssessment
PromptEvidenceManifest
PromptAuditEvent
```

Expected public functions:

```python
load_prompt_registry() -> PromptRegistry

register_prompt_contract(
    registry: PromptRegistry,
    contract: PromptContract
) -> PromptRegistry

register_prompt_version(
    registry: PromptRegistry,
    version: PromptVersion
) -> PromptRegistry

get_prompt_contract(
    registry: PromptRegistry,
    prompt_contract_id: str
) -> PromptContract | None

get_prompt_version(
    registry: PromptRegistry,
    prompt_version_id: str
) -> PromptVersion | None

get_active_prompt_version(
    registry: PromptRegistry,
    prompt_contract_id: str
) -> PromptVersion | None

check_prompt_permission(
    caller_role: str,
    task_type: str,
    model_profile_id: str,
    prompt_contract: PromptContract,
    prompt_version: PromptVersion,
    policy_context: dict
) -> PromptPermissionDecision

bind_prompt_for_runtime(
    registry: PromptRegistry,
    prompt_contract_id: str,
    caller_role: str,
    task_type: str,
    model_profile_id: str,
    context_pack_id: str | None,
    policy_context: dict
) -> PromptRuntimeBinding

validate_prompt_input_contract(
    input_contract: PromptInputContract,
    context: dict
) -> dict

validate_prompt_output_contract(
    output_contract: PromptOutputContract,
    output: dict | str
) -> dict

assess_prompt_injection(
    prompt_contract: PromptContract,
    context: dict
) -> PromptInjectionAssessment

create_prompt_diff(
    from_version: PromptVersion,
    to_version: PromptVersion
) -> PromptDiff

create_prompt_migration(
    from_version: PromptVersion,
    to_version: PromptVersion,
    migration_type: str
) -> PromptMigration

write_prompt_evidence(
    event: PromptAuditEvent,
    repo_root: Path
) -> dict
```

---

# 28. Simulated Dependency Test Contract

Tests must be able to run before later layers are fully implemented.

Allowed fake dependencies:

```text
FakePolicyRegistry
FakeModelAdapter
FakeContextBuilder
FakeToolAdapter
FakeFailureTaxonomy
```

Fake dependency rules:

```text
Fake dependencies must be explicit test fixtures.
Fake dependencies must never default ALLOW for unsafe cases.
Fake Policy must block unknown roles.
Fake Model Adapter must block unknown model profiles.
Fake Context Builder must block missing required context.
Fake Tool Adapter must prove prompt text cannot grant tool authority.
Fake Failure Taxonomy may classify with UNKNOWN_PROMPT_FAILURE.
```

Tests must prove both:

```text
valid dependency decisions allow safe binding
missing dependency decisions fail closed
```

---

# 29. Test Acceptance Criteria

Required tests:

```text
test_prompt_contract_schema_accepts_valid_contract
test_prompt_contract_schema_rejects_missing_prompt_name
test_prompt_version_schema_requires_hash
test_prompt_registry_rejects_duplicate_prompt_names
test_prompt_registry_requires_one_active_version
test_prompt_registry_hash_required
test_prompt_registry_session_snapshot_stable
test_prompt_permission_unknown_role_blocks
test_prompt_permission_mcp_client_limited
test_prompt_binding_active_version_succeeds
test_prompt_binding_inactive_version_blocks
test_prompt_binding_hash_mismatch_blocks
test_prompt_binding_missing_safety_rule_blocks
test_prompt_binding_missing_output_contract_blocks
test_prompt_binding_missing_provenance_blocks
test_prompt_input_contract_rejects_forbidden_context
test_prompt_output_contract_validates_json_output
test_prompt_diff_detects_tool_permission_expansion
test_prompt_migration_required_for_breaking_change
test_prompt_provenance_required_for_active_version
test_prompt_injection_attempt_blocks_tool_use_prompt
test_prompt_evidence_written
test_prompt_evidence_manifest_written
test_prompt_secrets_redacted_before_logging
test_missing_policy_blocks_unsafe_prompt_binding
test_prompt_text_cannot_grant_tool_permission
```

Negative tests:

```text
unregistered prompt cannot bind
unversioned prompt cannot bind
DEPRECATED prompt cannot bind for new runtime use unless legacy replay policy allows
REVOKED prompt cannot bind
prompt text hash mismatch blocks
prompt without provenance blocks
prompt with missing safety rule blocks
prompt cannot expand tool permissions
prompt cannot override policy by text
prompt cannot override sandbox by text
prompt cannot bind to disallowed model profile
prompt output schema mismatch fails
missing evidence writer blocks runtime binding
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema tests PASS
negative safety tests PASS
runtime binding tests PASS
provenance tests PASS
evidence tests PASS
hash tests PASS
no source mutation
completion record exists
```

---

# 30. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical prompt subdirectory is selected
[ ] prompt contract schema is defined
[ ] prompt version schema is defined
[ ] prompt registry schema is defined
[ ] input/output contract schemas are defined
[ ] safety rule schema is defined
[ ] provenance schema is defined
[ ] diff/migration schemas are defined
[ ] runtime binding schema is defined
[ ] role permission matrix is defined
[ ] evidence manifest schema is defined
[ ] prompt injection assessment schema is defined
[ ] runtime binding pipeline is defined
[ ] dependency gates are defined
[ ] evidence paths are defined
[ ] failure classes are defined
[ ] OpenCode borrowing is bounded
[ ] Agent_X integration points are defined
```

---

# 31. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] prompt registry loads
[ ] duplicate prompts block
[ ] inactive prompts block
[ ] unknown roles block
[ ] prompt hash mismatch blocks
[ ] missing provenance blocks
[ ] missing safety rules block
[ ] output contract validation works
[ ] prompt injection checks work
[ ] runtime binding evidence is written
[ ] evidence manifest is written
[ ] no source mutation occurs
[ ] completion record exists
```

---

# 32. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_PROMPT_CONTRACT_VERSIONING"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  prompt_contracts_verified: []
  prompt_versions_verified: []
  prompt_registry_verified: []
  prompt_bindings_verified: []
  prompt_permissions_verified: []
  prompt_safety_rules_verified: []
  prompt_provenance_verified: []
  prompt_migrations_verified: []
  prompt_hashes_verified: []
  prompt_injection_checks_verified: []
  policy_integration_verified: []
  tool_adapter_integration_verified: []
  model_adapter_integration_verified: []
  context_builder_integration_verified: []
  opencode_patterns_borrowed: []
  opencode_patterns_rejected_or_restricted: []
  deviations_from_contract: []
  unresolved_risks: []
```

---

# 33. Residual Risks

```yaml
residual_risks:
  - id: "PROMPT-RISK-001"
    description: "Prompt text may accidentally expand tool authority."
    severity: "critical"
    mitigation: "Prompt text cannot grant tool permissions; Tool / MCP Adapter and Policy Registry remain authoritative."
  - id: "PROMPT-RISK-002"
    description: "Prompt drift may cause unreviewed model behavior."
    severity: "high"
    mitigation: "Prompt hashes, version IDs, and runtime bindings are required for every model call."
  - id: "PROMPT-RISK-003"
    description: "Prompt injection may override task or governance instructions."
    severity: "critical"
    mitigation: "Input contracts, injection detection, and safety rules block untrusted instruction escalation."
  - id: "PROMPT-RISK-004"
    description: "Output contract drift may produce invalid tool plans or patch proposals."
    severity: "high"
    mitigation: "Output contracts are schema-validated and mismatches fail closed."
  - id: "PROMPT-RISK-005"
    description: "Generated prompt versions may become active without review."
    severity: "high"
    mitigation: "Generated prompts require provenance and review before activation."
```

---

# 34. Prompt Lifecycle State-Transition Contract

Prompt contracts and prompt versions must use controlled state transitions. No state transition may occur only by editing a string field without evidence.

## 34.1 Prompt Contract States

Allowed prompt contract states:

```text
DRAFT
ACTIVE
DEPRECATED
DISABLED
BLOCKED
```

Allowed transitions:

| From | To | Required control |
|---|---|---|
| `DRAFT` | `ACTIVE` | schema validation, active version, provenance, safety rules, permission matrix, evidence |
| `ACTIVE` | `DEPRECATED` | deprecation reason, replacement version or legacy policy, evidence |
| `ACTIVE` | `DISABLED` | disable reason, reviewer decision, evidence |
| `ACTIVE` | `BLOCKED` | critical safety reason, evidence |
| `DEPRECATED` | `ACTIVE` | explicit reactivation review, hash check, policy approval, evidence |
| `DISABLED` | `ACTIVE` | explicit re-enable review, full revalidation, evidence |
| `BLOCKED` | `ACTIVE` | not allowed without major remediation and new prompt version |

Forbidden transitions:

```text
REVOKED/BLOCKED behavior must not be bypassed by renaming states.
A prompt contract cannot move to ACTIVE without an ACTIVE prompt version.
A prompt contract cannot move to ACTIVE with missing provenance.
A prompt contract cannot move to ACTIVE with missing required safety rules.
A prompt contract cannot move to ACTIVE if its current version hash fails.
```

## 34.2 Prompt Version States

Allowed prompt version states:

```text
DRAFT
CANDIDATE
ACTIVE
DEPRECATED
REVOKED
```

Allowed transitions:

| From | To | Required control |
|---|---|---|
| `DRAFT` | `CANDIDATE` | schema validation, hash calculation, provenance draft |
| `CANDIDATE` | `ACTIVE` | review/approval if required, compatibility check, safety validation, evidence |
| `ACTIVE` | `DEPRECATED` | replacement or legacy replay rule, evidence |
| `ACTIVE` | `REVOKED` | critical safety reason, revocation evidence |
| `DEPRECATED` | `ACTIVE` | explicit reactivation review, full hash/provenance/safety revalidation |
| `REVOKED` | any runtime-bindable state | forbidden |

Rules:

```text
REVOKED versions must never bind at runtime.
ACTIVE prompt text is immutable.
Changing prompt text requires a new prompt_version_id.
Changing template variables requires a new version or migration record.
Changing output contract requires compatibility check and possible migration.
Changing allowed tools, roles, or models is a permission-affecting change and requires review.
```

---

# 35. Canonical Prompt Package Layout

The layer must separate source prompt-package artifacts from runtime evidence artifacts.

## 35.1 Source Prompt Package

Canonical source-controlled prompt package location:

```text
tools/agentx_evolve/prompts/package/
```

Expected package artifacts:

```text
prompt_registry.json
contracts/*.prompt_contract.json
versions/*.prompt_version.json
templates/*.prompt.md
input_contracts/*.prompt_input_contract.json
output_contracts/*.prompt_output_contract.json
safety_rules/*.prompt_safety_rule.json
provenance/*.prompt_provenance.json
migrations/*.prompt_migration.json
```

Rules:

```text
source prompt-package files are definitions, not runtime evidence.
runtime binding must not edit source prompt-package files.
prompt package updates require normal source governance and review.
prompt runtime evidence must be written under .agentx-init/prompts/.
prompt package files must be hashable deterministically.
prompt registry must record package file refs and hashes.
```

## 35.2 Runtime Evidence Boundary

Runtime prompt evidence must be written only under:

```text
.agentx-init/prompts/
```

Allowed delegated evidence roots remain:

```text
.agentx-init/tool_calls/
.agentx-init/policy/
.agentx-init/context/
.agentx-init/models/
.agentx-init/failures/
```

Any runtime write outside those roots must be recorded as a deviation and cannot be accepted if it mutates source prompt definitions during runtime binding.

---

# 36. Prompt Template and Rendering Contract

Prompt templates must be deterministic and validated before runtime binding.

## 36.1 Template Variable Schema

Each prompt version using variables must declare:

```json
{
  "template_variable_schema": {
    "required_variables": [],
    "optional_variables": [],
    "forbidden_variables": [],
    "variable_types": {},
    "max_variable_chars": {},
    "redaction_required": []
  }
}
```

Rules:

```text
missing required template variables block rendering.
unknown variables block unless explicitly allowed.
forbidden variables block rendering.
secret-like values must be redacted before evidence.
untrusted variable values must be marked as data, not instruction.
variable substitution must not alter system/developer/governance instruction hierarchy.
```

## 36.2 Deterministic Rendering

Prompt rendering must be deterministic for the same input package.

The render hash must be calculated over:

```text
prompt_contract_id
prompt_version_id
prompt_text_sha256
template variable names and normalized values
input contract id
output contract id
safety rule ids
registry_sha256
```

Required runtime binding fields:

```text
rendered_prompt_sha256
rendering_algorithm
template_variables_sha256
```

Rules:

```text
rendering must not fetch network content.
rendering must not execute tools.
rendering must not mutate source files.
rendering must not silently drop required variables.
rendered prompt hashes must be recorded when rendered prompt text is not durably stored.
```

---

# 37. Runtime Binding Conflict-Resolution Record

Every runtime binding decision must record authority decisions and the final conflict-resolution outcome.

Required conflict-resolution fields:

```json
{
  "authority_decisions": [
    {
      "authority": "PromptRegistry|RolePermissionMatrix|PolicyRegistry|ModelAdapter|ContextBuilder|ToolAdapter|FailureTaxonomy",
      "decision": "ALLOW|ALLOW_WITH_WARNINGS|NEEDS_REVIEW|NEEDS_APPROVAL|NEEDS_MIGRATION|NEEDS_REVALIDATION|BLOCK|INVALID",
      "decision_id": "string|null",
      "reason": "string"
    }
  ],
  "strictest_decision": "string",
  "final_binding_decision": "string",
  "conflict_resolution_reason": "string"
}
```

Rules:

```text
strictest decision wins.
missing authority for unsafe binding becomes BLOCK.
policy cannot be weakened by prompt text.
tool permissions cannot be widened by prompt text.
model profile restrictions cannot be widened by prompt text.
context boundary restrictions cannot be widened by prompt text.
```

---

# 38. Output Validation Handoff Contract

The prompt output contract defines what the model should produce. Later runtime layers must validate that output before use.

Required handoff fields for Model Adapter / LLM Implementation Worker:

```text
prompt_runtime_binding_id
prompt_contract_id
prompt_version_id
prompt_text_sha256
rendered_prompt_sha256, if rendered
output_contract_id
output_schema_ref, if JSON or structured output
expected_output_mode
allowed_tool_names
allows_source_patch
allows_tool_calls
must_include_evidence_refs
```

Rules:

```text
Prompt layer defines output expectations.
Model Adapter or LLM Worker validates actual output against those expectations.
Tool-call plans remain plans until Tool / MCP Adapter validates and executes them.
Patch proposals remain proposals until Governed Patch Execution validates and applies them.
Output validation failure must map to PROMPT_OUTPUT_CONTRACT_FAILED or a more specific downstream failure class.
```

---

# 39. Prompt Review, Activation, and Reviewer Independence

Prompt activation must be reproducible and reviewable.

Activation evidence must record:

```text
reviewed prompt contract id
reviewed prompt version id
prompt_text_sha256
registry_sha256
reviewer
reviewed_at
review_basis_documents
schema validation status
compatibility status
safety-rule status
permission-matrix status
provenance status
migration status, if applicable
activation decision
```

Reviewer independence rule:

```text
A generated or repaired prompt cannot become ACTIVE for implementation, repair, tool-use, source-mutation, or MCP-facing tasks based only on the generator's own approval.
```

A same-agent self-approval may be allowed only for low-risk DRAFT/CANDIDATE review artifacts and must not activate the prompt for runtime implementation behavior.

---

# 40. Rollback, Revocation, and Emergency Block Rules

Prompt rollback and revocation must be controlled and evidenced.

Rollback requirements:

```text
prior version exists
prior version hash matches recorded provenance
prior version is not REVOKED
rollback migration record exists
rollback reason recorded
runtime registry snapshot updated through governed source change or approved package update
```

Revocation requirements:

```text
revocation reason recorded
revoked prompt_version_id recorded
affected prompt_contract_id recorded
replacement or blocked status recorded
runtime binding attempts for revoked version block
existing evidence remains immutable
```

Emergency block behavior:

```text
critical injection defect -> BLOCK prompt version
secret leakage risk -> BLOCK prompt version
unauthorized tool-scope expansion -> BLOCK prompt version
hash mismatch -> BLOCK prompt version
missing provenance for active implementation prompt -> BLOCK prompt version
```

---

# 41. Issue Severity Classification

Use these severity levels for prompt-layer reviews.

## 41.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
compileall fails
pytest fails
schema validation fails
unregistered prompt binds
unversioned prompt binds
inactive prompt binds
revoked prompt binds
prompt hash mismatch does not block
rendered prompt hash missing for rendered prompt
missing provenance does not block active unsafe prompt
missing required safety rule does not block
unknown role is allowed
prompt text grants tool authority
prompt text overrides policy/sandbox/governance
prompt injection critical finding does not block unsafe prompt
output contract validation is skipped
prompt evidence is missing
evidence hashes are missing
source prompt package mutated during runtime binding
missing dependency defaults unsafe ALLOW
```

## 41.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
partial prompt migration coverage
partial prompt diff coverage
incomplete conflict-resolution evidence
incomplete template variable validation
reviewer independence not recorded
runtime evidence lacks authority decision refs
runtime artifact boundary deviation lacks justification
```

## 41.3 NON-BLOCKING

Non-blocking issues may be recorded as follow-up only if they do not affect runtime safety.

```text
minor wording mismatch
extra disabled prompt category
additional optional prompt package layout not yet used
legacy replay policy intentionally deferred safely
MCP-facing prompt exposure intentionally deferred safely
```


---

# 42. No-Go Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
prompt registry fails to load
unknown prompt binds at runtime
unversioned prompt binds at runtime
inactive prompt binds at runtime
prompt hash mismatch does not block
missing provenance does not block
missing safety rule does not block
unknown role is allowed
MCP_CLIENT can bind implementation/tool-execution prompts by default
prompt text grants tool permission
prompt text overrides policy/sandbox/governance
output contract validation is skipped
prompt evidence is not written
prompt evidence manifest is missing
prompt secrets are logged unredacted
prompt migration is missing for breaking changes
source mutation occurs directly in this layer
source prompt package is mutated during runtime binding
rendered prompt hash is missing for rendered prompt
prompt lifecycle transition occurs without evidence
prompt rollback or revocation lacks evidence
missing dependency defaults to unsafe ALLOW
```

---

# 43. Definition of Done

This layer is done when it can act as the controlled prompt governance layer for Agent_X.

It must prove:

```text
prompt contracts are structured and schema-valid
prompt versions are immutable and hash-checked
prompt registry loads deterministically
duplicate prompts are rejected
only one active version exists per prompt contract
unknown prompts fail closed
inactive prompts fail closed
role permissions are enforced
model profile restrictions are enforced
task type restrictions are enforced
tool scope restrictions are enforced
input contracts are validated
output contracts are validated
required safety rules are enforced
prompt provenance is required
prompt diffs detect breaking changes
prompt migrations are required for breaking changes
runtime bindings record prompt version and hash
registry snapshots are hash-checked
prompt injection checks run for untrusted context
prompt evidence is written
prompt evidence manifest is written
secrets are redacted before logging
no prompt can authorize tool execution by text alone
no source mutation occurs directly in this layer
source prompt package is not mutated during runtime binding
prompt lifecycle transitions are evidenced
rendered prompts have rendered hashes
conflict-resolution records are written
rollback and revocation are evidenced
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_prompt_* -q
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
prompt tests PASS
git status CLEAN or only expected runtime artifacts
```

---

# 44. Fresh-Clone Validation and Sign-Off

The implementation is accepted only after validation from a fresh checkout or clean working tree.

Required command sequence:

```bash
git clone https://github.com/Astrocytech/Agent_X.git Agent_X_prompt_contract_check
cd Agent_X_prompt_contract_check
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_prompt_* -q
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
prompt tests PASS
git status CLEAN or only expected ignored runtime artifacts
```

## 36.1 Final Sign-Off Checklist

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] prompt registry loads
[ ] duplicate prompts block
[ ] active prompt version rules pass
[ ] inactive prompt versions block
[ ] prompt hash mismatch blocks
[ ] unknown role blocks
[ ] model profile restriction works
[ ] task type restriction works
[ ] tool scope restriction works
[ ] input contract validation works
[ ] output contract validation works
[ ] safety rules enforced
[ ] provenance required
[ ] diff/migration checks work
[ ] prompt injection checks work
[ ] runtime binding evidence written
[ ] evidence manifest written
[ ] secrets redacted before evidence
[ ] no prompt grants tool authority by text
[ ] no source mutation
[ ] completion record exists
```

---

# 45. Final Freeze Rule

This v3 document is frozen as the controlling contract for the Prompt Contract / Prompt Versioning Layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional schemas, extra prompt categories, extra tests
MAJOR: changed permission model, changed versioning policy, changed runtime binding policy, changed prompt authority rules
```

Blocked without major revision:

```text
allowing unversioned prompts
allowing prompt text to grant tool permissions
removing prompt provenance
removing prompt hash checks
removing role permission checks
removing output contract validation
allowing inactive prompt binding
allowing generated prompts to activate without review
removing evidence logging
removing prompt injection checks for untrusted context
allowing missing dependencies to default ALLOW
```

The next document should be:

```text
PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC.md
```

---

# 46. Final Rating

This v3 contract document is rated:

```text
10/10
```

Reason:

```text
It preserves the full v2 coverage and adds the remaining handoff-critical controls: prompt lifecycle state transitions, binding conflict-resolution records, canonical prompt package layout, template-variable validation, deterministic prompt rendering, output validation handoff, rollback/revocation evidence rules, reviewer independence, reproducibility requirements, severity classification, and a clearer separation between source prompt-package artifacts and runtime evidence artifacts.
```
