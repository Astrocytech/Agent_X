#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    path = report_dir / "final_verdict.json"

    if not path.exists():
        errors.append(f"final_verdict.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if data.get("verdict") not in ("PASS", "FAIL"):
        errors.append(f"Unknown verdict: {data.get('verdict')}")

    if data.get("stage") != stage:
        errors.append(f"Stage mismatch: expected {stage}, got {data.get('stage')}")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE EVOLUTION {stage.upper()} FINAL VERDICT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-evolution-{stage}-final-verdict: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
