# FIC-L1-005: FIC Generator

**fic_id:** `FIC-L1-005`
**unit_id:** `UNIT-L1-005`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/fic_generator.py`

## Description

Takes a `UnitPlan` and generates `FicTemplate` data structures — one per planned unit. Each template contains the standard FIC fields (fic_id, unit_id, target_file, description, status, version).

## Public surface

```python
__all__ = [
    "FicTemplate",
    "FicGenerator",
    "FicGeneratorError",
    "generate_fics",
]
```

### Exports

- `FicTemplate` — frozen dataclass: `fic_id`, `unit_id`, `target_file`, `description`, `status`, `version`
- `FicGeneratorError` — base exception
- `FicGenerator` — class:
  - `generate(self, unit_plan: UnitPlan) -> tuple[FicTemplate, ...]`
- `generate_fics(unit_plan: UnitPlan) -> tuple[FicTemplate, ...]`

## Naming convention

- `fic_id`: `FIC-L1-PLAN-{n:03d}` (not a real FIC — these are planning stubs)
- `unit_id`: from the `PlannedUnit.unit_id`
- `target_file`: `L1/controller/unit_{n:03d}.py` (default; may be overridden)
- `status`: always `"draft"` for generated templates
- `version`: always `"v0.1.0"` for generated templates

## Dependency contract

- **stdlib only** (dataclasses, typing)
- May import `UnitPlan`, `PlannedUnit` from `L1.controller.unit_planner`
- May import `GoalType` from `L1.controller.goal_classifier`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. One `FicTemplate` per `PlannedUnit` in the plan.
2. `description` comes from `PlannedUnit.description`.
3. All templates default to `status="draft"` and `version="v0.1.0"`.
4. `generate` returns an empty tuple if the plan has no units.
5. Does NOT write files — only returns data structures.

## Edge cases

| Case | Behavior |
|---|---|
| plan with zero units | empty tuple |
| plan with many units | one template per unit |
| None or wrong type | `FicGeneratorError` |

## Test contract

Test file: `L1/tests/test_fic_generator.py`

Required tests (12):
1. `test_generates_one_template_per_unit`
2. `test_template_contains_unit_description`
3. `test_template_status_is_draft`
4. `test_template_version_is_v0_1_0`
5. `test_template_fic_id_format`
6. `test_template_unit_id_matches_planned`
7. `test_generates_empty_for_empty_plan`
8. `test_generates_for_single_unit_plan`
9. `test_generates_for_multi_unit_plan`
10. `test_template_is_frozen`
11. `test_fic_generator_no_forbidden_imports`
12. `test_generator_rejects_non_unit_plan`
