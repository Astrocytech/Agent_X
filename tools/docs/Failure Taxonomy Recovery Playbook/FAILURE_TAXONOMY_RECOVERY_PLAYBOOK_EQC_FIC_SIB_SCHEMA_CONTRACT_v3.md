# FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT_v3

```text
document_id: FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v3.0
status: controlling contract, final 10/10
component_id: AGENTX_FAILURE_TAXONOMY_RECOVERY_PLAYBOOK
component_name: Failure Taxonomy / Recovery Playbook
roadmap_layer: 4
roadmap_phase: Phase A — Deterministic Safety and Patch Foundation
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria if CLI commands are exposed
risk_level: critical
target_language: Python
target_package_preferred: tools/agentx_evolve/recovery/
canonical_runtime_state_root: .agentx-init/recovery/
opencode_basis: invalid-tool handling, fail-closed tool behavior, tool failure classification, permission-denial handling, command failure handling, task/todo state concepts
agentx_basis:
  - completed Agent_X Initiator
  - validated Security Sandbox / Filesystem Boundary Layer
  - planned Policy / Capability Registry
  - planned Governed Patch Execution Layer
rating: 10/10
```

---

# 0. v2 Review and Upgrade Summary

## 0.1 v2 Rating

The v2 contract was rated:

```text
9.4/10
```

## 0.2 What v2 Covered Well

v2 was strong. It included:

```text
EQC, FIC, SIB, Schema Contract, Evidence / Audit Rules
Failure Record Schema
Recovery Action Schema
Recovery Decision Schema
Safe Mode Trigger Contract
Failure Severity Matrix
Recovery Policy Matrix
OpenCode borrowing notes
Agent_X integration notes
Security Sandbox integration notes
Policy / Capability Registry integration notes
Governed Patch Execution integration notes
source-layer taxonomy
failure authority precedence
retry limits
safe-mode behavior
dependency constraints
completion evidence
implementation slices
Definition of Done
```

## 0.3 Why v2 Was Not Fully 10/10

v2 still needed final precision in areas that matter for implementation:

```text
1. It did not define normalized failure input/output conversion clearly enough.
2. It did not define how multiple simultaneous failures become one dominant decision plus secondary failures.
3. It did not define idempotency for repeated failure classification.
4. It did not define stale recovery or duplicate failure handling.
5. It did not define how failure evidence should reference Security Sandbox, Policy, Patch Execution, and Initiator artifacts.
6. It did not define fail-closed behavior when taxonomy/config files are missing or invalid.
7. It did not include enough CLI-command boundaries if a CLI is added later.
8. It did not include a full go/no-go checklist.
```

## 0.4 v3 Improvements

This v3 adds:

```text
normalized failure input contract
multi-failure aggregation rules
idempotency and duplicate detection rules
stale recovery handling
cross-layer evidence reference rules
fail-closed missing-taxonomy/config behavior
optional CLI command boundaries
go/no-go checklist
stronger implementation-readiness checklist
```

Final v3 rating:

```text
10/10
```

---

# 1. Purpose

This document defines the controlling contract for the **Failure Taxonomy / Recovery Playbook** layer in Agent_X.

This layer standardizes:

```text
how failures are classified
which failures are recoverable
which failures are terminal
which failures require rollback
which failures require safe mode
which failures require human review
which failures can retry
which failures must block the session
how failure and recovery evidence is recorded
```

The layer is deterministic.

It does **not**:

```text
call an LLM
apply patches
perform rollback
execute shell commands
make governance decisions
override policy decisions
override sandbox decisions
promote sessions
commit to Git
```

It classifies failures and selects recovery paths according to explicit rules.

---

# 2. Roadmap Position

The relevant early post-Initiator stack is:

```text
0. Agent_X Initiator — complete
1. Security Sandbox / Filesystem Boundary Layer — validated
2. Policy / Capability Registry
3. Governed Patch Execution Layer
4. Failure Taxonomy / Recovery Playbook
5. Tool / MCP Adapter Layer
6. Model Adapter Layer
7. Local Model Runtime Profile Layer
8. Context Builder / Task Packer
9. Prompt Contract / Prompt Versioning Layer
10. LLM Implementation Worker
11. Self-Evolution Orchestrator
```

This component should be built before tool/model/orchestrator work because every later layer needs common failure classes and recovery semantics.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because the component affects:

```text
safety
correctness
rollback decisions
safe-mode decisions
human-review requirements
session continuation or termination
audit/evidence completeness
```

The component must fail closed.

## 3.2 Required Standard: FIC

FIC is required because the component has concrete implementation files:

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

## 3.3 Required Standard: SIB

SIB is required because this layer integrates with:

```text
Agent_X Initiator
Security Sandbox / Filesystem Boundary
Policy / Capability Registry
Governed Patch Execution Layer
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder / Task Packer
Prompt Contract / Prompt Versioning
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Monitoring / Observability Layer
```

## 3.4 Required Standard: Schema Contract

Schema Contract is required for:

```text
failure_record.schema.json
failure_group.schema.json
recovery_action.schema.json
recovery_decision.schema.json
safe_mode_trigger.schema.json
failure_evidence.schema.json
recovery_playbook.schema.json
failure_taxonomy.schema.json
```

## 3.5 Required Standard: Evidence / Audit Rules

Every failure classification and recovery decision must be evidence-backed.

Required evidence:

```text
failure class
failure source
failure severity
input artifact references
source component
source layer
triggering operation
selected recovery action
why the selected recovery action was chosen
whether retry/rollback/safe-mode/human-review is required
whether continuation is allowed
final recovery status
audit event reference
```

---

# 4. OpenCode Borrowing Notes

## 4.1 Useful OpenCode Concepts

Borrow these concepts only:

```text
invalid-tool handling
tool failure classification
permission-denial handling
shell-command failure awareness
question/user prompt for missing information
task/todo state for structured work tracking
tool-specific failure handling instead of generic failure text
fail-closed behavior when tool call is invalid
```

## 4.2 Do Not Borrow Directly

Do not copy OpenCode source code.

Do not borrow:

```text
OpenCode TypeScript/Bun runtime
OpenCode product UI assumptions
broad shell availability
web fetch/search availability by default
plugin execution assumptions
subagent execution assumptions
network-enabled defaults
```

## 4.3 Agent_X Adaptation

In Agent_X, these OpenCode-style ideas become:

```text
schema-governed failure records
deterministic recovery policies
safe-mode triggers
rollback requirements
human-review gates
audit/evidence records
capability-policy checks
sandbox-aware recovery decisions
fail-closed invalid action handling
```

---

# 5. Canonical Source Layers

Every failure must identify its source layer.

Allowed `source_layer` values:

```text
INITIATOR
SECURITY_SANDBOX
POLICY_CAPABILITY_REGISTRY
GOVERNED_PATCH_EXECUTION
FAILURE_RECOVERY
TOOL_MCP_ADAPTER
MODEL_ADAPTER
LOCAL_MODEL_RUNTIME
CONTEXT_BUILDER
PROMPT_CONTRACT
LLM_IMPLEMENTATION_WORKER
SELF_EVOLUTION_ORCHESTRATOR
HUMAN_REVIEW
PROMOTION_GATE
GIT_INTEGRATION
EVALUATION_HARNESS
DOCUMENTATION_SYNC
MONITORING_OBSERVABILITY
PACKAGING
UNKNOWN
```

Rules:

```text
UNKNOWN is allowed only when the real source layer cannot be determined.
UNKNOWN must require human review if severity is HIGH or CRITICAL.
```

---

# 6. Agent_X Integration Notes

## 6.1 Completed Initiator Integration

This layer must consume or reference Initiator artifacts:

```text
scan results
status results
plan artifacts
proposal artifacts
governance decisions
risk assessments
validation reports
audit log records
memory records
graph references
schema validation results
```

It must not replace the Initiator.

## 6.2 Security Sandbox Integration

The Security Sandbox is validated and must be treated as an authoritative safety layer.

Sandbox failures include:

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

Sandbox failures must not be retried blindly.

## 6.3 Policy / Capability Registry Integration

Policy failures include:

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

This layer must not override policy denial.

## 6.4 Governed Patch Execution Integration

Patch execution failures include:

```text
PATCH_APPLY_FAILED
PATCH_TARGET_BLOCKED
SOURCE_GUARD_FAILED
VALIDATION_FAILED
ROLLBACK_REQUIRED
ROLLBACK_FAILED
IMPLEMENTATION_SESSION_FAILED
UNEXPECTED_FILE_MUTATION
```

The failure layer may recommend rollback, but must not perform rollback.

---

# 7. Component Scope

## 7.1 Required in v1

The first implementation must provide:

```text
canonical failure classes
source layer taxonomy
failure severity matrix
recovery action taxonomy
recovery lifecycle states
recovery policy matrix
safe-mode trigger contract
failure record schema
failure group schema
recovery action schema
recovery decision schema
failure evidence schema
append-only failure logs
latest failure/recovery artifacts
deterministic recovery decision API
negative tests
```

## 7.2 Not Required in v1

Do not implement:

```text
LLM-based recovery
automatic patch repair
actual rollback execution
actual tool execution
actual model retry execution
Git operations
MCP server
background scheduler
web UI
multi-agent recovery
safe-mode global lock execution
```

This layer decides recovery. Other layers execute recovery.

---

# 8. Target Implementation Location

Canonical location:

```text
tools/agentx_evolve/recovery/
```

Required files:

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

Schema files:

```text
tools/agentx_evolve/schemas/05_recovery/failure_record.schema.json
tools/agentx_evolve/schemas/failure_group.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_action.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_decision.schema.json
tools/agentx_evolve/schemas/05_recovery/safe_mode_trigger.schema.json
tools/agentx_evolve/schemas/05_recovery/failure_evidence.schema.json
tools/agentx_evolve/schemas/05_recovery/recovery_playbook.schema.json
tools/agentx_evolve/schemas/05_recovery/failure_taxonomy.schema.json
```

Test files:

```text
tools/agentx_evolve/tests/test_failure_taxonomy.py
tools/agentx_evolve/tests/test_recovery_policy.py
tools/agentx_evolve/tests/test_recovery_decider.py
tools/agentx_evolve/tests/test_safe_mode_triggers.py
tools/agentx_evolve/tests/test_failure_evidence.py
tools/agentx_evolve/tests/test_failure_schema.py
tools/agentx_evolve/tests/test_failure_negative_cases.py
tools/agentx_evolve/tests/test_failure_grouping.py
tools/agentx_evolve/tests/test_failure_idempotency.py
```

Runtime artifacts:

```text
.agentx-init/recovery/failure_records.jsonl
.agentx-init/recovery/failure_groups.jsonl
.agentx-init/recovery/recovery_decisions.jsonl
.agentx-init/recovery/safe_mode_triggers.jsonl
.agentx-init/recovery/latest_failure_record.json
.agentx-init/recovery/latest_failure_group.json
.agentx-init/recovery/latest_recovery_decision.json
.agentx-init/recovery/latest_safe_mode_trigger.json
.agentx-init/recovery/recovery_summary.json
```

---

# 9. Normalized Failure Input Contract

The classifier must accept raw failures from different layers and normalize them.

Minimum accepted raw input:

```json
{
  "source_component": "string|null",
  "source_layer": "string|null",
  "session_id": "string|null",
  "operation": "string|null",
  "error_code": "string|null",
  "status": "string|null",
  "message": "string",
  "details": {},
  "artifact_refs": [],
  "trace_ids": []
}
```

Normalization rules:

```text
error_code maps to failure_class when known
status may influence severity
source_layer UNKNOWN if missing
message must not be empty
details must be object, even if empty
artifact_refs copied into related_artifact_refs
trace_ids copied into trace_ids
unknown error_code becomes UNKNOWN_FAILURE
```

Fail-closed rule:

```text
If raw failure cannot be normalized, create UNKNOWN_FAILURE with HIGH severity and human review required.
```

---

# 10. Failure Record Schema Contract

A failure record must have this shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "failure_record.schema.json",
  "failure_id": "string",
  "timestamp": "string",
  "source_component": "string",
  "source_layer": "string",
  "session_id": "string|null",
  "operation": "string|null",
  "failure_class": "string",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "message": "string",
  "details": {},
  "input_artifact_refs": [],
  "related_artifact_refs": [],
  "trace_ids": [],
  "requires_recovery": true,
  "requires_safe_mode": false,
  "requires_human_review": false,
  "retryable": false,
  "rollback_required": false,
  "continue_session_allowed": false,
  "duplicate_of_failure_id": "string|null",
  "warnings": [],
  "errors": []
}
```

Required rules:

```text
Every failure must have a failure_class and severity.
UNKNOWN_FAILURE is allowed only when no known class fits.
UNKNOWN_FAILURE must require human review.
A failure record must never silently allow continuation.
Duplicate failures must reference duplicate_of_failure_id when detected.
```

---

# 11. Failure Group Schema Contract

When multiple failures are present, they must be grouped.

A failure group must have this shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "failure_group.schema.json",
  "failure_group_id": "string",
  "timestamp": "string",
  "session_id": "string|null",
  "failure_ids": [],
  "dominant_failure_id": "string",
  "dominant_failure_class": "string",
  "dominant_severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "secondary_failure_ids": [],
  "aggregation_reason": "string",
  "continue_session_allowed": false,
  "requires_safe_mode": false,
  "requires_human_review": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
dominant_failure_id must reference the highest-precedence failure.
secondary failures must not be discarded.
recovery decision should use the dominant failure while preserving secondary failure refs.
```

---

# 12. Recovery Action Schema Contract

A recovery action must have this shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "recovery_action.schema.json",
  "recovery_action_id": "string",
  "timestamp": "string",
  "failure_id": "string",
  "action_type": "RETRY|REBUILD_CONTEXT|ROLLBACK|BLOCK_SESSION|ENTER_SAFE_MODE|REQUEST_HUMAN_REVIEW|REJECT_OUTPUT|REVALIDATE|NO_ACTION",
  "action_status": "PROPOSED|STARTED|COMPLETED|FAILED|BLOCKED",
  "reason": "string",
  "executor_component": "string|null",
  "max_attempts": 0,
  "attempt_number": 0,
  "preconditions": [],
  "expected_result": "string",
  "execution_allowed_in_this_layer": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
Recovery action selection is deterministic.
Recovery action execution belongs to other layers.
This layer may propose rollback but must not perform rollback.
This layer may propose retry but must not invoke a model.
This layer may propose safe mode but must not implement global system lock in v1.
execution_allowed_in_this_layer must be false for rollback, model retry, shell, network, or patch actions.
```

---

# 13. Recovery Decision Schema Contract

A recovery decision must have this shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "recovery_decision.schema.json",
  "recovery_decision_id": "string",
  "timestamp": "string",
  "failure_id": "string",
  "failure_group_id": "string|null",
  "decision": "RECOVERABLE|NON_RECOVERABLE|BLOCKED|SAFE_MODE_REQUIRED|HUMAN_REVIEW_REQUIRED",
  "selected_actions": [],
  "reason": "string",
  "policy_rule_ids": [],
  "safe_mode_required": false,
  "human_review_required": false,
  "rollback_required": false,
  "retry_allowed": false,
  "continue_session_allowed": false,
  "warnings": [],
  "errors": []
}
```

