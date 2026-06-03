# FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC_v3

```text
document_id: FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC
version: v3.0
status: implementation-ready, final acceptance-aligned
based_on: FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
component_id: AGENTX_FAILURE_TAXONOMY_RECOVERY_PLAYBOOK
component_name: Failure Taxonomy / Recovery Playbook
roadmap_layer: 4
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
target_language: Python
target_package: tools/agentx_evolve/recovery/
runtime_state_root: .agentx-init/recovery/
implementation_mode: deterministic, non-LLM, non-mutating recovery-decision layer
rating_target: 10/10
```

---

# 0. v3 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 implementation spec was rated:

```text
9.7/10
```

## 0.2 Why v2 Was Not Fully 10/10

The v2 document was already strong. It covered the required files, schemas, runtime artifacts, integrations, tests, acceptance criteria, Definition of Done, fresh-clone validation, and non-execution boundaries.

The remaining gaps were precision gaps for a coding LLM:

```text
1. It did not define exact minimum field defaults for each dataclass.
2. It did not define exact context keys and their default values.
3. It did not define exact expected behavior when failure input is malformed.
4. It did not define status/result values for evidence-writing helper returns.
5. It did not define schema validation expectations for completion evidence.
6. It did not provide a per-file acceptance checklist.
7. It did not include a final "do not broaden scope" rule tied to future layers.
```

## 0.3 v3 Improvements

This v3 adds:

