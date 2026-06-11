#!/usr/bin/env python3
import json, sys, os, hashlib, platform

REQUIRED_FIELDS = [
    "replay_id", "verdict", "source_commit",
    "commands", "environment", "artifact_hashes",
    "diff_summary", "verified_at",
]

VALID_VERDICTS = {"PASS", "FAIL", "PARTIAL"}

MIN_COMMANDS = 3
MIN_ARTIFACT_HASHES = 3
ENV_KEYS = {"os_type", "python_version", "git_commit"}
DIFF_KEYS = {"clean", "expected_diffs", "unexplained_diffs"}


def validate(path):
    errors = []
    with open(path) as f:
        data = json.load(f)

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing field: {field}")

    verdict = data.get("verdict", "")
    if verdict not in VALID_VERDICTS:
        errors.append(f"verdict '{verdict}' not in {VALID_VERDICTS}")

    commands = data.get("commands", [])
    if not isinstance(commands, list):
        errors.append("commands must be a list")
    elif len(commands) < MIN_COMMANDS:
        errors.append(f"Too few commands ({len(commands)}), min {MIN_COMMANDS}")
    else:
        for i, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                errors.append(f"commands[{i}] must be a dict")
                continue
            for key in ("command", "exit_code"):
                if key not in cmd:
                    errors.append(f"commands[{i}] missing '{key}'")
            exit_code = cmd.get("exit_code")
            if exit_code is not None and exit_code != 0:
                errors.append(f"commands[{i}] has non-zero exit code ({exit_code})")

    env = data.get("environment", {})
    for key in ENV_KEYS:
        if key not in env:
            errors.append(f"environment missing '{key}'")
    if env.get("python_version"):
        parts = env["python_version"].split(".")
        if len(parts) < 2:
            errors.append(f"python_version malformed: {env['python_version']}")

    hashes = data.get("artifact_hashes", {})
    if not isinstance(hashes, dict):
        errors.append("artifact_hashes must be a dict")
    elif len(hashes) < MIN_ARTIFACT_HASHES:
        errors.append(f"Too few artifact hashes ({len(hashes)}), min {MIN_ARTIFACT_HASHES}")

    diff = data.get("diff_summary", {})
    for key in DIFF_KEYS:
        if key not in diff:
            errors.append(f"diff_summary missing '{key}'")
    if "clean" not in diff:
        errors.append("diff_summary missing 'clean'")
    if "unexplained_diffs" not in diff:
        errors.append("diff_summary missing 'unexplained_diffs'")
    if "expected_diffs" not in diff:
        errors.append("diff_summary missing 'expected_diffs'")

    if not data.get("verified_at"):
        errors.append("verified_at is empty or missing")

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/final/five_document_clean_checkout_replay.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found"); sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} error(s)"); [print(f"  - {e}") for e in errors]
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    print(f"PASS: {path} validates ({len(data.get('commands',[]))} commands, "
          f"{len(data.get('artifact_hashes',{}))} hashes, "
          f"verdict={data.get('verdict')})")


if __name__ == "__main__":
    main()
