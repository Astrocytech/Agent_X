#!/usr/bin/env python3
"""Validate terminal seal: verify sealed hashes against current file bytes."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")

SEALED_FILES = [
    "final_verdict.json",
    "classification_report.json",
    "evidence_manifest.json",
]


def validate() -> list[str]:
    errors: list[str] = []
    seal_path = REPORT_BASE / "terminal_seal.json"
    if not seal_path.exists():
        errors.append("terminal_seal.json not found")
        return errors

    try:
        seal = json.loads(seal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"terminal_seal.json invalid: {e}")
        return errors

    if seal.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0', got {seal.get('schema_version')}")

    if seal.get("artifact_type") != "terminal_seal":
        errors.append("artifact_type must be 'terminal_seal'")

    sealed = seal.get("sealed_files", {})
    for fname in SEALED_FILES:
        sealed_hash = sealed.get(fname, "")
        if not sealed_hash:
            errors.append(f"Missing sealed hash for {fname}")
            continue
        if sealed_hash == "MISSING":
            errors.append(f"File {fname} was MISSING at sealing time")
            continue
        actual_path = REPORT_BASE / fname
        if not actual_path.exists():
            errors.append(f"Sealed file {fname} no longer exists")
            continue
        actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        if actual_hash != sealed_hash:
            errors.append(
                f"Terminal seal BREACHED for {fname}: "
                f"sealed hash={sealed_hash}, current hash={actual_hash}"
            )

    if not seal.get("all_present"):
        errors.append("Not all sealed files were present at sealing time")

    return errors


def main() -> int:
    errs = validate()
    if errs:
        print("VALIDATE TERMINAL SEAL FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-terminal-seal: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
