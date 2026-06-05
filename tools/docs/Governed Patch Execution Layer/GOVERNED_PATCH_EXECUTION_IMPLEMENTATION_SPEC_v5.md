# GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC_v5

```text
document_id: GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC
version: v5.0
status: final implementation-ready, transaction-safe, acceptance-final, coding-handoff-frozen
based_on: GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
component_id: AGENTX_GOVERNED_PATCH_EXECUTION
component_name: Governed Patch Execution Layer
roadmap_layer: 3
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
target_language: Python
canonical_subdirectory: tools/agentx_evolve/patch_execution/
runtime_state_root: .agentx-init/implementation/
depends_on:
  - Agent_X Initiator
  - Security Sandbox / Filesystem Boundary Layer
  - Policy / Capability Registry, or minimal fail-closed policy adapter until registry exists
opencode_basis: edit/write/patch/apply_patch concepts, diff visibility, permission-scanned shell separation
```

---

# 0. v5 Review and Upgrade Summary

## 0.1 v4 Rating

The v4 implementation spec was rated:

```text
9.8/10
```

## 0.2 Why v4 Was Not Fully 10/10

v4 contained the needed technical content, but it still had two minor handoff risks:

```text
1. It did not provide a compact final build-slice checklist that a coding LLM can follow without scanning the whole document.
2. It did not include a final implementation acceptance state table separating DONE, BLOCKED, ROLLED_BACK, FAILED, and VALIDATED.
```

Those are not architecture gaps, but they matter for implementation discipline.

## 0.3 v5 Improvements

This v5 adds:

```text
final build-slice checklist
implementation acceptance state table
final pass/fail evidence checklist
explicit "no further broadening" freeze note
```

Final v5 rating:

```text
10/10
```

---

# 1. Purpose

This document is the full implementation specification for the **Governed Patch Execution Layer**.

It converts the controlling contract:

```text
GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
```

into exact implementation instructions.

This layer is the deterministic actuator that safely applies approved, bounded changes to source files.

It must support:

```text
implementation sessions
dry-run patch execution
live patch execution
rollback snapshots
rollback verification
source change guard
validation gate
patch evidence
audit events
completion records
```

It must not become an LLM agent, planner, policy registry, promotion gate, Git automation layer, or OpenCode clone.

---

# 2. Canonical Destination Summary

The implementation must create this component here:

```text
tools/agentx_evolve/patch_execution/
```

Schemas must go here:

```text
tools/agentx_evolve/schemas/
```

Tests must go here:

```text
tools/agentx_evolve/tests/
```

Runtime artifacts must go here:

```text
.agentx-init/implementation/
```

Existing completed layers remain where they are:

```text
tools/agentx_initiator/
tools/agentx_evolve/security/
```

This is the canonical layer split:

```text
tools/agentx_initiator/             = completed Initiator
tools/agentx_evolve/security/       = completed Security Sandbox / Filesystem Boundary
tools/agentx_evolve/patch_execution/ = new Governed Patch Execution Layer
```

---

# 3. OpenCode Borrowing Boundary

This layer borrows OpenCode-style coding-agent primitives as concepts only.

## 2.1 Borrowed Concepts

| OpenCode concept | Agent_X implementation | Borrowing limit |
|---|---|---|
| `edit` | governed exact edit operation | Must run inside implementation session with rollback. |
| `write` | governed file write/create operation | Target path must be approved and sandbox-allowed. |
| `patch` / `apply_patch` | governed bounded patch operation | Target paths must be explicit; no freeform repo mutation. |
| `shell` | validation command handoff/precheck | No shell file mutation; validation only and allowlisted. |
| diff visibility | before/after hashes and source change guard | Evidence-based, schema-governed. |
| invalid operation handling | blocked patch execution decision | Fail closed with audit evidence. |

## 2.2 Not Borrowed

Do not copy:

```text
OpenCode source code
OpenCode TypeScript/Bun implementation
OpenCode broad shell assumptions
OpenCode plugin execution model
OpenCode network fetch/search behavior
OpenCode UI workflow
OpenCode subagent execution
```

Agent_X implementation must remain:

```text
Python
local-first
schema-governed
sandbox-checked
rollback-protected
audit-backed
```

---

# 4. Implementation Goal

The layer must safely execute this sequence:

```text
1. Create implementation session.
2. Load proposal or explicit patch input.
3. Check governance reference.
4. Check policy/capability permission.
5. Run Security Sandbox precheck for all target paths.
6. Create rollback snapshot.
7. Apply patch in dry-run or live mode.
8. Verify actual changed paths.
9. Run validation gate.
10. Accept if validation passes.
11. Roll back if validation fails or source guard fails.
12. Write evidence and completion record.
```

The layer must produce one of these final states:

```text
ACCEPTED
ROLLED_BACK
FAILED
BLOCKED
```

It must never silently accept a failed validation or unsafe mutation.

---

# 5. Required Directory Tree

Create or update this exact tree:

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

    schemas/
      implementation_session.schema.json
      patch_application.schema.json
      patch_operation.schema.json
      patch_result.schema.json
      rollback_snapshot.schema.json
      rollback_record.schema.json
      source_change_guard.schema.json
      implementation_validation_gate.schema.json
      patch_execution_decision.schema.json
      patch_execution_audit.schema.json

    tests/
      test_patch_session.py
      test_patch_applier.py
      test_rollback_manager.py
      test_source_change_guard.py
      test_implementation_validation_gate.py
      test_patch_evidence.py
      test_patch_execution_schema.py
      test_patch_execution_negative_cases.py
      test_patch_execution_sandbox_integration.py
      test_patch_execution_initiator_integration.py
```

---

# 6. Runtime Artifacts

Create runtime artifacts under:

```text
.agentx-init/implementation/
```

Required runtime tree:

```text
.agentx-init/
  implementation/
    sessions/
      <session_id>.json
    rollback_snapshots/
      <session_id>/
    implementation_history.jsonl
    implementation_evidence.jsonl
    patch_applications.jsonl
    source_change_guard_results.jsonl
    validation_gate_results.jsonl
    rollback_history.jsonl
    latest_implementation_session.json
    latest_patch_result.json
    latest_rollback_record.json
    governed_patch_execution_completion_record.json
