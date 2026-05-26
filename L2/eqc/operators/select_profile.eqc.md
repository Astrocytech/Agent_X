# Operator: select_profile

## Purpose

Given a specialization classification, select matching profile candidates.

## Input

`classification`: Output of `classify_specialization_request`.

## Output

`candidates`: A list of profile objects, each with:
- `profile_id` (string)
- `name` (string)
- `status` (string)
- `reason` (string)
- `risk_level` (string)

## Logic

1. Look up `classification.specialization_type` in the profile catalog.
2. Filter to profiles with `status: draft` or `status: active`.
3. Exclude profiles whose `forbidden_actions` conflict with the request.
4. Return remaining profiles sorted by risk_level (lowest first).
5. If no match, return empty list.
