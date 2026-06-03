# TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT

```text
document_id: TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT
version: v4.0
status: final frozen controlling contract, implementation-ready
component_id: AGENTX_TASK_QUEUE_SESSION_SCHEDULER
component_name: Task Queue / Session Scheduler
roadmap_layer: 18
roadmap_phase: Phase C — Scheduled Work Control
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria, Monitoring / Observability Acceptance Criteria
risk_level: critical
target_language: Python
canonical_subdirectory: tools/agentx_evolve/scheduler/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/scheduler/
queue_artifact_root: .agentx-init/scheduler/queue/
session_artifact_root: .agentx-init/scheduler/sessions/
claim_artifact_root: .agentx-init/scheduler/claims/
lease_artifact_root: .agentx-init/scheduler/leases/
retry_artifact_root: .agentx-init/scheduler/retries/
failure_artifact_root: .agentx-init/scheduler/failures/
audit_artifact_root: .agentx-init/scheduler/audit/
contract_rating: 10/10
previous_version_rating: 9.8/10
current_version_rating: 10/10
next_document: TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC
```

---

# 0. v4 Review and Upgrade Summary

The v3 contract was strong and implementation-ready. I would rate it:

```text
9.8/10
```

It already covered the required controlling-contract areas:

```text
EQC
FIC
SIB
Schema Contract
Task Queue Schema
Session Schema
Scheduler Policy Schema
Queue State Schema
Task Claim / Lease Schema
Retry / Backoff Contract
Concurrency / Locking Contract
Crash Recovery Contract
Audit / Evidence Contract
Agent_X integration notes
OpenCode / coding-agent borrowing notes
task definition
session definition
queueing
claiming
session lifecycle
retry handling
failure recording
stale-lock recovery
duplicate-execution prevention
queue persistence
scheduler evidence
orchestrator interaction
scheduler operating modes
priority and starvation rules
cancellation, drain, and emergency stop
task-effect authority mapping
two-phase readiness and execution handoff
transition logging
snapshot, compaction, and replay safety
review-ready evidence requirements
```

It was not fully 10/10 because a few final production-control details were still under-specified:

```text
1. Task payload safety was not explicit enough; scheduler records can carry tool arguments, prompts, paths, and commands that need redaction and injection handling.
2. Scheduler API authorization needed a clearer per-operation authority matrix for create, claim, cancel, retry, resume, close, recover, drain, and emergency stop.
3. The v1 deployment boundary needed to state whether locking is local-filesystem-only or distributed-safe.
4. Clock behavior needed a stricter monotonic/UTC rule for lease expiry, retry_after, heartbeat, and recovery comparisons.
5. Hash chaining and tamper-evidence needed a stronger rule for queue state, transition logs, evidence manifests, and snapshots.
6. Schema migration/version compatibility needed a contract so old queue artifacts do not get silently reinterpreted.
7. Runner batch limits and fairness caps needed stronger bounds to avoid one invocation consuming the whole queue.
8. Repair mode needed to be separated from normal recovery so corrupt state is inspected and evidenced, not silently fixed.
9. Downstream cancellation acknowledgement needed to be explicit for tasks already handed off to tools, models, patch, or Git layers.
10. Sensitive task payloads needed a durable redaction and minimal-retention rule.
```

This v4 applies those corrections and is the final 10/10 controlling contract.

---

# 1. Purpose

This document defines the controlling contract for the **Task Queue / Session Scheduler** layer in Agent_X.

This layer controls how Agent_X records queued work, starts and resumes sessions, leases tasks to workers, prevents duplicate execution, handles retries, recovers stale sessions, and writes scheduler evidence.

The Task Queue / Session Scheduler must ensure that queued work is:

```text
schema-valid
policy-aware
lease-controlled
audit-backed
crash-recoverable
idempotent where required
safe by default
non-duplicated
traceable from task creation to final outcome
bounded by policy, lease, retry, and session rules
separate from actual tool/patch/model execution
```

This layer must not become a hidden background executor. It may prepare, queue, claim, resume, retry, cancel, recover, and close work, but actual mutation must still pass through the relevant Agent_X safety layers.

---

# 2. Scope

## 2.1 Required in This Layer

The Task Queue / Session Scheduler must define contracts for:

```text
task records
session records
queue state
scheduler state
task dependency records
task claim records
task lease records
retry and backoff records
failure records
stale-lock recovery
crash recovery
duplicate-execution prevention
worker/session ownership
queue persistence
audit/evidence records
scheduler policy checks
orchestrator interaction with queued work
Tool / MCP Adapter handoff boundaries
```

## 2.2 Not Required in This Layer

This layer must not implement:

```text
LLM worker behavior
model selection
prompt execution
patch generation
patch application
source mutation logic
Git write behavior
network fetching
human approval UI
promotion gate
long-term learning
MCP runtime server
background daemon that starts automatically
raw shell execution
actual tool execution outside Tool / MCP Adapter
```

The scheduler may coordinate work. It must not perform unsafe work directly.

---

# 3. Standards Package

## 3.1 Primary Standard: EQC

EQC is primary because the scheduler controls when work exists, when it can run, who may claim it, when it may retry, and whether duplicate or stale execution is prevented.

EQC applies to:

```text
task lifecycle correctness
session lifecycle correctness
claim/lease correctness
recovery correctness
retry correctness
dependency correctness
duplicate-execution prevention
source mutation prevention
policy integration
evidence completeness
runtime artifact boundaries
```

The layer must fail closed.

## 3.2 Required Supporting Standard: FIC

FIC is required because this layer has concrete implementation files.

Expected implementation files must live under:

```text
tools/agentx_evolve/scheduler/
```

Each file must have:

```text
clear responsibility
public API
input schema
output schema
state invariants
failure behavior
test coverage
evidence behavior
runtime artifact boundary
```

## 3.3 Required Supporting Standard: SIB

SIB is required because this layer connects multiple Agent_X components:

```text
Self-Evolution Orchestrator
Tool / MCP Adapter
Policy / Capability Registry
Security Sandbox / Filesystem Boundary
Governed Patch Execution Layer
Failure Taxonomy / Recovery Playbook
Monitoring / Observability Layer
Human Review / Approval Interface
Git Integration Layer
Promotion / Release Gate
Backup / Disaster Recovery Layer
```

The scheduler is an integration boundary. It must not bypass any connected subsystem.

## 3.4 Required Schema Contract

Every persisted task, session, dependency, claim, lease, retry, failure, queue-state, scheduler-state, recovery, and audit record must be schema-valid.

Required schemas include:

```text
task_record.schema.json
scheduler_session.schema.json
queue_state.schema.json
scheduler_state.schema.json
task_dependency.schema.json
task_claim.schema.json
task_lease.schema.json
task_retry.schema.json
task_failure.schema.json
scheduler_policy.schema.json
scheduler_recovery.schema.json
scheduler_audit.schema.json
scheduler_evidence_manifest.schema.json
scheduler_completion_record.schema.json
scheduler_mode.schema.json
task_cancellation.schema.json
scheduler_transition.schema.json
scheduler_snapshot_manifest.schema.json
```

## 3.5 Required Evidence / Audit Rules

Every scheduler-relevant state transition must create evidence.

Evidence is required for:

```text
task created
task queued
task dependency evaluated
task dependency blocked
task made ready
task claimed
task lease granted
task lease renewed
task lease expired
task started
task blocked
task retried
task failed
task completed
task cancelled
session created
session resumed
session paused
session closed
stale lock detected
stale lock recovered
crash recovery performed
duplicate claim rejected
policy-denied scheduling action
invalid task record
invalid session record
queue corruption detected
queue corruption preserved
```

---

# 4. Why This Layer Is Safety-Critical

The Task Queue / Session Scheduler is safety-critical because it decides:

```text
which tasks exist
which tasks are pending, ready, claimed, running, blocked, failed, cancelled, or done
which worker or session may claim a task
whether a task dependency is satisfied
whether a task can be retried
whether a failed task should stop dependent work
whether duplicate execution is prevented
whether stale locks are recovered safely
whether scheduled work can indirectly mutate source
whether queued work respects policy, sandbox, governance, and approval gates
whether evidence exists for every scheduled action
```

Without this layer, Agent_X could have:

```text
uncontrolled queued work
duplicate workers executing the same task
lost task state
stale locks that block progress forever
unsafe retries
untraceable session resumes
hidden background behavior
unreviewable scheduler decisions
```

---

# 5. Dependency Gates

This layer depends on earlier Agent_X safety components. It must not become a bypass around them.