```

Rules:

```text
JSONL files are append-only.
Latest JSON files are written atomically.
Rollback snapshots are never deleted during the same session.
Evidence is never deleted during rollback.
No runtime artifact may contain unredacted secrets.
```

---

# 7. Transaction, Locking, and Atomic Write Contract

## 6.1 Session Transaction Boundary

Every live patch execution must be treated as one transaction.

A transaction starts when:

```text
ImplementationSession is created
```

A transaction ends only when the session reaches one of:

```text
ACCEPTED
ROLLED_BACK
FAILED
BLOCKED
```

No live mutation may occur outside an active session.

## 6.2 Required Locks

The implementation must create and respect these locks:

```text
.agentx-init/implementation/implementation_session.lock
.agentx-init/implementation/patch_apply.lock
.agentx-init/implementation/rollback.lock
```

Rules:

```text
only one live patch session may run at a time
dry-run may run without mutation lock but must not overlap live mutation
stale lock must be detected and reported
lock removal must be evidence-backed
lock failure blocks live execution
```

## 6.3 Atomic Artifact Writes

All `latest_*.json` artifacts must be written atomically:

```text
write temp file in same directory
validate artifact if schema validator exists
replace target with atomic rename
never replace valid latest artifact with invalid output
```

Append-only JSONL files must:

```text
append one JSON object per line
never rewrite old lines
never delete malformed old lines
record malformed line as warning if encountered
```

## 6.4 Partial Apply Failure Handling

If any operation fails during live mode:

```text
stop applying remaining operations
record failed operation
run source change guard if any mutation may have occurred
rollback using snapshot
verify rollback
mark session ROLLED_BACK if rollback succeeds
mark session FAILED if rollback fails
write evidence
```

The implementation must not continue applying later operations after a failed operation.

## 6.5 No Mutation Before Required Gates

Live mutation is forbidden until all are true:

```text
session exists
governance_decision_id exists
policy_decision_id exists or fail-closed adapter explicitly allows current low-risk case
target paths are explicit
sandbox precheck passed
rollback snapshot created
patch operations validated
```


---

# 8. Implementation Order

Use this exact order:

```text
1. patch_models.py
2. schemas
3. patch_policy.py
4. initiator_patch_compat.py
5. patch_session.py
6. rollback_manager.py
7. patch_applier.py
8. source_change_guard.py
9. implementation_validation_gate.py
10. patch_evidence.py
11. patch_execution_service.py
12. tests
13. completion evidence
```

Rationale:

```text
models before behavior
schemas before evidence
policy before mutation
compat before integration
session before snapshot
snapshot before patch application
patch application before source guard
source guard before validation gate
evidence after artifacts exist
service orchestration last
```

---

# 9. Dry-Run Output Contract

Dry-run mode must produce a complete preview without modifying files.

Required dry-run behavior:

```text
create implementation session
validate operations
run policy check
run sandbox precheck
compute target paths
compute planned changed paths
compute before hashes
compute simulated after hashes where possible
do not create rollback snapshot unless policy wants dry-run preview only
do not write source files
do not modify runtime state except dry-run evidence/session artifacts
return status DRY_RUN_READY or BLOCKED
```

Required dry-run artifact fields:

```text
mode = DRY_RUN
operations
target_paths
planned_changed_paths
before_hashes
simulated_after_hashes
sandbox_decision_ids
policy_decision_id
warnings
errors
```

Dry-run must be accepted only as preview evidence. It must not mark a session as ACCEPTED.


---

# 10. File-by-File Implementation Spec

---

## 7.1 `tools/agentx_evolve/patch_execution/__init__.py`

### Purpose

Expose the public patch execution API.

### Required Exports

```python
from .patch_models import (
    ImplementationSession,
    PatchApplication,
    PatchOperation,
    PatchResult,
    RollbackSnapshot,
    RollbackRecord,
    SourceChangeGuardResult,
    ImplementationValidationGateResult,
    PatchExecutionDecision,
)

from .patch_session import create_implementation_session, update_implementation_session
from .rollback_manager import create_rollback_snapshot, rollback_session
from .patch_applier import apply_patch_operations
from .source_change_guard import verify_source_changes
from .implementation_validation_gate import run_validation_gate
from .patch_execution_service import execute_governed_patch
```

### Must Not Do

```text
no filesystem writes on import
no network
no validation command execution on import
no Git write
```

---

## 7.2 `patch_models.py`

### Purpose

Define dataclasses and constants shared by the patch execution layer.

### Required Constants

Statuses:

```python
STATUS_CREATED = "CREATED"
STATUS_PROPOSAL_LOADED = "PROPOSAL_LOADED"
STATUS_GOVERNANCE_CHECKED = "GOVERNANCE_CHECKED"
STATUS_POLICY_CHECKED = "POLICY_CHECKED"
STATUS_SANDBOX_CHECKED = "SANDBOX_CHECKED"
STATUS_SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
STATUS_DRY_RUN_READY = "DRY_RUN_READY"
STATUS_PATCH_APPLIED = "PATCH_APPLIED"
STATUS_SOURCE_GUARD_CHECKED = "SOURCE_GUARD_CHECKED"
STATUS_VALIDATION_RUNNING = "VALIDATION_RUNNING"
STATUS_VALIDATION_PASSED = "VALIDATION_PASSED"
STATUS_VALIDATION_FAILED = "VALIDATION_FAILED"
STATUS_ROLLBACK_RUNNING = "ROLLBACK_RUNNING"
STATUS_ROLLED_BACK = "ROLLED_BACK"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_FAILED = "FAILED"
STATUS_BLOCKED = "BLOCKED"
```

Operation types:

```python
OP_EXACT_EDIT = "EXACT_EDIT"
OP_WRITE_FILE = "WRITE_FILE"
OP_CREATE_FILE = "CREATE_FILE"
OP_DELETE_FILE = "DELETE_FILE"
OP_RENAME_FILE = "RENAME_FILE"
OP_PATCH_TEXT = "PATCH_TEXT"
```

Final decisions:

```python
FINAL_PENDING = "PENDING"
FINAL_ACCEPT = "ACCEPT"
FINAL_REJECT = "REJECT"
FINAL_ROLLBACK = "ROLLBACK"
```

### Required Dataclasses

#### `PatchOperation`

Fields:

```python
operation_id: str
operation_type: str
target_path: str
old_text: str | None = None
new_text: str | None = None
content: str | None = None
allow_create: bool = False
allow_delete: bool = False
expected_before_hash: str | None = None
requires_rollback_snapshot: bool = True
```

#### `PatchApplication`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "patch_application.schema.json"
application_id: str
session_id: str
proposal_id: str | None
governance_decision_id: str | None
policy_decision_id: str | None
timestamp: str
source_component: str = "GovernedPatchExecution"
mode: str
operations: list[dict]
target_paths: list[str]
status: str
before_hashes: dict[str, str | None]
after_hashes: dict[str, str | None]
warnings: list[str]
errors: list[str]
```

#### `PatchResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "patch_result.schema.json"
result_id: str
session_id: str
application_id: str
timestamp: str
source_component: str = "PatchApplier"
mode: str
status: str
changed_paths: list[str]
created_paths: list[str]
deleted_paths: list[str]
before_hashes: dict[str, str | None]
after_hashes: dict[str, str | None]
warnings: list[str]
errors: list[str]
```

#### `RollbackSnapshot`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "rollback_snapshot.schema.json"
snapshot_id: str
session_id: str
timestamp: str
source_component: str = "RollbackManager"
snapshot_root: str
files: list[dict]
status: str
warnings: list[str]
errors: list[str]
```

