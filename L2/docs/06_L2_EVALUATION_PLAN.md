# L2 Evaluation Plan

## Evaluation Model

Each profile has an associated evaluation spec in `L2/evaluation_specs/`.
Evaluation at L2 level is specification review and profile validation — not
runtime testing.

## Evaluation Types

| Type | Scope | Method |
|------|-------|--------|
| Profile validation | Single profile | Review YAML against profile model |
| Blueprint review | Single blueprint | Check clarity, completeness, L1 handoff readiness |
| Boundary check | Integration spec | Verify boundary rules are not violated |
| Catalog consistency | All profiles | Cross-check specialization types, L1 dependencies |

## Evaluation Flow

```
Profile draft → Blueprint created → Integration spec → Evaluation spec →
L1 handoff feasibility → Ready for L1 FIC
```

## Gate Criteria

Before an L2 profile can trigger an L1 FIC:

1. Profile YAML is valid against the profile model.
2. Blueprint exists and is coherent.
3. Evaluation spec exists and defines measurable criteria.
4. Integration boundaries are documented.
5. Risk level is assessed and acceptable.
6. No forbidden actions are present.

## Current Status

Profiles: draft. No formal evaluation has been performed yet.
Evaluation is triggered when a profile moves from draft to active.
