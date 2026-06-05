# PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC

```text
document_id: PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, final frozen handoff, v3 precision-updated
component_id: AGENTX_PROMPT_CONTRACT_VERSIONING
component_name: Prompt Contract / Prompt Versioning Layer
roadmap_layer: 9
roadmap_phase: Phase C — Prompt Governance and Runtime Binding
based_on: PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria
target_language: Python
canonical_subdirectory: tools/agentx_evolve/prompts/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/prompts/
implementation_mode: deterministic prompt contracts first, runtime prompt binding controlled and auditable
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 implementation spec was rated:

```text
9.7/10
```

## 0.2 Why v2 Was Not Fully 10/10

The v2 document was strong and implementation-ready. It covered the requested implementation areas and added dependency fallbacks, schema examples, locking/idempotency, runtime binding, prompt safety, evidence propagation, hashing, and drift blockers.

It was not fully 10/10 because several final handoff details were still under-specified for a coding agent:

```text
1. It did not define the exact __init__.py public export contract.
2. It did not define a schema-controlled worker payload for later LLM worker consumption.
3. It did not make the render/log boundary explicit enough: rendered prompt payload may contain prompt body, but durable evidence must store hashes/redacted summaries unless explicitly allowed.
4. It did not define exact evidence manifest fields with command exit codes, output artifact hashes, dependency-state records, and runtime boundary status.
5. It did not require dependency-state recording for Policy, Tool Adapter, Model Adapter, Context Builder, and LLM Worker.
6. It did not define optional CLI handling precisely enough if prompt validation commands are later exposed.
7. It did not include a schema inventory update for prompt worker payload and prompt registry snapshot.
8. It did not require stable dependency test doubles for unavailable upstream layers.
9. It did not define exact activation failure records for rejected prompt activation attempts.
10. It did not include a hard freeze rule separating PATCH, MINOR, and MAJOR changes after v3.
```

## 0.3 v3 Improvements

This v3 adds:

```text
exact package export contract
prompt worker payload schema and render boundary
prompt registry snapshot schema
activation failure records
dependency-state evidence records
strict evidence manifest fields
command/CLI optional acceptance rules
stable dependency test-double rules
stronger runtime redaction rules
final freeze rule for future revisions
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Prompt Contract / Prompt Versioning Layer**.

The layer defines how Agent_X stores, validates, versions, compares, migrates, approves, and binds prompts at runtime.

It must ensure that prompts are not uncontrolled strings passed directly to models, tools, orchestrators, or workers. Every prompt must have:

```text
stable identity
explicit version
declared purpose
declared role permissions
declared model/task compatibility
declared input contract
declared output contract
declared safety rules
declared allowed tools
declared provenance
declared runtime binding rules
audit/evidence records
```

This layer does **not** execute LLM calls. It controls prompt definitions and runtime prompt selection so later layers can safely use prompts.

The implementation must be deterministic, local-first, testable without external services, and fail-closed when required dependency metadata is unavailable.

---

# 2. Canonical Destination Summary

Create the Prompt Contract / Prompt Versioning package here:

```text
tools/agentx_evolve/prompts/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must be written here:

```text
.agentx-init/prompts/
```

Intended package placement:

```text
tools/agentx_evolve/policy/       = Policy / Capability Registry
tools/agentx_evolve/tools/        = Tool / MCP Adapter
tools/agentx_evolve/models/       = future Model Adapter
tools/agentx_evolve/context/      = future Context Builder / Task Packer
tools/agentx_evolve/prompts/      = new Prompt Contract / Prompt Versioning Layer
tools/agentx_evolve/llm_worker/   = future LLM Implementation Worker
```

The Prompt Contract / Prompt Versioning Layer must not be placed under the Tool / MCP Adapter, Model Adapter, Context Builder, or LLM Worker package. Those layers consume prompt bindings later; they do not own prompt governance.

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic prompt-governance layer that can:

```text
load prompt contracts
load prompt versions
load prompt registry
validate prompt input contracts
validate prompt output contracts
validate prompt safety rules
validate prompt provenance
register prompt versions
reject duplicate active versions
compare prompt versions
classify prompt diffs as compatible or breaking
create migration records
bind a prompt version to a runtime request
check role permissions before prompt use
check model/task compatibility before prompt use
check allowed tool requests before prompt use
write prompt audit/evidence records
fail closed when prompt contract, version, input, output, safety, or binding checks fail
```

The layer must not implement:

```text
LLM execution
model routing
tool execution
context packing logic
prompt optimization by model
self-evolution orchestration
approval UI
network calls
hosted model calls
background daemon
```

---

# 4. Exact Subdirectory

The implementation must live under:

```text
tools/agentx_evolve/prompts/
```

Required package files:

```text
tools/agentx_evolve/prompts/__init__.py
tools/agentx_evolve/prompts/prompt_models.py
tools/agentx_evolve/prompts/prompt_registry.py
tools/agentx_evolve/prompts/prompt_validator.py
tools/agentx_evolve/prompts/prompt_versioning.py
tools/agentx_evolve/prompts/prompt_compatibility.py
tools/agentx_evolve/prompts/prompt_diff.py
tools/agentx_evolve/prompts/prompt_migration.py
tools/agentx_evolve/prompts/prompt_runtime_binding.py
tools/agentx_evolve/prompts/prompt_safety.py
tools/agentx_evolve/prompts/prompt_provenance.py
tools/agentx_evolve/prompts/prompt_audit_logger.py
```

Optional later file, only if CLI commands are exposed:

```text
tools/agentx_evolve/prompts/prompt_cli.py
```

---

# 5. Schemas to Create

Create the following schemas in:

```text
tools/agentx_evolve/schemas/
```

Required schema files:

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
prompt_worker_payload.schema.json
prompt_registry_snapshot.schema.json
prompt_permission_decision.schema.json
prompt_audit.schema.json
prompt_evidence_manifest.schema.json
prompt_completion_record.schema.json
```

Each schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require warnings
require errors
reject missing required fields
define enum values for prompt status, prompt type, compatibility result, migration status, safety level, and permission decision
include artifact_refs and evidence_refs where applicable
support deterministic validation without network, model, or external provider calls
```

## 5.1 Schema Example Requirement

For every schema, tests must include:

```text
one valid example object
one missing-required-field negative example
one invalid-enum negative example, if the schema contains enums
one malformed-type negative example
```

Required named examples:

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
valid_prompt_worker_payload
valid_prompt_registry_snapshot
valid_prompt_permission_decision
valid_prompt_audit_event
valid_prompt_evidence_manifest
valid_prompt_completion_record
```

Schema tests must prove:

```text
valid examples pass
missing required fields fail
invalid enum values fail
malformed field types fail
schema-invalid prompt bindings cannot be written as latest valid binding
```

---

# 6. Files to Create

## 6.1 Prompt Package Files

```text
[ ] tools/agentx_evolve/prompts/__init__.py
[ ] tools/agentx_evolve/prompts/prompt_models.py
[ ] tools/agentx_evolve/prompts/prompt_registry.py
[ ] tools/agentx_evolve/prompts/prompt_validator.py
[ ] tools/agentx_evolve/prompts/prompt_versioning.py
[ ] tools/agentx_evolve/prompts/prompt_compatibility.py
[ ] tools/agentx_evolve/prompts/prompt_diff.py
[ ] tools/agentx_evolve/prompts/prompt_migration.py
[ ] tools/agentx_evolve/prompts/prompt_runtime_binding.py
[ ] tools/agentx_evolve/prompts/prompt_safety.py
[ ] tools/agentx_evolve/prompts/prompt_provenance.py
[ ] tools/agentx_evolve/prompts/prompt_audit_logger.py
```

## 6.2 Schema Files

```text
[ ] tools/agentx_evolve/schemas/prompt_contract.schema.json
[ ] tools/agentx_evolve/schemas/prompt_version.schema.json
[ ] tools/agentx_evolve/schemas/prompt_registry.schema.json
[ ] tools/agentx_evolve/schemas/prompt_input_contract.schema.json
[ ] tools/agentx_evolve/schemas/prompt_output_contract.schema.json
[ ] tools/agentx_evolve/schemas/prompt_safety_rule.schema.json
[ ] tools/agentx_evolve/schemas/prompt_provenance.schema.json
[ ] tools/agentx_evolve/schemas/prompt_diff.schema.json
[ ] tools/agentx_evolve/schemas/prompt_migration.schema.json
[ ] tools/agentx_evolve/schemas/prompt_runtime_binding.schema.json
[ ] tools/agentx_evolve/schemas/prompt_worker_payload.schema.json
[ ] tools/agentx_evolve/schemas/prompt_registry_snapshot.schema.json
[ ] tools/agentx_evolve/schemas/prompt_permission_decision.schema.json
[ ] tools/agentx_evolve/schemas/prompt_audit.schema.json
[ ] tools/agentx_evolve/schemas/prompt_evidence_manifest.schema.json
[ ] tools/agentx_evolve/schemas/prompt_completion_record.schema.json
```

