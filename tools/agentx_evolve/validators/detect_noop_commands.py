#!/usr/bin/env python3
"""Detect no-op commands in a transcript."""
import json, sys, os

NOOP_PATTERNS = ["echo ok", "echo passed", "exit 0", "true"]

def detect(path):
    issues = []
    with open(path) as f:
        data = json.load(f) if path.endswith(".json") else []
    if isinstance(data, dict):
        data = [data]
    for i, entry in enumerate(data):
        cmd = entry.get("command", "")
        for pat in NOOP_PATTERNS:
            if pat in cmd.lower():
                issues.append(f"Entry {i}: possible no-op command: {cmd}")
                break
    return issues

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/baseline/baseline_command_transcript.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found — command transcript is a mandatory proof artifact"); sys.exit(1)
    issues = detect(path)
    if issues:
        print(f"ISSUES: {len(issues)} no-op command(s):"); [print(f"  - {i}") for i in issues]
    else:
        print(f"PASS: no no-op commands in {path}")

if __name__ == "__main__":
    main()
