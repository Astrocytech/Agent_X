# Agent_X Evolve Package Architecture

`tools/agentx_evolve/` contains the implementation packages for the self-evolution tool stack. Source modules are organized by capability. Runtime evidence is written to the repository-root `.agentx-init/`.

## Canonical Runtime Root

Use:

```text
.agentx-init/
```

Do not write active runtime state under:

```text
tools/agentx_evolve/.agentx-init/
tools/.agentx-init/
tools/agentx_initiator/.agentx-init/
```

Those nested runtime roots are not canonical.

## Canonical Layer Modules

1. Governed patch execution: `patch_execution/`
2. Tool/MCP adapter: `tools/`, `mcp/`
3. Model adapter: `models/`
4. Context builder/task packer: `context/`
5. LLM implementation worker: `worker/` and `workers/llm_implementation_worker/`
6. Self-evolution orchestrator: `orchestrator/`
7. Human review approval: `human_review/`
8. Promotion/release gate: `promotion/`
9. Long-term learning: `learning/`
10. Policy/capability registry: `policy/`
11. Task queue/session scheduler: `scheduler/`
12. Evaluation harness: `evaluation/`
13. Failure taxonomy/recovery: `recovery/`
14. Documentation synchronization: `docs_sync/`
15. Local model runtime profile: `model_runtime/`
16. Security sandbox/filesystem boundary: `security/`
17. Git integration: `git/`
18. Packaging/distribution: `packaging/`
19. Monitoring/observability: `monitoring/`
20. Final system acceptance: `final_acceptance/`
21. Backup/disaster recovery: `backup/`
22. Prompt contract/versioning: `prompts/`

## Compatibility Wrappers

Some directories exist for compatibility with older import names or document terminology:

- `patch/` wraps `patch_execution/`
- `docsync/` wraps `docs_sync/`
- `failure/` and `failure_taxonomy/` are compatibility surfaces around recovery/failure taxonomy concepts
- `context_builder/` is a compatibility surface around `context/`
- `llm_worker/` is a compatibility surface around worker implementations
- `local_runtime/`, `model_adapter/`, and `runtime/` are compatibility surfaces around `model_runtime/` and `models/`

Do not add new implementation logic to compatibility wrappers unless the wrapper itself is the documented canonical owner.

## Generated Files

Generated files, caches, and package metadata should not be treated as source architecture:

- `__pycache__/`
- `.pytest_cache/`
- `*.egg-info/`
- build output directories

These can be regenerated and should stay outside architecture decisions.
