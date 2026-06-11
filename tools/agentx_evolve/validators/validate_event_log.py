#!/usr/bin/env python3
"""Validate an event log."""
import json, sys, os

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        for i, entry in enumerate(data):
            if "event_id" not in entry:
                errors.append(f"Entry {i}: missing event_id")
            if "timestamp_utc" not in entry:
                errors.append(f"Entry {i}: missing timestamp_utc")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_event_log_validation.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
