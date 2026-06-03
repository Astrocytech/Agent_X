# Agent_X Tool Development Docs

This directory contains the development documents for the self-evolution tool stack. Each layer directory is expected to contain exactly three markdown documents:

- implementation specification
- EQC/FIC/SIB/schema contract
- implementation review and definition of done

The directory names are descriptive. The canonical execution/order reference is the numbered list below.

## Layer Order

1. `Governed Patch Execution Layer`
2. `Tool MCP Adapter Layer`
3. `Model Adapter Layer`
4. `Context Builder Task Packer`
5. `LLM Implementation Worker`
6. `Self-Evolution Orchestrator`
7. `Human Review Approval Interface`
8. `Promotion Release Gate`
9. `Long-Term Learning Outcome Review Layer`
10. `Policy Capability Registry`
11. `Task Queue Session Scheduler`
12. `Evaluation Harness Regression Benchmark Layer`
13. `Failure Taxonomy Recovery Playbook`
14. `Documentation Synchronization Layer`
15. `Local Model Runtime Profile Layer`
16. `Security Sandbox Filesystem Boundary`
17. `Git Integration Layer`
18. `Packaging Distribution Layer`
19. `Monitoring Observability Layer`
20. `Final System Acceptance Layer`
21. `Backup Disaster Recovery Layer`
22. `Prompt Contract Prompt Versioning Layer`

## Runtime Artifact Rule

Runtime and evidence artifacts belong under the repository-root `.agentx-init/`.

Tool package directories such as `tools/agentx_evolve/` should contain source code, schemas, tests, fixtures, and package-local static resources. They should not contain active runtime state directories.

## Schema Order

`tools/agentx_evolve/schemas/` uses numbered directories. That numbered schema layout is the canonical schema ordering for the implemented tool stack.