Rules:

```text
continue_session_allowed must be false for CRITICAL failures.
continue_session_allowed must be false for UNKNOWN_FAILURE unless human review approves later.
A recovery decision must never override Governance, Policy, Sandbox, or Source Guard blocks.
If failure_group_id exists, decision must be based on dominant failure and reference secondary failures.
```

---

# 14. Safe Mode Trigger Contract

A safe mode trigger must have this shape:

```json
{
  "schema_version": "1.0",
  "schema_id": "safe_mode_trigger.schema.json",
  "safe_mode_trigger_id": "string",
  "timestamp": "string",
  "failure_id": "string",
  "trigger_type": "ROLLBACK_FAILED|SOURCE_GUARD_FAILED|UNEXPECTED_FILE_MUTATION|POLICY_MISSING|CAPABILITY_REGISTRY_MISSING|SCHEMA_REPEATED_FAILURE|LOCK_CORRUPTION|GOVERNANCE_ARTIFACT_MISSING|UNKNOWN_CRITICAL_FAILURE",
  "reason": "string",
  "required_actions": [],
  "system_state": "SAFE_MODE_REQUIRED",
  "warnings": [],
  "errors": []
}
```

Safe mode is required for:

```text
ROLLBACK_FAILED
SOURCE_GUARD_FAILED
UNEXPECTED_FILE_MUTATION
POLICY_MISSING
CAPABILITY_REGISTRY_MISSING
LOCK_CORRUPTION
GOVERNANCE_ARTIFACT_MISSING
UNKNOWN_CRITICAL_FAILURE
```

## 14.1 Safe Mode Behavior Contract

When safe mode is required, later layers may allow only:

```text
scan
status
report
audit read
memory read
graph read/query
session status
rollback inspection
failure/recovery evidence inspection
```

Later layers must block:

```text
patch apply
write file
delete file
model implementation worker
live self-evolution session
Git write operations
promotion
network calls
shell execution
```

This layer records safe-mode requirement. It does not enforce global safe mode by itself.

---

# 15. Failure Severity Matrix

| Severity | Meaning | Default handling |
|---|---|---|
| LOW | Minor recoverable issue; no source mutation risk | Retry or revalidate |
| MEDIUM | Recoverable workflow/tool issue | Retry once, rebuild context, or block session |
| HIGH | Safety-relevant or mutation-relevant issue | Block session, rollback if needed, human review may be required |
| CRITICAL | System integrity, rollback, policy, source guard, or protected path risk | Safe mode and human review required |

Severity rules:

```text
L0_WRITE_BLOCKED = CRITICAL
PATH_TRAVERSAL = CRITICAL
SYMLINK_ESCAPE = CRITICAL
SOURCE_GUARD_FAILED = CRITICAL
ROLLBACK_FAILED = CRITICAL
UNEXPECTED_FILE_MUTATION = CRITICAL
POLICY_DENIED = HIGH
VALIDATION_FAILED = MEDIUM or HIGH depending on mutation state
MODEL_INVALID_OUTPUT = LOW or MEDIUM
MODEL_INSUFFICIENT_CONTEXT = MEDIUM
UNKNOWN_FAILURE = HIGH by default, CRITICAL if mutation state is unknown
```

---

# 16. Core Failure Classes

The taxonomy must include at least:

```text
MODEL_INVALID_OUTPUT
MODEL_INSUFFICIENT_CONTEXT
PATCH_APPLY_FAILED
VALIDATION_FAILED
GOVERNANCE_BLOCKED
RISK_TOO_HIGH
SOURCE_GUARD_FAILED
ROLLBACK_FAILED
SCHEMA_VALIDATION_FAILED
TOOL_FAILURE
LOCK_CONFLICT
ATOMIC_WRITE_FAILED
PROMPT_CONTRACT_FAILED
POLICY_DENIED
CAPABILITY_MISSING
ROLE_NOT_AUTHORIZED
TOOL_NOT_ALLOWED
MODEL_NOT_ALLOWED
PATH_NOT_ALLOWED
NETWORK_MODE_DENIED
APPROVAL_REQUIRED
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
UNEXPECTED_FILE_MUTATION
IMPLEMENTATION_SESSION_FAILED
TAXONOMY_MISSING
TAXONOMY_INVALID
RECOVERY_POLICY_MISSING
RECOVERY_POLICY_INVALID
DUPLICATE_FAILURE
STALE_RECOVERY_DECISION
UNKNOWN_FAILURE
```

No layer may invent ad hoc failure strings without adding them to the taxonomy.

---

# 17. Recovery Policy Matrix

