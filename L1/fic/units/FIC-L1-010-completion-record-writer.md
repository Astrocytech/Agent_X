# FIC-L1-010: Completion Record Writer

**fic_id:** `FIC-L1-010`
**unit_id:** `UNIT-L1-010`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/completion_record_writer.py`

## Description

Writes a structured `CompletionRecord` from an `EvidenceBundle` for a given unit.

## Public surface

```python
__all__ = [
    "CompletionRecord",
    "CompletionRecordWriter",
    "CompletionRecordWriterError",
    "write_completion_record",
]
```

### Exports

- `CompletionRecord` — frozen dataclass: `unit_id`, `summary`, `evidence_total`, `evidence_passed`, `all_evidence_passed`, `status`
- `CompletionRecordWriterError` — base exception
- `CompletionRecordWriter` — class with `write(unit_id, summary, evidence_bundle) -> CompletionRecord`
- `write_completion_record(unit_id, summary, evidence_bundle) -> CompletionRecord`

## Status mapping

| Condition | status |
|---|---|
| total == 0 | no_evidence |
| all_passed | completed |
| otherwise | partial |

## Dependency contract

- **stdlib only** (dataclasses, typing)
- Imports `EvidenceBundle` from `L1.controller.evidence_collector`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Edge cases

| Case | Behavior |
|---|---|
| empty evidence | status=no_evidence |
| all evidence passes | status=completed |
| some failures | status=partial |
| None bundle | Error |

## Test contract

Test file: `L1/tests/test_completion_record_writer.py`

Required tests (10):
1. `test_writes_completed_status`
2. `test_writes_partial_status`
3. `test_writes_no_evidence_status`
4. `test_rejects_empty_unit_id`
5. `test_rejects_none_bundle`
6. `test_record_frozen`
7. `test_writer_error_type`
8. `test_completion_record_writer_no_forbidden_imports`
9. `test_write_completion_record_function`
10. `test_record_fields_correct`
