# FIC-L1-013: Boundary Checker

**fic_id:** `FIC-L1-013`
**unit_id:** `UNIT-L1-013`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/boundary_checker.py`

## Description

Validates that proposed file changes respect L0/L1/L2 boundaries. Rejects changes that modify L0 files or touch disallowed paths.

## Public surface

```python
__all__ = [
    "BoundaryCheck",
    "BoundaryCheckResult",
    "BoundaryChecker",
    "BoundaryCheckerError",
    "check_boundaries",
]
```

### Exports

- `BoundaryCheck` — frozen dataclass: `check_name`, `passed`, `message`
- `BoundaryCheckResult` — frozen dataclass: `checks`, `all_passed`
- `BoundaryCheckerError` — base exception
- `BoundaryChecker` — class with `check(changed_files)` method
- `check_boundaries(changed_files) -> BoundaryCheckResult`

## Built-in checks

| Check | Rule |
|---|---|
| `no_l0_changes` | No path starts with `L0/` |
| `paths_are_relative` | All paths are relative (no leading `/`) |

## Dependency contract

- **stdlib only** (dataclasses, typing)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Rules

1. All checks run regardless of prior failures.
2. Empty changed_files → all_passed=True.
3. None input → BoundaryCheckerError.

## Test contract

Test file: `L1/tests/test_boundary_checker.py`

Required tests (10):
1. `test_accepts_l1_only_changes`
2. `test_rejects_l0_changes`
3. `test_empty_list_passes`
4. `test_rejects_none`
5. `test_multiple_checks_all_fail`
6. `test_mixed_checks`
7. `test_check_is_frozen`
8. `test_result_is_frozen`
9. `test_boundary_checker_no_forbidden_imports`
10. `test_all_checks_run_despite_failure`