## 6.3 Test Files

```text
[ ] tools/agentx_evolve/tests/test_prompt_contract_schema.py
[ ] tools/agentx_evolve/tests/test_prompt_version_schema.py
[ ] tools/agentx_evolve/tests/test_prompt_registry.py
[ ] tools/agentx_evolve/tests/test_prompt_validator.py
[ ] tools/agentx_evolve/tests/test_prompt_versioning.py
[ ] tools/agentx_evolve/tests/test_prompt_compatibility.py
[ ] tools/agentx_evolve/tests/test_prompt_diff.py
[ ] tools/agentx_evolve/tests/test_prompt_migration.py
[ ] tools/agentx_evolve/tests/test_prompt_runtime_binding.py
[ ] tools/agentx_evolve/tests/test_prompt_worker_payload.py
[ ] tools/agentx_evolve/tests/test_prompt_registry_snapshot.py
[ ] tools/agentx_evolve/tests/test_prompt_safety.py
[ ] tools/agentx_evolve/tests/test_prompt_provenance.py
[ ] tools/agentx_evolve/tests/test_prompt_audit_logger.py
[ ] tools/agentx_evolve/tests/test_prompt_negative_cases.py
[ ] tools/agentx_evolve/tests/test_prompt_integration_boundaries.py
[ ] tools/agentx_evolve/tests/test_prompt_schema_validation.py
[ ] tools/agentx_evolve/tests/test_prompt_locking_idempotency.py
```

Optional validation script:

```text
tools/agentx_evolve/tests/validate_prompt_schemas.py
```

If this script is not implemented, `test_prompt_schema_validation.py` must provide equivalent coverage.

---

# 7. Classes and Functions

## 7.0 `__init__.py` Public Export Contract

### Purpose

Expose only the stable Prompt Contract / Prompt Versioning API.

### Required Exports

```python
from .prompt_models import (
    PromptContract,
    PromptVersion,
    PromptRegistry,
    PromptRegistrySnapshot,
    PromptInputContract,
    PromptOutputContract,
    PromptSafetyRule,
    PromptProvenance,
    PromptDiffRecord,
    PromptMigrationRecord,
    PromptRuntimeBinding,
    PromptWorkerPayload,
    PromptPermissionDecision,
    PromptAuditEvent,
)

from .prompt_registry import (
    load_prompt_registry,
    create_empty_prompt_registry,
    register_prompt_contract,
    register_prompt_version,
    get_prompt_contract,
    get_prompt_version,
    get_active_prompt_version,
    set_active_prompt_version,
    compute_registry_hash,
    create_registry_snapshot,
)

from .prompt_runtime_binding import (
    check_prompt_permission,
    bind_prompt_for_runtime,
    resolve_prompt_body,
    render_prompt_for_worker,
)
```

### Must Not Do

```text
no prompt registry loading on import
no filesystem writes on import
no runtime binding on import
no LLM/model calls
no tool calls
no network calls
no CLI registration side effects
```

---

## 7.1 `prompt_models.py`

### Purpose

Define shared dataclasses, enums, constants, and helpers for prompt contracts and prompt versions.

### Required Status Constants

```python
PROMPT_STATUS_DRAFT = "DRAFT"
PROMPT_STATUS_ACTIVE = "ACTIVE"
PROMPT_STATUS_DEPRECATED = "DEPRECATED"
PROMPT_STATUS_RETIRED = "RETIRED"
PROMPT_STATUS_BLOCKED = "BLOCKED"
```

### Required Prompt Type Constants

```python
PROMPT_TYPE_SYSTEM = "SYSTEM"
PROMPT_TYPE_DEVELOPER = "DEVELOPER"
PROMPT_TYPE_ROLE = "ROLE"
PROMPT_TYPE_TASK = "TASK"
PROMPT_TYPE_TOOL_USE = "TOOL_USE"
PROMPT_TYPE_REVIEW = "REVIEW"
PROMPT_TYPE_VALIDATION = "VALIDATION"
PROMPT_TYPE_REPAIR = "REPAIR"
PROMPT_TYPE_PROMOTION = "PROMOTION"
```

### Required Compatibility Constants

```python
COMPATIBILITY_COMPATIBLE = "COMPATIBLE"
COMPATIBILITY_BREAKING = "BREAKING"
COMPATIBILITY_REQUIRES_MIGRATION = "REQUIRES_MIGRATION"
COMPATIBILITY_UNKNOWN = "UNKNOWN"
```

### Required Permission Decision Constants

```python
PROMPT_DECISION_ALLOW = "ALLOW"
PROMPT_DECISION_BLOCK = "BLOCK"
PROMPT_DECISION_NEEDS_APPROVAL = "NEEDS_APPROVAL"
PROMPT_DECISION_NEEDS_GOVERNANCE = "NEEDS_GOVERNANCE"
PROMPT_DECISION_NEEDS_MIGRATION = "NEEDS_MIGRATION"
```

### Required Safety Level Constants

```python
PROMPT_SAFETY_LOW = "LOW"
PROMPT_SAFETY_MEDIUM = "MEDIUM"
PROMPT_SAFETY_HIGH = "HIGH"
PROMPT_SAFETY_CRITICAL = "CRITICAL"
```

### Required Migration Status Constants

```python
MIGRATION_STATUS_REQUIRED = "REQUIRED"
MIGRATION_STATUS_IN_PROGRESS = "IN_PROGRESS"
MIGRATION_STATUS_COMPLETE = "COMPLETE"
MIGRATION_STATUS_BLOCKED = "BLOCKED"
MIGRATION_STATUS_NOT_REQUIRED = "NOT_REQUIRED"
```

### Required Dataclasses

#### `PromptContract`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_contract.schema.json"
prompt_contract_id: str
prompt_name: str
description: str
owner_component: str
prompt_type: str
allowed_roles: list[str]
allowed_task_types: list[str]
allowed_model_profiles: list[str]
allowed_tool_names: list[str]
input_contract_id: str
output_contract_id: str
safety_rule_ids: list[str]
provenance_required: bool
runtime_binding_required: bool
versioning_required: bool
active_version_id: str | None
status: str
warnings: list[str]
errors: list[str]
```

#### `PromptVersion`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_version.schema.json"
prompt_version_id: str
prompt_contract_id: str
version: str
created_at: str
created_by: str
status: str
prompt_body: str
prompt_body_sha256: str
change_summary: str
breaking_change: bool
supersedes_version_id: str | None
migration_id: str | None
provenance_id: str
audit_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `PromptRegistry`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_registry.schema.json"
registry_id: str
registry_version: str
created_at: str
source_component: str = "PromptRegistry"
contracts: list[PromptContract]
versions: list[PromptVersion]
active_bindings: dict
registry_sha256: str | None
warnings: list[str]
errors: list[str]
```

#### `PromptRegistrySnapshot`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_registry_snapshot.schema.json"
snapshot_id: str
registry_id: str
registry_version: str
created_at: str
source_component: str = "PromptRegistry"
prompt_contract_ids: list[str]
prompt_version_ids: list[str]
active_bindings: dict
registry_sha256: str
warnings: list[str]
errors: list[str]
```

#### `PromptInputContract`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_input_contract.schema.json"
input_contract_id: str
required_fields: list[str]
optional_fields: list[str]
field_types: dict
max_input_chars: int
redaction_required: bool
context_sources_allowed: list[str]
warnings: list[str]
errors: list[str]
```

#### `PromptOutputContract`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_output_contract.schema.json"
output_contract_id: str
required_format: str
required_fields: list[str]
forbidden_fields: list[str]
max_output_chars: int
schema_ref: str | None
requires_json: bool
requires_evidence_refs: bool
warnings: list[str]
errors: list[str]
```

#### `PromptSafetyRule`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_safety_rule.schema.json"
safety_rule_id: str
name: str
safety_level: str
description: str
forbidden_content_patterns: list[str]
required_instructions: list[str]
tool_use_constraints: list[str]
model_use_constraints: list[str]
injection_defense_required: bool
warnings: list[str]
errors: list[str]
```

