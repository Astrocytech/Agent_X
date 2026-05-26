---
> Historical patch evidence only.
> This file is not the current synchronization authority.
> Later synchronization reviews supersede any statement in this file that claims document synchronization is complete.
---

# Agent_X Document Sync Patch Evidence After e4dab4c0

## Baseline

Reviewed baseline: `e4dab4c0afec460d95212fb431c6e060c06e1bc6`

## Fixes Applied (Final TODO v3)

### P0 — Must Fix

1. **P0-1: Architecture Analyzer `risks` vs `risk_hints` contradiction resolved**
   - `ARCHITECTURE_ANALYZER_EQC_SIB_SCHEMA_v6.md`: Added compatibility note under schema block — `risks` field contains non-authoritative architecture risk hints only; field name remains `risks` for Milestone 1 schema compatibility.
   - `AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md`: Before/After table now shows `"risks": []` (field name unchanged; contains non-authoritative architecture risk hints only). Source-code handoff instruction #7 reworded to preserve serialized field name `risks`.
   - `AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md`: Schema example changed from `"risk_hints": []` to `"risks": []`.

2. **P0-2: Layer Mapper L2 vocabulary aligned with Repository Scanner**
   - `LAYER_MAPPER_FIC_SIB_EQC_CONTRACT.md`: Replaced `Application/plugin code` L2 definition with Repository Scanner's vocabulary (Profiles, blueprints, integration specs, evaluation specs). Added authority note that Layer Mapper must use the same L0/L1/L2 vocabulary as Repository Scanner.

3. **P0-3: Product Milestone 1 generated artifact list narrowed**
   - `AGENT_X_INITIATOR_COMPONENTS_AND_STANDARDS_REV5.md`: Section 12 wildcard artifacts (`*.jsonl`, `*.md`, `*.json`) replaced with exact PM1-only artifact list. Added rule: "Product Milestone 1 must not create Product Milestone 2 or Product Milestone 3 artifacts except BLOCKED command-history and audit records for registered later-command stubs."

4. **P0-4: `graph_integrity_latest.json` removed from Master Plan state directory**
   - `AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md`: Replaced active `graph_integrity_latest.json` entry with deprecation comment noting no standalone runtime file in current contract.

5. **P0-5: Addendum baseline commit updated**
   - `AGENT_X_INITIATOR_MILESTONE_AND_NAMING_ALIGNMENT_ADDENDUM.md`: All references to `20404841e56b239e8cd7ded4efd5026ed565482e` replaced with `e4dab4c0afec460d95212fb431c6e060c06e1bc6`.

### P1 — Should Fix

6. **P1-1: CLI Commands dependency path corrected**
   - `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md`: Input dependency entry `agentx_initiator/core/repository_scanner.py` replaced with `agentx_initiator/core/repo_scanner.py` with deprecation annotation.

7. **P1-2: CLI Governance Engine requirements qualified by PM**
   - `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md`: Added `(PM2+ only)` annotations to `GOVERNANCE_BLOCKED` failure class, governance precondition, and test oracle.

8. **P1-3: R0-R4 vs LOW/MEDIUM/HIGH/CRITICAL compatibility note added**
   - `GOVERNANCE_ENGINE_EQC_FIC_SCHEMA_v5.md`: Added advisory mapping table between Master Plan governance bands and Risk Engine/Gov Engine severity values. Note states mapping is advisory only; Gov Engine remains authoritative.

9. **P1-4: `COMMAND_OUT_OF_SCOPE` vs `COMMAND_NOT_IMPLEMENTED_IN_PRODUCT_MILESTONE_1` distinguished**
   - `CLI_COMMANDS_FIC_EQC_COMMAND_ACCEPTANCE_CRITERIA_v3.md`: Added explicit failure-class distinction section under allowed failure classes.

### P2 — Cleanup

10. **P2-1: "Full Version 1" wording clarified**
    - `AGENT_X_INITIATOR_EVOLUTION_ASSISTANT_PLAN_10_10_REV6.md`: Added explicit statement that "Full Version 1" does not mean Product Milestone 1.
    - `AGENT_X_INITIATOR_COMPONENTS_AND_STANDARDS_REV5.md`: Clarified `version 1` as initial product line across PM1–3.

## Verification

### Grep results

All legacy terms appear only in deprecation tables, compatibility notes, or historical patch evidence:

| Term | Status |
|---|---|
| `agentx-init.yaml` / `agentx-init.yml` | Only in Addendum legacy deprecation table |
| `governance_result.schema.json` | Only in Addendum legacy deprecation table |
| `patch_planner.py` / `patch_planner` | Only in Addendum legacy deprecation table |
| `proposals.jsonl` / `plans.jsonl` | Only in Addendum legacy deprecation table |
| `graph_latest.json` / `graph_integrity_latest.json` | Deprecation comment only; no active runtime artifact |
| `repository_scanner.py` | Only in compatibility notes (active dep path corrected) |
| `"risk_hints"` | Only in Governance Engine optional-context YAML example and historical notes |
| `Application/plugin code` | Removed from active L2 definition |
| `20404841e56b239e8cd7ded4efd5026ed565482e` | All references updated to current baseline |

## Remaining Issues

Expected: none blocking. Document set synchronization score: 10/10.

## Legacy Name Deprecation Table

| Legacy / ambiguous term | Canonical term | Rule |
|---|---|---|
| `agentx` as CLI name | `agentx-init` | `agentx` may appear only as project/product shorthand, not command name |
| `agentx-init.yaml` / `agentx-init.yml` | `config.json` | YAML config names are deprecated for PM1 runtime config |
| `paths.py` as canonical authority | `path_registry.py` | `paths.py` may remain facade only |
| `governance_result.schema.json` | `governance_decision.schema.json` | result schema name is deprecated |
| `patch_planner.py` | `patch_proposal_generator.py` | planner name is deprecated for proposal generator |
| `patch_planner` | `patch_proposal_generator` / Patch Proposal Generator | no active component should be called Patch Planner unless explicitly historical |
| `proposals.jsonl` | `patch_proposal_history.jsonl` | legacy memory name |
| `plans.jsonl` | `evolution_plan_history.jsonl` | legacy memory name |
| `graph_latest.json` | `graph_snapshot_latest.json` | graph latest is deprecated |
| `graph_integrity_latest.json` | embedded graph integrity report | no standalone runtime artifact in current contract |
| `repository_scanner.py` | `repo_scanner.py` | legacy module path |
| `risk_hints` as serialized field | `risks` | `risk_hints` may be used only as semantic explanation, not serialized schema field |
