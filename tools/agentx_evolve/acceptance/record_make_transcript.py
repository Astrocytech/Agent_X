"""Record commands from make prove-functional-runtime-mvp in the transcript.

Called by the Makefile after each command group to append real subprocess
results to the run transcript.  Reads a pipe-delimited spec, runs the command,
appends the result, and writes the final transcript.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.acceptance.command_transcript import run_command, write_transcript

REPORT_DIR = Path(".agentx-init/reports")


def append_command(command: str, timeout: int = 600) -> None:
    result = run_command(command, timeout_seconds=timeout)
    transcript_path = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
    existing = []
    if transcript_path.exists():
        try:
            existing = json.loads(transcript_path.read_text(encoding="utf-8"))
            existing = existing if isinstance(existing, list) else []
        except (OSError, json.JSONDecodeError):
            existing = []
    existing.append(result.to_dict())
    write_transcript(
        [type("", (), {"to_dict": lambda self, d=cmd: d})() for cmd in existing],
        # We need to reconstruct CommandResult objects, so just use dicts
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: record_make_transcript.py <command>")
        sys.exit(1)
    append_command(sys.argv[1])
