"""FIC validator — checks FIC registry and unit contracts."""

from L1.validators.common import (
    ValidationResult, check_file, check_dir, check_nonempty, load_yaml,
)

VALID_LIFECYCLE_STATUSES = {
    "draft", "ready-for-code", "ready-for-review", "validated",
    "bootstrap-placeholder-not-release-evidence",
}

FIC_INDEX_PATH = "L1/fic/index.fic.yaml"
FIC_UNITS_DIR = "L1/fic/units/"


def validate() -> ValidationResult:
    r = ValidationResult(name="FIC")

    err = check_file(FIC_INDEX_PATH)
    if err:
        r.errors.append(err)
        r.status = "BLOCKED"
        return r

    err = check_dir(FIC_UNITS_DIR)
    if err:
        r.errors.append(err)
        r.status = "BLOCKED"
        return r

    registry = load_yaml(FIC_INDEX_PATH)
    if registry is None:
        r.errors.append("FIC registry could not be parsed")
        r.status = "BLOCKED"
        return r

    files = registry.get("files", [])
    if not files:
        r.errors.append("FIC registry contains no files entries")
        r.status = "BLOCKED"
        return r

    fic_l1_001_found = False
    seen_ids = set()

    for entry in files:
        fic_id = entry.get("fic_id", "")
        if not fic_id:
            r.errors.append("FIC entry missing fic_id")
            r.status = "BLOCKED"
            continue

        if fic_id in seen_ids:
            r.errors.append(f"Duplicate fic_id: {fic_id}")
            r.status = "BLOCKED"
        seen_ids.add(fic_id)

        required_fields = ["fic_id", "unit_id", "fic_path", "target_file",
                           "status", "version", "risk_level", "enforcement_profile"]
        for field in required_fields:
            if field not in entry:
                r.errors.append(f"{fic_id}: missing required field '{field}'")
                r.status = "BLOCKED"

        fic_path = entry.get("fic_path", "")
        if fic_path:
            err = check_file(fic_path)
            if err:
                r.errors.append(f"{fic_id}: {err}")
                r.status = "BLOCKED"

        status = entry.get("status", "")
        if status and status not in VALID_LIFECYCLE_STATUSES:
            r.warnings.append(f"{fic_id}: unknown lifecycle status '{status}'")

        if fic_id == "FIC-L1-001":
            fic_l1_001_found = True
            if status not in ("ready-for-code", "validated"):
                r.warnings.append(f"FIC-L1-001 status is '{status}', expected 'ready-for-code' or 'validated'")

            target = entry.get("target_file", "")
            if target:
                err = check_file(target)
                if err:
                    r.errors.append(f"FIC-L1-001 target file missing: {err}")
                    r.status = "BLOCKED"

            test_file = "L1/tests/test_document_loader.py"
            err = check_file(test_file)
            if err:
                r.errors.append(f"FIC-L1-001 test file missing: {err}")
                r.status = "BLOCKED"

    if not fic_l1_001_found:
        r.errors.append("FIC-L1-001 not registered in index")
        r.status = "BLOCKED"

    return r
