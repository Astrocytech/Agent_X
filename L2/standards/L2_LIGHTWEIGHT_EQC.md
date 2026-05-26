# L2 Lightweight EQC Standard

## Purpose

EQC at L2 separates named operators from procedure control flow for profile
selection and specialization logic. It is used selectively — only where L2
defines real algorithmic behavior.

## When to Use EQC at L2

- Profile selection logic (which profile to activate for a given request).
- Specialization classification (what type of request is this).
- L1 handoff decisions (does this require an L1 FIC).

## EQC Elements at L2

| Element | L2 Usage |
|---------|----------|
| Operators | Named functions: classify_specialization_request, select_profile, decide_l1_handoff_required |
| Procedures | Control flow: L2_SelectProfile |
| Manifests | Registry of EQC components |

## EQC Rules for L2

1. Operators must have single responsibility.
2. Procedures must be control-flow only (no hidden implementation).
3. No runtime code — EQC at L2 is specification only.
4. When an operator becomes implementation-ready, it moves to L1 via FIC.
