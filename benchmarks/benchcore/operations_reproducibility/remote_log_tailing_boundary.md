# Remote Log Tailing Boundary

## Status: NOT IMPLEMENTED

This document defines the boundary for remote log tailing operations. **This capability is not implemented and is deferred for future consideration.**

## Source
BENCHCORE-DOC-019

## Boundary Rules
1. **No SSH automation**: The BenchCore benchmark pack must not include any SSH client configurations, SSH command invocations, or SSH-based log retrieval automation.
2. **No credentials in repo**: No SSH keys, passwords, host keys, or connection strings may be stored in this repository under any circumstances.
3. **No live tailing**: No implementation of `tail -f` or equivalent over remote connections.

## What Exists
- Log parsing policies and fixtures in `data_quality/` operate on **local, static files only**.
- Log fixtures are synthetic and included directly in the benchmark pack.
- No mechanism to fetch logs from remote hosts exists or is planned in the current phase.

## Future Considerations (Deferred)
- If remote log tailing is implemented in a future phase, it must:
  - Use a dedicated secrets management system (not repo-stored credentials).
  - Support SSH key rotation and audit logging.
  - Be independently testable with mock SSH servers.
  - Have explicit opt-in configuration (disabled by default).

## Rationale
Remote log tailing introduces security, reliability, and reproducibility concerns that are outside the scope of the current benchmark pack. The focus is on grammar validation, data quality, and protocol architecture — all of which can be evaluated with local/synthetic data.
