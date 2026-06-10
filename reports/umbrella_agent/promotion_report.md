# Promotion Report: Umbrella Agent v2

## Status: PROMOTE

The umbrella agent has been restructured from a standalone Python script into a genuine Agent_X-derived agent. All acceptance criteria pass.

## Architecture Changes
1. **KernelService runtime** — agent processes through all 8 phases
2. **LLM for explanation only** — recommendation stays deterministic per §3
3. **L0 ToolGateway integration** — weather.fixture.read registered as seed tool
4. **Agent_X profile** — umbrella-agent with temperature=0.0
5. **Concept file** — concepts/umbrella_agent_v2.md with exact reference code

## Precondition Checks
- [x] L0 seed tool weather.fixture.read registered and callable
- [x] Profile umbrella-agent registered in profiles/builtin/
- [x] All 13 unit tests pass (§3 deterministic rules)
- [x] All 7 integration tests pass (ToolGateway + KernelService)
- [x] All 4 system tests pass (end-to-end)
- [x] All 10 fixture cases produce correct recommendations
- [x] Stage A infrastructure proven
- [x] Concept file created with exact reference source code
- [x] Agent files match concept file
- [x] Source boundary respected (no L0 controller modifications)

## Validation Results
- Unit tests: 13/13 PASS
- Integration tests: 7/7 PASS
- System tests: 4/4 PASS
- Fixture cases: 10/10 PASS

## Evidence Reference
- Evidence manifest: reports/umbrella_agent/evidence_manifest.json
- Architecture proof: reports/umbrella_agent/agent_architecture_proof.json
- Fixture results: reports/umbrella_agent/fixture_case_results.json
- Final acceptance: reports/umbrella_agent/final_acceptance_report.md

## Decision
**PROMOTE** — The umbrella agent v2 is ready.
