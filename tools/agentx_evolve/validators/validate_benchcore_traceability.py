#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
MATRIX = os.path.join(BC, "per_pdf_coverage_matrix.json")
COVERAGE = os.path.join(BC, "per_pdf_semantic_coverage_report.json")


def main() -> None:
    if not os.path.isfile(MATRIX):
        print(f"FAIL: '{MATRIX}' not found")
        sys.exit(1)

    with open(MATRIX) as f:
        matrix = json.load(f)

    if not isinstance(matrix, dict):
        print(f"FAIL: '{MATRIX}' is not a dict (got {type(matrix).__name__})")
        sys.exit(1)

    if len(matrix) == 0:
        print(f"FAIL: '{MATRIX}' is empty")
        sys.exit(1)

    # Check coverage matrix has status + total_pdfs
    status = matrix.get("status")
    if status not in ("PASS", "REGENERATED"):
        if status is None:
            print(f"FAIL: '{MATRIX}' missing 'status'")
        else:
            print(f"FAIL: '{MATRIX}' status is '{status}', expected 'PASS'")
        sys.exit(1)

    total = matrix.get("total_pdfs", 0)
    if total < 32:
        print(f"FAIL: '{MATRIX}' total_pdfs={total}, expected >= 32")
        sys.exit(1)

    print(f"PASS: benchcore traceability matrix: status={status}, total_pdfs={total}")


if __name__ == "__main__":
    main()