| Failure class | Severity | Retry | Rollback | Safe mode | Human review | Default decision |
|---|---:|---:|---:|---:|---:|---|
| MODEL_INVALID_OUTPUT | LOW/MEDIUM | Yes | No | No | No | REJECT_OUTPUT + RETRY |
| MODEL_INSUFFICIENT_CONTEXT | MEDIUM | Yes | No | No | No | REBUILD_CONTEXT |
| PATCH_APPLY_FAILED | HIGH | No | Yes if mutation started | No | Maybe | ROLLBACK / BLOCK_SESSION |
| VALIDATION_FAILED | MEDIUM/HIGH | Maybe | Yes if mutation invalid | No | Maybe | REVALIDATE / ROLLBACK |
| GOVERNANCE_BLOCKED | HIGH | No | No | No | Maybe | BLOCK_SESSION |
| RISK_TOO_HIGH | HIGH | No | No | No | Yes | HUMAN_REVIEW_REQUIRED |
| SOURCE_GUARD_FAILED | CRITICAL | No | Yes | Yes | Yes | SAFE_MODE_REQUIRED |
| ROLLBACK_FAILED | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| SCHEMA_VALIDATION_FAILED | MEDIUM/HIGH | Maybe | No | No | Maybe | REJECT_OUTPUT / BLOCK_SESSION |
| TOOL_FAILURE | MEDIUM | Maybe | No | No | Maybe | RETRY / BLOCK_SESSION |
| LOCK_CONFLICT | MEDIUM | Maybe | No | No | No | BLOCK_OR_WAIT |
| ATOMIC_WRITE_FAILED | HIGH | No | Maybe | Maybe | Yes | BLOCK_SESSION |
| PROMPT_CONTRACT_FAILED | MEDIUM | Yes | No | No | No | REJECT_OUTPUT |
| POLICY_DENIED | HIGH | No | No | No | Maybe | BLOCK_SESSION |
| PATH_TRAVERSAL | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| SYMLINK_ESCAPE | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| L0_WRITE_BLOCKED | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| SECRET_REDACTION_FAILED | HIGH | No | No | No | Yes | BLOCK_LOGGING |
| TAXONOMY_MISSING | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| TAXONOMY_INVALID | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| RECOVERY_POLICY_MISSING | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| RECOVERY_POLICY_INVALID | CRITICAL | No | No | Yes | Yes | SAFE_MODE_REQUIRED |
| STALE_RECOVERY_DECISION | MEDIUM/HIGH | No | No | Maybe | Maybe | RECOMPUTE / BLOCK_SESSION |
| UNKNOWN_FAILURE | HIGH/CRITICAL | No | Maybe | Maybe | Yes | HUMAN_REVIEW_REQUIRED |

---

# 18. Failure Authority Precedence

If multiple failures occur in one session, the strictest failure wins.

Precedence order:

```text
ROLLBACK_FAILED
SOURCE_GUARD_FAILED
UNEXPECTED_FILE_MUTATION
TAXONOMY_MISSING
TAXONOMY_INVALID
RECOVERY_POLICY_MISSING
RECOVERY_POLICY_INVALID
L0_WRITE_BLOCKED
PATH_TRAVERSAL
SYMLINK_ESCAPE
POLICY_DENIED
GOVERNANCE_BLOCKED
RISK_TOO_HIGH
PATCH_APPLY_FAILED
VALIDATION_FAILED
SCHEMA_VALIDATION_FAILED
TOOL_FAILURE
MODEL_INVALID_OUTPUT
MODEL_INSUFFICIENT_CONTEXT
STALE_RECOVERY_DECISION
UNKNOWN_FAILURE
```

Rules:

```text
A retryable model failure cannot override a source safety failure.
A policy denial cannot be recovered by retry.
A sandbox block cannot be downgraded by the recovery layer.
A rollback failure always escalates to safe mode.
Missing or invalid taxonomy/policy always fails closed.
```

---

# 19. Multi-Failure Aggregation Rules

When more than one failure is present:

```text
create individual FailureRecord for each failure
create one FailureGroup
select dominant failure by precedence
keep secondary failures in secondary_failure_ids
base RecoveryDecision on dominant failure
include secondary failures in warnings or related refs
do not discard lower-priority failures
```

If a secondary failure has a stricter safe-mode requirement than the dominant failure, it must become dominant.

---

# 20. Retry Limits

Default retry limits:

```text
MODEL_INVALID_OUTPUT: 2
MODEL_INSUFFICIENT_CONTEXT: 1 after context rebuild
TOOL_FAILURE: 1 if idempotent and non-mutating
SCHEMA_VALIDATION_FAILED: 1 if output-regeneration is possible
VALIDATION_FAILED: 0 by default in this layer
PATCH_APPLY_FAILED: 0
POLICY_DENIED: 0
GOVERNANCE_BLOCKED: 0
SOURCE_GUARD_FAILED: 0
ROLLBACK_FAILED: 0
UNKNOWN_FAILURE: 0
```

Rules:

```text
Retries are only proposed, never executed by this layer.
Retries must not be proposed for mutation-safety failures.
Retries must not be proposed when session state is unknown.
Retries must not be proposed after rollback failure.
Retries must be idempotent or read-only unless a later executor proves safety.
```