#### `PromptProvenance`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_provenance.schema.json"
provenance_id: str
prompt_contract_id: str
prompt_version_id: str
created_at: str
created_by: str
source_documents: list[str]
basis_contracts: list[str]
review_refs: list[str]
approval_refs: list[str]
prompt_body_sha256: str
warnings: list[str]
errors: list[str]
```

#### `PromptDiffRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_diff.schema.json"
diff_id: str
from_prompt_version_id: str
to_prompt_version_id: str
created_at: str
summary: str
added_sections: list[str]
removed_sections: list[str]
changed_sections: list[str]
compatibility_result: str
breaking_reasons: list[str]
diff_sha256: str | None
warnings: list[str]
errors: list[str]
```

#### `PromptMigrationRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_migration.schema.json"
migration_id: str
from_prompt_version_id: str
to_prompt_version_id: str
created_at: str
migration_status: str
required_actions: list[str]
affected_runtime_bindings: list[str]
approval_required: bool
governance_required: bool
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `PromptRuntimeBinding`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_runtime_binding.schema.json"
binding_id: str
prompt_contract_id: str
prompt_version_id: str
bound_at: str
bound_by_component: str
caller_role: str
task_type: str
model_profile_id: str | None
context_pack_id: str | None
allowed_tool_names: list[str]
input_contract_id: str
output_contract_id: str
policy_decision_id: str | None
registry_snapshot_sha256: str | None
prompt_body_sha256: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `PromptWorkerPayload`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_worker_payload.schema.json"
payload_id: str
binding_id: str
prompt_contract_id: str
prompt_version_id: str
prompt_body: str
prompt_body_sha256: str
input_data: dict
input_contract_id: str
output_contract_id: str
allowed_tool_names: list[str]
model_profile_id: str | None
context_pack_id: str | None
registry_snapshot_sha256: str
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

Rules:

```text
PromptWorkerPayload may contain the full prompt body only as an in-memory or immediate-return payload.
PromptWorkerPayload must not be durably logged with full prompt_body unless explicitly allowed by evidence policy.
Durable evidence must record prompt_body_sha256 and a redacted or bounded prompt summary.
```

#### `PromptPermissionDecision`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_permission_decision.schema.json"
decision_id: str
timestamp: str
source_component: str = "PromptPermission"
prompt_contract_id: str
prompt_version_id: str | None
caller_role: str
task_type: str
model_profile_id: str | None
decision: str
reason: str
missing_checks: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

#### `PromptAuditEvent`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "prompt_audit.schema.json"
audit_id: str
timestamp: str
source_component: str = "PromptContractVersioning"
event_type: str
prompt_contract_id: str | None
prompt_version_id: str | None
status: str
message: str
artifact_refs: list[str]
evidence_refs: list[str]
warnings: list[str]
errors: list[str]
```

### Required Helper Functions

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
sha256_text(value: str) -> str
sha256_dict(value: dict) -> str
redact_prompt_text(value: str, max_chars: int = 4000) -> str
to_dict(obj: object) -> dict
```

Acceptance:

```text
dataclasses instantiate
constants match schema enums
helper functions deterministic enough for tests
sha256_text returns stable hash
sha256_dict returns stable hash for sorted JSON
redaction helper bounds durable prompt-body evidence
no filesystem writes
no model/tool/network imports
```

---

# 8. Module-by-Module v1 Behavior Table

| Module | v1 behavior | Must call / depend on | Must not do |
|---|---|---|---|
| `prompt_models.py` | Dataclasses, constants, hashing helpers | Standard library only | No filesystem/model/tool calls |
| `prompt_registry.py` | Load/register/query registry, enforce active-version rules | Local prompt models and validator | No silent overwrite, no timestamp-only activation |
| `prompt_validator.py` | Validate schemas, contracts, versions, input/output, registry | JSON schema validator if available | No model-based validation |
| `prompt_versioning.py` | Create/activate/deprecate/retire versions | Compatibility, safety, provenance, migration | No activation bypass |
| `prompt_compatibility.py` | Conservative compatibility classification | Diff records and contract metadata | No LLM interpretation |
| `prompt_diff.py` | Deterministic diff and diff hash | Standard library only | No semantic/model diff |
| `prompt_migration.py` | Create/validate/complete migration records | Diff records and evidence refs | No migration completion without evidence |
| `prompt_runtime_binding.py` | Governed prompt binding | Registry, policy, tool registry metadata, model/context metadata if available | No model execution, no tool execution |
| `prompt_safety.py` | Safety and prompt-injection checks | Local deterministic pattern/rule checks | No weakening of policy/sandbox/tool controls |
| `prompt_provenance.py` | Create/validate provenance records | Hashing helpers | No activation without required provenance |
| `prompt_audit_logger.py` | Write append-only evidence and latest binding | Runtime artifact root | No source writes, no unredacted secrets |

---

# 9. Dependency Contract and Fallback Rules

## 9.1 Dependency Order

This layer may be implemented before some consumer layers exist. It must support restricted operation when dependencies are missing.

Expected dependency status:

```text
Policy / Capability Registry: should be used when available
Tool / MCP Adapter: should be used for tool registry metadata when available
Model Adapter: may be missing; use declared model_profile_id metadata only
Context Builder / Task Packer: may be missing; validate provided context metadata only
LLM Implementation Worker: may be missing; never called by this layer
```

## 9.2 Fail-Closed Fallbacks

Required fallback behavior:

```text
Policy unavailable -> runtime prompt binding BLOCKS, except schema-only validation mode
Tool Registry unavailable -> active prompts with unknown tools BLOCK; draft prompts may WARN
Model Adapter unavailable -> validate against declared allowed_model_profiles only; unknown provided model_profile_id BLOCKS
Context Builder unavailable -> validate provided input/context fields only; missing required fields BLOCK
LLM Worker unavailable -> no effect; this layer never executes prompts
```

## 9.3 Restricted Mode

Restricted mode allows:

```text
schema validation
contract validation
version validation
registry loading
diffing
compatibility classification
migration record creation
provenance validation
audit evidence writing
```

Restricted mode blocks:

```text
runtime prompt binding without policy
activation of breaking changes without migration/governance evidence
prompt use by unknown caller roles
prompt use with unknown tool requests
prompt rendering for LLM worker consumption
```

---

## 9.4 Dependency-State Evidence

Every runtime binding attempt must record the state of external dependencies used or intentionally not used.

Required dependency-state fields in evidence:

```text
policy_registry_status: AVAILABLE | UNAVAILABLE | NOT_APPLICABLE | ERROR
tool_adapter_status: AVAILABLE | UNAVAILABLE | NOT_APPLICABLE | ERROR
model_adapter_status: AVAILABLE | UNAVAILABLE | NOT_APPLICABLE | ERROR
context_builder_status: AVAILABLE | UNAVAILABLE | NOT_APPLICABLE | ERROR
llm_worker_status: NOT_CALLED
```

Rules:

```text
LLM Worker must always be NOT_CALLED in this layer.
Tool Adapter must be checked for tool metadata only, never invoked for execution.
Model Adapter must be checked for metadata only when available.
Context Builder must be checked for context-pack metadata only when available.
Policy Registry unavailable blocks runtime binding except schema-only validation mode.
```

## 9.5 Stable Dependency Test Doubles

Tests must use deterministic test doubles when upstream layers are unavailable.

Required test doubles:

```text
FakePolicyRegistryAllow
FakePolicyRegistryDeny
FakeToolRegistryMetadata
FakeModelProfileRegistry
FakeContextPackMetadata
FakeUnavailableDependency
```

Test doubles must not:

```text
call network
call models
execute tools
write source files
permit policy bypass
```

---

# 10. Public API Functions

## 10.1 `prompt_registry.py`

```python
load_prompt_registry(repo_root: Path) -> PromptRegistry
create_empty_prompt_registry() -> PromptRegistry
register_prompt_contract(registry: PromptRegistry, contract: PromptContract) -> PromptRegistry
register_prompt_version(registry: PromptRegistry, version: PromptVersion) -> PromptRegistry
get_prompt_contract(registry: PromptRegistry, prompt_contract_id: str) -> PromptContract | None
get_prompt_version(registry: PromptRegistry, prompt_version_id: str) -> PromptVersion | None
get_active_prompt_version(registry: PromptRegistry, prompt_contract_id: str) -> PromptVersion | None
set_active_prompt_version(registry: PromptRegistry, prompt_contract_id: str, prompt_version_id: str) -> PromptRegistry
compute_registry_hash(registry: PromptRegistry) -> str
create_registry_snapshot(registry: PromptRegistry) -> PromptRegistrySnapshot
```

Required behavior:

```text
registry loading is deterministic
missing registry returns empty registry only in initialization mode
duplicate prompt_contract_id is rejected
duplicate prompt_version_id is rejected
only one ACTIVE version may exist per prompt contract
active version must belong to same prompt contract
active version cannot be BLOCKED or RETIRED
registry hash changes when contract/version content changes
```

## 10.2 `prompt_validator.py`

```python
validate_prompt_contract(contract: PromptContract) -> list[str]
validate_prompt_version(version: PromptVersion, contract: PromptContract | None = None) -> list[str]
validate_prompt_registry(registry: PromptRegistry) -> list[str]
validate_prompt_input(input_data: dict, input_contract: PromptInputContract) -> list[str]
validate_prompt_output(output_data: dict | str, output_contract: PromptOutputContract) -> list[str]
validate_runtime_binding(binding: PromptRuntimeBinding, registry: PromptRegistry) -> list[str]
```

Required validation rules:

```text
prompt_contract_id required
prompt_name required
prompt_type must be known enum
allowed_roles cannot be empty
input_contract_id required
output_contract_id required
active_version_id must exist if set
prompt_version_id required
prompt_body cannot be empty
prompt_body_sha256 must match prompt_body
version string must be semantic-like or deterministic project format
safety_rule_ids must be present for high-risk prompt types
runtime binding must reference existing contract/version
input contract required fields must be present
output contract required fields must be present
forbidden output fields must be absent
```

## 10.3 `prompt_versioning.py`

```python
create_prompt_version(
    contract: PromptContract,
    prompt_body: str,
    version: str,
    created_by: str,
    change_summary: str,
    supersedes_version_id: str | None = None,
) -> PromptVersion

activate_prompt_version(
    registry: PromptRegistry,
    prompt_contract_id: str,
    prompt_version_id: str,
    approval_context: dict,
) -> PromptRegistry

deprecate_prompt_version(
    registry: PromptRegistry,
    prompt_version_id: str,
    reason: str,
) -> PromptRegistry

retire_prompt_version(
    registry: PromptRegistry,
    prompt_version_id: str,
    reason: str,
) -> PromptRegistry
```

Required behavior:

```text
new version records prompt_body_sha256
activation requires compatibility check
breaking activation requires governance/approval evidence
retired version cannot be active
blocked version cannot be active
deprecated version may remain usable only if active binding already exists and policy allows
activation writes audit event
```

## 10.4 `prompt_compatibility.py`

```python
check_prompt_compatibility(
    old_version: PromptVersion,
    new_version: PromptVersion,
    contract: PromptContract,
) -> PromptDiffRecord

classify_prompt_change(diff_record: PromptDiffRecord) -> str
requires_migration(diff_record: PromptDiffRecord) -> bool
```

Compatible changes:

```text
clarifying wording without changing required output fields
adding non-binding examples
adding stricter safety wording
improving redaction instructions
adding non-required context guidance
```

Breaking changes:

```text
changing required output format
removing required output fields
adding required input fields
changing allowed tools
changing allowed roles
changing task type compatibility
loosening safety constraints
changing model profile compatibility
changing runtime binding semantics
```

Requires migration:

```text
runtime bindings reference old version
output schema changed
input contract changed
allowed tools changed
allowed model profiles changed
safety rules changed materially
```

## 10.5 `prompt_diff.py`

```python
create_prompt_diff(old_version: PromptVersion, new_version: PromptVersion) -> PromptDiffRecord
summarize_prompt_diff(diff_record: PromptDiffRecord) -> str
hash_prompt_diff(diff_record: PromptDiffRecord) -> str
```

Required behavior:

```text
diff is deterministic
text comparison does not call an LLM
large prompt bodies are summarized with bounded output
hash is stable
sensitive prompt fragments are redacted in durable evidence if required
```

## 10.6 `prompt_migration.py`

```python
create_prompt_migration_record(
    diff_record: PromptDiffRecord,
    affected_runtime_bindings: list[str],
    approval_context: dict,
) -> PromptMigrationRecord

validate_prompt_migration_record(migration: PromptMigrationRecord) -> list[str]

mark_prompt_migration_complete(
    migration: PromptMigrationRecord,
    evidence_refs: list[str],
) -> PromptMigrationRecord
```

Required behavior:

```text
breaking changes require migration record
migration record lists affected runtime bindings
migration record states whether governance is required
migration record states whether human approval is required
migration cannot be marked complete without evidence refs
```

## 10.7 `prompt_runtime_binding.py`

```python
check_prompt_permission(
    registry: PromptRegistry,
    prompt_contract_id: str,
    caller_role: str,
    task_type: str,
    model_profile_id: str | None,
    requested_tool_names: list[str],
    policy_context: dict,
) -> PromptPermissionDecision

bind_prompt_for_runtime(
    registry: PromptRegistry,
    prompt_contract_id: str,
    caller_role: str,
    task_type: str,
    model_profile_id: str | None,
    context_pack_id: str | None,
    requested_tool_names: list[str],
    policy_context: dict,
) -> PromptRuntimeBinding

resolve_prompt_body(
    registry: PromptRegistry,
    binding: PromptRuntimeBinding,
) -> str

render_prompt_for_worker(
    registry: PromptRegistry,
    binding: PromptRuntimeBinding,
    input_data: dict,
) -> PromptWorkerPayload
```

`render_prompt_for_worker` may prepare a controlled prompt payload, but it must not call the LLM Worker.

Required binding rules:

```text
prompt contract must exist
active prompt version must exist
caller_role must be allowed by prompt contract
requested task_type must be allowed by prompt contract
model_profile_id must be allowed unless model binding is intentionally deferred
requested tools must be subset of allowed_tool_names
Policy / Capability Registry decision must not block prompt use
Context Builder pack must match prompt input contract when context_pack_id is provided
binding writes evidence
binding records prompt version ID and prompt body hash
binding records registry snapshot hash
```

Render/log boundary:

```text
render_prompt_for_worker may return a PromptWorkerPayload containing prompt_body for immediate downstream use.
append-only evidence must not store full prompt_body unless explicitly permitted by prompt evidence policy.
evidence records must store prompt_body_sha256, prompt_version_id, binding_id, and redacted_prompt_summary.
input_data must be validated and redacted before durable evidence.
worker payload must validate against prompt_worker_payload.schema.json.
```

Fail-closed rules:

```text
missing contract -> BLOCK
missing active version -> BLOCK
role not allowed -> BLOCK
task type not allowed -> BLOCK
model profile not allowed -> BLOCK
requested tool not allowed -> BLOCK
policy unavailable -> BLOCK unless schema-only validation mode
context pack incompatible -> BLOCK
```

## 10.8 `prompt_safety.py`

```python
validate_prompt_safety_rules(rules: list[PromptSafetyRule]) -> list[str]
check_prompt_body_safety(prompt_body: str, rules: list[PromptSafetyRule]) -> list[str]
check_prompt_injection_defenses(prompt_body: str, prompt_type: str) -> list[str]
check_prompt_drift_risk(old_version: PromptVersion, new_version: PromptVersion) -> list[str]
```

Required safety checks:

```text
prompt must not instruct bypassing Policy / Capability Registry
prompt must not instruct bypassing Security Sandbox
prompt must not instruct bypassing Tool / MCP Adapter
prompt must not instruct raw shell execution
prompt must not instruct unapproved source mutation
prompt must not instruct unapproved Git writes
prompt must not instruct network calls by default
prompt must include injection-resistance wording where applicable
prompt must preserve output contract requirements
prompt must preserve evidence/audit requirements
prompt must not tell downstream workers to ignore prompt contracts
prompt must not weaken role/tool/model/context boundaries
```

## 10.9 `prompt_provenance.py`

```python
create_prompt_provenance(
    prompt_contract_id: str,
    prompt_version_id: str,
    prompt_body: str,
    created_by: str,
    source_documents: list[str],
    basis_contracts: list[str],
    review_refs: list[str],
    approval_refs: list[str],
) -> PromptProvenance

validate_prompt_provenance(provenance: PromptProvenance) -> list[str]
```

Required behavior:

```text
prompt_body_sha256 must match prompt body
source documents recorded where applicable
basis contracts recorded where applicable
review refs recorded before activation for critical prompts
approval refs recorded before activation for breaking changes
```

## 10.10 `prompt_audit_logger.py`