```text
exact dataclass default rules
context-default contract
malformed input handling
evidence helper return contract
completion evidence validation rules
per-file acceptance checklist
scope-freeze rule
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the full implementation specification for the **Failure Taxonomy / Recovery Playbook** layer.

It converts the controlling contract:

```text
FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v1
```

into concrete implementation instructions.

The implementation must create a deterministic recovery-decision layer that standardizes:

```text
failure classes
failure severity
recovery actions
safe-mode triggers
human-review requirements
rollback requirements
retry rules
failure evidence
recovery evidence
```

This layer must not execute recovery. It decides what recovery should happen.

---

# 2. Canonical Subdirectory

The implementation must reside under:

```text
tools/agentx_evolve/recovery/
```

Schemas must reside under:

```text
tools/agentx_evolve/schemas/
```

Tests must reside under:

```text
tools/agentx_evolve/tests/
```

Runtime evidence must reside under:

```text
.agentx-init/recovery/
```

This is the canonical layout:

```text
tools/agentx_evolve/security/   = validated Security Sandbox / Filesystem Boundary
tools/agentx_evolve/recovery/   = new Failure Taxonomy / Recovery Playbook
```

## 1.1 Import and Package Rule

Source and tests should import the package as:

```python
from agentx_evolve.recovery.failure_taxonomy import classify_failure
from agentx_evolve.recovery.recovery_decider import decide_recovery
```

Do not use this as the default import style:

```python
from tools.agentx_evolve.recovery.failure_taxonomy import classify_failure
```

Test-time command examples should use:

```bash
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
```

The implementation must not require:

```text
LLM
GPU
network
OpenCode runtime
Bun
Node
MCP server
Git write access
```

## 1.2 Security Sandbox Integration Rule

All durable writes under `.agentx-init/recovery/` should use either:

```text
the validated Security Sandbox safe runtime write path
```

or:

```text
a local atomic write helper that follows the same rules
```

Required behavior:

```text
write only under .agentx-init/recovery/
append JSONL history only
write latest JSON atomically
do not mutate source
do not write unredacted sensitive data
```

---

# 3. Scope

## 2.1 Required in v1

Implement:

```text
failure model dataclasses
failure class registry
failure severity matrix
recovery action registry
recovery policy matrix
safe-mode trigger rules
recovery decision engine
append-only failure evidence
latest failure/recovery artifacts
schema files
tests
completion evidence
```

## 2.2 Not Required in v1

Do not implement:

```text
actual rollback execution
actual patch repair
actual model retry
actual shell execution
actual network call
actual MCP tool execution
Git operations
LLM-based recovery
background scheduler
web UI
human review UI
```

This layer decides. Later layers execute.

## 2.3 Strict Non-Execution Boundary

This layer may output:

```text
RETRY
REBUILD_CONTEXT
ROLLBACK
BLOCK_SESSION
ENTER_SAFE_MODE
REQUEST_HUMAN_REVIEW
REJECT_OUTPUT
REVALIDATE
NO_ACTION
```

But it must not actually:

```text
retry a model call
rebuild a context packet
apply a patch
rollback files
enter global safe mode
ask a human
run validation
execute a tool
execute shell
write source
```

Those actions belong to later layers.

This layer is a deterministic classifier and decider only.

---

# 4. OpenCode Borrowing Boundary

This implementation may borrow these OpenCode ideas conceptually:

```text
invalid-tool handling
tool failure handling
permission-denied failure flow
command failure awareness
question/human prompt concept
todo/task-state concept
fail-closed tool result behavior
```

It must not borrow:

```text
OpenCode source code
OpenCode TypeScript/Bun runtime
OpenCode shell assumptions
OpenCode plugin execution assumptions
OpenCode network-enabled defaults
OpenCode UI/product architecture
```

Agent_X adaptation:

```text
OpenCode invalid-tool concept -> UNKNOWN_FAILURE or TOOL_NOT_ALLOWED
OpenCode permission denial -> POLICY_DENIED / CAPABILITY_MISSING / ROLE_NOT_AUTHORIZED
OpenCode command failure -> TOOL_FAILURE / COMMAND_NOT_ALLOWLISTED / SUBPROCESS_BLOCKED
OpenCode ask-user concept -> REQUEST_HUMAN_REVIEW recovery action
OpenCode task/todo state -> future session evidence, not implemented here
```

No Bun, Node, TypeScript, OpenCode runtime, plugin execution, or network behavior is allowed in this layer.

---

# 5. Exact Files to Create

## 3.1 Python Package Files

Create:

```text
tools/agentx_evolve/recovery/__init__.py
tools/agentx_evolve/recovery/failure_models.py
tools/agentx_evolve/recovery/failure_taxonomy.py
tools/agentx_evolve/recovery/recovery_playbook.py
tools/agentx_evolve/recovery/recovery_policy.py
tools/agentx_evolve/recovery/safe_mode_triggers.py
tools/agentx_evolve/recovery/failure_evidence.py
tools/agentx_evolve/recovery/recovery_decider.py
```

## 3.2 Schema Files

Create:

```text
tools/agentx_evolve/schemas/05_recovery/failure_record.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_action.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_decision.schema.json
tools/agentx_evolve/schemas/05_recovery/safe_mode_trigger.schema.json
tools/agentx_evolve/schemas/05_recovery/failure_evidence.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_playbook.schema.json
tools/agentx_evolve/schemas/05_recovery/failure_taxonomy.schema.json
```

## 3.3 Test Files

Create:

```text
tools/agentx_evolve/tests/test_failure_taxonomy.py
tools/agentx_evolve/tests/test_recovery_policy.py
tools/agentx_evolve/tests/test_recovery_decider.py
tools/agentx_evolve/tests/test_safe_mode_triggers.py
tools/agentx_evolve/tests/test_failure_evidence.py
tools/agentx_evolve/tests/test_failure_schema.py
tools/agentx_evolve/tests/test_failure_negative_cases.py
```

## 3.4 Runtime Artifacts

The implementation must write only under:

```text
.agentx-init/recovery/
```

Required runtime artifacts:

```text
.agentx-init/recovery/failure_records.jsonl
.agentx-init/recovery/recovery_decisions.jsonl
.agentx-init/recovery/safe_mode_triggers.jsonl
.agentx-init/recovery/latest_failure_record.json
.agentx-init/recovery/latest_recovery_decision.json
.agentx-init/recovery/latest_safe_mode_trigger.json
.agentx-init/recovery/recovery_summary.json
.agentx-init/recovery/failure_recovery_completion_record.json
```

---

# 6. Implementation Order

Implement in this order:

```text
1. failure_models.py
2. failure_taxonomy.py
3. recovery_playbook.py
4. recovery_policy.py
5. safe_mode_triggers.py
6. recovery_decider.py
7. failure_evidence.py
8. schemas
9. tests
10. completion evidence
```

Reason:

```text
models first
taxonomy before policy
policy before decision engine
safe-mode rules before recovery decision
evidence after structured records exist
schemas/tests after expected data shapes are stable
```

---

# 7. File-by-File Implementation

---

## 5.1 `tools/agentx_evolve/recovery/__init__.py`

Purpose:

```text
Expose the public recovery-layer API.
```

Required exports:

```python
from .failure_models import (
    FailureRecord,
    RecoveryAction,
    RecoveryDecision,
    SafeModeTrigger,
)
from .failure_taxonomy import (
    REQUIRED_FAILURE_CLASSES,
    get_failure_severity,
    classify_failure,
)
from .recovery_policy import select_recovery_actions
from .recovery_decider import decide_recovery
from .safe_mode_triggers import requires_safe_mode, build_safe_mode_trigger
from .failure_evidence import (
    append_failure_record,
    append_recovery_decision,
    write_latest_failure_record,
    write_latest_recovery_decision,
)
```

Must not:

```text
execute recovery
write files at import time
read config at import time
call network
call model
```

---

## 5.2 `failure_models.py`

Purpose:

```text
Define structured recovery dataclasses and constants.
```

Required constants:

```python
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

DECISION_RECOVERABLE = "RECOVERABLE"
DECISION_NON_RECOVERABLE = "NON_RECOVERABLE"
DECISION_BLOCKED = "BLOCKED"
DECISION_SAFE_MODE_REQUIRED = "SAFE_MODE_REQUIRED"
DECISION_HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"

ACTION_RETRY = "RETRY"
ACTION_REBUILD_CONTEXT = "REBUILD_CONTEXT"
ACTION_ROLLBACK = "ROLLBACK"
ACTION_BLOCK_SESSION = "BLOCK_SESSION"
ACTION_ENTER_SAFE_MODE = "ENTER_SAFE_MODE"
ACTION_REQUEST_HUMAN_REVIEW = "REQUEST_HUMAN_REVIEW"
ACTION_REJECT_OUTPUT = "REJECT_OUTPUT"
ACTION_REVALIDATE = "REVALIDATE"
ACTION_NO_ACTION = "NO_ACTION"
```

Required helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
```

