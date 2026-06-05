# Monitoring / Observability Layer — EQC / FIC / SIB / Schema Contract v4

**Roadmap Layer:** 17
**Roadmap Phase:** Phase E — Monitoring

---

## Schema Contract

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string (const `"1.0"`) | ✅ | Version identifier |
| `schema_id` | string (const `"monitoring_audit_event.schema.json"`) | ✅ | Schema identity |
| `event_id` | string (minLength 1) | ✅ | Unique event ID |
| `event_type` | string (minLength 1) | ✅ | One of `ALL_EVENT_TYPES` |
| `session_id` | string (minLength 1) | ✅ | Owning session |
| `component` | string (minLength 1) | ✅ | Source component name |
| `message` | string (minLength 1) | ✅ | Human-readable description |
| `timestamp` | string (format: date-time) | ✅ | UTC ISO-8601 |
| `warnings` | array of strings | ✅ | Warning messages |
| `errors` | array of strings | ✅ | Error messages |
| `metadata` | object | ❌ | Arbitrary structured data |

**File:** `schemas/monitoring_audit_event.schema.json`
**Draft:** Draft-07 (minified)

---

## Event Integrity Contract (EIC)

Each audit event produces a SHA-256 hash via `sha256_dict(event.to_dict())`.
This hash is embedded in `AuditEventHash` dataclass and returned in
`SessionInspector.inspect_session()` results as `event_hash`.

---

## Functional Interface Contract (FIC)

| Function | Input | Output | Side Effects |
|---|---|---|---|
| `canonical_json(data)` | `object` | `str` | None |
| `sha256_dict(data)` | `dict` | `str` (64 hex chars) | None |
| `write_json_atomic(path, data)` | `Path`, `dict` | `Path` | Creates/overwrites file atomically |
| `append_jsonl(path, data)` | `Path`, `dict` | `Path` | Appends line to JSONL file |
| `AuditLog.log()` | event_type, session_id, component, message, metadata | `AuditEvent` | In-memory append |
| `AuditLog.log_event()` | ... + warnings, errors | `AuditEvent` | In-memory + JSONL append |
| `AuditLog.write_latest_event(event)` | `AuditEvent` | `Path` | Atomic JSON write |
| `AuditLog.load_events_from_disk()` | None | None | Reads JSONL into memory |
| `AuditLog.acquire_audit_lock()` | None | `bool` | Creates `audit.lock` |
| `AuditLog.release_audit_lock()` | None | None | Releases `audit.lock` |
| `SessionInspector.inspect_session(sid)` | session_id | `dict` | None |
| `SessionInspector.get_session_summary(sid)` | session_id | `dict` | None |
| `SessionInspector.get_component_events(c)` | component | `list[AuditEvent]` | None |
| `SessionInspector.get_recent_events(n)` | count | `list[AuditEvent]` | None |

---

## Security / Isolation Boundary (SIB)

- Audit log files are written under `.agentx-init/monitoring/` with `mkdir(parents=True)`.
- File locking via `fcntl.flock` with non-blocking flag prevents concurrent write corruption.
- Atomic writes use `.tmp` + `replace()` to prevent partial writes.
- No secrets or credentials are logged — metadata is caller-provided.