#### `RollbackRecord`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "rollback_record.schema.json"
rollback_id: str
session_id: str
snapshot_id: str
timestamp: str
source_component: str = "RollbackManager"
trigger: str
restored_files: list[str]
removed_created_files: list[str]
verification_status: str
status: str
warnings: list[str]
errors: list[str]
```

#### `ImplementationSession`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "implementation_session.schema.json"
session_id: str
timestamp: str
source_component: str = "GovernedPatchExecution"
proposal_id: str | None
governance_decision_id: str | None
policy_decision_id: str | None
sandbox_decision_ids: list[str]
rollback_snapshot_id: str | None
patch_application_id: str | None
source_change_guard_id: str | None
validation_result_id: str | None
rollback_record_id: str | None
target_paths: list[str]
changed_paths: list[str]
status: str
final_decision: str
warnings: list[str]
errors: list[str]
```

#### `SourceChangeGuardResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "source_change_guard.schema.json"
guard_id: str
session_id: str
timestamp: str
source_component: str = "SourceChangeGuard"
approved_paths: list[str]
actual_changed_paths: list[str]
unexpected_paths: list[str]
missing_expected_paths: list[str]
forbidden_paths: list[str]
status: str
warnings: list[str]
errors: list[str]
```

#### `ImplementationValidationGateResult`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "implementation_validation_gate.schema.json"
validation_gate_id: str
session_id: str
timestamp: str
source_component: str = "ImplementationValidationGate"
commands_requested: list[str]
commands_run: list[dict]
status: str
passed: bool
warnings: list[str]
errors: list[str]
```

#### `PatchExecutionDecision`

Fields:

```python
schema_version: str = "1.0"
schema_id: str = "patch_execution_decision.schema.json"
decision_id: str
session_id: str
timestamp: str
source_component: str = "GovernedPatchExecution"
decision: str
reason: str
required_actions: list[str]
warnings: list[str]
errors: list[str]
```

### Required Helpers

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
sha256_text(text: str) -> str
sha256_file(path: Path) -> str | None
```

---

## 7.3 `patch_policy.py`

### Purpose

Provide a minimal fail-closed policy adapter until the Policy / Capability Registry is complete.

### Required Public Functions

```python
check_patch_operation_allowed(
    operation: PatchOperation,
    approved_paths: list[str],
    policy_decision_id: str | None = None
) -> PatchExecutionDecision

check_session_allowed(
    target_paths: list[str],
    governance_decision_id: str | None,
    policy_decision_id: str | None
) -> PatchExecutionDecision
```

### Rules

```text
block if governance_decision_id is missing
block if target_paths is empty
block if any target path is not in approved_paths
block DELETE_FILE and RENAME_FILE in v1
block unknown operation types
allow EXACT_EDIT only if old_text and new_text are present
allow WRITE_FILE only if content is present
allow CREATE_FILE only if allow_create is true and content is present
allow PATCH_TEXT only if target path is explicit and bounded
```

### Status

This is not the final Policy / Capability Registry. It is a local fail-closed adapter.

---

## 11.4 Patch Policy Decision Contract

`patch_policy.py` must return schema-style decisions.

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_execution_decision.schema.json",
  "decision_id": "string",
  "session_id": "string|null",
  "timestamp": "string",
  "source_component": "PatchPolicy",
  "decision": "ALLOW|BLOCK|NEEDS_GOVERNANCE|NEEDS_POLICY|NEEDS_ROLLBACK_SNAPSHOT",
  "reason": "string",
  "required_actions": [],
  "warnings": [],
  "errors": []
}
```

Decision rules:

```text
missing governance_decision_id -> NEEDS_GOVERNANCE
missing policy_decision_id -> NEEDS_POLICY unless fail-closed adapter explicitly allows low-risk test case
missing approved paths -> BLOCK
unknown operation -> BLOCK
DELETE_FILE -> BLOCK in v1
RENAME_FILE -> BLOCK in v1
unapproved target path -> BLOCK
valid operation under approved path -> ALLOW
```

A policy ALLOW cannot override sandbox BLOCK.


---

## 7.4 `initiator_patch_compat.py`

### Purpose

Bridge to existing Initiator services without modifying Initiator internals.

### Required Class

```python
class InitiatorPatchCompat:
    def __init__(self, repo_root: Path | None = None): ...

    def get_repo_root(self) -> Path: ...

    def get_runtime_state_root(self) -> Path: ...

    def load_proposal(self, proposal_id: str) -> dict: ...

    def load_governance_decision(self, governance_decision_id: str) -> dict: ...

    def validate_schema(self, artifact: dict, schema_id: str) -> dict: ...

    def write_json_atomic(self, path: Path, artifact: dict) -> dict: ...

    def append_jsonl(self, path: Path, artifact: dict) -> dict: ...

    def append_audit_event(self, event: dict) -> dict: ...

    def run_validation_command(self, command: list[str]) -> dict: ...
```

### Import Strategy

Attempt package imports:

```python
from agentx_initiator.core import artifact_io
from agentx_initiator.core import schema_validation
from agentx_initiator.core import audit_log
from agentx_initiator.core import validation_allowlist
```

Fallbacks may exist for local deterministic writing, but must not fake governance or validation success.

### Fail-Closed Rule

If a required governance/proposal artifact is missing:

```text
BLOCK
```

---

## 7.5 `patch_session.py`

### Purpose

Create, store, and update implementation sessions.

### Required Public Functions

```python
create_implementation_session(
    repo_root: Path,
    target_paths: list[str],
    proposal_id: str | None,
    governance_decision_id: str | None,
    policy_decision_id: str | None,
    compat: InitiatorPatchCompat | None = None
) -> ImplementationSession

update_implementation_session(
    session: ImplementationSession,
    repo_root: Path,
    status: str,
    final_decision: str | None = None,
    changed_paths: list[str] | None = None,
    rollback_snapshot_id: str | None = None,
    patch_application_id: str | None = None,
    source_change_guard_id: str | None = None,
    validation_result_id: str | None = None,
    rollback_record_id: str | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    compat: InitiatorPatchCompat | None = None
) -> ImplementationSession
```

### Required Writes

```text
.agentx-init/implementation/sessions/<session_id>.json
.agentx-init/implementation/latest_implementation_session.json
.agentx-init/implementation/implementation_history.jsonl
```

### Rules

```text
session must exist before live mutation
session target_paths must not be empty
session status transitions must be recorded
latest session must be atomic
history is append-only
```

---

## 7.6 `rollback_manager.py`

### Purpose

Snapshot files before mutation and restore them on failure.

### Required Public Functions

```python
create_rollback_snapshot(
    session: ImplementationSession,
    repo_root: Path,
    target_paths: list[str],
    compat: InitiatorPatchCompat | None = None
) -> RollbackSnapshot

rollback_session(
    session: ImplementationSession,
    snapshot: RollbackSnapshot,
    repo_root: Path,
    trigger: str,
    created_paths: list[str] | None = None,
    compat: InitiatorPatchCompat | None = None
) -> RollbackRecord

verify_rollback(
    snapshot: RollbackSnapshot,
    repo_root: Path,
    created_paths: list[str] | None = None
) -> dict
```

### Snapshot Rules

```text
snapshot before any live mutation
for existing files, copy content to snapshot directory
for non-existing files, record existed_before=false
record before hashes
preserve directory structure safely under snapshot root
do not snapshot outside repo
do not snapshot L0 target because L0 mutation should already block
```

