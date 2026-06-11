# Evidence Artifacts Reference

## Root Directory: `.agentx-init/post_umbrella/`

| Phase | Directory | Key Artifacts |
|-------|-----------|---------------|
| 0 | `phase_0_prior_verification/` | prior_milestone_verification.json, blockers.json |
| 1 | `phase_1_baseline/` | source_manifest.json, test_manifest.json, evidence_manifest.json |
| 2 | `phase_2_infrastructure/` | infrastructure_report.md, infrastructure_results.json |
| 3 | `phase_3_example_agents/` | example_agents_report.json, example_agents_report.md |
| 4 | `phase_4_benchmarks/` | benchmark_cases.json, benchmark_results.json, benchmark_report.md |
| 5 | `phase_5_failure_recovery/` | failure_recovery_cases.json, failure_recovery_results.json |
| 6 | `phase_6_model_provider/` | provider_report.md |
| 7 | `phase_7_security_policy/` | security_report.md |
| 8 | `phase_8_release_readiness/` | INSTALL_AND_REPLAY.md, RELEASE_CLAIMS_AND_NON_CLAIMS.md |
| 9 | `phase_9_final_acceptance/` | acceptance_matrix.json, evidence_manifest.json, replay_report.md |

## Addenda
| Addendum | Directory | Key Artifacts |
|----------|-----------|---------------|
| A | `addendum_a/` | determinism_and_time_control.json |
| B | `addendum_b/` | safety_report.md, safety_results.json |
| C | `addendum_c/` | capability_matrix.json, negative_tests.json |
| D | `addendum_d/` | idempotency_report.md, idempotency_results.json |
| E | `addendum_e/` | coverage_matrix.json, uncovered_requirements.json |
| F | `addendum_f/` | appendix_refresh.md, appendix_refresh.json |
| G | `addendum_g/` | reconciliation_report.md, reconciliation_results.json |
| H | `addendum_h/` | RC_GATE.md, rc_gate.json |

## Root Artifacts
| Artifact | Description |
|----------|-------------|
| `post_umbrella_truth.json` | Central truth record for all phases |
| `post_umbrella_summary.md` | Human-readable summary |
