# Stage B Replay Report

## Purpose
Prove that Stage B is fully replayable in a fresh temp workspace: identical inputs produce identical outputs.

## Method
1. Clone/checkout from pre-Stage-B commit `a949f6c` (post-Stage-A baseline)
2. Create fresh ephemeral git worktree
3. Re-run the governed pipeline: proposal → risk → context → prompt → patch → validate → evidence → review → promotion
4. Compare all outputs with the original Stage B run

## Idempotency Check
- **Workspace**: Fresh temp workspace each replay — no state leakage between runs
- **Fixture data**: Deterministic hardcoded data — same input produces same recommendation
- **Recommendation rules**: §3 deterministic — precip≥60→yes (0.7), 30–59→maybe (0.4), <30→no (0.8)
- **Path resolution**: Same `approved_paths` filter → same file set created
- **L0 guard**: `.agentx-init/` prefix blocked identically every run

## Output Comparison
| Artifact | Original | Replay | Match |
|----------|----------|--------|-------|
| `fixture_case_results.json` | 10/10 PASS | 10/10 PASS | YES |
| `patch_candidate.json` | 3 CREATE ops | 3 CREATE ops | YES |
| `patch_execution_report.json` | DRY_RUN+LIVE | DRY_RUN+LIVE | YES |
| `source_diff_report.json` | 3 added, 0 mod, 0 del | 3 added, 0 mod, 0 del | YES |
| `events.jsonl` | 20 events (A+B) | 20 events (A+B) | YES |

## Verdict
**PASS** — Stage B is fully replayable. A fresh temp workspace from the pre-Stage-B commit produces functionally identical results across all pipeline stages and evidence artifacts.
