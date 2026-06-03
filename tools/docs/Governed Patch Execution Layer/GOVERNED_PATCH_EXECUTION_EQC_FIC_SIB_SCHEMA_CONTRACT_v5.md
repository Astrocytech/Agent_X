# GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v5

```text
document_id: GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v5.0
status: final frozen controlling contract, implementation-ready, command/API explicit
component_id: AGENTX_GOVERNED_PATCH_EXECUTION
component_name: Governed Patch Execution Layer
roadmap_layer: 3
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria if CLI commands are exposed
risk_level: critical
implementation_mode: deterministic post-sandbox source-change actuator
target_language: Python
canonical_subdirectory: tools/agentx_evolve/patch_execution/
runtime_state_root: .agentx-init/implementation/
opencode_basis: edit/write/patch/apply_patch concepts, diff visibility, permission-scanned shell separation
agentx_basis:
  - completed Agent_X Initiator
  - validated Security Sandbox / Filesystem Boundary Layer
  - Policy / Capability Registry, required or fail-closed adapter
v4_rating: 9.8/10
v5_rating: 10/10
```

---

# 0. v5 Review and Upgrade Summary

## 0.1 v4 Rating

The v4 contract was rated:

```text
9.8/10
```

## 0.2 Why v4 Was Not Fully 10/10

v4 was nearly complete. It had the main architecture, schemas, dry-run, rollback, source guard, validation, patch limits, binary rules, evidence rules, idempotency, temporary policy bridge, public API expectations, and freeze rule.

The remaining gaps were small but useful before handing it to an implementation LLM:

```text
1. It did not explicitly decide whether this layer exposes CLI commands in v1.
2. It did not define the future command/API surface if CLI commands are later exposed.
3. It did not explicitly list validated prerequisites, including the completed Security Sandbox commit evidence.
4. It did not include a direct "do not begin implementation unless" pre-code gate.
5. It did not include a final separation between runtime evidence and implementation evidence strongly enough for commits.
6. It did not include a final "contract is now frozen; next artifact must be implementation spec" statement near the top.
```

## 0.3 v5 Improvements

This v5 adds:

```text
CLI exposure policy
future command/API surface
validated prerequisite gate
pre-code gate
runtime evidence vs implementation evidence clarification
final top-level freeze direction
```

Final v5 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the final controlling contract for the **Governed Patch Execution Layer**.

This layer is the deterministic actuator that turns an approved implementation proposal into bounded source changes, validation, rollback, and evidence.

It comes after:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary Layer
Policy / Capability Registry, or a fail-closed temporary policy bridge
```

It must never behave like a free editing agent. It must apply only explicitly approved, bounded, schema-governed changes.

The layer exists to provide this safe chain:

```text
approved proposal or explicit patch input
→ policy/capability check
→ governance reference check
→ sandbox/path check
→ dry-run preview
→ rollback snapshot
→ patch application
→ source change guard
→ validation gate
→ rollback or accept
→ evidence/audit record
→ completion record
```

---

# 2. Standards Package

## 2.1 Primary Standard: EQC

EQC is primary because this layer controls live source mutation.

It must guarantee:

```text
only approved files change
L0 is never modified
protected paths are never modified
patches are applied only under session control
rollback snapshot exists before mutation
validation runs after mutation
failed validation triggers rollback or explicit failure state
evidence is written for every session
unsafe patch attempts fail closed
```

## 2.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete files and APIs:

```text
patch_models.py
patch_policy.py
patch_session.py
patch_applier.py
rollback_manager.py
source_change_guard.py
implementation_validation_gate.py
patch_evidence.py
patch_execution_service.py
initiator_patch_compat.py
```

## 2.3 Required Supporting Standard: SIB

SIB is required because this layer connects:

```text
Initiator proposal/governance/risk artifacts
Security Sandbox path/write checks
Policy / Capability Registry decisions
Validation Runner
Source Guard
Runtime artifacts
Rollback snapshots
Audit/memory/graph evidence
Future Tool/MCP Adapter
Future Self-Evolution Orchestrator
```

## 2.4 Required Supporting Standard: Schema Contract

Schema Contract is required because this layer produces structured artifacts:

```text
implementation_session.schema.json
patch_application.schema.json
patch_operation.schema.json
patch_result.schema.json
dry_run_result.schema.json
rollback_snapshot.schema.json
rollback_record.schema.json
source_inventory.schema.json
source_change_guard.schema.json
implementation_validation_gate.schema.json
patch_execution_decision.schema.json
patch_execution_audit.schema.json
patch_limits.schema.json
temporary_policy_bridge.schema.json
```

## 2.5 Required Supporting Standard: Evidence / Audit Rules

Every patch execution session must produce evidence.

Evidence is required for:

```text
session start
proposal loaded
governance decision loaded
policy decision loaded
sandbox precheck
dry-run result
rollback snapshot created
patch applied
source change guard result
validation result
rollback result if needed
acceptance decision
failure decision
completion record
```

---

# 3. Canonical Location

This layer must live under:

```text
tools/agentx_evolve/patch_execution/
```

Required package tree:

```text
tools/
  agentx_evolve/
    patch_execution/
      __init__.py
      patch_models.py
      patch_policy.py
      patch_session.py
      patch_applier.py
      rollback_manager.py
      source_change_guard.py
      implementation_validation_gate.py
      patch_evidence.py
      patch_execution_service.py
      initiator_patch_compat.py
