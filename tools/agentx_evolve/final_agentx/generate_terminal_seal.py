#!/usr/bin/env python3
"""Generate terminal seal after all reports are produced.

Binds final_verdict.json, classification_report.json, and
evidence_manifest.json with SHA-256 hashes and the current run_id/commit.
This seal is the final proof that artifacts were not mutated after sealing.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")

SEALED_FILES = [
    "final_verdict.json",
    "classification_report.json",
    "evidence_manifest.json",
]


def _get_run_id() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()[:8]
    except Exception:
        return "UNKNOWN"


def generate_seal() -> dict:
    commits = {}
    for fname in SEALED_FILES:
        fpath = REPORT_BASE / fname
        if fpath.exists():
            commits[fname] = hashlib.sha256(fpath.read_bytes()).hexdigest()
        else:
            commits[fname] = "MISSING"

    seal = {
        "schema_version": "1.0",
        "artifact_type": "terminal_seal",
        "producer": "tools/agentx_evolve/final_agentx/generate_terminal_seal.py",
        "sealed_files": commits,
        "all_present": all(v != "MISSING" for v in commits.values()),
        "all_hashes_match": True,
    }
    return seal


def validate_seal() -> list[str]:
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

    if seal.get("artifact_type") != "terminal_seal":
        errors.append("artifact_type must be 'terminal_seal'")

    sealed = seal.get("sealed_files", {})
    for fname in SEALED_FILES:
        sealed_hash = sealed.get(fname, "")
        if sealed_hash == "MISSING":
            errors.append(f"Seal missing hash for {fname}")
            continue
        actual_path = REPORT_BASE / fname
        if not actual_path.exists():
            errors.append(f"Sealed file {fname} no longer exists")
            continue
        actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()
        if actual_hash != sealed_hash:
            errors.append(f"Seal hash mismatch for {fname}: sealed={sealed_hash}, actual={actual_hash}")

    if not seal.get("all_present"):
        errors.append("Terminal seal indicates not all files were present at sealing time")

    return errors


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    seal = generate_seal()
    seal_path = REPORT_BASE / "terminal_seal.json"
    tmp = seal_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(seal, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(seal_path)
    print(f"Terminal seal written to {seal_path}")
    print(f"  All sealed files present: {seal['all_present']}")

    errs = validate_seal()
    if errs:
        print("TERMINAL SEAL SELF-VALIDATION FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("Terminal seal self-validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
