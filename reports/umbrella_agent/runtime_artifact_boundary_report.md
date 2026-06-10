# Runtime Artifact Boundary Report

## Purpose
Clearly distinguish between source files, tests, schemas, generated reports, runtime evidence, and ephemeral umbrella agent files.

## Classification

### Source Files (Permanent, Commit)
- `schemas/umbrella_agent_input.schema.json` — Interface contract
- `schemas/umbrella_weather_fixture.schema.json` — Fixture contract
- `schemas/umbrella_agent_output.schema.json` — Output contract
- `tools/agentx_evolve/evidence/evidence_writer.py` — Evidence utility
- `tools/agentx_evolve/evidence/event_logger.py` — Event log utility
- `tools/agentx_evolve/evidence/manifest_builder.py` — Manifest utility

### Tests (Permanent, Commit)
- `scripts/canary-patch-test.sh` — Canary patch verification
- `tools/agentx_evolve/tests/` — Evolve tool tests
- `tests/system/test_negative_*.py` — Negative security tests

### Schemas (Permanent, Commit)
- `schemas/umbrella_agent_*.schema.json` — Milestone contract schemas

### Generated Reports (Permanent, in reports/umbrella_agent/)
- All `pass_*`, `stage_*`, and `*_report.*` files — Milestone evidence

### Runtime Evidence (Ephemeral, in .agentx-init/ inside temp workspace)
- Session records, rollback snapshots, implementation history
- Not committed, discarded with temp workspace

### Umbrella Agent Source (Ephemeral, in temp workspace)
- `umbrella_agent/__init__.py`
- `umbrella_agent/weather_fixture.py`
- `tests/test_umbrella_agent.py`

## Boundary Rules
| Artifact Type | Location | Persistence |
|--------------|----------|-------------|
| Source files | repo root or `tools/` | permanent |
| Tests | `tests/` or `tools/*/tests/` | permanent |
| Schemas | `schemas/` | permanent |
| Reports | `reports/umbrella_agent/` | permanent |
| Runtime evidence | `.agentx-init/` | ephemeral |
| Umbrella agent | `umbrella_agent/` in temp workspace | ephemeral |

## Verdict
**PASS** — All artifact types are correctly classified and bounded.