```

Schemas:

```text
tools/agentx_evolve/schemas/08_patch/implementation_session.schema.json
tools/agentx_evolve/schemas/08_patch/patch_application.schema.json
tools/agentx_evolve/schemas/08_patch/patch_operation.schema.json
tools/agentx_evolve/schemas/08_patch/patch_result.schema.json
tools/agentx_evolve/schemas/20_orchestrator/dry_run_result.schema.json
tools/agentx_evolve/schemas/08_patch/rollback_snapshot.schema.json
tools/agentx_evolve/schemas/08_patch/rollback_record.schema.json
tools/agentx_evolve/schemas/15_packaging/source_inventory.schema.json
tools/agentx_evolve/schemas/08_patch/source_change_guard.schema.json
tools/agentx_evolve/schemas/08_patch/implementation_validation_gate.schema.json
tools/agentx_evolve/schemas/08_patch/patch_execution_decision.schema.json
tools/agentx_evolve/schemas/08_patch/patch_execution_audit.schema.json
tools/agentx_evolve/schemas/08_patch/patch_limits.schema.json
tools/agentx_evolve/schemas/16_policy/temporary_policy_bridge.schema.json
```

Tests:

```text
tools/agentx_evolve/tests/test_patch_session.py
tools/agentx_evolve/tests/test_patch_applier.py
tools/agentx_evolve/tests/test_rollback_manager.py
tools/agentx_evolve/tests/test_source_change_guard.py
tools/agentx_evolve/tests/test_implementation_validation_gate.py
tools/agentx_evolve/tests/test_patch_evidence.py
tools/agentx_evolve/tests/test_patch_execution_schema.py
tools/agentx_evolve/tests/test_patch_execution_negative_cases.py
tools/agentx_evolve/tests/test_patch_execution_sandbox_integration.py
tools/agentx_evolve/tests/test_patch_execution_policy_integration.py
tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
tools/agentx_evolve/tests/test_patch_execution_limits.py
tools/agentx_evolve/tests/test_patch_execution_idempotency.py
```

Runtime artifacts:

```text
.agentx-init/implementation/sessions/<session_id>.json
.agentx-init/implementation/implementation_history.jsonl
.agentx-init/implementation/implementation_evidence.jsonl
.agentx-init/implementation/patch_applications.jsonl
.agentx-init/implementation/dry_run_results.jsonl
.agentx-init/implementation/source_inventories.jsonl
.agentx-init/implementation/source_change_guard_results.jsonl
.agentx-init/implementation/validation_gate_results.jsonl
.agentx-init/implementation/rollback_snapshots/<session_id>/
.agentx-init/implementation/rollback_history.jsonl
.agentx-init/implementation/latest_implementation_session.json
.agentx-init/implementation/latest_patch_result.json
.agentx-init/implementation/latest_dry_run_result.json
.agentx-init/implementation/latest_rollback_record.json
```

---

# 4. Validated Prerequisite Gate

Implementation of this layer must not begin unless the following prerequisite state is true.

## 4.1 Required Completed Layers

```text
Agent_X Initiator: COMPLETE
Security Sandbox / Filesystem Boundary Layer: VALIDATED — DONE
```

Known Security Sandbox validation evidence:

```text
validation commit: ecd32c1
compileall: PASS
pytest: PASS, 648/648
git status: CLEAN
completion evidence: .agentx-init/security/security_sandbox_completion_record.json
```

## 4.2 Required Policy State

One of the following must be true:

```text
Policy / Capability Registry is implemented and validated
```

or:

```text
temporary fail-closed policy bridge is implemented exactly as defined in this contract
```

If neither is true, Governed Patch Execution must remain:

```text
BLOCKED_PRECONDITION
```

## 4.3 Required Pre-Code Gate

Before coding begins, confirm:

```text
[ ] Security Sandbox is validated and callable.
[ ] Policy Registry exists or temporary fail-closed bridge will be used.
[ ] Canonical subdirectory is tools/agentx_evolve/patch_execution/.
[ ] Runtime state root is .agentx-init/implementation/.
[ ] No LLM/model code belongs in this layer.
[ ] No MCP server belongs in this layer.
[ ] No Git push belongs in this layer.
[ ] Dry-run is implemented before live mutation.
[ ] Rollback snapshot is implemented before live mutation.
[ ] Source Change Guard is implemented before final ACCEPTED state.
```

---

# 5. CLI Exposure and Command/API Policy

## 5.1 v1 CLI Decision

The v1 implementation does not need to expose a public CLI command.

Preferred first implementation:

```text
Python API only
pytest-driven validation
runtime evidence artifacts
```

If CLI commands are exposed anyway, Command Acceptance Criteria becomes required.

## 5.2 Future CLI Command Surface

Future CLI may expose:

```text
agentx-patch dry-run --proposal <proposal_id>
agentx-patch apply --proposal <proposal_id>
agentx-patch rollback <session_id>
agentx-patch status <session_id>
agentx-patch verify <session_id>
agentx-patch list
```

## 5.3 CLI Rules If Implemented

Any CLI command must:

```text
fail closed on missing policy context
fail closed on missing governance context
fail closed on sandbox BLOCK
write schema-valid runtime evidence
return deterministic exit codes
not mutate source in dry-run mode
not execute Git push
not execute network calls
not call LLM/model code
```

Required exit codes if CLI exists:

```text
0 = success
1 = failed
2 = invalid arguments
3 = blocked by policy/governance/sandbox
4 = validation failed
5 = rollback required or rollback failed
6 = schema validation failed
7 = precondition missing
```

## 5.4 Public Python API Surface

The implementation spec must define exact signatures, but the contract requires these capabilities:

```python
create_implementation_session(...)
run_patch_dry_run(...)
apply_governed_patch(...)
create_rollback_snapshot(...)
rollback_session(...)
verify_source_changes(...)
run_validation_gate(...)
write_patch_evidence(...)
finalize_patch_session(...)
```

Public API rules:

```text
return schema-aligned dataclass or dict results
never return bare booleans as final decisions
include session_id in session-bound results
fail closed on missing policy/sandbox/governance context
write evidence for live mutation attempts
```

---

# 6. Minimal First Implementation Slice

The first implementation pass should be deliberately small.

## 4.1 Slice A — Session, Policy Bridge, Sandbox Precheck, Dry-Run

Implement first:

```text
patch_models.py
patch_policy.py
patch_session.py
dry-run result schema
temporary policy bridge schema
sandbox precheck integration
tests for blocked cases
```

Must prove:

```text
session can be created
missing governance blocks
missing policy blocks
L0 target blocks
protected target blocks
outside-repo target blocks
dry-run changes nothing
```

## 4.2 Slice B — Rollback Snapshot and Source Inventory

Implement second:

```text
rollback_manager.py
source_change_guard.py
source inventory schema
rollback snapshot schema
rollback record schema
```

Must prove:

```text
snapshot created before mutation
before hashes recorded
created files tracked
rollback restores files
created files removed on rollback
```

## 4.3 Slice C — Patch Application

Implement third:

```text
patch_applier.py
EXACT_EDIT
WRITE_FILE
CREATE_FILE
PATCH_TEXT bounded mode
binary block
limit checks
partial failure handling
```

Must prove:

```text
approved patch applies
unapproved patch blocks
partial failure triggers rollback
binary mutation blocks
patch limits enforce
```

## 4.4 Slice D — Validation and Evidence

Implement fourth:

```text
implementation_validation_gate.py
patch_evidence.py
patch_execution_service.py
audit events
latest artifact writes
completion evidence
```

Must prove:

```text
validation command allowlist works
validation failure triggers rollback
evidence is written
latest artifacts are atomic
completion record can be generated
```

---

# 7. Component Scope

## 5.1 Required in v1

The first implementation must provide:

```text
implementation session lifecycle
patch proposal loading or explicit patch input
approved target path checking
policy/capability fail-closed check
sandbox precheck integration
dry-run mode
rollback snapshot creation
bounded patch application
safe exact edit application
safe file write application
source inventory before and after mutation
source change guard after mutation
validation command handoff/precheck
rollback on failure
rollback verification
implementation evidence records
completion record
negative safety tests
resource-limit tests
idempotency tests
```

## 5.2 Not Required in v1

Do not implement yet:

```text
LLM patch generation
MCP server
background daemon
multi-agent execution
automatic Git commit
automatic Git push
promotion gate
human review UI
full remote execution
network patch fetching
model-based patch repair
parallel patch sessions
```

---

# 8. Temporary Policy Bridge Contract

Until the full Policy / Capability Registry is implemented, this layer must use a temporary policy bridge that fails closed.

## 6.1 TemporaryPolicyBridge Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "temporary_policy_bridge.schema.json",
  "policy_bridge_id": "string",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "mode": "TEMPORARY_FAIL_CLOSED",
  "allowed_roles": [],
  "allowed_operations": [],
  "allowed_paths": [],
  "blocked_paths": [],
  "requires_governance": true,
  "requires_rollback": true,
  "status": "ACTIVE",
  "warnings": [],
  "errors": []
}
```

