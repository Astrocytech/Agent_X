# Milestones

This document is a high-level summary. The authoritative milestone definition is in:

> [`docs/development/AGENT_X_INITIATOR_ALL_MILESTONES_SUMMARY_v6.md`](development/AGENT_X_INITIATOR_ALL_MILESTONES_SUMMARY_v6.md)

## Quick Reference

| Stage | Active Commands | Key Components |
|---|---|---|
| **Product Milestone 1** (current) | `help`, `scan`, `status` | Config/Paths, Audit Log, Repository Scanner, Layer Mapper, Minimal Architecture Analyzer, Minimal Report Writer |
| **Product Milestone 2** (planned) | `explain`, `plan`, `propose`, `validate`, `audit`, `report`, `memory` | Governance Engine, Risk Engine, Evolution Planner, Patch Proposal Generator, Validation Runner, Memory Store, Expanded Report Writer |
| **Product Milestone 3** (future) | `graph` | Knowledge Graph |

## Key Distinctions

- **Component Milestone 1** ≠ **Product Milestone 1**. A component may have a complete contract while being scheduled for a later product milestone.
- PM1 is read-only toward source files. Only `.agentx-init/` is writable at runtime.
- Later commands are BLOCKED stubs returning `COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1`.

---

> **Synchronization Status:** This document is a summary. The authoritative milestone control document is `docs/development/AGENT_X_INITIATOR_ALL_MILESTONES_SUMMARY_v6.md`. All milestone placement, naming, and activation rules are defined there.
