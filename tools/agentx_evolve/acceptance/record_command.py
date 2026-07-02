"""Append a real command result to the command transcript.
Called by the Makefile for each step in prove-functional-runtime-mvp.

Usage:
    python3 record_command.py -- <command>
    
Runs <command> as a subprocess with the standard PYTHONPATH, appends
its CommandResult to .agentx-init/reports/command_transcript.json,
and exits with the command's exit code.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORT_DIR = _PROJECT_ROOT / ".agentx-init/reports"
TRANSCRIPT_PATH = REPORT_DIR / "functional_runtime_mvp_command_transcript.json"
LOG_DIR = REPORT_DIR / "logs"
# Debug alternate path to detect overwrites
DEB_PATH = REPORT_DIR / "record_command_debug.ndjson"


def _git_commit_full() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _environment() -> str:
    import platform
    return f"Python {sys.version.split()[0]}, {platform.platform()}"


def _next_command_index() -> int:
    if TRANSCRIPT_PATH.exists():
        try:
            existing = json.loads(TRANSCRIPT_PATH.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                return len(existing)
        except (OSError, json.JSONDecodeError):
            pass
    return 0


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


def append_command(cmd: str, exit_code: int, stdout_full: str,
                    stderr_full: str, duration: float) -> None:
    import hashlib
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cmd_index = _next_command_index()
    stdout_hash = hashlib.sha256((stdout_full or "").encode()).hexdigest()
    stderr_hash = hashlib.sha256((stderr_full or "").encode()).hexdigest()
    timestamp = datetime.now(timezone.utc).isoformat()
    full_git_commit = _git_commit_full()
    working_dir = str(Path.cwd())
    provenance_id = _compute_provenance_id(
        cmd, exit_code, stdout_hash, stderr_hash,
        timestamp, full_git_commit, working_dir,
    )
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stdout_log = LOG_DIR / f"stdout_{cmd_index:04d}.log"
    stderr_log = LOG_DIR / f"stderr_{cmd_index:04d}.log"
    # Store full output for hash verification (item 49-50)
    stdout_log.write_text(stdout_full or "", encoding="utf-8")
    stderr_log.write_text(stderr_full or "", encoding="utf-8")
    entry = {
        "command": cmd,
        "exit_code": exit_code,
        "stdout_summary": stdout_full[:500] if stdout_full else "",
        "stderr_summary": stderr_full[:500] if stderr_full else "",
        "stdout_log": str(stdout_log.relative_to(REPORT_DIR)),
        "stderr_log": str(stderr_log.relative_to(REPORT_DIR)),
        "cmd_index": cmd_index,
        "timestamp": timestamp,
        "duration_seconds": round(duration, 3),
        "git_commit": full_git_commit,
        "working_directory": working_dir,
        "environment": _environment(),
        "source": "subprocess",
        "recorded_by": "record_command.py",
        "source_detail": f"record_command.py at {timestamp}",
        "provenance_id": provenance_id,
        "stdout_hash": stdout_hash,
        "stderr_hash": stderr_hash,
    }
    existing = []
    if TRANSCRIPT_PATH.exists():
        try:
            existing = json.loads(TRANSCRIPT_PATH.read_text(encoding="utf-8"))
            existing = existing if isinstance(existing, list) else []
        except (OSError, json.JSONDecodeError):
            existing = []
    existing.append(entry)
    TRANSCRIPT_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    # Append to debug NDJSON (with full entry)
    import io
    with open(str(DEB_PATH), "a") as fdeb:
        record = {"_cmd_was": cmd, "_ec": exit_code, "_path": str(TRANSCRIPT_PATH), "_entry": entry}
        fdeb.write(json.dumps(record) + "\n")


def _pop_env_prefix(args: list[str]) -> dict[str, str]:
    """Extract leading KEY=value tokens as environment overrides."""
    env_updates: dict[str, str] = {}
    while args and "=" in args[0] and not args[0].startswith("-"):
        k, _, v = args.pop(0).partition("=")
        env_updates[k] = v.strip("\"'")
    return env_updates


def main() -> int:
    if len(sys.argv) < 1:
        print("Usage: record_command.py -- <command>", file=sys.stderr)
        return 1
    if len(sys.argv) >= 2 and sys.argv[1] == "--":
        command_args = sys.argv[2:]
    else:
        command_args = sys.argv[1:]
    orig_args = list(command_args)
    env_updates = _pop_env_prefix(command_args)
    command_str = " ".join(orig_args)

    start = time.time()
    env = os.environ.copy()
    env.update(env_updates)
    try:
        r = subprocess.run(
            command_args, capture_output=True, text=True,
            timeout=3600, env=env,
        )
        exit_code = r.returncode
        stdout_summary = r.stdout or ""
        stderr_summary = r.stderr or ""
    except subprocess.TimeoutExpired:
        exit_code = -1
        stdout_summary = ""
        stderr_summary = "TIMEOUT after 3600s"
    except Exception as e:
        exit_code = -1
        stdout_summary = ""
        stderr_summary = str(e)[:500]
    if stdout_summary:
        print(stdout_summary, end="")
    if stderr_summary:
        print(stderr_summary, end="", file=sys.stderr)
    duration = time.time() - start
    append_command(command_str, exit_code, stdout_summary, stderr_summary, duration)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
