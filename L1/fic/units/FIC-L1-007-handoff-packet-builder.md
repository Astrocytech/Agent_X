# FIC-L1-007: Handoff Packet Builder

**fic_id:** `FIC-L1-007`
**unit_id:** `UNIT-L1-007`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/handoff_packet_builder.py`

## Description

Takes validated `FicTemplate` records and the originating `UnitPlan`, and builds `HandoffPacket` bundles — one per template. Each packet combines the FIC template with complexity and dependency metadata from the plan.

## Public surface

```python
__all__ = [
    "HandoffPacket",
    "HandoffPacketBuilder",
    "HandoffPacketBuilderError",
    "build_handoff_packets",
]
```

### Exports

- `HandoffPacket` — frozen dataclass: `packet_id`, `fic_id`, `unit_id`, `target_file`, `description`, `complexity`, `dependencies`, `status`
- `HandoffPacketBuilderError` — base exception
- `HandoffPacketBuilder` — class:
  - `build(self, templates: tuple[FicTemplate, ...], unit_plan: UnitPlan) -> tuple[HandoffPacket, ...]`
- `build_handoff_packets(templates, unit_plan) -> tuple[HandoffPacket, ...]`

## Mapping rules

The builder pairs each `FicTemplate` with the corresponding `PlannedUnit` (by index). If counts mismatch, the shorter length wins and remaining items are dropped.

| Packet field | Source |
|---|---|
| `packet_id` | `"HOP-L1-{n:03d}"` |
| `fic_id` | `FicTemplate.fic_id` |
| `unit_id` | `FicTemplate.unit_id` |
| `target_file` | `FicTemplate.target_file` |
| `description` | `FicTemplate.description` |
| `complexity` | `PlannedUnit.complexity` |
| `dependencies` | `PlannedUnit.dependencies` |
| `status` | `"draft"` |

## Dependency contract

- **stdlib only** (dataclasses, typing)
- May import `FicTemplate` from `L1.controller.fic_generator`
- May import `UnitPlan` from `L1.controller.unit_planner`
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. Each packet is frozen.
2. `build` never raises — returns at least an empty tuple.
3. If counts mismatch, the minimum length is used.
4. All packets get `status="draft"`.

## Edge cases

| Case | Behavior |
|---|---|
| templates=(), plan has units | empty tuple |
| templates non-empty, plan empty | empty tuple |
| counts mismatch | min(len(templates), len(plan.units)) packets |
| None arguments | `HandoffPacketBuilderError` |

## Test contract

Test file: `L1/tests/test_handoff_packet_builder.py`

Required tests (12):
1. `test_builds_one_packet_per_unit`
2. `test_packet_contains_fic_id_from_template`
3. `test_packet_contains_complexity_from_plan`
4. `test_packet_contains_dependencies_from_plan`
5. `test_packet_status_is_draft`
6. `test_packet_id_format`
7. `test_empty_templates_returns_empty`
8. `test_empty_plan_returns_empty`
9. `test_count_mismatch_uses_minimum`
10. `test_packet_is_frozen`
11. `test_handoff_builder_no_forbidden_imports`
12. `test_builder_rejects_none`