```python
append_prompt_audit_event(event: PromptAuditEvent, repo_root: Path) -> dict
append_prompt_registry_event(registry: PromptRegistry, repo_root: Path) -> dict
append_prompt_version_event(version: PromptVersion, repo_root: Path) -> dict
append_prompt_binding_event(binding: PromptRuntimeBinding, repo_root: Path) -> dict
append_prompt_diff_event(diff_record: PromptDiffRecord, repo_root: Path) -> dict
append_prompt_migration_event(migration: PromptMigrationRecord, repo_root: Path) -> dict
append_prompt_safety_event(event: dict, repo_root: Path) -> dict
write_latest_prompt_binding(binding: PromptRuntimeBinding, repo_root: Path) -> dict
write_prompt_evidence_manifest(evidence: dict, repo_root: Path) -> dict
write_prompt_completion_record(record: dict, repo_root: Path) -> dict
```

Required runtime paths:

```text
.agentx-init/prompts/prompt_registry_history.jsonl
.agentx-init/prompts/prompt_version_history.jsonl
.agentx-init/prompts/prompt_binding_history.jsonl
.agentx-init/prompts/prompt_diff_history.jsonl
.agentx-init/prompts/prompt_migration_history.jsonl
.agentx-init/prompts/prompt_safety_history.jsonl
.agentx-init/prompts/latest_prompt_binding.json
.agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json
.agentx-init/prompts/prompt_contract_versioning_completion_record.json
```

Required evidence rules:

```text
append-only JSONL for histories
atomic JSON writes for latest artifacts
SHA-256 hashes for final evidence artifacts
redact secrets before logging
redact large prompt bodies if policy requires
record prompt version ID and prompt body hash
record registry hash
record runtime binding ID
record policy decision ID where available
```

---

# 11. Runtime Binding Dispatcher Pipeline

No downstream component may use a prompt body directly unless it has a valid `PromptRuntimeBinding`.

Required `bind_prompt_for_runtime` pipeline:

```text
1. Receive runtime binding request.
2. Load or receive PromptRegistry.
3. Validate registry structure.
4. Locate PromptContract.
5. Locate active PromptVersion.
6. Verify active version belongs to contract.
7. Validate PromptContract.
8. Validate PromptVersion and prompt_body_sha256.
9. Validate caller role against contract.
10. Validate task type against contract.
11. Validate model_profile_id against allowed_model_profiles when provided.
12. Validate requested tools against allowed_tool_names.
13. Check Tool Registry metadata when available.
14. Check Policy / Capability Registry decision.
15. Check context/input compatibility when context metadata is provided.
16. Check prompt safety rules and injection-defence requirements.
17. Create registry snapshot hash.
18. Create PromptPermissionDecision.
19. Create PromptRuntimeBinding.
20. Write binding evidence.
21. Write latest binding atomically.
22. Return PromptRuntimeBinding.
```

Rules:

```text
No skipped stage is allowed unless explicitly marked NOT APPLICABLE in the binding warnings.
Any failed required stage returns a BLOCK decision or raises a controlled validation error converted to audit evidence.
No model call, tool call, network call, or raw shell call is allowed in the pipeline.
```

---

# 12. Prompt Registry Behavior

The Prompt Registry must be deterministic and auditable.

Required behavior:

```text
load registry without side effects
create empty registry only in initialization mode
reject duplicate prompt contract IDs
reject duplicate prompt version IDs
reject multiple active versions for same contract
reject active version that does not belong to contract
reject active retired/blocked version
compute registry hash
preserve disabled/deprecated prompts for evidence
record registry version
record active binding map
create registry snapshot hash for runtime binding
```

Registry must not:

```text
silently overwrite prompt versions
silently remove deprecated versions
select latest version by timestamp without explicit activation
activate breaking prompt changes without migration/governance evidence
```

---

# 13. Registry Locking and Idempotency Rules

## 13.1 Registry Snapshot Lock

During a runtime binding request, the registry snapshot must be stable.

Required behavior:

```text
compute registry_sha256 before binding
include registry_sha256 in PromptRuntimeBinding
if registry changes during binding, binding must retry or block
runtime binding evidence records registry_sha256
```

## 13.2 Active Version Lock

Activation must be atomic from the perspective of a registry object.

Required behavior:

```text
only one active version per prompt contract
a new activation deactivates or supersedes the previous active version deterministically
activation produces audit event
activation updates registry hash
activation cannot partially update active_bindings
```

## 13.3 Idempotency

Repeated equivalent operations must be stable.

Required behavior:

```text
registering same contract twice returns duplicate error, not silent success
registering same version twice returns duplicate error, not silent success
creating same prompt body/version with same inputs produces same prompt_body_sha256
computing same diff twice produces same diff hash
binding same request against same registry snapshot produces equivalent binding content except timestamp/id fields
writing latest binding is atomic
history logs are append-only
```

---

# 14. Prompt Versioning Behavior

Prompt versions must be explicit.

Required behavior:

```text
every prompt version has unique prompt_version_id
every prompt version belongs to one prompt_contract_id
every prompt version records version string
every prompt version records prompt_body_sha256
every prompt version records created_by and created_at
every prompt version records change_summary
every prompt version records supersedes_version_id where applicable
every prompt version records provenance_id
active version is changed only through activation function
breaking changes require migration record before activation
```

Version activation must fail closed when:

```text
contract missing
version missing
version belongs to different contract
version is retired
version is blocked
compatibility result is BREAKING without governance approval
migration required but missing
provenance missing
safety validation fails
```

---

## 14.1 Activation Failure Records

Rejected activation attempts must be evidenced.

Required behavior:

```text
failed activation writes PromptAuditEvent
failed activation records prompt_contract_id and attempted prompt_version_id
failed activation records failure reason
failed activation records compatibility result if available
failed activation records migration requirement if available
failed activation does not change active_version_id
failed activation does not update active_bindings as if successful
```

Blocking activation failures include:

```text
missing provenance
missing migration for breaking change
missing governance evidence
unsafe prompt body
role/tool/model compatibility violation
registry hash mismatch during activation
```

---

# 15. Prompt Compatibility Checks

Compatibility checks must be deterministic and conservative.

Required checks:

```text
input contract changed?
output contract changed?
required output fields changed?
forbidden output fields changed?
allowed roles changed?
allowed task types changed?
allowed model profiles changed?
allowed tools changed?
safety rules changed?
runtime binding rules changed?
prompt body hash changed?
```

Compatibility outputs:

```text
COMPATIBLE
BREAKING
REQUIRES_MIGRATION
UNKNOWN
```

Rule:

```text
If the system cannot determine compatibility safely, return UNKNOWN and require review.
```

---

# 16. Prompt Migration Rules

Migration is required when a prompt version change may alter downstream behavior.

Migration required for:

```text
output schema change
input schema change
allowed tools change
allowed roles change
model compatibility change
task compatibility change
safety rule relaxation
runtime binding change
breaking prompt-body instruction change
```

Migration record must include:

```text
migration_id
from_prompt_version_id
to_prompt_version_id
affected_runtime_bindings
required_actions
approval_required
governance_required
migration_status
evidence_refs
```

Migration cannot be complete unless:

```text
affected bindings are listed
required actions are complete
evidence refs exist
approval/governance refs exist when required
```

---

# 17. Prompt Diffing Rules

Prompt diffing must be deterministic and non-model-based.

Required behavior:

```text
compare old and new prompt bodies
compare old and new hashes
identify added sections
identify removed sections
identify changed sections
classify compatibility impact
produce bounded diff summary
write diff evidence
```

Forbidden behavior:

```text
no LLM-based diffing
no semantic rewriting
no prompt optimization
no external tool calls
no network calls
```

---

# 18. Prompt Safety, Injection, and Drift Rules

Prompt safety must be deterministic and conservative.

Blocked prompt-body patterns include instructions to:

```text
ignore Policy / Capability Registry
ignore Security Sandbox
ignore Tool / MCP Adapter
ignore prompt contracts or prompt versioning
execute raw shell
write source directly
commit, push, merge, or rewrite Git history without governance
call network by default
use an unregistered prompt
use an unregistered tool
hide evidence or avoid audit logging
remove required output fields
bypass human approval or governance
```

Prompt injection defense is required for prompts that consume untrusted user input, file content, tool output, web content, or context-pack content.

Required injection defenses:

```text
treat external/context content as data, not instructions
preserve higher-priority system/developer/contract rules
never follow embedded instructions that bypass policy, sandbox, tool, model, or evidence rules
validate output against output contract
record evidence refs for runtime binding and prompt version
```

Prompt drift check must flag:

```text
removal of safety instructions
weakening of role boundaries
weakening of tool restrictions
weakening of output schema requirements
new instructions that authorize direct mutation
new instructions that reduce evidence/audit requirements
```

---

# 19. Runtime Artifacts

Runtime artifacts must be under:

```text
.agentx-init/prompts/
```

