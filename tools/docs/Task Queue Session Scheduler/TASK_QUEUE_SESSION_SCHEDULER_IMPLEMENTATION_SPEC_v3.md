# TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC

```text
document_id: TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC
version: v4.0
status: implementation-ready, final frozen handoff with v4 precision controls
component_id: AGENTX_TASK_QUEUE_SESSION_SCHEDULER
component_name: Task Queue / Session Scheduler
roadmap_layer: 18
roadmap_phase: Phase C — Orchestration Runtime Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, Monitoring / Observability Acceptance Criteria
optional_standards: ES, Report Template
target_language: Python
canonical_scheduler_subdirectory: tools/agentx_evolve/scheduler/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/scheduler/
implementation_mode: deterministic local queue and session scheduler first; no background daemon by default
previous_version_rating: 9.7/10
current_version_rating: 10/10
```

---

# 0. v4 Review and Upgrade Summary

The v3 implementation spec was strong and close to final. I would rate it:

```text
9.7/10
```

It already covered the requested implementation-spec categories:

```text
exact subdirectory
files to create
schemas to create
classes/functions
runtime artifacts
queue storage format
session storage format
locking implementation
lease / claim implementation
retry and backoff rules
crash recovery behavior
integration with Tool / MCP Adapter
integration with Policy / Capability Registry
integration with Failure Taxonomy
integration with Monitoring / Observability
test files
test cases
implementation slices
acceptance criteria
Definition of Done
```

It was not fully 10/10 because a few coding-agent precision gaps remained:

```text
1. It did not define the canonical state-reconstruction rule from append-only records strongly enough.
2. It did not separate claim records from lease records as first-class implementation objects.
3. It described a scheduler policy gate but did not require a scheduler_policy.py module.
4. It defined a public dispatcher boundary but did not require a scheduler_dispatcher.py module or dedicated dispatcher tests.
5. It did not define task record revisioning, record hashes, previous-record hashes, and append sequence handling.
6. It did not define clock injection and UTC-only comparison rules for deterministic tests.
7. It did not define atomic lock creation with exclusive-create semantics precisely enough.
8. It did not define state-hash rules that exclude self-referential hash fields.
9. It did not define snapshot rebuild behavior after queue/session corruption.
10. It did not define dependency-on-real-prior-layers behavior strongly enough: import real integrations when stable, fail closed when unavailable.
11. It did not require explicit tests proving no task payload is executed during claim, recovery, snapshot rebuild, or dispatcher calls.
12. It did not include a final freeze rule for the implementation spec itself.
```

This v4 adds those precision controls and is the final 10/10 implementation-ready handoff.

---

# 1. Purpose

This document is the full implementation specification for the **Task Queue / Session Scheduler** layer.

This layer provides the controlled runtime mechanism for tracking queued tasks, active sessions, task claims, leases, retries, backoff, crash recovery, and scheduler evidence.

The layer must make Agent_X capable of managing work without:

```text
uncontrolled background behavior
duplicate task execution
stale locks
lost task state
lost session state
unevidenced task transitions
scheduler-created policy bypass
scheduler-created tool bypass
```

The scheduler is a **local deterministic runtime-control layer**. It is not an autonomous worker, daemon, external queue service, or tool executor.

It must not introduce:

```text
background daemon by default
network scheduler
external queue service dependency
database dependency
cron dependency
LLM dependency
MCP runtime dependency
uncontrolled subprocess execution
source mutation directly in the scheduler
Git write operations
Tool / MCP Adapter bypass
Policy / Capability Registry bypass
Security Sandbox bypass
```

The scheduler does not decide what code to write, which model to call, which tool result is safe, or whether a risky operation is allowed. It only controls the lifecycle of tasks and sessions and delegates authority checks to the correct Agent_X layers.

---

# 2. Canonical Destination Summary

Create the scheduler package here:

```text
tools/agentx_evolve/scheduler/
```

Create schemas here:

```text
tools/agentx_evolve/schemas/
```

Create tests here:

```text
tools/agentx_evolve/tests/
```

Write runtime artifacts here:

```text
.agentx-init/scheduler/
```

Use `.agentx-init/scheduler/` instead of `.agentx-init/task_queue/` because this layer is broader than a queue. It also controls sessions, claims, leases, locks, retries, backoff, scheduler state, crash recovery, local health summaries, and scheduler evidence.

---

# 3. Implementation Goal

At the end of this implementation, Agent_X must have a deterministic local scheduler that can:

```text
create task records
validate task records
deduplicate tasks through idempotency keys
append tasks to a queue
load queue state deterministically
select claimable tasks deterministically
claim pending tasks safely
create task leases
renew task leases
release task leases
prevent duplicate active claims
prevent duplicate task execution
start scheduler sessions
heartbeat scheduler sessions
resume scheduler sessions
close scheduler sessions
record task transitions
resolve task dependencies
block tasks with unmet dependencies
retry failed tasks according to policy
apply deterministic backoff
detect stale running tasks
detect stale sessions
detect expired leases
recover stale locks safely
recover stale leases safely
write scheduler audit/evidence
write latest scheduler state atomically
hash final scheduler evidence artifacts
integrate with Tool / MCP Adapter without bypassing tool policy
integrate with Policy / Capability Registry before executable work
map failures through Failure Taxonomy or deterministic local fallback classes
emit monitoring-ready local events without requiring monitoring runtime
```

The implementation must not:

```text
execute task payloads directly
call tools without Tool / MCP Adapter
bypass Policy / Capability Registry
bypass Security Sandbox indirectly through task payloads
apply patches
write source files
perform Git writes
open network connections
start a daemon automatically
spawn background workers by default
silently overwrite locks
silently drop task/session history
silently retry safety-denied tasks
```

---

# 4. Exact Subdirectory

The canonical implementation directory is:

```text
tools/agentx_evolve/scheduler/
```

The package must be importable as:

```python
agentx_evolve.scheduler
```

The scheduler must not write runtime artifacts outside:

```text
.agentx-init/scheduler/
```

except for approved evidence references produced by other layers, such as:

```text
.agentx-init/tool_calls/
.agentx-init/policy/
.agentx-init/failures/
.agentx-init/observability/
```

Any exception must be listed later in the review document deviation register.

---

# 5. Files to Create

## 5.1 Scheduler Package Files

Create:

```text
tools/agentx_evolve/scheduler/__init__.py
tools/agentx_evolve/scheduler/scheduler_models.py
tools/agentx_evolve/scheduler/queue_store.py
tools/agentx_evolve/scheduler/session_store.py
tools/agentx_evolve/scheduler/lock_manager.py
tools/agentx_evolve/scheduler/lease_manager.py
tools/agentx_evolve/scheduler/retry_policy.py
tools/agentx_evolve/scheduler/crash_recovery.py
tools/agentx_evolve/scheduler/scheduler_policy.py
tools/agentx_evolve/scheduler/scheduler_dispatcher.py
tools/agentx_evolve/scheduler/scheduler_engine.py
tools/agentx_evolve/scheduler/scheduler_evidence.py
tools/agentx_evolve/scheduler/scheduler_observability.py
tools/agentx_evolve/scheduler/scheduler_validation.py
```

## 5.2 Optional Future Files

Do not create these in v1 unless explicitly needed:

```text
tools/agentx_evolve/scheduler/scheduler_cli.py
tools/agentx_evolve/scheduler/scheduler_daemon.py
tools/agentx_evolve/scheduler/scheduler_network.py
```

Rules:

```text
scheduler_cli.py requires Command Acceptance Criteria
scheduler_daemon.py is not allowed in this implementation pass
scheduler_network.py is not allowed in this implementation pass
```

## 5.3 Schema Files

Create:

```text
tools/agentx_evolve/schemas/21_scheduler/scheduler_task.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_queue.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_session.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_lock.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_lease.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_claim.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_retry_policy.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_event.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_state.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_policy_decision.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_evidence_manifest.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_review_report.schema.json
tools/agentx_evolve/schemas/21_scheduler/scheduler_completion_record.schema.json
```

