# FIC-L1-008: Proof/Check Runner

**fic_id:** `FIC-L1-008`
**unit_id:** `UNIT-L1-008`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/proof_check_runner.py`

## Description

Runs in-process proof checks against the repo filesystem. Supports file existence, content keyword, and directory checks. Produces structured `ProofCheckResult`.

## Public surface

```python
__all__ = [
    "CheckStatus",
    "ProofCheck",
    "ProofCheckResult",
    "ProofCheckRunner",
    "ProofCheckRunnerError",
    "run_proof_checks",
]
```

### Exports

- `CheckStatus` — enum: PENDING, PASS, FAIL, SKIPPED
- `ProofCheck` — frozen dataclass: `check_id`, `name`, `description`, `status`, `details`
- `ProofCheckResult` — frozen dataclass: `checks`, `all_passed`, `summary`
- `ProofCheckRunnerError` — base exception
- `ProofCheckRunner` — class with `add_check(name, desc, fn)` and `run_all() -> ProofCheckResult`
- `run_proof_checks(repo_root=".") -> ProofCheckResult`

## Dependency contract

- **stdlib only** (dataclasses, enum, pathlib, typing)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Built-in checks

| Check | What it validates |
|---|---|
| `validation_report_exists` | L1/generated/validation_report.md exists with keywords |
| `lockfile_exists` | L1/generated/semantic_lockfile.yaml exists with required fields |
| `readiness_report_exists` | L1/generated/readiness_report.md exists |
| `release_manifest_exists` | L1/generated/release_package_manifest.yaml exists |
| `evidence_directory_exists` | L1/evidence/ directory exists |
| `fic_index_exists` | L1/fic/index.fic.yaml exists |

## Edge cases

| Case | Behavior |
|---|---|
| file missing | check fails with details |
| empty checks list | all_passed=True |
| nonexistent repo_root | ProofCheckRunnerError on init |
| check function raises | caught, recorded as FAIL |

## Test contract

Test file: `L1/tests/test_proof_check_runner.py`

Required tests (14):
1. `test_all_checks_pass`
2. `test_some_checks_fail`
3. `test_empty_checks_passes`
4. `test_check_results_order`
5. `test_add_check_and_run`
6. `test_rejects_nonexistent_repo_root`
7. `test_check_id_format`
8. `test_check_is_frozen`
9. `test_result_is_frozen`
10. `test_proof_check_runner_no_forbidden_imports`
11. `test_status_enum_values`
12. `test_check_fn_exception_handling`
13. `test_run_proof_checks_function`
14. `test_builtin_checks_present`