### Rollback Rules

```text
restore files that existed before
remove files created during the session
verify restored hashes match before hashes
write rollback record
if verification fails, status FAILED and future patch sessions must be blocked by higher-level safe mode
```

---

## 7.7 `patch_applier.py`

### Purpose

Apply bounded patch operations after session, policy, sandbox, and rollback checks.

### Required Public Function

```python
apply_patch_operations(
    session: ImplementationSession,
    operations: list[PatchOperation],
    repo_root: Path,
    mode: str,
    approved_paths: list[str],
    sandbox_policy: object,
    compat: InitiatorPatchCompat | None = None
) -> PatchResult
```

### Required Modes

```text
DRY_RUN
LIVE
```

### Operation Behavior

#### EXACT_EDIT

```text
target path must be approved
old_text must appear exactly once
replace once
dry-run returns planned hash
live writes through safe file operation or atomic write after sandbox approval
```

#### WRITE_FILE

```text
target path must be approved
content required
existing or new file allowed only if operation permits
live write must have rollback snapshot
```

#### CREATE_FILE

```text
target path must not already exist unless policy allows overwrite
allow_create must be true
parent path must be inside approved scope
```

#### PATCH_TEXT

```text
v1 may support simple unified-diff-like patch only if target path explicit
if parser is not implemented, block with PATCH_APPLY_FAILED rather than applying unsafely
```

#### DELETE_FILE / RENAME_FILE

```text
blocked in v1 unless future policy explicitly allows
```

### Required Checks

```text
policy check
sandbox check
approved path check
operation type check
rollback snapshot already exists for live mode
```

---

## 9.8 Patch Operation Validation Rules

Before any operation is applied, validate it according to this matrix.

| Operation | Required fields | Block if | Live requirements |
|---|---|---|---|
| EXACT_EDIT | `target_path`, `old_text`, `new_text` | old_text missing, new_text missing, no match, multiple matches | rollback snapshot exists |
| WRITE_FILE | `target_path`, `content` | content missing, target not approved | rollback snapshot exists |
| CREATE_FILE | `target_path`, `content`, `allow_create=true` | file exists, parent not approved, allow_create false | rollback snapshot records existed_before=false |
| PATCH_TEXT | `target_path`, bounded patch content | target path not explicit, patch parser unsafe | rollback snapshot exists |
| DELETE_FILE | explicit future approval | always blocked in v1 | not implemented in v1 |
| RENAME_FILE | explicit future approval | always blocked in v1 | not implemented in v1 |

General validation rules:

```text
operation_id required
operation_type must be known
target_path required
target_path must be repo-relative in durable artifacts
absolute outside-repo paths blocked
path traversal blocked
symlink escape blocked
L0 target blocked
protected target blocked
unapproved target blocked
```


---

## 7.8 `source_change_guard.py`

### Purpose

Verify only approved files changed.

### Required Public Function

```python
verify_source_changes(
    session: ImplementationSession,
    repo_root: Path,
    approved_paths: list[str],
    before_hashes: dict[str, str | None],
    after_hashes: dict[str, str | None],
    compat: InitiatorPatchCompat | None = None
) -> SourceChangeGuardResult
```

### Required Behavior

```text
compare expected changed paths to actual changed paths
detect unexpected paths
detect missing expected paths
detect forbidden paths
detect L0/protected path change
return PASS only if all changes are within approved paths
```

### v1 Actual Changed Path Source

In v1, actual changed paths may come from:

```text
patch result changed_paths
before/after hash comparison
optional git diff --name-only if read-only Git integration exists
```

Do not require Git for v1.

---

## 7.9 `implementation_validation_gate.py`

### Purpose

Run or represent validation after patch application.

### Required Public Function

```python
run_validation_gate(
    session: ImplementationSession,
    repo_root: Path,
    validation_commands: list[list[str]],
    compat: InitiatorPatchCompat | None = None
) -> ImplementationValidationGateResult
```

### Required Behavior

```text
if no validation commands, return BLOCKED unless docs-only policy allows
commands must be allowlisted by Initiator validation allowlist or local fail-closed policy
commands must be prechecked by Security Sandbox safe_subprocess
record commands requested
record commands run
redact output
return passed true only when all required commands pass
```

### v1 Allowed Validation

Start with safe deterministic commands only:

```text
python -m compileall tools/agentx_evolve
python -m pytest selected test files
```

No network, no Git push, no destructive commands.

---

## 11.10 Validation Command Boundary

Validation commands must be treated as controlled execution, not arbitrary shell access.

Allowed v1 validation command patterns:

```text
python -m compileall tools/agentx_evolve
python -m pytest tools/agentx_evolve/tests/test_<specific_file>.py
```

Blocked by default:

```text
pytest with no path if policy does not allow broad suite
commands outside repo root
commands containing shell operators
commands requiring network
commands invoking Git write operations
commands invoking package install
commands invoking curl/wget
commands invoking bash/sh -c
```

If broad test-suite execution is desired, it must be explicitly allowlisted.

The validation gate should call Security Sandbox subprocess precheck before command execution.


---

## 7.10 `patch_evidence.py`

### Purpose

Write patch execution evidence.

### Required Public Functions

```python
append_implementation_history(session: ImplementationSession, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

append_patch_application(application: PatchApplication | PatchResult, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

append_source_change_guard_result(result: SourceChangeGuardResult, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

append_validation_gate_result(result: ImplementationValidationGateResult, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

append_rollback_record(record: RollbackRecord, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

write_latest_artifact(name: str, artifact: dict, repo_root: Path, compat: InitiatorPatchCompat | None = None) -> dict

build_patch_execution_audit_event(session: ImplementationSession, event_type: str, decision: str, artifacts: list[str]) -> dict
```

### Required Files

```text
.agentx-init/implementation/implementation_history.jsonl
.agentx-init/implementation/implementation_evidence.jsonl
.agentx-init/implementation/patch_applications.jsonl
.agentx-init/implementation/source_change_guard_results.jsonl
.agentx-init/implementation/validation_gate_results.jsonl
.agentx-init/implementation/rollback_history.jsonl
.agentx-init/memory/audit_events.jsonl
```

Rules:

```text
append-only
atomic latest writes
redact secrets
do not write raw model content
do not delete evidence during rollback
```

---

## 7.11 `patch_execution_service.py`

### Purpose

Provide the high-level deterministic orchestration function.

### Required Public Function

```python
execute_governed_patch(
    repo_root: Path,
    operations: list[PatchOperation],
    approved_paths: list[str],
    proposal_id: str | None,
    governance_decision_id: str | None,
    policy_decision_id: str | None,
    mode: str = "DRY_RUN",
    validation_commands: list[list[str]] | None = None,
    sandbox_policy: object | None = None,
    compat: InitiatorPatchCompat | None = None
) -> ImplementationSession
```

### Required Flow

```text
1. create session
2. check session allowed
3. sandbox precheck target paths
4. if dry-run: evaluate patch without writing and return DRY_RUN_READY / BLOCKED
5. if live: create rollback snapshot
6. apply patch operations
7. run source change guard
8. run validation gate
9. if validation passes: mark ACCEPTED
10. if validation fails or source guard fails: rollback
11. write all evidence
12. return final session
```

