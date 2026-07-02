#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "anti_false_pass_report.json"
    if not path.exists():
        errors.append(f"anti_false_pass_report.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("anti_false_pass_report.json must be a JSON object")
        return errors

    results = data.get("results", [])
    if not results:
        errors.append("No attack results in report")
        return errors

    for r in results:
        if not r.get("blocked"):
            errors.append(f"Attack not blocked: {r.get('attack', 'UNKNOWN')}")
        if r.get("expected_failure_reason") and not r.get("failure_reason_matched"):
            errors.append(
                f"Attack {r.get('attack', 'UNKNOWN')}: expected failure reason "
                f"'{r.get('expected_failure_reason')}' not matched "
                f"(actual: '{r.get('actual_failure_reason', 'UNKNOWN')}')"
            )

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_anti_false_pass",
        "passed": len(errs) == 0,
        "all_attacks_blocked": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_anti_false_pass.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE ANTI FALSE PASS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-anti-false-pass: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
