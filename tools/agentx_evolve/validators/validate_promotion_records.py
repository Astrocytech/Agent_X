#!/usr/bin/env python3
"""Validate promotion records."""
import json, sys, os

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        for i, entry in enumerate(data):
            if "promotion_id" not in entry:
                errors.append(f"Entry {i}: missing promotion_id")
            if "decision" not in entry:
                errors.append(f"Entry {i}: missing decision")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_promotion_record_validation.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
