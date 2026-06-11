# Phase 7 — Security and Policy Regression Expansion

## Status: PASS

### Negative tests across all agents
1. L0/ mutation — protected by path boundary
2. Protected path write — blocked by seed tool policy
3. Path traversal — blocked by ToolGateway
4. Unrestricted shell command — not in allowed_tools
5. Unapproved network use — weather.fixture.read simulates only
6. Invalid model output — rejected by JSON parser
7. Patch without proposal — governed pipeline requires proposal
8. Patch without policy approval — policy gate enforces
9. Patch without risk classification — risk gate enforces
10. Promotion without review — promotion gate requires review artifact
11. Promotion without passing tests — test gate blocks promotion
12. Missing evidence manifest — manifest validator fails
13. Hash mismatch — source guard detects
14. Placeholder test target — noop detector flags
15. Manual insertion — provenance manifest tracks origin
16. Silent document weakening — diff validator required
17. Dependency change without approval — dep_change_validator
18. Credential leakage — secret scanner
19. Unapproved tool capability — policy registry
20. Live API when fixture required — provider gate
21. Event log modification — append-only validator
22. Approval referencing nonexistent evidence — integrity check
23. Promotion referencing nonexistent review — integrity check
24. Source changed without requirement link — traceability check
25. Benchmark runner with zero cases — noop detector

### Security boundaries
- All 3 agents have forbidden_tools in their profiles
- seed.emit_answer is the only allowed output tool
- Fixture tools are registered as seed tools (controlled)
- LLM runs at temperature=0.0 for deterministic behavior
