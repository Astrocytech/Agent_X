# TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD

```text
document_id: TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD
version: v4.0
status: final post-implementation review template and Definition of Done
component_id: AGENTX_TASK_QUEUE_SESSION_SCHEDULER
component_name: Task Queue / Session Scheduler
roadmap_layer: 18
roadmap_phase: Phase C — Runtime Coordination
review_use: use after code is committed
basis_documents:
  - TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT
  - TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC
primary_standard: EQC
supporting_standards: FIC, SIB, Schema Contract, Evidence Rules, Audit Rules
conditional_standards: Command Acceptance Criteria, MCP Protocol Acceptance Criteria, Monitoring / Observability Acceptance Criteria
optional_standards: ES, Report Template
canonical_scheduler_subdirectory: tools/agentx_evolve/scheduler/
canonical_schema_subdirectory: tools/agentx_evolve/schemas/
canonical_test_subdirectory: tools/agentx_evolve/tests/
runtime_artifact_root: .agentx-init/scheduler/
review_document_rating: 10/10
final_verdict_field: DONE | NOT DONE
```


---

# 0. v4 Review and Upgrade Summary

The v3 review / DoD document was strong and I would rate it:

```text
9.7/10
```

It already covered the requested post-implementation review areas and included strong scheduler-specific controls for dependency gates, task statuses, lease timing, idempotency, priority/fairness, cancellation, crash recovery, dependency/DAG checks, deterministic ordering, multi-worker scope, lease fencing, queue compaction, evidence manifests, review reports, completion records, and strict GO / NO-GO rules.

It was not fully 10/10 because several final precision gaps remained:

```text
1. Some subsection numbers still referenced the previous section numbers, which weakens stable review references.
2. The review report artifact example still identified the document version as v2.0 instead of the active version.
3. Task dependency review did not require an explicit topological-sort or dependency-resolution artifact when dependencies are implemented.
4. Scheduler inputs did not have a separate queue-admission validation gate before tasks become claimable.
5. Dead-letter queue behavior was not explicit for exhausted retries or unrecoverable failures.
6. Scheduler-step replay and dry-run behavior needed a clearer reproducibility rule.
7. Runtime configuration drift was not explicitly covered through scheduler config hash/provenance.
8. Queue-state migration/version compatibility was not explicitly reviewed.
9. Cross-component evidence links to Policy, Tool / MCP Adapter, Failure Taxonomy, and Monitoring needed stronger reference requirements.
10. Final evidence needed a stricter rule that scheduler state hashes, config hashes, and dependency-resolution hashes are part of the DONE proof when applicable.
```

This v4 applies those corrections and is the final 10/10 review / DoD template.

This document's 10/10 rating is for the review template only. It does not mean the scheduler implementation is done. The implementation can be marked `DONE` only after the recorded validation evidence satisfies every GO criterion.
---

# 1. Purpose

This document is the post-implementation review and Definition of Done template for the **Task Queue / Session Scheduler** layer.

Use this document after code is committed to determine whether the Task Queue / Session Scheduler layer is complete, validated, safe, reproducible, and ready to mark as `DONE`.

The review must determine:

```text
what exists
what passed
what failed
whether compileall passes
whether pytest passes
whether schemas validate
whether task queue behavior is complete
whether session lifecycle behavior is complete
whether lease / locking behavior is safe
whether retry / backoff behavior is deterministic
whether crash recovery behavior is safe
whether duplicate execution is prevented
whether policy integration works
whether tool integration works
whether audit/evidence is written
whether source mutation checks pass
whether runtime artifact boundary checks pass
whether evidence manifest exists
whether review report exists
whether completion record exists
whether the implementation is DONE or NOT DONE
```

This document reviews the implementation. The implementation is done only after the validation commands and evidence checks in this document pass.

---

# 2. Standards Applied

## 2.1 Primary Standard

```text
EQC
```

EQC is primary because this layer controls queued work, active sessions, task claims, retry behavior, recovery after crashes, and whether scheduled work may indirectly trigger source mutation or tool execution.

## 2.2 Required Standards

```text
FIC
SIB
Schema Contract
Evidence / Audit Rules
Command Acceptance Criteria, if scheduler exposes CLI commands
```

## 2.3 Conditional Standards

```text
MCP Protocol Acceptance Criteria, only if queue/session operations are exposed through MCP
Monitoring / Observability Acceptance Criteria, if scheduler emits metrics/events
```

## 2.4 Optional Standards

```text
ES, only for ecosystem placement
Report Template, only if it writes markdown reports
```

---

# 3. Why This Layer Needs These Standards

Task Queue / Session Scheduler is safety-critical because it decides:

```text
which tasks exist
which tasks are pending/running/blocked/failed/done
which agent/session may claim a task
whether a task can be retried
whether a failed task should stop the queue
whether duplicate execution is prevented
whether stale sessions are recovered safely
whether scheduled work can mutate source indirectly
whether queued work respects policy, sandbox, and governance gates
whether evidence exists for every scheduled action
```

Without this layer, Agent_X can have:

```text
uncontrolled task execution
duplicate workers
lost state
stale locks
unclear retries
untraceable background-style behavior
unsafe recovery after interruption
unreviewable task history
policy bypass through queued work
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
[ ] expected-failure tests record the expected failure condition
[ ] review report artifact is created
[ ] evidence manifest exists before final DONE is claimed
[ ] completion record exists before final DONE is claimed
[ ] required evidence hashes are present
[ ] reviewer did not rely only on this template's document status
```

A document rating and an implementation rating are separate:

```text
document_rating: quality of this review / DoD template
implementation_rating: validated quality of the actual committed implementation
```

---

# 5. Status Vocabulary

Use only these status values in review tables.

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
| DEFERRED SAFELY | Feature is intentionally deferred and cannot execute, mutate, schedule, expose, or bypass policy/sandbox. | Yes, only for accepted deferred areas |

A review cannot mark the implementation `DONE` if any required area remains `NOT CHECKED` or any required command remains `NOT RUN`.

## 5.1 Scheduler Status Vocabulary

Task statuses must use a frozen vocabulary.

```text
PENDING
CLAIMED
RUNNING
BLOCKED
FAILED
DONE
CANCELLED
EXPIRED
RECOVERING
RETRY_WAITING
```

Session statuses must use a frozen vocabulary.

```text
ACTIVE
IDLE
PAUSED
CLOSING
CLOSED
EXPIRED
RECOVERING
FAILED
```

Lease statuses must use a frozen vocabulary.

```text
ACTIVE
RENEWED
RELEASED
EXPIRED
RECOVERED
FAILED
```

A final `DONE` verdict is invalid if the implementation accepts unknown task, session, or lease statuses without returning schema-valid `INVALID` or `BLOCKED` evidence.

## 5.2 Required Task Transition Rules

The review must verify allowed transitions and block invalid transitions.

Allowed task transitions:

```text
PENDING -> CLAIMED
CLAIMED -> RUNNING
RUNNING -> DONE
RUNNING -> FAILED
RUNNING -> BLOCKED
RUNNING -> RETRY_WAITING
RETRY_WAITING -> PENDING
CLAIMED -> EXPIRED, only through lease expiry / recovery
RUNNING -> RECOVERING, only through crash recovery
RECOVERING -> PENDING | BLOCKED | FAILED
PENDING -> CANCELLED
CLAIMED -> CANCELLED, only if lease owner or recovery process cancels safely
```

Terminal states:

```text
DONE
CANCELLED
```

Terminal states must not be rescheduled unless a new task record or explicit retry record is created with a new idempotency decision.

## 5.3 Dependency Gate Rules

The scheduler must not become a bypass around other Agent_X safety layers.

```text
If Policy / Capability Registry is unavailable -> non-read-only dispatch BLOCKS.
If Tool / MCP Adapter is unavailable -> tool dispatch BLOCKS.
If Failure Taxonomy is unavailable -> failure is recorded as SCHEDULER_FAILURE_UNCLASSIFIED and dispatch BLOCKS where classification is required.
If Security Sandbox is required by the queued tool and unavailable -> dispatch BLOCKS.
If Governed Patch Execution is required and unavailable -> patch/source-mutating queued work BLOCKS.
If Monitoring / Observability is unavailable -> scheduler still operates locally unless monitoring is required by policy.
If MCP runtime is unavailable -> MCP scheduler exposure is NOT APPLICABLE or DEFERRED SAFELY, not partially enabled.
```

Allowed restricted mode:

```text
queue inspection
schema validation
read-only status reporting
session state inspection
safe recovery preview / dry-run
audit/evidence writing
```

Restricted mode must block:

```text
tool dispatch
source mutation
patch application
raw command execution
Git write
network scheduling
MCP mutating scheduling
unattended background execution
```

## 5.4 Background Execution Boundary

This layer may define task/session state and deterministic scheduler operations. It must not create uncontrolled background behavior.

