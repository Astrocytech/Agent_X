"""SIB validator — checks SIB sidecars and schemas."""

from pathlib import Path

from L1.validators.common import (
    ValidationResult, check_dir, check_nonempty,
)

REQUIRED_SIB_FILES = [
    "L1/sib/sib-registry.yaml",
    "L1/sib/sib-bindings.yaml",
    "L1/sib/sib-graph.yaml",
    "L1/sib/sib-doc-registry.yaml",
    "L1/sib/sib-error-codes.yaml",
    "L1/sib/sib-waivers.yaml",
    "L1/sib/sib-source-freshness.yaml",
    "L1/sib/sib-version-impact.yaml",
    "L1/sib/sib-validation-log.md",
]

SIB_SCHEMAS_DIR = "L1/sib/sib-schemas/"
BASE = Path(__file__).resolve().parent.parent


def validate() -> ValidationResult:
    r = ValidationResult(name="SIB")

    for path in REQUIRED_SIB_FILES:
        err = check_nonempty(path)
        if err:
            r.errors.append(err)
            r.status = "BLOCKED"

    err = check_dir(SIB_SCHEMAS_DIR)
    if err:
        r.errors.append(err)
        r.status = "BLOCKED"
    else:
        schemas = list((BASE / "sib" / "sib-schemas").glob("*.json"))
        if not schemas:
            r.errors.append("SIB schemas directory contains no JSON schema files")
            r.status = "BLOCKED"

    return r
