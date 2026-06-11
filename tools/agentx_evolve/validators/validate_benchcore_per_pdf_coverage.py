#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
COVERAGE = os.path.join(BC, "per_pdf_semantic_coverage_report.json")
INVENTORY = os.path.join(BC, "source_inventory.json")


def main() -> None:
    if not os.path.isfile(COVERAGE):
        print(f"FAIL: '{COVERAGE}' not found")
        sys.exit(1)

    with open(COVERAGE) as f:
        coverage = json.load(f)

    if not isinstance(coverage, list):
        print(f"FAIL: '{COVERAGE}' is not a list")
        sys.exit(1)

    if len(coverage) == 0:
        print(f"FAIL: '{COVERAGE}' is empty")
        sys.exit(1)

    PLACEHOLDER_PATS = ["PLACEHOLDER", "REPLACE_WITH_ACTUAL", "to be written", "not yet implemented"]

    hashes = {}
    if os.path.isfile(INVENTORY):
        with open(INVENTORY) as f:
            inv = json.load(f)
        hashes = {e.get("path"): e.get("sha256") for e in inv if isinstance(e, dict)}

    errors = []
    placeholder_errors = []
    for i, entry in enumerate(coverage):
        if not isinstance(entry, dict):
            errors.append(f"entry[{i}] is not a dict")
            continue
        if not any(k in entry for k in ("source_id", "filename", "pdf_path", "path")):
            errors.append(f"entry[{i}] missing identifier field")

        for field in ("hash", "sha256", "source_hash"):
            val = entry.get(field, "")
            if val:
                for pat in PLACEHOLDER_PATS:
                    if pat.lower() in val.lower():
                        placeholder_errors.append(f"entry[{i}] field '{field}' contains placeholder '{pat}': {val[:60]}")

    if placeholder_errors:
        for e in placeholder_errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: benchcore per-PDF coverage: {len(coverage)} PDFs with coverage data")


if __name__ == "__main__":
    main()
