# MySQL Restore Boundary

## Status: NOT IMPLEMENTED

This document defines the boundary for MySQL database restore operations. **This capability is not implemented and is deferred for future consideration.**

## Source
BENCHCORE-DOC-031

## Boundary Rules
1. **No DB automation**: The BenchCore benchmark pack must not include any MySQL client configurations, automated restore scripts, or database connection logic.
2. **No real SQL backups in repo**: No actual SQL dump files, backup archives, or database snapshots may be stored in this repository.
3. **No connection strings**: No MySQL hostnames, ports, usernames, passwords, or connection URIs may be present in any file in this repository.

## What Exists
- SQL mapping policies in `data_quality/sql_mapping_policy.json` define **traceability rules only** — they map XML elements to SQL statements conceptually.
- No SQL execution engine, database driver, or migration tool is included.

## Future Considerations (Deferred)
- If MySQL restore is implemented in a future phase, it must:
  - Use a dedicated secrets management system for credentials.
  - Support dry-run mode (validate without executing).
  - Include schema versioning and rollback capability.
  - Be independently testable with mock MySQL containers.

## Rationale
Database restore operations introduce significant operational risk and infrastructure dependencies. The current benchmark pack focuses on verifiable, self-contained evaluations that do not require live database access.