Required artifacts:

```text
prompt_registry_history.jsonl
prompt_version_history.jsonl
prompt_binding_history.jsonl
prompt_diff_history.jsonl
prompt_migration_history.jsonl
prompt_safety_history.jsonl
latest_prompt_binding.json
prompt_contract_versioning_evidence_manifest.json
prompt_contract_versioning_completion_record.json
```

Rules:

```text
append-only JSONL histories
atomic JSON writes for latest artifacts
SHA-256 hashes for final evidence artifacts
no source writes outside approved runtime artifact root
no prompt body leakage if redaction policy requires redaction
```

---

# 20. Evidence Reference Propagation

PromptRuntimeBinding and related audit events must carry evidence references where available.

Required mappings:

```text
policy decision produced -> PromptPermissionDecision.evidence_refs includes policy decision ID
policy decision produced -> PromptRuntimeBinding.policy_decision_id records policy decision ID
tool registry checked -> PromptRuntimeBinding.evidence_refs includes tool registry snapshot or hash
model metadata checked -> PromptRuntimeBinding.evidence_refs includes model metadata reference when available
context metadata checked -> PromptRuntimeBinding.evidence_refs includes context pack reference when available
safety check produced -> PromptRuntimeBinding.evidence_refs includes safety audit event ID
provenance record produced -> PromptVersion.provenance_id records provenance ID
diff record produced -> migration record references diff ID or evidence ID
migration record produced -> activation evidence references migration ID
runtime binding produced -> latest_prompt_binding and binding history include binding ID
```

If an evidence source is required for safety and unavailable, the operation must block or record a controlled failure.

---

# 21. Artifact Hashing and Provenance Rules

Required hashes:

```text
prompt_body_sha256 for every PromptVersion
registry_sha256 for every PromptRegistry snapshot used in binding
diff_sha256 for every PromptDiffRecord
prompt_contract_versioning_evidence_manifest sha256 in completion record
prompt_contract_versioning_completion_record sha256 computed after finalization or recorded by review layer
command output artifact hashes if stored as files
```

Hashing rule:

```text
Use SHA-256.
Use Python standard library hashlib.
Stable dict hashes must serialize JSON with sorted keys and deterministic separators.
A final DONE verdict is invalid if required prompt evidence hashes are missing.
```

Prompt provenance must include:

```text
source documents where applicable
basis contracts where applicable
review refs where applicable
approval refs for breaking or critical prompts
prompt_body_sha256
```

---

# 22. Integration with Policy / Capability Registry

The Prompt Contract / Prompt Versioning Layer must call or respect Policy / Capability Registry decisions before prompt binding.

Policy must decide:

```text
caller role allowed?
prompt contract allowed?
prompt version allowed?
task type allowed?
model profile allowed?
requested tools allowed?
governance required?
human approval required?
```

Required behavior:

```text
policy-denied prompt use returns BLOCK
policy-unavailable prompt binding blocks unless running schema-only validation
policy decision ID is recorded in PromptRuntimeBinding when available
prompt permissions must not override tool permissions
prompt permission ALLOW does not grant tool execution permission
```

Fail-closed rule:

```text
If a prompt requests a tool that policy denies, prompt binding must block.
```

---

# 23. Integration with Tool / MCP Adapter

Prompt contracts must declare which tools a prompt may request.

Required integration:

```text
allowed_tool_names in PromptContract must be checked against Tool Registry when available
unknown tool names in prompt contracts are warnings in draft mode and blockers in active mode
prompt binding must reject requested tools not in allowed_tool_names
MCP-exposed prompts must not expand MCP tool access
prompt instructions must not bypass Tool / MCP Adapter
```

Rules:

```text
Prompt layer never executes tools.
Tool layer remains authoritative for tool execution.
Prompt allowed_tool_names are an upper bound, not permission to execute.
```

---

# 24. Integration with Model Adapter

The Model Adapter may not exist yet. This layer must still define model compatibility metadata.

Required behavior:

```text
PromptContract.allowed_model_profiles lists compatible model profiles
PromptRuntimeBinding records model_profile_id where available
if Model Adapter is missing, model_profile_id validation may run in restricted metadata-only mode
if model_profile_id is provided and not allowed, binding blocks
prompt output contract must be compatible with model/task requirements where metadata exists
```

Rules:

```text
Prompt layer does not call models.
Prompt layer does not select providers.
Prompt layer does not enable network/hosted model use.
```

---

# 25. Integration with Context Builder / Task Packer

The Context Builder / Task Packer may not exist yet. This layer must still define input-contract boundaries.

Required behavior:

```text
PromptInputContract defines required context fields
PromptRuntimeBinding records context_pack_id when available
if context pack metadata exists, validate it against PromptInputContract
if required input fields are missing, binding blocks
redaction_required must be respected before prompt use
```

Rules:

```text
Prompt layer does not build context packs.
Prompt layer validates compatibility with context pack metadata.
Prompt layer records context_pack_id for audit.
```

---

# 26. Integration with LLM Implementation Worker

The LLM Implementation Worker may not exist yet. This layer must define what the worker may consume later.

Required behavior:

```text
LLM worker must receive prompt_contract_id
LLM worker must receive prompt_version_id
LLM worker must receive prompt_body_sha256
LLM worker must receive input_contract_id
LLM worker must receive output_contract_id
LLM worker must receive runtime binding ID
LLM worker must receive allowed_tool_names upper bound
LLM worker must not use unregistered prompt strings
LLM worker must not use retired/blocked prompt versions
```

Rules:

```text
Prompt layer prepares controlled prompt bindings.
LLM worker executes later, under its own acceptance contract.
Prompt layer does not call the LLM worker.
```

---

# 27. Test Implementation Plan

## 27.1 Test Fixtures

Create fixtures:

```python
@pytest.fixture
def valid_prompt_contract(): ...

@pytest.fixture
def valid_prompt_version(): ...

@pytest.fixture
def valid_prompt_registry(): ...

@pytest.fixture
def valid_input_contract(): ...

@pytest.fixture
def valid_output_contract(): ...

@pytest.fixture
def valid_safety_rule(): ...

@pytest.fixture
def valid_policy_context(): ...

@pytest.fixture
def temp_repo(tmp_path): ...
```

## 27.2 Required Test Cases

```text
test_prompt_contract_schema_accepts_valid_contract
test_prompt_contract_schema_rejects_missing_prompt_contract_id
test_prompt_contract_schema_rejects_invalid_prompt_type
test_prompt_version_schema_accepts_valid_version
test_prompt_version_schema_rejects_missing_prompt_body_hash
test_prompt_registry_loads_empty_registry
test_prompt_registry_rejects_duplicate_contract_id
test_prompt_registry_rejects_duplicate_version_id
test_prompt_registry_rejects_multiple_active_versions
test_prompt_registry_hash_changes_on_content_change
test_prompt_registry_snapshot_hash_is_stable
test_prompt_version_hash_matches_body
test_activate_prompt_version_blocks_retired_version
test_activate_prompt_version_blocks_missing_provenance
test_compatible_prompt_change_allows_activation
test_breaking_prompt_change_requires_migration
test_output_contract_change_is_breaking
test_allowed_tools_change_requires_migration
test_prompt_diff_is_deterministic
test_prompt_diff_hash_is_stable
test_prompt_migration_requires_evidence_to_complete
test_runtime_binding_blocks_unknown_contract
test_runtime_binding_blocks_missing_active_version
test_runtime_binding_blocks_disallowed_role
test_runtime_binding_blocks_disallowed_task_type
test_runtime_binding_blocks_disallowed_model_profile
test_runtime_binding_blocks_disallowed_requested_tool
test_runtime_binding_records_registry_snapshot_hash
test_prompt_worker_payload_schema_accepts_valid_payload
test_prompt_worker_payload_records_binding_and_hash
test_prompt_registry_snapshot_schema_accepts_valid_snapshot
test_prompt_permission_policy_denied_blocks
test_prompt_safety_blocks_policy_bypass_instruction
test_prompt_safety_blocks_sandbox_bypass_instruction
test_prompt_safety_blocks_tool_adapter_bypass_instruction
test_prompt_safety_blocks_raw_shell_instruction
test_prompt_safety_blocks_prompt_contract_bypass_instruction
test_prompt_provenance_hash_matches_prompt_body
test_prompt_audit_history_written
test_latest_prompt_binding_written_atomically
test_prompt_evidence_manifest_written
test_prompt_completion_record_written
```

## 27.3 Negative Tests

