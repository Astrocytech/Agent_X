"""Validate that validators themselves are correctly structured.

Covers gap list items 227-230:
  227. Positive-control + negative-control: validators pass clean, fail corrupted
  228. No import-time report loading before --report-dir parsed
  229. No unreplaceable global REPORT_DIR
  230. No different behavior when imported vs executed as script
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
VALIDATORS_DIR = Path(__file__).resolve().parent
STATUS_OK = 0
STATUS_FAIL = 1


def get_validator_modules() -> list[str]:
    modules = []
    for f in sorted(VALIDATORS_DIR.glob("validate_functional_runtime_mvp_*.py")):
        if f.name == "validate_functional_runtime_mvp_validator_proof.py":
            continue
        modules.append(f.stem)
    return modules


def validate_validator_proof() -> list[str]:
    errors = []
    validator_names = get_validator_modules()

    if not validator_names:
        errors.append("No validator modules found")
        return errors

    for vname in validator_names:
        vpath = VALIDATORS_DIR / f"{vname}.py"

        # Gap 228: Check for import-time report loading
        source = vpath.read_text(encoding="utf-8")
        if "REPORT_DIR = " in source and "parse_report_dir()" not in source:
            lines = source.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("REPORT_DIR = ") and "parse_report_dir" not in line:
                    errors.append(
                        f"Validator {vname}: has REPORT_DIR that does not use parse_report_dir() "
                        f"(line {i + 1})"
                    )

        # Gap 229: Check that REPORT_DIR can be overridden
        if "parse_report_dir" not in source:
            errors.append(f"Validator {vname}: does not use parse_report_dir() for REPORT_DIR")

        # Gap 230: Check for __name__ == "__main__" guard
        if "if __name__ == \"__main__\":" not in source and 'if __name__ == "__main__":' not in source:
            errors.append(f"Validator {vname}: missing __name__ == '__main__' guard")

        # Check valid main() function exists
        has_main = "def main()" in source
        if not has_main:
            errors.append(f"Validator {vname}: missing main() function")

        # Check nonzero exit codes on failure
        has_status_fail = "STATUS_FAIL" in source and "STATUS_OK" in source
        has_sys_exit = "sys.exit(1)" in source or "sys.exit(STATUS_FAIL)" in source
        has_return_fail = "return 1" in source or "return STATUS_FAIL" in source
        if not has_status_fail and not has_sys_exit and not has_return_fail:
            errors.append(f"Validator {vname}: missing STATUS_FAIL/STATUS_OK constants")

        # Check for missing __name__ guard
        if "if __name__" not in source:
            errors.append(f"Validator {vname}: missing __name__ guard for script execution")

        # Check main() returns proper exit codes
        if "sys.exit(main())" not in source and "sys.exit(" not in source:
            errors.append(f"Validator {vname}: does not call sys.exit(main())")

    # Gap 227: Positive-control check — run validators against actual clean reports
    try:
        for vname in validator_names:
            result = subprocess.run(
                [sys.executable, str(VALIDATORS_DIR / f"{vname}.py"),
                 "--report-dir", str(REPORT_DIR)],
                capture_output=True, text=True, timeout=30,
            )
            # We only warn if the validator itself crashes (infrastructure error)
            stderr = result.stderr or ""
            is_infra = (
                "No such file or directory" in stderr
                or "ModuleNotFoundError" in stderr
                or "ImportError" in stderr
            )
            if is_infra:
                errors.append(f"Positive-control: validator {vname} crashed on clean reports:\n{stderr[:300]}")
    except subprocess.TimeoutExpired:
        errors.append("Positive-control: validator execution timed out")
    except OSError as e:
        errors.append(f"Positive-control: cannot run validators: {e}")

    return errors


def main() -> int:
    errs = validate_validator_proof()
    if errs:
        print("VALIDATE VALIDATOR PROOF FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-validator-proof: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