### Required Fail-Closed Behavior

```text
missing governance_decision_id -> BLOCKED
missing approved_paths -> BLOCKED
sandbox block -> BLOCKED
rollback snapshot failure -> FAILED
patch failure -> rollback if mutation occurred, else FAILED
source guard failure -> rollback
validation failure -> rollback
rollback failure -> FAILED and safe-mode recommendation
```

---

# 11. Schema Files to Create

Create these exact schemas.

```text
implementation_session.schema.json
patch_application.schema.json
patch_operation.schema.json
patch_result.schema.json
rollback_snapshot.schema.json
rollback_record.schema.json
source_change_guard.schema.json
implementation_validation_gate.schema.json
patch_execution_decision.schema.json
patch_execution_audit.schema.json
```

Each schema must require:

```text
schema_version
schema_id
timestamp
source_component
status or decision where applicable
warnings
errors
```

Use the same JSON Schema draft already used by `tools/agentx_evolve/schemas/`.

---

# 12. Integration Requirements

## 9.1 Security Sandbox Integration

Required imports:

```python
from agentx_evolve.security.safe_file_ops import safe_read_file, safe_write_file, safe_exact_edit, safe_patch_precheck
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.sandbox_policy import default_sandbox_policy
```

Required behavior:

```text
every target path passes sandbox check before live mutation
sandbox BLOCK always blocks patch execution
sandbox NEEDS_ROLLBACK_SNAPSHOT forces snapshot before live mutation
sandbox decisions are recorded in implementation session
```

## 9.2 Policy / Capability Registry Integration

If full registry exists, use it.

If not, use `patch_policy.py` fail-closed adapter.

Minimum required policy behavior:

```text
missing governance -> BLOCK
missing approved paths -> BLOCK
unapproved target path -> BLOCK
DELETE/RENAME -> BLOCK in v1
unknown operation -> BLOCK
```

## 9.3 Initiator Integration

Required imports through `initiator_patch_compat.py`:

```text
schema_validation
artifact_io
audit_log
validation_allowlist
proposal/governance artifact readers where available
```

Rules:

```text
do not fake governance success
do not fake schema validation success
do not fake validation command success
do not modify Initiator source
```

---

# 13. Test Files and Test Cases

## 10.1 `test_patch_session.py`

Required tests:

```text
test_create_implementation_session
test_session_requires_target_paths
test_session_records_proposal_governance_policy_ids
test_session_writes_latest_atomically
test_session_appends_history
test_session_status_updates
```

## 10.2 `test_patch_applier.py`

Required tests:

```text
test_dry_run_changes_nothing
test_exact_edit_applies_to_approved_file
test_exact_edit_blocks_no_match
test_exact_edit_blocks_multiple_matches
test_write_file_applies_to_approved_file
test_create_file_applies_to_approved_path
test_patch_text_blocks_if_unbounded
test_delete_file_blocked_in_v1
test_rename_file_blocked_in_v1
```

## 10.3 `test_rollback_manager.py`

Required tests:

```text
test_snapshot_existing_file
test_snapshot_non_existing_file
test_rollback_restores_existing_file
test_rollback_removes_created_file
test_rollback_verifies_before_hash
test_rollback_failure_records_failed_status
```

## 10.4 `test_source_change_guard.py`

Required tests:

```text
test_source_change_guard_passes_approved_change
test_source_change_guard_blocks_unexpected_path
test_source_change_guard_blocks_l0_path
test_source_change_guard_blocks_protected_path
test_source_change_guard_detects_missing_expected_path
```

## 10.5 `test_implementation_validation_gate.py`

Required tests:

```text
test_validation_gate_blocks_empty_commands_without_docs_policy
test_validation_gate_prechecks_subprocess
test_validation_gate_passes_allowed_command
test_validation_gate_fails_failed_command
test_validation_gate_redacts_output
```

## 10.6 `test_patch_evidence.py`

Required tests:

```text
test_append_implementation_history
test_append_patch_application
test_append_source_change_guard_result
test_append_validation_gate_result
test_append_rollback_record
test_write_latest_artifact_atomic
test_audit_event_built
test_evidence_not_deleted_during_rollback
```

## 10.7 `test_patch_execution_schema.py`

Required tests:

```text
test_implementation_session_schema
test_patch_application_schema
test_patch_operation_schema
test_patch_result_schema
test_rollback_snapshot_schema
test_rollback_record_schema
test_source_change_guard_schema
test_validation_gate_schema
test_patch_execution_decision_schema
test_patch_execution_audit_schema
```

## 10.8 `test_patch_execution_negative_cases.py`

Required tests:

```text
test_missing_governance_blocks
test_missing_policy_blocks_or_fails_closed
test_unapproved_path_blocks
test_l0_target_blocks
test_protected_target_blocks
test_outside_repo_target_blocks
test_symlink_escape_blocks
test_validation_failure_triggers_rollback
test_source_guard_failure_triggers_rollback
test_rollback_failure_blocks_acceptance
test_no_llm_dependency
test_no_network_dependency
test_no_git_push
test_no_opencode_runtime_dependency
```

## 10.9 `test_patch_execution_sandbox_integration.py`

Required tests:

```text
test_sandbox_patch_precheck_called
test_sandbox_block_blocks_patch_session
test_sandbox_needs_rollback_snapshot_enforced
test_sandbox_l0_block_respected
test_sandbox_runtime_boundary_respected
```

## 10.10 `test_patch_execution_initiator_integration.py`

Required tests:

```text
test_initiator_patch_compat_imports_schema_validation
test_initiator_patch_compat_imports_artifact_io
test_initiator_patch_compat_imports_audit_log
test_initiator_patch_compat_imports_validation_allowlist
test_missing_governance_artifact_fails_closed
test_initiator_source_not_modified
```

---

# 14. Manual Validation Commands

