# L1: External Evolution / Controller Control Plane

L1 is the external evolution/controller layer for Agent_X. It is not imported by L0 and does not make L0 depend on L1 or L2.

## Current status

Mode A scaffold: present.
Release-ready validation: not yet complete.

## Directory map

| Path | Purpose |
|---|---|
| `standards/` | Finalized L1 standards: EQC-FIC, Pseudocode-to-FIC workflow, lightweight SIB, lightweight ES, lightweight EQC |
| `docs/` | L1 control-plane documents `00–11` |
| `fic/` | FIC registry and unit implementation contracts |
| `controller/` | L1 implementation modules |
| `tests/` | L1 unit and structure tests |
| `sib/` | Lightweight SIB sidecars and schemas |
| `ecosystem/` | Lightweight ES registry, graph, and schemas |
| `eqc/` | Lightweight EQC operators, procedures, schemas, traces, and test vectors |
| `generated/` | Bootstrap/generated placeholders and validation artifacts |
| `evidence/` | Evidence records, completion records, review packets, and bootstrap logs |

## Commands

```bash
make prove-l1
make prove-all
```

## Boundary rule

L1 may inspect L0 contracts and proof outputs. L0 must not import L1 or L2.
