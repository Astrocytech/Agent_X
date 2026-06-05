# Task Queue / Session Scheduler Layer — Implementation Spec v4

**Roadmap Layer:** 20
**Roadmap Phase:** Phase E — Task Queue
**Component:** agentx_evolve/queue/

## Overview

Layer 20 provides a dedicated Task Queue & Session Scheduler layer that manages task items in a queue, persists queue state to disk, maintains a manifest, and supports locking for crash-safe concurrent access.

## Modules

### task_queue.py
- **TaskQueueItem** — dataclass tracking a single queue item: item_id, session_id, description, status, priority, created_at, warnings, errors.
- **QueueManifest** — dataclass with manifest_id, total_items, pending, running, completed, failed, cancelled, paused, created_at, warnings, errors.
- **TaskQueue** — dict-backed queue with enqueue, get, list_all, update_status, remove, clear_completed, plus disk persistence (load/save), manifest generation, lock acquire/release, queue history append.
- **Schema validation** — `validate_schema` static method on `TaskQueueItem` validates data against schemas/task_queue_item.schema.json contract.

### Constants & Helpers
- `TQ_SCHEMA_VERSION`, `TQ_SCHEMA_ID`
- `QS_PENDING`, `QS_RUNNING`, `QS_PAUSED`, `QS_COMPLETED`, `QS_CANCELLED`, `QS_FAILED`, `ALL_QUEUE_STATUSES`
- `canonical_json`, `sha256_dict`, `write_json_atomic`, `append_jsonl`

### Persistence
- Queue state saved to `.agentx-init/queue/queue_state.json`
- Manifest written to `.agentx-init/queue/queue_manifest.json`
- History appended to `.agentx-init/queue/queue_history.jsonl`
- File locking via `.agentx-init/queue/.queue.lock`

## Schema
`schemas/task_queue_item.schema.json` (Draft-07) validates task queue item payloads.

## Dependencies
- `agentx_evolve.model.model_models` — `new_id`, `to_dict`