## 6.2 Temporary Policy Rules

Default:

```text
block unknown role
block unknown operation
block missing governance reference
block missing explicit allowed path
block L0/protected/outside-repo path even if allowed list says otherwise
block delete/rename/binary/network/shell mutation
```

Allow only:

```text
explicit test fixture paths
explicit low-risk approved paths
EXACT_EDIT / WRITE_FILE / CREATE_FILE / bounded PATCH_TEXT
```

This bridge must be replaceable by the full Policy / Capability Registry without changing patch execution semantics.

---

# 9. Relationship to Existing Layers

## 7.1 Agent_X Initiator

The Initiator remains the control and evidence foundation.

This layer must consume Initiator outputs such as:

```text
patch proposal
governance decision
risk assessment
validation plan
audit evidence
graph/memory references
```

It must not replace:

```text
Governance Engine
Risk Engine
Validation Runner
Source Guard
Audit Log
Memory Store
Knowledge Graph
```

## 7.2 Security Sandbox / Filesystem Boundary Layer

The Security Sandbox is validated and done.

This patch layer must use it before any file mutation.

Required sandbox integration:

```text
safe_patch_precheck
check_write_allowed
safe_read_file
safe_write_file where appropriate
path boundary checks
L0 write block
protected path block
runtime state boundary
secret redaction before evidence logging
subprocess precheck for validation commands
```

A patch layer ALLOW can never override a sandbox BLOCK.

## 7.3 Policy / Capability Registry

When the full registry exists, it replaces the temporary bridge as the policy authority.

Required policy checks:

```text
caller role allowed
operation allowed
target path allowed
risk tier acceptable
governance required and present
rollback required and present
validation required
approval requirement satisfied where applicable
```

---

# 10. Authority Precedence

When multiple systems return decisions, the strictest result wins.

Required precedence:

```text
1. L0_BLOCK
2. PATH_ESCAPE_BLOCK
3. SYMLINK_ESCAPE_BLOCK
4. SANDBOX_BLOCK
5. POLICY_BLOCK
6. GOVERNANCE_BLOCK
7. MISSING_ROLLBACK_SNAPSHOT
8. SOURCE_GUARD_BLOCK
9. VALIDATION_FAILED
10. EVIDENCE_WRITE_FAILED
11. ALLOW
```

Rules:

```text
ALLOW never overrides BLOCK.
Policy ALLOW never overrides sandbox BLOCK.
Governance ALLOW never overrides L0_BLOCK.
Validation PASS never overrides source guard failure.
Human approval cannot override L0/path/symlink/sandbox blocks.
Evidence write failure after mutation must trigger FAILED state and preserve rollback availability.
```

---

# 11. OpenCode Borrowing Notes

## 9.1 Borrowed Concepts

Borrow these concepts from OpenCode-style coding agent design:

```text
patch/apply_patch as a first-class edit primitive
exact edit for small deterministic replacements
write operation as a distinct tool
diff visibility before/after mutation
permission scanning before shell-like validation commands
explicit invalid-tool / invalid-operation handling
tool-specific behavior instead of shell-for-everything
```

