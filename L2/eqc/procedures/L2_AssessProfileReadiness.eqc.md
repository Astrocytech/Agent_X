# Procedure: L2_AssessProfileReadiness

## Control Flow

```
Procedure L2_AssessProfileReadiness(profile, profile_catalog, policy):

1. Validate profile exists in catalog.
2. Check profile has all required fields.
3. Verify profile status is not deprecated or blocked.
4. Check profile has required_l1_units listed (even if empty).
5. Verify profile has evaluation_refs.
6. Calculate readiness score via build_profile_readiness_score.
7. Return readiness assessment.
```

## Inputs

- `profile`: A profile object.
- `profile_catalog`: The L2 profile catalog.
- `policy`: Policy overrides (optional).

## Outputs

- `ready`: boolean
- `score`: float 0.0–1.0
- `missing_items`: list of strings
- `warnings`: list of strings

## Runtime Authority

```
Runtime Authority: none
Implementation Authority: none
L1 Handoff Required For Implementation: true
```
