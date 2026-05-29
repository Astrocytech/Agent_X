# L2 Lightweight Workflow Standard

## Purpose

Define the workflow for creating and maintaining L2 profiles, blueprints, and
specifications.

## Workflow Steps

1. **System Goal** — Define what L2 should achieve.
2. **Profile Model** — Define the standard profile shape.
3. **Create Profiles** — Write YAML profile definitions.
4. **Create Blueprints** — Write specification documents for each profile.
5. **Define Integration Boundaries** — Document external system connections.
6. **Create Evaluation Specs** — Define how each profile is evaluated.
7. **Register in ES** — Add profiles and docs to ecosystem registry.
8. **Bind in SIB** — Bind profiles to future L1 handoff targets.
9. **Handoff to L1** — When ready, produce handoff packet for L1 FIC creation.

## Governance

L2 follows the same governance principles as L1 but at the specification level:

- All profiles must be registered in the ecosystem registry.
- All profiles must be bound to L1 targets via SIB.
- No L2 spec may violate the architecture contract.
- L2 does not issue FICs — L1 does.
