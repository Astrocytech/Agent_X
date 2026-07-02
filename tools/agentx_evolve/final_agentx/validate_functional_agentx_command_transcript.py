#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import get_run_id, get_git_commit

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")

MANDATORY_COMMANDS = [
    "make prove-functional-runtime-mvp",
    "make prove-agentx-adapter-mvp",
    "make prove-functional-agent-evolution-alpha",
    "make prove-functional-agent-evolution-beta",
    "make prove-governed-self-evolution-prototype",
    "make prove-agentx-repo-memory-mvp",
    "make prove-agentx-generated-agent-git-promotion",
    "make prove-functional-agentx",
]


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "command_transcript.json"
    if not path.exists():
        errors.append(f"command_transcript.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("command_transcript.json must be a JSON object")
        return errors

    if data.get("schema_version") != "1.0":
        errors.append(f"schema_version expected '1.0', got {data.get('schema_version')}")

    if data.get("artifact_type") != "command_transcript":
        errors.append("artifact_type must be 'command_transcript'")

    source = data.get("source", "")
    if source != "recorded":
        errors.append(f"Command transcript source is '{source}', expected 'recorded'")

    transcript_run_id = data.get("run_id", "")
    transcript_commit = data.get("git_commit", "")
    current_run_id = get_run_id()
    current_commit = get_git_commit()
    if transcript_run_id and transcript_run_id != current_run_id:
        errors.append(f"Command transcript run_id '{transcript_run_id}' does not match current run '{current_run_id}'")
    if transcript_commit and transcript_commit != current_commit:
        errors.append(f"Command transcript git_commit '{transcript_commit}' does not match current '{current_commit}'")

    entries = data.get("entries", [])
    if not entries:
        errors.append("Command transcript has 0 entries")

    for i, entry in enumerate(entries):
        cmd = entry.get("command", "")
        if not cmd:
            errors.append(f"Entry {i} has empty command")

        argv = entry.get("argv")
        if not argv or not isinstance(argv, list):
            errors.append(f"Entry {i} missing or invalid argv array")

        cwd = entry.get("cwd", "")
        if not cwd:
            errors.append(f"Entry {i} missing cwd")

        exit_code = entry.get("exit_code")
        if exit_code is None:
            errors.append(f"Entry {i} missing exit_code")

        stdout_hash = entry.get("stdout_hash")
        stderr_hash = entry.get("stderr_hash")
        if not stdout_hash:
            errors.append(f"Entry {i} missing stdout_hash")
        if not stderr_hash:
            errors.append(f"Entry {i} missing stderr_hash")

        stdout_log = entry.get("stdout_log")
        stderr_log = entry.get("stderr_log")
        if stdout_log:
            log_path = Path(stdout_log)
            if log_path.exists():
                actual_hash = hashlib.sha256(log_path.read_bytes()).hexdigest()
                if stdout_hash and actual_hash != stdout_hash:
                    errors.append(f"Entry {i} stdout_hash mismatch with log file {stdout_log}")
            else:
                errors.append(f"Entry {i} stdout_log '{stdout_log}' not found")
        if stderr_log:
            log_path = Path(stderr_log)
            if log_path.exists():
                actual_hash = hashlib.sha256(log_path.read_bytes()).hexdigest()
                if stderr_hash and actual_hash != stderr_hash:
                    errors.append(f"Entry {i} stderr_hash mismatch with log file {stderr_log}")
            else:
                errors.append(f"Entry {i} stderr_log '{stderr_log}' not found")

        if "mandatory" not in entry:
            errors.append(f"Entry {i} missing mandatory flag")

    # Check mandatory command coverage
    entry_commands = [e.get("command", "") for e in entries]
    for mandatory in MANDATORY_COMMANDS:
        found = False
        for cmd in entry_commands:
            if mandatory in cmd:
                found = True
                break
        if not found:
            errors.append(f"Mandatory proof command not found in transcript: '{mandatory}'")

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_command_transcript",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_command_transcript.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE COMMAND TRANSCRIPT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-command-transcript: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