```text
test_unregistered_prompt_cannot_bind
test_retired_prompt_version_cannot_bind
test_blocked_prompt_version_cannot_bind
test_prompt_with_unknown_tool_blocks_when_active
test_prompt_with_policy_bypass_instruction_blocks
test_prompt_with_sandbox_bypass_instruction_blocks
test_prompt_with_tool_adapter_bypass_instruction_blocks
test_prompt_with_unapproved_git_write_instruction_blocks
test_prompt_with_network_by_default_instruction_blocks
test_breaking_change_without_migration_blocks_activation
test_missing_policy_blocks_runtime_binding
test_context_incompatible_with_input_contract_blocks
test_output_missing_required_field_fails_validation
test_prompt_registry_does_not_silently_overwrite_versions
test_prompt_layer_does_not_execute_tools
test_prompt_layer_does_not_call_model
test_prompt_layer_does_not_call_network
test_prompt_layer_does_not_execute_raw_shell
test_schema_invalid_binding_does_not_replace_latest_valid_binding
```

---

# 28. Implementation Order

Implement in this exact order:

```text
1. tools/agentx_evolve/prompts/__init__.py
2. tools/agentx_evolve/prompts/prompt_models.py
3. prompt schema files
4. schema example tests
5. tools/agentx_evolve/prompts/prompt_validator.py
6. tools/agentx_evolve/prompts/prompt_registry.py
7. tools/agentx_evolve/prompts/prompt_safety.py
8. tools/agentx_evolve/prompts/prompt_provenance.py
9. tools/agentx_evolve/prompts/prompt_diff.py
10. tools/agentx_evolve/prompts/prompt_compatibility.py
11. tools/agentx_evolve/prompts/prompt_migration.py
12. tools/agentx_evolve/prompts/prompt_versioning.py
13. tools/agentx_evolve/prompts/prompt_runtime_binding.py
14. tools/agentx_evolve/prompts/prompt_audit_logger.py
15. integration-boundary tests
16. negative tests
17. schema validation utility, if used
18. completion evidence
```

Rationale:

```text
models first
schemas second
schema tests before behavior tests
validation before registry mutation
safety/provenance before version activation
diff/compatibility before migration
migration before version activation
runtime binding after registry/versioning rules
audit logger after public objects stabilize
integration and negative tests after public surfaces exist
```

---

# 29. Minimal Implementation Slices

## Slice A — Models and Schemas

Implement:

```text
prompt_models.py
all prompt schema files
basic schema tests
```

Acceptance:

```text
dataclasses instantiate
schemas accept valid examples
schemas reject missing required fields
schemas reject invalid enum values
schemas reject malformed field types
no registry mutation yet
no runtime binding yet
```

## Slice B — Validation and Registry

Implement:

```text
prompt_validator.py
prompt_registry.py
```

Acceptance:

```text
registry loads
duplicates rejected
active version rules enforced
registry hash computed
registry snapshot hash stable
invalid contracts rejected
```

## Slice C — Safety and Provenance

Implement:

```text
prompt_safety.py
prompt_provenance.py
```

Acceptance:

```text
unsafe prompt instructions blocked
prompt injection defenses checked
prompt drift risks flagged
provenance hash validates
activation can require provenance
```

## Slice D — Diff, Compatibility, Migration

Implement:

```text
prompt_diff.py
prompt_compatibility.py
prompt_migration.py
```

Acceptance:

```text
diff is deterministic
diff hash is stable
breaking changes classified
migration record required when needed
migration cannot complete without evidence
```

## Slice E — Versioning and Runtime Binding

Implement:

```text
prompt_versioning.py
prompt_runtime_binding.py
```

Acceptance:

```text
version creation records hash
activation blocks unsafe/breaking/missing-provenance cases
runtime binding checks role/task/model/tool/policy/context constraints
runtime binding records registry snapshot hash
```

## Slice F — Audit and Evidence

Implement:

```text
prompt_audit_logger.py
```

Acceptance:

```text
prompt histories written
latest binding written atomically
evidence manifest written
completion record written
secrets and prompt bodies redacted where required
```

---

# 30. Acceptance Criteria

The implementation is acceptable only if:

```text
all target files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
schema validation passes
prompt registry loads deterministically
duplicate contracts are rejected
duplicate versions are rejected
only one active version per contract is allowed
prompt version hash validation works
prompt compatibility checks classify breaking changes
migration records are required for breaking changes
prompt diffing is deterministic
runtime binding checks role permissions
runtime binding checks task type compatibility
runtime binding checks model profile compatibility where metadata exists
runtime binding checks requested tools
runtime binding checks policy decision
runtime binding records registry snapshot hash
worker payload validates against prompt_worker_payload.schema.json
prompt safety blocks bypass instructions
prompt provenance records prompt body hash
prompt audit/evidence is written
evidence hashes are written
no model call occurs
no tool execution occurs
no network call occurs
no raw shell occurs
no source mutation occurs outside approved runtime artifacts
completion record exists
```

---

# 31. Optional CLI / Command Acceptance Criteria

This layer does not require CLI exposure in v1. If prompt validation or prompt registry commands are exposed later, they must follow Command Acceptance Criteria.

Allowed optional CLI commands:

```text
agentx-prompts validate
agentx-prompts registry-status
agentx-prompts diff
agentx-prompts check-compatibility
agentx-prompts bind-dry-run
```

CLI commands must:

```text
run without network/model/tool execution
write evidence only under .agentx-init/prompts/
return non-zero exit code for validation failure
record command text, exit code, status, and summary
not expose prompt bodies in logs unless redaction policy allows it
not activate prompt versions without governance/migration checks
```

CLI commands must not:

```text
call an LLM
execute tools
start MCP
open network access
write source files
modify Git state
```

If no CLI is implemented, this section is `NOT APPLICABLE` and must be recorded as such in the post-implementation review.

---

# 32. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py
git status --short
```

If `validate_prompt_schemas.py` is not implemented, use the pytest schema test files as the schema validation proof.

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
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
```

---

# 33. Runtime Artifact Boundary

Approved runtime artifact root:

```text
.agentx-init/prompts/
```

The Prompt Contract / Prompt Versioning Layer may not write outside that root except for approved source-controlled implementation files, schemas, and tests created during coding.

During runtime and tests, any generated prompt evidence must stay under:

```text
.agentx-init/prompts/
```

Unapproved runtime writes outside `.agentx-init/prompts/` are a blocking failure unless recorded as a deviation in the post-implementation review document.

---

