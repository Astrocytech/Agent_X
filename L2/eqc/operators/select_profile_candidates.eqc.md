# Operator: select_profile_candidates

## Purpose

Select candidate profiles from catalog matching a specialization type.

## Input

`specialization_type`: string from classification result.
`catalog`: The profile catalog.

## Output

`candidates`: list of profile objects matching the specialization type.

## Logic

1. Filter catalog to profiles with matching specialization_type.
2. Exclude profiles with status "deprecated" or "blocked".
3. Return filtered list.

## Purity Class

```
Purity Class: PURE
Determinism: deterministic
```