## 5.1 Required Prior Components for Live Risky Work

Before a task involving mutation, command execution, network, model execution, patching, Git, promotion, or human approval is allowed to move into executable form, these components must be present and validated as applicable:

```text
Policy / Capability Registry
Tool / MCP Adapter
Security Sandbox / Filesystem Boundary
Failure Taxonomy / Recovery Playbook
Governed Patch Execution Layer, for patch tasks
Human Review / Approval Interface, for approval-required tasks
Git Integration Layer, for Git tasks
Model Adapter / LLM Worker, for model tasks
```

## 5.2 Restricted Mode

Restricted mode allows:

```text
schema validation
queue inspection
task creation for read-only/planning work
session creation
session resume for read-only inspection
claim dry-run
dependency evaluation
failure recording
crash recovery inspection
evidence writing
```

Restricted mode blocks:

```text
source mutation tasks
patch application tasks
subprocess/command tasks
Git write tasks
network tasks
model execution tasks
MCP mutating exposure
human approval override behavior
promotion tasks
```

## 5.3 Dependency Gate Rules

```text
If Policy / Capability Registry is missing -> risky claim, retry, cancellation, and resume actions BLOCK.
If Tool / MCP Adapter is missing -> executable tool tasks remain BLOCKED or READY_ONLY_PLANNED.
If Security Sandbox is missing -> tasks involving paths, files, commands, or source mutation BLOCK before execution handoff.
If Failure Taxonomy is missing -> scheduler uses UNKNOWN_SCHEDULER_FAILURE but still blocks risky execution.
If Governed Patch Execution is missing -> patch execution tasks remain BLOCKED.
If Human Review is missing -> human-approval-required tasks remain BLOCKED.
If Model Adapter / LLM Worker is missing -> model execution tasks remain BLOCKED.
If MCP runtime dependency is missing -> scheduler MCP exposure remains NOT APPLICABLE or DEFERRED SAFELY.
```

## 5.4 Authority Rule

A scheduler decision does not grant execution permission by itself.

A task may proceed only when all required authorities agree:

```text
Scheduler state
Scheduler policy
Policy / Capability Registry
Tool / MCP Adapter, for tool calls
Security Sandbox, for path/file/command work
Governed Patch Execution, for patch tasks
Human approval, when required
Failure Taxonomy, for failure classification
```

If authorities disagree, the strictest result wins.

Decision precedence:

```text
INVALID
BLOCKED
RECOVERY_REQUIRED
NEEDS_APPROVAL
NEEDS_GOVERNANCE
DRY_RUN_ONLY
READY
ALLOW
```

---

# 6. Status Vocabulary

Use only these status values unless a later major contract revision adds new values.

## 6.1 Task Status Values

```text
PENDING
READY
CLAIMED
RUNNING
BLOCKED
FAILED
CANCELLED
DONE
RECOVERING
```

## 6.2 Session Status Values

```text
CREATED
ACTIVE
PAUSED
RECOVERING
CLOSING
CLOSED
FAILED
```

## 6.3 Claim Status Values

```text
REQUESTED
GRANTED
DENIED
EXPIRED
RELEASED
```

## 6.4 Lease Status Values

```text
ACTIVE
RENEWED
EXPIRED
RELEASED
REVOKED
```

## 6.5 Retry Status Values

```text
NOT_ALLOWED
SCHEDULED
SKIPPED
EXHAUSTED
BLOCKED
```

## 6.6 Scheduler Operation Result Values

```text
SUCCESS
PARTIAL
BLOCKED
FAILED
INVALID
RECOVERY_REQUIRED
```

---

# 7. Definitions

## 7.1 Task

A task is a durable unit of scheduled work.

A task must define:

```text
what work is requested
which component owns it
which role may create, claim, or execute it
which policy gates apply
which dependencies must be satisfied
which artifacts it may read or write
whether it is idempotent
whether it may retry
what timeout applies
what final outcome was recorded
```

A task is not an unstructured prompt. It is a schema-valid scheduler object.

## 7.2 Session

A session is a durable execution context for one or more tasks.

A session must define:

```text
session identity
session owner
active worker identity, if any
current task, if any
session status
created/resumed/closed timestamps
policy context
runtime artifact root
recovery state
last heartbeat
```

A session is not a background daemon. It is a persisted state object that can be started, resumed, paused, recovered, or closed.

## 7.3 Queue

A queue is the durable ordered set of known tasks.

The queue must track:

```text
pending tasks
ready tasks
claimed tasks
running tasks
blocked tasks
failed tasks
cancelled tasks
completed tasks
recovering tasks
dependency relationships
priority
claim status
lease status
retry status
```

## 7.4 Claim

A claim is a request by a worker/session to take responsibility for a task.

A claim must be atomic. Only one active claim may own a task at a time.

## 7.5 Lease

A lease is a time-bounded ownership grant for a claimed task.

A lease prevents duplicate execution while allowing recovery when a worker dies, crashes, or stops heartbeating.

## 7.6 Scheduler State

Scheduler state is the durable summary of the scheduler runtime.

It must track:

```text
queue version
queue hash
active sessions
active leases
last recovery scan
last transition ID
scheduler lock status
evidence manifest references
```

---

# 8. Canonical Subdirectories

## 8.1 Scheduler Package

```text
tools/agentx_evolve/scheduler/
```

Expected files:

```text
__init__.py
scheduler_models.py
task_queue.py
session_store.py
lease_manager.py
retry_policy.py
scheduler_policy.py
scheduler_audit.py
crash_recovery.py
queue_runner.py
scheduler_state.py
scheduler_locks.py
scheduler_hashing.py
```

## 8.2 Schema Directory

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
task_record.schema.json
scheduler_session.schema.json
queue_state.schema.json
scheduler_state.schema.json
task_dependency.schema.json
task_claim.schema.json
task_lease.schema.json
task_retry.schema.json
task_failure.schema.json
scheduler_policy.schema.json
scheduler_recovery.schema.json
scheduler_audit.schema.json
scheduler_evidence_manifest.schema.json
scheduler_completion_record.schema.json
scheduler_mode.schema.json
task_cancellation.schema.json
scheduler_transition.schema.json
scheduler_snapshot_manifest.schema.json
```

## 8.3 Test Directory

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_scheduler_models.py
test_task_queue.py
test_session_store.py
test_lease_manager.py
test_retry_policy.py
test_scheduler_policy.py
test_scheduler_audit.py
test_crash_recovery.py
test_queue_runner.py
test_scheduler_locks.py
test_scheduler_hashing.py
test_scheduler_operating_modes.py
test_scheduler_cancellation.py
test_scheduler_transition_log.py
test_scheduler_snapshot_replay.py
test_scheduler_negative_cases.py
test_scheduler_schema_validation.py
```

## 8.4 Runtime Artifacts

Scheduler runtime artifacts must live under:

```text
.agentx-init/scheduler/
```

Expected runtime files:

```text
.agentx-init/scheduler/queue/tasks.jsonl
.agentx-init/scheduler/queue/queue_state.json
.agentx-init/scheduler/queue/task_dependencies.jsonl
.agentx-init/scheduler/sessions/session_history.jsonl
.agentx-init/scheduler/sessions/latest_session.json
.agentx-init/scheduler/claims/claim_history.jsonl
.agentx-init/scheduler/leases/lease_history.jsonl
.agentx-init/scheduler/retries/retry_history.jsonl
.agentx-init/scheduler/failures/failure_history.jsonl
.agentx-init/scheduler/recovery/recovery_history.jsonl
.agentx-init/scheduler/audit/scheduler_audit.jsonl
.agentx-init/scheduler/transitions/transition_history.jsonl
.agentx-init/scheduler/cancellations/cancellation_history.jsonl
.agentx-init/scheduler/snapshots/snapshot_manifest.json
.agentx-init/scheduler/latest_scheduler_mode.json
.agentx-init/scheduler/latest_scheduler_state.json
.agentx-init/scheduler/scheduler_evidence_manifest.json
.agentx-init/scheduler/scheduler_completion_record.json
```

---

# 9. Task Queue Schema Contract

