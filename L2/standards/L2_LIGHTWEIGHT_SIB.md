# L2 Lightweight SIB Standard

## Purpose

EQC-SIB at L2 binds profiles to future L1 handoff targets. It does not bind to
code yet — implementation bindings come later through L1 FICs.

## Binding Rules

1. Every profile must have at least one SIB binding to L1 units.
2. Binding strength is `REFERENCE` (not `IMPLEMENTS`) until L1 FIC exists.
3. `implementation_allowed: false` is the default.
4. SIB bindings are one-to-many: one profile may bind to multiple L1 units.
5. Changes to profiles propagate through SIB to L1 unit planning.

## L2 SIB Lifecycle

```
Profile created → SIB doc-registry entry → SIB binding created →
Profile promoted to active → L1 FIC created → implementation_allowed: true
```
