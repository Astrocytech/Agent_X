#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    path = report_dir / "anti_false_pass_report.json"

    if not path.exists():
        errors.append(f"anti_false_pass_report.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    results = data.get("results", [])
    if not results:
        errors.append(f"No attack results in anti_false_pass_report for stage {stage}")
        return errors

    for r in results:
        if not r.get("blocked"):
            errors.append(f"Attack not blocked: {r.get('attack', '?')}")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE EVOLUTION {stage.upper()} ANTI FALSE PASS FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-evolution-{stage}-anti-false-pass: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
