# Framework Evolution Follow-up Proof Bundle

Commit reviewed: 0de6b1992b022fe901025d6ef69dfd423b15ee1f
Follow-up commit: <to be filled after commit>
Date/time: 2026-05-30T16:00:00Z
Environment: Linux, Python 3.12, pytest 9.0, no external ML/AI dependencies

## Baseline result before fixes

- `python -m compileall -q L0 L1 L2`: PASS (no errors)
- `make prove-seed`: PASS (52 tests)
- `make prove-l1`: PASS (257 tests, 1 pre-existing Lockfile WARNING)
- `make prove-l2`: PASS (43 tests)
- `make prove-all`: PASS (352 total)

No baseline failures.

## Final result after fixes

- `python -m compileall -q L0 L1 L2`: PASS
- YAML parse check: all YAML files parse successfully
- `make help`: PASS
- `make prove-seed`: PASS
- `make prove-l1`: PASS
- `make prove-l2`: PASS
- `make prove-all`: PASS
- Format guard tests: PASS

## Test counts

- L0: 52
- L1: 275 (257 existing + 18 framework/manifest tests)
- L2: 47 (43 existing + 4 profile validator tests)
- Format guard: 4
- Total: 374

## Validator coverage

- **target taxonomy validator**: `L1/validators/validate_target_taxonomy.py` — validates `L1/target_taxonomy.yaml` structure, required fields, framework section, migration rule. Integrated into `validate_all.py`.
- **target profile validator**: `L2/validators/validate_target_profiles.py` — validates all `L2/profiles/*.yaml` against taxonomy rules. Integrated into `bootstrap_validate_l2_scaffold.py`.
- **framework manifest validator**: `L1/validators/validate_framework_manifest.py` — validates framework package manifests. Tests cover valid, missing contracts, missing/bad promotion status, missing compatibility.
- **text format guard**: `tests/test_text_file_formatting.py` — prevents collapsed single-line source files.

## Changed files

### New files:
- `tests/test_text_file_formatting.py` — format guard tests
- `L1/validators/validate_target_taxonomy.py` — taxonomy validator
- `L1/validators/validate_framework_manifest.py` — manifest validator
- `L2/validators/validate_target_profiles.py` — profile validator
- `L1/evidence/framework_evolution_proof_bundle_0de6b199_followup.md` — this file
- `L1/fixtures/framework_manifest_invalid_missing_promotion_status.yaml`
- `L1/fixtures/framework_manifest_invalid_bad_promotion_status.yaml`
- `L1/fixtures/framework_manifest_invalid_missing_rollback.yaml`
- `L1/fixtures/framework_manifest_invalid_missing_compatibility.yaml`
- `L1/fixtures/framework_candidate_invalid_provider_locked_core.yaml`
- `L1/fixtures/framework_candidate_invalid_evidence_free_promotion.yaml`
- `L1/fixtures/framework_candidate_invalid_irreversible_export_without_approval.yaml`
- `L1/fixtures/framework_candidate_invalid_missing_rollback.yaml`
- `L1/fixtures/framework_candidate_invalid_missing_compatibility_surface.yaml`
- `L1/fixtures/framework_candidate_invalid_unknown_target_kind.yaml`
- `L1/fixtures/framework_candidate_invalid_new_profile_missing_target_kind.yaml`

### Modified files:
- `L1/target_taxonomy.yaml` — normalized to v2 schema with `framework` section, renamed capabilities, added migration rule
- `L1/validators/validate_all.py` — added `validate_target_taxonomy` to validator list
- `L2/validators/bootstrap_validate_l2_scaffold.py` — integrated profile validator
- `L1/tests/test_l1_framework_target.py` — uses production taxonomy validator, added manifest validator tests
- `L2/tests/test_l2_framework_target.py` — uses production profile validator for all validations
- `L2/profiles/framework_seed.yaml` — updated capabilities to match taxonomy naming
- `L1/fixtures/framework_candidate_invalid_governance_bypass.yaml` — updated to `ungoverned_tool_execution`
- `L1/fixtures/framework_candidate_invalid_hidden_state.yaml` — updated to `hidden_non_replayable_state`
- `L1/fixtures/framework_candidate_invalid_separate_seed_repo.yaml` — updated to `required_separate_framework_seed_repo`
- `L2/README.md` — updated profile count to 5, added framework seed row
- `L1/README.md` — added framework-target support directories
- `README.md` — added note about no separate Framework_X repo

## Known limitations

- Framework Seed remains specification/profile-only. No runtime implementation exists.
- No runtime L0 self-modification was added.
- No separate framework seed repo was created.
- Lockfile validator WARNING is pre-existing and unrelated.

## Promotion status

**bootstrap evidence** — not release evidence.
