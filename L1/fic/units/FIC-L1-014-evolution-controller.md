# FIC-L1-014: Evolution Controller

**Status:** `draft`
**Version:** `v0.1.0`
**Layer:** 1
**Risk Level:** high
**Enforcement Profile:** strict

**Target File:** `L1/controller/evolution_controller.py`

## Description

Orchestrates the full L1 evolution workflow.

## Interface

- `evolve(target_capability: str) -> dict`

## Rules

- EvolutionController must invoke sub-controllers in order.
- EvolutionController must record completion evidence.
- EvolutionController must not import L0 or L2 packages.