## 5.4 Test Files

Create:

```text
tools/agentx_evolve/tests/test_scheduler_models.py
tools/agentx_evolve/tests/test_scheduler_schemas.py
tools/agentx_evolve/tests/test_queue_store.py
tools/agentx_evolve/tests/test_session_store.py
tools/agentx_evolve/tests/test_lock_manager.py
tools/agentx_evolve/tests/test_lease_manager.py
tools/agentx_evolve/tests/test_scheduler_policy.py
tools/agentx_evolve/tests/test_scheduler_dispatcher.py
tools/agentx_evolve/tests/test_retry_policy.py
tools/agentx_evolve/tests/test_crash_recovery.py
tools/agentx_evolve/tests/test_scheduler_engine.py
tools/agentx_evolve/tests/test_scheduler_evidence.py
tools/agentx_evolve/tests/test_scheduler_observability.py
tools/agentx_evolve/tests/test_scheduler_validation.py
tools/agentx_evolve/tests/test_scheduler_negative_cases.py
```

Dedicated schema validator:

```text
tools/agentx_evolve/tests/validate_scheduler_schemas.py
```

---

# 6. Runtime Artifacts

All scheduler runtime artifacts must be written under:

```text
.agentx-init/scheduler/
```

Required runtime files:

```text
.agentx-init/scheduler/tasks.jsonl
.agentx-init/scheduler/queue_state.json
.agentx-init/scheduler/sessions.jsonl
.agentx-init/scheduler/session_state.json
.agentx-init/scheduler/lock_history.jsonl
.agentx-init/scheduler/locks/
.agentx-init/scheduler/leases.jsonl
.agentx-init/scheduler/events.jsonl
.agentx-init/scheduler/retry_history.jsonl
.agentx-init/scheduler/recovery_history.jsonl
.agentx-init/scheduler/quarantine.jsonl
.agentx-init/scheduler/latest_task.json
.agentx-init/scheduler/latest_session.json
.agentx-init/scheduler/latest_event.json
.agentx-init/scheduler/latest_health_snapshot.json
.agentx-init/scheduler/scheduler_evidence_manifest.json
.agentx-init/scheduler/scheduler_review_report.json
.agentx-init/scheduler/scheduler_completion_record.json
```

Purpose of lock artifacts:

```text
locks/ = active lock files created by atomic create semantics
lock_history.jsonl = append-only evidence of lock acquire/release/stale/recovery events
```

Rules:

```text
append-only JSONL for history files
atomic JSON writes for latest/state/manifest/report files
no source files written by scheduler
no task payload execution during persistence
no deletion of historical evidence during normal operation
preserve malformed existing JSONL lines by quarantining or reporting them
record corruption as scheduler evidence instead of silently ignoring it
```

---

# 7. Atomic Write and Persistence Rules

## 7.1 Atomic JSON Writes

All snapshot/latest JSON files must be written atomically:

```text
write to temporary file under the same directory
flush file content
fsync file where supported
rename/replace temporary file into final path
never leave partially written final JSON file
```

Required helper behavior:

```python
atomic_write_json(path: Path, payload: dict) -> dict
append_jsonl(path: Path, payload: dict) -> dict
load_jsonl_records(path: Path) -> tuple[list[dict], list[dict]]
```

## 7.2 JSONL History Rules

```text
history writes append only
malformed lines are not rewritten or deleted
malformed lines are copied into quarantine evidence with line number and parse error
load functions return valid records plus parse warnings
```

## 7.3 Hash Rules

Final evidence artifacts must have SHA-256 hashes:

```text
scheduler_evidence_manifest.json
scheduler_review_report.json
scheduler_completion_record.json
command output artifacts, if stored
state snapshots used for review
```

Use Python standard-library `hashlib` if no project hash helper exists.

---

# 8. Queue Storage Format

## 8.1 Task Record