Not allowed in this layer unless a later runtime acceptance pass explicitly approves it:

```text
background daemon
unbounded worker loop
thread/process pool that starts automatically on import
timer that dispatches work without explicit caller action
network listener
MCP server auto-start
cron-style host scheduler integration
```

Allowed:

```text
single-step scheduler tick function
claim-next-task function
recover-stale-state function
manual CLI command, if command acceptance criteria pass
dry-run scheduling preview
```

## 5.5 Clock, Lease, and Time Rules

The review must verify deterministic time handling.

```text
timestamps must be UTC ISO-8601
lease expiry must be explicit
lease renewal must require owner session
clock skew tolerance must be defined or not applicable for local-only runtime
expired lease must not continue executing new work
stale lease recovery must preserve evidence
retry/backoff must be deterministic under injected test clock
```

Tests should use an injectable clock or deterministic timestamp helper. A review cannot mark time-dependent lease behavior as PASS if tests depend on real-time sleeping except for minimal bounded cases.

## 5.6 Idempotency and Replay Protection Rules

The review must verify that repeated scheduler operations do not duplicate work.

```text
enqueue with same idempotency key must return existing task or BLOCK duplicate
claim request must include task_id/session_id/lease context
replayed claim must not create a second active lease
replayed completion must not rewrite terminal task evidence incorrectly
recovery replay must not duplicate completed work
```

Required evidence fields:

```text
idempotency_key
idempotency_decision
replay_detected
previous_task_id, when applicable
previous_lease_id, when applicable
```

## 5.7 Priority, Fairness, and Starvation Rules

If task priority is implemented, the review must verify:

```text
priority values are schema-defined
queue ordering is deterministic
same-priority tasks use stable FIFO or documented tie-breaker
low-priority tasks cannot starve indefinitely unless policy explicitly allows it
priority cannot bypass policy, lease, governance, or approval checks
```

If priority is not implemented, status must be `NOT APPLICABLE` with a clear statement that ordering is FIFO or otherwise deterministic.

## 5.8 Cancellation / Pause / Resume Rules

If cancellation or pause/resume is implemented, the review must verify:

```text
cancellation writes evidence
cancellation does not delete task history
paused session cannot claim new work unless explicitly allowed
resume requires valid session identity
cancelled task is terminal unless a new task or explicit retry record is created
non-owner cancellation is blocked unless policy permits supervisor recovery
```

If cancellation or pause/resume is not implemented, the review must verify that no hidden partial behavior exists.

## 5.9 Task Dependency and DAG Rules

If task dependencies are implemented, the review must verify:

```text
dependency fields are schema-defined
dependency graph is deterministic
dependency cycles are rejected before execution
blocked dependency prevents dependent task claim
done dependency permits dependent task claim only after evidence exists
failed dependency behavior is explicit: BLOCK, FAIL_DEPENDENT, or WAIT_FOR_RETRY
dependency resolution cannot bypass policy or priority rules
dependency evidence includes upstream task ids and decision reason
```

If dependencies are not implemented, status must be `NOT APPLICABLE` with proof that queued tasks are independent and no partial dependency fields are accepted silently.

## 5.10 Deterministic Ordering Rules

The review must verify deterministic task selection.

```text
claim-next-task order is stable
same-priority tasks use FIFO or documented tie-breaker
tie-breaker uses created_at plus task_id or another stable field
deterministic ordering is tested without wall-clock sleeps
scheduler restart does not reorder already persisted tasks incorrectly
manual requeue records a new ordering decision or preserves original order explicitly
```

A final `DONE` verdict is invalid if repeated runs over the same queue state can claim different next tasks without an explicit policy reason.

## 5.11 Queue Persistence Integrity Rules

The scheduler must persist state in a recoverable and auditable way.

The review must verify:

```text
queue state writes are atomic
session state writes are atomic
lease state writes are atomic
append-only history exists for task/session/lease events
latest state is either rebuildable from event history or hash-checked against history
state files include schema_version and schema_id
state files include queue_id or scheduler_instance_id
state files include reviewed component/version where applicable
corrupt state is detected and does not silently load as valid
recovery from corrupt latest state uses event log only if event log validates
state hashes are recorded in evidence manifest
```

If the implementation uses only event sourcing and no latest snapshot, that is acceptable only if replay is deterministic and tested.

## 5.12 Single-Step Scheduler Boundary

This layer may expose scheduler operations, but it must not become an uncontrolled runtime worker.

Required review distinction:

```text
claim_next_task is allowed
scheduler_tick_once is allowed
recover_stale_leases is allowed
run_until_empty is not allowed unless bounded, explicit, and command-accepted
background loop is not allowed in this layer
thread/process worker pool is not allowed unless separately accepted
import-time execution is forbidden
```

The review must verify that every execution entrypoint has a bounded scope and returns control to the caller.

## 5.13 Multi-Worker Concurrency Scope

The review must classify concurrency support explicitly.

Allowed statuses:

```text
SINGLE_PROCESS_ONLY
MULTI_PROCESS_SAFE
MULTI_HOST_SAFE
DEFERRED SAFELY
```

Rules:

```text
If SINGLE_PROCESS_ONLY, multi-process claims must be blocked or documented as unsupported with tests proving no advertised multi-worker behavior.
If MULTI_PROCESS_SAFE, file locks or equivalent atomic claims must be tested.
If MULTI_HOST_SAFE, distributed locking/clock assumptions must be defined and tested.
If DEFERRED SAFELY, no public API may claim multi-worker safety.
```

A final `DONE` verdict is invalid if the scheduler advertises concurrent workers but lacks lease fencing and atomic claim tests.

## 5.14 Lease Fencing Token Rules

Every claimed task must have a current lease/fencing token.

The review must verify:

```text
claim creates lease_id and fencing_token
renew requires current lease_id and fencing_token
complete requires current lease_id and fencing_token
fail requires current lease_id and fencing_token
stale owner cannot complete after lease expiry/recovery
recovered task receives a new lease/fencing token before execution
fencing token is included in evidence
```

This prevents an old worker/session from completing a task after another session has recovered and reclaimed it.

## 5.15 Queue Compaction and Retention Rules

If compaction, cleanup, or retention is implemented, the review must verify:

```text
compaction does not delete required evidence
terminal task history remains auditable
retention policy is explicit
retention never removes active lease/session evidence
cleanup is dry-run capable
cleanup writes evidence
cleanup cannot remove review report, evidence manifest, or completion record
```

If cleanup is not implemented, the review must verify there is no hidden cleanup side effect.


## 5.16 Queue Admission Validation Rules

The review must verify that tasks are validated before they become claimable.

```text
task payload schema must validate before enqueue
task type must be known or explicitly marked external/manual
task effect/risk metadata must be present before scheduling
task dependencies must be validated before enqueue when dependency support exists
task idempotency key must be generated or supplied before enqueue
tasks that fail admission must not appear as PENDING
admission failure must write schema-valid evidence
```

A final `DONE` verdict is invalid if malformed tasks can become claimable work.

## 5.17 Dead-Letter Queue Rules

The review must verify how exhausted or unrecoverable tasks are preserved.

```text
max retry exhaustion must move task to BLOCKED, FAILED, or DEAD_LETTER state according to schema
unrecoverable scheduler failures must preserve original task payload summary and evidence refs
dead-letter entries must include failure_class, final_attempt_number, reason, and source task id
dead-letter entries must not be silently deleted by cleanup/compaction
dead-letter replay must require explicit policy/governance decision or new task id
```

If a separate `DEAD_LETTER` task status is not implemented, the review must prove equivalent behavior through `FAILED` or `BLOCKED` plus a durable dead-letter record.

## 5.18 Scheduler Replay and Dry-Run Rules

The scheduler must support deterministic review of scheduler decisions without side effects.

```text
scheduler_tick_once dry-run must not claim, renew, complete, fail, or dispatch tools
replay over the same event history and config must produce the same queue/session/lease state
replay must identify config hash, event history hash, and schema version
replay failure must not overwrite current latest state
replay results must be written as evidence only, not as active queue state
```

## 5.19 Runtime Configuration and Migration Rules

The review must verify scheduler configuration provenance and state-version handling.

```text
scheduler config must be schema-validated
config hash must be recorded in evidence manifest and review report
config changes that affect ordering, retries, leases, or concurrency must be evidenced
state schema version must be recorded in every durable state file
state migration must be explicit, tested, and evidenced
unknown future state versions must fail closed, not silently downgrade
```

A final `DONE` verdict is invalid if scheduler behavior depends on unrecorded runtime configuration.

---

# 6. Expected Implementation Scope

## 6.1 Required Scheduler Package

Expected location:

```text
tools/agentx_evolve/scheduler/
```

Expected files:

```text
tools/agentx_evolve/scheduler/__init__.py
tools/agentx_evolve/scheduler/scheduler_models.py
tools/agentx_evolve/scheduler/task_queue.py
tools/agentx_evolve/scheduler/session_store.py
tools/agentx_evolve/scheduler/task_lease.py
tools/agentx_evolve/scheduler/retry_policy.py
tools/agentx_evolve/scheduler/backoff.py
tools/agentx_evolve/scheduler/crash_recovery.py
tools/agentx_evolve/scheduler/duplicate_guard.py
tools/agentx_evolve/scheduler/scheduler_policy.py
tools/agentx_evolve/scheduler/scheduler_logger.py
tools/agentx_evolve/scheduler/scheduler_runner.py
tools/agentx_evolve/scheduler/scheduler_config.py
tools/agentx_evolve/scheduler/dead_letter_queue.py
tools/agentx_evolve/scheduler/dependency_resolver.py
```

## 6.2 Required Schemas

Expected location:

```text
tools/agentx_evolve/schemas/
```

Expected schemas:

```text
task_record.schema.json
session_record.schema.json
queue_state.schema.json
task_claim.schema.json
task_lease.schema.json
retry_policy.schema.json
scheduler_policy.schema.json
scheduler_event.schema.json
scheduler_audit.schema.json
scheduler_evidence_manifest.schema.json
scheduler_review_report.schema.json
scheduler_completion_record.schema.json
scheduler_config.schema.json
dead_letter_record.schema.json
dependency_resolution.schema.json
```

## 6.3 Required Tests

Expected location:

```text
tools/agentx_evolve/tests/
```

Expected tests:

```text
test_scheduler_models.py
test_task_queue.py
test_session_store.py
test_task_lease.py
test_retry_policy.py
test_backoff.py
test_crash_recovery.py
test_duplicate_guard.py
test_scheduler_policy.py
test_scheduler_logger.py
test_scheduler_runner.py
test_scheduler_schema_validation.py
test_scheduler_negative_cases.py
test_scheduler_config.py
test_dead_letter_queue.py
test_dependency_resolver.py
test_scheduler_replay_dry_run.py
test_scheduler_state_migration.py
```

## 6.4 Required Runtime Artifacts

Expected location:

```text
.agentx-init/scheduler/
```

Expected artifacts:

```text
task_queue.json
queue_state.json
session_state.json
active_leases.json
scheduler_event_history.jsonl
scheduler_audit_history.jsonl
scheduler_error_history.jsonl
scheduler_recovery_history.jsonl
latest_scheduler_event.json
latest_queue_state.json
latest_session_state.json
task_queue_scheduler_evidence_manifest.json
task_queue_scheduler_review_report.json
task_queue_scheduler_completion_record.json
scheduler_config.json
dead_letter_history.jsonl
dependency_resolution_history.jsonl
```

---

# 7. Fresh-Clone Validation Requirement

The implementation must be validated from a fresh checkout or a clean working tree.

Required command sequence:

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
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

If `validate_scheduler_schemas.py` is not implemented, the same schema coverage must be proven by a documented pytest file such as:

```text
tools/agentx_evolve/tests/test_scheduler_schema_validation.py
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
external MCP server
background daemon
```

---

# 8. Contract-to-Implementation Coverage Matrix

| Area | Expected | Status |
|---|---|---|
| Scheduler package location | `tools/agentx_evolve/scheduler/` exists | PASS / PARTIAL / FAIL / NOT CHECKED |
| Scheduler schemas | all required schemas exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Schema validation command | schema command or pytest equivalent exists and passes | PASS / PARTIAL / FAIL / NOT CHECKED |
| Scheduler tests | required tests exist | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task queue coverage | enqueue, dequeue, update, block, complete, fail | PASS / PARTIAL / FAIL / NOT CHECKED |
| Session lifecycle coverage | create, resume, heartbeat, close, expire | PASS / PARTIAL / FAIL / NOT CHECKED |
| Lease / locking coverage | claim, renew, release, expire stale lock | PASS / PARTIAL / FAIL / NOT CHECKED |
| Retry / backoff coverage | max retries, deterministic backoff, retry stop conditions | PASS / PARTIAL / FAIL / NOT CHECKED |
| Crash recovery coverage | recover queue/session/lease state safely | PASS / PARTIAL / FAIL / NOT CHECKED |
| Duplicate-execution prevention | task cannot run twice under active lease | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | queued work checks policy before execution | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool integration | scheduler calls Tool / MCP Adapter only through controlled path | PASS / PARTIAL / FAIL / NOT CHECKED |
| Audit/evidence | JSONL + latest artifacts + manifest + review report | PASS / PARTIAL / FAIL / NOT CHECKED |
| Runtime artifact boundary | scheduler writes only under approved runtime root or deviation listed | PASS / PARTIAL / FAIL / NOT CHECKED |
| Source mutation safety | scheduler does not mutate source directly | PASS / PARTIAL / FAIL / NOT CHECKED |
| CLI command wrappers | no raw shell, allowlist enforced, output controlled | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| MCP exposure | queue/session operations hidden or safe if exposed | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
| Monitoring / Observability | events/metrics emitted safely if implemented | PASS / PARTIAL / FAIL / NOT CHECKED / NOT APPLICABLE |
```

---

# 9. Traceability Matrix

The implementation must be traceable from contract to code to test to evidence.

| Contract requirement | Implementation file | Test file | Evidence artifact | Status |
|---|---|---|---|---|
| Task enqueue/dequeue | `task_queue.py` | `test_task_queue.py` | queue state + event history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task status transitions | `task_queue.py` | `test_task_queue.py` | scheduler audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Session create/resume/close | `session_store.py` | `test_session_store.py` | session state + event history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Task claim / lease | `task_lease.py` | `test_task_lease.py` | active leases + audit history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Stale lease recovery | `crash_recovery.py` | `test_crash_recovery.py` | recovery history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Retry policy | `retry_policy.py` | `test_retry_policy.py` | task history | PASS / PARTIAL / FAIL / NOT CHECKED |
| Backoff behavior | `backoff.py` | `test_backoff.py` | task state | PASS / PARTIAL / FAIL / NOT CHECKED |
| Duplicate execution guard | `duplicate_guard.py` | `test_duplicate_guard.py` | blocked duplicate event | PASS / PARTIAL / FAIL / NOT CHECKED |
| Policy integration | `scheduler_policy.py` | `test_scheduler_policy.py` | policy decision refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Tool integration | `scheduler_runner.py` | `test_scheduler_runner.py` | tool call refs | PASS / PARTIAL / FAIL / NOT CHECKED |
| Evidence logging | `scheduler_logger.py` | `test_scheduler_logger.py` | JSONL histories | PASS / PARTIAL / FAIL / NOT CHECKED |
| Review report | report writer or manual creation | schema/manual validation | review report JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |
| Completion record | completion writer | schema validation test | completion record JSON + hash | PASS / PARTIAL / FAIL / NOT CHECKED |

---

# 10. Validation Commands

Run from a fresh checkout of the implementation commit.

Record the exact command, exit code, status, and summary for every command. `PASS` requires exit code `0`.

```bash
cd <Agent_X repo root>
git checkout <implementation commit>
git status --short
python --version
PYTHONPATH=tools python -m compileall tools/agentx_evolve
PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
git status --short
```

Required result:

```text
compileall: PASS, exit_code 0
pytest: PASS, exit_code 0
schema validation: PASS, exit_code 0
git status: CLEAN or only expected runtime artifacts
```

If unrelated future-layer tests exist in `tools/agentx_evolve/tests`, record a scoped scheduler pytest command such as:

```bash
PYTHONPATH=tools python -m pytest \
  tools/agentx_evolve/tests/test_scheduler_models.py \
  tools/agentx_evolve/tests/test_task_queue.py \
  tools/agentx_evolve/tests/test_session_store.py \
  tools/agentx_evolve/tests/test_task_lease.py \
  tools/agentx_evolve/tests/test_retry_policy.py \
  tools/agentx_evolve/tests/test_backoff.py \
  tools/agentx_evolve/tests/test_crash_recovery.py \
  tools/agentx_evolve/tests/test_duplicate_guard.py \
  tools/agentx_evolve/tests/test_scheduler_policy.py \
  tools/agentx_evolve/tests/test_scheduler_logger.py \
  tools/agentx_evolve/tests/test_scheduler_runner.py \
  tools/agentx_evolve/tests/test_scheduler_schema_validation.py \
  tools/agentx_evolve/tests/test_scheduler_negative_cases.py
