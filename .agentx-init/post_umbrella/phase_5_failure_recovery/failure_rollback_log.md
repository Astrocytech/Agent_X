# Phase 5 — Rollback Log

## Rollback Events

| Event | Trigger | Action Taken | Result | Evidence |
|-------|---------|-------------|--------|----------|
| F001 | Patch with invalid syntax | git apply rejects; pre-patch source preserved via git checkout | PASS | validation_report.json |
| F002 | Patch modifies protected L0/ path | _enforce_target_boundary raises PlanParseError before git apply | PASS | structured_plan.json error |
| F003 | Patch fails tests | Validation report marks FAIL; source not modified | PASS | validation_report.json |
| F004 | Partial patch application | git apply `--recount` fails atomically; no partial state | PASS | applied_patch.diff, validation_report.json |
| F005 | Malformed model output | StructuredPlanParser raises PlanParseError; no file writes occur | PASS | model_response.json, final_verdict.json |
| F006 | Schema-invalid model output | PlanParseError; no patch candidate created | PASS | model_response.json, plan error |
| F007 | Missing evidence artifact | check_missing_evidence_artifact returns violations; final verdict = FAIL | PASS | infrastructure_validator test result |
| F008 | Promotion without review | Promotion decision artifact missing review reference; verdict = FAIL | PASS | human_review.json, promotion_decision.json |
| F009 | Missing policy approval | Policy approval artifact absent; proposal status = pending | PASS | policy_approval.json, proposal_artifact.json |
| F010 | Rollback after failed patch | git checkout restores original files from index | PASS | failure_source_manifest_before.json, failure_source_manifest_after.json |
| F011 | No-op command target | check_noop_target returns True for commands with tests_run=0 | PASS | infrastructure_validator.py test |
| F012 | Evidence manifest hash mismatch | check_invalid_evidence_hash returns mismatched paths | PASS | infrastructure_validator.py test |
| F013 | Source hash mismatch | Source manifest validation detects tampered files | PASS | failure_source_manifest comparison |
| F014 | Generated file lacks provenance | check_provenance finds file not in stage_b origin set | PASS | infrastructure_validator.py test |
| F015 | Dependency change without approval | check_dependency_change_without_approval returns unapproved files | PASS | infrastructure_validator.py test |
| F016 | Event log malformed | validate_events_append_only returns False for duplicate IDs | PASS | infrastructure_validator.py test |
| F017 | Source diff omits changed file | Source diff report review detects omission | PASS | source_diff_report.md, evidence_manifest.json |
| F018 | Secret in evidence output | scan_secrets detects private key / API key patterns | PASS | infrastructure_validator.py test |
| F019 | Live provider in fixture mode | ProviderRouter rejects live mode; returns fixture provider | PASS | provider_router.py test |
| F020 | Unsupported release claim | check_unsupported_final_claim returns claims not in supported set | PASS | infrastructure_validator.py test |

## Summary

- 20/20 failure cases tested
- 20/20 rollback/recovery events documented
- Source state preserved in all cases (hashes match before/after manifests)
- All rollback behavior verified via governance benchmarks B010, B015-B020
