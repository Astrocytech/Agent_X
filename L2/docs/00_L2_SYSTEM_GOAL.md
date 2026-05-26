# L2 System Goal

L2 defines specialization profiles, blueprints, integration specs, and evaluation
specs that L1 can later convert into governed implementation work.

L2 does not execute tools, patch L0, bypass L1, or introduce runtime autonomy
directly.

## Core Principle

```
L2 proposes specialization.
L1 governs implementation.
L0 remains protected.
```

## Boundaries

| Layer | Role | Authority |
|-------|------|-----------|
| L0 | Seed data, MCTS proofs, math core | Immutable unless L0 FIC |
| L1 | Governed unit implementation, FICs, validators, evidence | Implementation authority |
| L2 | Profile/specification layer, specialization definitions | Proposal only — no runtime |

## What L2 Produces

- Profile definitions (YAML)
- Blueprints (specification documents)
- Integration boundary specs
- Evaluation plans
- Lightweight SIB / ES registrations
- Handoff proposals to L1

## What L2 Does Not Produce (yet)

- Runtime controller code
- Tool execution wrappers
- Autonomous agents
- Model routing
- Memory or state management
- Direct patches to any layer
