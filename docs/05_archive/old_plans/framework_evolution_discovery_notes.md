# Framework Evolution Discovery Notes

## Existing Structure

- L0 files: `L0/CODE/` (kernel), `L0/manifests/` (CAPABILITY_MANIFEST.yaml, SEED_INVARIANTS.yaml, SEED_PACKAGE_MANIFEST.yaml), `L0/tests/seed_l0/`, `L0/scripts/proofs/`, `L0/docs/`
- L1 files: `L1/controller/` (14 modules), `L1/validators/` (validate_all, validate_fic, validate_sib, validate_es, validate_eqc, validate_lockfile, common), `L1/tests/` (18 test files), `L1/fic/` (index + 14 FIC units), `L1/standards/`, `L1/sib/`, `L1/ecosystem/`, `L1/eqc/`, `L1/evidence/`, `L1/generated/`, `L1/docs/`, `L1/patch_planner/`, `L1/proof_runner/`, `L1/prompts/`, `L1/workflows/`
- L2/profile files: `L2/profiles/` (coding_agent.yaml, orchestrator.yaml, research_agent.yaml, repo_maintenance_agent.yaml, symbolic_regression_controller.yaml), `L2/blueprints/`, `L2/evaluation_specs/`, `L2/docs/`
- Schema files: `L1/sib/sib-schemas/` (JSON schemas), `L1/ecosystem/ecosystem-schemas/`, `L1/eqc/schemas/`, `L2/fic/` (JSON schemas), `L2/ecosystem/ecosystem-schemas/`, `L2/eqc/schemas/`
- Test/proof files: `L0/tests/seed_l0/` (14 tests), `L1/tests/` (18 tests), `L2/tests/` (5 tests), `L0/scripts/proofs/` (7 proof scripts)
- Documentation entrypoints: `README.md`, `L0/README.md`, `L1/README.md`, `L2/README.md`
- Evidence/trace/promotion files: `L0/.local/runtime/traces/`, `L1/evidence/`, `L1/generated/`

## Existing Target Handling

- **No existing `target_kind` field** in any profile or manifest.
- Profiles use `specialization_type` (values: `coding`, `research`, `symbolic-regression`, `repo-maintenance`, `orchestration`) instead of `target_kind`.
- L0 has no hardcoded agent-only assumptions. The term "agent" appears only in natural-language descriptions (e.g., "universal agent seed").
- Controller and orchestrator are represented as profiles with `specialization_type: "orchestration"`, not as separate target kinds.
- Schemas are scattered across L1/sib/schemas/, L1/ecosystem/schemas/, L2/fic/, L2/ecosystem/schemas/, L2/eqc/schemas/ — no centralized schema location.

## Path Mapping

| Proposed path in TODO | Actual repo path used | Reason |
|---|---|---|
| `L1/target_taxonomy.yaml` | `L1/target_taxonomy.yaml` | Repo already uses `L1/` for governance |
| `L1/evaluators/framework_evaluation_criteria.md` | `L1/evaluators/framework_evaluation_criteria.md` | New `evaluators/` subdirectory under L1 |
| `L1/templates/framework_candidate_comparison.md` | `L1/templates/framework_candidate_comparison.md` | New `templates/` subdirectory under L1 |
| `L1/promotion/framework_promotion_rules.md` | `L1/promotion/framework_promotion_rules.md` | New `promotion/` subdirectory under L1 |
| `L1/schemas/framework_package_manifest.schema.yaml` | `L1/schemas/framework_package_manifest.schema.yaml` | New `schemas/` subdirectory under L1 |
| `L1/fixtures/framework_manifest_valid.yaml` | `L1/fixtures/framework_manifest_valid.yaml` | New `fixtures/` subdirectory under L1 |
| `L1/fixtures/framework_manifest_invalid_missing_contracts.yaml` | `L1/fixtures/framework_manifest_invalid_missing_contracts.yaml` | Same |
| `L1/fixtures/framework_candidate_invalid_governance_bypass.yaml` | `L1/fixtures/framework_candidate_invalid_governance_bypass.yaml` | Same |
| `L1/fixtures/framework_candidate_invalid_l0_self_modification.yaml` | `L1/fixtures/framework_candidate_invalid_l0_self_modification.yaml` | Same |
| `L1/fixtures/framework_candidate_invalid_hidden_state.yaml` | `L1/fixtures/framework_candidate_invalid_hidden_state.yaml` | Same |
| `L1/fixtures/framework_candidate_invalid_separate_seed_repo.yaml` | `L1/fixtures/framework_candidate_invalid_separate_seed_repo.yaml` | Same |
| `L1/fixtures/agent_target_valid_minimal.yaml` | `L1/fixtures/agent_target_valid_minimal.yaml` | Backward-compat fixture |
| `L1/fixtures/controller_target_valid_minimal.yaml` | `L1/fixtures/controller_target_valid_minimal.yaml` | Backward-compat fixture |
| `L1/fixtures/orchestrator_target_valid_minimal.yaml` | `L1/fixtures/orchestrator_target_valid_minimal.yaml` | Backward-compat fixture |
| `L2/profiles/framework_seed.yaml` | `L2/profiles/framework_seed.yaml` | Repo already uses `L2/profiles/` |
| `L2/blueprints/framework_seed_blueprint.md` | `L2/blueprints/framework_seed_blueprint.md` | Repo already uses `L2/blueprints/` |
| `L2/evaluations/framework_seed_eval_spec.md` | `L2/evaluation_specs/framework_seed_eval_spec.md` | Repo uses `L2/evaluation_specs/` not `L2/evaluations/` |

## Risk Notes

- L0 risks: None identified. L0 is target-kind neutral and has no framework-specific behavior.
- L1 risks: Adding `target_kind` to taxonomy is new and must not break existing FIC, SIB, ES, EQC validators. New directories (evaluators/, templates/, promotion/, schemas/, fixtures/) are additive and will not break existing structure tests.
- L2 risks: Adding `framework_seed.yaml` to profiles is additive. Must update `bootstrap_validate_l2_scaffold.py` to include it. Existing profiles without `target_kind` must remain valid via migration rule.
- Test risks: Existing tests must not break. New tests must not require runtime self-modification, model providers, or heavy dependencies.

## Migration Rule

If an existing profile has no `target_kind` and is clearly an agent profile (based on `specialization_type` or content), treat it as `target_kind: agent` for backward compatibility. New profiles must declare `target_kind` explicitly.