```

---

# 11. Compileall Result

Record the compile result.

```text
command: PYTHONPATH=tools python -m compileall tools/agentx_evolve
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any scheduler Python file fails compile
any scheduler schema/test module fails import due to syntax
exit code is missing
```

---

# 12. Pytest Result

Record the pytest result.

```text
command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <example: 000 passed in 0.00s>
failures: <none or list>
output_artifact: <path>
```

Acceptance:

```text
PASS required
exit_code must be 0
```

Blocking if:

```text
any required task queue, session, lease, retry, recovery, duplicate guard, schema, evidence, policy, tool integration, or negative test fails
exit code is missing
```

---

# 13. Schema Validation Result

Record the dedicated schema validation result.

```text
command: PYTHONPATH=tools python tools/agentx_evolve/tests/validate_scheduler_schemas.py
fallback_command: PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests/test_scheduler_schema_validation.py
exit_code: <integer>
status: PASS | FAIL | NOT RUN
summary: <paste summary>
failures: <none or list>
output_artifact: <path>
```

Required schema tests:

```text
task record schema accepts valid queued/running/done/failed/blocked tasks
task record schema rejects missing task_id
task record schema rejects invalid status
session record schema accepts valid active/closed/expired sessions
session record schema rejects missing session_id
queue state schema accepts valid queue state
task claim schema accepts valid claim
task lease schema accepts valid lease and rejects expired active lease mismatch
retry policy schema accepts valid retry policy
scheduler policy schema accepts valid policy decision context
scheduler event schema accepts valid event
scheduler audit schema accepts valid audit record
evidence manifest schema accepts valid evidence manifest
review report schema accepts valid review report
completion record schema accepts final completion record
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
schema-invalid tasks are accepted
schema-invalid sessions are accepted
schema-invalid leases are accepted
schema-invalid queue states are accepted
scheduler evidence manifest cannot be schema-validated
scheduler review report cannot be schema-validated
scheduler completion record cannot be schema-validated
schema validation exit code is missing
```

---

# 14. Task Queue Coverage

Required task queue behavior:

```text
[ ] task can be enqueued with schema-valid task record
[ ] task IDs are unique
[ ] queue ordering is deterministic
[ ] pending task can be claimed only through lease logic
[ ] running task cannot be claimed by another active session
[ ] blocked task is not scheduled
[ ] failed task follows retry policy
[ ] done task is not rescheduled
[ ] cancelled task is not rescheduled
[ ] task status transitions are validated
[ ] invalid status transition is blocked and evidenced
[ ] queue state is persisted atomically
[ ] queue corruption is detected and handled safely
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
task can run without a valid task record
duplicate task IDs are accepted silently
blocked/done/failed terminal tasks are rescheduled incorrectly
invalid transitions are allowed
queue persistence can silently corrupt task state
```

---

# 15. Session Lifecycle Coverage

Required session behavior:

```text
[ ] session can be created
[ ] session has unique session_id
[ ] session has owner/agent identity
[ ] session can heartbeat
[ ] session can be resumed if valid
[ ] session can be closed
[ ] expired session cannot claim new work
[ ] stale session can be recovered safely
[ ] session state is persisted atomically
[ ] session history is evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
anonymous session can claim tasks
expired session can claim work
closed session can claim work
session state is lost without recovery evidence
```

---

# 16. Lease / Locking Coverage

Required lease / locking behavior:

```text
[ ] task claim creates lease
[ ] lease records task_id, session_id, claimed_at, expires_at
[ ] active lease prevents duplicate claim
[ ] lease can be renewed by owning session only
[ ] lease can be released by owning session only
[ ] expired lease can be recovered safely
[ ] stale lock detection works
[ ] lock operations are atomic enough for local runtime
[ ] lock failure returns schema-valid BLOCKED or FAILED result
[ ] lease history is evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
two sessions can hold active lease for same task
non-owner can renew/release lease
expired lease remains permanently stuck without recovery path
lock failure permits execution anyway
```

---

# 17. Retry / Backoff Coverage

Required retry / backoff behavior:

```text
[ ] retry policy defines max_attempts
[ ] retry policy defines retryable failure classes
[ ] retry policy defines non-retryable failure classes
[ ] backoff is deterministic and bounded
[ ] retry count increments correctly
[ ] retry stops at max_attempts
[ ] non-retryable failure stops retry
[ ] blocked governance/policy/sandbox failures do not retry blindly
[ ] retry event is evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
infinite retry is possible
policy/sandbox denial retries blindly
retry count is not persisted
backoff can schedule uncontrolled immediate loops
```

---

# 18. Crash Recovery Coverage

Required crash recovery behavior:

```text
[ ] detects interrupted running tasks
[ ] detects stale sessions
[ ] detects expired leases
[ ] recovers pending tasks safely
[ ] does not rerun task if completion evidence exists
[ ] records recovery decision
[ ] records unrecoverable state as BLOCKED or FAILED
[ ] preserves original failure evidence
[ ] does not delete evidence during recovery
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
crash recovery loses task state
crash recovery duplicates completed work
crash recovery deletes evidence
unrecoverable state is silently ignored
```

---

# 19. Duplicate-Execution Prevention Coverage

Required duplicate prevention behavior:

```text
[ ] active lease prevents second runner
[ ] completed task cannot be rerun unless explicit new task/retry record exists
[ ] duplicate claim returns BLOCKED
[ ] duplicate execution attempt is evidenced
[ ] idempotency key or equivalent is recorded
[ ] repeated enqueue with same idempotency key does not create duplicate task
[ ] scheduler restart does not duplicate active work without recovery decision
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
same task can run twice under active lease
repeated enqueue creates duplicate work silently
restart can duplicate running task without recovery record
```

---

# 20. Task Dependency / DAG Coverage

Required behavior if dependencies are implemented:

```text
[ ] dependency schema exists
[ ] dependencies reference known task IDs or valid external dependency refs
[ ] dependency cycles are rejected
[ ] dependent tasks cannot be claimed while prerequisite tasks are unresolved
[ ] failed prerequisite behavior is explicit and tested
[ ] dependency decisions are evidenced
[ ] dependency logic cannot bypass policy, priority, lease, or cancellation rules
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
dependency cycles are accepted
blocked dependencies are ignored
dependent task executes before prerequisite is complete
failed dependency behavior is implicit or inconsistent
dependency evidence is missing
```

---

# 21. Deterministic Ordering Coverage

Required behavior:

```text
[ ] claim-next-task ordering is deterministic
[ ] tie-breaker is documented and schema/evidence-backed
[ ] restart preserves persisted ordering or records a valid reorder decision
[ ] same queue state produces same claim result
[ ] priority cannot bypass safety gates
[ ] ordering tests do not depend on real-time sleeping
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
same queue state can claim different tasks unpredictably
priority/tie-breaker is not deterministic
restart loses task ordering without evidence
```

---

# 22. Persistence Integrity Coverage

Required behavior:

```text
[ ] task state writes are atomic
[ ] session state writes are atomic
[ ] lease state writes are atomic
[ ] event history is append-only
[ ] latest state is hash-checked or rebuildable from valid event history
[ ] corrupt latest state is detected
[ ] corrupt event history is detected
[ ] recovery never silently drops tasks, sessions, leases, or evidence
[ ] state hashes are included in evidence manifest
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
state corruption is accepted silently
state writes can be partially written as valid state
recovery discards active tasks or leases without evidence
state hashes are missing for final DONE
```

---

# 23. Concurrency Scope Coverage

Required behavior:

```text
[ ] concurrency mode is declared: SINGLE_PROCESS_ONLY, MULTI_PROCESS_SAFE, MULTI_HOST_SAFE, or DEFERRED SAFELY
[ ] advertised concurrency mode is tested
[ ] unsupported concurrency modes are blocked or clearly not exposed
[ ] concurrent claim tests prove one active lease per task for supported modes
[ ] file lock or equivalent mechanism is tested if multi-process support is claimed
[ ] distributed lock assumptions are tested if multi-host support is claimed
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | DEFERRED SAFELY
```

Blocking if:

```text
implementation advertises multi-worker safety without tests
two workers can claim the same task
lease ownership is not atomic for the advertised mode
```

---

# 24. Lease Fencing Coverage

Required behavior:

```text
[ ] claim creates lease_id and fencing_token
[ ] renew requires current lease_id and fencing_token
[ ] complete requires current lease_id and fencing_token
[ ] fail requires current lease_id and fencing_token
[ ] stale owner cannot complete after expiry/recovery
[ ] recovered task receives a new lease/fencing token
[ ] fencing token appears in evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
stale owner can complete or renew a recovered task
fencing token is missing for active lease
completion does not verify current lease ownership
```

---

# 25. Queue Compaction / Retention Coverage

Required behavior if cleanup, compaction, archival, or retention exists:

```text
[ ] compaction preserves required evidence
[ ] terminal task history remains auditable
[ ] retention policy is explicit
[ ] cleanup cannot remove active lease/session evidence
[ ] cleanup cannot remove review report, evidence manifest, or completion record
[ ] cleanup has dry-run mode or explicit bounded command acceptance
[ ] cleanup writes evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
cleanup deletes required evidence
cleanup removes active state
retention is implicit or unreviewable
```

---

## 25.1 Queue Admission Validation Coverage

Required behavior:

```text
[ ] malformed task payloads are rejected before enqueue
[ ] unknown task type is rejected or explicitly marked manual/external
[ ] missing idempotency metadata is rejected or generated deterministically
[ ] missing risk/effect metadata is rejected for executable tasks
[ ] tasks failing admission cannot be claimed
[ ] admission failures write evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
malformed tasks become claimable
admission failure lacks evidence
executable tasks can enter queue without policy-relevant metadata
```

## 25.2 Dead-Letter Queue Coverage

Required behavior:

```text
[ ] exhausted retries are preserved as failed/blocked/dead-letter records
[ ] unrecoverable failures include failure_class and source task id
[ ] dead-letter evidence includes final attempt and reason
[ ] cleanup/compaction cannot remove dead-letter evidence required for review
[ ] replaying dead-letter work requires explicit new task or approval path
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
exhausted tasks disappear silently
failed tasks can be retried indefinitely without policy
unrecoverable failures have no durable record
```

## 25.3 Scheduler Replay / Dry-Run Coverage

Required behavior:

```text
[ ] scheduler dry-run has no side effects
[ ] replay over event history is deterministic
[ ] replay records event history hash and config hash
[ ] replay failure does not overwrite active latest state
[ ] replay result is evidenced separately from active queue state
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
dry-run claims or dispatches work
replay mutates active state
same history/config replays to different scheduler state
```

## 25.4 Scheduler Configuration / Migration Coverage

Required behavior:

```text
[ ] scheduler config schema validates
[ ] scheduler config hash is recorded
[ ] queue/session/lease state schema versions are recorded
[ ] unsupported state version fails closed
[ ] migration path is tested if migration exists
[ ] config changes affecting behavior are evidenced
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
scheduler behavior depends on unrecorded config
unknown state versions are silently accepted
state migration loses tasks, leases, or evidence
```

---

# 26. Failure Taxonomy Integration Coverage

Required failure taxonomy behavior:

```text
[ ] scheduler failures use standard failure_class values
[ ] failure taxonomy record id/evidence ref is attached when available
[ ] queue corruption maps to SCHEDULER_QUEUE_CORRUPT
[ ] duplicate claim maps to SCHEDULER_DUPLICATE_CLAIM
[ ] lease conflict maps to SCHEDULER_LEASE_CONFLICT
[ ] expired session claim maps to SCHEDULER_SESSION_EXPIRED
[ ] retry exhausted maps to SCHEDULER_RETRY_EXHAUSTED
[ ] recovery failure maps to SCHEDULER_RECOVERY_FAILED
[ ] policy denial maps to POLICY_DENIED or SCHEDULER_POLICY_DENIED
[ ] tool dispatch failure preserves ToolResult failure_class
[ ] unknown failures map to SCHEDULER_UNKNOWN_FAILURE
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
scheduler errors are unclassified
failure classes are inconsistent with Failure Taxonomy
policy/tool/sandbox denials lose original failure evidence
unknown exceptions escape without schema-valid evidence
```

---

# 27. Policy Integration Coverage

Required policy behavior:

```text
[ ] queued work has requested effect metadata
[ ] queued work has caller/session identity
[ ] scheduler checks policy before dispatching tool work
[ ] policy denial blocks dispatch
[ ] governance-required work is not executed without governance record
[ ] human-approval-required work is not executed without approval record
[ ] missing policy fails closed for non-read-only work
[ ] policy decision ID is attached to task/session evidence where available
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
queued work can bypass policy
mutating queued work executes without governance
missing policy results in ALLOW for non-read-only work
policy denial is not evidenced
```

---

# 28. Tool Integration Coverage

Required tool integration behavior:

```text
[ ] scheduler dispatches work only through Tool / MCP Adapter or approved local API
[ ] scheduler does not call raw shell
[ ] scheduler does not directly mutate source
[ ] tool call ID is linked to task ID
[ ] tool result ID is linked to task result
[ ] tool failure updates task state deterministically
[ ] blocked tool result blocks or fails task according to policy
[ ] invalid tool result fails task with evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
scheduler bypasses Tool / MCP Adapter for tool execution
scheduler executes raw shell
scheduler mutates source directly
scheduler loses tool result evidence
```

---

# 29. Audit / Evidence Coverage

Required evidence behavior:

```text
[ ] scheduler_event_history.jsonl is written
[ ] scheduler_audit_history.jsonl is written
[ ] scheduler_error_history.jsonl is written for errors
[ ] scheduler_recovery_history.jsonl is written for recovery
[ ] latest_scheduler_event.json is written atomically
[ ] latest_queue_state.json is written atomically
[ ] latest_session_state.json is written atomically
[ ] task_queue_scheduler_evidence_manifest.json is written
[ ] task_queue_scheduler_review_report.json is written
[ ] completion record is written after validation
[ ] evidence includes timestamps
[ ] evidence includes reviewed commit
[ ] evidence includes task IDs
[ ] evidence includes session IDs
[ ] evidence includes lease IDs where applicable
[ ] evidence includes command text, exit codes, statuses, and summaries for validation
[ ] evidence includes schema validation summary
[ ] evidence includes SHA-256 hashes for final evidence artifacts
[ ] secrets are redacted before logging
[ ] raw tool output is not durably logged without truncation/redaction
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
scheduler events are not logged
scheduler decisions are not logged
lease/retry/recovery decisions lack evidence
secrets are logged
reviewed commit is missing from evidence
required hashes are missing
```

---

# 30. Atomic Persistence and Corruption Handling Coverage

Required persistence behavior:

```text
[ ] queue_state.json writes atomically
[ ] session_state.json writes atomically
[ ] active_leases.json writes atomically
[ ] latest artifacts write atomically
[ ] partial write/corrupt JSON is detected
[ ] corrupt state is not silently overwritten without evidence
[ ] recovery path preserves prior corrupt artifact or records hash/reference
[ ] append-only JSONL history tolerates malformed previous lines without deleting them
[ ] state file schema version is recorded
[ ] state migration is blocked or explicitly governed if schema version changes
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Blocking if:

