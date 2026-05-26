# Framework Promotion Rules

## Promotion Statuses

```text
rejected
revise
experimental_framework_profile
exportable_framework_package
promoted_framework_package
```

## Promotion Requirements

A framework candidate cannot be promoted unless all are true:

1. Declares `target_kind: framework`.
2. Has a complete framework package manifest.
3. Has explicit module boundaries.
4. Has extension/plugin contracts.
5. Has composition/build rules.
6. Has an evaluation suite.
7. Has promotion rules.
8. Has packaging/export format.
9. Has rollback/migration notes.
10. Passes L0 invariants.
11. Does not require L0 runtime self-modification.
12. Does not bypass governance.
13. Has trace/evidence records.
14. Preserves old Agent_X agent-target behavior.
15. Has no required scoring dimension below 7/10.
16. Does not require a separate Framework_X seed repo.
17. Does not introduce model/provider/cloud lock-in into the core.

## Promotion Record

```yaml
candidate_id: string
target_kind: framework
status: rejected | revise | experimental_framework_profile | exportable_framework_package | promoted_framework_package
reason: string
evaluator: string
evaluation_report: string
evidence_refs:
  - string
rollback_ref: string
l0_invariant_check: pass | fail
regression_check: pass | fail
approved_by_user: true | false | not_required
```
