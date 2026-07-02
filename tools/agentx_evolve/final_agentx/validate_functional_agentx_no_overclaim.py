#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "no_overclaim_report.json"
    if not path.exists():
        errors.append(f"no_overclaim_report.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    findings = data.get("findings", [])
    if findings:
        for f in findings:
            errors.append(f"Overclaim flagged: {f.get('file')}:{f.get('line')} - {f.get('pattern')}")

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_no_overclaim",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_no_overclaim.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE NO OVERCLAIM FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-no-overclaim: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
