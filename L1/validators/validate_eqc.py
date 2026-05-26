"""EQC validator — checks EQC manifest, procedures, operators, schemas."""

from pathlib import Path

from L1.validators.common import (
    ValidationResult, check_file, check_dir, check_nonempty, load_yaml,
)

REQUIRED_EQC_FILES = [
    "L1/eqc/manifests/l1-eqc-manifest.yaml",
    "L1/eqc/procedures/L1_EvolveOnce.eqc.md",
    "L1/eqc/procedures/L1_ValidateFICBundle.eqc.md",
    "L1/eqc/operators/classify_goal.eqc.md",
    "L1/eqc/operators/decide_readiness.eqc.md",
    "L1/eqc/traces/l1-validation-trace.schema.yaml",
    "L1/eqc/tests/goal-classifier.test-vectors.yaml",
]

EQC_SCHEMAS_DIR = "L1/eqc/schemas/"
EQC_PROCEDURES_DIR = "L1/eqc/procedures/"
EQC_OPERATORS_DIR = "L1/eqc/operators/"
EQC_TRACES_DIR = "L1/eqc/traces/"
EQC_TESTS_DIR = "L1/eqc/tests/"
BASE = Path(__file__).resolve().parent.parent


def validate() -> ValidationResult:
    r = ValidationResult(name="EQC")

    for path in REQUIRED_EQC_FILES:
        err = check_nonempty(path)
        if err:
            r.errors.append(err)
            r.status = "BLOCKED"

    for d in [EQC_PROCEDURES_DIR, EQC_OPERATORS_DIR, EQC_TRACES_DIR, EQC_TESTS_DIR, EQC_SCHEMAS_DIR]:
        err = check_dir(d)
        if err:
            r.errors.append(f"EQC: {err}")
            r.status = "BLOCKED"

    schemas = list((BASE / "eqc" / "schemas").glob("*.json"))
    if not schemas:
        r.errors.append("EQC schemas directory contains no JSON schema files")
        r.status = "BLOCKED"

    manifest = load_yaml("L1/eqc/manifests/l1-eqc-manifest.yaml")
    if manifest:
        l1 = manifest.get("l1_eqc_manifest", {})
        for proc in l1.get("procedures", []):
            proc_path = proc.get("path", "")
            if proc_path:
                err = check_file(proc_path)
                if err:
                    r.errors.append(f"EQC procedure {proc.get('procedure_id', '?')}: {err}")
                    r.status = "BLOCKED"
        for op in l1.get("operators", []):
            op_path = op.get("path", "")
            if op_path:
                err = check_file(op_path)
                if err:
                    r.errors.append(f"EQC operator {op.get('name', '?')}: {err}")
                    r.status = "BLOCKED"

    return r
