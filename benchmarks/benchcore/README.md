# BenchCore Benchmark Pack

## Purpose

Agent_X has integrated BenchCore as a real-world benchmark pack that strengthens its universal-agent foundation.

> **Alias:** This directory is the repository-safe name for the **Scriptor** benchmark pack.
> See [ALIAS_TO_SCRIPTOR.md](ALIAS_TO_SCRIPTOR.md) for details.

## What It Is

A **governed, source-backed, replayable benchmark/capability pack** that:
- Sources 32 real-world BenchCore PDF documents across diverse domains
- Extracts semantic content, requirements, patterns, and test fixtures
- Provides schemas, visual inventories, and traceability matrices
- Includes sabotage testing and clean-replay verification
- Enforces claim boundaries to prevent overclaiming

## What It Is NOT

- **Not** instant universality — no single benchmark proves general intelligence
- **Not** full BenchCore implementation — only benchmark patterns, not production systems
- **Not** live systems capability — no real credentials, SSH, MySQL, WSL, or production dependencies

## 32 PDFs Covered

| Partition | Count | Description |
|-----------|-------|-------------|
| **Now** | 26 | Fully implemented with inventory, artifacts, and tests (includes 2 benchmark-only) |
| **Later** | 5 | Deferred: architecture part 2, remote log tailing, UI plugin, MySQL, WSL |
| **Optional / Later** | 1 | Camera change detection (optional benchmark) |

## Architecture Overview

```
Source Inventory (32 PDFs)
    ↓
Semantic Extraction (concepts, requirements, patterns)
    ↓
Schemas & Fixtures (valid/invalid/fixture data)
    ↓
Tests & Sabotage Tests (validation, rejection, replay)
    ↓
Evidence & Acceptance Reports (traceability, scoring)
    ↓
Claim Boundary Enforcement (universal claim rejection)
```

## Forbidden Claims

The following claims are explicitly rejected by `instant_universal_claim_rejection_test.json`:
- "Agent_X is now instantly universal"
- "Agent_X can now build any agent safely"
- "Agent_X has fully implemented BenchCore"
- "Agent_X can now operate live MOS, OverDrive, Inception, customer databases, SSH log tailing, WSL, or production systems"
- "One project benchmark proves general intelligence or universal agency"
- "Agent_X is now fully autonomous"
- "Agent_X can self-evolve without human review"

## Acceptance Report

See [reports/final_acceptance.md](reports/final_acceptance.md)