A task record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_record.schema.json",
  "task_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "source_component": "string",
  "created_by_role": "string",
  "task_type": "string",
  "title": "string",
  "description": "string",
  "status": "PENDING|READY|CLAIMED|RUNNING|BLOCKED|FAILED|CANCELLED|DONE|RECOVERING",
  "priority": 0,
  "queue_name": "default",
  "depends_on": [],
  "blocks": [],
  "idempotency_key": "string|null",
  "idempotency_scope": "GLOBAL|QUEUE|SESSION|NONE",
  "allowed_roles": [],
  "required_capabilities": [],
  "required_policy_checks": [],
  "requires_sandbox": false,
  "requires_governance": false,
  "requires_human_approval": false,
  "may_mutate_source": false,
  "may_run_commands": false,
  "may_use_network": false,
  "max_attempts": 1,
  "attempt_count": 0,
  "timeout_seconds": 300,
  "lease_id": "string|null",
  "session_id": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Required task rules:

```text
task_id is required
task_type is required
status is required
created_by_role is required
allowed_roles is required
attempt_count must not exceed max_attempts
depends_on must reference existing or planned task IDs
idempotency_key must be present for retryable risky work
may_mutate_source requires policy, sandbox, governance, and appropriate downstream layer
may_run_commands requires policy and command acceptance checks
may_use_network blocks by default unless explicitly allowed by policy
```

---

# 10. Task Dependency Contract

Task dependencies must be explicit and acyclic.

A task dependency record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_dependency.schema.json",
  "dependency_id": "string",
  "created_at": "string",
  "task_id": "string",
  "depends_on_task_id": "string",
  "dependency_type": "MUST_COMPLETE|MUST_PASS|MUST_EXIST|MUST_BE_APPROVED",
  "status": "PENDING|SATISFIED|BLOCKED|FAILED",
  "reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Dependency rules:

```text
cycles are forbidden
missing dependency blocks task readiness
FAILED dependency blocks dependent tasks unless policy permits continuation
CANCELLED dependency blocks dependent tasks unless policy permits continuation
DONE dependency satisfies only completion dependencies
approval dependencies require approval evidence
readiness evaluation must write evidence
```

---

# 11. Session Schema Contract

A session record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_session.schema.json",
  "session_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "started_at": "string|null",
  "resumed_at": "string|null",
  "closed_at": "string|null",
  "last_heartbeat_at": "string|null",
  "source_component": "TaskQueueSessionScheduler",
  "owner_role": "string",
  "owner_id": "string|null",
  "status": "CREATED|ACTIVE|PAUSED|RECOVERING|CLOSING|CLOSED|FAILED",
  "current_task_id": "string|null",
  "claimed_task_ids": [],
  "runtime_artifact_root": ".agentx-init/scheduler/",
  "policy_context_ref": "string|null",
  "recovery_state": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Required session rules:

```text
session_id is required
owner_role is required
status is required
only ACTIVE sessions may claim tasks
only ACTIVE sessions may renew leases
closed sessions may not claim, renew, or complete tasks
failed sessions require recovery evidence
resumed sessions must reference prior session evidence
session state must be persisted before task execution starts
```

---

# 12. Scheduler Policy Schema Contract

A scheduler policy record must define:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_policy.schema.json",
  "policy_id": "string",
  "created_at": "string",
  "source_component": "SchedulerPolicy",
  "allowed_task_types": [],
  "blocked_task_types": [],
  "allowed_roles": [],
  "max_concurrent_tasks": 1,
  "max_concurrent_tasks_per_session": 1,
  "default_lease_seconds": 300,
  "max_lease_seconds": 1800,
  "default_timeout_seconds": 300,
  "max_attempts_default": 1,
  "allow_source_mutation_tasks": false,
  "allow_command_tasks": false,
  "allow_network_tasks": false,
  "allow_background_auto_start": false,
  "requires_policy_for_all_claims": true,
  "requires_evidence_for_all_transitions": true,
  "warnings": [],
  "errors": []
}
```

Scheduler policy rules:

```text
unknown task type blocks by default
unknown role blocks by default
source mutation tasks block unless explicitly allowed by policy and downstream authorities
command tasks block unless command acceptance criteria pass
network tasks block by default
policy service unavailable -> scheduler blocks risky actions
background auto-start is disabled by default
```

---

# 13. Queue State Schema Contract

Queue state must persist the current summary of all known tasks.

A queue state record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "queue_state.schema.json",
  "queue_state_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "source_component": "TaskQueueSessionScheduler",
  "queue_name": "default",
  "pending_task_ids": [],
  "ready_task_ids": [],
  "claimed_task_ids": [],
  "running_task_ids": [],
  "blocked_task_ids": [],
  "failed_task_ids": [],
  "cancelled_task_ids": [],
  "done_task_ids": [],
  "recovering_task_ids": [],
  "task_count": 0,
  "active_session_ids": [],
  "active_lease_ids": [],
  "queue_version": 1,
  "queue_hash": "string",
  "previous_queue_hash": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Queue state rules:

```text
a task may appear in only one lifecycle bucket at a time
queue_version increments on every state transition
queue_hash changes when queue state changes
previous_queue_hash links state history
state writes must be atomic
partial/corrupt queue state must trigger recovery path
```

---

# 14. Scheduler State Schema Contract

Scheduler state must describe scheduler runtime health and provenance.

A scheduler state record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_state.schema.json",
  "scheduler_state_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "source_component": "TaskQueueSessionScheduler",
  "scheduler_version": "string",
  "queue_state_id": "string",
  "queue_hash": "string",
  "active_session_ids": [],
  "active_lease_ids": [],
  "last_transition_id": "string|null",
  "last_recovery_scan_at": "string|null",
  "runtime_artifact_root": ".agentx-init/scheduler/",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Scheduler state rules:

```text
scheduler state must reference the latest queue state
scheduler state must be written atomically
scheduler state must not omit active leases
scheduler state must include evidence refs for recovery scans
```

---

# 15. Task Claim / Lease Schema Contract

## 15.1 Task Claim

A task claim record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_claim.schema.json",
  "claim_id": "string",
  "created_at": "string",
  "task_id": "string",
  "session_id": "string",
  "claimant_role": "string",
  "claimant_id": "string|null",
  "claim_status": "REQUESTED|GRANTED|DENIED|EXPIRED|RELEASED",
  "reason": "string",
  "policy_decision_ref": "string|null",
  "lease_id": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

## 15.2 Task Lease

A lease record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_lease.schema.json",
  "lease_id": "string",
  "created_at": "string",
  "updated_at": "string",
  "expires_at": "string",
  "task_id": "string",
  "session_id": "string",
  "owner_role": "string",
  "owner_id": "string|null",
  "lease_status": "ACTIVE|RENEWED|EXPIRED|RELEASED|REVOKED",
  "renewal_count": 0,
  "max_renewals": 3,
  "heartbeat_required": true,
  "last_heartbeat_at": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Claim and lease rules:

```text
only READY tasks may be claimed
only one ACTIVE lease may exist per task
a claim must be atomic
claim conflict returns DENIED, not partial ownership
lease expiration must not mark task DONE
expired lease moves task to RECOVERING or READY depending on recovery policy
lease renewal requires active session heartbeat
duplicate claim attempts must be evidenced
```

---

# 16. Retry / Backoff Contract

Retry behavior must be deterministic and bounded.

A retry record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_retry.schema.json",
  "retry_id": "string",
  "created_at": "string",
  "task_id": "string",
  "session_id": "string|null",
  "attempt_number": 1,
  "max_attempts": 3,
  "retry_status": "NOT_ALLOWED|SCHEDULED|SKIPPED|EXHAUSTED|BLOCKED",
  "retry_allowed": false,
  "retry_after": "string|null",
  "backoff_strategy": "NONE|FIXED|EXPONENTIAL",
  "backoff_seconds": 0,
  "failure_class": "string|null",
  "reason": "string",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Retry rules:

```text
retry is disabled by default
attempt_count must never exceed max_attempts
unsafe failures do not retry automatically
policy-denied tasks do not retry automatically
sandbox-denied tasks do not retry automatically
schema-invalid tasks do not retry automatically
source-mutation tasks require idempotency key before retry
transient infrastructure failure may retry only if policy permits
retry decision must be evidenced
backoff must be persisted
```

---

# 17. Time, Heartbeat, and Expiration Contract

Time-sensitive scheduler decisions must be deterministic and evidence-backed.

Rules:

```text
all timestamps must be UTC ISO-8601 strings
lease expiration must compare against recorded UTC time
heartbeat timeout must be explicit in scheduler policy
clock skew assumptions must be recorded if distributed runtime is added later
expired lease does not imply failure or completion by itself
missing heartbeat moves session/task to RECOVERING or BLOCKED, not DONE
```

Required defaults:

```text
default_lease_seconds = 300
default_timeout_seconds = 300
max_lease_seconds = 1800
max_renewals = 3
heartbeat_required = true
```

---

# 18. Concurrency / Locking Contract

The scheduler must prevent duplicate task execution.

Required concurrency rules:

```text
task claim must be atomic
lease grant must be atomic
queue state update must be atomic
session state update must be atomic
only one active lease may exist per task
only lease owner may mark task RUNNING or DONE
stale lease must be recovered before another worker can claim the task
concurrent claims must result in exactly one winner
losing claim must produce DENIED evidence
```

Acceptable v1 locking approach:

```text
atomic create for lock files
atomic replace for state JSON
lease files with expires_at
recovery scan for stale locks
no long-lived daemon required
```

Atomic write protocol:

```text
write to temporary file in same directory
fsync file where available
atomic replace target
write evidence after successful state transition
preserve failed temporary files only if useful for recovery and evidence
```

Forbidden:

```text
silent lock override
best-effort claim without evidence
marking task running without a lease
marking task done without ownership
shared mutable in-memory queue as only source of truth
```

---

# 19. Crash Recovery Contract

Crash recovery must restore a safe queue state after interrupted work.

Recovery must handle:

```text
stale active lease
session heartbeat timeout
missing latest session file
partial queue_state write
corrupt JSON artifact
interrupted retry update
task marked RUNNING but lease expired
task claimed but never started
task completed but evidence missing
```

Recovery rules:

```text
never assume task completed without completion evidence
never continue mutating work after unknown crash state
prefer BLOCKED or RECOVERING over unsafe READY
preserve corrupt artifacts for inspection
write recovery evidence
record all recovered task IDs
require policy check before requeueing risky tasks
```

A crash recovery record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_recovery.schema.json",
  "recovery_id": "string",
  "timestamp": "string",
  "source_component": "TaskQueueSessionScheduler",
  "affected_task_ids": [],
  "affected_session_ids": [],
  "affected_lease_ids": [],
  "detected_condition": "string",
  "recovery_action": "string",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID|RECOVERY_REQUIRED",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 20. Failed Task Recording Contract

Failed tasks must be recorded as durable failure records.

A task failure record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_failure.schema.json",
  "failure_id": "string",
  "created_at": "string",
  "task_id": "string",
  "session_id": "string|null",
  "attempt_number": 0,
  "failure_class": "string",
  "failure_source": "SCHEDULER|POLICY|SANDBOX|TOOL|PATCH|MODEL|UNKNOWN",
  "message": "string",
  "retry_allowed": false,
  "blocks_dependent_tasks": true,
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Failure rules:

```text
failed task must not disappear from queue
failed task must have failure_class
failed task must reference attempt number
failed task must record whether retry is allowed
failed task must record whether dependents are blocked
failure must be written before queue state marks task FAILED
```

---

# 21. Audit / Evidence Contract

Scheduler audit events must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_audit.schema.json",
  "audit_id": "string",
  "timestamp": "string",
  "source_component": "TaskQueueSessionScheduler",
  "event_type": "string",
  "task_id": "string|null",
  "session_id": "string|null",
  "claim_id": "string|null",
  "lease_id": "string|null",
  "status": "SUCCESS|PARTIAL|BLOCKED|FAILED|INVALID|RECOVERY_REQUIRED",
  "message": "string",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Required evidence behavior:

```text
append-only JSONL for history
atomic JSON write for latest state
schema validation before final state write where possible
redact secrets before durable logging
record policy decision refs
record lease decision refs
record recovery refs
record queue hash and session refs
record transition IDs
```

Evidence must not include:

```text
raw secrets
provider credentials
unredacted command output
large raw prompt text
unbounded model output
```

---

# 22. Evidence Manifest and Hashing Contract

Create:

```text
.agentx-init/scheduler/scheduler_evidence_manifest.json
```

The evidence manifest must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_evidence_manifest.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
  "created_at": "string",
  "validated_commit": "string|null",
  "runtime_artifact_root": ".agentx-init/scheduler/",
  "queue_state_path": "string|null",
  "scheduler_state_path": "string|null",
  "evidence_files": [],
  "evidence_file_hashes": [],
  "deviation_register": [],
  "warnings": [],
  "errors": []
}
```