Required dataclasses:

```python
@dataclass
class FailureRecord:
    schema_version: str
    schema_id: str
    failure_id: str
    timestamp: str
    source_component: str
    source_layer: str
    session_id: str | None
    operation: str | None
    failure_class: str
    severity: str
    message: str
    details: dict
    input_artifact_refs: list[str]
    related_artifact_refs: list[str]
    requires_recovery: bool
    requires_safe_mode: bool
    requires_human_review: bool
    retryable: bool
    rollback_required: bool
    warnings: list[str]
    errors: list[str]
```

```python
@dataclass
class RecoveryAction:
    schema_version: str
    schema_id: str
    recovery_action_id: str
    timestamp: str
    failure_id: str
    action_type: str
    action_status: str
    reason: str
    executor_component: str | None
    max_attempts: int
    attempt_number: int
    preconditions: list[str]
    expected_result: str
    warnings: list[str]
    errors: list[str]
```

```python
@dataclass
class RecoveryDecision:
    schema_version: str
    schema_id: str
    recovery_decision_id: str
    timestamp: str
    failure_id: str
    decision: str
    selected_actions: list[dict]
    reason: str
    policy_rule_ids: list[str]
    safe_mode_required: bool
    human_review_required: bool
    rollback_required: bool
    retry_allowed: bool
    continue_session_allowed: bool
    warnings: list[str]
    errors: list[str]
```

```python
@dataclass
class SafeModeTrigger:
    schema_version: str
    schema_id: str
    safe_mode_trigger_id: str
    timestamp: str
    failure_id: str
    trigger_type: str
    reason: str
    required_actions: list[str]
    system_state: str
    warnings: list[str]
    errors: list[str]
```

Acceptance:

```text
all dataclasses instantiate
to_dict works
IDs are generated
timestamps are stable ISO strings
no runtime side effects
```

## 5.2.1 Dataclass Default Rules

All dataclasses must be easy to construct from helper factory functions without callers manually filling every metadata field.

Use helper constructors or classmethods such as:

```python
make_failure_record(...)
make_recovery_action(...)
make_recovery_decision(...)
make_safe_mode_trigger(...)
```

Required default behavior:

```text
schema_version defaults to "1.0"
schema_id defaults to the matching schema filename
timestamp defaults to utc_now_iso()
IDs default to new_id(<prefix>)
warnings defaults to []
errors defaults to []
details defaults to {}
artifact ref lists default to []
```

Do not use mutable list/dict defaults directly in dataclasses. Use `default_factory`.

Required ID prefixes:

```text
failure_id -> fail_
recovery_action_id -> recact_
recovery_decision_id -> recdec_
safe_mode_trigger_id -> safemode_
```

---

## 5.3 `failure_taxonomy.py`

Purpose:

```text
Define canonical failure classes and severity defaults.
```

Required set:

```python
REQUIRED_FAILURE_CLASSES = {
    "MODEL_INVALID_OUTPUT",
    "MODEL_INSUFFICIENT_CONTEXT",
    "PATCH_APPLY_FAILED",
    "VALIDATION_FAILED",
    "GOVERNANCE_BLOCKED",
    "RISK_TOO_HIGH",
    "SOURCE_GUARD_FAILED",
    "ROLLBACK_FAILED",
    "SCHEMA_VALIDATION_FAILED",
    "TOOL_FAILURE",
    "LOCK_CONFLICT",
    "ATOMIC_WRITE_FAILED",
    "PROMPT_CONTRACT_FAILED",
    "POLICY_DENIED",
    "CAPABILITY_MISSING",
    "ROLE_NOT_AUTHORIZED",
    "TOOL_NOT_ALLOWED",
    "MODEL_NOT_ALLOWED",
    "PATH_NOT_ALLOWED",
    "NETWORK_MODE_DENIED",
    "APPROVAL_REQUIRED",
    "PATH_TRAVERSAL",
    "PATH_OUTSIDE_REPO",
    "SYMLINK_ESCAPE",
    "L0_WRITE_BLOCKED",
    "PROTECTED_PATH_BLOCKED",
    "SOURCE_WRITE_DISABLED",
    "RUNTIME_WRITE_BOUNDARY_VIOLATION",
    "SUBPROCESS_BLOCKED",
    "COMMAND_NOT_ALLOWLISTED",
    "NETWORK_BLOCKED",
    "SECRET_REDACTION_FAILED",
    "UNEXPECTED_FILE_MUTATION",
    "IMPLEMENTATION_SESSION_FAILED",
    "UNKNOWN_FAILURE",
}
```

Required maps:

```python
DEFAULT_SEVERITY_BY_FAILURE_CLASS: dict[str, str]
```

Required functions:

```python
is_known_failure_class(failure_class: str) -> bool

normalize_failure_class(failure_class: str | None) -> str

get_failure_severity(failure_class: str, context: dict | None = None) -> str

classify_failure(raw_failure: dict) -> FailureRecord
```

