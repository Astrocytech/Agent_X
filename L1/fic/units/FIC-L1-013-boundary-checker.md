# FIC-L1-013: Boundary Checker

**Status:** `draft`
**Version:** `v0.1.0`
**Layer:** 1
**Risk Level:** medium
**Enforcement Profile:** standard

**Target File:** `L1/controller/boundary_checker.py`

## Description

Validates that proposed changes respect L0 boundaries.

## Interface

- `check(proposed_change: dict) -> dict`

## Rules

- BoundaryChecker must not modify L0 files outside of permitted patterns.
- BoundaryChecker must reject changes that add L0 → L1/L2 imports.
