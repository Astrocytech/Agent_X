# Final Replay Report

## Replay Requirements
Clean-checkout replay must be reproducible from a fresh clone.

## Command Sequence
1. `git clone <repo> /tmp/agentx-replay`
2. `cd /tmp/agentx-replay`
3. `PYTHONPATH=tools:L0/CODE python3 -m pytest tests/quick/ -q --tb=short`
4. `PYTHONPATH=tools:L0/CODE python3 -m pytest tests/release/test_governance_benchmarks.py -q --tb=short`

## Expected Results
- 59 unit tests pass
- 29 governance benchmark tests pass
- All 20 benchmark categories pass

## Fixture Mode
All agents use deterministic fixture tools (weather.fixture.read, clothing.fixture.read, planning.fixture.read).
No live API calls required for acceptance tests.

## Verdict
Replay verified. All commands reproducible from clean checkout.
