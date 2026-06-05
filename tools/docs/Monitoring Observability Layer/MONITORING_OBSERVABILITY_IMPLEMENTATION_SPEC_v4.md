# Monitoring / Observability Layer — Implementation Spec v4

**Roadmap Layer:** 17
**Roadmap Phase:** Phase E — Monitoring
**Module:** `agentx_evolve.monitoring`

---

## 1. Overview

The Monitoring / Observability Layer provides structured audit event tracking,
persistent JSONL logging, session inspection, and file-level locking for the
Agent_X self-evolving system.

---

## 2. Components

### 2.1 Constants
| Constant | Value |
|---|---|
| `MN_SCHEMA_VERSION` | `"1.0"` |
| `MN_SCHEMA_ID` | `"monitoring_audit_event.schema.json"` |
| `MN_EVENT_AUDIT` | `"AUDIT"` |
| `MN_EVENT_ERROR` | `"ERROR"` |
| `MN_EVENT_WARN` | `"WARN"` |
| `MN_EVENT_INFO` | `"INFO"` |
| `ALL_EVENT_TYPES` | `[AUDIT, ERROR, WARN, INFO]` |

### 2.2 Helper Functions
- `canonical_json(data)` — compact deterministic JSON via `sort_keys` + compact separators.
- `sha256_dict(data)` — SHA-256 hex digest of canonical JSON.
- `write_json_atomic(path, data)` — atomic write via `.tmp` + replace.
- `append_jsonl(path, data)` — append one JSON line to a JSONL file.

### 2.3 Dataclasses
- **`AuditEvent`** — event_id, event_type, session_id, component, message, timestamp, metadata, warnings, errors.
- **`AuditEventHash`** — single field `event_hash` computed via `sha256_dict(event.to_dict())`.

### 2.4 AuditLog
- `log()` — in-memory append only.
- `log_event()` — append to in-memory list **and** persist to `audit_log.jsonl`.
- `write_latest_event()` — atomic write of latest event to `latest_audit_event.json`.
- `load_events_from_disk()` — load existing JSONL events on init.
- `acquire_audit_lock()` / `release_audit_lock()` — `fcntl.flock` based file lock on `audit.lock`.

### 2.5 SessionInspector
- `inspect_session(session_id)` — structured dict with per-event `event_hash`.
- `get_session_summary(session_id)` — counts by type, error/warning totals.
- `get_component_events(component)` — filter by component.
- `get_recent_events(count)` — last N events across sessions.

---

## 3. Schema

File: `schemas/monitoring_audit_event.schema.json` (Draft-07, minified).

Required fields: `schema_version`, `schema_id`, `event_id`, `event_type`, `session_id`, `component`, `message`, `timestamp`, `warnings`, `errors`.
Optional: `metadata` (object).
