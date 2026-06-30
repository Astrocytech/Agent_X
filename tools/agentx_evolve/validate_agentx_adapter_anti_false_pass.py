"""
validate_agentx_adapter_anti_false_pass.py

Validates the output of the anti-false-pass audit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / ".." / ".." / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_anti_false_pass_audit.json"


def main() -> int:
    if not AUDIT.exists():
        print("FAIL: anti-false-pass audit not found")
        return 1

    with open(AUDIT) as f:
        result = json.load(f)

    if result["status"] != "PASS":
        print(f"FAIL: anti-false-pass audit found {result['issues_found']} issue(s)")
        return 1

    print(f"PASS: anti-false-pass audit ({result['files_checked']} files checked, 0 issues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
