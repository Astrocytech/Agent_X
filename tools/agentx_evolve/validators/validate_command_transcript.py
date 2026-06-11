#!/usr/bin/env python3
"""Validate a command transcript JSON."""
import json, sys, os

def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f) if path.endswith(".json") else []
    if isinstance(data, dict):
        data = [data]
    for i, entry in enumerate(data):
        if "command" not in entry:
            errors.append(f"Entry {i}: missing 'command'")
        if "exit_code" not in entry:
            errors.append(f"Entry {i}: missing 'exit_code'")
    return errors

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/baseline/baseline_command_transcript.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    print(f"PASS: {path} validates")

if __name__ == "__main__":
    main()
