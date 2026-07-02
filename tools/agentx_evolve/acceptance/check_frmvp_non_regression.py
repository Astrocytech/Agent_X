"""Check FRMVP non-regression for the Adapter MVP proof pipeline.

Validates that the FRMVP verdict exists, is well-formed, and reports
"verified" status with classification FUNCTIONAL_RUNTIME_MVP.

Exit code 0 on pass, 1 on failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    p = Path(".agentx-init/reports/functional_runtime_mvp_final_verdict.json")
    if not p.exists():
        print("FRMVP non-regression FAIL: verdict file not found")
        return 1
    v = json.loads(p.read_text())
    verdict_status = v.get("verdict_status", "unknown")
    classification = v.get("classification", "unknown")
    final_val = v.get("final_validator", "unknown")
    non_regression_ok = (
        verdict_status == "verified"
        and classification == "FUNCTIONAL_RUNTIME_MVP"
        and final_val == "all_passed"
    )
    label = "PASS" if non_regression_ok else "FAIL"
    print(f"FRMVP non-regression: {label} (status={verdict_status}, class={classification}, final={final_val})")
    return 0 if non_regression_ok else 1


if __name__ == "__main__":
    sys.exit(main())
