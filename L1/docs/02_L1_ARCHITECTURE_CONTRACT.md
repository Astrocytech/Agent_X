# L1 Architecture Contract

**Document ID:** `AX-L1-DOC-ARCH-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Boundary Rules

- L0 must not import L1 or L2.
- L1 may inspect L0 public contracts and proof outputs.
- L1 must not modify L0 without an explicit L0-impact FIC, proof plan, rollback plan, and review gate.
- L2 is reserved for specialization profiles and blueprints.
- Generated artifacts are validator-owned unless a FIC explicitly authorizes manual maintenance.

## Root Layers

```text
L0 = governed seed kernel
L1 = external evolution/controller layer
L2 = future specialization profiles and blueprints
```