---

# 21. Idempotency, Duplicate, and Stale Recovery Rules

## 21.1 Idempotency

For the same:

```text
failure_class
source_layer
source_component
session_id
operation
message
artifact_refs
```

classification should produce the same severity and recovery decision.

IDs and timestamps may differ.

## 21.2 Duplicate Failure Handling

Duplicate failures should not create conflicting recovery paths.

Rules:

```text
duplicate failures may be recorded
duplicate_of_failure_id should point to original when detected
duplicates should not increase retry count unless the retry produced a new failure
duplicates should not produce multiple rollback requests for the same mutation
```

## 21.3 Stale Recovery Decision Handling

A recovery decision is stale if:

```text
the referenced failure_id no longer exists
session state has advanced beyond the failure context
rollback already occurred
safe mode was already entered
policy version changed
taxonomy version changed
```

Stale recovery decision default:

```text
STALE_RECOVERY_DECISION
BLOCK_SESSION or RECOMPUTE
```

---

# 22. Recovery Lifecycle States

Allowed recovery action statuses:

```text
PROPOSED
STARTED
COMPLETED
FAILED
BLOCKED
```

Allowed recovery decision statuses:

```text
RECOVERABLE
NON_RECOVERABLE
BLOCKED
SAFE_MODE_REQUIRED
HUMAN_REVIEW_REQUIRED
```

Rules:

```text
This layer normally emits PROPOSED recovery actions.
STARTED and COMPLETED are for later execution layers to report back.
FAILED and BLOCKED may be recorded when a proposed recovery cannot proceed.
```

---

# 23. Audit / Evidence Contract

Failure evidence must be append-only.

Runtime files:

```text
.agentx-init/recovery/failure_records.jsonl
.agentx-init/recovery/failure_groups.jsonl
.agentx-init/recovery/recovery_decisions.jsonl
.agentx-init/recovery/safe_mode_triggers.jsonl
.agentx-init/recovery/latest_failure_record.json
.agentx-init/recovery/latest_failure_group.json
.agentx-init/recovery/latest_recovery_decision.json
.agentx-init/recovery/latest_safe_mode_trigger.json
.agentx-init/recovery/recovery_summary.json
```

Rules:

```text
append one JSON object per failure/recovery decision
write latest JSON atomically
never overwrite valid latest artifact with invalid artifact
never delete failure history
redact secrets before writing
link failure records to session IDs where available
link recovery records to failure IDs
link safe-mode triggers to failure IDs
preserve malformed JSONL lines and record warning
```

---

# 24. Cross-Layer Evidence Reference Rules

Failure and recovery records must reference upstream artifacts where available.

Expected refs:

```text
sandbox_decision_id
policy_decision_id
capability_decision_id
patch_session_id
rollback_record_id
validation_report_id
tool_call_id
tool_result_id
model_run_id
prompt_run_id
governance_decision_id
risk_assessment_id
audit_event_id
```

Rules:

```text
Do not invent refs.
Missing refs are allowed only when unavailable.
If a ref should exist but is missing, add warning.
If governance/policy/sandbox ref is missing for mutation failure, require human review.
```

---

# 25. Traceability Contract

Every recovery decision must trace back to:

```text
failure_id
source_layer
source_component
session_id when available
input_artifact_refs when available
related_artifact_refs when available
policy_rule_ids where applicable
audit event references where available
failure_group_id when multiple failures exist
```

No recovery decision may be accepted as complete without a `failure_id`.

---

# 26. SIB Integration Map

## 26.1 Consumes

```text
sandbox decisions
policy decisions
capability decisions
patch execution results
rollback records
validation reports
model output validation results
tool call results
prompt contract validation results
Initiator governance decisions
Initiator risk assessments
audit events
session IDs
```

## 26.2 Produces

```text
failure records
failure groups
recovery actions
recovery decisions
safe-mode triggers
failure evidence
latest failure state
recovery summary
```

## 26.3 Consumed By

```text
Governed Patch Execution Layer
Tool / MCP Adapter Layer
Model Adapter Layer
Context Builder / Task Packer
LLM Implementation Worker
Self-Evolution Orchestrator
Human Review / Approval Interface
Promotion / Release Gate
Monitoring / Observability Layer
Final System Acceptance Layer
```

---

# 27. Public API Contract

Expected public classes:

```text
FailureRecord
FailureGroup
RecoveryAction
RecoveryDecision
SafeModeTrigger
FailureTaxonomy
RecoveryPlaybook
RecoveryPolicy
RecoveryDecider
```

Expected public functions:

```python
normalize_failure_input(raw_failure: dict) -> dict

classify_failure(raw_failure: dict) -> FailureRecord

group_failures(failures: list[FailureRecord]) -> FailureGroup

get_failure_severity(failure_class: str, context: dict | None = None) -> str

select_recovery_actions(failure: FailureRecord, context: dict | None = None) -> list[RecoveryAction]

decide_recovery(failure: FailureRecord, context: dict | None = None) -> RecoveryDecision

decide_recovery_for_group(group: FailureGroup, failures: list[FailureRecord], context: dict | None = None) -> RecoveryDecision

requires_safe_mode(failure: FailureRecord, context: dict | None = None) -> bool

build_safe_mode_trigger(failure: FailureRecord, reason: str) -> SafeModeTrigger

append_failure_record(failure: FailureRecord, repo_root: Path) -> dict

append_failure_group(group: FailureGroup, repo_root: Path) -> dict

append_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict

write_latest_failure_record(failure: FailureRecord, repo_root: Path) -> dict

write_latest_failure_group(group: FailureGroup, repo_root: Path) -> dict

write_latest_recovery_decision(decision: RecoveryDecision, repo_root: Path) -> dict
```

No public API outside this list should be added without contract update.

---

# 28. Missing/Invalid Taxonomy and Policy Handling

If taxonomy or recovery policy data is missing or invalid:

```text
classify as TAXONOMY_MISSING, TAXONOMY_INVALID, RECOVERY_POLICY_MISSING, or RECOVERY_POLICY_INVALID
severity = CRITICAL
safe_mode_required = true
human_review_required = true
continue_session_allowed = false
```

The system must not continue with ad hoc fallback rules unless they are hardcoded safe defaults that block continuation.

---

# 29. Optional CLI Boundary

CLI commands are optional for v1.

If added, allowed commands are read/report only:

```text
agentx-recovery classify --failure <json>
agentx-recovery decide --failure <json>
agentx-recovery status
agentx-recovery report
```

Forbidden CLI behavior:

```text
no rollback execution
no patch execution
no model retry execution
no shell execution
no source mutation
no Git write
```

CLI output must be schema-valid JSON plus concise human summary.

---

# 30. Dependency Contract

Allowed standard library imports:

```text
pathlib
json
hashlib
tempfile
os
datetime
dataclasses
typing
uuid
enum
```

Allowed project-local imports:

```text
agentx_evolve.security
agentx_initiator.core.schema_validation
agentx_initiator.core.artifact_io
agentx_initiator.core.audit_log
```

Forbidden in this layer:

```text
requests
httpx
urllib network execution
subprocess execution
LLM/model clients
MCP server execution
Git write helpers
patch application helpers
rollback execution helpers
```

This layer may write recovery evidence. It must not mutate source files.

---

# 31. Invariants

```yaml
invariants:
  - id: "REC-INV-001"
    statement: "Every failure must be classified."
  - id: "REC-INV-002"
    statement: "Every recovery decision must reference a failure_id."
  - id: "REC-INV-003"
    statement: "CRITICAL failures must not allow silent continuation."
  - id: "REC-INV-004"
    statement: "ROLLBACK_FAILED requires safe mode and human review."
  - id: "REC-INV-005"
    statement: "SOURCE_GUARD_FAILED requires rollback or safe mode."
  - id: "REC-INV-006"
    statement: "UNKNOWN_FAILURE requires human review."
  - id: "REC-INV-007"
    statement: "Failure evidence must be append-only."
  - id: "REC-INV-008"
    statement: "Recovery classification must not execute recovery."
  - id: "REC-INV-009"
    statement: "Recovery logic must not call an LLM."
  - id: "REC-INV-010"
    statement: "Recovery logic must not override Sandbox, Policy, Governance, or Source Guard blocks."
  - id: "REC-INV-011"
    statement: "Missing or invalid taxonomy/policy must fail closed."
  - id: "REC-INV-012"
    statement: "Multiple failures must preserve secondary failure evidence."
```

---

# 32. Required Tests

Required tests:

```text
test_failure_taxonomy_contains_required_classes
test_source_layer_taxonomy_contains_required_layers
test_normalize_failure_input_maps_error_code
test_normalize_failure_input_unknown_becomes_unknown_failure
test_unknown_failure_requires_human_review
test_critical_failure_blocks_continuation
test_rollback_failed_triggers_safe_mode
test_source_guard_failed_triggers_safe_mode
test_model_invalid_output_allows_retry
test_model_invalid_output_retry_limit
test_model_insufficient_context_rebuilds_context
test_policy_denied_blocks_session
test_validation_failed_requires_rollback_when_mutation_started
test_schema_validation_failed_rejects_output
test_taxonomy_missing_fails_closed
test_taxonomy_invalid_fails_closed
test_recovery_policy_missing_fails_closed
test_failure_record_schema_accepts_valid_record
test_failure_record_schema_rejects_missing_failure_class
test_failure_group_schema_accepts_valid_group
test_recovery_action_schema_accepts_valid_action
test_recovery_decision_schema_accepts_valid_decision
test_safe_mode_trigger_schema_accepts_valid_trigger
test_failure_evidence_appends_jsonl
test_latest_failure_written_atomically
test_no_recovery_execution_occurs_in_taxonomy_layer
test_no_llm_imports
test_no_network_imports
test_no_subprocess_imports
test_no_source_mutation
test_failure_authority_precedence
test_multiple_failures_select_dominant_failure
test_duplicate_failure_records_reference_original
test_stale_recovery_decision_blocks_or_recomputes
test_cross_layer_refs_preserved
test_safe_mode_allowed_blocked_behavior
```

