# Final System Acceptance Layer — Implementation Specification v4

**roadmap_layer:** 19  
**roadmap_phase:** Phase E — Acceptance  
**component:** `agentx_evolve/acceptance/`

---

## 1. Purpose

The Final System Acceptance Layer validates that the entire Agent X self-evolving system meets all 19 layer-level acceptance criteria before promotion or deployment. It provides deterministic, verifiable, and schema-enforced acceptance reports.

## 2. Architecture

```
acceptance/
├── __init__.py          # Public API re-exports
├── acceptance.py        # Core: checks, report, helpers, locking, schema validation
schemas/
├── acceptance_check_result.schema.json   # Schema for individual check results
tests/
├── test_acceptance.py   # Unit / integration tests
```

## 3. Core Data Structures

| Class / Constant | Purpose |
|---|---|
| `AcceptanceCheckResult` | Single check outcome (check_name, status, details, warnings, errors) |
| `AcceptanceReport` | Full report with aggregated stats and schema_id |
| `AcceptanceReportHash` | Wraps a report with a SHA-256 content hash |
| `AcceptanceCheck` | Check runner orchestrating all 19 named checks |
| `AC_SCHEMA_VERSION` | `"1.0"` |
| `AC_SCHEMA_ID` | `"acceptance_check_result.schema.json"` |
| `AC_CHECK_PASS / FAIL / SKIP` | Status constants |

## 4. 19 Acceptance Checks

| # | Check Name | What It Validates |
|---|---|---|
| 1 | fresh_clone_install | Repo root and package exist |
| 2 | initiator_commands | initiator_tools importable |
| 3 | patch_execution | patch_execution module importable |
| 4 | rollback | rollback_manager importable |
| 5 | source_guard | source_change_guard importable |
| 6 | llm_worker_output | worker module importable |
| 7 | orchestrator_session | orchestrator module importable |
| 8 | human_review | human_tools importable |
| 9 | promotion_gate | promotion module importable |
| 10 | audit_memory_graph | review module importable |
| 11 | no_l0_mutation | Git status clean (expected artifacts exempt) |
| 12 | no_uncontrolled_shell | safe_subprocess importable |
| 13 | no_network_default | network_policy importable |
| 14 | small_model_profile | model_models importable |
| 15 | schema_validation | compileall passes on agentx_evolve |
| 16 | tool_protocol | tool_registry importable |
| 17 | prompt_contracts | prompt_contract importable |
| 18 | backup_restore | backup_recovery importable |
| 19 | controlled_degradation | monitoring module importable |

## 5. Report Format (JSON)

```json
{
  "schema_version": "1.0",
  "schema_id": "acceptance_check_result.schema.json",
  "report_id": "ac-<uuid>",
  "checks": [ ... ],
  "total": 19,
  "passed": 19,
  "failed": 0,
  "skipped": 0,
  "all_passed": true,
  "checked_at": "2026-06-05T12:00:00+00:00",
  "warnings": [],
  "errors": []
}
```

## 6. Helpers

| Function | Purpose |
|---|---|
| `canonical_json` | Deterministic, minified JSON serialization |
| `sha256_dict` | SHA-256 of canonical JSON for content integrity |
| `write_json_atomic` | Atomic write via temp file + rename |
| `append_jsonl` | Append one JSON object per line to a file |
| `acquire_acceptance_lock` | Context manager for file-level exclusive lock |
| `validate_report_schema` | Validate a report against its Draft-07 schema |

## 7. Storage Layout

```
.agentx-init/acceptance/
├── acceptance_report_<report_id>.json   # Individual reports
├── history.jsonl                         # Append-only history
└── .acceptance.lock                      # Exclusive lock file
```

## 8. Dependencies

- `jsonschema` (optional, for schema validation)
- `fcntl` (POSIX file locking; fallback no-op on non-POSIX)

## 9. Version History

| Version | Date | Notes |
|---|---|---|
| v1 | 2026-05-01 | Initial |
| v4 | 2026-06-05 | Schema registry, content hashing, atomic I/O, locking |
