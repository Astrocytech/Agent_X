# L2 Lightweight EQC SIB Bridge Standard v0.4

## Purpose

Define how L2 SIB (Specification Integration Binder) bridges L2 profile/spec
artifacts to L1 implementation targets without authorizing implementation.

## Core Rule

```
L2 SIB binds profiles to future L1 handoff targets.
L2 SIB does not authorize implementation.
```

## Binding Model

| Field | Description |
|-------|-------------|
| `source_profile` | L2 profile global ID |
| `target_l1_units` | L1 unit IDs that may implement this profile |
| `binding_strength` | REFERENCE (default), DEPENDS, GOVERNS |
| `implementation_allowed` | Must be false until L1 FIC exists |

## Handoff Map

The `sib-l1-handoff-map.yaml` records which L2 profiles have proposed
handoff targets in L1. Each entry must set `implementation_allowed_by_l2: false`.

## Cross-Layer Rules

1. L2 SIB does not create L1 bindings — it proposes them.
2. L1 must accept or reject each binding via FIC.
3. L2 SIB may not modify L0 or L1 SIB registries.
4. All SIB artifacts must set `release_evidence: false`.

## Bridge Procedure

1. Register profile in L2 SIB doc-registry.
2. Create binding to target L1 units.
3. Create handoff map entry.
4. L1 reviews and accepts or rejects.
5. If accepted, L1 creates FIC-governed implementation.
6. L2 profile status remains `draft` until L1 FIC is active.
