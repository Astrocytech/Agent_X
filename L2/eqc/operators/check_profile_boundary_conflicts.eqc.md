# Operator: check_profile_boundary_conflicts

## Purpose

Check if a given request conflicts with any of a profile's forbidden actions.

## Input

`profile`: A profile object.
`request`: The incoming request.

## Output

`conflicts`: list of strings describing conflicts.
`has_conflict`: boolean.

## Logic

1. For each forbidden_action in profile, check if request description matches.
2. If match found, add to conflicts list.
3. Return conflicts and has_conflict flag.

## Purity Class

```
Purity Class: PURE
Determinism: deterministic
```
