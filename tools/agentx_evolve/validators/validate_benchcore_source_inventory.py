#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
INVENTORY = os.path.join(BC, "source_inventory.json")
EXPECTED_COUNT = 32


def main() -> None:
    if not os.path.isfile(INVENTORY):
        print(f"FAIL: '{INVENTORY}' not found")
        sys.exit(1)

    with open(INVENTORY) as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"FAIL: '{INVENTORY}' is not a list (got {type(data).__name__})")
        sys.exit(1)

    if len(data) != EXPECTED_COUNT:
        print(f"FAIL: '{INVENTORY}' has {len(data)} entries, expected {EXPECTED_COUNT}")
        sys.exit(1)

    PLACEHOLDER_PATS = ["PLACEHOLDER", "REPLACE_WITH_ACTUAL", "to be written", "not yet implemented"]

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"FAIL: entry {i} is not a dict")
            sys.exit(1)
        if not any(k in entry for k in ("source_id", "path", "filename")):
            print(f"FAIL: entry[{i}] missing identifier field (source_id/path/filename)")
            sys.exit(1)
        sha = entry.get("sha256", "")
        if not sha:
            print(f"FAIL: entry[{i}] missing 'sha256'")
            sys.exit(1)
        if sha == "PLACEHOLDER—REPLACE_WITH_ACTUAL_HASH":
            print(f"FAIL: entry[{i}] still has placeholder hash")
            sys.exit(1)
        if len(sha) != 64:
            print(f"FAIL: entry[{i}] sha256 has length {len(sha)}, expected 64")
            sys.exit(1)
        for pat in PLACEHOLDER_PATS:
            if pat.lower() in sha.lower():
                print(f"FAIL: entry[{i}] sha256 contains placeholder pattern '{pat}'")
                sys.exit(1)
        try:
            int(sha, 16)
        except ValueError:
            print(f"FAIL: entry[{i}] sha256 is not valid hex")
            sys.exit(1)

    print(f"PASS: benchcore source inventory: {len(data)}/{EXPECTED_COUNT} PDFs with valid hashes")


if __name__ == "__main__":
    main()
