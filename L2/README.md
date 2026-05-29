# L2: Specialization Profiles and Integration Blueprints

L2 defines **specialization targets** for the L1 evolution controller. It contains profiles, blueprints, and specifications for different agent specializations.

L2 is a **specification-only layer**. It does not contain executable code.

## Contents

| Path | Purpose |
|---|---|
| `profiles/` | Agent specialization profiles (YAML) — coding agent, orchestrator, research agent, symbolic regression controller |
| `blueprints/` | Architecture blueprints for each specialization |
| `extension_specs/` | Extension policies — tool access, memory, model |
| `evaluation_specs/` | Evaluation criteria for each specialization |
| `integration_specs/` | Integration specifications for external libraries (PySR, Glyphser, Symbiant) |
| `tests/` | L2 structure tests |

## Direction

- L2 defines specialization targets for L1
- L2 profiles inform L1 evolution planning
- L2 **does not** contain executable autonomy
