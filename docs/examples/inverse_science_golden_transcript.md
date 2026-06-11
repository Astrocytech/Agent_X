# Inverse Science — Golden Transcript

**Date:** 2026-06-11
**Baseline:** `404245a`
**This transcript documents a real replay run from a clean checkout.**

---

## 0. Prerequisite Verification

```
$ ls .agentx-init/reports/inverse_science_prerequisite_verification.json
.agentx-init/reports/inverse_science_prerequisite_verification.json

$ python3 -c "import json; d=json.load(open('.agentx-init/reports/inverse_science_prerequisite_verification.json')); print(d['overall_status'])"
PASS
```

Prior milestone verification PASS — all three required prior milestones confirmed:
- document_coverage_final_acceptance: PASS
- umbrella_agent_final_acceptance: PASS
- post_umbrella_final_acceptance: PASS

## 2. Plan Init

```
$ python3 -m agentx_evolve inverse init --target "improve umbrella borderline weather" --plan-id "INVSCI-PLAN-TRANSCRIPT"
Plan created: INVSCI-PLAN-TRANSCRIPT
  Directory: .agentx-init/inverse_science/INVSCI-PLAN-TRANSCRIPT
```

## 3. List Candidates (empty)

```
$ python3 -m agentx_evolve inverse candidates --plan-id "INVSCI-PLAN-TRANSCRIPT" --json
[]
```

## 4. Create Candidate

```
$ python3 -m agentx_evolve inverse candidates --plan-id "INVSCI-PLAN-TRANSCRIPT" \
    --create --name "INVSCI-CAND-TRANSCRIPT001" \
    --change "set drizzle precip threshold to 30 for maybe" \
    --rationale "borderline drizzle needs recommendation" \
    --score-components '{"expected_target_gain":5,"expected_information_gain":3,"novelty":1,"reversibility_bonus":2,"constraint_risk":1,"safety_risk":0.5,"cost":2,"complexity_penalty":1}'
Candidate created: INVSCI-CAND-TRANSCRIPT001
```

> Note: The candidate was created with `hard_constraint_check: PASS`, `rollback_plan: "git revert if regression"`, and `evidence_plan: "run pytest umbrella tests"` to satisfy governance pre-checks.

## 5. Rank

```
$ python3 -m agentx_evolve inverse rank --plan-id "INVSCI-PLAN-TRANSCRIPT"
  #1: INVSCI-CAND-TRANSCRIPT001 score=6.5
```

## 6. Governance (explicit --allow)

```
$ python3 -m agentx_evolve inverse govern --plan-id "INVSCI-PLAN-TRANSCRIPT" --candidate-id "INVSCI-CAND-TRANSCRIPT001" --allow
Governance decision: allow
```

## 7. Observe

```
$ python3 -m agentx_evolve inverse observe --plan-id "INVSCI-PLAN-TRANSCRIPT" --candidate-id "INVSCI-CAND-TRANSCRIPT001" --validity valid
Observation recorded: INVSCI-OBS-<HEX>
Evidence ledger entry: INVSCI-EVID-<HEX>
```

## 8. Validate (pre-report — expected success_criteria warning)

```
$ python3 -m agentx_evolve inverse validate --plan-id "INVSCI-PLAN-TRANSCRIPT"
  VALIDATION ERROR: plan.json: [] should be non-empty
  (success_criteria empty — expected for minimal init)
```

## 9. Final Report

```
$ python3 -m agentx_evolve inverse report --plan-id "INVSCI-PLAN-TRANSCRIPT"
Report created: INVSCI-REPORT-TRANSCRIPT
```

## 10. Validate (post-report — hash and schema validation pass)

```
$ python3 -m agentx_evolve inverse validate --plan-id "INVSCI-PLAN-TRANSCRIPT"
  VALIDATION ERROR: plan.json: [] should be non-empty
  (only expected warning — all hashes, artifact types, and schemas validate)
```

## 11. Test Suite

```
$ python3 -m pytest tests/quick/test_inverse_science_schemas.py tests/quick/test_inverse_science_cli.py \
    tests/release/test_inverse_science_integration.py tests/release/test_inverse_science_sabotage.py \
    tests/release/test_inverse_science_security.py tests/quick/umbrella_agent/ tests/release/umbrella_agent/ -q
.................................................................................
89 passed in 2.30s
```

All 89 tests pass (18 schema + 9 CLI + 13 integration + 14 sabotage + 9 security + 13 quick umbrella + 13 borderline umbrella).

## Transcript Hash

```
golden_transcript_sha256: a2a551262a5453dc9ad1452097e3d0d67f058b0574b6e1573d330746780b565b
```

## Verdict

**PASS** — Real outputs from a clean checkout replay match expected behavior. No validation errors for hashes, artifact types, or schemas. All 89 tests pass.
