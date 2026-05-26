# Procedure: L2_BuildL1HandoffProposal

## Control Flow

```
Procedure L2_BuildL1HandoffProposal(profile, request, evaluation):

1. Validate profile is ready for handoff.
2. Collect profile identity and required L1 units.
3. Attach evaluation criteria.
4. Attach risk assessment.
5. Attach blueprint reference.
6. Set implementation_allowed_by_l2 to false.
7. Set l1_acceptance_required to true.
8. Return handoff proposal packet.
```

## Inputs

- `profile`: The selected profile.
- `request`: The original request.
- `evaluation`: Readiness evaluation from L2_AssessProfileReadiness.

## Outputs

- `handoff_proposal`: A structured handoff packet.
- `handoff_id`: string
- `status`: "draft"

## Runtime Authority

```
Runtime Authority: none
Implementation Authority: none
L1 Handoff Required For Implementation: true
```