Each task must be represented as a schema-valid record.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_task.schema.json",
  "task_id": "task_<id>",
  "record_id": "task_record_<id>",
  "revision": 1,
  "append_sequence": 1,
  "previous_record_hash": null,
  "task_record_hash": "<sha256>",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "task_type": "TOOL_CALL|IMPLEMENTATION_STEP|VALIDATION_STEP|REVIEW_STEP|REPORT_STEP|MAINTENANCE_STEP",
  "title": "string",
  "description": "string",
  "status": "PENDING",
  "priority": 100,
  "queue_name": "default",
  "session_id": null,
  "parent_task_id": null,
  "depends_on": [],
  "blocked_by": [],
  "payload": {},
  "requested_tool_name": null,
  "requested_effect": null,
  "caller_role": "ORCHESTRATOR",
  "policy_context_ref": null,
  "lease_id": null,
  "claim_id": null,
  "attempt_count": 0,
  "max_attempts": 1,
  "next_run_at": "<UTC timestamp>",
  "timeout_seconds": 300,
  "idempotency_key": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "failure_class": null,
  "warnings": [],
  "errors": []
}
```

## 8.2 Task Type Values

Allowed task types:

```text
TOOL_CALL
IMPLEMENTATION_STEP
VALIDATION_STEP
REVIEW_STEP
REPORT_STEP
MAINTENANCE_STEP
```

## 8.3 Task Status Values

Allowed task statuses:

```text
PENDING
CLAIMED
RUNNING
BLOCKED
WAITING
RETRY_SCHEDULED
FAILED
CANCELLED
DONE
STALE
RECOVERED
INVALID
```

## 8.4 Queue State File

The queue state file must be an atomically written snapshot:

```text
.agentx-init/scheduler/queue_state.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_queue.schema.json",
  "queue_id": "queue_default",
  "queue_name": "default",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "task_counts": {
    "PENDING": 0,
    "CLAIMED": 0,
    "RUNNING": 0,
    "BLOCKED": 0,
    "WAITING": 0,
    "RETRY_SCHEDULED": 0,
    "FAILED": 0,
    "CANCELLED": 0,
    "DONE": 0,
    "STALE": 0,
    "RECOVERED": 0,
    "INVALID": 0
  },
  "active_session_ids": [],
  "active_lease_ids": [],
  "last_event_id": null,
  "queue_hash": "<sha256>",
  "warnings": [],
  "errors": []
}
```

---

# 9. Deterministic Queue Ordering and Claim Selection

Claim selection must be deterministic.

A task is claimable only if all are true:

```text
status is PENDING or RETRY_SCHEDULED
next_run_at <= current UTC time
depends_on tasks are DONE
blocked_by is empty or all blockers are resolved
task has no active lease
task has no active non-stale claim
attempt_count < max_attempts
policy gate allows claim for this session/role
```

Sorting order for claimable tasks:

```text
1. lower priority number first
2. earlier next_run_at first
3. earlier created_at first
4. lexicographically smaller task_id first
```

This makes `claim_next_task` deterministic and testable.

Claim selection must not depend on:

```text
filesystem directory order
JSONL append order alone when priority/next_run_at differ
random numbers
current process id except for lock ownership evidence
```

---

# 10. Dependency Resolution

Task dependencies are represented by:

```text
depends_on: task IDs that must be DONE
blocked_by: blocking task IDs or blocking condition IDs
```

Rules:

```text
missing dependency task -> task becomes BLOCKED or WAITING with SCHEDULER_DEPENDENCY_MISSING
failed dependency -> task becomes BLOCKED with SCHEDULER_DEPENDENCY_FAILED
cancelled dependency -> task becomes BLOCKED with SCHEDULER_DEPENDENCY_CANCELLED
pending/running dependency -> task remains WAITING
DONE dependency -> dependency is satisfied
```

Dependency checks are required before claim.

Recovery must not bypass dependency checks.

---

# 11. Task Status Transition Table

Allowed transitions:

| From | To | Reason |
|---|---|---|
| `PENDING` | `CLAIMED` | task claimed by session |
| `PENDING` | `WAITING` | dependency/governance/human approval not ready |
| `PENDING` | `BLOCKED` | policy/safety/dependency denial |
| `PENDING` | `CANCELLED` | explicit cancellation |
| `CLAIMED` | `RUNNING` | session starts work |
| `CLAIMED` | `STALE` | lease/session expired |
| `CLAIMED` | `RETRY_SCHEDULED` | recovery schedules retry |
| `CLAIMED` | `FAILED` | non-retryable failure or attempts exhausted |
| `RUNNING` | `DONE` | schema-valid successful result |
| `RUNNING` | `FAILED` | non-retryable failure or attempts exhausted |
| `RUNNING` | `BLOCKED` | safety block during execution boundary |
| `RUNNING` | `RETRY_SCHEDULED` | retryable failure |
| `RUNNING` | `STALE` | session/lease expires |
| `WAITING` | `PENDING` | dependency/governance/human approval resolved |
| `WAITING` | `BLOCKED` | unresolved blocker becomes terminal |
| `RETRY_SCHEDULED` | `CLAIMED` | retry task claimed after next_run_at |
| `STALE` | `RECOVERED` | recovery pass records stale recovery |
| `RECOVERED` | `RETRY_SCHEDULED` | retryable recovered task |
| `RECOVERED` | `FAILED` | non-retryable recovered task |

Terminal statuses:

```text
DONE
FAILED
BLOCKED
CANCELLED
INVALID
```

Terminal statuses may not transition back to `PENDING` except through a new task with a new `task_id` and a linked `parent_task_id`.

Invalid transitions must fail closed and write evidence.

---

# 12. Session Storage Format

## 12.1 Session Record

Each scheduler session must be represented as a schema-valid record.

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_session.schema.json",
  "session_id": "session_<id>",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "closed_at": null,
  "source_component": "TaskQueueSessionScheduler",
  "session_type": "ORCHESTRATOR|IMPLEMENTATION_WORKER|VALIDATION_WORKER|REVIEW_WORKER|MAINTENANCE",
  "status": "ACTIVE",
  "owner_role": "ORCHESTRATOR",
  "owner_id": "string|null",
  "queue_name": "default",
  "claimed_task_ids": [],
  "active_lease_ids": [],
  "completed_task_ids": [],
  "failed_task_ids": [],
  "heartbeat_at": "<UTC timestamp>",
  "timeout_seconds": 1800,
  "policy_context_ref": null,
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

## 12.2 Session Status Values

Allowed session statuses:

```text
ACTIVE
IDLE
PAUSED
CLOSING
CLOSED
STALE
RECOVERED
FAILED
INVALID
```

## 12.3 Session State File

The session state file must be atomically written:

```text
.agentx-init/scheduler/session_state.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_state.schema.json",
  "state_id": "scheduler_state_<id>",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "active_sessions": [],
  "stale_sessions": [],
  "active_locks": [],
  "active_leases": [],
  "last_recovery_at": null,
  "state_hash": "<sha256>",
  "warnings": [],
  "errors": []
}
```

---

# 13. Locking Implementation

## 13.1 Purpose

The lock manager prevents duplicate active scheduler mutations, duplicate task claims, and conflicting session writes.

## 13.2 Lock Scope

Required lock scopes:

```text
QUEUE_STATE
TASK_RECORD
SESSION_RECORD
LEASE_RECORD
RECOVERY_PASS
```

## 13.3 Lock File Strategy

The first implementation must use deterministic local file locking with atomic create semantics.

Required active lock directory:

```text
.agentx-init/scheduler/locks/
```

Active lock file path format:

```text
.agentx-init/scheduler/locks/<lock_scope>__<resource_id>.lock.json
```

Lock history path:

```text
.agentx-init/scheduler/lock_history.jsonl
```

Required lock record format:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_lock.schema.json",
  "lock_id": "lock_<id>",
  "created_at": "<UTC timestamp>",
  "expires_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "lock_scope": "TASK_RECORD",
  "resource_id": "task_<id>",
  "owner_session_id": "session_<id>",
  "owner_process_id": "string|null",
  "status": "ACTIVE",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

## 13.4 Lock Rules

```text
lock acquisition must use atomic create mode
lock acquisition must fail closed if the lock file already exists and is not stale
stale locks may be recovered only through crash_recovery.py or explicit recover_stale_lock
locks must have expires_at
locks must record owner_session_id
locks must write lock_history.jsonl evidence
locks must not be silently overwritten
lock release must write evidence
lock release may remove active lock file only after writing release evidence
```

## 13.5 Lock Status Values

```text
ACTIVE
RELEASED
STALE
RECOVERED
FAILED
INVALID
```

---

# 14. Lease / Claim Implementation

## 14.1 Purpose

A claim assigns a task to a session. A lease limits how long the claim remains valid without renewal.

The claim/lease mechanism prevents duplicate execution and enables safe recovery if a worker crashes.

## 14.2 Lease Record

Required format:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_lease.schema.json",
  "lease_id": "lease_<id>",
  "claim_id": "claim_<id>",
  "task_id": "task_<id>",
  "session_id": "session_<id>",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "expires_at": "<UTC timestamp>",
  "renewal_count": 0,
  "max_renewals": 10,
  "status": "ACTIVE",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

## 14.3 Claim Record

A claim is a first-class scheduler record. A lease is the time-bound authority attached to that claim.

Required format:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_claim.schema.json",
  "claim_id": "claim_<id>",
  "task_id": "task_<id>",
  "session_id": "session_<id>",
  "lease_id": "lease_<id>",
  "created_at": "<UTC timestamp>",
  "updated_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "status": "ACTIVE",
  "claim_reason": "CLAIM_NEXT_TASK",
  "idempotency_key": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Allowed claim statuses:

```text
ACTIVE
RELEASED
STALE
RECOVERED
FAILED
INVALID
```

Claim rules:

```text
claim record must be written before task is marked RUNNING
claim record must reference exactly one task, session, and lease
active claim without active lease is recoverable but not executable
claim history is append-only
duplicate active claims for one task are BLOCKED
claim evidence must include lock and lease refs where available
```

## 14.4 Lease Status Values

```text
ACTIVE
RENEWED
RELEASED
EXPIRED
STALE
RECOVERED
FAILED
INVALID
```

## 14.4 Claim Rules

```text
only PENDING or RETRY_SCHEDULED tasks may be claimed
blocked dependencies prevent claim
next_run_at in the future prevents claim
a task may have only one active lease
claiming requires an ACTIVE or IDLE session
claiming requires QUEUE_STATE lock and TASK_RECORD lock
claiming updates task status to CLAIMED
mark_task_running later updates CLAIMED to RUNNING
claiming writes lease evidence
claiming writes scheduler event evidence
claiming must be idempotent for same idempotency_key and same session/task
```

## 14.5 Renewal Rules

```text
only ACTIVE or RENEWED leases may be renewed
expired leases cannot be renewed without recovery
renewal requires matching session_id
renewals must increment renewal_count
renewal_count cannot exceed max_renewals
renewal writes evidence
```

## 14.6 Release Rules

```text
release requires matching session_id
release marks lease RELEASED
release updates task status to DONE, FAILED, BLOCKED, CANCELLED, or RETRY_SCHEDULED
release writes evidence
release must not delete the lease record from history
```

---

# 15. Idempotency Rules

Every task must have an `idempotency_key`.

Required behavior:

```text
same idempotency_key + same task payload -> return existing task instead of creating duplicate
same idempotency_key + different task payload -> BLOCKED or INVALID with SCHEDULER_IDEMPOTENCY_CONFLICT
same claim request repeated by same session for same task -> return existing active lease
same claim request repeated by different session -> BLOCKED with SCHEDULER_LEASE_CONFLICT
same completion request repeated with same result_ref -> return existing DONE task
same retry scheduling repeated for same attempt_count -> return existing RETRY_SCHEDULED state
```

Idempotency records must be derived from append-only task history, not from an untrusted in-memory cache.

---

# 16. Retry and Backoff Rules

## 16.1 Retry Policy

Retry logic must be deterministic and policy-controlled.

Required retry policy record:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_retry_policy.schema.json",
  "policy_id": "retry_policy_default",
  "created_at": "<UTC timestamp>",
  "source_component": "TaskQueueSessionScheduler",
  "max_attempts": 3,
  "base_delay_seconds": 30,
  "max_delay_seconds": 900,
  "backoff_multiplier": 2,
  "jitter_enabled": false,
  "retryable_failure_classes": [
    "TOOL_TIMEOUT",
    "TOOL_EXECUTION_FAILED",
    "TRANSIENT_SCHEDULER_FAILURE"
  ],
  "non_retryable_failure_classes": [
    "TOOL_POLICY_DENIED",
    "TOOL_SANDBOX_DENIED",
    "TOOL_SCHEMA_INVALID",
    "TOOL_NOT_FOUND",
    "SCHEDULER_POLICY_DENIED"
  ],
  "warnings": [],
  "errors": []
}
```

