# Repository Structure

## Root

- `L0/` — governed seed kernel.
- `L1/` — governance, FIC, validation, evidence, controlled evolution planning.
- `L2/` — specialization profiles, blueprints, evaluation specs.
- `tools/agentx_initiator/` — project inspection/initiation companion tool.
- `tools/agentx_evolve/` — runtime integration, chat, self-upgrade, init-agent, evolve-agent.
- `tests/` — cross-component, system, regression, and smoke tests.
- `docs/` — project-level documentation.
- `examples/` — user-facing examples.
- `requirements/` — dependency lists.

## Test Ownership

Unit and component tests live beside their owner.

Cross-component tests live under root `tests/`.

## Document Ownership

Layer-specific documents live inside the layer.

Tool-specific documents live inside the tool.

Project-wide documents live under root `docs/`.
