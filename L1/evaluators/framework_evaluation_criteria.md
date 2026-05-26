# Framework Evaluation Criteria

Each dimension is scored 0-10.
A framework candidate is not promotable if any required dimension is below 7/10.
A framework candidate is not promotable if evidence, rollback, governance, compatibility, or regression checks are missing.

## Dimensions

1. **Generality** — Can the framework support multiple framework families (e.g., coding-agent framework, evaluator framework) without changes to the kernel?
2. **Modularity** — Are module boundaries, extension contracts, and composition rules cleanly defined?
3. **Governability** — Does the candidate route promotion, tool use, mutation, export, and irreversible operations through governance?
4. **Evaluability** — Can the candidate be tested, scored, and compared deterministically?
5. **Replayability** — Can any framework operation be replayed from traces for audit or debugging?
6. **Extensibility** — Can new extensions, modules, or adapters be added without modifying core contracts?
7. **Packaging/export** — Can a candidate framework be packaged with manifest, tests, evidence, and rollback notes?
8. **Agent_X compatibility** — Does the candidate remain compatible with L0 governance, L1 evolution, and existing L2 profiles?
9. **Minimality** — Does the candidate avoid heavy runtime machinery before tests prove the need?
10. **Practical evolvability** — Can the candidate evolve into specialized frameworks through L1 + L2 without rewriting?

## Output Format

```yaml
candidate_id: string
target_kind: framework
overall_score: number
required_dimension_minimum: 7
scores:
  generality: number
  modularity: number
  governability: number
  evaluability: number
  replayability: number
  extensibility: number
  packaging_export: number
  agent_x_compatibility: number
  minimality: number
  practical_evolvability: number
promotion_recommendation: reject | revise | promote_experimental | promote_exportable
blocking_issues:
  - string
evidence_refs:
  - string
rollback_ref: string
```

## Rejection Conditions

A candidate is automatically rejected if any of these are true:

1. Missing required common fields (id, name, version, target_kind, purpose, constraints, evaluation)
2. Invalid target_kind (not in the canonical taxonomy)
3. Missing framework-specific fields (non_goals, required_capabilities, required_interfaces, promotion, packaging, rollback, compatibility)
4. Missing required framework capabilities (module_registry, extension_contracts, composition_rules, evaluation_suite, promotion_rules, artifact_packaging, rollback_migration, compatibility_surface, evidence_traceability)
5. Contains forbidden capabilities (l0_runtime_self_modification, governance_bypass, etc.)
6. Requires L0 runtime self-modification
7. Requires a separate Framework_X root seed repo
8. Any required dimension score below 7/10