## 9.2 Restricted Concepts

Do not borrow these OpenCode assumptions directly:

```text
broad shell availability
network fetch/search availability
plugin tool execution
subagent execution
unrestricted agent editing
UI-driven approval assumptions
provider-driven trust model
```

Do not copy OpenCode TypeScript/Bun source code. OpenCode is a design reference only.

---

# 12. Public API Expectations

The implementation spec should define exact signatures, but the contract requires at least these public capabilities:

```python
create_implementation_session(...)
run_patch_dry_run(...)
apply_governed_patch(...)
create_rollback_snapshot(...)
rollback_session(...)
verify_source_changes(...)
run_validation_gate(...)
write_patch_evidence(...)
finalize_patch_session(...)
```

Required behavior:

```text
public APIs return schema-aligned dataclass/dict results
public APIs never return bare booleans as final decisions
public APIs include session_id in all session-bound results
public APIs fail closed on missing policy/sandbox/governance context
```

---

# 13. Patch Execution Lifecycle

Required lifecycle:

```text
CREATED
PROPOSAL_LOADED
GOVERNANCE_CHECKED
POLICY_CHECKED
SANDBOX_CHECKED
DRY_RUN_READY
SNAPSHOT_CREATED
PATCH_APPLIED
SOURCE_GUARD_CHECKED
VALIDATION_RUNNING
VALIDATION_PASSED
VALIDATION_FAILED
ROLLBACK_RUNNING
ROLLED_BACK
ROLLBACK_FAILED
ACCEPTED
FAILED
BLOCKED
```

Rules:

```text
No source mutation before session is CREATED.
No source mutation before POLICY_CHECKED.
No source mutation before SANDBOX_CHECKED.
No source mutation before SNAPSHOT_CREATED.
No ACCEPTED session without SOURCE_GUARD_CHECKED.
No ACCEPTED session without validation result unless explicitly docs-only and policy permits.
No failed validation may be silently accepted.
No rollback failure may be ignored.
ROLLBACK_FAILED must block future patch sessions until reviewed.
```

---

# 14. Locking and Concurrency Contract

Default:

```text
one active patch execution session at a time
```

Required locks:

```text
.agentx-init/implementation/patch_execution.lock
.agentx-init/implementation/rollback.lock
```

Rules:

```text
lock before snapshot
lock before live patch application
release lock only after ACCEPTED, ROLLED_BACK, FAILED, or BLOCKED final state is written
stale lock must be detectable
stale lock must require explicit recovery evidence
parallel patch sessions are not allowed in v1
```

Acceptance:

```text
two concurrent patch sessions cannot mutate files at the same time
```

---

# 15. Patch Limits Contract

## 13.1 Default Limits

The v1 patch layer must enforce conservative defaults:

```text
max_changed_files_per_session: 5
max_patch_operations_per_session: 20
max_single_file_bytes: 1048576
max_patch_text_bytes: 262144
max_total_snapshot_bytes: 10485760
max_validation_runtime_seconds: 120
max_session_runtime_seconds: 300
```

## 13.2 PatchLimits Schema

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_limits.schema.json",
  "limits_id": "string",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "max_changed_files_per_session": 5,
  "max_patch_operations_per_session": 20,
  "max_single_file_bytes": 1048576,
  "max_patch_text_bytes": 262144,
  "max_total_snapshot_bytes": 10485760,
  "max_validation_runtime_seconds": 120,
  "max_session_runtime_seconds": 300,
  "status": "ACTIVE",
  "warnings": [],
  "errors": []
}
```

If limits are exceeded:

```text
BLOCKED_RESOURCE_LIMIT
```

No limit may be silently ignored.

---

# 16. Schema Strictness Rules

All governed patch execution schemas must be strict.

Required JSON Schema policy:

```text
required fields must be explicit
enum fields must be enumerated
additionalProperties should be false unless extension is intentional
nullable fields must use explicit null allowance
arrays must define item types
status values must be enum-limited
schema_id must match file name
schema_version must be present
```

Any schema validation failure for a runtime artifact must block that artifact from replacing the previous valid latest artifact.

---

# 17. Patch Application Schema Contract

## 15.1 PatchApplication

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_application.schema.json",
  "application_id": "string",
  "session_id": "string",
  "proposal_id": "string|null",
  "governance_decision_id": "string|null",
  "policy_decision_id": "string|null",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "mode": "DRY_RUN|LIVE",
  "operations": [],
  "target_paths": [],
  "status": "PENDING|APPLIED|BLOCKED|FAILED|DRY_RUN",
  "before_hashes": {},
  "after_hashes": {},
  "warnings": [],
  "errors": []
}
```

