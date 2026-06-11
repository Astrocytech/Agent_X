#!/usr/bin/env python3
"""Validate a five-document traceability matrix."""
import json, sys, os
from pathlib import Path

ALLOWED_STATUSES = {
    "PASS", "FAIL", "PARTIAL", "SCAFFOLD_ONLY", "MISSING", "BLOCKED",
    "CONFLICT", "UNKNOWN", "UNVERIFIED", "WEAK_TARGET", "NOT_RUN",
    "COMMAND_MISSING", "PLACEHOLDER", "NOT_APPLICABLE_WITH_REASON"
}

def validate(path: str) -> list[str]:
    errors = []
    with open(path) as f:
        data = json.load(f)

    if "requirements" not in data:
        errors.append("Missing 'requirements' array")
        return errors

    for req in data["requirements"]:
        rid = req.get("requirement_id", "?")
        if "status" not in req:
            errors.append(f"{rid}: missing status")
            continue
        status = req["status"]
        if status not in ALLOWED_STATUSES:
            errors.append(f"{rid}: invalid status '{status}'")
        if status == "PASS":
            if not req.get("implementation_files") and not req.get("test_files"):
                errors.append(f"{rid}: PASS but no implementation or test files")
        if req.get("mandatory", False) and status in ("UNKNOWN", "MISSING", "BLOCKED", "CONFLICT"):
            errors.append(f"{rid}: mandatory requirement has blocking status '{status}'")

    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/matrix/five_document_traceability_matrix.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found")
        sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
