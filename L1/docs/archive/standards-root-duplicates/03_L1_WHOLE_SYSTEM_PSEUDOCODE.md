# L1 Whole-System Pseudocode

**Document ID:** `AX-L1-DOC-PS-001`  
**Version:** `v0.1.0`  
**Status:** `active`  
**Layer:** `L1`

```text
Procedure L1_EvolveOnce(goal):

1. Load L0 repository state.
2. Load L1 control documents.
3. Verify document authority and freshness.
4. Classify the requested goal.
5. Determine whether the goal affects L0, L1, L2, docs, tests, tooling, or generated artifacts.
6. If the goal is too broad, split it into bounded units.
7. Build or update the unit DAG.
8. Select one implementation unit.
9. Create or update the EQC-FIC document for the selected unit.
10. Validate the FIC against the pre-code gate.
11. If validation fails, return BLOCKED with reasons.
12. Freeze approved inputs in the semantic lockfile.
13. Build a bounded implementation handoff packet.
14. Allow implementation only inside declared permitted files.
15. Run declared checks and proof commands.
16. Collect evidence.
17. Produce completion record.
18. Produce review packet.
19. Update traceability matrix.
20. If implementation failed or drift occurred, update failure-learning log.
21. Return controlled status.
```

Allowed statuses:

```text
READY_FOR_IMPLEMENTATION
BLOCKED
NO_CHANGE
IMPLEMENTED_UNVALIDATED
VALIDATED
IMPLEMENTED_WITH_WAIVERS
REJECTED
```
