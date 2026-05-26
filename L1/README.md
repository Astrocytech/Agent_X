# L1: External Evolution / Controller Control Plane

L1 is the external evolution/controller control plane for Agent_X.
L1 does not run inside L0 and L0 must not import L1.

## Current authoritative scaffold

- `standards/` — canonical L1 standards
- `docs/` — L1 control-plane docs 00–11 (root FIC-governance documents below)
- `fic/` — FIC registry and unit contracts
- `controller/` — governed L1 implementation modules
- `tests/` — L1 tests
- `sib/` — lightweight SIB sidecars
- `ecosystem/` — lightweight ES registry and graph
- `eqc/` — lightweight EQC procedures/operators/test vectors
- `generated/` — generated placeholders and validator outputs
- `evidence/` — evidence records and bootstrap logs
- `target_taxonomy.yaml` — canonical target-kind taxonomy
- `evaluators/` — framework scoring criteria
- `promotion/` — framework promotion rules
- `schemas/` — framework package manifest schema/documentation
- `templates/` — comparison/evidence templates
- `fixtures/` — positive and negative validation fixtures
- `validators/` — executable taxonomy/profile/manifest validation

## FIC Governance Documents

L1 contains the root FIC-governance documents for Agent_X:

- `docs/00_L1_SYSTEM_GOAL.md`
- `docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md`
- `docs/05_L1_SHARED_TYPES_AND_INTERFACES.md`
- `docs/FIC_GOVERNANCE_INDEX.md`

These files define the root goal, whole-system governed workflow, shared lifecycle statuses, shared record types, interface contracts, and traceability vocabulary used by L1 FIC units.

They are governance documents, not runtime code.

Individual implementation-unit FIC contracts should live under `L1/fic/` and should cite these root documents.

L1 supports framework-target evaluation and promotion, but it is not itself
a runtime framework engine.

## Legacy/support directories

`L1/patch_planner/`, `L1/proof_runner/`, `L1/workflows/`, `L1/prompts/`, `L1/reports/` are legacy or support scaffolds unless explicitly registered in SIB/FIC.

## Historical notes

Files in `L1/docs/` such as `AGENT_X_AGENT_EVOLUTION_GUIDE_V11.md`, `EVOLUTION_ACCEPTANCE.md`, and `INVERSE_SCIENCE.txt` provide background but do not override current standards or FICs. See `L1/docs/HISTORICAL_NOTES_README.md`.

Older root-like L1 documents that overlap with the active FIC-governance root set are kept under `docs/archive/standards-root-duplicates/` as historical/background material only.

## Validation

```bash
make prove-l1
make prove-all
python L1/validators/bootstrap_validate_mode_a.py
```

## Status

Mode A scaffold exists. Release-grade L1 validation is not complete until schemas, digests, ES/SIB/EQC validators, and post-commit evidence are current.