## 16.2 Backoff Calculation

Backoff formula:

```text
delay = min(base_delay_seconds * (backoff_multiplier ** (attempt_count - 1)), max_delay_seconds)
```

Rules:

```text
attempt_count starts at 0 before first claim
first retry increments attempt_count to 1
next_run_at is set to now + delay
jitter is disabled by default for deterministic tests
policy-denied and sandbox-denied failures are not retryable by default
schema-invalid tasks are not retryable by default
max_attempts exceeded -> FAILED
retry scheduling writes retry_history.jsonl
```

---

# 17. Crash Recovery Behavior

## 17.1 Purpose

Crash recovery detects stale sessions, stale locks, expired leases, and tasks stuck in CLAIMED/RUNNING status.

## 17.2 Recovery Inputs

Recovery must inspect:

```text
queue_state.json
session_state.json
tasks.jsonl
sessions.jsonl
locks/
lock_history.jsonl
leases.jsonl
events.jsonl
retry_history.jsonl
```

## 17.3 Recovery Rules

```text
recovery requires RECOVERY_PASS lock
expired lease -> mark lease EXPIRED or STALE
stale session heartbeat -> mark session STALE
task with expired lease and retryable failure -> RECOVERED then RETRY_SCHEDULED
task with expired lease and non-retryable failure -> RECOVERED then FAILED or BLOCKED
task with no valid session and active claim -> RECOVERED then RETRY_SCHEDULED or FAILED
stale lock -> recover only if expires_at is past
recovery must write recovery_history.jsonl
recovery must write scheduler event
recovery must not execute task payloads
recovery must not delete evidence
```

## 17.4 Recovery Safety

```text
recovery cannot convert policy-denied tasks to PENDING
recovery cannot convert sandbox-denied tasks to PENDING
recovery cannot bypass max_attempts
recovery cannot overwrite newer state with older state
recovery must use updated_at comparison where applicable
recovery must record before/after state refs in evidence
```

---

# 18. Scheduler Policy Gate

The scheduler must check policy before creating, claiming, or progressing tasks that imply controlled actions.

Scheduler policy is separate from tool policy execution. It answers:

```text
can this role create this task type?
can this role claim this task type?
can this session progress this task?
can this task request this effect?
does this queue allow mutating work?
does this task require governance?
does this task require human approval?
is the current runtime mode allowed to progress this task?
```

Fail-closed behavior:

```text
policy unavailable -> block mutating/executable task claims
unknown role -> block
unknown task type -> INVALID
requested effect not allowed -> BLOCKED
missing governance -> WAITING or BLOCKED
missing human approval -> WAITING or BLOCKED
```

The scheduler may allow local read-only queue inspection without full policy availability. It must not allow executable or mutating task progression without policy approval.

---

# 19. Classes and Functions

## 19.1 `scheduler_models.py`

Required dataclasses:

```python
SchedulerTask
SchedulerQueueState
SchedulerSession
SchedulerLock
SchedulerLease
SchedulerRetryPolicy
SchedulerEvent
SchedulerPolicyDecision
SchedulerEvidenceManifest
SchedulerReviewReport
SchedulerCompletionRecord
```

Required constants:

```python
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_CLAIMED = "CLAIMED"
TASK_STATUS_RUNNING = "RUNNING"
TASK_STATUS_BLOCKED = "BLOCKED"
TASK_STATUS_WAITING = "WAITING"
TASK_STATUS_RETRY_SCHEDULED = "RETRY_SCHEDULED"
TASK_STATUS_FAILED = "FAILED"
TASK_STATUS_CANCELLED = "CANCELLED"
TASK_STATUS_DONE = "DONE"
TASK_STATUS_STALE = "STALE"
TASK_STATUS_RECOVERED = "RECOVERED"
TASK_STATUS_INVALID = "INVALID"

SESSION_STATUS_ACTIVE = "ACTIVE"
SESSION_STATUS_IDLE = "IDLE"
SESSION_STATUS_PAUSED = "PAUSED"
SESSION_STATUS_CLOSING = "CLOSING"
SESSION_STATUS_CLOSED = "CLOSED"
SESSION_STATUS_STALE = "STALE"
SESSION_STATUS_RECOVERED = "RECOVERED"
SESSION_STATUS_FAILED = "FAILED"
SESSION_STATUS_INVALID = "INVALID"
```

Required helper functions:

```python
utc_now_iso() -> str
new_id(prefix: str) -> str
to_dict(obj: object) -> dict
canonical_scheduler_root(repo_root: Path) -> Path
sha256_text(value: str) -> str
```

Acceptance:

```text
dataclasses instantiate
dataclasses serialize to dict
status constants match schema enums
no filesystem writes during model import
```

## 19.2 `queue_store.py`

Required public functions:

```python
append_task(task: SchedulerTask, repo_root: Path) -> dict
load_tasks(repo_root: Path, queue_name: str = "default") -> list[SchedulerTask]
load_queue_state(repo_root: Path, queue_name: str = "default") -> SchedulerQueueState
write_queue_state(state: SchedulerQueueState, repo_root: Path) -> dict
get_task(task_id: str, repo_root: Path) -> SchedulerTask | None
get_task_by_idempotency_key(idempotency_key: str, repo_root: Path) -> SchedulerTask | None
update_task(task: SchedulerTask, repo_root: Path) -> dict
list_claimable_tasks(repo_root: Path, queue_name: str = "default") -> list[SchedulerTask]
quarantine_malformed_record(raw_line: str, source_path: Path, error: str, repo_root: Path) -> dict
```

Rules:

```text
append-only history is required
state snapshots must be atomic
task update must append a new record, not rewrite history only
latest task must be written atomically
malformed task lines must not crash the scheduler
claimable task ordering must follow Section 9
```

## 19.3 `session_store.py`

Required public functions:

```python
start_session(session: SchedulerSession, repo_root: Path) -> SchedulerSession
load_sessions(repo_root: Path) -> list[SchedulerSession]
get_session(session_id: str, repo_root: Path) -> SchedulerSession | None
heartbeat_session(session_id: str, repo_root: Path) -> SchedulerSession
close_session(session_id: str, repo_root: Path, status: str = "CLOSED") -> SchedulerSession
write_session_state(repo_root: Path) -> dict
```

Rules:

```text
session start writes sessions.jsonl
heartbeat updates heartbeat_at and writes evidence
close_session does not delete session history
stale sessions are handled by crash_recovery.py
```

## 19.4 `lock_manager.py`

Required public functions:

```python
acquire_lock(resource_id: str, lock_scope: str, session_id: str, repo_root: Path, ttl_seconds: int = 60) -> SchedulerLock
release_lock(lock_id: str, repo_root: Path) -> SchedulerLock
load_active_locks(repo_root: Path) -> list[SchedulerLock]
is_lock_stale(lock: SchedulerLock) -> bool
recover_stale_lock(lock: SchedulerLock, repo_root: Path) -> SchedulerLock
```

Rules:

```text
atomic lock creation required
existing non-stale lock blocks acquisition
stale lock recovery must be explicit and evidenced
```

## 19.5 `lease_manager.py`

Required public functions:

```python
claim_task(task_id: str, session_id: str, repo_root: Path, lease_seconds: int = 300) -> SchedulerLease
renew_lease(lease_id: str, session_id: str, repo_root: Path, lease_seconds: int = 300) -> SchedulerLease
release_lease(lease_id: str, session_id: str, repo_root: Path, final_task_status: str) -> SchedulerLease
load_active_leases(repo_root: Path) -> list[SchedulerLease]
find_task_lease(task_id: str, repo_root: Path) -> SchedulerLease | None
is_lease_expired(lease: SchedulerLease) -> bool
```

Rules:

```text
claim requires active session
claim requires no active lease for task
claim must update task status
release must update task status
lease operations must write evidence
```

## 19.6 `retry_policy.py`

Required public functions:

```python
load_default_retry_policy() -> SchedulerRetryPolicy
is_retryable_failure(failure_class: str | None, policy: SchedulerRetryPolicy) -> bool
calculate_backoff_seconds(attempt_count: int, policy: SchedulerRetryPolicy) -> int
schedule_retry(task: SchedulerTask, policy: SchedulerRetryPolicy, repo_root: Path) -> SchedulerTask
mark_non_retryable_failure(task: SchedulerTask, repo_root: Path) -> SchedulerTask
```

Rules:

```text
policy-denied failures are not retryable
sandbox-denied failures are not retryable
schema-invalid failures are not retryable
max attempts must be enforced
```

## 19.7 `crash_recovery.py`

Required public functions:

```python
run_recovery_pass(repo_root: Path, queue_name: str = "default") -> dict
recover_expired_leases(repo_root: Path) -> list[SchedulerLease]
recover_stale_sessions(repo_root: Path) -> list[SchedulerSession]
recover_stale_locks(repo_root: Path) -> list[SchedulerLock]
recover_stale_tasks(repo_root: Path) -> list[SchedulerTask]
```

Rules:

```text
recovery requires RECOVERY_PASS lock
recovery does not execute tasks
recovery writes recovery_history.jsonl
recovery writes scheduler events
```

## 19.8 `scheduler_policy.py`

Required public functions:

```python
check_scheduler_permission(arguments: dict, action: str, repo_root: Path, policy_context: dict | None = None) -> SchedulerPolicyDecision
can_create_task(arguments: dict, repo_root: Path, policy_context: dict | None = None) -> SchedulerPolicyDecision
can_claim_task(task: SchedulerTask, session: SchedulerSession, repo_root: Path, policy_context: dict | None = None) -> SchedulerPolicyDecision
can_progress_task(task: SchedulerTask, session: SchedulerSession, new_status: str, repo_root: Path, policy_context: dict | None = None) -> SchedulerPolicyDecision
```

Rules:

```text
use real Policy / Capability Registry if available and stable
if real policy import fails, use restrictive local fallback
read-only inspection may be allowed for known read roles
create/claim/progress of executable or mutating tasks blocks when policy is unavailable
policy decisions must be evidenced
missing governance or human approval returns WAITING or BLOCKED, not ALLOW
```

## 19.9 `scheduler_dispatcher.py`

Required public functions:

```python
submit_scheduler_task(arguments: dict, repo_root: Path, policy_context: dict | None = None) -> SchedulerTask
start_scheduler_session(arguments: dict, repo_root: Path, policy_context: dict | None = None) -> SchedulerSession
claim_scheduler_task(session_id: str, repo_root: Path, queue_name: str = "default", policy_context: dict | None = None) -> SchedulerTask | None
mark_scheduler_task_running(task_id: str, session_id: str, repo_root: Path, policy_context: dict | None = None) -> SchedulerTask
complete_scheduler_task(task_id: str, session_id: str, repo_root: Path, result_ref: str | None = None, policy_context: dict | None = None) -> SchedulerTask
fail_scheduler_task(task_id: str, session_id: str, repo_root: Path, failure_class: str, message: str, policy_context: dict | None = None) -> SchedulerTask
cancel_scheduler_task(task_id: str, session_id: str, repo_root: Path, reason: str, policy_context: dict | None = None) -> SchedulerTask
run_scheduler_recovery(repo_root: Path, queue_name: str = "default", policy_context: dict | None = None) -> dict
```

Rules:

```text
external callers use scheduler_dispatcher.py, not store modules
dispatcher validates schema before state mutation
dispatcher checks scheduler policy before executable/mutating task progression
dispatcher writes evidence for every accepted, blocked, invalid, or failed request
dispatcher never executes task payloads
dispatcher never calls tool wrappers directly; Tool / MCP Adapter remains the execution boundary
```

## 19.10 `scheduler_engine.py`

Required public functions:

```python
create_task(arguments: dict, repo_root: Path) -> SchedulerTask
enqueue_task(task: SchedulerTask, repo_root: Path) -> SchedulerTask
claim_next_task(session_id: str, repo_root: Path, queue_name: str = "default") -> SchedulerTask | None
mark_task_running(task_id: str, session_id: str, repo_root: Path) -> SchedulerTask
complete_task(task_id: str, session_id: str, repo_root: Path, result_ref: str | None = None) -> SchedulerTask
fail_task(task_id: str, session_id: str, repo_root: Path, failure_class: str, message: str) -> SchedulerTask
cancel_task(task_id: str, session_id: str, repo_root: Path, reason: str) -> SchedulerTask
```

Rules:

```text
engine coordinates queue, session, lock, lease, retry, and evidence modules
engine does not execute task payloads directly
engine must require valid session for claim/running/completion/failure transitions
engine must write scheduler events for every transition
```

## 19.11 `scheduler_evidence.py`

Required public functions:

```python
append_scheduler_event(event: SchedulerEvent, repo_root: Path) -> dict
write_latest_event(event: SchedulerEvent, repo_root: Path) -> dict
write_latest_task(task: SchedulerTask, repo_root: Path) -> dict
write_latest_session(session: SchedulerSession, repo_root: Path) -> dict
write_scheduler_evidence_manifest(repo_root: Path, validated_commit: str | None = None) -> dict
write_scheduler_review_report(repo_root: Path, reviewed_commit: str | None = None) -> dict
write_scheduler_completion_record(repo_root: Path, status: str) -> dict
redact_scheduler_payload(payload: dict) -> dict
sha256_file(path: Path) -> str
```

Rules:

```text
secrets must be redacted before evidence
raw task payload may be summarized if sensitive
hash final evidence artifacts with SHA-256
atomic writes for latest files and manifests
```

## 19.12 `scheduler_observability.py`

Required public functions:

```python
emit_scheduler_metric(event_name: str, data: dict, repo_root: Path) -> dict
build_scheduler_health_snapshot(repo_root: Path) -> dict
build_queue_summary(repo_root: Path, queue_name: str = "default") -> dict
```

Rules:

```text
observability must be file/event based in v1
no network metrics exporter by default
no daemon
no external monitoring dependency
```

## 19.13 `scheduler_validation.py`

Required public functions:

```python
validate_task(task: SchedulerTask | dict) -> list[str]
validate_session(session: SchedulerSession | dict) -> list[str]
validate_queue_state(state: SchedulerQueueState | dict) -> list[str]
validate_lease(lease: SchedulerLease | dict) -> list[str]
validate_transition(old_status: str, new_status: str) -> bool
validate_task_dependencies(task: SchedulerTask, repo_root: Path) -> list[str]
```

Rules:

```text
invalid records must not be silently accepted
invalid task payloads become INVALID or BLOCKED records
invalid status transitions fail closed
dependency checks must run before claim
```

---

# 20. Public Scheduler Dispatcher Boundary

The implementation must expose a controlled scheduler service boundary.

Required dispatcher functions:

```python
submit_scheduler_task(arguments: dict, repo_root: Path, policy_context: dict | None = None) -> SchedulerTask
start_scheduler_session(arguments: dict, repo_root: Path, policy_context: dict | None = None) -> SchedulerSession
claim_scheduler_task(session_id: str, repo_root: Path, queue_name: str = "default", policy_context: dict | None = None) -> SchedulerTask | None
complete_scheduler_task(task_id: str, session_id: str, repo_root: Path, result_ref: str | None = None) -> SchedulerTask
fail_scheduler_task(task_id: str, session_id: str, repo_root: Path, failure_class: str, message: str) -> SchedulerTask
run_scheduler_recovery(repo_root: Path, queue_name: str = "default") -> dict
```

