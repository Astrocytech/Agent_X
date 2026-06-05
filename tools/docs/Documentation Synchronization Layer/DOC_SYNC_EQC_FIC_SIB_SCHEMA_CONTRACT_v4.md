# Documentation Synchronization Layer — EQC / FIC / SIB / Schema Contract v4

**Roadmap Layer:** 16  
**Roadmap Phase:** Phase E — Documentation  

## Schema Contract

| Field | Type | Required | Constraint |
|---|---|---|---|
| schema_version | string | yes | pattern `^1\.0$` |
| schema_id | string | yes | const `doc_sync_check.schema.json` |
| check_id | string | yes | free |
| created_at | string | yes | ISO 8601 |
| total_checks | integer | yes | >= 0 |
| drifts | array | yes | array of Drift objects |
| passed | boolean | yes | — |
| warnings | array of string | yes | — |
| errors | array of string | yes | — |

## Drift Object

| Field | Type | Required |
|---|---|---|
| location | string | no |
| expected | string | no |
| actual | string | no |
| severity | string | no |

## EQC (Exact Quality Criteria)

1. Every `DocSyncReport` must validate against `doc_sync_check.schema.json`.
2. `result_hash` must be SHA-256 of canonical JSON of report without result_hash.
3. `run_check` must write both report JSON and append history JSONL.

## FIC (Functional Integrity Criteria)

1. Lock must prevent concurrent docsync writes.
2. Lock timeout must raise `TimeoutError`.
3. `check_with_schema` must load schema from disk and extract `properties` keys.

## SIB (System Integration Boundary)

1. Persistence layer writes under `.agentx-init/docsync/`.
2. All public functions/classes exported from `docsync/__init__.py`.
