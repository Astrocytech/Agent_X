# L2 Handoff to L1 Rules

## When to Hand Off

L2 hands off to L1 when a profile requires implementation. The trigger is:

1. A profile is promoted from `draft` to `active` status.
2. An evaluation spec exists and defines measurable gates.
3. The required L1 units are identified.
4. Risk is assessed as acceptable.

## Handoff Packet

The L2 → L1 handoff packet contains:

```yaml
handoff:
  source: "L2"
  source_profile: "L2-PROFILE-XXX"
  target_l1_unit_ids: []
  blueprint_ref: ""
  evaluation_spec_ref: ""
  integration_spec_refs: []
  risk_assessment: ""
  special_instructions: ""
  implementation_allowed: false  # Set to true only by L1 FIC
```

## Handoff Rules

1. **No direct handoff without L1 FIC.**
   L2 may not create L1 FICs. L2 produces handoff proposals; L1's
   `goal_classifier` and `unit_planner` convert them to FICs.

2. **Implementation blocked until FIC is created.**
   `implementation_allowed: false` is the default and must remain false
   until an L1 FIC exists for the target unit.

3. **Handoff is one-way.**
   L2 proposes. L1 decides whether to implement. L2 does not follow
   the implementation into L1.

4. **Evidence remains in L1.**
   All implementation evidence, test results, and validation reports
   belong in L1. L2 registers profiles, not evidence.
