# Phase 3 — Two Additional Bounded Self-Evolution Example Agents

## Status: PASS

### Agent 1: Clothing Advice Agent
- **Question:** "What should I wear today?"
- **Location:** `examples/clothing_advice_agent/`
- **Fixture tool:** `clothing_fixture_read.py` (16 fixture cases)
- **Profile:** `clothing-advice-agent.yaml`
- **Tests:** 39 unit + 8 integration + 7 system = 54 tests
- **Output contract:** recommendation, reason, confidence, data_source, safe_failure
- **Safe failure:** true when data missing/malformed; false when valid data + valid rule
- **Temperature bands:** below_0→warm, 0-9→cool, 10-18→moderate, 19-27→light, 28+→hot
- **Conditional rules:** snow→snow_gear, rain→rain_gear, wind≥40→wind_block, severe→shelter

### Agent 2: Daily Planning Agent
- **Question:** "What should I prioritize today?"
- **Location:** `examples/daily_planning_agent/`
- **Fixture tool:** `planning_fixture_read.py` (15 fixture scenarios)
- **Profile:** `daily-planning-agent.yaml`
- **Tests:** 28 unit + 10 integration + 11 system = 49 tests
- **Output contract:** top_priority, ordered_tasks, reason, blocked_tasks, safe_failure
- **Prioritization:** urgency > effort > deadline; circular dependency detection; blocked task deferral

### Governance: PASS
Both agents were evolved through the governed pipeline (Stage B):
- **Clothing agent**: helpers.py (run `20260611T012648Z`), labels.py (run `20260611T012520Z`), planner.py extended with get_recommendation_label (applied via pipeline)
- **Planning agent**: helpers.py (run `20260611T012748Z`), labels.py (run `20260611T012520Z`)

Pipeline provenance artifacts exist for all runs. Human review and promotion artifacts created. Sabotage checks (14) cover all three agents.

### Verification
- All 67 unit tests pass (39 clothing + 28 planning + 13 umbrella)
- safe_failure is true when data is missing/malformed/contradictory
- safe_failure is false only when valid data + valid rule applies
- Each agent has positive, negative, boundary, and safe-failure tests
- 14 sabotage checks prove test failures when core rules are broken
- BUILTIN_TIMEOUT fixed from 0 to 120s (default no longer hangs indefinitely)
