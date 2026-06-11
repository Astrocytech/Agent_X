#!/usr/bin/env python3
"""Validate a clean replay report."""
import json, sys, os

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)
    if "replay_id" not in data:
        errors.append("Missing replay_id")
    if "verdict" not in data:
        errors.append("Missing verdict")
    if "source_commit" not in data:
        errors.append("Missing source_commit")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_clean_checkout_replay.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
