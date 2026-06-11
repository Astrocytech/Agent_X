"""Validate idempotency report for Functional Runtime MVP."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def validate_idempotency() -> list[str]:
    errors = []

    report_path = REPORT_DIR / "functional_runtime_mvp_idempotency_report.json"
    if not report_path.exists():
        errors.append("Idempotency report missing")
        return errors

    report = load_json(str(report_path))
    if not report:
        errors.append("Idempotency report does not parse")
        return errors

    runs = report.get("runs", [])
    if len(runs) != 2:
        errors.append(f"Idempotency report must have exactly 2 runs, got {len(runs)}")

    for i, run in enumerate(runs):
        if not run.get("transcript_hash"):
            errors.append(f"Run {i + 1} missing transcript_hash")

    if report.get("verdict") != "PASS":
        errors.append(f"Idempotency verdict not PASS: {report.get('verdict')}")

    return errors


def main() -> int:
    errs = validate_idempotency()
    if errs:
        print("VALIDATE IDEMPOTENCY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-idempotency: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
