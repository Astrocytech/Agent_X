# Operator: build_l1_handoff_proposal

## Purpose

Construct a structured L1 handoff proposal packet from a profile and evaluation.

## Input

`profile`: The selected profile.
`evaluation`: Readiness evaluation.

## Output

`proposal`: A handoff proposal packet.

## Fields

```
handoff_id: "L2-HANDOFF-<profile-short-id>"
source_profile_id: profile.global_profile_id
source_profile_path: profile path
target_l1_units: profile.required_l1_units
implementation_allowed_by_l2: false
l1_acceptance_required: true
l1_may_reject: true
risk_level: profile.risk_level
evaluation_refs: profile.evaluation_refs
status: "draft"
proposed_at_utc: current UTC timestamp
```

## Purity Class

```
Purity Class: PURE
Determinism: deterministic
```
