#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")

MANDATORY_GATES = {"FRMVP", "AdapterMVP", "Alpha", "Beta", "Governed", "Memory", "GitPromotion"}


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "acceptance_matrix.json"
    if not path.exists():
        errors.append(f"acceptance_matrix.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("acceptance_matrix.json must be a JSON object")
        return errors

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0', got {data.get('schema_version')}")

    if data.get("artifact_type") != "acceptance_matrix":
        errors.append("artifact_type must be 'acceptance_matrix'")

    rows = data.get("rows", [])
    if not rows:
        errors.append("acceptance_matrix.json has no rows")
        return errors

    for row in rows:
        rid = row.get("id", "UNKNOWN")
        status = row.get("status", "UNKNOWN")
        category = row.get("category", "")
        required = row.get("required", "false")
        evidence_refs = row.get("evidence_refs", [])

        if status == "UNKNOWN":
            errors.append(f"Row {rid} has UNKNOWN status")
        if status == "PENDING":
            errors.append(f"Row {rid} has PENDING status")

        # Check NOT_APPLICABLE_WITH_REASON constraint for mandatory gates
        if status == "NOT_APPLICABLE_WITH_REASON" and category in MANDATORY_GATES:
            errors.append(f"Mandatory gate row {rid} (category={category}) cannot be NOT_APPLICABLE_WITH_REASON")

        # Check evidence refs for PASS rows (allow missing files — generated later by enterprise pipeline)
        if status == "PASS":
            if not evidence_refs:
                errors.append(f"Row {rid} has PASS status but no evidence_refs")

        # Check required status constraints
        if required == "true" and status not in ("PASS", "BLOCKED_WITH_REASON", "NOT_APPLICABLE_WITH_REASON"):
            errors.append(f"Required row {rid} has status {status}")

        # Check for BLOCKED rows that still have empty evidence_refs (should have reason)
        if "BLOCKED" in status and not evidence_refs and required == "true":
            errors.append(f"Required BLOCKED row {rid} has no evidence_refs to diagnose blockage")

    # Check blocked rows (but allow enterprise-deferred ones)
    blocked = [r for r in rows if "BLOCKED" in r.get("status", "")]
    if blocked:
        blocked_ids = [r["id"] for r in blocked]
        errors.append(f"Blocked rows: {blocked_ids}")

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_acceptance_matrix",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_acceptance_matrix.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE ACCEPTANCE MATRIX FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-acceptance-matrix: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
