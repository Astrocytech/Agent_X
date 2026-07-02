#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {
        "repo-memory": "repo-memory-mvp",
        "git-promotion": "generated-agent-git-promotion",
    }
    dir_name = stage_map.get(stage, "")
    if not dir_name:
        errors.append(f"Unknown stage: {stage}")
        return errors

    report_dir = Path(f".agentx-init/reports/{dir_name}")
    path = report_dir / "acceptance_matrix.json"

    if not path.exists():
        errors.append(f"acceptance_matrix.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("acceptance_matrix.json must be a JSON object")
        return errors

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0', got {data.get('schema_version')}")

    if data.get("artifact_type") != "acceptance_matrix":
        errors.append("artifact_type must be 'acceptance_matrix'")

    rows = data.get("rows", [])
    if not rows:
        errors.append("No rows in matrix")
        return errors

    for row in rows:
        status = row.get("status", "")
        rid = row.get("id", "?")
        if status in ("UNKNOWN", "PENDING"):
            errors.append(f"Row {rid} has {status} status")

        if status == "PASS":
            evidence_refs = row.get("evidence_refs", [])
            if not evidence_refs:
                errors.append(f"Row {rid} has PASS status but no evidence_refs")
            for idx, ref in enumerate(evidence_refs):
                if not Path(ref).exists():
                    errors.append(f"Row {rid} evidence_ref[{idx}] '{ref}' does not exist")
        elif "NOT_APPLICABLE" in status:
            errors.append(f"Row {rid} cannot be NOT_APPLICABLE for mandatory stage {stage}")

        if row.get("required") == "true" and status not in ("PASS", "BLOCKED_WITH_REASON"):
            errors.append(f"Required row {rid} has status {status}")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("repo-memory", "git-promotion"):
        print(f"Usage: {sys.argv[0]} <repo-memory|git-promotion>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE STAGE BUNDLE {stage} ACCEPTANCE MATRIX FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-stage-bundle-{stage}-acceptance-matrix: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
