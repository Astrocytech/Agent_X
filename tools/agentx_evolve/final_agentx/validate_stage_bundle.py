#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REQUIRED_BUNDLE_FILES = [
    "acceptance_matrix.json",
    "ACCEPTANCE_REVIEW.md",
    "command_transcript.json",
    "evidence_manifest.json",
    "replay_report.json",
    "anti_false_pass_report.json",
    "final_verdict.json",
]

STAGE_MAP = {
    "repo-memory": "repo-memory-mvp",
    "git-promotion": "generated-agent-git-promotion",
}

VALIDATOR_DIR = Path("tools/agentx_evolve/final_agentx")


def _run_validator(script: str, stage: str, report_dir: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_DIR / script), stage],
        capture_output=True, text=True, timeout=30,
    )
    return result


def validate(stage: str) -> list[str]:
    errors: list[str] = []
    dir_name = STAGE_MAP.get(stage, "")
    if not dir_name:
        errors.append(f"Unknown stage: {stage}")
        return errors

    report_dir = Path(f".agentx-init/reports/{dir_name}")

    if not report_dir.exists():
        errors.append(f"Stage report directory not found: {report_dir}")
        return errors

    # Check all required bundle files exist
    for fname in REQUIRED_BUNDLE_FILES:
        fpath = report_dir / fname
        if not fpath.exists():
            errors.append(f"Missing required bundle file: {fname}")

    # Validate command transcript source is recorded
    ct_path = report_dir / "command_transcript.json"
    if ct_path.exists():
        try:
            ct_data = json.loads(ct_path.read_text(encoding="utf-8"))
            if ct_data.get("source") != "recorded":
                errors.append(f"Command transcript source is '{ct_data.get('source')}', expected 'recorded'")
            if not ct_data.get("entries"):
                errors.append("Command transcript has 0 entries")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Invalid command_transcript.json: {e}")

    # Validate replay report fields
    rr_path = report_dir / "replay_report.json"
    if rr_path.exists():
        try:
            rr_data = json.loads(rr_path.read_text(encoding="utf-8"))
            if not rr_data.get("artifact_hashes"):
                errors.append("Replay report missing artifact_hashes")
            for expected_hash in ("acceptance_matrix.json", "final_verdict.json"):
                if expected_hash not in rr_data.get("artifact_hashes", {}):
                    errors.append(f"Replay report missing hash for {expected_hash}")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Invalid replay_report.json: {e}")

    # Validate evidence manifest has refs
    em_path = report_dir / "evidence_manifest.json"
    if em_path.exists():
        try:
            em_data = json.loads(em_path.read_text(encoding="utf-8"))
            if not em_data.get("evidence_refs"):
                errors.append("Evidence manifest has no evidence_refs")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Invalid evidence_manifest.json: {e}")

    # Validate final verdict is PASS
    fv_path = report_dir / "final_verdict.json"
    if fv_path.exists():
        try:
            fv_data = json.loads(fv_path.read_text(encoding="utf-8"))
            if fv_data.get("verdict") not in ("PASS", "PARTIAL"):
                errors.append(f"Final verdict is '{fv_data.get('verdict')}', expected PASS or PARTIAL")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Invalid final_verdict.json: {e}")

    # Validate anti-false-pass report
    afp_path = report_dir / "anti_false_pass_report.json"
    if afp_path.exists():
        try:
            afp_data = json.loads(afp_path.read_text(encoding="utf-8"))
            if not afp_data.get("all_attacks_blocked"):
                errors.append("Anti-false-pass report: not all attacks blocked")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Invalid anti_false_pass_report.json: {e}")

    return errors


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("repo-memory", "git-promotion"):
        print(f"Usage: {sys.argv[0]} <repo-memory|git-promotion>")
        return 1

    errs = validate(stage)
    if errs:
        print(f"VALIDATE STAGE BUNDLE {stage} FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"validate-stage-bundle-{stage}: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
