# Framework Evolution Follow-up Proof Bundle v2

Reviewed commit: `e6685a06edea239cc451d078cdf2848086ac6978`
Follow-up commit: pending until committed
Purpose: fix collapsed formatting, validator integration, taxonomy ambiguity, L2 framework-profile validation, and proof quality.

Date/time: 2026-05-30T16:17:00Z
Environment: Linux, Python 3.12, pytest 9.0, no external ML/AI dependencies

---

## Collapsed files reformatted

The following files were reformatted to be readable multiline Python/YAML:

- `L1/validators/validate_target_taxonomy.py`
- `L1/validators/validate_framework_manifest.py`
- `L1/validators/validate_all.py`
- `L2/validators/validate_target_profiles.py`
- `L2/validators/bootstrap_validate_l2_scaffold.py`
- `tests/test_text_file_formatting.py`
- `L1/target_taxonomy.yaml`
- `L2/profiles/framework_seed.yaml`

## Taxonomy ambiguity removed

Top-level `framework:` rules section renamed to `framework_rules:`.

**Before (ambiguous):**
```yaml
target_kinds:
  framework:
    ...
framework:
  required_capabilities: ...
```

**After (unambiguous):**
```yaml
target_kinds:
  framework:
    ...
framework_rules:
  required_capabilities: ...
```

All validators and tests updated to read `framework_rules` instead of `framework`. The `target_kinds.framework` entry and `allowed_target_kinds` inclusion of `framework` are both separately validated.

## Formatting guard coverage

`tests/test_text_file_formatting.py` now explicitly covers:
- Python validator/test files with minimum line-count thresholds (>=25 lines each)
- YAML files with minimum line-count thresholds (>=40 for taxonomy, >=80 for framework_seed)
- The guard file itself (>=40 lines)
- Expanded YAML structure checks (target_kinds.framework expanded; framework_rules keys expanded)
- Collapse-pattern detection (multiple defs/classes per line, semicolon compression)

## Manifest validation integration

- Created `L1/framework_manifests/framework_seed_manifest.example.yaml` — preferred valid example manifest
- `L1/validators/validate_all.py` now discovers and validates all manifests in that directory
- If the directory is absent, `validate_all` reports an explicit WARNING
- Aggregate output now includes "FrameworkManifests" as a named validation step

## L2 profile validation

- Production profile validator (`L2/validators/validate_target_profiles.py`) distinguishes:
  - **Legacy profiles** without `target_kind` (explicit allowlist: coding_agent, symbolic_regression_controller, research_agent, repo_maintenance, orchestrator)
  - **New profiles** that must declare `target_kind`
  - **Framework profiles** validated against L1 taxonomy `framework_rules`
- Unknown `target_kind` rejected
- Forbidden capability scan covers: `required_capabilities`, `features`, `forbidden_actions`
- Top-level boolean forbidden keys scanned: `requires_l0_runtime_self_modification`, `requires_separate_framework_seed_repo`, `hidden_state_without_replay`, `unmediated_tool_execution`, `ungoverned_promotion`
- `framework_seed.yaml` explicitly declares `target_kind: framework`
- L2 scaffold validator calls production validator; does not duplicate validation logic

---

## Actual command output summaries

### `python -m compileall -q L0 L1 L2 tests`

**PASS** — no compile errors.

### `python -m L1.validators.validate_all`

```
7 validators: 6 PASS, 1 WARNING (pre-existing Lockfile), 0 FAIL
Validators: FIC, SIB, ES, EQC, Lockfile (WARNING), TargetTaxonomy, FrameworkManifests
```

### `python L2/validators/bootstrap_validate_l2_scaffold.py`

```
Errors: 0
Warnings: 0
=== bootstrap-validate-l2-scaffold: PASS ===
```

### `pytest tests/test_text_file_formatting.py -q`

```
7 passed in 0.37s
```

### `make prove-seed`

```
52 passed
=== prove-seed: OK ===
```

### `make prove-l1`

```
273 passed
7 validators: 6 PASS, 1 WARNING
=== prove-l1: OK ===
```

### `make prove-l2`

```
38 passed
=== prove-l2: OK ===
```

### `make prove-all`

```
L0: 52 passed
L1: 273 passed
L2: 38 passed
=== prove-all: OK ===
```

### Framework-specific test confirmation

```
pytest tests/test_text_file_formatting.py L1/tests/test_l1_framework_target.py L2/tests/test_l2_framework_target.py
54 passed
```

---

## Known limitations

- Framework Seed remains specification/profile-only. No runtime implementation exists.
- No runtime L0 self-modification was added.
- No separate Framework_X repository was created.
- Lockfile validator WARNING is pre-existing and unrelated.

---

## Final acceptance checklist

| Item | Status |
|------|--------|
| Collapsed Python files reformatted | ✅ |
| Collapsed YAML files reformatted | ✅ |
| `tests/test_text_file_formatting.py` readable and multiline | ✅ |
| Formatting guard would catch e6685a0 collapse failure | ✅ |
| Top-level taxonomy rules named `framework_rules` | ✅ |
| `target_kinds.framework` present and validated | ✅ |
| `allowed_target_kinds` includes `framework` and is validated | ✅ |
| L1 taxonomy validation is reusable production logic | ✅ |
| L1 framework manifest validation is reusable production logic | ✅ |
| L1 aggregate validation runs framework manifest validation | ✅ |
| Example manifest at `L1/framework_manifests/framework_seed_manifest.example.yaml` | ✅ |
| L2 profile validation distinguishes legacy/new/framework/unknown | ✅ |
| `framework_seed.yaml` declares `target_kind: framework` | ✅ |
| Framework forbidden capabilities rejected from all supported locations | ✅ |
| L2 scaffold validation calls production profile validation | ✅ |
| L1/L2 tests call production validators directly | ✅ |
| README says one Agent_X seed, no separate Framework_X repo | ✅ |
| L0 unchanged | ✅ |
| Proof bundle updated with actual commands and results | ✅ |
| Final proof commands pass | ✅ |

**bootstrap evidence** — not release evidence.