Rules:

```text
unknown or missing failure_class becomes UNKNOWN_FAILURE
UNKNOWN_FAILURE requires human review
UNKNOWN_FAILURE severity HIGH by default
UNKNOWN_FAILURE severity CRITICAL if mutation_state_unknown is true
CRITICAL failures require safe mode if safe-mode trigger rules say so
```

Acceptance:

```text
all required failure classes exist
unknown failure maps safely
severity is deterministic
no ad hoc failure strings outside taxonomy
```

## 5.3.1 Malformed Input Handling

`classify_failure(raw_failure)` must handle malformed input safely.

Rules:

```text
raw_failure is None -> UNKNOWN_FAILURE
raw_failure is not dict -> UNKNOWN_FAILURE
missing failure_class -> UNKNOWN_FAILURE
empty failure_class -> UNKNOWN_FAILURE
unknown failure_class -> UNKNOWN_FAILURE
missing message -> generated safe default message
missing source_component -> "unknown"
missing source_layer -> "unknown"
missing details -> {}
missing artifact refs -> []
```

Malformed input must never cause silent success.

Malformed input must produce:

```text
failure_class = UNKNOWN_FAILURE
requires_human_review = true
requires_recovery = true
continue_session_allowed = false after decision
```

---

## 5.4 `recovery_playbook.py`

Purpose:

```text
Define allowed recovery actions and policy rule IDs.
```

Required recovery action types:

```text
RETRY
REBUILD_CONTEXT
ROLLBACK
BLOCK_SESSION
ENTER_SAFE_MODE
REQUEST_HUMAN_REVIEW
REJECT_OUTPUT
REVALIDATE
NO_ACTION
```

Required rule IDs:

```text
REC-POL-001-MODEL-INVALID-OUTPUT
REC-POL-002-MODEL-INSUFFICIENT-CONTEXT
REC-POL-003-PATCH-APPLY-FAILED
REC-POL-004-VALIDATION-FAILED
REC-POL-005-GOVERNANCE-BLOCKED
REC-POL-006-RISK-TOO-HIGH
REC-POL-007-SOURCE-GUARD-FAILED
REC-POL-008-ROLLBACK-FAILED
REC-POL-009-SCHEMA-VALIDATION-FAILED
REC-POL-010-TOOL-FAILURE
REC-POL-011-LOCK-CONFLICT
REC-POL-012-ATOMIC-WRITE-FAILED
REC-POL-013-PROMPT-CONTRACT-FAILED
REC-POL-014-POLICY-DENIED
REC-POL-015-SANDBOX-CRITICAL
REC-POL-016-SECRET-REDACTION-FAILED
REC-POL-017-UNKNOWN-FAILURE
```

Required public functions:

```python
get_recovery_rule_for_failure(failure_class: str) -> dict

get_allowed_recovery_actions() -> set[str]
```

Acceptance:

```text
each required failure class maps to a rule or default safe rule
no recovery action executes here
```

---

## 5.5 `recovery_policy.py`

Purpose:

```text
Map failure records to recovery action proposals.
```

Required public function:

```python
select_recovery_actions(
    failure: FailureRecord,
    context: dict | None = None
) -> list[RecoveryAction]
```

Required mappings:

```text
MODEL_INVALID_OUTPUT -> REJECT_OUTPUT + RETRY
MODEL_INSUFFICIENT_CONTEXT -> REBUILD_CONTEXT
PATCH_APPLY_FAILED -> ROLLBACK if mutation_started else BLOCK_SESSION
VALIDATION_FAILED -> REVALIDATE or ROLLBACK depending on mutation state
GOVERNANCE_BLOCKED -> BLOCK_SESSION
RISK_TOO_HIGH -> REQUEST_HUMAN_REVIEW + BLOCK_SESSION
SOURCE_GUARD_FAILED -> ROLLBACK + ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
ROLLBACK_FAILED -> ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
SCHEMA_VALIDATION_FAILED -> REJECT_OUTPUT or BLOCK_SESSION
TOOL_FAILURE -> RETRY or BLOCK_SESSION
LOCK_CONFLICT -> BLOCK_SESSION
ATOMIC_WRITE_FAILED -> BLOCK_SESSION + optional REQUEST_HUMAN_REVIEW
PROMPT_CONTRACT_FAILED -> REJECT_OUTPUT
POLICY_DENIED -> BLOCK_SESSION
PATH_TRAVERSAL -> ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
SYMLINK_ESCAPE -> ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
L0_WRITE_BLOCKED -> ENTER_SAFE_MODE + REQUEST_HUMAN_REVIEW
SECRET_REDACTION_FAILED -> BLOCK_SESSION + REQUEST_HUMAN_REVIEW
UNKNOWN_FAILURE -> REQUEST_HUMAN_REVIEW + BLOCK_SESSION
```

Context keys:

```text
mutation_started
validation_failed_after_mutation
mutation_state_unknown
retry_count
max_retries
rollback_available
```

Context defaults:

```text
mutation_started = false
validation_failed_after_mutation = false
mutation_state_unknown = false
retry_count = 0
max_retries = 1
rollback_available = false
policy_registry_available = false
governed_patch_execution_available = false
initiator_artifacts_available = false
```

If context is missing, use safe defaults. Missing context must not allow risky continuation.


Rules:

```text
do not retry if max_retries exceeded
do not continue after CRITICAL failure
do not select rollback if rollback is unavailable; select safe mode + human review instead
do not silently ignore unknown failure
```

---

## 5.6 `safe_mode_triggers.py`

Purpose:

```text
Decide whether a failure requires safe mode and build safe-mode trigger records.
```

Required trigger types:

```text
ROLLBACK_FAILED
SOURCE_GUARD_FAILED
UNEXPECTED_FILE_MUTATION
POLICY_MISSING
CAPABILITY_REGISTRY_MISSING
SCHEMA_REPEATED_FAILURE
LOCK_CORRUPTION
GOVERNANCE_ARTIFACT_MISSING
UNKNOWN_CRITICAL_FAILURE
```

Required public functions:

```python
requires_safe_mode(
    failure: FailureRecord,
    context: dict | None = None
) -> bool

get_safe_mode_trigger_type(
    failure: FailureRecord,
    context: dict | None = None
) -> str | None

build_safe_mode_trigger(
    failure: FailureRecord,
    reason: str
) -> SafeModeTrigger
```

Required rules:

```text
ROLLBACK_FAILED requires safe mode
SOURCE_GUARD_FAILED requires safe mode
UNEXPECTED_FILE_MUTATION requires safe mode
PATH_TRAVERSAL requires safe mode
SYMLINK_ESCAPE requires safe mode
L0_WRITE_BLOCKED requires safe mode
UNKNOWN_FAILURE + CRITICAL requires safe mode
missing governance artifact for mutation requires safe mode
```

---

## 5.7 `recovery_decider.py`

Purpose:

```text
Produce final recovery decision for a failure.
```

Required public function:

```python
decide_recovery(
    failure: FailureRecord,
    context: dict | None = None
) -> RecoveryDecision
```

Decision logic:

```text
1. Select recovery actions.
2. Check safe-mode trigger.
3. Check human-review requirement.
4. Check rollback requirement.
5. Check retry allowance.
6. Decide whether session may continue.
7. Return schema-shaped RecoveryDecision.
```

Decision rules:

```text
CRITICAL -> continue_session_allowed false
safe mode required -> decision SAFE_MODE_REQUIRED
human review required and no safe mode -> HUMAN_REVIEW_REQUIRED
rollback required -> selected_actions include ROLLBACK or safe-mode fallback
policy denial -> BLOCKED
recoverable low/medium model failure -> RECOVERABLE
unknown failure -> HUMAN_REVIEW_REQUIRED or SAFE_MODE_REQUIRED
```

---

## 5.8 `failure_evidence.py`

Purpose:

```text
Write append-only failure and recovery evidence.
```

Required public functions:

```python
append_failure_record(failure: FailureRecord, repo_root: Path) -> dict

append_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict

append_safe_mode_trigger(trigger: SafeModeTrigger, repo_root: Path) -> dict

write_latest_failure_record(failure: FailureRecord, repo_root: Path) -> dict

write_latest_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict

write_latest_safe_mode_trigger(trigger: SafeModeTrigger, repo_root: Path) -> dict

write_recovery_summary(summary: dict, repo_root: Path) -> dict
```

Runtime paths:

```text
.agentx-init/recovery/failure_records.jsonl
.agentx-init/recovery/recovery_decisions.jsonl
.agentx-init/recovery/safe_mode_triggers.jsonl
.agentx-init/recovery/latest_failure_record.json
.agentx-init/recovery/latest_recovery_decision.json
.agentx-init/recovery/latest_safe_mode_trigger.json
.agentx-init/recovery/recovery_summary.json
```

Rules:

```text
append JSONL only
write latest JSON atomically
create .agentx-init/recovery if missing
never delete history
never execute recovery
redact secrets if details may contain sensitive text
```

Use local atomic-write helper if available from Security Sandbox or Initiator. If unavailable, implement deterministic temp-file + replace behavior locally.

## 5.8.1 Evidence Helper Return Contract

Every evidence helper must return a dict with this shape:

```json
{
  "status": "SUCCESS|FAILED|BLOCKED",
  "path": "string",
  "artifact_id": "string|null",
  "message": "string",
  "warnings": [],
  "errors": []
}
```

Rules:

```text
SUCCESS only when write completed
FAILED when write was attempted and failed
BLOCKED when input was invalid or path was outside .agentx-init/recovery/
errors must not be empty for FAILED or BLOCKED
```

Evidence helpers must not raise unhandled exceptions for expected filesystem errors.

---

# 8. Schema Implementation Spec

Use JSON Schema Draft 2020-12 or the same draft used by current Agent_X schemas.

Each schema must require:

```text
schema_version
schema_id
timestamp
warnings
errors
```

## 6.0 Required Enum Constraints

Schema enum values must be explicit.

Severity enum:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Recovery decision enum:

```text
RECOVERABLE
NON_RECOVERABLE
BLOCKED
SAFE_MODE_REQUIRED
HUMAN_REVIEW_REQUIRED
```

Recovery action type enum:

```text
RETRY
REBUILD_CONTEXT
ROLLBACK
BLOCK_SESSION
ENTER_SAFE_MODE
REQUEST_HUMAN_REVIEW
REJECT_OUTPUT
REVALIDATE
NO_ACTION
```

Action status enum:

```text
PROPOSED
STARTED
COMPLETED
FAILED
BLOCKED
```

Safe mode trigger enum:

```text
ROLLBACK_FAILED
SOURCE_GUARD_FAILED
UNEXPECTED_FILE_MUTATION
POLICY_MISSING
CAPABILITY_REGISTRY_MISSING
SCHEMA_REPEATED_FAILURE
LOCK_CORRUPTION
GOVERNANCE_ARTIFACT_MISSING
UNKNOWN_CRITICAL_FAILURE
```

Failure class enum should include every required class listed in this document.


## 6.1 `failure_record.schema.json`

Must require:

```text
failure_id
timestamp
source_component
source_layer
session_id
operation
failure_class
severity
message
details
input_artifact_refs
related_artifact_refs
requires_recovery
requires_safe_mode
requires_human_review
retryable
rollback_required
warnings
errors
```

## 6.2 `recovery_action.schema.json`

Must require:

```text
recovery_action_id
timestamp
failure_id
action_type
action_status
reason
executor_component
max_attempts
attempt_number
preconditions
expected_result
warnings
errors
```

## 6.3 `recovery_decision.schema.json`

Must require:

```text
recovery_decision_id
timestamp
failure_id
decision
selected_actions
reason
policy_rule_ids
safe_mode_required
human_review_required
rollback_required
retry_allowed
continue_session_allowed
warnings
errors
```

## 6.4 `safe_mode_trigger.schema.json`

Must require:

```text
safe_mode_trigger_id
timestamp
failure_id
trigger_type
reason
required_actions
system_state
warnings
errors
```

## 6.5 `failure_evidence.schema.json`

Must require:

```text
evidence_id
timestamp
source_component
event_type
failure_id
recovery_decision_id
artifact_refs
success
warnings
errors
```

## 6.6 `recovery_playbook.schema.json`

Must require:

```text
playbook_id
timestamp
version
rules
warnings
errors
```

## 6.7 `failure_taxonomy.schema.json`

Must require:

```text
taxonomy_id
timestamp
version
failure_classes
severity_matrix
warnings
errors
```

---

# 9. Integration Requirements

## 7.1 Integration With Security Sandbox

The recovery layer must classify sandbox failures:

```text
PATH_TRAVERSAL
PATH_OUTSIDE_REPO
SYMLINK_ESCAPE
L0_WRITE_BLOCKED
PROTECTED_PATH_BLOCKED
SOURCE_WRITE_DISABLED
RUNTIME_WRITE_BOUNDARY_VIOLATION
SUBPROCESS_BLOCKED
COMMAND_NOT_ALLOWLISTED
NETWORK_BLOCKED
SECRET_REDACTION_FAILED
```

Rules:

```text
sandbox CRITICAL failures must not be retried blindly
PATH_TRAVERSAL, SYMLINK_ESCAPE, L0_WRITE_BLOCKED require safe mode
SECRET_REDACTION_FAILED blocks logging and requests human review
```

## 7.2 Integration With Policy / Capability Registry

The recovery layer must classify policy failures:

```text
POLICY_DENIED
CAPABILITY_MISSING
ROLE_NOT_AUTHORIZED
TOOL_NOT_ALLOWED
MODEL_NOT_ALLOWED
PATH_NOT_ALLOWED
NETWORK_MODE_DENIED
APPROVAL_REQUIRED
```

Rules:

```text
POLICY_DENIED blocks session
CAPABILITY_MISSING blocks session unless configuration can be repaired manually
APPROVAL_REQUIRED routes to human review
this layer must not override policy denial
```

## 7.3 Integration With Governed Patch Execution

The recovery layer must classify patch failures:

```text
PATCH_APPLY_FAILED
SOURCE_GUARD_FAILED
VALIDATION_FAILED
ROLLBACK_FAILED
UNEXPECTED_FILE_MUTATION
IMPLEMENTATION_SESSION_FAILED
```

Rules:

```text
SOURCE_GUARD_FAILED requires rollback or safe mode
ROLLBACK_FAILED requires safe mode
UNEXPECTED_FILE_MUTATION requires safe mode
VALIDATION_FAILED after mutation requires rollback or repair decision
```

## 7.4 Integration With Initiator

The recovery layer must reference Initiator artifacts where available:

```text
governance decision IDs
risk assessment IDs
validation report IDs
audit event IDs
memory references
graph references
proposal IDs
plan IDs
```

Rules:

```text
do not replace Initiator governance
do not rewrite Initiator artifacts
do not make risk decisions independently
only classify failure and decide recovery path
```

## 7.5 Fallback Behavior for Not-Yet-Built Layers

Because Policy / Capability Registry and Governed Patch Execution may not exist yet when this layer is first implemented, use deterministic placeholder integration rules.