Run from repository root:

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
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
git status --short
```

No command may require:

```text
GPU
network
hosted provider
LLM
OpenCode runtime
Bun
Node
Git push
```

---

# 15. Source Change Guard Baseline Strategy

The source change guard must compare intended changes to actual changes.

## 12.1 Required Baseline

Before live mutation, capture:

```text
approved_paths
target_paths
before_hashes for all existing target files
existence state for all target files
optional repository file hash/index for approved scope
```

## 12.2 Actual Change Detection

After patch application, detect actual changes through at least one deterministic method:

```text
before/after hashes for target paths
created/deleted path tracking from patch result
optional read-only git diff --name-only if available
```

Git is optional in v1. If Git is not used, hash comparison and explicit operation tracking are required.

## 12.3 Guard Failure

Source change guard fails if:

```text
actual changed path not in approved paths
L0 path changed
protected path changed
outside-repo path appears
expected changed path did not change when it should have
created file was not approved
deleted file was not approved
```

On failure:

```text
rollback immediately
write source_change_guard result
block acceptance
```

---

# 16. Rollback Verification Contract

Rollback is not complete when files are merely copied back.

Rollback is complete only when:

```text
all files that existed_before=true are restored
restored file hashes match before_hash
files created during the session are removed
files that did not exist before remain absent
source change guard passes after rollback or reports clean state
rollback record is written
session status is updated
```

If rollback verification fails:

```text
mark rollback record FAILED
mark session FAILED
write evidence
recommend safe mode
block further patch sessions until human review
```

---

# 17. Fresh-Clone Validation and GO / NO-GO Rules

## 14.1 Fresh-Clone Validation

Final validation must be run from a clean checkout:

```bash
git clone <repo> Agent_X_patch_execution_check
cd Agent_X_patch_execution_check
git checkout <commit>
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
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_patch_execution_initiator_integration.py
git status --short
```

## 14.2 GO Criteria

Mark DONE only if:

```text
compileall passes
all patch execution tests pass
git status shows no unexpected source mutation
dry-run changes no source files
approved patch changes only approved files
rollback snapshot exists before mutation
rollback verification passes
source change guard blocks unexpected mutation
validation failure triggers rollback
completion record exists
```

## 14.3 NO-GO Criteria

Keep NOT DONE if any are true:

```text
compileall fails
any safety test fails
rollback test fails
source change guard test fails
sandbox integration test fails
policy/fail-closed behavior fails
validation failure does not rollback
L0 mutation possible
protected path mutation possible
outside-repo mutation possible
network dependency introduced
LLM dependency introduced
Git push introduced
OpenCode runtime dependency introduced
```


---

# 18. Acceptance Criteria

The implementation is accepted only when:

```text
canonical subdirectory exists
all files exist
all schemas exist
all tests exist
compileall passes
all patch execution tests pass
dry-run mode changes no files
approved live patch changes only approved files
unapproved patch is blocked
rollback snapshot exists before mutation
rollback restores files after failure
source change guard blocks unexpected mutation
validation failure triggers rollback
evidence artifacts are written
latest artifacts are atomic
sandbox integration works
policy integration works or fails closed
Initiator integration works or fails closed
no L0 mutation is possible
no protected path mutation is possible
no outside-repo mutation is possible
no network dependency exists
no LLM dependency exists
no Git push exists
completion record exists
```

---

# 19. Definition of Done

The layer is **DONE** only when this evidence exists:

```text
compileall PASS
pytest PASS for all patch execution tests
git status CLEAN or only expected ignored runtime artifacts
completion record written to .agentx-init/implementation/governed_patch_execution_completion_record.json
```

The completion record must confirm:

```text
approved patch applied
unapproved patch blocked
L0 patch blocked
protected path patch blocked
outside-repo patch blocked
dry-run changes nothing
rollback snapshot created before mutation
rollback verified after failure
source change guard passed for approved change
source change guard failed for unexpected change
validation failure triggers rollback
evidence files written
Security Sandbox integration verified
Policy / Capability integration verified or fail-closed adapter used
Initiator integration verified or fail-closed behavior used
OpenCode concepts borrowed safely
no OpenCode source copied
```

Final expected status:

```text
Governed Patch Execution Layer: VALIDATED — DONE
```

---

# 20. Completion Evidence Record

Path:

```text
.agentx-init/implementation/governed_patch_execution_completion_record.json
```

Required content shape:

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
    "GOVERNED_PATCH_EXECUTION_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "GOVERNED_PATCH_EXECUTION_IMPLEMENTATION_SPEC_v1"
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

# 21. Implementation Drift Blockers

Reject the implementation if it:

```text
places the component outside tools/agentx_evolve/patch_execution/ without recorded deviation
applies patches without rollback snapshot
bypasses Security Sandbox
allows L0 mutation
allows protected path mutation
allows outside-repo mutation
accepts failed validation silently
ignores rollback failure
uses shell to mutate files
adds LLM/model dependency
adds network dependency
adds OpenCode runtime dependency
copies OpenCode source code
adds Git push
deletes evidence during rollback
```

---

# 22. Minimal Implementation Slices

Implement in slices. Do not build the whole layer in one pass.

## 19.1 Slice A — Models, Schemas, Sessions

```text
patch_models.py
schemas
patch_session.py
patch_evidence.py basic history write
session tests
schema tests
```

## 19.2 Slice B — Rollback Manager

```text
rollback_manager.py
snapshot existing files
record non-existing files
restore files
remove created files
verify hashes
rollback tests
```

## 19.3 Slice C — Patch Applier Dry-Run and Exact Edit

```text
patch_policy.py
patch_applier.py
dry-run mode
EXACT_EDIT
WRITE_FILE
CREATE_FILE
operation validation
sandbox precheck integration
```

## 19.4 Slice D — Source Change Guard

```text
source_change_guard.py
before/after hash comparison
unexpected path blocking
L0/protected path blocking
guard evidence
```

## 19.5 Slice E — Validation Gate and Service Orchestration

```text
implementation_validation_gate.py
patch_execution_service.py
validation failure rollback
source guard failure rollback
final session state
completion evidence
```

Each slice must pass compileall and its relevant tests before moving to the next slice.


---

# 23. Coding LLM Handoff Checklist

Before handing this spec to a coding LLM, confirm:

```text
[ ] Security Sandbox is already validated and done.
[ ] New component goes under tools/agentx_evolve/patch_execution/.
[ ] Runtime artifacts go under .agentx-init/implementation/.
[ ] No patch may be applied before session creation.
[ ] No live mutation may occur before rollback snapshot.
[ ] No patch may bypass sandbox precheck.
[ ] OpenCode is conceptual reference only.
[ ] Implementation is Python.
[ ] Tests must not need GPU, network, hosted model, Bun, Node, OpenCode runtime, or Git push.
```

---

# 24. Final Scope-Control Blockers

Reject the implementation if it broadens the layer into any of these:

```text
LLM patch generation
model repair loop
MCP tool server
web UI
remote execution
network patch fetch
Git commit
Git push
promotion gate
human approval UI
task scheduler
background daemon
multi-agent orchestration
```

Those belong to later roadmap layers.

This layer must remain:

```text
deterministic
local
bounded
rollback-protected
sandbox-integrated
evidence-backed
```

---

# 25. Final Coding Handoff Verdict

This v3 document is sufficient for implementation.

A coding LLM should be able to implement the Governed Patch Execution Layer using:

```text
this implementation spec
the v1 contract
the completed Security Sandbox code
the existing Agent_X Initiator code
```

No additional broad planning document is required before implementation.



---

# 26. Explicit Lock File Payload and Stale-Lock Rules

## 28.1 Required Lock Files

The patch execution layer must use these lock files:

```text
.agentx-init/implementation/implementation_session.lock
.agentx-init/implementation/patch_apply.lock
.agentx-init/implementation/rollback.lock
```

## 28.2 Required Lock Payload

Each lock file must contain JSON:

```json
{
  "schema_version": "1.0",
  "schema_id": "implementation_lock.schema.json",
  "lock_id": "string",
  "session_id": "string|null",
  "lock_type": "IMPLEMENTATION_SESSION|PATCH_APPLY|ROLLBACK",
  "owner_component": "GovernedPatchExecution",
  "created_at": "string",
  "pid": "integer|null",
  "repo_root": "string",
  "status": "ACTIVE|STALE|RELEASED",
  "warnings": [],
  "errors": []
}
```

## 28.3 Lock Rules

```text
one live patch session at a time
one rollback at a time
dry-run may not overlap live mutation unless it is read-only and does not inspect half-written artifacts
lock acquisition failure blocks live execution
lock release failure writes warning evidence
lock files are never silently deleted
```

## 28.4 Stale Lock Rules

A lock may be marked stale only if all are true:

```text
lock timestamp is older than configured stale threshold
no active process is associated with the lock, if process check is available
no session is currently PATCH_APPLIED, ROLLBACK_RUNNING, or VALIDATION_RUNNING
the operator/test explicitly permits stale-lock recovery
```

If uncertain:

```text
BLOCK
```

No uncertain stale lock may be removed automatically.

---

# 27. Patch Input Object Contract

The high-level service must accept a schema-style patch input object so tests, CLI wrappers, future Tool/MCP adapters, and future orchestrators all use the same shape.

Required object:

```json
{
  "schema_version": "1.0",
  "schema_id": "governed_patch_input.schema.json",
  "patch_input_id": "string",
  "proposal_id": "string|null",
  "governance_decision_id": "string",
  "policy_decision_id": "string|null",
  "mode": "DRY_RUN|LIVE",
  "approved_paths": [],
  "operations": [],
  "validation_commands": [],
  "warnings": [],
  "errors": []
}
```

Rules:

```text
governance_decision_id is required for LIVE mode
approved_paths must be non-empty for any source mutation
operations must be non-empty
each operation target path must be explicit
each operation target path must appear in approved_paths
validation_commands may be empty only when docs-only policy explicitly allows it
unknown fields may be preserved but must not affect safety decisions
```

If this object is invalid:

```text
status = BLOCKED
failure_class = PATCH_PROPOSAL_INVALID
no source mutation occurs
evidence is written
```

---

# 28. Expected Hash and Conflict Handling

Patch operations may include:

```text
expected_before_hash
```

If `expected_before_hash` is provided:

```text
read current target hash before mutation
compare current hash to expected_before_hash
if mismatch, block the operation
do not mutate the file
record PATCH_TARGET_CONFLICT
write evidence
```

If `expected_before_hash` is missing:

```text
record actual before_hash anyway
continue only if policy permits non-conflict-checked operation
```

Recommended v1 default:

```text
expected_before_hash is optional for tests and dry-run
expected_before_hash mismatch always blocks when provided
actual before_hash is always recorded
```

Failure class:

```text
PATCH_TARGET_CONFLICT
```

---

# 29. Parent Directory and Created File Rollback Rules

## 31.1 Parent Directory Creation

If CREATE_FILE or WRITE_FILE creates missing parent directories, record them:

```json
{
  "created_parent_dirs": []
}
```

## 31.2 Rollback Cleanup

On rollback:

```text
remove files created during the session
restore files that existed before the session
remove created parent directories only if empty
never remove directories that existed before the session
never remove directories containing unrelated files
record skipped cleanup as warning
```

## 31.3 Created File Tracking

For every path where `existed_before=false`:

```text
if rollback runs and file exists, remove it
verify it is absent afterward
record it in removed_created_files
```

If a created file cannot be removed:

```text
rollback verification fails
session status becomes FAILED
future patch sessions are blocked until review
```

---

# 30. Patch Policy Decision Object Contract

`patch_policy.py` must return a schema-style decision object.

```json
{
  "schema_version": "1.0",
  "schema_id": "patch_execution_decision.schema.json",
  "decision_id": "string",
  "session_id": "string|null",
  "timestamp": "string",
  "source_component": "PatchPolicy",
  "decision": "ALLOW|BLOCK|NEEDS_GOVERNANCE|NEEDS_POLICY|NEEDS_ROLLBACK_SNAPSHOT",
  "reason": "string",
  "required_actions": [],
  "warnings": [],
  "errors": []
}
```

Decision rules:

```text
missing governance_decision_id -> NEEDS_GOVERNANCE
missing policy_decision_id -> NEEDS_POLICY unless fail-closed adapter explicitly allows the current low-risk test case
missing approved paths -> BLOCK
unknown operation -> BLOCK
DELETE_FILE -> BLOCK in v1
RENAME_FILE -> BLOCK in v1
unapproved target path -> BLOCK
valid operation under approved path -> ALLOW
```

A policy ALLOW cannot override:

```text
sandbox BLOCK
L0 block
protected path block
outside-repo block
symlink escape block
rollback requirement
```

---

# 31. Validation Command Boundary

Validation commands are controlled execution, not general shell access.

Allowed v1 validation patterns:

```text
python -m compileall tools/agentx_evolve
python -m pytest tools/agentx_evolve/tests/test_<specific_file>.py
```

Blocked by default:

```text
pytest with no path unless explicitly allowlisted
commands outside repo root
commands containing shell operators
commands requiring network
commands invoking Git write operations
commands invoking package install
commands invoking curl/wget
commands invoking bash/sh -c
commands invoking python -c
```

Rules:

```text
all validation commands go through Security Sandbox subprocess precheck
stdout/stderr must be redacted before durable evidence
failed validation triggers rollback in LIVE mode
validation commands must not mutate source files
```

If validation command policy is missing:

```text
BLOCK
```

---

# 32. Rollback Failure Safe-Mode Marker

If rollback verification fails, write:

```text
.agentx-init/implementation/ROLLBACK_FAILED_SAFE_MODE_REQUIRED
```

Marker content:

```json
{
  "schema_version": "1.0",
  "schema_id": "safe_mode_marker.schema.json",
  "session_id": "string",
  "rollback_id": "string",
  "created_at": "string",
  "reason": "ROLLBACK_FAILED",
  "required_action": "HUMAN_REVIEW_REQUIRED",
  "blocked_operations": [
    "LIVE_PATCH_EXECUTION",
    "PROMOTION",
    "GIT_COMMIT"
  ]
}
```

While this marker exists:

```text
live patch execution must block
dry-run may continue only if it does not mutate
evidence/report commands may continue
rollback inspection may continue
```

---

# 33. Final Evidence Package Requirements

The final implementation must produce or capture:

```text
compileall output
pytest output for every required patch execution test file
git status before validation
git status after validation
completion record JSON
list of generated runtime artifacts
rollback snapshot evidence
rollback verification evidence
source change guard PASS evidence
source change guard BLOCK evidence
validation failure rollback evidence
dry-run no-mutation evidence
```

Each evidence item must be marked:

```text
PASS
FAIL
NOT APPLICABLE
NOT IMPLEMENTED
```

No missing evidence item may be silently omitted.

---

# 34. Patch Execution Final Sign-Off Checklist

Use this checklist before marking the layer done.

```text
Structure:
[ ] tools/agentx_evolve/patch_execution/ exists
[ ] required patch execution modules exist
[ ] required schemas exist
[ ] required tests exist