Hashing rule:

```text
SHA-256 hashes are required for final evidence files.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.
```

Runtime artifact boundary:

```text
Scheduler-owned runtime artifacts must be under .agentx-init/scheduler/.
Writes outside that root require a deviation entry.
Delegated writes by approved downstream components must reference the owning component evidence.
```

---

# 23. Agent_X Integration Notes

## 23.1 Orchestrator Integration

The orchestrator may create tasks, inspect queue state, claim ready work, and close sessions through this layer.

The orchestrator must not:

```text
write queue files directly
mark tasks DONE without scheduler API
bypass leases
bypass policy checks
start background work outside a session
```

## 23.2 Tool / MCP Adapter Integration

Queued tasks that call tools must go through the Tool / MCP Adapter.

Required rule:

```text
scheduler decides when a tool-call task may be eligible to run
tool adapter decides whether the tool call is allowed
```

The scheduler must not directly execute raw tools.

## 23.3 Policy / Capability Registry Integration

Every task claim and every risky task transition must check policy.

Policy must decide:

```text
role may create task
role may claim task
task type allowed
source mutation allowed
command execution allowed
network allowed
human approval required
governance required
retry allowed
cancel allowed
resume allowed
```

Policy unavailable means:

```text
read-only inspection may continue
risky claim blocks
mutating task blocks
command task blocks
network task blocks
retry of risky task blocks
```

## 23.4 Security Sandbox Integration

Scheduler must not validate paths itself as the final authority.

If a task involves files, paths, commands, or source mutation, the downstream tool/patch layer must call the Security Sandbox before execution.

The scheduler may store sandbox decision references but must not replace sandbox enforcement.

## 23.5 Failure Taxonomy Integration

Every blocked, failed, or invalid scheduler action must map to a failure class.

Examples:

```text
SCHEDULER_TASK_INVALID
SCHEDULER_POLICY_DENIED
SCHEDULER_LEASE_CONFLICT
SCHEDULER_LEASE_EXPIRED
SCHEDULER_SESSION_CLOSED
SCHEDULER_QUEUE_CORRUPT
SCHEDULER_DUPLICATE_EXECUTION_BLOCKED
SCHEDULER_RETRY_DENIED
SCHEDULER_RECOVERY_REQUIRED
UNKNOWN_SCHEDULER_FAILURE
```

## 23.6 Monitoring / Observability Integration

If the Monitoring / Observability Layer exists, this layer may emit metrics/events for:

```text
tasks queued
tasks running
tasks completed
tasks failed
tasks blocked
lease conflicts
stale leases
retry counts
recovery counts
```

Metrics must not replace evidence.

## 23.7 MCP Exposure Boundary

If scheduler operations are exposed through MCP later, MCP exposure must be read-only by default.

Allowed by default:

```text
inspect queue state
inspect task status
inspect session status
inspect audit summaries
```

Blocked by default:

```text
create task
claim task
cancel task
retry task
resume session
close session
start runner
mutating scheduler operation
```

MCP scheduler exposure requires a separate acceptance pass if implemented.

---

# 24. OpenCode / Coding-Agent Borrowing Notes

## 24.1 Concepts to Borrow

Borrow these coding-agent concepts:

```text
task queue
session state
work item lifecycle
plan/todo tracking
claiming work before execution
structured status updates
retry-limited execution
append-only event history
worker-safe state transitions
human-readable queue reports
```

## 24.2 Concepts to Restrict

Do not copy these assumptions directly:

```text
free-form task execution
implicit background workers
direct shell execution from scheduler
unbounded retries
session state stored only in memory
marking work done from model output alone
auto-claiming unsafe tasks
network-enabled scheduling by default
```

## 24.3 Agent_X Mapping

| Coding-agent concept | Agent_X scheduler equivalent | Required control |
|---|---|---|
| todo item | `TaskRecord` | schema + evidence |
| task queue | `QueueState` | atomic persistence |
| worker session | `SessionRecord` | heartbeat + lifecycle |
| task claim | `TaskClaim` | policy + atomic claim |
| task lock | `TaskLease` | expiration + recovery |
| retry | `TaskRetry` | bounded policy-controlled retry |
| task failure | `TaskFailure` | failure taxonomy + evidence |
| background worker | explicit session runner | no auto-start daemon |
| status update | scheduler audit event | append-only evidence |

---

# 25. Task Lifecycle

Required lifecycle states:

```text
PENDING
READY
CLAIMED
RUNNING
BLOCKED
FAILED
CANCELLED
DONE
RECOVERING
```

Allowed transitions:

```text
PENDING -> READY
PENDING -> BLOCKED
READY -> CLAIMED
CLAIMED -> RUNNING
CLAIMED -> READY, if claim expires safely
CLAIMED -> RECOVERING, if claim state is uncertain
RUNNING -> DONE
RUNNING -> FAILED
RUNNING -> BLOCKED
RUNNING -> RECOVERING, if session/lease state becomes uncertain
RECOVERING -> READY, only if safe recovery permits
RECOVERING -> BLOCKED, if safety is uncertain
FAILED -> READY, only through policy-approved retry
BLOCKED -> READY, only after blocker resolved
PENDING/READY/CLAIMED/RUNNING/BLOCKED/FAILED/RECOVERING -> CANCELLED, if policy permits
```

Forbidden transitions:

```text
PENDING -> DONE
READY -> DONE
FAILED -> DONE without execution evidence
BLOCKED -> RUNNING without blocker resolution
RUNNING -> READY without recovery evidence
RECOVERING -> DONE without completion evidence
CANCELLED -> RUNNING
DONE -> RUNNING
```

---

# 26. Session Lifecycle

Required lifecycle states:

```text
CREATED
ACTIVE
PAUSED
RECOVERING
CLOSING
CLOSED
FAILED
```

Allowed transitions:

```text
CREATED -> ACTIVE
ACTIVE -> PAUSED
PAUSED -> ACTIVE
ACTIVE -> CLOSING
CLOSING -> CLOSED
ACTIVE -> FAILED
FAILED -> RECOVERING
RECOVERING -> ACTIVE
RECOVERING -> CLOSED
```

Rules:

```text
only ACTIVE sessions may claim tasks
PAUSED sessions may not hold active leases unless explicitly allowed
CLOSED sessions may not claim, renew, or complete tasks
FAILED sessions must trigger recovery before reusing tasks
session close must release or resolve active leases
```

---

# 27. Duplicate Execution Prevention

The scheduler must prevent duplicate execution through:

```text
idempotency_key
idempotency_scope
single active lease per task
atomic claim operation
queue state version check
session ownership check
lease expiration check
completion evidence check
```

Duplicate prevention rules:

```text
same idempotency_key cannot create multiple active equivalent tasks unless policy allows
same task cannot be RUNNING in two sessions
same task cannot have two ACTIVE leases
task cannot be marked DONE twice without idempotent completion handling
claim conflict must return BLOCKED or DENIED with evidence
```

---

# 28. Queue Persistence Rules

The queue must be persisted as durable runtime state.

Required persistence rules:

```text
append task records to task history
write latest queue_state atomically
write session history append-only
write latest session atomically
write claim/lease/retry/failure histories append-only
preserve malformed/corrupt artifacts during recovery
never use in-memory state as sole source of truth
```

Approved runtime artifact root:

```text
.agentx-init/scheduler/
```

Unapproved writes outside this root are not allowed unless delegated to an approved Agent_X component and evidenced.

---

# 29. Public API Contract

Expected public classes:

```text
TaskRecord
SessionRecord
QueueState
SchedulerState
TaskDependency
TaskClaim
TaskLease
TaskRetry
TaskFailure
SchedulerPolicy
SchedulerRecoveryRecord
SchedulerAuditEvent
```

Expected public functions:

```python
create_task(arguments: dict, context: dict) -> TaskRecord
validate_task(task: TaskRecord) -> list[str]
enqueue_task(task: TaskRecord, repo_root: Path) -> QueueState
get_queue_state(repo_root: Path) -> QueueState
evaluate_dependencies(task_id: str, repo_root: Path) -> list[TaskDependency]
claim_next_task(session: SessionRecord, repo_root: Path) -> TaskClaim
claim_task(task_id: str, session: SessionRecord, repo_root: Path) -> TaskClaim
renew_lease(lease_id: str, session: SessionRecord, repo_root: Path) -> TaskLease
release_lease(lease_id: str, session: SessionRecord, repo_root: Path) -> TaskLease
start_session(context: dict, repo_root: Path) -> SessionRecord
resume_session(session_id: str, repo_root: Path) -> SessionRecord
pause_session(session_id: str, repo_root: Path) -> SessionRecord
close_session(session_id: str, repo_root: Path) -> SessionRecord
record_task_failure(task_id: str, failure: TaskFailure, repo_root: Path) -> QueueState
schedule_retry(task_id: str, failure: TaskFailure, repo_root: Path) -> TaskRetry
recover_stale_sessions(repo_root: Path) -> SchedulerState
write_scheduler_audit(event: SchedulerAuditEvent, repo_root: Path) -> dict
write_scheduler_evidence_manifest(repo_root: Path) -> dict
```

---

# 30. Scheduler Execution Pipeline

Every scheduler operation must follow this pipeline:

```text
1. Receive request.
2. Normalize context.
3. Validate input schema.
4. Load queue state.
5. Load session state, if applicable.
6. Check scheduler policy.
7. Check task/session status.
8. Check dependencies.
9. Check claim/lease ownership.
10. Acquire operation lock where required.
11. Perform atomic state transition.
12. Persist state.
13. Write audit/evidence.
14. Release operation lock.
15. Return schema-valid result.
```

No operation may skip policy, status, dependency, lease, lock, or evidence checks when they apply.

---

# 31. Security Rules

The scheduler must enforce:

```text
no automatic background execution
no raw shell
no direct source mutation
no direct patch application
no Git write
no network by default
no model execution
no task completion without evidence
no duplicate active lease
no closed-session task claim
no unbounded retry
no silent crash recovery
no hidden queue state mutation
no MCP mutating exposure by default
```

---

# 32. Scheduler Operating Modes

The scheduler must support explicit operating modes. It must not silently become a background executor.

Allowed modes:

```text
LIBRARY_ONLY
MANUAL_RUNNER
CONTROLLED_ORCHESTRATOR_CALL
DRY_RUN_REPLAY
RECOVERY_ONLY
```

Forbidden default behavior:

```text
auto-start background daemon
implicit worker loop on import
unbounded polling loop
network listener
MCP server start
raw shell execution
model execution
source mutation
```

Mode rules:

```text
LIBRARY_ONLY may read/write scheduler state through explicit API calls only.
MANUAL_RUNNER may process eligible tasks only when explicitly invoked.
CONTROLLED_ORCHESTRATOR_CALL may claim and advance tasks only through orchestrator-approved context.
DRY_RUN_REPLAY may replay history and calculate decisions without mutating queue state.
RECOVERY_ONLY may inspect, recover, or block uncertain state, but must not execute queued work.
```

A scheduler mode record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_mode.schema.json",
  "mode_id": "string",
  "created_at": "string",
  "source_component": "TaskQueueSessionScheduler",
  "mode": "LIBRARY_ONLY|MANUAL_RUNNER|CONTROLLED_ORCHESTRATOR_CALL|DRY_RUN_REPLAY|RECOVERY_ONLY",
  "auto_start_enabled": false,
  "network_listener_enabled": false,
  "mcp_runtime_enabled": false,
  "worker_loop_enabled": false,
  "policy_context_ref": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 33. Priority, Ordering, and Starvation Contract

Task ordering must be deterministic and evidence-backed.

Ordering keys, in priority order:

```text
1. dependency satisfaction status
2. task priority, higher first
3. retry_after timestamp, if retry is scheduled
4. created_at timestamp, older first
5. task_id lexicographic order as final deterministic tie-breaker
```

Priority rules:

```text
priority must be an integer
negative priority is allowed only if policy permits
priority cannot bypass dependency checks
priority cannot bypass policy checks
priority cannot bypass lease checks
priority cannot make a risky task executable without downstream authorities
```

Starvation rules:

```text
low-priority READY tasks must remain visible in queue state
blocked tasks must record blocker reason
aging may be added later only through policy
starvation detection may report long-waiting tasks but must not auto-raise risky priority without policy
```

---

# 34. Cancellation, Drain, and Emergency Stop Contract

The scheduler must distinguish cancellation, graceful draining, and emergency stop.

Cancellation rules:

```text
PENDING or READY task may be cancelled if policy permits
CLAIMED task may be cancelled only by lease owner or authorized controller
RUNNING task cancellation must not assume execution stopped unless downstream component confirms stop or safe boundary
DONE task may not be cancelled
CANCELLED task may not resume without explicit new task or policy-approved restore
cancellation must write evidence
cancellation must update queue state atomically
```

Drain rules:

```text
drain mode stops new claims
active leases remain visible
running tasks are allowed to finish or move to RECOVERING/BLOCKED by policy
drain mode must be evidenced
```

