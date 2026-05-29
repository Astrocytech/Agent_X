# L1: External Evolution / Controller Layer

L1 is the **external evolution and controller layer** for Agent_X. It reads, verifies, and evolves L0 using the evolution doctrine.

L1 is **not** part of the L0 runtime. It is a separate set of tooling and scaffolding for an external coding agent or orchestrator.

## Contents

| Path | Purpose |
|---|---|
| `controller/` | Evolution controller, repo reader, boundary checker, evidence collector |
| `patch_planner/` | Patch plan data model and validation |
| `proof_runner/` | Proof suite execution wrapper |
| `workflows/` | Evolution workflow definitions (YAML) |
| `prompts/` | Evolution prompt packets for LLMs |
| `docs/` | Evolution guide, acceptance criteria, method doctrine |
| `reports/` | Evolution reports output directory |
| `tests/` | L1 structure and unit tests |

## Direction

- L1 reads/verifies/evolves L0
- L1 defines evolution targets for L2 profiles
- L1 **does not** import into L0 or make L0 depend on it
