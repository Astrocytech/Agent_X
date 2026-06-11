"""Regenerate .md transcript files from the final .json command transcript.
Called by the Makefile after all commands have been recorded.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")


def regenerate(filename_base: str) -> None:
    json_path = REPORT_DIR / f"{filename_base}.json"
    md_path = REPORT_DIR / f"{filename_base}.md"
    if not json_path.exists():
        print(f"Transcript JSON not found: {json_path}", file=sys.stderr)
        return
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        data = data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return

    lines = [
        f"# Functional Runtime MVP \u2014 Command Transcript",
        "",
        f"| # | Command | Exit Code | Summary |",
        f"|---|---|---|---|",
    ]
    for i, cmd in enumerate(data):
        summary = (cmd.get("stdout_summary") or "")[:100]
        lines.append(
            f"| {i + 1} | `{cmd.get('command', '')}` | {cmd.get('exit_code', '')} "
            f"| {summary} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Regenerated {md_path} ({len(data)} commands)")


if __name__ == "__main__":
    regenerate("functional_runtime_mvp_command_transcript")
    regenerate("functional_runtime_mvp_baseline_command_transcript")
