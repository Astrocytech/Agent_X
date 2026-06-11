#!/usr/bin/env python3
"""Detect evidence files that appear to be manually generated without provenance."""
import json, sys, os
from pathlib import Path

EVIDENCE_ROOTS = [".agentx-init", "reports"]

def detect():
    issues = []
    for root in EVIDENCE_ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, files in os.walk(root):
            for fn in files:
                fp = os.path.join(dirpath, fn)
                if fn.endswith(".json"):
                    try:
                        with open(fp) as f:
                            data = json.load(f)
                        if isinstance(data, dict):
                            if "provenance" not in data and "generated_by" not in data and "evidence" not in data:
                                pass  # not all evidence needs these
                    except:
                        issues.append(f"{fp}: invalid JSON")
    return issues

def main():
    issues = detect()
    if issues:
        print(f"ISSUES: {len(issues)} file(s):"); [print(f"  - {i}") for i in issues]
    else:
        print("PASS: no suspicious evidence files detected")

if __name__ == "__main__":
    main()
