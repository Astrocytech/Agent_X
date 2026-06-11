"""Validate failure taxonomy, structured error records, and proof-run isolation.

Gaps 314-327: failure taxonomy, atomic writes, truncated JSON, stale files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

REQUIRED_TAXONOMY_CODES = [
    "INFRASTRUCTURE_ERROR", "TIMEOUT", "VALIDATION_FAIL", "RESOURCE_LIMIT",
    "BLOCKED", "INTERNAL_ERROR", "UNKNOWN", "UNCLASSIFIED",
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_failure_taxonomy() -> list[str]:
    errors = []

    # Item 314: Failure taxonomy — machine-readable phase, component, code
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        for cmd_idx, cmd in enumerate(transcript):
            if not isinstance(cmd, dict):
                continue
            ec = cmd.get("exit_code", 0)
            if ec != 0:
                cname = cmd.get("command", "?")
                tax = cmd.get("failure_code", cmd.get("error_code", ""))
                if not tax:
                    errors.append(f"Failure-taxonomy: 314 - command '{cname}' exit_code={ec} missing failure_code")
                phase = cmd.get("phase", cmd.get("proof_phase", ""))
                if not phase:
                    errors.append(f"Failure-taxonomy: 314 - command '{cname}' exit_code={ec} missing phase")
                component = cmd.get("component", "")
                if not component:
                    errors.append(f"Failure-taxonomy: 314 - command '{cname}' exit_code={ec} missing component")

    # Item 315: Structured failure records in proof bundle
    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(proof_bundle, dict):
        failures = proof_bundle.get("failures", proof_bundle.get("failure_records", []))
        for f in failures if isinstance(failures, list) else []:
            if not isinstance(f, dict):
                continue
            tax_code = f.get("code", f.get("failure_code", ""))
            tax_phase = f.get("phase", "")
            tax_component = f.get("component", "")
            if not tax_code:
                errors.append("Failure-taxonomy: 315 - failure record missing taxonomy code")
            if tax_code and tax_code not in REQUIRED_TAXONOMY_CODES:
                errors.append(f"Failure-taxonomy: 315 - unrecognized taxonomy code: {tax_code}")

    # Item 316: Unclassified errors — UNKNOWN/UNCLASSIFIED should be BLOCKED
    for f in failures if isinstance(proof_bundle, dict) and isinstance((failures := proof_bundle.get("failures", proof_bundle.get("failure_records", []))), list) else []:
        if isinstance(f, dict):
            code = f.get("code", f.get("failure_code", ""))
            if code in ("UNKNOWN", "UNCLASSIFIED"):
                f_phase = f.get("phase", "?")
                f_comp = f.get("component", "?")
                errors.append(f"Failure-taxonomy: 316 - unclassified error in {f_phase}/{f_comp} — must be BLOCKED")

    # Items 319-320: Atomic writes, partial output detection
    for f in REPORT_DIR.iterdir():
        if not f.is_file():
            continue
        # Truncated JSON (item 321)
        if f.suffix == ".json" and f.stat().st_size > 0:
            try:
                raw = f.read_bytes()
                json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                errors.append(f"Failure-taxonomy: 321 - truncated/invalid JSON: {f.name}")
        # Zero-byte files
        if f.stat().st_size == 0:
            errors.append(f"Failure-taxonomy: 321 - zero-byte file: {f.name}")
        # Orphaned .tmp files
        if f.suffix in (".tmp", ".temp", ".part"):
            errors.append(f"Failure-taxonomy: 321 - orphaned temporary file: {f.name}")
        # Stale lock files
        if f.name.endswith(".lock"):
            errors.append(f"Failure-taxonomy: 321 - stale lock file: {f.name}")

    # Item 322-323: proof_run_id propagation
    if isinstance(proof_bundle, dict):
        bundle_rid = proof_bundle.get("proof_run_id", "")
        if bundle_rid:
            for jf in REPORT_DIR.glob("*.json"):
                data = load_json(str(jf))
                if isinstance(data, dict):
                    rid = data.get("proof_run_id", "")
                    if rid and rid != bundle_rid:
                        if jf.name not in ("functional_runtime_mvp_baseline_command_transcript.json",):
                            errors.append(f"Failure-taxonomy: 323 - {jf.name} proof_run_id '{rid}' != bundle '{bundle_rid}'")
        else:
            errors.append("Failure-taxonomy: 322 - proof bundle missing proof_run_id")

    # Items 324-325: Proof-run locking
    if isinstance(proof_bundle, dict):
        lock_info = proof_bundle.get("lock", proof_bundle.get("proof_run_lock", ""))
        if not lock_info:
            errors.append("Failure-taxonomy: 324 - proof bundle missing lock/proof_run_lock info")

    return errors


def main() -> int:
    errs = validate_failure_taxonomy()
    if errs:
        print("VALIDATE FAILURE TAXONOMY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-failure-taxonomy: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
