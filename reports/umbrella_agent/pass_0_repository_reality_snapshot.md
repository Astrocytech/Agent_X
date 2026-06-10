# Pass 0 — Repository Reality Snapshot

## Repository State
- **Branch:** main
- **Commit:** 6143fb0dd5a4abab11e19c236c6e6544211d155d
- **Dirty:** No (working tree clean)
- **Date:** 2026-06-09

## File Tree Summary

### Policy registry (`tools/agentx_evolve/policy/`)
15 source `.py` files: capability_policy, capability_registry, initiator_policy_compat, model_policy, policy_decision, policy_defaults, policy_enforcer, policy_evidence, policy_loader, policy_models, policy_registry, policy_request, role_matrix, sandbox_policy_compat, tool_policy.

### Patch execution (`tools/agentx_evolve/patch_execution/`)
11 source `.py` files: implementation_validation_gate, initiator_patch_compat, patch_applier, patch_evidence, patch_execution_service, patch_models, patch_policy, patch_session, rollback_manager, session_lock, source_change_guard.

### Evidence (`tools/agentx_evolve/evidence/`)
Empty (only `.gitkeep`).

### Tests
- `tests/integration/` — 13 test files
- `tests/system/` — 16 test files
- `tests/regression/` — 3 test files
- `tests/smoke/` — empty (only .gitkeep)
- No umbrella-specific test directories exist.

### Schemas
- No top-level `schemas/` directory (created by this milestone).
- Canonical schemas under `tools/agentx_evolve/schemas/` (478 files across 22 subdirs).

### Reports
- `reports/umbrella_agent/` — created by this milestone (currently empty).

### Existing Makefile targets
audit-structure, build-seed, clean, help, install, prove-all, prove-format, prove-hygiene, prove-organization, prove-seed, run, seed-boot, test-all, test-evolve, test-initiator, test-integration, test-live, test-regression, test-smoke, test-system.

### Implementation modules under `tools/agentx_evolve/`
50+ subdirectories covering: acceptance, context, context_builder, docs, docs_sync, docsync, evaluation, evidence, examples, failure, failure_taxonomy, final_acceptance, fixtures, git, human_review, learning, llm_worker, local_runtime, mcp, model_adapter, model_runtime, models, monitoring, orchestrator, packaging, patch, patch_execution, policy, promotion, prompts, providers, queue, recovery, review, runtime, scheduler, schemas, scripts, security, tests, tools, worker, workers, workflows.

### Evidence directories
- `.agentx-init/evidence/` — runtime evidence path
- `tools/agentx_evolve/docs/` — 22 report/matrix files from prior milestone

### Umbrella-related files
None exist in the repository. No files contain "umbrella" in name or content.