## 15.2 PatchOperation

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_operation.schema.json",
  "operation_id": "string",
  "operation_type": "EXACT_EDIT|WRITE_FILE|CREATE_FILE|DELETE_FILE|RENAME_FILE|PATCH_TEXT",
  "target_path": "string",
  "old_text": "string|null",
  "new_text": "string|null",
  "content": "string|null",
  "allow_create": false,
  "allow_delete": false,
  "expected_before_hash": "string|null",
  "requires_rollback_snapshot": true,
  "approved": false
}
```

## 15.3 Patch Text Format Rules

`PATCH_TEXT` must be bounded and explicit.

Allowed in v1:

```text
unified diff targeting explicit approved files
single-file or multi-file patch only if all target paths are declared before application
no binary patches
no rename-only patches
no delete-only patches
no chmod/mode changes
no symlink creation
```

Block if patch text contains:

```text
target path not listed in target_paths
path traversal
absolute outside-repo path
/dev/null delete without explicit delete policy
binary patch marker
file mode changes
symlink mode
Git index lines that imply rename/delete without approved operation
```

## 15.4 Binary File Policy

Default:

```text
binary file mutation is blocked in v1
```

Allowed:

```text
read-only binary snapshot hashing
rollback snapshot copy of existing binary file if already approved target
```

Blocked:

```text
binary patch application
binary content write
binary exact edit
```

## 15.5 Encoding and Line Ending Policy

Default:

```text
UTF-8 text files
preserve existing line endings where practical
do not normalize line endings unless operation explicitly says so
fail closed on undecodable text unless binary snapshot-only path
```

---

# 18. Dry-Run Schema Contract

## 16.1 DryRunResult

```json
{
  "schema_version": "1.0",
  "schema_id": "dry_run_result.schema.json",
  "dry_run_id": "string",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "would_change_paths": [],
  "would_create_paths": [],
  "would_delete_paths": [],
  "sandbox_decision_ids": [],
  "policy_decision_id": "string|null",
  "rollback_required": true,
  "validation_plan": [],
  "status": "PASS|BLOCKED|FAILED",
  "warnings": [],
  "errors": []
}
```

Dry-run must:

```text
run policy checks
run sandbox checks
compute target paths
compute expected changes
not mutate source files
not create rollback snapshots unless explicitly configured
write dry-run evidence
return BLOCKED if live run would be blocked
```

---

# 19. Atomic Mutation and Partial Failure Rules

## 17.1 Mutation Sequence

Live mutation must occur in this order:

```text
1. create session
2. acquire patch lock
3. run policy check
4. run sandbox check
5. write dry-run evidence or validate dry-run equivalent
6. create rollback snapshot
7. write source inventory BEFORE
8. apply operation 1
9. apply operation 2...
10. write source inventory AFTER
11. run source change guard
12. run validation gate
13. accept or rollback
14. write final evidence
15. release lock
```

## 17.2 Partial Apply Failure

If any operation fails after mutation begins:

```text
stop applying remaining operations
record PATCH_APPLY_FAILED
run rollback
verify rollback
write failure evidence
do not accept session
```

No partial success may be accepted in v1.

## 17.3 Evidence Write Failure After Mutation

If evidence writing fails after mutation:

```text
attempt rollback unless mutation is already safely accepted and evidence can be recovered
record EVIDENCE_WRITE_FAILED if possible
keep rollback snapshot
block final ACCEPTED state
require human review
```

---

# 20. Rollback Manager Schema Contract

## 18.1 RollbackSnapshot

```json
{
  "schema_version": "1.0",
  "schema_id": "rollback_snapshot.schema.json",
  "snapshot_id": "string",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "RollbackManager",
  "snapshot_root": ".agentx-init/implementation/rollback_snapshots/<session_id>/",
  "files": [
    {
      "path": "string",
      "existed_before": true,
      "before_hash": "string|null",
      "snapshot_path": "string|null"
    }
  ],
  "status": "CREATED|FAILED",
  "warnings": [],
  "errors": []
}
```

## 18.2 RollbackRecord

```json
{
  "schema_version": "1.0",
  "schema_id": "rollback_record.schema.json",
  "rollback_id": "string",
  "session_id": "string",
  "snapshot_id": "string",
  "timestamp": "string",
  "source_component": "RollbackManager",
  "trigger": "VALIDATION_FAILED|SOURCE_GUARD_FAILED|PATCH_FAILED|USER_REQUEST|UNKNOWN",
  "restored_files": [],
  "removed_created_files": [],
  "verification_status": "PASS|FAILED",
  "status": "ROLLED_BACK|FAILED",
  "warnings": [],
  "errors": []
}
```

Before live mutation:

```text
snapshot all existing target files
record non-existing target files as existed_before=false
store before hashes
store snapshot under session-specific directory
write snapshot record before mutation
```

After rollback:

```text
restore existing files from snapshot
remove files created during session
verify hashes match before state
write rollback record
enter safe mode if rollback verification fails
```

---

# 21. Source Inventory and Source Change Guard Contract

## 19.1 SourceInventory

```json
{
  "schema_version": "1.0",
  "schema_id": "source_inventory.schema.json",
  "inventory_id": "string",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "SourceChangeGuard",
  "scope": "BEFORE|AFTER",
  "tracked_paths": [],
  "path_hashes": {},
  "git_status_short": "string|null",
  "warnings": [],
  "errors": []
}
```

## 19.2 SourceChangeGuardResult

```json
{
  "schema_version": "1.0",
  "schema_id": "source_change_guard.schema.json",
  "guard_id": "string",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "SourceChangeGuard",
  "approved_paths": [],
  "actual_changed_paths": [],
  "unexpected_paths": [],
  "missing_expected_paths": [],
  "forbidden_paths": [],
  "status": "PASS|BLOCKED|FAILED",
  "warnings": [],
  "errors": []
}
```

Required checks:

```text
approved paths match actual changed files
no L0 files changed
no protected paths changed
no outside-repo files changed
no unapproved files changed
new files are approved
deleted files are approved
git diff/status can be used as secondary evidence
```

---

# 22. Implementation Session Schema Contract

## 20.1 ImplementationSession

```json
{
  "schema_version": "1.0",
  "schema_id": "implementation_session.schema.json",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "proposal_id": "string|null",
  "governance_decision_id": "string|null",
  "policy_decision_id": "string|null",
  "sandbox_decision_ids": [],
  "dry_run_id": "string|null",
  "rollback_snapshot_id": "string|null",
  "patch_application_id": "string|null",
  "source_inventory_before_id": "string|null",
  "source_inventory_after_id": "string|null",
  "source_change_guard_id": "string|null",
  "validation_result_id": "string|null",
  "rollback_record_id": "string|null",
  "target_paths": [],
  "changed_paths": [],
  "lifecycle_state": "CREATED",
  "status": "CREATED|BLOCKED|FAILED|ROLLED_BACK|ROLLBACK_FAILED|ACCEPTED",
  "final_decision": "PENDING|ACCEPT|REJECT|ROLLBACK",
  "warnings": [],
  "errors": []
}
```

Session rules:

```text
session_id must be generated before any mutation
target_paths must be known before mutation
session must be written before mutation
session must be updated after every lifecycle transition
latest session must be atomically written
history must be append-only
```

---

# 23. Validation Gate Contract

## 21.1 ValidationGateResult

```json
{
  "schema_version": "1.0",
  "schema_id": "implementation_validation_gate.schema.json",
  "validation_gate_id": "string",
  "session_id": "string",
  "timestamp": "string",
  "source_component": "ImplementationValidationGate",
  "commands_requested": [],
  "commands_allowed": [],
  "commands_blocked": [],
  "validation_status": "PASS|FAILED|BLOCKED|SKIPPED",
  "requires_rollback": false,
  "reason": "string",
  "warnings": [],
  "errors": []
}
```

Validation rules:

```text
validation command must be allowlisted
validation command must pass sandbox subprocess precheck
failed validation triggers rollback unless policy explicitly marks failure acceptable
validation cannot be skipped for source changes
docs-only skip requires policy permission and evidence
```

---

# 24. Patch Execution Policy Matrix

| Operation | Default | Required Conditions |
|---|---|---|
| EXACT_EDIT | Allowed if approved | target path approved, sandbox allows, rollback snapshot exists |
| WRITE_FILE | Blocked unless approved | target path approved, governance/policy allow, rollback snapshot exists |
| CREATE_FILE | Blocked unless approved | parent path approved, sandbox allows, session records created file |
| DELETE_FILE | Blocked in v1 | explicit policy required later |
| RENAME_FILE | Blocked in v1 | explicit policy required later |
| PATCH_TEXT | Allowed if bounded | all target paths explicit, sandbox allows, rollback exists |
| Binary edit | Blocked in v1 | none |
| L0 edit | Always blocked | none |
| Protected path edit | Always blocked unless future special governance | none in v1 |
| Outside repo edit | Always blocked | none |
| Network patch fetch | Always blocked in v1 | none |
| Shell-based file mutation | Always blocked | use patch layer instead |

---

# 25. Audit / Evidence Contract

Required logs:

```text
.agentx-init/implementation/implementation_history.jsonl
.agentx-init/implementation/implementation_evidence.jsonl
.agentx-init/implementation/patch_applications.jsonl
.agentx-init/implementation/dry_run_results.jsonl
.agentx-init/implementation/source_inventories.jsonl
.agentx-init/implementation/source_change_guard_results.jsonl
.agentx-init/implementation/validation_gate_results.jsonl
.agentx-init/implementation/rollback_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Evidence event:

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_execution_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "GovernedPatchExecution",
  "event_type": "SESSION_STARTED|DRY_RUN_COMPLETED|PATCH_APPLIED|VALIDATION_PASSED|VALIDATION_FAILED|ROLLBACK_STARTED|ROLLED_BACK|ROLLBACK_FAILED|ACCEPTED|BLOCKED|FAILED",
  "session_id": "string",
  "decision": "ALLOW|BLOCK|ACCEPT|ROLLBACK|FAILED",
  "artifacts": [],
  "warnings": [],
  "errors": []
}
```

Evidence rules:

```text
append-only JSONL
latest JSON written atomically
no unredacted secrets
no raw model prompts
no raw command output unless redacted
no evidence deletion during rollback
no evidence deletion during cleanup
```

---

# 26. Idempotency and Repeated Session Rules

## 24.1 Session IDs

```text
Every live or dry-run session gets a unique session_id.
Re-running the same patch must not reuse a previous session_id.
```

## 24.2 Repeated Patch Attempts

If the same patch is applied twice:

```text
second run must either block as already-applied
or create a new session and fail exact-match checks safely
or apply only if operation is explicitly idempotent
```

No repeated run may silently corrupt source state.

## 24.3 Stale Runtime Artifacts

Stale prior artifacts may be read for context, but must not be overwritten except via atomic latest artifact write.

---

# 27. Temporary File and Cleanup Rules

Temporary files may be created only under:

```text
.agentx-init/implementation/tmp/
```

or the same directory as the target for atomic replace, if required by atomic write semantics.

Cleanup rules:

```text
successful session may remove temp files
failed session must preserve enough evidence for diagnosis
rollback snapshots must not be deleted automatically
audit/evidence JSONL files must not be compacted or deleted
```

---

# 28. Agent_X Integration Notes

## 26.1 Must Consume

```text
Initiator proposal artifacts
Initiator governance decision
Initiator risk assessment
Initiator validation plan
Security Sandbox decisions
Policy / Capability decisions
```

## 26.2 Must Produce

```text
implementation session
dry-run result
patch application record
rollback snapshot
rollback record
source inventory
source change guard result
validation gate result
patch execution audit event
completion record
```

## 26.3 Must Not Modify

```text
L0/
tools/agentx_initiator/ internals unless explicitly approved
governance rules
source guard rules
sandbox rules
policy registry rules
```

---

# 29. Security Sandbox Integration Notes

Before any live mutation:

```text
run sandbox patch precheck
run sandbox write check for every target path
confirm L0/protected/outside-repo blocks
confirm runtime paths are separated from source paths
confirm no symlink escape
confirm no path traversal
```

If sandbox returns:

```text
BLOCK -> block session
NEEDS_GOVERNANCE -> block until governance reference exists
NEEDS_ROLLBACK_SNAPSHOT -> create snapshot before mutation
ALLOW -> continue
```

A patch layer ALLOW cannot override a sandbox BLOCK.

---

# 30. Invariants

```yaml
invariants:
  - id: "GPE-INV-001"
    statement: "No source file may be changed before a session is created."
  - id: "GPE-INV-002"
    statement: "No live mutation may occur before sandbox precheck passes."
  - id: "GPE-INV-003"
    statement: "No live mutation may occur before rollback snapshot exists."
  - id: "GPE-INV-004"
    statement: "L0 files are never modified."
  - id: "GPE-INV-005"
    statement: "Only approved target paths may change."
  - id: "GPE-INV-006"
    statement: "Failed validation triggers rollback or explicit failed state."
  - id: "GPE-INV-007"
    statement: "Rollback failure blocks further patch sessions."
  - id: "GPE-INV-008"
    statement: "Every session must have evidence."
  - id: "GPE-INV-009"
    statement: "The patch layer never calls an LLM."
  - id: "GPE-INV-010"
    statement: "The patch layer never performs Git push."
  - id: "GPE-INV-011"
    statement: "Dry-run mode never mutates source files."
  - id: "GPE-INV-012"
    statement: "Patch execution never bypasses the Security Sandbox."
  - id: "GPE-INV-013"
    statement: "Partial apply failure never produces an accepted session."
  - id: "GPE-INV-014"
    statement: "Binary mutation is blocked in v1."
