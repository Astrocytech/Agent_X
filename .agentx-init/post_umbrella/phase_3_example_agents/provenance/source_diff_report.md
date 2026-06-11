# Phase 3 — Source Diff Report

## Pipeline-Generated Files

### New Files Created
```
examples/clothing_advice_agent/helpers.py      (607 bytes) — RECOMMENDATION_LABELS, CONDITION_DESCRIPTIONS
examples/clothing_advice_agent/labels.py        (363 bytes) — RECOMMENDATION_LABELS
examples/daily_planning_agent/helpers.py       (111 bytes) — URGENCY_LABELS
examples/daily_planning_agent/labels.py         (111 bytes) — URGENCY_LABELS
```

### Pipeline-Evolved Files (Governed Patch Execution)
```
examples/clothing_advice_agent/helpers.py       — Added get_recommendation_label(temp_c: float) -> str
                                                  via run 8dd1742b (patch_applied: true, git apply --recount)
examples/daily_planning_agent/helpers.py        — Added validate_task_priority(priority: str) -> bool
                                                  via run 2bedf209 (patch_applied: true, git apply --recount)
```

### Stage A Manual Fixes
```
examples/clothing_advice_agent/planner.py       — Fixed data_source enum: 'fixture' → 'fixture|unavailable'
examples/clothing_advice_agent/planner.py       — Added get_recommendation_label (original, pre-patch-governance)
L0/CODE/tool_gateway/seed_tools/clothing_fixture_read.py
L0/CODE/tool_gateway/seed_tools/planning_fixture_read.py
tests/quick/clothing_advice_agent/test_clothing_advice.py
tests/quick/daily_planning_agent/test_daily_planning.py
tools/agentx_evolve/providers/opencode_provider.py   — plan agent + NL fallback parser
tools/agentx_evolve/workflows/evolve_agent.py        — pre-read files, rstrip("\n"), git apply --recount
tools/agentx_evolve/runtime/config.py                — BUILTIN_MODE = "apply"
```

### Provenance
- Stage A core agent code (planner.py, runtime.py, __init__.py) manually created
- helpers.py/labels.py created by original pipeline runs (OpenCode server wrote files directly)
- helpers.py evolved via governed patch execution in verification runs
- All 5 governance artifacts (proposal, policy, risk, human_review, promotion) auto-generated per run
