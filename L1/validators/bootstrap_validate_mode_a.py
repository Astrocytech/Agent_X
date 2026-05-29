#!/usr/bin/env python3
"""Mode A Bootstrap Validator — validates L1 scaffold after Mode A creation."""

from pathlib import Path
import sys

errors = []

def check_exists(path: str, description: str):
    p = Path(path)
    if not p.exists():
        errors.append(f"MISSING: {description} ({path})")
    elif p.stat().st_size == 0 and not path.endswith('.gitkeep'):
        errors.append(f"EMPTY: {description} ({path})")

def check_contains(path: str, text: str, description: str):
    p = Path(path)
    if not p.exists():
        errors.append(f"MISSING: {description} ({path})")
    elif text not in p.read_text():
        errors.append(f"MISSING_MARKER: {description} - expected '{text}' in {path}")

def check_multiline(path: str, min_lines: int, description: str):
    p = Path(path)
    if p.exists() and len(p.read_text(encoding="utf-8").splitlines()) < min_lines:
        errors.append(f"TOO_FLAT_FOR_REVIEW: {description} ({path}) must be >= {min_lines} lines")

# 1. Check required standards (canonical versioned paths)
standards = [
    "L1/standards/AGENT_X_L1_EQC_FIC_v0_6.md",
    "L1/standards/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md",
    "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md",
    "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md",
    "L1/standards/AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md",
]
for s in standards:
    check_exists(s, f"standard {s}")

# 1b. Forbid root-level duplicate standards
forbidden_duplicate_roots = [
    "L1/AGENT_X_L1_EQC_FIC_v0_6.md",
    "L1/AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md",
    "L1/AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md",
    "L1/AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md",
    "L1/AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md",
]
for p in forbidden_duplicate_roots:
    if Path(p).exists():
        errors.append(f"DUPLICATE_STANDARD_SOURCE: non-canonical root duplicate exists ({p})")

# 2. Check required L1 docs
docs = [
    "L1/docs/00_L1_SYSTEM_GOAL.md",
    "L1/docs/01_L1_BACKGROUND.md",
    "L1/docs/02_L1_ARCHITECTURE_CONTRACT.md",
    "L1/docs/03_L1_WHOLE_SYSTEM_PSEUDOCODE.md",
    "L1/docs/04_L1_UNIT_DAG.md",
    "L1/docs/05_L1_SHARED_TYPES_AND_INTERFACES.md",
    "L1/docs/06_L1_VALIDATION_PLAN.md",
    "L1/docs/07_L1_RISK_LEDGER.md",
    "L1/docs/08_L1_TRACEABILITY_MATRIX.md",
    "L1/docs/09_L1_CODING_AGENT_HANDOFF_RULES.md",
    "L1/docs/10_L1_FAILURE_LEARNING_LOG.md",
    "L1/docs/11_L1_REVIEW_GATE.md",
]
for d in docs:
    check_exists(d, f"L1 doc {d}")

# 3. Check FIC registry
check_exists("L1/fic/index.fic.yaml", "FIC index")

# 4. Check FIC-L1-001 exists and contains heading
check_contains("L1/fic/units/FIC-L1-001-document-loader.md",
               "FIC-L1-001: L1 Document Loader",
               "FIC-L1-001 heading")

# 5. Check ES sidecars
es_files = [
    "L1/ecosystem/ecosystem-registry.yaml",
    "L1/ecosystem/ecosystem-graph.yaml",
    "L1/ecosystem/ecosystem-validation-log.md",
    "L1/ecosystem/ecosystem-error-codes.yaml",
]
for f in es_files:
    check_exists(f, f"ES sidecar {f}")

# 6. Check SIB sidecars
sib_files = [
    "L1/sib/sib-registry.yaml",
    "L1/sib/sib-doc-registry.yaml",
    "L1/sib/sib-bindings.yaml",
    "L1/sib/sib-graph.yaml",
    "L1/sib/sib-validation-log.md",
    "L1/sib/sib-error-codes.yaml",
    "L1/sib/sib-waivers.yaml",
]
for f in sib_files:
    check_exists(f, f"SIB sidecar {f}")

# 7. Check EQC sidecars
eqc_files = [
    "L1/eqc/manifests/l1-eqc-manifest.yaml",
    "L1/eqc/procedures/L1_EvolveOnce.eqc.md",
    "L1/eqc/procedures/L1_ValidateFICBundle.eqc.md",
    "L1/eqc/operators/classify_goal.eqc.md",
    "L1/eqc/operators/decide_readiness.eqc.md",
]
for f in eqc_files:
    check_exists(f, f"EQC sidecar {f}")

# 8. Check generated placeholders contain not-release-evidence marker
generated = [
    "L1/generated/fic_bundle_manifest.yaml",
    "L1/generated/unit_dag.yaml",
    "L1/generated/semantic_lockfile.yaml",
    "L1/generated/requirement_coverage_matrix.yaml",
    "L1/generated/readiness_report.md",
    "L1/generated/validation_report.md",
    "L1/generated/review_packet.md",
    "L1/generated/release_candidate_report.md",
]
for g in generated:
    check_contains(g, "placeholder-not-release-evidence", f"generated placeholder {g}")

# 9. Check bootstrap artifact manifest exists
check_contains("L1/generated/bootstrap_artifact_manifest.yaml",
               "mode-a-bootstrap-not-release-evidence",
               "bootstrap artifact manifest")

# 10. Multiline formatting sanity check
multiline_required = [
    "L1/sib/sib-registry.yaml",
    "L1/sib/sib-bindings.yaml",
    "L1/sib/sib-doc-registry.yaml",
    "L1/sib/sib-graph.yaml",
    "L1/ecosystem/ecosystem-registry.yaml",
    "L1/ecosystem/ecosystem-graph.yaml",
    "L1/generated/semantic_lockfile.yaml",
]
for path in multiline_required:
    check_multiline(path, 3, f"multiline YAML {path}")

# Summary
if errors:
    print("MODE A BOOTSTRAP VALIDATOR: FAIL")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("MODE A BOOTSTRAP VALIDATOR: PASS")
    print("All required Mode A artifacts verified.")
    sys.exit(0)
