# Agent_X L2 — Profile/Specification Governance

L2 is the **profile and specification layer** for Agent_X. It defines
specialization profiles, blueprints, integration specs, and evaluation specs
that L1 can later convert into governed implementation work.

## Core Principle

```
L2 proposes specialization.
L1 governs implementation.
L0 remains protected.
```

## Structure

| Directory | Purpose |
|-----------|---------|
| `docs/` | System goal, architecture contract, profile model, catalog, boundaries, evaluation plan, risk ledger, traceability, handoff rules |
| `profiles/` | YAML profile definitions (4 profiles) |
| `blueprints/` | Specification documents for each profile |
| `integration_specs/` | External system integration boundaries |
| `evaluation_specs/` | Evaluation criteria per profile |
| `standards/` | Lightweight L2 standards (workflow, FIC, SIB, ES, EQC) |
| `ecosystem/` | ES registry and graph for L2 documents |
| `sib/` | SIB doc-registry, bindings, and graph linking profiles to L1 |
| `eqc/` | Lightweight EQC: manifest, operators, procedures |
| `generated/` | Placeholder bootstrap artifacts |
| `evidence/` | Reserved for future L2 evidence |
| `tests/` | Reserved for future L2 tests |

## Current Status

All profiles are **draft**. No L2 runtime code exists. No L2 implementation
has begun. L2 is a specification-only layer.

## Profiles

| Profile | Type | Status | Risk |
|---------|------|--------|------|
| Symbolic Regression Controller | symbolic-regression | draft | medium |
| Coding Agent | coding | draft | medium |
| Research Agent | research | draft | low |
| Repo Maintenance Agent | repo-maintenance | draft | low |

## Quick Start

```bash
# View all L2 profiles
ls L2/profiles/

# Read the system goal
cat L2/docs/00_L2_SYSTEM_GOAL.md

# View the ecosystem registry
cat L2/ecosystem/ecosystem-registry.yaml

# View SIB bindings to L1
cat L2/sib/sib-bindings.yaml
```
