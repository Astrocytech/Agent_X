#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
BOUNDARY = os.path.join(BC, "product_specific_boundary_report.json")


def main() -> None:
    if not os.path.isfile(BOUNDARY):
        print(f"FAIL: '{BOUNDARY}' not found")
        sys.exit(1)

    with open(BOUNDARY) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"FAIL: '{BOUNDARY}' is not a list (got {type(data).__name__})")
        sys.exit(1)

    if len(data) == 0:
        print(f"FAIL: '{BOUNDARY}' is empty")
        sys.exit(1)

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"FAIL: entry[{i}] is not a dict")
            sys.exit(1)

    print(f"PASS: benchcore claim boundaries: {len(data)} boundary entries")


if __name__ == "__main__":
    main()