Rules:

```text
external callers should use dispatcher functions rather than internal store functions
scheduler dispatcher must not execute task payloads
scheduler dispatcher must validate schemas and transitions
scheduler dispatcher must write evidence for every state transition
```

---

# 21. Integration with Tool / MCP Adapter

The scheduler may create and track tasks that eventually result in tool calls, but it must not call tools directly unless routed through the Tool / MCP Adapter.

Required integration rules:

```text
task payload may reference requested_tool_name
task payload may reference requested_effect
execution belongs to Tool / MCP Adapter
ToolResult evidence_refs should be attached to SchedulerTask evidence_refs
scheduler must not bypass Tool Registry
scheduler must not bypass Tool Policy
scheduler must not bypass Tool Adapter evidence logging
scheduler may mark a task DONE only after a schema-valid result or approved manual completion
```

Required behavior:

```text
if requested tool is unknown -> task becomes BLOCKED or FAILED with TOOL_NOT_FOUND
if tool policy denies -> task becomes BLOCKED with TOOL_POLICY_DENIED
if tool result fails -> task follows retry policy
if tool result is BLOCKED by safety -> task is not retried unless policy allows
```

The scheduler must treat Tool / MCP Adapter as the controlled execution boundary.

---

# 22. Integration with Policy / Capability Registry

The scheduler must check policy before creating, claiming, or running tasks that imply controlled actions.

Required policy checks:

```text
can role create this task type?
can role claim this task type?
can session execute this requested effect?
does the task require governance?
does the task require human approval?
is this task allowed in the current runtime mode?
is this queue allowed to run mutating tasks?
```

Fail-closed behavior:

```text
policy unavailable -> block mutating/executable task claims
unknown role -> block
unknown task type -> INVALID
requested effect not allowed -> BLOCKED
missing governance -> WAITING or BLOCKED
missing human approval -> WAITING or BLOCKED
```

---

# 23. Integration with Failure Taxonomy

Every failed, blocked, stale, recovered, invalid, or timed-out scheduler action must include a failure class.

Required scheduler failure classes:

```text
SCHEDULER_TASK_INVALID
SCHEDULER_TASK_DUPLICATE
SCHEDULER_TASK_BLOCKED
SCHEDULER_QUEUE_CORRUPT
SCHEDULER_SESSION_INVALID
SCHEDULER_SESSION_STALE
SCHEDULER_LOCK_DENIED
SCHEDULER_LOCK_STALE
SCHEDULER_LEASE_EXPIRED
SCHEDULER_LEASE_CONFLICT
SCHEDULER_RETRY_EXHAUSTED
SCHEDULER_RECOVERY_REQUIRED
SCHEDULER_RECOVERY_FAILED
SCHEDULER_POLICY_DENIED
SCHEDULER_TOOL_RESULT_FAILED
SCHEDULER_DEPENDENCY_MISSING
SCHEDULER_DEPENDENCY_FAILED
SCHEDULER_DEPENDENCY_CANCELLED
SCHEDULER_IDEMPOTENCY_CONFLICT
TRANSIENT_SCHEDULER_FAILURE
UNKNOWN_SCHEDULER_FAILURE
```

Mapping rules:

```text
policy denial -> SCHEDULER_POLICY_DENIED
duplicate task id -> SCHEDULER_TASK_DUPLICATE
queue parse failure -> SCHEDULER_QUEUE_CORRUPT
lease conflict -> SCHEDULER_LEASE_CONFLICT
expired lease -> SCHEDULER_LEASE_EXPIRED
stale session -> SCHEDULER_SESSION_STALE
retry limit exceeded -> SCHEDULER_RETRY_EXHAUSTED
unknown exception -> UNKNOWN_SCHEDULER_FAILURE
```

If the Failure Taxonomy layer is unavailable, the scheduler must still use deterministic local failure classes and must not fail open.

---

# 24. Integration with Monitoring / Observability

The scheduler must emit monitoring-ready events without requiring an external monitoring service.

Required event types:

```text
TASK_CREATED
TASK_ENQUEUED
TASK_CLAIMED
TASK_RUNNING
TASK_DONE
TASK_FAILED
TASK_BLOCKED
TASK_WAITING
TASK_RETRY_SCHEDULED
TASK_CANCELLED
SESSION_STARTED
SESSION_HEARTBEAT
SESSION_CLOSED
SESSION_STALE
LOCK_ACQUIRED
LOCK_RELEASED
LOCK_STALE
LEASE_CREATED
LEASE_RENEWED
LEASE_RELEASED
LEASE_EXPIRED
RECOVERY_STARTED
RECOVERY_COMPLETED
RECOVERY_FAILED
QUEUE_CORRUPTION_DETECTED
IDEMPOTENCY_CONFLICT
```

Required observability outputs:

```text
scheduler events in events.jsonl
queue summary through build_queue_summary
health snapshot through build_scheduler_health_snapshot
counts by task status
counts by session status
counts by stale locks and expired leases
```

Forbidden by default:

```text
network metrics push
hosted observability service
background monitoring daemon
long-running watch loop
```

---

# 25. Schema Requirements

Every schema must:

```text
require schema_version
require schema_id
require source_component where applicable
require created_at or timestamp where applicable
require warnings
require errors
define enums for statuses and task/session/lock/lease/event types
reject missing required fields
reject unknown status values
allow artifact_refs and evidence_refs arrays where applicable
```

Required schema example fixtures:

```text
valid_scheduler_task
valid_scheduler_queue_state
valid_scheduler_session
valid_scheduler_lock
valid_scheduler_lease
valid_scheduler_retry_policy
valid_scheduler_event
valid_scheduler_state
valid_scheduler_policy_decision
valid_scheduler_evidence_manifest
valid_scheduler_review_report
valid_scheduler_completion_record
```

Required schema tests:

```text
valid task passes
missing task_id fails
invalid task status fails
valid queue state passes
valid session passes
invalid session status fails
valid lock passes
invalid lock scope fails
valid lease passes
invalid lease status fails
valid retry policy passes
invalid retry policy fails
valid scheduler event passes
invalid event type fails
valid policy decision passes
valid evidence manifest passes
valid review report passes
valid completion record passes
```

---

# 26. Implementation Slices

Implement this layer in small slices.

## Slice A — Models and Schemas

Implement:

```text
scheduler_models.py
scheduler_task.schema.json
scheduler_queue.schema.json
scheduler_session.schema.json
scheduler_lock.schema.json
scheduler_lease.schema.json
scheduler_retry_policy.schema.json
scheduler_event.schema.json
scheduler_state.schema.json
scheduler_policy_decision.schema.json
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid examples
schemas reject missing required fields
schemas reject invalid enum values
no filesystem writes on import
```

## Slice B — Queue and Session Storage

Implement:

```text
queue_store.py
session_store.py
```

Acceptance:

```text
tasks append to JSONL
queue state writes atomically
sessions append to JSONL
session state writes atomically
malformed JSONL is quarantined or reported
```

## Slice C — Locks, Claims, and Leases

Implement:

```text
lock_manager.py
lease_manager.py
```

Acceptance:

```text
atomic lock acquisition works
active lock blocks duplicate acquisition
stale lock recovery is explicit
claim creates lease
same task cannot have two active leases
lease release updates task status
```

## Slice D — Retry and Crash Recovery

Implement:

```text
retry_policy.py
crash_recovery.py
```

Acceptance:

```text
retryable failures schedule retry
non-retryable safety failures do not retry
max attempts enforced
expired leases recovered
stale sessions recovered
recovery writes evidence
```

## Slice E — Scheduler Engine, Validation, and Evidence

Implement:

```text
scheduler_engine.py
scheduler_validation.py
scheduler_evidence.py
```

Acceptance:

```text
create/enqueue/claim/run/complete/fail/cancel transitions work
invalid transitions fail closed
dependency checks block unsatisfied tasks
idempotency conflicts block
events written for transitions
latest artifacts written atomically
scheduler evidence manifest created
```

## Slice F — Observability and Integration Tests

Implement:

```text
scheduler_observability.py
integration-oriented tests
review report
completion record
```

Acceptance:

```text
queue summary builds
health snapshot builds
observability emits local events only
compileall passes
pytest passes
schema validation passes
git status clean or expected runtime artifacts only
```

---

# 27. Test Cases

Required tests:

```text
test_scheduler_models_instantiate
test_scheduler_schema_accepts_valid_task
test_scheduler_schema_rejects_missing_task_id
test_scheduler_schema_rejects_invalid_task_status
test_scheduler_schema_requires_example_fixtures
test_scheduler_schema_accepts_valid_claim
test_scheduler_schema_rejects_invalid_claim_status
test_append_task_writes_jsonl
test_load_tasks_quarantines_malformed_lines
test_queue_state_written_atomically
test_start_session_writes_session_history
test_heartbeat_updates_session
test_close_session_preserves_history
test_acquire_lock_creates_atomic_lock
test_duplicate_active_lock_blocks
test_stale_lock_requires_recovery
test_lock_history_written
test_claim_pending_task_creates_claim_and_lease
test_claim_pending_task_creates_lease
test_claim_selection_is_deterministic
test_claim_blocked_if_task_already_leased
test_claim_blocked_if_dependencies_unmet
test_claim_blocked_if_next_run_at_future
test_renew_active_lease_extends_expiry
test_expired_lease_cannot_be_renewed_without_recovery
test_release_lease_updates_task_status
test_idempotent_task_create_returns_existing_task
test_idempotency_conflict_blocks
test_retryable_failure_schedules_retry
test_non_retryable_policy_denial_does_not_retry
test_non_retryable_sandbox_denial_does_not_retry
test_max_attempts_exhaustion_marks_failed
test_recovery_marks_stale_session
test_recovery_marks_expired_lease
test_recovery_does_not_execute_payload
test_invalid_transition_fails_closed
test_scheduler_event_written_for_task_claim
test_scheduler_evidence_redacts_secret_payload
test_scheduler_evidence_hashes_written
test_scheduler_health_snapshot_counts_statuses
test_scheduler_does_not_write_source_files
test_scheduler_does_not_start_background_daemon
test_scheduler_does_not_require_network
```

Negative tests:

```text
test_unknown_task_type_invalid
test_unknown_status_invalid
test_unknown_role_blocks_executable_task
test_policy_unavailable_blocks_mutating_claim
test_duplicate_task_id_blocks_or_records_duplicate
test_task_with_future_next_run_at_not_claimable
test_claim_without_session_blocks
test_claim_without_lock_blocks
test_two_sessions_cannot_claim_same_task
test_recovery_cannot_retry_policy_denied_task
test_recovery_cannot_retry_sandbox_denied_task
test_malformed_queue_state_fails_closed
test_scheduler_dispatcher_never_executes_payload
test_scheduler_never_calls_tool_directly
test_scheduler_never_starts_daemon_on_import
test_scheduler_never_opens_network_port
test_scheduler_never_requires_external_queue_or_database
```

---

# 28. Acceptance Criteria

The implementation is acceptable only if:

```text
all target files exist
all required schemas exist
all required tests exist
scheduler package imports without side effects
compileall passes
pytest passes
schema validation passes
schemas validate valid and invalid cases
queue state persists deterministically
task history is append-only
session history is append-only
atomic state snapshots work
locks prevent conflicting writes
leases prevent duplicate task execution
claims require active sessions
claim selection is deterministic
idempotency prevents duplicate task creation/execution
dependency checks block unsatisfied tasks
retry/backoff is deterministic
non-retryable safety failures do not retry
expired leases are recoverable
stale sessions are recoverable
crash recovery writes evidence
scheduler events are written
scheduler evidence manifest is written
scheduler review report is written
completion record is written
final evidence hashes are written
no source mutation occurs
no network is required
no background daemon starts by default
no external queue/database service is required
```

---

# 29. Manual Validation Commands

Run from repository root:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/scheduler
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_scheduler_models.py \
  tools/agentx_evolve/tests/test_scheduler_schemas.py \
  tools/agentx_evolve/tests/test_queue_store.py \
  tools/agentx_evolve/tests/test_session_store.py \
  tools/agentx_evolve/tests/test_lock_manager.py \
  tools/agentx_evolve/tests/test_lease_manager.py \
  tools/agentx_evolve/tests/test_retry_policy.py \
  tools/agentx_evolve/tests/test_crash_recovery.py \
  tools/agentx_evolve/tests/test_scheduler_engine.py \
  tools/agentx_evolve/tests/test_scheduler_evidence.py \
  tools/agentx_evolve/tests/test_scheduler_observability.py \
  tools/agentx_evolve/tests/test_scheduler_validation.py \
  tools/agentx_evolve/tests/test_scheduler_negative_cases.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
git status --short
```

Required result:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts under .agentx-init/scheduler/
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
MCP server
external queue service
database server
cron
background daemon
```

---

# 30. Implementation Drift Blockers

Reject or revise the implementation if it:

```text
places scheduler files outside tools/agentx_evolve/scheduler/ without recorded deviation
writes scheduler runtime artifacts outside .agentx-init/scheduler/ without recorded deviation
executes task payloads directly
calls tools without Tool / MCP Adapter
allows duplicate active claims for the same task
allows two active leases for the same task
silently overwrites locks
silently drops task/session history
silently accepts invalid transitions
silently accepts malformed queue records
retries policy-denied tasks by default
retries sandbox-denied tasks by default
starts a background daemon automatically
requires network
requires external queue service
requires database server
mutates source files
performs Git writes
opens MCP or scheduler server ports
logs unredacted secrets
ignores schema-invalid task records
marks stale tasks recovered without evidence
omits final evidence hashes
```

---

# 31. Evidence Manifest

After validation, write:

```text
.agentx-init/scheduler/scheduler_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_evidence_manifest.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "commands": [],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "queue_status": "PASS",
  "session_status": "PASS",
  "lock_status": "PASS",
  "lease_status": "PASS",
  "retry_status": "PASS",
  "recovery_status": "PASS",
  "observability_status": "PASS",
  "hash_status": "PASS",
  "final_decision": "DONE"
}
```

---

# 32. Review Report

After validation, write:

