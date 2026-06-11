#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
VISUAL = os.path.join(BC, "visual_inventory.json")


def main() -> None:
    if not os.path.isfile(VISUAL):
        print(f"FAIL: '{VISUAL}' not found")
        sys.exit(1)

    with open(VISUAL) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"FAIL: '{VISUAL}' is not a list (got {type(data).__name__})")
        sys.exit(1)

    if len(data) == 0:
        print(f"FAIL: '{VISUAL}' is empty")
        sys.exit(1)

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"FAIL: entry[{i}] is not a dict")
            sys.exit(1)
        if not any(k in entry for k in ("source_id", "path", "id")):
            print(f"FAIL: entry[{i}] missing identifier field")
            sys.exit(1)

    print(f"PASS: benchcore visual inventory: {len(data)} entries")


if __name__ == "__main__":
    main()
