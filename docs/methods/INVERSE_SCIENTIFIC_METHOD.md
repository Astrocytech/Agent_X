# Inverse Scientific Method — Optional Advisory Doctrine for Agent_X

> **Warning**: Inverse science is an optional planning and evidence discipline for selecting the next governed Agent_X evolution step. It does not replace policy, patch governance, review, promotion, testing, or replay.

## 1. Definition

The inverse scientific method is an optional planning discipline that inverts the traditional scientific method: instead of starting with a question and designing an experiment, it starts with a **desired output** and works backward through candidate actions, governance routing, observation, and evidence recording to select the next smallest governed evolution step.

In Agent_X terms, inverse science helps choose *what to try next* within the existing governed pipeline, without bypassing any policy, review, promotion, or testing gate.

## 2. Agent_X Terminology Mapping

| Source-method term | Agent_X term |
|---|---|
| Symbiant seed kernel | Agent_X L0/governed protected seed |
| external evolution agent | Agent_X governed LLM worker / evolution worker |
| seed-kernel invariants | L0, policy, patch, evidence, replay, review, promotion invariants |
| profile-level behavior | Agent_X profile / bounded generated-agent mode |
| repository evolution | governed Agent_X self-evolution |
| probe | governed candidate action / bounded patch / test/document/profile change |
| black box | current repository + tests + traces + runtime behavior |
| negative knowledge | structured record of rejected/failed candidates |
| best-known solution | best verified candidate state for a target |

## 3. Doctrine/Profile/Runtime Decision Gate

When using inverse science, the practitioner must decide which level applies:

| Level | When to use | Constraints |
|---|---|---|
| **Doctrine** | Planning which candidate to propose next | No runtime code changes; advisory only |
| **Profile** | Running the inverse-science planner as a bounded generated agent | Profile constrains allowed actions; no direct patch execution |
| **Runtime** | NOT ALLOWED for inverse science | Inverse science must never become mandatory core runtime |

If a proposed action would require runtime-level authority, it must be rejected and reframed at the doctrine or profile level.

## 4. Anti-Bloat Rule

No candidate may change more variables than necessary to test one specific claim. If a candidate changes three or more unrelated variables, it must be rejected or split into separate candidates.

## 5. Governance-Before-Action Rule

No candidate may execute any action — including patch application, file creation, or test execution — before passing through the existing Agent_X governance pipeline. Governance decisions must be recorded before any probe begins.

## 6. Evidence-Class Rule

Every claim made in a candidate or report must be classified into one of:

| Class | Meaning | Accepted for improvement claims? |
|---|---|---|
| `unsupported_claim` | No evidence provided | No |
| `inspection_evidence` | Manual review or static analysis | Partially |
| `test_evidence` | Deterministic test passes | Yes |
| `comparative_evidence` | Before/after comparison | Yes (with test evidence) |
| `replicated_evidence` | Independently replicated result | Yes |
| `negative_evidence` | Evidence that a claim is false | Yes |

No accepted improvement claim may rely on `unsupported_claim`. Runtime-path changes require test evidence and comparative evidence. Governance/tool changes require allowed-action and blocked-action evidence.

## 7. Negative-Knowledge Rule

All rejected or failed candidates must be recorded as structured negative knowledge. The failure must be classified into one of:

- `target_failure`
- `constraint_failure`
- `governance_failure`
- `evidence_failure`
- `measurement_failure`
- `model_failure`
- `complexity_failure`
- `reversibility_failure`
- `integration_failure`

Negative knowledge must affect future candidate ranking by adjusting risk/cost upward or expected gain downward for similar candidates. A candidate that repeats a previously failed approach without new information must be rejected.

## 8. Best-Known vs Proven-Optimum Distinction

The best-known solution is the best verified candidate state found so far. It may be classified as:

| Status | Meaning |
|---|---|
| `best_found_input` | Best input found during search |
| `local_optimum` | Best within a neighborhood |
| `global_optimum` | Proven best among all possibilities (requires strong proof) |
| `exact_inverse` | Exact solution to the inverse problem |
| `approximate_inverse` | Approximate solution |
| `feasible_solution` | Satisfies constraints but not proven optimal |
| `proven_impossibility` | No solution exists |
| `unresolved` | Not yet determined |

Claims of `global_optimum` require strong formal or empirical proof. No universal-agent, full-autonomy, or general-intelligence claim may be made from a single use case.

## 9. Stopping/Backtracking/Reframing Rules

- **Stopping**: A candidate may be stopped if new evidence makes it unlikely to succeed, if it violates a newly discovered constraint, or if the expected cost exceeds the expected value.
- **Backtracking**: If a probe fails or produces unexpected negative results, the planner may backtrack to the previous checkpoint and try a different candidate.
- **Reframing**: If all candidates fail, the planner must reframe the target — redefine the desired output, adjust constraints, or split the target into smaller sub-targets.

## 10. Adoption Status

Inverse science is **optional advisory doctrine** by default. It may be activated per planning session. It is not part of L0, not mandatory for any Agent_X workflow, and does not replace any existing governance, review, promotion, or testing process.

## 11. Source-Method Adaptation Note

```json
{
  "source_method_name": "INVERSE SCIENCE METHOD",
  "source_method_version": "2.0",
  "adapted_for": "Agent_X",
  "integration_level": "doctrine_contract_profile_workflow_not_mandatory_runtime",
  "symbiant_terms_translated": true,
  "runtime_adoption": false
}
```

## 12. References

- [Agent_X Layer Architecture](../01_architecture/LAYER_ARCHITECTURE.md)
- [Agent_X Governance Rules](../../docs/02_governance/GOVERNANCE_RULES.md)
- [Umbrella Agent Example](../../examples/umbrella_agent/)
