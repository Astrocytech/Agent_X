"""
validate_agentx_adapter_final_verdict.py

Validates that the final verdict file contains a valid claim. Accepts
AGENTX_ADAPTER_MVP or AGENTX_ADAPTER_MVP_CANDIDATE as passing verdicts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERDICT = HERE / ".." / ".." / ".agentx-init" / "reports" / "adapter-mvp" / "adapter_final_verdict.json"

ALLOWED_VERDICTS = {"AGENTX_ADAPTER_MVP", "AGENTX_ADAPTER_MVP_CANDIDATE"}


def main() -> int:
    if not VERDICT.exists():
        print("FAIL: final verdict not found")
        return 1

    with open(VERDICT) as f:
        result = json.load(f)

    v = result.get("verdict", "")
    if v in ALLOWED_VERDICTS:
        print(f"PASS: {v} ({result.get('acceptance_passed', '?')}/{result.get('acceptance_total', '?')} acceptance)")
        return 0

    if v == "PARTIAL":
        print(f"PARTIAL: {result.get('acceptance_passed', '?')}/{result.get('acceptance_total', '?')} passed")
        return 1

    print(f"FAIL: invalid verdict '{v}'")
    return 1


if __name__ == "__main__":
    sys.exit(main())
