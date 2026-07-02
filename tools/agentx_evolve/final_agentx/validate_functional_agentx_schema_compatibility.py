#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agentx_evolve.final_agentx import REPORT_BASE, load_json


SCHEMA_VERSION = "1.0"

STAGE_SCHEMA_FIELDS: dict[str, list[str]] = {
    "acceptance_matrix": [
        "schema_version", "artifact_type", "producer", "stage",
        "total_rows", "passed", "blocked", "rows",
    ],
    "final_verdict": [
        "schema_version", "artifact_type", "producer", "git_commit",
        "verdict", "classification", "ci_status",
        "mandatory_gates_total", "mandatory_gates_passed", "mandatory_gates_failed",
    ],
    "replay_report": [
        "schema_version", "status", "original_run_id", "replay_run_id",
        "contract_hash_match", "live_provider_used",
    ],
    "evidence_manifest": [
        "schema_version", "artifact_type", "producer", "git_commit", "evidence_refs",
    ],
    "anti_false_pass_report": [
        "schema_version", "artifact_type", "producer", "total_attacks", "blocked", "results",
    ],
}


def validate_schema(name: str, path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        errors.append(f"{name}: file not found at {path}")
        return errors

    data = load_json(path)
    if data is None:
        errors.append(f"{name}: could not parse JSON from {path}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"{name}: expected dict, got {type(data).__name__}")
        return errors

    sv = data.get("schema_version", "")
    if sv != SCHEMA_VERSION:
        errors.append(f"{name}: schema_version expected '{SCHEMA_VERSION}', got '{sv}'")

    expected_fields = STAGE_SCHEMA_FIELDS.get(name, [])
    if expected_fields:
        missing = [f for f in expected_fields if f not in data]
        if missing:
            errors.append(f"{name}: missing required fields: {', '.join(missing)}")

    return errors


def validate_all() -> list[str]:
    errors: list[str] = []

    artifact_map: dict[str, str] = {
        "acceptance_matrix": "acceptance_matrix.json",
        "final_verdict": "final_verdict.json",
        "replay_report": "replay_report.json",
        "evidence_manifest": "evidence_manifest.json",
        "anti_false_pass_report": "anti_false_pass_report.json",
    }

    for name, filename in artifact_map.items():
        path = REPORT_BASE / filename
        errs = validate_schema(name, path)
        errors.extend(errs)

    return errors


def main() -> int:
    errs = validate_all()
    if errs:
        print("SCHEMA COMPATIBILITY VALIDATION FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-schema-compatibility: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
