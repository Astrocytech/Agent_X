# Operator: decide_l1_handoff_required

## Purpose

Determine whether a selected profile requires L1 handoff for implementation.

## Input

`profile`: A profile object.
`request`: The original request.

## Output

`decision`: A map with:
- `handoff_required` (boolean)
- `reason` (string)
- `required_l1_units` (list of strings)

## Logic

1. If profile has `required_l1_units` listed, handoff is required.
2. If profile status is `draft`, handoff is not required yet — profile must be
   promoted to `active` first.
3. If profile `risk_level` is `critical`, handoff requires additional review.
4. Return the list of required L1 units from profile definition.
