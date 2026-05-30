# Operator: rank_profile_candidates

## Purpose

Rank profile candidates deterministically by risk level then profile ID.

## Input

`candidates`: list of profile objects.

## Output

`ranked`: list of profile objects sorted by risk_level ascending, then profile_id.

## Logic

1. Sort by risk_level priority (low < medium < high < critical).
2. Within same risk level, sort by profile_id lexicographically.
3. Return sorted list.

## Purity Class

```
Purity Class: PURE
Determinism: deterministic
```
