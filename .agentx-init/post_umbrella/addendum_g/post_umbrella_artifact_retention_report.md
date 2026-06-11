# Addendum G — Artifact Retention and Non-Overwrite Rules

## Status: PASS

### Rules

1. **Stable run ID** — Every run uses UUID-based `run_<uuid>` directories. Phase output dirs are fixed per-phase and never overwritten.
2. **No silent overwrite** — Summary files (`post_umbrella_summary.md`, `phase_manifest_complete.json`) reference current state. Prior evidence in `.agentx-init/evidence/` is immutable.
3. **Append-only logs** — Event logs are validated by `validate_events_append_only()` which checks for duplicate IDs and sequential gaps.
4. **Failed-run retention** — `phase_5_failure_recovery/` retains before/after manifest pairs for every failure case. `check_missing_failed_run_evidence()` verifies all failed-run verdicts and evidence files.
5. **Rollback retention** — 20 rollback log files (P5-F001 through P5-F020) retain pre-rollback and post-rollback source manifests.
6. **Sabotage separation** — Sabotage-test evidence lives in `phase_3_example_agents/sabotage/` and is never mixed with acceptance-run evidence.
7. **No cleanup scripts** — No evidence cleanup scripts exist in the repository.

### Validations

| ID | Check | Function | Result |
|----|-------|----------|--------|
| G-VAL-01 | Detect overwritten prior evidence | `check_overwritten_evidence()` | PASS |
| G-VAL-02 | Detect missing failed-run evidence | `check_missing_failed_run_evidence()` | PASS |
| G-VAL-03 | Detect event log truncation | `check_event_log_truncation()` | PASS |
| G-VAL-04 | Detect reused run ID with different content | `check_reused_run_id()` | PASS |

### Evidence Summary

All 7 artifact retention rules are implemented and verified. All 4 validation checks exist in `infrastructure_validator.py`. The Spec G requirement is fully satisfied with no remaining gaps.
