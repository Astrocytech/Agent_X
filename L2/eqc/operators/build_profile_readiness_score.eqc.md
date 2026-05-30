# Operator: build_profile_readiness_score

## Purpose

Calculate a numeric readiness score for a profile based on completeness.

## Input

`profile`: A profile object.

## Output

`score`: float 0.0–1.0.
`missing_items`: list of strings describing gaps.
`warnings`: list of strings.

## Logic

1. Check profile_id exists (weight 0.1).
2. Check version exists (weight 0.1).
3. Check purpose exists (weight 0.2).
4. Check required_l1_units listed (weight 0.2).
5. Check evaluation_refs exist (weight 0.2).
6. Check forbidden_actions populated (weight 0.2).
7. Sum weights for present fields = score.
8. Missing fields added to missing_items.

## Purity Class

```
Purity Class: PURE
Determinism: deterministic
```
