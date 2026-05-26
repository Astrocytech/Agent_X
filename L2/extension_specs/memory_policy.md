# Memory Policy

## Purpose
Define how L1/L2 components interact with L0 memory.

## Rules
- Memory writes go through L0 MemoryPort
- Memory reads are governed by profile permissions
- Cross-session memory requires explicit approval
- Evidence records are separate from operational memory

## Enforcement
- L0 governance enforces memory access rules
- Memory audit trail is part of evidence ledger
