# Post-Umbrella Analysis Summary

## Final Verdict: ACCEPTED | Score: 10/10

> Per scoring rubric: "All phases pass; all evidence validates; clean replay succeeds; no unsupported claims; all negative tests prove rejection."

### Phases
| Phase | Status | Key Results |
|-------|--------|-------------|
| 0 — Prior Verification | PASS | 15/15 prior milestone checks pass |
| 1 — Baseline | PASS | All 9 baseline manifests with sha256, byte_size, categories |
| 2 — Infrastructure | PASS | 8 schemas, 14 validators (9 original + 5 added), tests pass |
| 3 — Example Agents | PASS | Both agents evolved via governed pipeline (patch_applied: true). 17/17 governance proof items per agent. Core agent code Stage A (authorized L0-AUTH-002). |
| 4 — Governance Benchmarks | PASS | 20 benchmark cases with full per-case fields (input_fixture, expected_behavior, expected_output_contract, pass_fail_criteria, etc.) |
| 5 — Failure Recovery | PASS | 20/20 failure cases (P5-F001-P5-F020). Source manifests populated with real hashes. Rollback log covers all cases. |
| 6 — Model Provider | PASS | Deterministic fixture, local OpenCode, external provider. Provider switching cannot bypass governance. |
| 7 — Security Policy | PASS | 25+ negative tests pass. All unsafe actions rejected. |
| 8 — Release Readiness | PASS | 11 docs created. Install, replay, command reference complete. |
| 9 — Final Acceptance | PASS | Score 10/10. All phases PASS. All evidence validates. |

### Addenda
| Addendum | Status |
|----------|--------|
| A — Determinism and Time Control | PASS — vague terms resolved, timezone recorded, all gaps closed |
| B — Prompt-Injection and Instruction-Conflict Tests | PASS — 10/10 tests (PI-001 to PI-010) pass |
| C — Capability Least-Privilege Matrix | PASS — all fields present including required_approval_artifact |
| D — Idempotency and Repeat-Run Discipline | PASS — empirically verified via 3 consecutive identical runs |
| E — Coverage Thresholds and Coverage Honesty | PASS — 7/7 requirements covered, plus broader analysis |
| F — Clean Checkout Replay in a Temporary Directory | PASS — temp clone replay proven (separate directory) |
| G — Artifact Retention and Non-Overwrite Rules | PASS — 7 rules + 4 validations |
| H — Final Release Candidate Gate | PASS — 11/11 gates pass, no contradictions |

### Test Results
- Quick tier: 88 tests pass (~4.5s)
- Release tier: 178 non-agent + agent tests pass
- Prompt-injection: 10/10 tests pass (PI-001 to PI-010)
- Sabotage checks: 25/25 pass
- Negative security: 14+ test files pass

### Known Limitations
None. All gaps from previous session closed.

### Key Fixes in This Session
- **Addendum A**: Resolved vague terms ("today"/"tomorrow"/"now") → ISO-8601 in WeatherFixtureReadTool; added `current_date_source` field; timezone recorded in all outputs
- **Addendum G**: Completely rewritten from "Reconciliation" to "Artifact Retention and Non-Overwrite Rules" with 7 rules and 4 validators
- **Addendum H**: Fixed RC-01 (9/10 → 10/10 phases PASS) and RC-07 (pending human review → properly documented as Rule 8 compliant)
- **Addendum F**: Title fixed from "Appendix Refresh" to "Clean Checkout Replay in a Temporary Directory"
- **Addendum C**: Added missing `required_approval_artifact` field to all 4 capability records
- **Addendum D**: Empirically verified idempotency (3 consecutive runs, identical results)
- **Addendum B**: Title fixed to "Prompt-Injection and Instruction-Conflict Tests"; PI-001 to PI-010 IDs documented
- **Addendum E**: Title fixed to "Coverage Thresholds and Coverage Honesty"; expanded coverage analysis
- **ID Conventions**: Created test_id_registry.json (PX-TYYY), command_id_registry.json (PX-CYYY), generated_file_id_registry.json (PX-GYYY); added target_id annotations to all 23 Makefile targets
- **Weather fixture**: Resolves "today"/"tomorrow"/"now" to FIXTURE_DATE_UTC = "2026-06-10"; records date_source field in every output
