# L2 Background

## Why L2 Exists

Agent_X is structured as a layered architecture:

- **L0** provides seed data, MCTS-driven proof generation, and the mathematical core.
  It is intentionally narrow and stable. Changes require L0 FICs and strong evidence.

- **L1** provides governed implementation units: controllers, validators, FIC lifecycle,
  SIB/ES sidecar registries, evidence bootstrap, and test suites. L1 is responsible for
  turning specifications into implemented, tested, and evidenced code.

Between L0's stable core and L1's governed implementation, there is a gap: **what to build**.
L2 fills this gap as a profile/specification layer.

## The Gap

L1 knows *how* to implement. L1 does not know *what* to specialize toward.

L0 knows *what* is mathematically possible. L0 does not know *when* or *why* to
specialize Agent_X for different use cases.

L2 bridges this gap by defining:

- **Specialization profiles**: what kinds of agent behavior Agent_X should support
- **Blueprints**: how those behaviors should work at the specification level
- **Integration boundaries**: where external systems (PySR, Glyphser, Symbiant) connect
- **Evaluation specs**: how to measure success for each specialization

## Relationship to Other Layers

```
L0 (math core)         — stable, proven, minimal
  ↑ support
L1 (governed units)    — implements specs, produces evidence
  ↑ governed tasks
L2 (profiles/specs)    — proposes what to build, defines boundaries
```

L2 proposes. L1 governs implementation. L0 remains protected.
