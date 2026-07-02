#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")

    path = report_dir / "command_transcript.json"
    if not path.exists():
        errors.append(f"command_transcript.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON in command_transcript.json: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("command_transcript.json must be a JSON object")
        return errors

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0', got {data.get('schema_version')}")

    expected_type = f"evolution_command_transcript_{stage}"
    if data.get("artifact_type") not in ("command_transcript", expected_type):
        errors.append(f"artifact_type expected '{expected_type}' or 'command_transcript', got '{data.get('artifact_type')}'")

    source = data.get("source", "")
    if source != "recorded":
        errors.append(f"Command transcript source is '{source}', expected 'recorded'")

    entries = data.get("entries", [])
    if not entries:
        errors.append(f"Command transcript has 0 entries")

    for i, entry in enumerate(entries):
        cmd = entry.get("command", "")
        if not cmd:
            errors.append(f"Entry {i} has empty command")
        if "exit_code" not in entry:
            errors.append(f"Entry {i} missing exit_code")
        if "mandatory" not in entry:
            errors.append(f"Entry {i} missing mandatory flag")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE EVOLUTION {stage.upper()} COMMAND TRANSCRIPT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-evolution-{stage}-command-transcript: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
