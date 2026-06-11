#!/usr/bin/env python3
"""Validate a source hash manifest."""
import json, sys, os

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)
    for key, entry in data.items() if isinstance(data, dict) else enumerate(data):
        if isinstance(entry, dict):
            if "sha256" not in entry:
                errors.append(f"{key}: missing sha256")
            elif len(entry["sha256"]) != 64:
                errors.append(f"{key}: invalid sha256 length")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_source_hash_manifest_after.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
