# L1: External Evolution / Controller Control Plane

L1 is the external evolution/controller control plane for Agent_X.
L1 does not run inside L0 and L0 must not import L1.

## Current authoritative scaffold

- `standards/` — canonical L1 standards
- `docs/` — L1 control-plane docs 00–11
- `fic/` — FIC registry and unit contracts
- `controller/` — governed L1 implementation modules
- `tests/` — L1 tests
- `sib/` — lightweight SIB sidecars
- `ecosystem/` — lightweight ES registry and graph
- `eqc/` — lightweight EQC procedures/operators/test vectors
- `generated/` — generated placeholders and validator outputs
- `evidence/` — evidence records and bootstrap logs

## Legacy/support directories

`L1/patch_planner/`, `L1/proof_runner/`, `L1/workflows/`, `L1/prompts/`, `L1/reports/` are legacy or support scaffolds unless explicitly registered in SIB/FIC.

## Historical notes

Files in `L1/docs/` such as `AGENT_X_AGENT_EVOLUTION_GUIDE_V11.md`, `EVOLUTION_ACCEPTANCE.md`, and `INVERSE_SCIENCE.txt` provide background but do not override current standards or FICs. See `L1/docs/HISTORICAL_NOTES_README.md`.

## Validation

```bash
make prove-l1
make prove-all
python L1/generated/bootstrap_validate_mode_a.py
```

## Status

Mode A scaffold exists. Release-grade L1 validation is not complete until schemas, digests, ES/SIB/EQC validators, and post-commit evidence are current.