```text
queue/session/lease state can be silently corrupted
partial write can be accepted as valid state
recovery deletes evidence
schema version mismatch is ignored
```

---

# 31. Runtime Artifact Boundary Check

Approved runtime artifact root:

```text
.agentx-init/scheduler/
```

Allowed scheduler artifacts:

```text
task_queue.json
queue_state.json
session_state.json
active_leases.json
scheduler_event_history.jsonl
scheduler_audit_history.jsonl
scheduler_error_history.jsonl
scheduler_recovery_history.jsonl
latest_scheduler_event.json
latest_queue_state.json
latest_session_state.json
task_queue_scheduler_evidence_manifest.json
task_queue_scheduler_review_report.json
task_queue_scheduler_completion_record.json
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
scheduler writes source files directly
scheduler writes runtime artifacts outside approved root without deviation
scheduler deletes evidence files
scheduler writes hidden uncontrolled state
```

---

# 32. Source Mutation Check

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
only expected runtime artifacts under .agentx-init/scheduler/
```

Status:

```text
PASS | FAIL | NOT CHECKED
```

Blocking if:

```text
source files are modified by scheduler tests
source files are modified by scheduler runtime
unapproved files are created outside runtime artifact paths
runtime artifacts are written outside approved runtime roots
```

---

# 33. CLI / Command Acceptance Coverage

This section applies if scheduler exposes CLI commands.

Required behavior:

```text
[ ] CLI commands are allowlisted
[ ] CLI commands do not execute raw shell
[ ] enqueue command validates schema
[ ] claim command respects leases
[ ] resume command respects session state
[ ] recover command preserves evidence
[ ] status command is read-only
[ ] destructive commands are absent or blocked
[ ] command output is bounded and redacted
[ ] command evidence is written
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
raw shell executes
CLI can bypass lease/policy checks
CLI can delete evidence
CLI can mutate source directly
```

---

# 34. MCP Exposure Coverage

This section applies only if queue/session operations are exposed through MCP.

Required behavior:

```text
[ ] MCP exposure is disabled by default or read-only only
[ ] MCP cannot enqueue mutating work without policy/governance
[ ] MCP cannot claim tasks without valid session identity
[ ] MCP cannot release another session's lease
[ ] MCP cannot bypass scheduler policy
[ ] MCP cannot bypass Tool / MCP Adapter controls
[ ] MCP server does not start automatically
[ ] MCP opens no network port by default
[ ] MCP request evidence is written
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE | DEFERRED SAFELY
```

Blocking if:

```text
MCP can schedule mutating work by default
MCP can bypass policy
MCP can bypass lease ownership
MCP starts server automatically
MCP opens network port by default
```

---

# 35. Monitoring / Observability Coverage

This section applies if scheduler emits metrics/events.

Required behavior:

```text
[ ] metrics/events do not contain secrets
[ ] metrics/events do not contain raw task payloads unless redacted
[ ] queue depth metric is correct if implemented
[ ] running task count is correct if implemented
[ ] failed task count is correct if implemented
[ ] stale lease count is correct if implemented
[ ] metrics emission does not require network by default
[ ] metrics failure does not block safe scheduler operation unless required by policy
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED | NOT APPLICABLE
```

Blocking if:

```text
observability leaks secrets
observability requires network by default
metrics failure causes uncontrolled scheduler behavior
```

---

# 36. Negative Test Pack

The review must prove forbidden behavior fails closed.

Required negative cases:

```text
[ ] malformed task record -> INVALID or BLOCKED
[ ] missing task_id -> INVALID
[ ] duplicate task_id -> BLOCKED
[ ] invalid task status transition -> BLOCKED
[ ] anonymous session claims task -> BLOCKED
[ ] expired session claims task -> BLOCKED
[ ] second active claim for same task -> BLOCKED
[ ] non-owner lease release -> BLOCKED
[ ] stale lock recovery preserves evidence
[ ] retry stops at max_attempts
[ ] policy-denied task does not dispatch
[ ] sandbox-denied task does not dispatch tool execution
[ ] scheduler does not raw-shell
[ ] scheduler does not directly mutate source
[ ] crash recovery does not duplicate completed task
[ ] secret-like payload is redacted in evidence
```

Status:

```text
PASS | PARTIAL | FAIL | NOT CHECKED
```

Any failed negative test is a BLOCKER unless explicitly marked as non-applicable with justification.

---

# 37. Evidence Manifest

Create:

```text
.agentx-init/scheduler/task_queue_scheduler_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_evidence_manifest.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
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
      "output_artifact": "<path>"
    },
    {
      "name": "pytest",
      "command": "PYTHONPATH=tools python -m pytest tools/agentx_evolve/tests",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    },
    {
      "name": "schema_validation",
      "command": "<schema validation command>",
      "exit_code": 0,
      "status": "PASS",
      "summary": "<summary>",
      "output_artifact": "<path>"
    }
  ],
  "evidence_files": [],
  "evidence_file_hashes": [],
  "runtime_artifacts": [],
  "known_expected_runtime_artifacts": [],
  "deviation_register": [],
  "source_mutation_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "task_queue_status": "PASS",
  "session_lifecycle_status": "PASS",
  "lease_locking_status": "PASS",
  "retry_backoff_status": "PASS",
  "crash_recovery_status": "PASS",
  "duplicate_execution_prevention_status": "PASS",
  "policy_integration_status": "PASS",
  "tool_integration_status": "PASS",
  "redaction_status": "PASS",
  "hash_status": "PASS",
  "scheduler_mode": "SINGLE_STEP_LOCAL | CLI | RUNTIME_STUB",
  "background_execution_status": "NOT_PRESENT_OR_DEFERRED_SAFELY",
  "failure_taxonomy_status": "PASS",
  "atomic_persistence_status": "PASS",
  "idempotency_status": "PASS",
  "cancellation_pause_resume_status": "PASS_OR_NOT_APPLICABLE",
  "priority_fairness_status": "PASS_OR_NOT_APPLICABLE",
  "final_decision": "DONE"
}
```

Hashing rule:

```text
SHA-256 hashes are required.
Use Python standard library hashlib if no project hash helper exists.
A final DONE verdict is invalid if required final evidence hashes are missing.

