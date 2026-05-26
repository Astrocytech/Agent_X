# L1 Coding Agent Handoff Rules

**Document ID:** `AX-L1-DOC-HANDOFF-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

## Purpose

This document defines the default handoff rules for coding agents.

## Rules

- Implement only the selected FIC unit.
- Do not edit outside permitted files.
- Do not edit L0 unless an explicit L0-impact FIC authorizes it.
- Stop with `BLOCKED` when required context is missing.
- Produce completion evidence for every implementation attempt.