Compile:
[ ] PYTHONPATH=tools python -m compileall tools/agentx_evolve -> PASS

Tests:
[ ] test_patch_session.py -> PASS
[ ] test_patch_applier.py -> PASS
[ ] test_rollback_manager.py -> PASS
[ ] test_source_change_guard.py -> PASS
[ ] test_implementation_validation_gate.py -> PASS
[ ] test_patch_evidence.py -> PASS
[ ] test_patch_execution_schema.py -> PASS
[ ] test_patch_execution_negative_cases.py -> PASS
[ ] test_patch_execution_sandbox_integration.py -> PASS
[ ] test_patch_execution_initiator_integration.py -> PASS

Safety:
[ ] dry-run changes no source files
[ ] approved patch changes only approved files
[ ] unapproved patch blocks
[ ] L0 patch blocks
[ ] protected patch blocks
[ ] outside-repo patch blocks
[ ] symlink escape blocks
[ ] rollback snapshot exists before mutation
[ ] rollback restores before hashes
[ ] created files removed on rollback
[ ] source change guard detects unexpected mutation
[ ] validation failure triggers rollback
[ ] rollback failure creates safe-mode marker

Integration:
[ ] Security Sandbox integration verified
[ ] Policy / Capability adapter fails closed
[ ] Initiator integration works or fails closed
[ ] validation commands go through subprocess precheck

