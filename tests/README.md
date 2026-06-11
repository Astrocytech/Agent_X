# Test Organization

Tests are organized into three tiers by speed and purpose:

| Tier | Directory | When to run | Expected time |
|------|-----------|-------------|---------------|
| **Quick** | `tests/quick/` | After every change (pre-commit) | ~4s |
| **Dev** | `tests/dev/` | Work-in-progress (may fail) | Varies |
| **Release** | `tests/release/` | Before release / CI | ~5min |

## Quick (`tests/quick/`)
Always-run tests that provide fast feedback:
- Unit tests for each agent
- Formatting guards (line endings, file integrity, Makefile wiring)
- Smoke checks (import/help validation)
- Schema validation tests
- Validator unit tests

## Dev (`tests/dev/`)
Tests under active development. May fail or be incomplete.
- Not included in CI or pre-commit hooks

## Release (`tests/release/`)
Full verification suite for release readiness:
- Integration tests (cross-component behavior, runtime flows, governance routing)
- System tests (CLI workflows, evolve-agent lifecycle)
- Benchmark validation tests (benchcore)
- Governance benchmarks (B001-B020)
- Regression tests (prompt injection, sabotage checks)
- Negative tests (rejection of invalid operations)
