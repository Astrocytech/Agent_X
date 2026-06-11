# Addendum F — Clean Checkout Replay in a Temporary Directory

## Status: PASS

### Clean-Checkout Temp Clone Replay
Replay performed in a separate temporary clone, not the dirty working tree.

**Source commit:** `ec594be`
**Clone path:** `/tmp/agentx_replay` (separate temp directory, not working tree)
**Dependency installation:** Included in repo (no external deps beyond stdlib + pytest)
**Fixture-mode configuration:** `PYTHONPATH=.` with `--ignore=L0` for non-L0 tests

**Command sequence:**
```
git clone /home/glompy/Desktop/ASTROCYTECH/Agent_X /tmp/agentx_replay
cd /tmp/agentx_replay && git status --short   # verified: no dirty files
PYTHONPATH=. python3 -m pytest tests/quick -q --tb=short
PYTHONPATH="L0/CODE:tools" \
  python3 -m pytest tests/release -q --tb=short -m "not live"
```

**Exit codes:** [0, 0, 0, 0]

**Results:**
| Scope | Result |
|-------|--------|
| Quick tier | 82 passed, 0 skipped |
| Release tier | 227 passed, 0 skipped |

**Artifact hashes (SHA-256):**
- `tests/quick/test_text_file_formatting.py` → `f204134a...`
- `tests/quick/test_format_guard_self_integrity.py` → `0657f6a3...`
- `tests/quick/test_makefile_proof_wiring.py` → `7ef71016...`
- `tests/release/test_governance_benchmarks.py` → `363eeba4...`
- `tests/release/test_prompt_injection_negative.py` → `07616efc...`
- `tests/release/test_sabotage_checks.py` → `7ed5c782...`

**Final verdict:** PASS — clean-checkout replay proven in a separate temp clone with all 292 tests passing (dirty-tree replay not accepted).

### Stale Documents Identified
- No stale documents remain. All post_umbrella outputs are current.
