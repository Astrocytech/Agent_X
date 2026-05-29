"""Semantic lockfile validator — checks lockfile state and release readiness."""

from L1.validators.common import (
    ValidationResult, check_file, load_yaml,
)

LOCKFILE_PATH = "L1/generated/semantic_lockfile.yaml"
PLACEHOLDER_STATUS = "placeholder-not-release-evidence"

RELEASE_REQUIRED_FIELDS = [
    "generated_from", "created_at_utc", "base_commit",
    "selected_unit_id", "control_documents", "fic_units",
]


def validate() -> ValidationResult:
    r = ValidationResult(name="Lockfile")

    err = check_file(LOCKFILE_PATH)
    if err:
        r.errors.append(err)
        r.status = "BLOCKED"
        return r

    lock = load_yaml(LOCKFILE_PATH)
    if lock is None:
        r.errors.append("Semantic lockfile could not be parsed")
        r.status = "FAIL"
        return r

    status = lock.get("status", "")
    release_evidence = lock.get("release_evidence", True)

    if PLACEHOLDER_STATUS in str(status):
        r.warnings.append("Semantic lockfile status is placeholder — not release evidence")
        if r.status == "PASS":
            r.status = "WARNING"

    if release_evidence is False:
        r.warnings.append("release_evidence is false — validator must not report release-ready")
        if r.status == "PASS":
            r.status = "WARNING"

    if release_evidence is True:
        for field in RELEASE_REQUIRED_FIELDS:
            val = lock.get(field)
            if not val:
                r.errors.append(f"Lockfile missing release-required field: {field}")
                r.status = "BLOCKED"

        if not lock.get("control_documents"):
            r.errors.append("Lockfile control_documents is empty — required for release")
            r.status = "BLOCKED"

        if not lock.get("fic_units"):
            r.errors.append("Lockfile fic_units is empty — required for release")
            r.status = "BLOCKED"

    return r
