# FIC-L1-009: Evidence Collector

**fic_id:** `FIC-L1-009`
**unit_id:** `UNIT-L1-009`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/evidence_collector.py`

## Description

Transforms `ProofCheckResult` into a structured `EvidenceBundle` of `EvidenceRecord` objects for downstream persistence.

## Public surface

```python
__all__ = [
    "EvidenceRecord",
    "EvidenceBundle",
    "EvidenceCollector",
    "EvidenceCollectorError",
    "collect_evidence",
]
```

### Exports

- `EvidenceRecord` — frozen dataclass: `evidence_id`, `check_name`, `status`, `details`
- `EvidenceBundle` — frozen dataclass: `records`, `total`, `passed`, `failed`, `all_passed`
- `EvidenceCollectorError` — base exception
- `EvidenceCollector` — class with `collect(result) -> EvidenceBundle`
- `collect_evidence(result) -> EvidenceBundle`

## Dependency contract

- **stdlib only** (dataclasses, typing)
- Imports `ProofCheckResult` from `L1.controller.proof_check_runner`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Rules

1. `evidence_id` follows `EVD-L1-{n:03d}`.
2. PASS maps to status `"pass"`; all others map to `"fail"`.

## Edge cases

| Case | Behavior |
|---|---|
| empty result | bundle with 0 records, all_passed=True |
| None input | Error |
| mixed pass/fail | correct counts |

## Test contract

Test file: `L1/tests/test_evidence_collector.py`

Required tests (10):
1. `test_collects_one_record_per_check`
2. `test_evidence_id_format`
3. `test_bundle_counts_correct`
4. `test_all_passed_true`
5. `test_all_passed_false`
6. `test_empty_result`
7. `test_record_is_frozen`
8. `test_bundle_is_frozen`
9. `test_evidence_collector_no_forbidden_imports`
10. `test_collect_rejects_none`