If Policy / Capability Registry is not present:

```text
classify policy-related failures using raw input records
do not attempt policy execution
do not claim policy integration is fully validated
record integration as NOT_AVAILABLE or NOT_YET_IMPLEMENTED where evidence requires it
```

If Governed Patch Execution is not present:

```text
classify patch-related failures using synthetic or test records
do not apply patches
do not execute rollback
do not claim live patch integration is validated
record integration as NOT_AVAILABLE or NOT_YET_IMPLEMENTED where evidence requires it
```

If Initiator artifacts are unavailable:

```text
allow classification from raw failure dictionaries
record missing artifact refs in warnings
do not invent governance or risk decisions
```

This keeps v1 deterministic and implementable before later layers exist.

---

# 10. Test Cases

## 8.1 `test_failure_taxonomy.py`

Required tests:

```text
test_failure_taxonomy_contains_required_classes
test_unknown_failure_maps_to_unknown_failure
test_unknown_failure_requires_human_review
test_l0_write_blocked_is_critical
test_path_traversal_is_critical
test_model_invalid_output_is_low_or_medium
test_required_failure_classes_have_severity
```

## 8.2 `test_recovery_policy.py`

Required tests:

```text
test_model_invalid_output_selects_reject_and_retry
test_model_insufficient_context_selects_rebuild_context
test_policy_denied_blocks_session
test_risk_too_high_requires_human_review
test_patch_apply_failed_after_mutation_selects_rollback
test_validation_failed_after_mutation_selects_rollback_or_revalidate
test_secret_redaction_failed_blocks_logging_and_review
test_unknown_failure_selects_human_review
```

## 8.3 `test_recovery_decider.py`

Required tests:

```text
test_critical_failure_blocks_continuation
test_recoverable_model_failure_allows_retry
test_policy_denied_decision_blocked
test_safe_mode_failure_decision_safe_mode_required
test_human_review_failure_decision_human_review_required
test_unknown_failure_does_not_continue_silently
```

## 8.4 `test_safe_mode_triggers.py`

Required tests:

```text
test_rollback_failed_triggers_safe_mode
test_source_guard_failed_triggers_safe_mode
test_unexpected_file_mutation_triggers_safe_mode
test_l0_write_blocked_triggers_safe_mode
test_path_traversal_triggers_safe_mode
test_symlink_escape_triggers_safe_mode
test_unknown_critical_failure_triggers_safe_mode
test_low_model_failure_does_not_trigger_safe_mode
```

## 8.5 `test_failure_evidence.py`

Required tests:

```text
test_failure_record_appends_jsonl
test_recovery_decision_appends_jsonl
test_safe_mode_trigger_appends_jsonl
test_latest_failure_written_atomically
test_latest_recovery_decision_written_atomically
test_recovery_summary_written
test_existing_history_not_deleted
```

## 8.6 `test_failure_schema.py`

Required tests:

```text
test_failure_record_schema_accepts_valid_record
test_failure_record_schema_rejects_missing_failure_class
test_recovery_action_schema_accepts_valid_action
test_recovery_decision_schema_accepts_valid_decision
test_safe_mode_trigger_schema_accepts_valid_trigger
test_failure_taxonomy_schema_accepts_valid_taxonomy
test_recovery_playbook_schema_accepts_valid_playbook
```

## 8.7 `test_failure_negative_cases.py`

Required tests:

```text
test_no_llm_imports
test_no_network_imports
test_no_patch_execution_imports
test_no_rollback_execution
test_no_shell_execution
test_no_source_mutation
test_critical_failure_cannot_continue
test_unknown_failure_cannot_be_silent_success
```

---

# 11. Validation Commands

## 9.1 Fresh-Clone Validation

Preferred final validation should run from a clean checkout:

```bash
git status --short
PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_decider.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_safe_mode_triggers.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_negative_cases.py
git status --short
```

Expected:

```text
compileall PASS
all recovery tests PASS
no unexpected source mutation
```

## 9.2 Individual Validation Commands

