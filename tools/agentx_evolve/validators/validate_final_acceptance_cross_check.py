#!/usr/bin/env python3
import json, sys, os

CROSS_CHECK_FILE = os.path.join(".agentx-init", "reports", "final_acceptance_cross_check_matrix.json")

R3_13_CHECKS = [
    "CC-031", "CC-032", "CC-033", "CC-034", "CC-035",
    "CC-036", "CC-037", "CC-038", "CC-039", "CC-040",
    "CC-041", "CC-042", "CC-043", "CC-044", "CC-045",
    "CC-046", "CC-047", "CC-048", "CC-049", "CC-050",
    "CC-051", "CC-052", "CC-053", "CC-054",
]
EXPECTED_IDS = [f"CC-{i:03d}" for i in range(1, 31)] + R3_13_CHECKS

BLOCKED_STATUSES = {"FAIL", "BLOCKED", "UNKNOWN"}

def main():
    if not os.path.isfile(CROSS_CHECK_FILE):
        print(f"FAIL: Cross-check matrix '{CROSS_CHECK_FILE}' not found")
        sys.exit(1)

    try:
        with open(CROSS_CHECK_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: '{CROSS_CHECK_FILE}' invalid JSON: {e}")
        sys.exit(1)

    errors = []
    rows = data if isinstance(data, list) else data.get("rows", data.get("entries", data.get("checks", [])))
    if not isinstance(rows, list):
        errors.append("Cross-check matrix contains no rows list")
        rows = []

    found_ids = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"Row {i} is not a dict")
            continue
        cid = row.get("cross_check_id", row.get("id", f"row-{i}"))
        found_ids.add(cid)

        status = row.get("status", row.get("verdict", row.get("result", "")))
        if status in BLOCKED_STATUSES:
            errors.append(f"Row '{cid}' has blocking status '{status}'")

    for expected in EXPECTED_IDS:
        if expected not in found_ids:
            errors.append(f"Expected cross-check ID '{expected}' not found in matrix")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: cross-check matrix validates with {len(rows)} rows, all {len(EXPECTED_IDS)} expected IDs present, no blocking statuses")
    sys.exit(0)

if __name__ == "__main__":
    main()
