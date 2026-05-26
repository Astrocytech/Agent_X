# FIC-L1-012: Failure Learning Updater

**fic_id:** `FIC-L1-012`
**unit_id:** `UNIT-L1-012`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/failure_learning_updater.py`

## Description

Records evidence failures and associated learning recommendations. Takes `ProofCheckResult` and produces structured `FailureRecord` and `LearningEntry` objects.

## Public surface

```python
__all__ = [
    "FailureRecord",
    "LearningEntry",
    "FailureLearningUpdater",
    "FailureLearningUpdaterError",
    "process_failures",
]
```

### Exports

- `FailureRecord` — frozen dataclass: `failure_id`, `check_name`, `details`
- `LearningEntry` — frozen dataclass: `entry_id`, `failure_id`, `recommendation`
- `FailureLearningUpdaterError` — base exception
- `FailureLearningUpdater` — class with `process(result)` and `recommend(failure, recommendation)` methods
- `process_failures(result) -> tuple[FailureRecord, ...]`

## Dependency contract

- **stdlib only** (dataclasses, typing)
- May import `ProofCheckResult` from `L1.controller.proof_check_runner`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Rules

1. Only checks with FAIL status produce FailureRecords.
2. `failure_id` follows `FAIL-L1-{n:03d}`.
3. `entry_id` follows `LRN-L1-{n:03d}`.

## Edge cases

| Case | Behavior |
|---|---|
| all pass | empty tuple |
| None input | Error |

## Test contract

Test file: `L1/tests/test_failure_learning_updater.py`

Required tests (10):
1. `test_records_failed_checks`
2. `test_skips_passing_checks`
3. `test_empty_returns_empty`
4. `test_failure_id_format`
5. `test_rejects_none`
6. `test_learning_entry_links_to_failure`
7. `test_failure_record_is_frozen`
8. `test_learning_entry_is_frozen`
9. `test_failure_learning_no_forbidden_imports`
10. `test_recommend_creates_entry`