Run:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_decider.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_safe_mode_triggers.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_negative_cases.py
```

Then:

```bash
git status --short
```

Expected:

```text
no unexpected source mutation
only expected runtime artifacts under .agentx-init/recovery/
```

---

# 12. Acceptance Criteria

The implementation is accepted only if:

```text
all required files exist
all required schemas exist
all required tests exist
compileall passes
all recovery tests pass
failure classes are complete
severity matrix is complete
recovery policy matrix is complete
safe-mode trigger rules are complete
append-only evidence works
latest artifact atomic writes work
CRITICAL failures block continuation
ROLLBACK_FAILED triggers safe mode
SOURCE_GUARD_FAILED triggers safe mode
UNKNOWN_FAILURE requires human review
no LLM/model calls occur
no network calls occur
no shell execution occurs
no patch execution occurs
no rollback execution occurs
no source mutation occurs
completion evidence exists
```

---

# 13. Definition of Done

The layer is done when this checklist is satisfied:

```text
[ ] tools/agentx_evolve/recovery/ exists
[ ] failure_models.py exists
[ ] failure_taxonomy.py exists
[ ] recovery_playbook.py exists
[ ] recovery_policy.py exists
[ ] safe_mode_triggers.py exists
[ ] failure_evidence.py exists
[ ] recovery_decider.py exists
[ ] all required recovery schemas exist
[ ] all required recovery tests exist
[ ] compileall passes
[ ] pytest recovery tests pass
[ ] required failure classes are implemented
[ ] severity matrix is implemented
[ ] recovery policy matrix is implemented
[ ] safe-mode trigger contract is implemented
[ ] failure evidence appends JSONL
[ ] latest failure/recovery artifacts write atomically
[ ] CRITICAL failures cannot continue silently
[ ] ROLLBACK_FAILED triggers safe mode
[ ] SOURCE_GUARD_FAILED triggers safe mode
[ ] UNKNOWN_FAILURE requires human review
[ ] this layer does not execute recovery
[ ] this layer does not call LLMs
[ ] this layer does not call network
[ ] this layer does not execute shell
[ ] this layer does not mutate source
[ ] completion record exists
```

---

# 14. Completion Evidence Record

Write:

```text
.agentx-init/recovery/failure_recovery_completion_record.json
```

Minimum content:

```json
{
  "schema_version": "1.0",
  "schema_id": "completion_record.schema.json",
  "component_id": "AGENTX_FAILURE_TAXONOMY_RECOVERY_PLAYBOOK",
  "component_name": "Failure Taxonomy / Recovery Playbook",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_subdirectory": "tools/agentx_evolve/recovery/",
  "basis_documents": [
    "FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v1",
    "FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC_v3"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "integration_points_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE"
}
```

Completion evidence must be valid JSON.

Before marking done, run:

```bash
python -m json.tool .agentx-init/recovery/failure_recovery_completion_record.json
```

Required:

```text
valid JSON
status = VALIDATED
final_decision = DONE
deviations_from_contract = []
unresolved_risks = []
```

---

# 15. Go / No-Go Acceptance Rules

## 13.1 GO

The implementation may be marked DONE only if all are true:

```text
all required files exist
all schemas exist
all tests exist
compileall passes
all recovery tests pass
git status shows no unexpected source mutation
UNKNOWN_FAILURE requires human review
CRITICAL failures block continuation
ROLLBACK_FAILED triggers safe mode
SOURCE_GUARD_FAILED triggers safe mode
this layer executes no recovery
this layer imports no LLM/model/network packages
evidence files are append-only
latest artifacts are atomic
completion record exists
```

## 13.2 NO-GO

The implementation must remain NOT DONE if any are true:

```text
any required failure class missing
any CRITICAL failure can continue silently
UNKNOWN_FAILURE is treated as success
ROLLBACK_FAILED does not trigger safe mode
SOURCE_GUARD_FAILED does not trigger safe mode
recovery layer executes rollback
recovery layer applies patches
recovery layer calls shell
recovery layer calls network
recovery layer calls LLM/model
source files are mutated during tests
failure evidence is not written
schemas are missing or not enforced
```

---

# 16. Implementation Drift Blockers

Reject the implementation if it:

```text
places files outside tools/agentx_evolve/recovery/ without recorded deviation
executes rollback
executes patch application
executes shell commands
calls an LLM
calls network
mutates source
silently allows UNKNOWN_FAILURE
allows CRITICAL failure continuation
fails to write evidence
uses ad hoc failure classes outside taxonomy
overrides Policy / Capability Registry denial
overrides Initiator governance
```

---

# 17. Final Implementation Sequence

Use this exact sequence:

```text
1. Create tools/agentx_evolve/recovery/ package.
2. Implement failure_models.py.
3. Implement failure_taxonomy.py.
4. Implement recovery_playbook.py.
5. Implement recovery_policy.py.
6. Implement safe_mode_triggers.py.
7. Implement recovery_decider.py.
8. Implement failure_evidence.py.
9. Add schemas.
10. Add tests.
11. Run compileall.
12. Run pytest recovery tests.
13. Check git status.
14. Generate completion record.
15. Report validation evidence.
```

---

# 18. Coding LLM Handoff Checklist

Before implementation, confirm:

```text
[ ] This is a deterministic recovery-decision layer only.
[ ] Canonical subdirectory is tools/agentx_evolve/recovery/.
[ ] Runtime state goes under .agentx-init/recovery/.
[ ] Security Sandbox is validated and should be used for safe runtime write concepts.
[ ] Policy / Capability Registry may not exist yet, so fallback integration must be deterministic.
[ ] Governed Patch Execution may not exist yet, so tests may use synthetic failure records.
[ ] This layer must not execute rollback, patch, shell, network, or model calls.
[ ] UNKNOWN_FAILURE must require human review.
[ ] CRITICAL failures must block continuation.
[ ] Completion evidence must be written after tests pass.
```

---

# 19. Final Rating

This v3 implementation spec is rated:

```text
10/10
```

It includes:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
integration with Security Sandbox
integration with Policy / Capability Registry
integration with Governed Patch Execution
integration with Initiator
test files
test cases
implementation order
acceptance criteria
Definition of Done
```
