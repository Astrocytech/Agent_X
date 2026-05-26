# L2 Risk Ledger

## Risk Model

L2 profiles carry risk proportional to their specialization scope and integration
depth. At the spec level, risks are **anticipatory** — they describe what could go
wrong during implementation.

## Risk Register

| ID | Risk | Profile | Likelihood | Impact | Mitigation |
|----|------|---------|------------|--------|------------|
| R-L2-001 | Profile boundary creep — profile performs ungoverned actions | All | Medium | High | Enforce forbidden_actions; require L1 FIC for all implementation |
| R-L2-002 | Premature runtime — L2 profile implemented before L1 governance is ready | SR, Coding | Medium | Critical | Mark `implementation_allowed: false` by default |
| R-L2-003 | Integration bypass — external tool called without L1 governance | SR (PySR) | Low | Critical | L2 must not import external systems; L1 implements all integration code |
| R-L2-004 | L0 boundary violation — profile modifies L0 | Orchestration | Low | Critical | Architecture contract: L0 remains protected |
| R-L2-005 | Profile drift — profile YAML diverges from blueprint | All | Medium | Medium | ES registry + SIB bindings detect drift |
| R-L2-006 | Over-specification — too much detail in L2, not enough left for L1 | All | Low | Low | L2 spec should leave implementation decisions to L1 |
| R-L2-007 | Handoff ambiguity — L2 output cannot be converted to L1 FIC | All | Medium | High | Handoff rules define clear conversion path |

## Current Assessment

All profiles are draft. No implementation has begun. Risk ledger will be updated
when any profile moves to active status.
