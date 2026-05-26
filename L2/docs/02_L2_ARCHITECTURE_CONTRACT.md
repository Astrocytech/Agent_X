# L2 Architecture Contract

## Layer Identity

L2 is a **profile/specification governance layer**. It is not an implementation layer,
not a runtime layer, and not an autonomy layer.

## Binding Rules

1. **L2 proposes, L1 governs, L0 protects.**
   - L2 may define profiles, blueprints, and specs.
   - L1 must issue a FIC before any L2 proposal becomes implemented code.
   - L0 may not be modified by L2 proposals without an L0 FIC.

2. **No runtime code in L2.**
   - L2/controller/, L2/runtime/, L2/agents/, L2/tools/ must not exist.
   - Python entry points, async loops, tool wrappers, model routing, and memory
     management belong in L1 governed units.

3. **No autonomous execution.**
   - L2 profiles may describe *what* an agent should do.
   - L2 must not execute tools, call APIs, or modify filesystem state.

4. **No direct layer bypass.**
   - L2 may not patch L0 or L1 directly.
   - L2 must route all implementation proposals through L1 FICs.

## Contract

```
I, L2, agree:
- To remain a specification-only layer until L1 creates a FIC-governed task.
- To register all profiles in the L2 ecosystem registry.
- To bind each profile to its future L1 implementation targets via SIB.
- To mark implementation_allowed: false until L1 handoff is complete.
- To never execute, patch, or autonomously modify the system.
```