The manifest must include paths and hashes for all final evidence files, including:

```text
task_queue_scheduler_evidence_manifest.json
task_queue_scheduler_review_report.json
task_queue_scheduler_completion_record.json
scheduler_event_history.jsonl, if used by review
scheduler_audit_history.jsonl, if used by review
scheduler_recovery_history.jsonl, if used by review
latest_queue_state.json, if used by review
latest_session_state.json, if used by review
active_leases.json, if used by review
command output artifacts, if stored as files
```

The manifest itself must be hashed after final write. If self-hashing is implemented through a stable canonicalization rule, record that rule. Otherwise record the manifest hash in the review report and completion record.
```

---

# 38. Review Report Artifact

Create:

```text
.agentx-init/scheduler/task_queue_scheduler_review_report.json
```

Required fields:

```json
{
  "schema_version": "1.0",
  "schema_id": "scheduler_review_report.schema.json",
  "component_id": "AGENTX_TASK_QUEUE_SESSION_SCHEDULER",
  "review_document_id": "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD",
  "review_document_version": "v4.0",
  "reviewed_commit": "<commit hash>",
  "reviewed_branch": "<branch name>",
  "reviewed_at": "<UTC timestamp>",
  "reviewer": "<name or tool>",
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "working_tree_start_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "working_tree_end_status": "CLEAN_OR_EXPECTED_RUNTIME_ARTIFACTS_ONLY",
  "commands_run": [],
  "coverage_statuses": {},
  "blockers": [],
  "high_issues": [],
  "non_blocking_followups": [],
  "deviation_register": [],
  "evidence_manifest_path": ".agentx-init/scheduler/task_queue_scheduler_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/scheduler/task_queue_scheduler_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_path": ".agentx-init/scheduler/task_queue_scheduler_completion_record.json",
  "completion_record_sha256": "<sha256>",
  "scheduler_config_hash": "<sha256>",
  "queue_state_hash": "<sha256>",
  "session_state_hash": "<sha256>",
  "lease_state_hash": "<sha256>",
  "dependency_resolution_hash": "<sha256 or NOT_APPLICABLE>",
  "implementation_rating": 10.0,
  "final_verdict": "DONE"
}
```

The review report is the bridge between this template and the implementation. A final `DONE` verdict is invalid if this report is missing, if it does not identify the exact reviewed commit, or if it lacks command exit codes.

## 38.1 Evidence Immutability Rule

After the review report records a final `DONE` verdict:

```text
final evidence files must not be modified without creating a new review report
changed evidence hashes invalidate the previous DONE verdict
new validation evidence must record a new timestamp and reviewed commit
manual edits to completion evidence after sign-off must be listed as deviations
```

---

# 39. Completion Evidence Record

After validation, create:

```text
.agentx-init/scheduler/task_queue_scheduler_completion_record.json
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
  "review_environment": {
    "os": "<name/version>",
    "python_version": "<version>",
    "pytest_version": "<version or NOT INSTALLED>"
  },
  "canonical_scheduler_subdirectory": "tools/agentx_evolve/scheduler/",
  "canonical_schema_subdirectory": "tools/agentx_evolve/schemas/",
  "canonical_test_subdirectory": "tools/agentx_evolve/tests/",
  "runtime_artifact_root": ".agentx-init/scheduler/",
  "basis_documents": [
    "TASK_QUEUE_SESSION_SCHEDULER_EQC_FIC_SIB_SCHEMA_CONTRACT",
    "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_SPEC",
    "TASK_QUEUE_SESSION_SCHEDULER_IMPLEMENTATION_REVIEW_AND_DOD"
  ],
  "commands_run": [],
  "files_created_or_changed": [],
  "schemas_created_or_changed": [],
  "tests_created_or_changed": [],
  "validated_capabilities": [],
  "task_queue_coverage_verified": [],
  "session_lifecycle_verified": [],
  "lease_locking_verified": [],
  "retry_backoff_verified": [],
  "crash_recovery_verified": [],
  "duplicate_execution_prevention_verified": [],
  "queue_admission_verified": [],
  "dead_letter_queue_verified": [],
  "scheduler_replay_dry_run_verified": [],
  "scheduler_config_migration_verified": [],
  "policy_integration_verified": [],
  "tool_integration_verified": [],
  "audit_evidence_verified": [],
  "negative_tests_verified": [],
  "evidence_manifest_path": ".agentx-init/scheduler/task_queue_scheduler_evidence_manifest.json",
  "evidence_manifest_sha256": "<sha256>",
  "review_report_path": ".agentx-init/scheduler/task_queue_scheduler_review_report.json",
  "review_report_sha256": "<sha256>",
  "completion_record_sha256": "<sha256>",
  "deviation_register": [],
  "unresolved_risks": [],
  "implementation_score": 10.0,
  "final_decision": "DONE"
}
```

---

# 40. What Exists

Fill after implementation.

```text
scheduler package files:
  - <PASS/PARTIAL/FAIL + notes>
schema files:
  - <PASS/PARTIAL/FAIL + notes>
test files:
  - <PASS/PARTIAL/FAIL + notes>
runtime artifacts:
  - <PASS/PARTIAL/FAIL + notes>
validation utilities:
  - <PASS/PARTIAL/FAIL + notes>
