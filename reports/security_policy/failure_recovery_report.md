# Failure Recovery Report

**Gate:** 11
**JSON data:** `reports/security_policy/failure_recovery_report.json`

## Failure Taxonomy

| Failure | Recovery |
|---|---|
| Source validation failure | Rollback patch |
| Schema validation failure | Reject patch |
| Test failure | Rollback and report |
| Dependency conflict | Block deployment |

## Status: PASS