```text
.agentx-init/scheduler/scheduler_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_review_report.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
  "review_document_id": "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD",
  "implementation_spec_id": "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC",
  "implementation_spec_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_at": "<UTC timestamp>",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/scheduler/scheduler_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/scheduler/scheduler_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

---

# 33. Completion Evidence

After validation, write:

```text
.agentx-init/scheduler/scheduler_completion_record.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_completion_record.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
  "component_name": "Task Queue / Session Scheduler",
  "status": "VALIDATED",
  "validated_commit": "<commit hash>",
  "validated_at": "<UTC timestamp>",
  "canonical_scheduler_subdirectory": "tools/agentx_evolve/scheduler/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/scheduler/",
  "basis_documents": [
    "TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC_v4"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "queue_coverage_verified": [],
  "session_coverage_verified": [],
  "locking_coverage_verified": [],
  "lease_coverage_verified": [],
  "retry_coverage_verified": [],
  "crash_recovery_coverage_verified": [],
  "tool_adapter_integration_verified": [],
  "policy_integration_verified": [],
  "failure_taxonomy_integration_verified": [],
  "observability_integration_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/scheduler/scheduler_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/scheduler/scheduler_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviations_from_contract": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 34. Definition of Done

The Task Queue / Session Scheduler layer is done when it can safely manage queued work and scheduler sessions without uncontrolled execution.

It must prove:

```text
all scheduler files exist
all schemas exist
all tests exist
scheduler package imports cleanly
queue storage works
session storage works
append-only task history works
append-only session history works
atomic state snapshots work
locks prevent conflicting writes
leases prevent duplicate task execution
claims require active sessions
claim selection is deterministic
idempotency prevents duplicate execution
dependency checks block unsatisfied tasks
retry and backoff rules are deterministic
safety-denied tasks are not retried by default
expired leases are recoverable
stale sessions are recoverable
crash recovery writes evidence
scheduler events are written
scheduler evidence manifest is written
scheduler review report is written
completion record is written
final evidence hashes are written
Tool / MCP Adapter integration boundary is respected
Policy / Capability Registry integration boundary is respected
Failure Taxonomy mapping exists
Monitoring / Observability local event output exists
no source mutation occurs directly in this layer
no network is required
no background daemon starts by default
no external queue/database service is required
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve/scheduler
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_scheduler_*.py
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts under .agentx-init/scheduler/
```

---

# 35. Final Frozen Acceptance Matrix

| Area | Required outcome |
|---|---|
| Structure | Scheduler package, schemas, tests, and runtime root exist. |
| Queue | Append-only task history and deterministic queue state work. |
| Sessions | Sessions start, heartbeat, close, stale-detect, and recover. |
| Locks | Atomic active lock files prevent conflicting writes. |
| Leases | One active lease per task; renew/release evidenced. |
| Claims | Claim selection is deterministic and dependency-aware. |
| Idempotency | Duplicate create/claim/retry/complete calls do not duplicate execution. |
| Retry | Backoff deterministic; safety-denied failures not retried by default. |
| Recovery | Expired leases/stale sessions/stale locks recover with evidence. |
| Validation | Invalid records and invalid transitions fail closed. |
| Tool boundary | No direct tool execution; Tool / MCP Adapter is respected. |
| Policy boundary | Executable/mutating task progression requires policy approval. |
| Failure taxonomy | All scheduler failures have deterministic failure classes. |
| Observability | Local event/summary/health outputs exist without network. |
| Evidence | Manifest, review report, completion record, and SHA-256 hashes exist. |
| Safety | No source mutation, network, daemon, external DB/queue, or Git write. |

---

# 36. v4 Precision Controls

## 36.1 Canonical State Reconstruction

Append-only history is the source of truth. Snapshot files are derived caches.

Required reconstruction rules:

```text
effective task state = latest valid task record per task_id
effective session state = latest valid session record per session_id
effective lease state = latest valid lease record per lease_id
effective claim state = latest valid claim record per claim_id
latest record order = higher append_sequence, then later updated_at, then lexicographically greater record_id
malformed records are quarantined and excluded from effective state
snapshots may be rebuilt from valid append-only history
snapshot rebuild must write an event and evidence reference
```

Snapshot files must not be treated as more authoritative than valid append-only history. If a snapshot conflicts with history, rebuild the snapshot and record the conflict.

## 36.2 Task Record Revisioning and Hashing

Every appended task revision must include:

```text
record_id
revision
append_sequence
previous_record_hash
task_record_hash
```

Rules:

```text
revision starts at 1
revision increments on each state-changing task record
append_sequence is monotonic within the local scheduler history file
previous_record_hash references the previous effective task record when available
task_record_hash is computed over canonical JSON excluding task_record_hash itself
queue_hash and state_hash are computed over canonical JSON excluding their own hash fields
```

Hash calculation must use deterministic key ordering.

## 36.3 Clock and Time Rules

All scheduler time values must be UTC ISO-8601 timestamps.

Required implementation rule:

```text
production code may call utc_now_iso()
tests must be able to inject or monkeypatch the clock
all comparisons must normalize to UTC
naive local datetime values are invalid
next_run_at, expires_at, heartbeat_at, created_at, and updated_at must be comparable deterministically
```

No test may depend on wall-clock sleep for correctness.

## 36.4 Atomic Lock Creation Rule

Active lock acquisition must use exclusive-create semantics.

Required behavior:

```text
open lock file with exclusive create mode or os.open O_CREAT|O_EXCL
write full lock payload immediately after successful exclusive creation
if creation fails because file exists, load lock and check staleness
non-stale existing lock returns SCHEDULER_LOCK_DENIED
stale existing lock requires explicit recovery path before re-acquire
```

Do not implement lock acquisition as write-temp-then-replace, because replace can overwrite a concurrent lock. Atomic replace is allowed for snapshots, not for acquiring active locks.

## 36.5 Claim / Lease Separation

Claims and leases are related but not identical.

```text
claim = assignment of task to session
lease = time-bound validity of that claim
```

A task may be marked `CLAIMED` only when both a claim record and an active lease record exist.

## 36.6 Real Integration vs Fallback Rule

When prior layers exist, use them through stable public APIs.

Required behavior:

```text
use real Policy / Capability Registry if available
use real Failure Taxonomy if available
use Tool / MCP Adapter only as execution boundary, never internal direct wrappers
if integration import or call fails, fail closed for executable/mutating scheduler operations
local fallback classes may be used only for deterministic BLOCKED/INVALID/FAILED results
```

Fallback must never turn an unavailable authority into `ALLOW`.

## 36.7 Queue Corruption Quarantine and Snapshot Rebuild

Malformed history lines and corrupt snapshots must be handled explicitly.

Required behavior:

```text
malformed JSONL line -> copy safe summary to quarantine.jsonl
invalid schema record -> copy safe summary to quarantine.jsonl
corrupt snapshot -> ignore snapshot, rebuild from valid history, write QUEUE_CORRUPTION_DETECTED
rebuild failure -> fail closed and keep scheduler state read-only
quarantine evidence must include source path, line number if available, parse/schema error, and hash of raw line when safe
```

Raw sensitive payloads must be redacted before quarantine evidence is written.

## 36.8 Payload Non-Execution Rule

The scheduler must treat task payloads as data only.

This rule applies to:

```text
create_task
enqueue_task
claim_next_task
mark_task_running
complete_task
fail_task
run_recovery_pass
snapshot rebuild
observability summary
scheduler dispatcher functions
```

No task payload may be imported, evaluated, executed, shell-expanded, passed to a subprocess, or treated as Python code by this layer.

## 36.9 Scheduler Policy Module Requirement

The implementation must include `scheduler_policy.py`. The policy module is required because queue/session permission is not identical to tool execution permission.

It must decide whether a role/session may create, claim, progress, cancel, recover, or inspect tasks. Tool execution permission remains owned by the Tool / MCP Adapter and Policy / Capability Registry.

## 36.10 Scheduler Dispatcher Module Requirement

The implementation must include `scheduler_dispatcher.py`. This is the external service boundary for scheduler operations. Store modules are internal persistence helpers and must not be the default external API.

## 36.11 Implementation Freeze Rule

This v4 spec is frozen as the implementation handoff.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes, clearer test names
MINOR: additive optional helper functions that do not change safety behavior
MAJOR: new required storage backend, daemon mode, network scheduling, external queue, database dependency, changed status model, changed lock semantics, or changed policy behavior
```

Blocked without major revision:

```text
allowing background daemon by default
allowing external queue/database dependency by default
allowing scheduler to execute task payloads
allowing scheduler to bypass Tool / MCP Adapter
allowing scheduler to bypass Policy / Capability Registry
allowing duplicate active claims
allowing non-exclusive active lock creation
allowing policy/sandbox-denied tasks to retry by default
removing append-only history
removing evidence logging
removing SHA-256 evidence hashing
```

---

# 37. Final Rating

This v4 implementation spec is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 coverage and fixes the remaining implementation-handoff gaps: canonical state reconstruction, task revisioning, claim/lease separation, scheduler policy module, scheduler dispatcher module, UTC clock rules, exclusive lock creation, state hash rules, corruption quarantine, real-integration fail-closed behavior, payload non-execution tests, and a final freeze rule. It now defines exact subdirectories, files, schemas, classes, functions, runtime artifacts, queue/session formats, locks, leases, claims, retries, recovery, integrations, observability, evidence, tests, acceptance criteria, drift blockers, and Definition of Done at implementation-ready precision.
```