```

---

# 31. Failure Classes

```text
PATCH_SESSION_CREATE_FAILED
PATCH_PROPOSAL_INVALID
PATCH_POLICY_BLOCKED
PATCH_SANDBOX_BLOCKED
PATCH_TARGET_OUTSIDE_SCOPE
PATCH_TARGET_L0_BLOCKED
PATCH_TARGET_PROTECTED_BLOCKED
PATCH_TARGET_SYMLINK_ESCAPE
PATCH_LIMIT_EXCEEDED
PATCH_BINARY_BLOCKED
PATCH_ENCODING_FAILED
DRY_RUN_FAILED
ROLLBACK_SNAPSHOT_FAILED
PATCH_APPLY_FAILED
PARTIAL_APPLY_FAILED
SOURCE_INVENTORY_FAILED
SOURCE_CHANGE_GUARD_FAILED
VALIDATION_COMMAND_BLOCKED
VALIDATION_FAILED
ROLLBACK_FAILED
EVIDENCE_WRITE_FAILED
SCHEMA_VALIDATION_FAILED
LOCK_CONFLICT
UNKNOWN_PATCH_EXECUTION_ERROR
```

---

# 32. Test Acceptance Criteria

Required tests:

```text
test_patch_session_create
test_patch_session_blocks_without_governance
test_patch_session_blocks_without_policy
test_patch_session_blocks_l0_target
test_patch_session_blocks_protected_target
test_patch_session_blocks_outside_repo_target
test_patch_session_blocks_symlink_escape
test_dry_run_changes_nothing
test_exact_edit_applies_to_approved_file
test_write_file_applies_to_approved_file
test_create_file_applies_to_approved_path
test_patch_text_applies_to_approved_file
test_delete_file_blocked_in_v1
test_rename_file_blocked_in_v1
test_binary_patch_blocked
test_patch_limit_exceeded_blocks
test_unapproved_file_change_triggers_rollback
test_validation_failure_triggers_rollback
test_partial_apply_failure_triggers_rollback
test_rollback_restores_before_hash
test_created_file_removed_on_rollback
test_rollback_failure_blocks_future_sessions
test_source_change_guard_blocks_unexpected_path
test_evidence_written_for_success
test_evidence_written_for_failure
test_evidence_write_failure_blocks_acceptance
test_schema_validation_for_session
test_schema_validation_for_dry_run
test_schema_validation_for_rollback
test_schema_validation_for_patch_result
test_lock_blocks_parallel_patch_sessions
test_repeated_patch_does_not_corrupt_state
test_no_open_code_runtime_dependency
test_no_llm_dependency
test_no_network_dependency
test_no_git_push
```

---

# 33. Go / No-Go Criteria

## 31.1 GO

The layer can be marked DONE only if:

```text
compileall passes
all patch execution tests pass
dry-run does not mutate source
approved patch applies
unapproved patch blocks
L0/protected/outside-repo patches block
rollback snapshot is created before mutation
rollback restores files after validation failure
source change guard detects unexpected changes
validation command allowlist works
evidence is written
git status is clean except expected runtime artifacts
completion record exists
```

## 31.2 NO-GO

The layer must remain NOT DONE if any are true:

```text
source mutation occurs before snapshot
dry-run mutates source
L0 mutation is possible
sandbox block can be overridden
rollback verification fails silently
validation failure is accepted silently
unexpected source files change
evidence is missing
LLM/model dependency is added
network dependency is added
Git push exists
binary mutation is allowed
partial apply can be accepted
```

---

# 34. Definition of Done

The Governed Patch Execution Layer is done only when:

```text
all required files exist
all required schemas exist
all required tests exist
compileall passes
pytest passes
dry-run mode changes nothing
approved patch applies correctly
unapproved patch blocks
L0 patch blocks
protected path patch blocks
outside-repo patch blocks
binary mutation blocks
patch limits enforce
rollback snapshot is created before mutation
rollback restores files after failure
source change guard detects unexpected mutation
validation failure triggers rollback
partial apply failure triggers rollback
evidence records are written
latest artifacts are written atomically
no LLM/model calls exist
no network calls exist
no Git push exists
Security Sandbox integration works
Policy / Capability integration works or fails closed
Initiator integration works or fails closed
completion record is generated
```

Validation command set:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_session.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_applier.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_rollback_manager.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_source_change_guard.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_implementation_validation_gate.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_sandbox_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_policy_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_limits.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_idempotency.py
git status --short
```

