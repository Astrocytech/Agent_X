# Procedure: L2_SelectProfile

## Control Flow

```
Procedure L2_SelectProfile(request, profile_catalog, policy):

1. Validate request.
   - Check request has required fields.
   - If invalid, return error.

2. Classify specialization request.
   - Call classify_specialization_request(request).
   - If classification.type == "unknown", return no-match.

3. Select matching profile candidates.
   - Call select_profile(classification).
   - If candidates is empty, return no-match.

4. Reject profiles with forbidden boundary conflicts.
   - For each candidate, check request against forbidden_actions.
   - Remove candidates with conflicts.

5. Rank valid profiles deterministically.
   - Sort by risk_level ascending, then by profile_id.

6. Decide whether L1 handoff is required.
   - Call decide_l1_handoff_required(primary_candidate, request).

7. Return selected profile, reasons, and required L1 units.
```

## Inputs

- `request`: The incoming request object.
- `profile_catalog`: The L2 profile catalog.
- `policy`: Policy overrides (optional).

## Outputs

- `selected_profile`: The chosen profile, or null.
- `reasons`: Explanation of the decision.
- `required_l1_units`: List of L1 units needed for implementation.
- `handoff_required`: Whether L1 handoff is needed now.