Evidence:
[ ] implementation history written
[ ] patch application record written
[ ] source change guard result written
[ ] validation gate result written
[ ] rollback record written when applicable
[ ] latest artifacts written atomically
[ ] completion record written

Forbidden:
[ ] no LLM dependency
[ ] no network dependency
[ ] no OpenCode runtime dependency
[ ] no Bun/Node dependency
[ ] no Git push
[ ] no evidence deletion during rollback

Final:
[ ] git status clean or only expected ignored runtime artifacts
[ ] final decision: VALIDATED — DONE
```

---

# 35. Final Scope-Control Blockers

Reject the implementation if it broadens this layer into:

```text
LLM patch generation
model repair loop
MCP tool server
web UI
remote execution
network patch fetch
Git commit
Git push
promotion gate
human approval UI
task scheduler
background daemon
multi-agent orchestration
```

Those belong to later roadmap layers.

This layer must remain:

```text
deterministic
local
bounded
rollback-protected
sandbox-integrated
policy-checked
evidence-backed
```



---

# 36. Final Build-Slice Checklist

Use this as the compact implementation sequence.

## 38.1 Slice 1 — Models and Schemas

```text
[ ] patch_models.py
[ ] implementation_session.schema.json
[ ] patch_application.schema.json
[ ] patch_operation.schema.json
[ ] patch_result.schema.json
[ ] rollback_snapshot.schema.json
[ ] rollback_record.schema.json
[ ] source_change_guard.schema.json
[ ] implementation_validation_gate.schema.json
[ ] patch_execution_decision.schema.json
[ ] patch_execution_audit.schema.json
[ ] schema tests pass
```

## 38.2 Slice 2 — Session, Evidence, and Locks

```text
[ ] patch_session.py
[ ] patch_evidence.py
[ ] lock file creation
[ ] stale lock fail-closed handling
[ ] atomic latest artifact write
[ ] append-only JSONL evidence
[ ] session tests pass
[ ] evidence tests pass
```

## 38.3 Slice 3 — Rollback Manager

```text
[ ] rollback_manager.py
[ ] snapshot existing files
[ ] record non-existing files
[ ] restore before hashes
[ ] remove created files
[ ] clean created empty parent directories only
[ ] rollback failure safe-mode marker
[ ] rollback tests pass
```

## 38.4 Slice 4 — Policy and Patch Application

```text
[ ] patch_policy.py
[ ] patch_applier.py
[ ] governed_patch_input validation
[ ] EXACT_EDIT
[ ] WRITE_FILE
[ ] CREATE_FILE
[ ] bounded PATCH_TEXT or explicit safe block
[ ] DELETE_FILE blocked in v1
[ ] RENAME_FILE blocked in v1
[ ] expected_before_hash conflict handling
[ ] dry-run no-mutation proof
[ ] patch applier tests pass
```

## 38.5 Slice 5 — Source Guard and Validation Gate

```text
[ ] source_change_guard.py
[ ] implementation_validation_gate.py
[ ] before/after hash comparison
[ ] unexpected path detection
[ ] L0/protected path detection
[ ] validation command allowlist
[ ] validation failure rollback
[ ] source guard tests pass
[ ] validation gate tests pass
```

## 38.6 Slice 6 — Service Orchestration and Completion

```text
[ ] patch_execution_service.py
[ ] full dry-run session
[ ] full live accepted session
[ ] live validation-failure rollback session
[ ] live source-guard-failure rollback session
[ ] completion record
[ ] fresh-clone validation
[ ] final git status check
```

---

# 37. Implementation Acceptance State Table

| Final State | Meaning | May mark layer DONE? |
|---|---|---|
| `VALIDATED` | compileall, tests, safety checks, evidence, and completion record all pass | Yes |
| `DONE` | acceptable synonym only when evidence says `VALIDATED` | Yes |
| `DRY_RUN_READY` | dry-run preview works but live patch path not proven | No |
| `BLOCKED` | policy, sandbox, governance, or input blocked mutation safely | No, unless testing a blocked case |
| `ROLLED_BACK` | mutation occurred and rollback completed successfully | No for layer completion, yes for rollback test |
| `FAILED` | patch, validation, source guard, evidence, or rollback failed | No |
| `SAFE_MODE_REQUIRED` | rollback or guard failure requires human review | No |
| `NOT_IMPLEMENTED` | required feature missing | No |

Final layer completion requires:

```text
status = VALIDATED
final_decision = DONE
```

in:

```text
.agentx-init/implementation/governed_patch_execution_completion_record.json
```

---

# 38. Final Pass / Fail Evidence Checklist

The final validation evidence must include:

```text
[ ] exact commit hash
[ ] compileall command and PASS result
[ ] pytest command and PASS result
[ ] total test count and runtime
[ ] git status before tests
[ ] git status after tests
[ ] dry-run no-mutation evidence
[ ] approved live patch evidence
[ ] unapproved patch block evidence
[ ] L0/protected/outside-repo block evidence
[ ] rollback snapshot evidence
[ ] rollback verification evidence
[ ] validation failure rollback evidence
[ ] source change guard failure rollback evidence
[ ] safe-mode marker test evidence, if rollback failure is simulated
[ ] completion record path
[ ] completion record JSON validates
```

No item should be marked complete from intent alone. Each item must be proven by test output, artifact output, or explicit completion evidence.

---

# 39. Freeze Note

This v5 document is frozen as the implementation handoff document for Governed Patch Execution.

Do not add broad new responsibilities to this layer.

Any future additions such as:

```text
LLM patch generation
MCP exposure
Git commit
promotion
human approval UI
model-based repair
remote execution
```

must be implemented in their own roadmap layers and must not be folded into this patch execution layer.


---

# 40. Final Rating

This v5 implementation spec is rated:

```text
10/10
```

It is complete enough for a coding LLM or developer to implement the Governed Patch Execution Layer using this document plus the repository contents and the contract document.