```

---

# 41. What Passed

Fill after validation.

```text
compileall:
pytest:
schema validation:
task queue coverage:
session lifecycle coverage:
lease / locking coverage:
retry / backoff coverage:
crash recovery coverage:
duplicate-execution prevention coverage:
failure taxonomy integration:
policy integration:
tool integration:
CLI / command acceptance:
MCP exposure:
monitoring / observability:
audit/evidence:
atomic persistence / corruption handling:
evidence manifest:
review report:
evidence hashes:
negative tests:
runtime artifact boundary check:
source mutation check:
completion record:
```

---

# 42. What Failed

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

# 43. Issue Severity Classification

## 43.1 BLOCKER

The layer cannot be marked done if any BLOCKER exists.

```text
reviewed commit is missing
command exit code is missing
compileall fails
pytest fails
schema validation fails
task queue allows duplicate task IDs silently
two sessions can claim same task at same time
expired/closed session can claim work
lease owner rules are not enforced
retry can loop indefinitely
queue corruption is accepted silently
state writes are non-atomic and unsafe
dependency cycle is accepted
malformed task becomes claimable
dead-letter/exhausted retry handling is missing
scheduler dry-run mutates active state
unsupported state version is silently accepted
scheduler config hash is missing
task ordering is nondeterministic without evidence
advertised multi-worker mode is not tested
stale lease owner can complete recovered task
crash recovery duplicates completed work
scheduler bypasses policy for queued work
scheduler bypasses Tool / MCP Adapter for tool execution
scheduler executes raw shell
scheduler mutates source directly
scheduler deletes evidence
secrets are logged
evidence lacks reviewed commit
evidence hashes are missing
review report is missing
completion record is missing
required area remains NOT CHECKED
```

## 43.2 HIGH

High issues must be fixed before this layer is used by an orchestrator.

```text
incomplete evidence references
partial crash recovery coverage
partial retry policy coverage
partial Failure Taxonomy mapping
partial Tool / MCP Adapter integration
runtime artifact boundary exception lacks justification
review environment not recorded
scheduler metrics incomplete but enabled
```

## 43.3 NON-BLOCKING

Non-blocking issues may be documented as follow-up.

```text
minor wording mismatch
extra disabled scheduler command
monitoring intentionally deferred
MCP exposure intentionally absent
human-visible schedule dashboard intentionally deferred
additional future-layer tests exist outside scoped scheduler suite
```

---

# 44. Deviation Register

Any exception, deferral, or non-standard artifact path must be recorded here and in the evidence manifest.

```text
deviations:
  - id: <DEV-001>
    area: <Queue | Session | Lease | Retry | Recovery | Policy | Tool Integration | Evidence | Runtime Artifact Boundary | MCP | Monitoring | Other>
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
HIGH items cannot be accepted for DONE unless the review proves they are not part of the active runtime path.
Runtime artifact writes outside `.agentx-init/scheduler/` require a deviation entry.
MCP deferral requires a deviation entry if MCP files exist but runtime exposure is deferred.
Missing evidence hashes cannot be accepted as a deviation for DONE.
```

---

# 45. Implementation Scoring Rubric

Use this rubric only after validation has been run.

| Category | Points | Required for full credit |
|---|---:|---|
| Structure and expected files | 1.0 | Scheduler, schema, test, runtime artifact paths exist as required. |
| Compileall | 1.0 | Compile command passes with exit code 0. |
| Pytest | 1.0 | Full relevant test suite passes with exit code 0. |
| Schema validation | 1.0 | Valid and invalid schema cases pass, including evidence manifest, review report, and completion record. |
| Task queue and session lifecycle | 1.0 | Enqueue/dequeue/status transitions/session create/resume/close/expire work safely. |
| Lease / locking and duplicate prevention | 1.0 | Claims, renewals, releases, stale leases, and duplicate execution prevention work. |
| Retry / backoff / crash recovery | 1.0 | Retry is bounded, recovery is safe, completed work is not duplicated. |
| Policy and tool integration | 1.0 | Queued work checks policy and dispatches only through controlled tool path. |
| Audit / evidence | 1.0 | JSONL histories, latest artifacts, evidence manifest, review report, hashes, redaction, completion record. |
| Source mutation and runtime boundary safety | 1.0 | Scheduler does not mutate source, raw-shell, or write uncontrolled runtime artifacts. |

Scoring rule:

```text
10.0 = fully DONE
9.0-9.9 = strong but NOT DONE if any required area is partial
8.0-8.9 = substantial implementation, missing important coverage
7.0-7.9 = usable draft, not scheduler-safe
below 7.0 = not acceptable for controlled task/session execution
```

Hard cap rules:

```text
missing reviewed commit caps score at 6.0
missing command exit code caps score at 7.0
compileall FAIL caps score at 5.0
pytest FAIL caps score at 6.0
schema validation FAIL caps score at 6.5
duplicate active execution caps score at 4.0
unknown/invalid task status accepted caps score at 6.0
expired/closed session can claim work caps score at 4.0
raw shell executes caps score at 4.0
source mutation by scheduler caps score at 5.0
policy bypass caps score at 5.0
uncontrolled background execution caps score at 4.0
non-atomic state persistence without recovery caps score at 6.0
queue corruption silently accepted caps score at 5.0
dependency cycle accepted caps score at 5.0
nondeterministic task ordering caps score at 7.0
advertised multi-worker mode without tests caps score at 6.0
stale lease owner can complete recovered task caps score at 4.0
missing scheduler state hashes caps score at 8.0
missing scheduler config hash caps score at 8.0
dry-run/replay mutates active state caps score at 5.0
malformed task becomes claimable caps score at 5.0
unsupported state version is silently accepted caps score at 6.0
missing evidence caps score at 7.0
missing evidence hashes caps score at 8.0
any NOT CHECKED required area caps score at 8.0
any NOT RUN required command caps score at 8.0
missing review report caps score at 8.0
missing completion record caps score at 8.0
```

---

# 46. GO / NO-GO Rules

## 46.1 GO Criteria

The layer may be marked DONE only if:

```text
reviewed commit is recorded
review environment is recorded
compileall passes with exit code 0
pytest passes with exit code 0
schema validation passes with exit code 0
task queue tests pass
session lifecycle tests pass
lease / locking tests pass
retry / backoff tests pass
crash recovery tests pass
duplicate-execution prevention tests pass
task dependency tests pass or are not applicable
deterministic ordering tests pass
persistence integrity tests pass
concurrency scope tests pass or concurrency is deferred safely
lease fencing tests pass
queue compaction / retention tests pass or are not applicable
queue admission validation tests pass
dead-letter queue tests pass or equivalent failed/blocked terminal handling is proven
scheduler replay / dry-run tests pass
scheduler configuration / migration tests pass
policy integration tests pass
tool integration tests pass
audit/evidence tests pass
evidence manifest exists
evidence hashes exist
scheduler state hashes exist
scheduler config hash exists
dependency-resolution hash exists or is NOT_APPLICABLE with proof
review report exists
CLI / command wrapper tests pass or are not applicable
MCP exposure tests pass or are not applicable / deferred safely
monitoring / observability tests pass or are not applicable
negative tests pass
runtime artifact boundary check passes
source mutation check passes
completion record exists
no required area remains NOT CHECKED
no required command remains NOT RUN
no BLOCKER exists
accepted deviations are listed and non-blocking
```

## 46.2 NO-GO Criteria

The layer must remain NOT DONE if any are true:

```text
reviewed commit is not recorded
review environment is not recorded
required command exit code is missing
compileall fails
pytest fails
schema validation fails
duplicate task execution is possible
dependency cycle is accepted
malformed task becomes claimable
dead-letter/exhausted retry handling is missing
scheduler dry-run mutates active state
unsupported state version is silently accepted
scheduler config hash is missing
task ordering is nondeterministic without evidence
advertised multi-worker mode lacks tests
stale lease owner can complete recovered task
lease ownership is not enforced
expired/closed session can claim work
retry can loop indefinitely
queue corruption is accepted silently
state writes are non-atomic and unsafe
dependency cycle is accepted
malformed task becomes claimable
dead-letter/exhausted retry handling is missing
scheduler dry-run mutates active state
unsupported state version is silently accepted
scheduler config hash is missing
task ordering is nondeterministic without evidence
advertised multi-worker mode is not tested
stale lease owner can complete recovered task
crash recovery duplicates completed work
queued work bypasses policy
queued work bypasses Tool / MCP Adapter
failure taxonomy evidence is missing for failed/blocked scheduler decisions
scheduler starts an uncontrolled background daemon or worker loop
scheduler executes raw shell
scheduler mutates source directly
scheduler writes uncontrolled runtime artifacts
secrets are logged
scheduler evidence is missing
evidence manifest is missing
evidence hashes are missing
review report is missing
completion record is missing
any required area remains NOT CHECKED
any required command remains NOT RUN
any BLOCKER remains
```

---

# 47. Remediation Rules

If implementation fails validation, fixes must not weaken safety.

Allowed fixes:

```text
fix import paths
fix schema required fields
fix dataclass defaults
fix queue status transitions
fix lease ownership checks
fix stale lock recovery
fix retry/backoff bounds
fix duplicate guard logic
fix scheduler policy checks
fix tool dispatch integration
fix evidence writing
fix evidence manifest generation
fix review report generation
fix evidence hashing
fix secret redaction
fix tests to reflect the contract
fix runtime artifact boundary checks
```

Forbidden fixes:

```text
do not remove policy checks to pass tests
do not bypass Tool / MCP Adapter to pass tests
do not remove lease checks to pass tests
do not allow duplicate execution to avoid blocking
do not make retries infinite
do not mark crashed tasks done without evidence
do not enable raw shell
do not enable network by default
do not mutate source directly from scheduler
do not skip evidence writing
do not omit hashes for final DONE
do not log secrets
do not mark NOT CHECKED as PASS
do not accept a BLOCKER as a deviation
```

---

# 48. Definition of Done

The Task Queue / Session Scheduler layer is done when it can coordinate Agent_X work safely and reproducibly.

It must prove:

```text
all target files exist
all schemas exist
all tests exist
tasks can be enqueued safely
task admission validates payload, metadata, dependencies, and idempotency before claimability
task status transitions are validated
sessions can be created, resumed, heartbeated, closed, and expired safely
task claims require valid leases
active leases prevent duplicate execution
lease ownership is enforced
stale leases can be recovered safely
retry policy is bounded and deterministic
backoff is bounded and deterministic
crash recovery preserves evidence
crash recovery does not duplicate completed work
exhausted retry/dead-letter behavior preserves evidence
scheduler dry-run/replay has no active side effects
state persistence is atomic or safely recovered
scheduler config and state hashes are evidenced
state schema versions and migrations are explicit
queue corruption is detected and evidenced
failure taxonomy integration records scheduler failures
queued work checks policy before dispatch
queued work dispatches only through controlled tool path
scheduler does not execute raw shell
scheduler does not mutate source directly
scheduler writes queue/session/lease evidence
scheduler writes recovery/retry evidence
scheduler writes evidence manifest
scheduler writes review report
scheduler writes completion record
scheduler redacts secrets before durable logging
scheduler stays within runtime artifact boundary
scheduler does not start uncontrolled background execution
review environment is recorded
evidence hashes are written
final verdict is recorded
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
compileall PASS, exit_code 0
pytest PASS, exit_code 0
schema validation PASS, exit_code 0
git status CLEAN or only expected runtime artifacts
```

---

# 49. Required Evidence Package

The completion evidence package must include:

```text
compileall output
pytest output
schema validation result
task queue test result
session lifecycle test result
lease / locking test result
retry / backoff test result
crash recovery test result
duplicate-execution prevention test result
queue admission validation test result
dead-letter queue test result or equivalent terminal-failure proof
scheduler replay / dry-run test result
scheduler configuration / migration test result
policy integration test result
tool integration test result
CLI / command wrapper test result or N/A note
MCP exposure test result or N/A / safe-deferred note
monitoring / observability test result or N/A note
negative-test result
audit/evidence test result
evidence manifest
review report
git status output
completion record
SHA-256 hashes for final evidence artifacts
```

The evidence package must show:

```text
reviewed commit
validation timestamp
review environment
command exit codes
no source mutation
no raw shell
no uncontrolled runtime artifacts
no duplicate execution
lease ownership enforcement
bounded retry behavior
dead-letter or equivalent exhausted retry evidence
safe crash recovery
scheduler config hash and state hashes
replay/dry-run no-side-effect proof
policy and tool integration
secrets redacted
hashes for final evidence artifacts
```

---

# 50. Final Done / Not-Done Verdict

Fill after validation.

```text
final_verdict: DONE | NOT DONE
implementation_rating: <0-10>
review_document_rating: <0-10>
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
evidence hashes are missing
review report is missing
completion record is missing
```

---

# 51. Final Frozen Checklist

Use this checklist for the final review.

```text
Structure:
[ ] tools/agentx_evolve/scheduler/ exists
[ ] scheduler schemas exist
[ ] scheduler tests exist
[ ] runtime artifact root exists or is created safely