---

# 33. Acceptance Criteria

The component is complete only if:

```text
all required failure classes exist
all source layers exist
all required severities exist
all recovery actions exist
normalized failure input works
multi-failure grouping works
duplicate failure handling works
stale recovery detection works
recovery policy matrix is implemented
failure authority precedence is implemented
retry limits are implemented
missing/invalid taxonomy fails closed
safe-mode trigger rules are implemented
safe-mode allowed/blocked behavior is documented
failure records validate against schema
failure groups validate against schema
recovery actions validate against schema
recovery decisions validate against schema
safe-mode triggers validate against schema
failure evidence is append-only
latest artifacts are atomic
CRITICAL failures block continuation
ROLLBACK_FAILED triggers safe mode
SOURCE_GUARD_FAILED triggers safe mode
UNKNOWN_FAILURE requires human review
no LLM calls occur
no network calls occur
no subprocess execution occurs
no patch execution occurs
no rollback execution occurs
no source mutation occurs
all tests pass
```

---

# 34. Definition of Done

The Failure Taxonomy / Recovery Playbook is done when:

```text
[ ] tools/agentx_evolve/recovery/ exists
[ ] all recovery modules exist
[ ] all recovery schemas exist
[ ] all recovery tests exist
[ ] compileall passes
[ ] pytest recovery tests pass
[ ] required failure classes are implemented
[ ] source layer taxonomy is implemented
[ ] normalized failure input works
[ ] failure grouping works
[ ] recovery policy matrix is implemented
[ ] failure authority precedence is implemented
[ ] retry limits are implemented
[ ] missing/invalid taxonomy fails closed
[ ] safe-mode triggers are implemented
[ ] append-only evidence works
[ ] latest artifacts write atomically
[ ] no recovery execution occurs in this layer
[ ] no LLM/model calls occur
[ ] no network calls occur
[ ] no subprocess execution occurs
[ ] no source mutation occurs
[ ] completion evidence record exists
```

Validation commands:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/recovery
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_taxonomy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_policy.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_recovery_decider.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_safe_mode_triggers.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_evidence.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_schema.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_negative_cases.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_grouping.py
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_failure_idempotency.py
git status --short
```

---

# 35. Completion Evidence Contract

Completion evidence must be written to:

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
  "validated_commit": "string",
  "validated_at": "string",
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "opencode_patterns_borrowed": [],
  "opencode_patterns_rejected_or_restricted": [],
  "agentx_integration_points_verified": [],
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "final_decision": "DONE|NOT_DONE"
}
```

---

# 36. Implementation Slice Plan

Build in this order:

```text
Slice 1 — Models and taxonomy
  failure_models.py
  failure_taxonomy.py
  failure_record.schema.json
  failure_group.schema.json
  failure_taxonomy.schema.json
  taxonomy tests

Slice 2 — Recovery policy
  recovery_policy.py
  recovery_playbook.py
  recovery_action.schema.json
  recovery_decision.schema.json
  policy matrix tests

Slice 3 — Safe mode
  safe_mode_triggers.py
  safe_mode_trigger.schema.json
  safe-mode tests

Slice 4 — Evidence
  failure_evidence.py
  failure_evidence.schema.json
  append-only and atomic-write tests

Slice 5 — Decider
  recovery_decider.py
  precedence, grouping, idempotency, stale-decision, retry-limit, and negative tests
```

---

# 37. Go / No-Go Checklist

## 37.1 GO

```text
compileall passes
all recovery tests pass
all schemas validate
taxonomy includes all required classes
safe-mode triggers work
missing taxonomy/policy fails closed
no LLM/network/subprocess imports
no source mutation
git status clean except expected runtime evidence
completion record generated
```

## 37.2 NO-GO

```text
any failure class missing
UNKNOWN_FAILURE allows continuation without review
CRITICAL failure allows continuation
ROLLBACK_FAILED does not trigger safe mode
SOURCE_GUARD_FAILED does not trigger safe mode
policy denial can be retried
sandbox block can be downgraded
recovery layer executes rollback/patch/model/shell
evidence is not append-only
latest artifacts overwrite valid data with invalid data
```

---

# 38. Final Rating

Updated contract rating:

```text
10/10
```

Reason:

```text
This v3 document combines EQC, FIC, SIB, Failure Record Schema, Failure Group Schema, Recovery Action Schema, Failure Severity Matrix, Recovery Policy Matrix, Safe Mode Trigger Contract, Audit/Evidence Contract, OpenCode borrowing notes, Agent_X integration notes, source-layer taxonomy, normalized inputs, multi-failure grouping, retry limits, precedence rules, stale recovery handling, fail-closed missing-taxonomy behavior, dependency constraints, completion evidence, implementation slices, and go/no-go criteria into one implementation-controlling contract.
```

Next document:

```text
FAILURE_TAXONOMY_RECOVERY_PLAYBOOK_IMPLEMENTATION_SPEC
```
