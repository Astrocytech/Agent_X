# Framework Seed Evaluation Spec

## Test 1: Target-Kind Validity

Input profile declares `target_kind: framework`.

Pass condition:
The profile validates without L0 framework-specific logic.

## Test 2: Multi-Framework Generality

The profile must describe at least two distinct framework families, for example:

- coding-agent framework
- evaluator framework

Pass condition:
Both are expressible without changing L0.

## Test 3: Contract Completeness

The candidate must define:

- module registry
- extension contract
- composition contract
- evaluator contract
- promotion contract
- package manifest
- rollback contract
- compatibility contract

Pass condition:
No required contract is missing.

## Test 4: Governance Preservation

The candidate must route promotion, tool use, mutation, export, and irreversible operations through governance.

Pass condition:
No direct bypass path exists.

## Test 5: Packaging Readiness

Candidate package must include:

- manifest
- profile
- contracts
- tests
- evaluation report
- evidence report
- rollback notes

Pass condition:
Package is complete and inspectable.

## Test 6: Regression Safety

Existing Agent_X tests must still pass.

Pass condition:
No existing L0/L1/L2 behavior regresses.

## Test 7: Anti-Bloat Check

Candidate must not add heavy framework machinery before there are tests requiring it.

Pass condition:
Every new file supports taxonomy, profile, evaluation, promotion, manifest, evidence, fixtures, tests, or documentation.

## Test 8: No Separate Seed Check

Candidate must not create a second root seed or separate Framework_X repo.

Pass condition:
Framework seed remains an Agent_X L2 target.

## Test 9: Backward Compatibility Check

Existing agent/controller/orchestrator targets must remain valid.

Pass condition:
Framework-only fields are not required for non-framework targets.