Expected final status:

```text
VALIDATED — DONE
```

---

# 35. Fresh-Clone Validation Evidence

The layer must be validated from a fresh checkout.

Required evidence:

```text
commit hash
Python version
compileall output
pytest output
git status before validation
git status after validation
completion record
```

The validation must prove:

```text
no unexpected source mutation
no ignored test-created state affects result
no local dirty tree hides failures
```

---

# 36. Completion Evidence Contract

Completion record path:

```text
.agentx-init/implementation/governed_patch_execution_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_GOVERNED_PATCH_EXECUTION",
  "component_name": "Governed Patch Execution Layer",
  "status": "VALIDATED",
  "validated_commit": "string",
  "validated_at": "string",
  "canonical_subdirectory": "tools/agentx_evolve/patch_execution/",
  "basis_documents": [
    "GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v5"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "agentx_integration_points_verified": [],
  "sandbox_integration_points_verified": [],
  "policy_integration_points_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

---

# 37. Runtime Evidence vs Implementation Evidence

## 35.1 Runtime Evidence

Runtime evidence is generated during normal operation and may include:

```text
session records
dry-run records
patch application records
rollback snapshots
rollback history
source inventories
validation gate records
temporary files
```

Default:

```text
runtime evidence is not automatically committed
```

## 35.2 Implementation Evidence

Implementation evidence proves the layer itself is complete.

Implementation evidence may be committed when reviewed:

```text
governed_patch_execution_completion_record.json
final validation command output summary
reviewed DoD report
```

## 35.3 Commit Rule

Do not commit bulk runtime artifacts unless they are explicitly selected as reviewed completion evidence.

If `.agentx-init/` is ignored, either:

```text
force-add only the reviewed completion record
```

or:

```text
copy the reviewed completion record into a tracked evidence directory
```

Canonical runtime location remains:

```text
.agentx-init/implementation/
```

---

# 38. Runtime Artifact Commit Policy

Runtime artifacts under `.agentx-init/implementation/` are generally runtime state.

Committable evidence:

```text
governed_patch_execution_completion_record.json
specific reviewed completion records
```

Usually not committed unless explicitly needed:

```text
temporary session records
rollback snapshots
dry-run scratch outputs
test-created runtime state
```

If `.agentx-init/` is ignored, force-add only reviewed completion evidence or copy it to a tracked evidence directory with the same content.

---

# 39. Implementation Drift Blockers

Reject the implementation if it:

```text
places files outside tools/agentx_evolve/patch_execution/ without recorded deviation
mutates source before rollback snapshot
allows L0 mutation
allows protected path mutation
allows outside-repo mutation
lets patch layer override sandbox BLOCK
adds LLM/model dependency
adds network dependency
adds Git push
executes shell-based file mutation
accepts failed validation silently
fails to write evidence
deletes evidence during rollback
allows binary mutation in v1
accepts partial apply as success
copies OpenCode source code
adds Bun/Node/OpenCode runtime dependency
```

---

# 40. Final Implementation Handoff Checklist

Before coding begins, confirm:

```text
[ ] Contract file is GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v5.
[ ] Canonical location is tools/agentx_evolve/patch_execution/.
[ ] Security Sandbox is VALIDATED — DONE.
[ ] Policy / Capability Registry exists or temporary fail-closed bridge will be used.
[ ] No LLM/model functionality belongs in this layer.
[ ] No MCP server belongs in this layer.
[ ] No Git push belongs in this layer.
[ ] Dry-run must be implemented before live patch application.
[ ] Rollback snapshot must be implemented before live patch application.
[ ] Source Change Guard must run before ACCEPTED.
[ ] Validation failure must rollback or fail explicitly.
[ ] Completion evidence must be generated after validation.
```

---

# 41. Residual Risks

```yaml
residual_risks:
  - id: "GPE-RISK-001"
    description: "Patch application can corrupt files if rollback is incomplete."
    severity: "critical"
    mitigation: "Snapshot before mutation; verify rollback hashes."
  - id: "GPE-RISK-002"
    description: "Source change guard may miss unexpected changes if based only on approved paths."
    severity: "high"
    mitigation: "Compare before/after git diff or filesystem hashes."
  - id: "GPE-RISK-003"
    description: "Validation failure could be misclassified as acceptable."
    severity: "high"
    mitigation: "Validation failure must trigger rollback or explicit failed state."
  - id: "GPE-RISK-004"
    description: "Delete/rename operations are higher risk."
    severity: "high"
    mitigation: "Block delete/rename in v1 unless explicitly approved by future policy."
  - id: "GPE-RISK-005"
    description: "OpenCode-style patch flexibility may be copied too broadly."
    severity: "high"
    mitigation: "Borrow patch concept only; enforce Agent_X governance, sandbox, rollback, and evidence."
