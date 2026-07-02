#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")

    path = report_dir / "replay_report.json"
    if not path.exists():
        errors.append(f"replay_report.json not found for stage {stage}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON in replay_report.json: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("replay_report.json is not a dict")
        return errors

    status = data.get("status", data.get("verdict", ""))
    if status == "FAIL":
        errors.append(f"replay_report.json for stage {stage} has FAIL status")
    if data.get("live_provider_used") is True:
        errors.append(f"replay_report.json for stage {stage} used live provider")

    # Require run IDs
    if not data.get("original_run_id") and not data.get("replay_run_id"):
        errors.append(f"replay_report.json for stage {stage} missing original_run_id and replay_run_id")

    # Require artifact_hashes for evidence-backed replay
    artifact_hashes = data.get("artifact_hashes", {})
    if not artifact_hashes:
        errors.append(f"replay_report.json for stage {stage} missing artifact_hashes")
    else:
        for expected in ("acceptance_matrix.json", "final_verdict.json"):
            if expected not in artifact_hashes:
                errors.append(f"replay_report.json for stage {stage} missing hash for {expected}")

    # Require agent_identity_hash
    if not data.get("agent_identity_hash"):
        errors.append(f"replay_report.json for stage {stage} missing agent_identity_hash")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE EVOLUTION {stage.upper()} REPLAY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-evolution-{stage}-replay: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
