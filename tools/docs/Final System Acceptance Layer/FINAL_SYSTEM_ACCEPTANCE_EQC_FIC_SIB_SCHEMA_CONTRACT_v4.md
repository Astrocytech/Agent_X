# Final System Acceptance Layer — EQC / FIC / SIB Schema Contract v4

**roadmap_layer:** 19  
**roadmap_phase:** Phase E — Acceptance  

---

## 1. Contract Overview

This document defines the formal schema contract between the Final System Acceptance Layer and its consumers: **EQC** (Evolution Quality Controller), **FIC** (Final Integration Checker), and **SIB** (System Integrity Boundary). All three consumers rely on the `acceptance_check_result.schema.json` Draft-07 schema.

## 2. Schema Contract

**File:** `schemas/acceptance_check_result.schema.json`  
**$id:** `https://astrocytech.io/schemas/acceptance_check_result.schema.json`  
**$schema:** `http://json-schema.org/draft-07/schema#`  
**schema_id:** `acceptance_check_result.schema.json`  

### 2.1 Top-Level Object

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | string | no | Version of the schema format |
| `schema_id` | string | no | Canonical schema identifier |
| `report_id` | string | **yes** | Unique report identifier (prefix `ac-`) |
| `checks` | array[CheckResult] | **yes** | Ordered list of individual check results |
| `total` | integer | no | Total number of checks executed |
| `passed` | integer | no | Number of checks that passed |
| `failed` | integer | no | Number of checks that failed |
| `skipped` | integer | no | Number of checks that were skipped |
| `all_passed` | boolean | no | True iff failed === 0 |
| `checked_at` | string | no | ISO-8601 timestamp of check execution |
| `warnings` | array[string] | no | Non-fatal warnings |
| `errors` | array[string] | no | Fatal errors encountered |

### 2.2 CheckResult Object

| Field | Type | Required | Description |
|---|---|---|---|
| `check_name` | string | **yes** | Name of the acceptance check |
| `status` | string (enum) | **yes** | One of `"PASS"`, `"FAIL"`, `"SKIP"` |
| `details` | string | no | Human-readable detail message |
| `warnings` | array[string] | no | Check-level warnings |
| `errors` | array[string] | no | Check-level errors |

## 3. EQC Contract

**Evolution Quality Controller** consumes reports to decide whether an evolution cycle is healthy.

- Must receive a valid report conforming to the schema above.
- Checks `all_passed === true` to green-light promotion.
- Maintains a history in `history.jsonl` for trend analysis.

## 4. FIC Contract

**Final Integration Checker** verifies that the system is ready for deployment.

- Runs `AcceptanceCheck.run_all()` and validates output against the schema.
- Verifies that all 19 checks are present in the report.
- Rejects if any check status is FAIL.

## 5. SIB Contract

**System Integrity Boundary** enforces constraints on external facing surfaces.

- Uses `sha256_dict` to hash reports for audit trails.
- Relies on `write_json_atomic` for durable, crash-safe persistence.
- Uses `acquire_acceptance_lock` to prevent concurrent acceptance runs.

## 6. Example Valid Report

```json
{
  "schema_version": "1.0",
  "schema_id": "acceptance_check_result.schema.json",
  "report_id": "ac-a1b2c3d4e5f6",
  "checks": [
    {"check_name": "fresh_clone_install", "status": "PASS", "details": "Repo root and agentx_evolve package exist"}
  ],
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

## 7. Version History

| Version | Date | Notes |
|---|---|---|
| v1 | 2026-05-01 | Initial |
| v4 | 2026-06-05 | Schema ID, content hashing, EQC/FIC/SIB contracts |