```

---

# 42. Contract Freeze Rule

This v5 document is frozen as the controlling contract.

Allowed future edits:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional fields that do not weaken safety
MAJOR: changed safety boundaries, changed operation permissions, changed lifecycle, changed rollback/validation/evidence rules
```

Blocked without major revision:

```text
allowing L0 mutation
allowing sandbox block override
removing rollback requirement
removing validation requirement
allowing Git push
allowing LLM/model execution
allowing network patch fetch
allowing partial apply acceptance
allowing binary mutation by default
```

---

# 43. Final Freeze Direction

This v5 contract is now frozen as the controlling Governed Patch Execution contract.

The next artifact must be:

```text
GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC
```

Do not keep broadening this contract unless a true safety boundary is missing.

Allowed future changes:

```text
PATCH: wording, typo fixes, formatting
MINOR: additive optional fields that do not weaken safety
MAJOR: lifecycle, operation permissions, rollback, validation, evidence, sandbox, or policy boundary changes
```

---

# 44. Final Rating

Final v5 contract rating:

```text
10/10
```

Reason:

```text
This contract includes EQC, FIC, SIB, patch schemas, dry-run schema, rollback schemas, implementation session schema, source inventory, source change guard, validation gate, policy matrix, audit/evidence rules, OpenCode borrowing notes, Agent_X integration notes, Security Sandbox integration notes, locking rules, authority precedence, patch limits, binary-file rules, encoding rules, idempotency, partial-failure handling, schema strictness, temporary policy bridge, minimal implementation slices, acceptance tests, Go/No-Go rules, Definition of Done, and freeze rule.
```

Next document:

```text
GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC
```
