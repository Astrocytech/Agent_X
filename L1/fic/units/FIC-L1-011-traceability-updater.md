# FIC-L1-011: Traceability Updater

**fic_id:** `FIC-L1-011`
**unit_id:** `UNIT-L1-011`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/traceability_updater.py`

## Description

Builds a `TraceabilityGraph` linking completion records to handoff packets for a full unit lifecycle audit trail.

## Public surface

```python
__all__ = [
    "TraceLink",
    "TraceabilityGraph",
    "TraceabilityUpdater",
    "TraceabilityUpdaterError",
    "build_traceability_graph",
]
```

### Exports

- `TraceLink` — frozen dataclass: `source_id`, `target_id`, `relationship`
- `TraceabilityGraph` — frozen dataclass: `links`, `nodes`
- `TraceabilityUpdaterError` — base exception
- `TraceabilityUpdater` — class with `add_link(source, target, relationship)` and `get_graph() -> TraceabilityGraph`
- `build_traceability_graph(completion_records, handoff_packets) -> TraceabilityGraph`

## Dependency contract

- **stdlib only** (dataclasses, typing)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`

## Rules

1. Duplicate links (same source+target+relationship) are silently ignored.

## Edge cases

| Case | Behavior |
|---|---|
| empty inputs | empty graph (no links, no nodes) |
| duplicate links | deduplicated |

## Test contract

Test file: `L1/tests/test_traceability_updater.py`

Required tests (10):
1. `test_add_link_creates_link`
2. `test_get_graph_returns_graph`
3. `test_dedup_links`
4. `test_empty_graph`
5. `test_link_is_frozen`
6. `test_graph_is_frozen`
7. `test_traceability_updater_no_forbidden_imports`
8. `test_build_traceability_graph_function`
9. `test_nodes_deduped_in_graph`
10. `test_graph_nodes_sorted`
