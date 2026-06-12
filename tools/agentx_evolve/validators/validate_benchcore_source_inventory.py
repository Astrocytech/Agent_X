#!/usr/bin/env python3
import json, os, sys

BC = os.path.join("benchmarks", "benchcore")
INVENTORY = os.path.join(BC, "source_inventory.json")
HASHES = os.path.join(BC, "source_hashes.json")
EXPECTED_COUNT = 32

PLACEHOLDER_PATS = ["PLACEHOLDER", "REPLACE_WITH_ACTUAL", "to be written", "not yet implemented"]


def _validate_sha256(sha: str, label: str) -> None:
    if not sha:
        print(f"FAIL: {label} missing 'sha256'")
        sys.exit(1)
    if sha == "PLACEHOLDER—REPLACE_WITH_ACTUAL_HASH":
        print(f"FAIL: {label} still has placeholder hash")
        sys.exit(1)
    if len(sha) != 64:
        print(f"FAIL: {label} sha256 has length {len(sha)}, expected 64")
        sys.exit(1)
    for pat in PLACEHOLDER_PATS:
        if pat.lower() in sha.lower():
            print(f"FAIL: {label} sha256 contains placeholder pattern '{pat}'")
            sys.exit(1)
    try:
        int(sha, 16)
    except ValueError:
        print(f"FAIL: {label} sha256 is not valid hex")
        sys.exit(1)


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

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"FAIL: entry {i} is not a dict")
            sys.exit(1)
        source_id = entry.get("source_id", "")
        if not source_id:
            print(f"FAIL: entry[{i}] missing 'source_id'")
            sys.exit(1)
        sha = entry.get("sha256", "")
        _validate_sha256(sha, f"entry[{i}] ({source_id})")

    print(f"PASS: source_inventory.json: {len(data)}/{EXPECTED_COUNT} PDFs with valid hashes")

    if not os.path.isfile(HASHES):
        print(f"FAIL: '{HASHES}' not found")
        sys.exit(1)

    with open(HASHES) as f:
        hash_data = json.load(f)

    if not isinstance(hash_data, dict):
        print(f"FAIL: '{HASHES}' is not a dict (got {type(hash_data).__name__})")
        sys.exit(1)

    if len(hash_data) != EXPECTED_COUNT:
        print(f"FAIL: '{HASHES}' has {len(hash_data)} entries, expected {EXPECTED_COUNT}")
        sys.exit(1)

    for doc_id, info in hash_data.items():
        if not isinstance(info, dict):
            print(f"FAIL: '{HASHES}' entry '{doc_id}' is not a dict")
            sys.exit(1)
        sha = info.get("sha256", "")
        _validate_sha256(sha, f"'{HASHES}' entry '{doc_id}'")

    for entry in data:
        doc_id = entry.get("source_id", "")
        if doc_id not in hash_data:
            print(f"FAIL: source_inventory.json has '{doc_id}' not in source_hashes.json")
            sys.exit(1)
        expected = entry["sha256"]
        actual = hash_data[doc_id]["sha256"]
        if expected != actual:
            print(f"FAIL: hash mismatch for {doc_id}: inventory={expected}, hashes={actual}")
            sys.exit(1)

    print(f"PASS: source_hashes.json: {len(hash_data)}/{EXPECTED_COUNT} entries, all match source_inventory.json")


if __name__ == "__main__":
    main()
