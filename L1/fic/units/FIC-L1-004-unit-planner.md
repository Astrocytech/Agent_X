# FIC-L1-004: Unit Planner

**fic_id:** `FIC-L1-004`
**unit_id:** `UNIT-L1-004`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/unit_planner.py`

## Description

Takes a classified `GoalRecord` and plans a set of bounded, reviewable implementation units. Each unit has a description, complexity estimate, and optional dependency list.

## Public surface

```python
__all__ = [
    "UnitComplexity",
    "PlannedUnit",
    "UnitPlan",
    "UnitPlanner",
    "UnitPlannerError",
    "plan_from_goal",
]
```

### Exports

- `UnitComplexity` — enum: `SMALL`, `MEDIUM`, `LARGE`
- `PlannedUnit` — frozen dataclass: `unit_id`, `description`, `complexity`, `dependencies`
- `UnitPlan` — frozen dataclass: `goal_summary`, `units`, `total_units`
- `UnitPlannerError` — base exception
- `UnitPlanner` — class:
  - `plan(self, goal_record: GoalRecord) -> UnitPlan`
- `plan_from_goal(goal_record) -> UnitPlan`

## Planning rules (deterministic)

| Goal Type | Splitting strategy |
|---|---|
| FEATURE | Split on " and ", ",", "; " at the sentence level; each phrase becomes a unit |
| BUG_FIX | Single unit (unless multiple "and"-separated bugs detected) |
| REFACTOR | Split on " and ", "," |
| RESEARCH | Single unit |
| DOCUMENTATION | Split on " and ", "," at sentence level |
| INFRASTRUCTURE | Split on " and ", "," |

**Complexity assignment:**
- SYSTEM scope → `LARGE`
- CROSS_COMPONENT scope → `MEDIUM`
- COMPONENT scope → `SMALL`

**Dependencies:**
- Units are ordered; each subsequent unit may implicitly depend on prior units
- Explicit dependency keywords in unit descriptions ("depends on", "after", "once") create explicit edges

## Dependency contract

- **stdlib only** (enum, dataclasses, re, typing)
- May import `GoalRecord` from `L1.controller.goal_classifier`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. `plan` always returns a valid `UnitPlan` (at least one unit).
2. Empty or whitespace-only goal → single unit with summary as description.
3. Unit IDs follow pattern `UNIT-L1-PLAN-{n:03d}`.
4. `dependencies` is a tuple of unit_id strings (empty for first unit).
5. `total_units` equals `len(units)`.
6. No recursive splitting — one pass only.
7. Preserves original goal record's summary in `goal_summary`.

## Edge cases

| Case | Behavior |
|---|---|
| empty goal summary | single unit, description "Unnamed unit" |
| single sentence with no conjunctions | single unit |
| many split fragments (10+) | each fragment is a unit; no limit |
| goal with only constraints | single unit using first constraint as description |

## Test contract

Test file: `L1/tests/test_unit_planner.py`

Required tests (18):
1. `test_plans_feature_as_multiple_units`
2. `test_plans_bug_fix_as_single_unit`
3. `test_plans_refactor_as_multiple_units`
4. `test_plans_research_as_single_unit`
5. `test_assigns_large_complexity_for_system_scope`
6. `test_assigns_medium_complexity_for_cross_component`
7. `test_assigns_small_complexity_for_component_scope`
8. `test_unit_ids_are_sequential`
9. `test_first_unit_has_no_dependencies`
10. `test_plan_contains_goal_summary`
11. `test_plan_for_empty_goal_returns_one_unit`
12. `test_documentation_goal_split`
13. `test_infrastructure_goal_split`
14. `test_planned_unit_is_frozen`
15. `test_total_units_matches_length`
16. `test_full_round_trip_goal_to_plan`
17. `test_unit_planner_no_forbidden_imports`
18. `test_planner_rejects_non_goal_record`