Validation:
[ ] reviewed commit recorded
[ ] review environment recorded
[ ] compileall PASS with exit_code 0
[ ] pytest PASS with exit_code 0
[ ] schema validation PASS with exit_code 0
[ ] git status clean or expected runtime artifacts only

Task Queue:
[ ] enqueue works
[ ] queue admission validates payload and metadata before claimability
[ ] queue state persists atomically
[ ] invalid status transitions block
[ ] terminal tasks are not rescheduled incorrectly

Session Lifecycle:
[ ] create/resume/heartbeat/close/expire work
[ ] expired/closed sessions cannot claim work
[ ] session evidence is written

Lease / Locking:
[ ] active lease prevents duplicate claim
[ ] lease ownership enforced
[ ] stale leases recover safely

Retry / Recovery:
[ ] retry bounded
[ ] backoff bounded
[ ] crash recovery preserves evidence
[ ] completed work is not duplicated
[ ] exhausted retry/dead-letter behavior preserves evidence
[ ] scheduler dry-run/replay has no active side effects
[ ] scheduler config hash and state hashes are recorded

Policy / Tool Integration:
[ ] queued work checks policy
[ ] scheduler dispatches through controlled tool path
[ ] scheduler does not raw-shell
[ ] scheduler does not mutate source directly

Evidence:
[ ] scheduler event history written
[ ] scheduler audit history written
[ ] recovery history written
[ ] latest queue/session state written atomically
[ ] evidence manifest written
[ ] review report written
[ ] completion record written
[ ] SHA-256 hashes written
[ ] secrets redacted

Runtime Boundary:
[ ] artifacts stay under .agentx-init/scheduler/
[ ] exceptions recorded in deviation register

Final:
[ ] implementation score is 10.0
[ ] final verdict recorded
[ ] no required area is NOT CHECKED
[ ] no required command is NOT RUN
[ ] no BLOCKER remains
[ ] accepted deviations are non-blocking and recorded
```

---

# 52. Final Sign-Off Template

Use this after implementation validation.

```text
Task Queue / Session Scheduler Validation — Commit <hash>

Reviewer / Environment:
- reviewer: <name or tool>
- reviewed commit: <hash>
- reviewed branch: <branch>
- reviewed at UTC: <timestamp>
- OS: <name/version>
- Python: <version>
- pytest: <version or NOT INSTALLED>

Status:
- initial git status: CLEAN/EXPECTED_RUNTIME_ARTIFACTS_ONLY/DIRTY
- compileall: PASS/FAIL, exit_code=<code>
- pytest: PASS/FAIL, exit_code=<code>
- schema validation: PASS/FAIL, exit_code=<code>
- task queue coverage: PASS/FAIL
- session lifecycle coverage: PASS/FAIL
- lease / locking coverage: PASS/FAIL
- retry / backoff coverage: PASS/FAIL
- crash recovery coverage: PASS/FAIL
- duplicate-execution prevention coverage: PASS/FAIL
- queue admission validation coverage: PASS/FAIL
- dead-letter queue coverage: PASS/FAIL/N/A
- scheduler replay / dry-run coverage: PASS/FAIL
- scheduler config / migration coverage: PASS/FAIL
- policy integration coverage: PASS/FAIL
- tool integration coverage: PASS/FAIL
- CLI / command wrapper coverage: PASS/FAIL/N/A
- MCP exposure coverage: PASS/FAIL/N/A/DEFERRED SAFELY
- monitoring / observability coverage: PASS/FAIL/N/A
- negative-test coverage: PASS/FAIL
- audit/evidence coverage: PASS/FAIL
- runtime artifact boundary check: PASS/FAIL
- source mutation check: PASS/FAIL
- evidence manifest: PRESENT/MISSING
- evidence hashes: PRESENT/MISSING
- review report: PRESENT/MISSING
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

# 53. Final Rating

This v4 review / DoD document is rated:

```text
10/10
```

Reason:

```text
It covers standards, expected files, fresh-clone validation, compileall, pytest, schema validation, task queue coverage, session lifecycle coverage, lease / locking coverage, retry / backoff coverage, crash recovery coverage, duplicate-execution prevention, dependency/DAG behavior, queue admission validation, dead-letter handling, scheduler replay/dry-run, scheduler configuration and migration, policy integration, tool integration, failure taxonomy integration, audit/evidence coverage, source mutation checks, runtime artifact boundary checks, atomic persistence, idempotency, cancellation/pause/resume, priority/fairness, background-execution boundaries, evidence manifest, review report, completion record, scoring, GO / NO-GO rules, Definition of Done, and final DONE / NOT DONE verdict.
```
