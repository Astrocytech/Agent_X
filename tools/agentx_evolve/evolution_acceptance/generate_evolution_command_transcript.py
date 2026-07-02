#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

RECORDER_PATH = Path(".agentx-init/reports/functional_runtime_mvp_command_transcript.json")

STAGE_COMMAND_SUBSTRINGS = {
    "alpha": [
        "evolution_acceptance/",
    ],
    "beta": [
        "evolution_acceptance/",
    ],
    "governed": [
        "evolution_acceptance/",
        "governed-self-evolution/",
    ],
}

STAGE_REPORT_DIRS = {
    "alpha": "agent-evolution-alpha",
    "beta": "agent-evolution-beta",
    "governed": "governed-self-evolution",
}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_git_commit() -> str:
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        return "UNKNOWN"


def generate_transcript(stage: str) -> dict:
    git_commit = get_git_commit()
    expected_substrings = STAGE_COMMAND_SUBSTRINGS.get(stage, [])

    recorded = load_json(RECORDER_PATH)
    if recorded and isinstance(recorded, list) and len(recorded) > 0:
        entries: list[dict] = []
        for rec in recorded:
            cmd = rec.get("command", "")
            if any(s in cmd for s in expected_substrings):
                entries.append({
                    "command": cmd,
                    "cwd": rec.get("working_directory", "."),
                    "env_redaction_status": "RECORDED",
                    "start_time": rec.get("timestamp", ""),
                    "end_time": rec.get("timestamp", ""),
                    "exit_code": rec.get("exit_code", -1),
                    "stdout_hash": rec.get("stdout_hash"),
                    "stderr_hash": rec.get("stderr_hash"),
                    "stdout_log": rec.get("stdout_log"),
                    "stderr_log": rec.get("stderr_log"),
                    "mandatory": True,
                    "failure_allowed": False,
                    "failure_reason": None if rec.get("exit_code", 0) == 0 else f"Exit code {rec.get('exit_code')}",
                    "provenance_id": rec.get("provenance_id"),
                })

        return {
            "schema_version": "1.0",
            "artifact_type": f"evolution_command_transcript_{stage}",
            "producer": "tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py",
            "stage": stage,
            "git_commit": git_commit,
            "source": "recorded",
            "total_commands": len(entries),
            "passed": sum(1 for e in entries if e["exit_code"] == 0),
            "failed": sum(1 for e in entries if e["exit_code"] != 0),
            "entries": entries,
        }

    return {
        "schema_version": "1.0",
        "artifact_type": f"evolution_command_transcript_{stage}",
        "producer": "tools/agentx_evolve/evolution_acceptance/generate_evolution_command_transcript.py",
        "stage": stage,
        "git_commit": git_commit,
        "source": "no_recorder_fallback",
        "total_commands": 0,
        "passed": 0,
        "failed": 0,
        "entries": [],
        "warning": "No recorder transcript found; transcript is empty",
    }


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    report_dir = Path(f".agentx-init/reports/{STAGE_REPORT_DIRS[stage]}")
    report_dir.mkdir(parents=True, exist_ok=True)

    transcript = generate_transcript(stage)
    out_path = report_dir / "command_transcript.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(transcript, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evolution {stage} command transcript written to {out_path} ({transcript['total_commands']} entries, source: {transcript.get('source', 'unknown')})")
    if transcript["total_commands"] == 0:
        print(f"  WARNING: No recorded commands found. Run with FUNCTIONAL_AGENTX_REC enabled.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
