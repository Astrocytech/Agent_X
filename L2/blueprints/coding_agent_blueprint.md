# Coding Agent Blueprint

## Purpose
Build a coding agent capability on top of L0 governed kernel.

## Components
- L1 controller with patch planning and proof execution
- Code reading and analysis tools
- Patch application and verification pipeline

## Boundaries
- Cannot modify L0 kernel invariants
- Must run L0 proofs after every change
- Evidence must be recorded before/after each change

## Integration
- Uses L1 proof runner for verification
- Reads L0 manifests for constraint awareness
