# Task Queue / Session Scheduler Layer — EQC / FIC / SIB / Schema Contract v4

**Roadmap Layer:** 20
**Roadmap Phase:** Phase E — Task Queue

## Schema Contract

| Field | Type | Required | Constraint |
|---|---|---|---|
| schema_version | string | yes | pattern `^1\.0$` |
| schema_id | string | yes | const `task_queue_item.schema.json` |
| item_id | string | yes | — |
| session_id | string | yes | — |
| description | string | yes | — |
| status | string | yes | enum PENDING/RUNNING/PAUSED/COMPLETED/CANCELLED/FAILED |
| priority | integer | yes | — |
| created_at | string | yes | ISO 8601 |
| warnings | array of string | yes | — |
| errors | array of string | yes | — |

## EQC (Exact Quality Criteria)

1. Every `TaskQueueItem` representation must satisfy `validate_schema()` with zero errors.
2. `list_all` must return items sorted by priority descending, then created_at ascending.
3. `save_to_disk` + `load_from_disk` must round-trip faithfully.
4. `generate_manifest` must produce counts matching current queue state.

## FIC (Functional Integrity Criteria)

1. Lock must prevent concurrent queue writes.
2. Lock timeout must raise `TimeoutError`.
3. `validate_schema` must reject missing required fields and invalid status enum values.
4. `update_status` must return `False` for non-existent item_id.
5. `clear_completed` must only remove items with COMPLETED, CANCELLED, or FAILED status.

## SIB (System Integration Boundary)

1. Persistence layer writes under `.agentx-init/queue/`.
2. All public functions/classes exported from `queue/__init__.py`.
