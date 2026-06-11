# Capability Least-Privilege Matrix

## Summary
Every example agent has capabilities strictly narrower than the full Agent_X system.

## Agent Capabilities

| Agent | Allowed Tools | Forbidden | Network | Provider |
|-------|--------------|-----------|---------|----------|
| Umbrella | weather.fixture.read, seed.emit_answer | All others | None (fixture) | fixture + LLM |
| Clothing | clothing.fixture.read, seed.emit_answer | All others | None (fixture) | fixture + LLM |
| Planning | planning.fixture.read, seed.emit_answer | All others | None (fixture) | fixture + LLM |
| Governance | validators, gate_policy, gate_decision | direct source mutation | None | deterministic |

## Principle of Least Privilege
Each agent is limited to:
1. Reading its own fixture data only
2. Emitting a structured answer only
3. No network access (fixture-only mode)
4. No L0/ or protected path writes
5. No arbitrary shell commands

## Verification
- Positive tests prove allowed actions work
- Negative tests (governance benchmarks B007-B008) prove forbidden actions fail
