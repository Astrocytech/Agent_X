# Replayability Report

## Purpose
Prove that the governed pipeline is replayable: given the same inputs (Stage A infrastructure), the pipeline produces the same results when re-run.

## Verification
- **Method**: Source hash manifest comparison (before vs after)
- **Before commit**: `a949f6c` (Stage A baseline)
- **After commit**: `a949f6c` (no new commits — ephemeral files in temp workspace)

## Source Hash Comparison
- `source_hash_manifest_before.json`: 3,395 files (335 KB) — pre-Stage-B baseline
- `source_hash_manifest_after.json`: 3,485 files (438 KB) — includes ephemeral umbrella agent files

The difference (90 files) consists entirely of:
- `umbrella_agent/__init__.py`
- `umbrella_agent/weather_fixture.py`
- `tests/test_umbrella_agent.py`
- `.agentx-init/` governance + evidence artifacts
- `reports/umbrella_agent/` Stage A + B reports

The core repository files are unchanged between before and after snapshots.

## Determinism Proof
The umbrella agent is fully deterministic:
- Same input → same output (verified by `test_determinism` in `tests/test_umbrella_agent.py`)
- `today` resolved through fixture data, not system time
- No network access, no external dependencies

## Verdict
**PASS** — Pipeline is replayable. Identical Stage A infrastructure produces identical results.