Emergency stop rules:

```text
emergency stop prevents new claims immediately
emergency stop must not delete queue state
emergency stop must not mark running work DONE
emergency stop writes audit evidence
emergency stop requires recovery before risky work resumes
```

A cancellation record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "task_cancellation.schema.json",
  "cancellation_id": "string",
  "created_at": "string",
  "task_id": "string",
  "session_id": "string|null",
  "requested_by_role": "string",
  "reason": "string",
  "previous_status": "string",
  "new_status": "CANCELLED|BLOCKED|RECOVERING",
  "policy_decision_ref": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 35. Task Type / Effect Authority Matrix

Task scheduling does not grant execution authority. Every task type must map to required downstream authorities.

| Task effect | Scheduler may queue? | Scheduler may execute directly? | Required downstream authority | Default |
|---|---:|---:|---|---|
| READ_STATE | Yes | No direct raw IO unless scheduler state only | Policy if external state | Allowed for known roles |
| PLAN | Yes | No | Initiator / Orchestrator | Allowed if policy permits |
| TOOL_CALL | Yes | No | Tool / MCP Adapter | Block until adapter allows |
| SOURCE_MUTATION | Yes | No | Policy + Sandbox + Governed Patch Execution | Blocked |
| COMMAND_EXECUTION | Yes | No | Tool Adapter + Command Acceptance Criteria + Sandbox | Blocked |
| MODEL_EXECUTION | Yes | No | Model Adapter / LLM Worker | Blocked |
| NETWORK_USE | Yes | No | Policy + explicit provider/network mode | Blocked |
| GIT_WRITE | Yes | No | Git Integration + Human/Governance approval | Blocked |
| PROMOTION | Yes | No | Promotion / Release Gate | Blocked |

Rules:

```text
queue eligibility is not execution permission
READY means dependencies and scheduler policy allow consideration
EXECUTABLE means downstream authorities have also approved the operation
scheduler must store required_authorities on risky tasks
missing authority keeps task BLOCKED or READY_WAITING_AUTHORITY, not RUNNING
```

---

# 36. Two-Phase Readiness and Execution Handoff Contract

The scheduler must separate readiness from execution handoff.

Phase 1 — Scheduler readiness:

```text
task schema valid
dependencies satisfied
queue policy allows task to become READY
no active lease conflict
retry/backoff window satisfied
session eligible to claim
```

Phase 2 — Execution handoff readiness:

```text
Policy / Capability Registry allows the requested operation
Tool / MCP Adapter accepts the tool call, if applicable
Security Sandbox permits path/file/command scope, if applicable
Governed Patch Execution permits patch session, if applicable
Human/governance approval exists, if required
Model Adapter exists and permits model task, if applicable
```

Rules:

```text
READY does not mean RUNNING
CLAIMED does not mean downstream execution is allowed
RUNNING requires active lease and handoff approval
if handoff is denied, task becomes BLOCKED or FAILED based on failure class
handoff denial must write evidence
```

---

# 37. Transition Log Contract

Every state transition must be replayable.

A scheduler transition record must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_transition.schema.json",
  "transition_id": "string",
  "created_at": "string",
  "source_component": "TaskQueueSessionScheduler",
  "entity_type": "TASK|SESSION|CLAIM|LEASE|QUEUE|SCHEDULER|RETRY|RECOVERY",
  "entity_id": "string",
  "previous_status": "string|null",
  "new_status": "string",
  "previous_hash": "string|null",
  "new_hash": "string",
  "reason": "string",
  "policy_decision_ref": "string|null",
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

Transition rules:

```text
transition records are append-only
state transition must be persisted before dependent transition is attempted
transition ID must be referenced by queue state or scheduler audit
transition hash must cover the transitioned entity after redaction
missing transition evidence blocks final DONE
```

---

# 38. Snapshot, Compaction, and Replay Contract

The queue may grow over time. Compaction is allowed only when history remains auditable.

Rules:

```text
append-only histories are the source of truth for audit
latest JSON snapshots are convenience artifacts, not sole truth
compaction must preserve prior evidence hashes or produce a signed/hash-linked snapshot manifest
corrupt history lines must be preserved, not deleted silently
replay from history must either reconstruct the latest state or report RECOVERY_REQUIRED
snapshot mismatch with history hash blocks risky scheduling
```

A snapshot manifest must include:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_snapshot_manifest.schema.json",
  "snapshot_id": "string",
  "created_at": "string",
  "source_component": "TaskQueueSessionScheduler",
  "covered_history_files": [],
  "covered_transition_ids": [],
  "snapshot_files": [],
  "snapshot_hashes": [],
  "previous_snapshot_hash": "string|null",
  "evidence_refs": [],
  "warnings": [],
  "errors": []
}
```

---

# 39. Schema Example and Validation Contract

Every scheduler schema must have explicit positive and negative examples in tests.

Required examples:

```text
valid_task_record
valid_session_record
valid_queue_state
valid_scheduler_state
valid_task_dependency
valid_task_claim
valid_task_lease
valid_task_retry
valid_task_failure
valid_scheduler_policy
valid_scheduler_recovery
valid_scheduler_audit
valid_scheduler_transition
valid_scheduler_mode
valid_task_cancellation
valid_scheduler_evidence_manifest
valid_scheduler_completion_record
```

Each schema test must prove:

```text
valid example passes
missing required field fails
invalid enum value fails
wrong type fails for ID/status/list fields
unsafe default is rejected where applicable
```

---

# 40. Review-Ready Evidence and Source-Mutation Proof

The implementation spec and review / DoD document must require review-ready evidence.

Minimum final validation evidence:

```text
reviewed commit
review environment
compileall command, exit code, and output summary
pytest command, exit code, and output summary
schema validation command, exit code, and output summary
initial git status
final git status
evidence manifest with SHA-256 hashes
completion record
source mutation check
runtime artifact boundary check
negative-test summary
```

Source-mutation proof:

```text
scheduler tests must not modify source files
scheduler runtime artifacts must stay under .agentx-init/scheduler/
delegated downstream artifacts must identify owning component
final git status must be CLEAN or expected runtime artifacts only
```

---

# 41. Test Acceptance Criteria

Required tests:

```text
test_task_record_schema_accepts_valid_task
test_task_record_schema_rejects_missing_task_id
test_session_record_schema_accepts_valid_session
test_queue_state_schema_rejects_duplicate_bucket_membership
test_dependency_cycle_blocks_readiness
test_create_task_writes_evidence
test_enqueue_task_updates_queue_state
test_claim_next_task_grants_single_lease
test_concurrent_claims_have_one_winner
test_duplicate_claim_is_denied_with_evidence
test_closed_session_cannot_claim_task
test_lease_expiration_does_not_mark_done
test_stale_lease_recovery_records_evidence
test_retry_denied_after_max_attempts
test_policy_denied_task_blocks
test_failed_task_records_failure_class
test_crash_recovery_preserves_corrupt_artifact
test_queue_state_written_atomically
test_session_resume_requires_existing_session
test_scheduler_does_not_execute_raw_shell
test_scheduler_does_not_mutate_source
test_scheduler_evidence_redacts_secrets
test_scheduler_evidence_manifest_contains_hashes
test_scheduler_does_not_auto_start_background_worker
test_priority_ordering_is_deterministic
test_emergency_stop_blocks_new_claims
test_running_task_cancellation_does_not_mark_done
test_ready_task_requires_handoff_before_running
test_transition_log_is_append_only
test_snapshot_replay_detects_hash_mismatch
```

Definition of Done requires:

```text
compileall PASS
pytest PASS
schema validation PASS
negative safety tests PASS
no source mutation
no raw shell
no network by default
no duplicate active lease
evidence written for every scheduler transition
completion record exists
```

---

# 42. Implementation Slices

Build this layer in small slices.

## 42.1 Slice A — Models and Schemas

Implement:

```text
scheduler_models.py
all scheduler schemas
schema validation tests
```

Acceptance:

```text
dataclasses instantiate
schemas validate valid records
schemas reject missing required fields
schemas reject invalid statuses
```

## 42.2 Slice B — Queue and Session Stores

Implement:

```text
task_queue.py
session_store.py
scheduler_state.py
```

Acceptance:

```text
tasks can be created and queued
queue state persists atomically
sessions can be started/resumed/closed
state is durable under .agentx-init/scheduler/
```

## 42.3 Slice C — Claims, Leases, and Locking

Implement:

```text
lease_manager.py
scheduler_locks.py
claim logic
atomic lock behavior
```

Acceptance:

```text
single active lease per task
concurrent claims produce one winner
duplicate claim is denied with evidence
lease expiration is recoverable
```

## 42.4 Slice D — Retry and Failure Handling

Implement:

```text
retry_policy.py
failure recording
backoff records
```

Acceptance:

```text
failures are durable
retry is bounded
unsafe failures do not retry automatically
max attempts enforced
```

## 42.5 Slice E — Audit, Hashing, and Crash Recovery

Implement:

```text
scheduler_audit.py
scheduler_hashing.py
crash_recovery.py
```

Acceptance:

```text
all transitions write evidence
stale locks are detected
crash recovery preserves corrupt files
recovery never assumes completion without evidence
evidence manifest contains hashes
```

## 42.6 Slice F — Queue Runner / Integration Surface

Implement:

```text
queue_runner.py
orchestrator-safe public API
```

Acceptance:

```text
runner does not auto-start
runner does not raw-shell
runner does not mutate source
runner delegates tool execution to Tool / MCP Adapter
```

---

# 43. Pre-Code Gate

Implementation must not begin unless:

```text
[ ] canonical subdirectory is selected
[ ] runtime artifact root is selected
[ ] task schema is defined
[ ] session schema is defined
[ ] queue state schema is defined
[ ] scheduler state schema is defined
[ ] dependency schema is defined
[ ] claim/lease schema is defined
[ ] retry/backoff contract is defined
[ ] crash recovery contract is defined
[ ] concurrency/locking contract is defined
[ ] evidence paths are defined
[ ] Agent_X integration boundaries are defined
[ ] OpenCode/coding-agent borrowing is bounded
```

---

# 44. Post-Code Gate

After implementation:

```text
[ ] target files exist
[ ] schemas exist
[ ] tests exist
[ ] compileall passes
[ ] pytest passes
[ ] schema validation passes
[ ] task queue persists state
[ ] session lifecycle works
[ ] dependencies are evaluated safely
[ ] claims/leases prevent duplicate execution
[ ] retries are bounded
[ ] stale locks recover safely
[ ] failed tasks are recorded
[ ] crash recovery writes evidence
[ ] evidence manifest includes hashes
[ ] no raw shell occurs
[ ] no source mutation occurs
[ ] no network is enabled by default
[ ] completion record exists
```

---

# 45. Completion Evidence Contract

Completion evidence must include:

```yaml
completion_record:
  component_id: "AGENTX_TASK_QUEUE_SESSION_SCHEDULER"
  status: "VALIDATED|IMPLEMENTED_UNVALIDATED|BLOCKED"
  validated_commit: "<commit hash>"
  validated_at: "<UTC timestamp>"
  files_created_or_changed: []
  schemas_created_or_changed: []
  tests_created_or_changed: []
  commands_run: []
  artifacts_generated: []
  task_queue_coverage_verified: []
  session_lifecycle_verified: []
  dependency_handling_verified: []
  lease_locking_verified: []
  retry_backoff_verified: []
  crash_recovery_verified: []
  duplicate_execution_prevention_verified: []
  policy_integration_verified: []
  tool_adapter_integration_verified: []
  evidence_verified: []
  evidence_hashes_verified: []
  deviations_from_contract: []
  unresolved_risks: []
  final_decision: "DONE|NOT_DONE"
