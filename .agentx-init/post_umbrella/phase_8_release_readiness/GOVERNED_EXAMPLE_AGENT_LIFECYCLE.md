# Governed Example Agent Lifecycle

## Overview
Agent_X uses a governed pipeline for creating and evolving agents. Each agent goes through:

1. **Proposal** — What agent to create/evolve and why
2. **Policy Review** — Capability and risk assessment
3. **Risk Classification** — Severity and blast radius evaluation
4. **Context Packet** — Task description, relevant docs, prior evidence
5. **Prompt Contract** — Input/output schema for the model
6. **Model Execution** — LLM or deterministic worker produces output
7. **Patch Candidate** — Model output is packaged as a patch
8. **Patch Execution** — Patch is applied in a bounded session
9. **Validation** — Tests, schema, and evidence checks
10. **Rollback (if needed)** — Failed patches are reverted
11. **Evidence Recording** — All artifacts are hashed and stored
12. **Append-Only Event Log** — Every action is recorded
13. **Human Review** — A reviewer examines the validation evidence
14. **Promotion Decision** — Accepted or rejected

## Current State
- **Umbrella Agent**: Complete lifecycle with all 14 steps. Provenance exists in `reports/umbrella_agent/`.
- **Clothing Advice Agent**: Step 6-14 missing. Created manually (Stage A infrastructure work).
- **Daily Planning Agent**: Step 6-14 missing. Created manually (Stage A infrastructure work).

## Required Improvements
Re-run clothing and planning agents through the governed pipeline to complete the lifecycle.
