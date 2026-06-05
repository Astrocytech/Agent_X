# Packaging Distribution Layer — EQC / FIC / SIB / Schema Contract v4

**Roadmap Layer:** 18
**Roadmap Phase:** Phase E — Packaging

## Schema Contract

| Field | Type | Required | Constraint |
|---|---|---|---|
| schema_version | string | yes | pattern `^1\.0$` |
| schema_id | string | yes | const `packaging_distribution_check.schema.json` |
| check_id | string | yes | free |
| fresh_clone_install | string | yes | enum `PASS`, `FAIL`, `WARN` |
| optional_dependencies | string | no | enum `PASS`, `FAIL`, `WARN` |
| base_install_no_gpu | string | yes | enum `PASS`, `FAIL`, `WARN` |
| commands_available | array of string | yes | — |
| dep_groups_defined | array of string | yes | — |
| checks | array | yes | array of PackagingCheckResult |
| checked_at | string | yes | ISO 8601 |
| warnings | array of string | yes | — |
| errors | array of string | yes | — |

## PackagingCheckResult Object

| Field | Type | Required |
|---|---|---|
| check_name | string | yes |
| status | string | yes (PASS/FAIL/WARN) |
| details | string | no |
| warnings | array of string | no |
| errors | array of string | no |

## EQC (Exact Quality Criteria)

1. Every `PackagingDistributionCheck` report must satisfy `validate_schema()` with zero errors.
2. `result_hash` must be SHA-256 of canonical JSON of report without result_hash.
3. `run_check` with `repo_root` must write both report JSON and append history JSONL.

## FIC (Functional Integrity Criteria)

1. Lock must prevent concurrent packaging writes.
2. Lock timeout must raise `TimeoutError`.
3. `validate_schema` must reject missing required fields and invalid status enum values.

## SIB (System Integration Boundary)

1. Persistence layer writes under `.agentx-init/packaging/`.
2. All public functions/classes exported from `packaging/__init__.py`.