```

---

# 46. Residual Risks

```yaml
residual_risks:
  - id: "SCHEDULER-RISK-001"
    description: "Duplicate workers could execute the same task if claim/lease locking is weak."
    severity: "critical"
    mitigation: "Atomic claim, single active lease per task, concurrent claim tests."
  - id: "SCHEDULER-RISK-002"
    description: "Stale sessions could block the queue forever."
    severity: "high"
    mitigation: "Lease expiration, heartbeat checks, crash recovery tests."
  - id: "SCHEDULER-RISK-003"
    description: "Unsafe retries could repeat source mutation or command execution."
    severity: "critical"
    mitigation: "Retry disabled by default; policy-controlled retries; idempotency keys."
  - id: "SCHEDULER-RISK-004"
    description: "Queue state corruption could cause lost or duplicated tasks."
    severity: "high"
    mitigation: "Append-only histories, atomic latest state writes, recovery preservation."
  - id: "SCHEDULER-RISK-005"
    description: "Scheduler could become a hidden background executor."
    severity: "critical"
    mitigation: "No auto-start daemon; explicit sessions only; tool execution delegated to Tool / MCP Adapter."
  - id: "SCHEDULER-RISK-006"
    description: "Task dependencies could deadlock or create cycles."
    severity: "high"
    mitigation: "DAG validation, cycle tests, dependency readiness evidence."
