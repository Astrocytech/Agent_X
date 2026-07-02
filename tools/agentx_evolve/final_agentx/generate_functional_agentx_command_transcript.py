#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, atomic_write_json, get_git_commit, get_run_id, load_json

RECORDER_TRANSCRIPT = Path(".agentx-init/reports/functional_runtime_mvp_command_transcript.json")


def generate_transcript() -> dict:
    run_id = get_run_id()
    git_commit = get_git_commit()

    recorded = load_json(RECORDER_TRANSCRIPT)
    if recorded and isinstance(recorded, list) and len(recorded) > 0:
        entries: list[dict] = []
        for rec in recorded:
            command_str = rec.get("command", "UNKNOWN")
            argv = rec.get("argv")
            if not argv:
                argv = command_str.split()
            entries.append({
                "command": command_str,
                "argv": argv,
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

        transcript = {
            "schema_version": "1.0",
            "artifact_type": "command_transcript",
            "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_command_transcript.py",
            "run_id": run_id,
            "git_commit": git_commit,
            "source": "recorded",
            "recorder_transcript": str(RECORDER_TRANSCRIPT),
            "total_commands": len(entries),
            "passed": sum(1 for e in entries if e["exit_code"] == 0),
            "failed": sum(1 for e in entries if e["exit_code"] != 0),
            "entries": entries,
        }
        return transcript

    # Fallback: no recorder transcript found — fail immediately
    print(f"ERROR: Recorder transcript not found at {RECORDER_TRANSCRIPT}", file=sys.stderr)
    print("Run with FUNCTIONAL_AGENTX_REC=1 to record commands", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    transcript = generate_transcript()

    json_path = REPORT_BASE / "command_transcript.json"
    atomic_write_json(json_path, transcript)

    md_lines = [
        "# Functional Agent_X Command Transcript\n",
        f"Run ID: {transcript['run_id']}  \n",
        f"Source: {transcript.get('source', 'unknown')}  \n",
        f"Total commands: {transcript['total_commands']}  \n",
        f"Passed: {transcript['passed']}  \n",
        f"Failed: {transcript['failed']}\n",
        "",
        "| Command | Exit Code | Mandatory | Failure Reason |",
        "|---------|-----------|-----------|----------------|",
    ]
    for e in transcript["entries"]:
        reason = e.get("failure_reason", "") or ""
        md_lines.append(f"| `{e['command'][:80]}` | {e['exit_code']} | {e['mandatory']} | {reason} |")

    if transcript["total_commands"] == 0:
        md_lines.append("")
        md_lines.append("*No recorded commands found.*")

    md_path = REPORT_BASE / "COMMAND_TRANSCRIPT.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Command transcript written to {json_path} ({transcript['total_commands']} entries, source: {transcript.get('source', 'unknown')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
