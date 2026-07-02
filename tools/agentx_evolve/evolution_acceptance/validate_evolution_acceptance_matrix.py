#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    path = report_dir / "acceptance_matrix.json"

    if not path.exists():
        errors.append(f"acceptance_matrix.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0'")

    rows = data.get("rows", [])
    if not rows:
        errors.append("No rows in matrix")
        return errors

    for row in rows:
        status = row.get("status", "")
        rid = row.get("id", "?")
        if status in ("UNKNOWN", "PENDING"):
            errors.append(f"Row {rid} has {status} status")

        # Check evidence_refs for PASS rows
        if status == "PASS":
            evidence_refs = row.get("evidence_refs", [])
            if not evidence_refs:
                errors.append(f"Row {rid} has PASS status but no evidence_refs")
            for idx, ref in enumerate(evidence_refs):
                if not Path(ref).exists():
                    errors.append(f"Row {rid} evidence_ref[{idx}] '{ref}' does not exist")

        if row.get("required") == "true" and status == "BLOCKED_WITH_REASON":
            errors.append(f"Required row {rid} is blocked")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE EVOLUTION {stage.upper()} ACCEPTANCE MATRIX FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-evolution-{stage}-acceptance-matrix: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
