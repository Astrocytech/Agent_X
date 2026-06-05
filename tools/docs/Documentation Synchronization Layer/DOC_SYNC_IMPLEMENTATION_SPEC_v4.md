# Documentation Synchronization Layer — Implementation Spec v4

**Roadmap Layer:** 16  
**Roadmap Phase:** Phase E — Documentation  
**Component:** agentx_evolve/docsync/  

## Overview

Layer 16 provides a dedicated Documentation Synchronization layer that detects drift between expected and actual documentation content, validates schema-document alignment, and persists check results for auditability.

## Modules

### doc_sync.py
- **DocDrift** — dataclass tracking a single drift: location, expected, actual, severity.
- **DocSyncResult** — dataclass with total_checks, drifts list, passed bool, warnings/errors.
- **DocSyncReport** — extends DocSyncResult with check_id, created_at, checks list, result_hash.
- **DocSyncChecker** — runs checks, persists reports, maintains history, acquires/releases file lock.
- **SchemaDocChecker** — validates schema fields against documented fields; `check_with_schema` loads a JSON schema file directly.

### Constants & Helpers
- `DS_SCHEMA_VERSION`, `DS_SCHEMA_ID`
- `DS_PASS`, `DS_FAIL`, `DS_WARN`, `DS_SKIP`
- `canonical_json`, `sha256_dict`, `write_json_atomic`, `append_jsonl`

### Persistence
- Reports written to `.agentx-init/docsync/doc_sync_check_report.json`
- History appended to `.agentx-init/docsync/doc_sync_history.jsonl`
- File locking via `.agentx-init/docsync/.docsync.lock`

## Schema
`schemas/doc_sync_check.schema.json` (Draft-07) validates check report payloads.

## Dependencies
- `agentx_evolve.model.model_models` — `new_id`, `utc_now_iso`, `to_dict`