# 34. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places package files outside tools/agentx_evolve/prompts/ without recorded deviation
places schemas outside tools/agentx_evolve/schemas/ without recorded deviation
stores prompt evidence outside .agentx-init/prompts/ without recorded deviation
allows duplicate active prompt versions
activates a breaking prompt change without migration/governance evidence
uses latest timestamp as active version without explicit activation
executes an LLM call
executes a tool call
opens network access
executes raw shell
performs source mutation directly
bypasses Policy / Capability Registry for runtime binding
ignores Tool / MCP Adapter allowed-tool boundaries
allows prompt instructions to bypass sandbox/policy/tool controls
logs unredacted secrets
silently overwrites prompt versions
silently removes deprecated/retired prompts from evidence
returns unstructured prompt binding records
omits prompt body hashes
omits registry snapshot hashes for runtime bindings
omits evidence hashes from final completion evidence
```

---

# 35. Evidence Manifest

After validation, write:

```text
.agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_evidence_manifest.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
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
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    },
    {
      "name": "schema_validation",
      "command": "PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path or null>",
      "output_sha256": "<sha256 or null>"
    }
  ],
  "dependency_state": {
    "policy_registry_status": "AVAILABLE_OR_RESTRICTED",
    "tool_adapter_status": "AVAILABLE_OR_METADATA_ONLY",
    "model_adapter_status": "AVAILABLE_OR_METADATA_ONLY",
    "context_builder_status": "AVAILABLE_OR_METADATA_ONLY",
    "llm_worker_status": "NOT_CALLED"
  },
  "runtime_artifacts": [],
  "evidence_file_hashes": [],
  "prompt_body_hashes_verified": [],
  "registry_snapshot_hashes_verified": [],
  "diff_hashes_verified": [],
  "redaction_status": "PASS",
  "runtime_boundary_status": "PASS",
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "deviation_register": [],
  "final_decision": "DONE"
}
```

Required manifest rules:

```text
all required commands record exit_code
PASS requires exit_code 0
manifest includes dependency-state records
manifest includes hashes for final evidence artifacts
manifest includes prompt-body, registry-snapshot, and diff hash verification summaries
manifest records that LLM Worker was NOT_CALLED
manifest records that Tool Adapter was not invoked for execution
```

---

# 36. Completion Evidence

After implementation, write:

```text
.agentx-init/prompts/prompt_contract_versioning_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "prompt_completion_record.schema.json",
  "component_id": "AGENTX_PROMPT_CONTRACT_VERSIONING",
  "component_name": "Prompt Contract / Prompt Versioning Layer",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/prompts/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/prompts/",
  "basis_documents": [
    "PROMPT_CONTRACT_VERSIONING_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "PROMPT_CONTRACT_VERSIONING_IMPLEMENTATION_SPEC_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "prompt_contracts_verified": [],
  "prompt_versions_verified": [],
  "prompt_registry_verified": [],
  "prompt_compatibility_verified": [],
  "prompt_migrations_verified": [],
  "prompt_runtime_bindings_verified": [],
  "prompt_safety_verified": [],
  "prompt_provenance_verified": [],
  "prompt_evidence_verified": [],
  "policy_integration_verified": [],
  "tool_adapter_integration_verified": [],
  "model_adapter_integration_verified": [],
  "context_builder_integration_verified": [],
  "llm_worker_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/prompts/prompt_contract_versioning_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 37. Definition of Done

The Prompt Contract / Prompt Versioning Layer is done when it can act as the controlled prompt-governance interface for Agent_X.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
prompt contracts validate
prompt versions validate
prompt registry loads deterministically
duplicate contracts are rejected
duplicate versions are rejected
active version rules are enforced
prompt version hashes are recorded and verified
registry snapshot hashes are recorded for runtime bindings
prompt safety rules are enforced
prompt injection defenses are checked
prompt provenance is recorded
prompt diffs are deterministic
prompt compatibility checks identify breaking changes
prompt migration records are required for breaking changes
runtime prompt binding checks role/task/model/tool/policy/context constraints
prompt audit/evidence is written
prompt evidence manifest is written
dependency-state evidence is written
completion record exists
no LLM call occurs in this layer
no tool execution occurs in this layer
no network call occurs in this layer
no raw shell occurs in this layer
no direct source mutation occurs in this layer
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_prompt_schemas.py
git status --short
```

Expected proof:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 38. Go / No-Go Rules

## 38.1 GO Criteria

The layer may be marked DONE only if all are true:

```text
compileall passes
pytest passes
schema validation passes
all target files exist
all required schemas exist
all required tests exist
prompt registry loads
prompt duplicate checks pass
prompt active-version checks pass
prompt compatibility checks pass
prompt migration checks pass
prompt runtime binding checks pass
prompt safety checks pass
prompt provenance checks pass
prompt audit/evidence checks pass
evidence hashes exist
completion record exists
no source mutation occurs outside expected runtime artifacts
no model execution occurs
no tool execution occurs
no network call occurs
no raw shell occurs
```

## 38.2 NO-GO Criteria

The layer is NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
prompt registry silently overwrites entries
duplicate active versions are allowed
breaking prompt change activates without migration/governance evidence
runtime binding allows disallowed role
runtime binding allows disallowed tool
runtime binding allows disallowed task type
runtime binding allows disallowed model profile when metadata exists
policy-denied prompt use is allowed
unsafe prompt instructions pass safety validation
prompt injection bypass instructions pass safety validation
prompt provenance is missing
prompt evidence is missing
evidence hashes are missing
LLM call occurs
tool execution occurs
network call occurs
raw shell occurs
source mutation occurs directly in this layer
completion record is missing
```

---

# 39. Final Frozen Acceptance Matrix

| Area | Required proof | Status |
|---|---|---|
| Subdirectory | `tools/agentx_evolve/prompts/` exists | PASS / FAIL / NOT CHECKED |
| Schemas | all prompt schemas exist | PASS / FAIL / NOT CHECKED |
| Tests | all required tests exist | PASS / FAIL / NOT CHECKED |
| Compile | compileall passes | PASS / FAIL / NOT RUN |
| Pytest | pytest passes | PASS / FAIL / NOT RUN |
| Schema validation | dedicated script or pytest equivalent passes | PASS / FAIL / NOT RUN |
| Registry | duplicate and active-version rules enforced | PASS / FAIL / NOT CHECKED |
| Versioning | hashes, provenance, activation rules enforced | PASS / FAIL / NOT CHECKED |
| Compatibility | breaking changes detected | PASS / FAIL / NOT CHECKED |
| Migration | required migration records enforced | PASS / FAIL / NOT CHECKED |
| Diff | deterministic diff and hash | PASS / FAIL / NOT CHECKED |
| Runtime binding | role/task/model/tool/policy/context checked | PASS / FAIL / NOT CHECKED |
| Safety | bypass/injection/drift checks enforced | PASS / FAIL / NOT CHECKED |
| Evidence | histories, latest binding, manifest, completion record | PASS / FAIL / NOT CHECKED |
| Hashes | prompt, registry, diff, evidence hashes exist | PASS / FAIL / NOT CHECKED |
| Boundary | no LLM/tool/network/raw-shell execution | PASS / FAIL / NOT CHECKED |
| Source mutation | no direct source mutation | PASS / FAIL / NOT CHECKED |

Any `FAIL`, `NOT RUN`, or required `NOT CHECKED` status blocks DONE.

---

# 40. Final Implementation Sequence for Coding Agent

Use this sequence:

```text
1. Create tools/agentx_evolve/prompts/ package.
2. Implement prompt_models.py.
3. Create prompt schemas.
4. Create schema example tests.
5. Implement prompt_validator.py.
6. Implement prompt_registry.py.
7. Implement prompt_safety.py.
8. Implement prompt_provenance.py.
9. Implement prompt_diff.py.
10. Implement prompt_compatibility.py.
11. Implement prompt_migration.py.
12. Implement prompt_versioning.py.
13. Implement prompt_runtime_binding.py.
14. Implement prompt_audit_logger.py.
15. Create integration-boundary tests.
16. Create negative tests.
17. Run compileall.
18. Run pytest.
19. Run schema validation.
20. Verify git status.
21. Write evidence manifest.
22. Write completion record.
```

Do not reorder unless required by real import dependencies.

---

# 41. Coding Agent Handoff Checklist

Before implementation begins, confirm:

```text
[ ] The target repository is Agent_X.
[ ] The new prompt package must live under tools/agentx_evolve/prompts/.
[ ] Schemas must live under tools/agentx_evolve/schemas/.
[ ] Tests must live under tools/agentx_evolve/tests/.
[ ] Runtime artifacts must live under .agentx-init/prompts/.
[ ] Prompt layer must not execute LLM calls.
[ ] Prompt layer must not execute tools.
[ ] Prompt layer must not call network.
[ ] Prompt layer must not perform source mutation.
[ ] Prompt registry must be deterministic.
[ ] Prompt versions must be explicit.
[ ] Active prompt version must be explicitly selected.
[ ] Breaking prompt changes require migration/governance evidence.
[ ] Runtime binding must check role/task/model/tool/policy/context constraints.
[ ] Runtime binding must record registry snapshot hash.
[ ] Prompt body hashes must be recorded.
[ ] Prompt provenance must be recorded.
[ ] Prompt audit/evidence must be written.
[ ] Evidence hashes must be written.
[ ] Tests must run without GPU, network, hosted model, LLM, Bun, Node, or running MCP server.
```

---

# 42. Final Freeze Rule

This v3 document is frozen as the implementation specification for the Prompt Contract / Prompt Versioning Layer.

Allowed future changes:

```text
PATCH: typo fixes, wording clarification, example corrections
MINOR: additive optional CLI/report fields that do not change safety behavior
MAJOR: changed prompt permission semantics, changed runtime binding policy, changed required schemas, new required prompt category, or changed evidence boundary
```

Blocked without major revision:

```text
allowing unregistered prompt strings
allowing prompt binding without policy when not in schema-only mode
removing prompt body hashes
removing registry snapshot hashes
removing migration requirement for breaking changes
allowing LLM execution in this layer
allowing tool execution in this layer
allowing network calls in this layer
allowing raw shell execution in this layer
removing evidence logging
logging unredacted prompt bodies by default
```

---

# 43. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

Reason:

```text
It defines exact subdirectories, package exports, files, schemas, classes, functions, registry behavior, versioning behavior, compatibility checks, migration rules, diffing rules, runtime artifacts, integrations, dependency fallbacks, schema examples, locking/idempotency, worker payload rendering, prompt safety and injection controls, evidence propagation, hashing/provenance, dependency-state evidence, CLI optional handling, test cases, implementation order, acceptance criteria, drift blockers, and Definition of Done for the Prompt Contract / Prompt Versioning Layer.
```
