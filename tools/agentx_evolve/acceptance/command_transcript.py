from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentx_evolve.acceptance.proof_result import CommandResult


REPORT_DIR = Path(".agentx-init/reports")


def _git_commit(cwd: str = ".") -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _git_branch(cwd: str = ".") -> str:
    try:
        r = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _environment() -> str:
    return f"Python {sys.version.split()[0]}, {platform.platform()}"


def _compute_provenance_id(cmd: str, exit_code: int, stdout_hash: str,
                           stderr_hash: str, timestamp: str,
                           git_commit: str, working_dir: str) -> str:
    import hashlib
    fields = [
        cmd,
        str(exit_code),
        stdout_hash,
        stderr_hash,
        timestamp,
        git_commit,
        working_dir,
    ]
    return hashlib.sha256("|".join(fields).encode()).hexdigest()


def run_command(
    command: str,
    cwd: str = ".",
    timeout_seconds: int = 600,
    env: dict[str, str] | None = None,
) -> CommandResult:
    import hashlib
    git_commit = _git_commit(cwd)
    branch = _git_branch(cwd)
    environment = _environment()
    timestamp = datetime.now(timezone.utc).isoformat()
    working_dir = str(Path(cwd).resolve())

    start = time.time()
    try:
        r = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=timeout_seconds, env=env,
        )
        exit_code = r.returncode
        stdout_summary = r.stdout.strip()[:500] if r.stdout else ""
        stderr_summary = r.stderr.strip()[:500] if r.stderr else ""
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout_summary = ""
        stderr_summary = f"TIMEOUT after {timeout_seconds}s"
    except Exception as e:
        exit_code = -1
        stdout_summary = ""
        stderr_summary = str(e)[:500]
    duration = round(time.time() - start, 3)

    stdout_hash = hashlib.sha256((stdout_summary or "").encode()).hexdigest()
    stderr_hash = hashlib.sha256((stderr_summary or "").encode()).hexdigest()
    provenance_id = _compute_provenance_id(
        command, exit_code, stdout_hash, stderr_hash,
        timestamp, git_commit, working_dir,
    )

    return CommandResult(
        command=command,
        exit_code=exit_code,
        stdout_summary=stdout_summary,
        stderr_summary=stderr_summary,
        timestamp=timestamp,
        duration_seconds=duration,
        git_commit=git_commit,
        branch=branch,
        environment=environment,
        source="subprocess",
        provenance_id=provenance_id,
        stdout_hash=stdout_hash,
        stderr_hash=stderr_hash,
        working_directory=working_dir,
        recorded_by="command_transcript.run_command",
        source_detail=f"command_transcript.run_command at {timestamp}",
    )


def write_transcript(
    commands: list[CommandResult],
    filename_base: str = "functional_runtime_mvp_command_transcript",
    output_dir: Path = REPORT_DIR,
) -> tuple[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"{filename_base}.md"
    js_path = output_dir / f"{filename_base}.json"

    git_commit = _git_commit()
    environment = _environment()

    md_lines = [
        f"# Functional Runtime MVP \u2014 Command Transcript",
        "",
        f"**Git commit**: {git_commit}",
        f"**Environment**: {environment}",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| # | Command | Exit Code | Summary |",
        "|---|---|---|---|",
    ]
    for i, cmd in enumerate(commands):
        md_lines.append(
            f"| {i + 1} | `{cmd.command}` | {cmd.exit_code} "
            f"| {cmd.stdout_summary[:100]} |"
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    js_path.write_text(
        json.dumps([c.to_dict() for c in commands], indent=2),
        encoding="utf-8",
    )
    return str(md_path), str(js_path)