```

---

# 47. Definition of Done

The Task Queue / Session Scheduler is done when it can safely control queued Agent_X work.

It must prove:

```text
tasks are schema-valid
sessions are schema-valid
queue state is schema-valid
scheduler state is schema-valid
tasks can be queued
task dependencies are checked
dependency cycles are blocked
tasks can be claimed atomically
single active lease per task is enforced
sessions can be started, resumed, paused, and closed
closed sessions cannot claim tasks
stale leases recover safely
duplicate execution is prevented
failed tasks are recorded with failure classes
retry/backoff is bounded and policy-aware
crash recovery writes evidence
queue state is persisted atomically
scheduler state is evidenced
evidence manifest includes hashes
orchestrator interaction goes through scheduler API
Tool / MCP Adapter integration is delegated, not bypassed
policy checks run for risky scheduler operations
no raw shell executes
no source mutation occurs directly in this layer
no network is enabled by default
completion record exists
```

Final command proof:

```bash
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
git status --short
```

Expected:

```text
compileall PASS
pytest PASS
schema validation PASS
git status CLEAN or only expected runtime artifacts
```

---

# 48. GO / NO-GO Rules

## 48.1 GO Criteria

The layer may be marked DONE only if:

```text
all target files exist
all schemas exist
all tests exist
compileall passes
pytest passes
schema validation passes
task queue state persists
session state persists
dependency checks work
atomic claim works
single active lease per task is enforced
retry/backoff is bounded
crash recovery preserves evidence
no duplicate active lease is possible
no raw shell executes
no source mutation occurs directly
no network is enabled by default
evidence manifest exists
evidence hashes exist
completion record exists
```

## 48.2 NO-GO Conditions

The layer must remain NOT DONE if any are true:

```text
compileall fails
pytest fails
schema validation fails
task queue state is not persisted
session state is not persisted
task dependency cycle is accepted
two active leases can exist for one task
duplicate task execution is possible
closed session can claim a task
stale lease cannot be recovered
failed task disappears from queue
retry exceeds max attempts
unsafe retry occurs automatically
scheduler executes raw shell
scheduler mutates source directly
scheduler enables network by default
scheduler marks task DONE without completion evidence
queue corruption is silently overwritten
scheduler evidence is missing
evidence hashes are missing
secrets are logged unredacted
completion record is missing
```

---

# 49.1 Task Payload Safety and Redaction Contract

Task payloads may contain paths, proposed commands, tool arguments, prompt fragments, model instructions, user text, or artifact references. The scheduler must treat all task payload content as untrusted data.

A task payload contract must enforce:

```text
payload is schema-valid object data, not executable code
payload is never evaluated as Python, shell, template code, or policy expression
payload fields are redacted before durable evidence when they may contain secrets
payload size is bounded before persistence
payload references artifacts by path/ref where possible instead of embedding large raw content
payload prompt text, if any, is stored only when explicitly needed and redacted/minimized
payload command text is treated as data and cannot execute from scheduler layer
payload paths are not trusted until downstream Sandbox checks them
payload tool arguments are not trusted until Tool / MCP Adapter validates them
```

Required redaction targets:

```text
API keys
tokens
passwords
private keys
provider credentials
environment values
cookies
session IDs not needed for audit
large raw prompt text
large model output
raw command output
unreviewed file contents
```

Prompt-injection handling rule:

```text
Task descriptions, prompt fragments, artifact text, and model-generated payload fields must never alter scheduler policy, dependency rules, lease rules, retry rules, or evidence behavior. They are task data only.
```

---

# 49.2 Scheduler API Authorization Matrix

Scheduler APIs must define who may perform each scheduler operation. Queue state alone does not authorize the operation.

| Operation | Allowed by default | Requires policy? | Requires active session? | Notes |
|---|---:|---:|---:|---|
| Inspect queue | Known read roles | Yes for non-public state | No | Redacted summaries only by default |
| Create task | Orchestrator / approved controller | Yes | No | Risky task types block without policy |
| Enqueue task | Orchestrator / approved controller | Yes | No | Must write task evidence |
| Evaluate dependencies | Scheduler / Orchestrator | Yes for risky tasks | No | No execution authority granted |
| Start session | Orchestrator / approved worker | Yes | No | Must persist before claim |
| Resume session | Owner / approved controller | Yes | Existing session | Must reference prior evidence |
| Claim task | Active session owner | Yes | Yes | Atomic claim required |
| Renew lease | Lease owner | Yes | Yes | Heartbeat required |
| Release lease | Lease owner / recovery controller | Yes | Usually yes | Must not mark DONE |
| Complete task | Lease owner | Yes | Yes | Completion evidence required |
| Fail task | Lease owner / recovery controller | Yes | Context-dependent | Failure record required |
| Retry task | Orchestrator / scheduler policy | Yes | No | Bounded by max attempts |
| Cancel task | Owner / authorized controller | Yes | Context-dependent | Running task needs downstream acknowledgement |
| Drain queue | Orchestrator / operator | Yes | No | Stops new claims only |
| Emergency stop | Human/operator/orchestrator policy | Yes | No | Stops new claims immediately |
| Recover stale state | Recovery controller | Yes | No | Must write recovery evidence |

Forbidden by default:

```text
UNKNOWN_CALLER performing any scheduler mutation
MCP_CLIENT performing scheduler mutation
closed session claiming work
lease non-owner marking work complete
policy-missing risky operation proceeding
```

---

# 49.3 Local Filesystem Locking Boundary

The v1 scheduler locking model is local-repository and local-filesystem oriented unless a later major revision adds a distributed lock service.

Allowed v1 assumption:

```text
single repository working tree
local filesystem artifacts
atomic file create/replace semantics provided by the host OS
explicit scheduler API calls, not hidden background workers
```

Not guaranteed in v1:

```text
distributed multi-host locking
network filesystem lock correctness
cross-machine lease arbitration
remote worker crash detection
clock-synchronized distributed scheduling
```

If distributed execution is added later, it requires a major revision defining:

```text
distributed lock authority
clock-skew tolerance
lease quorum or compare-and-swap mechanism
remote heartbeat protocol
conflict resolution
distributed recovery tests
```

Until then, tests must simulate concurrent local claims and prove exactly one local winner.

---

# 49.4 Clock, Monotonic Time, and Expiry Rules

The scheduler must use UTC timestamps for durable records and monotonic elapsed time where the implementation needs elapsed comparisons inside one process.

Rules:

```text
durable timestamps use UTC ISO-8601
lease expires_at is persisted as UTC ISO-8601
retry_after is persisted as UTC ISO-8601
heartbeat timestamps are persisted as UTC ISO-8601
same-process elapsed timers should use monotonic time when available
clock rollback must not mark tasks DONE
clock uncertainty must prefer BLOCKED or RECOVERING over READY/RUNNING
recovery must record the observed current time used for expiry decisions
```

Forbidden:

```text
local timezone timestamps in persisted records
implicit timezone parsing
marking expired work complete because of clock anomaly
unbounded lease renewal without recorded time evidence
```

---

# 49.5 Hash Chain and Tamper-Evidence Contract

The scheduler must make state history tamper-evident.

Required hash behavior:

```text
queue_state.queue_hash covers redacted queue state content
queue_state.previous_queue_hash links to previous queue state
transition.new_hash covers redacted transitioned entity content
transition.previous_hash links to prior entity hash when available
snapshot_manifest.snapshot_hashes cover snapshot files
evidence_manifest.evidence_file_hashes cover all final evidence files
completion record references evidence manifest hash
```

Rules:

```text
hashes use SHA-256
hash input must use deterministic JSON serialization
redaction must occur before hash when raw secrets would otherwise be hashed into evidence
missing expected hash blocks final DONE
hash mismatch triggers RECOVERY_REQUIRED and blocks risky scheduling
manual edits to runtime artifacts after validation invalidate prior DONE evidence
```

---

# 49.6 Schema Versioning and Migration Contract

Scheduler artifacts may outlive one implementation version. The scheduler must not silently reinterpret old artifacts.

Rules:

```text
every persisted artifact includes schema_version and schema_id
unknown schema_id blocks normal processing
unsupported schema_version triggers RECOVERY_REQUIRED or explicit migration path
migration must preserve original artifact and write migration evidence
migration must not drop task history, lease history, failure history, or transition history
migration must update evidence manifest and hashes
schema downgrade is forbidden unless explicitly supported and evidenced
```

Required migration evidence fields:

```text
migration_id
source_schema_id
source_schema_version
target_schema_id
target_schema_version
input_artifact_refs
output_artifact_refs
input_hashes
output_hashes
status
warnings
errors
```

---

# 49.7 Runner Batch Limits and Fairness Bounds

A scheduler runner invocation must be bounded.

Required runner bounds:

```text
max_tasks_per_run
max_claims_per_run
max_recoveries_per_run
max_runtime_seconds_per_run
max_retries_scheduled_per_run
max_failures_processed_per_run
```

Rules:

```text
one run must not consume the entire queue unless policy explicitly permits
runner must persist progress after each successful state transition
runner must stop safely when limits are reached
runner limit hit is PARTIAL, not FAILED, if state remains consistent
runner must not bypass priority, dependency, lease, or policy rules to meet a batch goal
```

---

# 49.8 Repair Mode Contract

Repair mode is separate from normal crash recovery.

Normal recovery may:

```text
expire stale leases
move uncertain tasks to RECOVERING or BLOCKED
preserve corrupt artifacts
rebuild latest state from valid append-only history
write recovery evidence
```

Repair mode may:

```text
create repaired snapshots
quarantine corrupt artifacts
write migration/repair evidence
mark records unusable while preserving originals
```

Repair mode must not:

```text
delete corrupt artifacts silently
mark tasks DONE without completion evidence
invent missing execution evidence
rewrite append-only history in place
bypass policy to requeue risky work
```

Repair mode requires explicit invocation and must not run automatically on import.

---

# 49.9 Downstream Cancellation Acknowledgement Contract

If a task has already been handed off to Tool / MCP Adapter, Model Adapter, Governed Patch Execution, Git Integration, or any future execution layer, scheduler cancellation alone does not prove execution stopped.

Rules:

```text
scheduler cancellation records requested cancellation
downstream layer must acknowledge stopped, blocked, failed, or completed state
until acknowledgement exists, task moves to RECOVERING or BLOCKED, not CANCELLED/DONE
running source-mutation tasks require downstream patch/session evidence before safe finalization
running command/model/network tasks require downstream result or timeout evidence
```

Required acknowledgement data:

```text
downstream_component
downstream_operation_id
downstream_status
downstream_evidence_refs
received_at
safety_status
```

---

# 49.10 Minimal Retention and Sensitive Payload Policy

The scheduler should store the minimum durable payload needed for audit and recovery.

Rules:

```text
store artifact references instead of full content where possible
store redacted summaries for large prompt/model/tool data
store decision IDs instead of full downstream decision records where possible
store hashes for provenance without storing sensitive content when acceptable
apply bounded field sizes before persistence
reject or truncate oversized task payloads according to policy
```

Final evidence must prove:

```text
secret-like payloads are redacted
oversized payloads are bounded
raw file contents are not copied into scheduler logs by default
raw command output is not copied into scheduler logs by default
```

---

# 50. Final Freeze Rule

This v4 document is frozen as the controlling contract for the Task Queue / Session Scheduler layer.

Allowed future changes:

```text
PATCH: wording, examples, typo fixes
MINOR: additive optional implementation details
MAJOR: changed lifecycle states, changed lease policy, changed retry rules, changed default safety behavior, new required integration boundary
```

Blocked without major revision:

```text
allowing duplicate active leases
allowing raw shell execution
allowing source mutation directly in scheduler
allowing unbounded retries
allowing background daemon auto-start
removing policy checks
removing evidence logging
allowing network by default
marking tasks DONE without evidence
removing evidence hashing for final DONE
```

The next document should be:

```text
TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC.md
```

---

# 51. Final Rating

This v4 contract is rated:

```text
10/10
```

Reason:

```text
It preserves the strong v3 coverage and fixes the remaining final production-control gaps: task payload safety and redaction, scheduler API authorization, local-filesystem locking boundary, monotonic/UTC time rules, hash chaining and tamper evidence, schema migration/version compatibility, runner batch bounds, repair-mode separation, downstream cancellation acknowledgement, and minimal-retention rules for sensitive task payloads.
```
