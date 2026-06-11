#!/usr/bin/env python3
import json, os, sys, subprocess

RUN_MANIFEST_FILE = os.path.join(".agentx-init", "reports", "final_project_run_manifest.json")

REQUIRED_FIELDS = [
    "project", "repository_url", "run_id", "commit_before", "commit_after",
    "milestones", "commands", "artifacts", "schemas", "evidence",
    "event_logs", "replay_reports", "final_claims", "forbidden_claim_scan_path",
    "final_verdict",
]

MIN_TEST_COUNT = 2000
MIN_EVIDENCE_PATHS = 10
MIN_COMMAND_ENTRIES = 5


def _scan_test_count() -> int:
    count = 0
    search_dirs = ["tests", "L0", "L1", "L2", "tools"]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for fname in files:
                if fname.startswith("test_") and fname.endswith(".py"):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath) as f:
                            content = f.read()
                        count += content.count("def test_")
                    except (OSError, UnicodeDecodeError):
                        pass
    return count


def main():
    if not os.path.isfile(RUN_MANIFEST_FILE):
        print(f"FAIL: Run manifest '{RUN_MANIFEST_FILE}' not found")
        sys.exit(1)

    try:
        with open(RUN_MANIFEST_FILE) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: '{RUN_MANIFEST_FILE}' invalid JSON: {e}")
        sys.exit(1)

    errors = []

    # 1. Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Required field '{field}' missing from run manifest")

    # 2. Final verdict must be meaningful
    final_verdict = data.get("final_verdict", "")
    if not final_verdict:
        errors.append("final_verdict is empty or missing")
    elif len(final_verdict) < 10:
        errors.append(f"final_verdict too short ({len(final_verdict)} chars) — must include justification")
    elif "PASS" not in final_verdict.upper() and "FAIL" not in final_verdict.upper():
        errors.append("final_verdict must contain PASS or FAIL verdict keyword")

    # 3. Command exit-code cross-check
    commands = data.get("commands", [])
    if not isinstance(commands, list):
        errors.append("'commands' must be a list")
    else:
        if len(commands) < MIN_COMMAND_ENTRIES:
            errors.append(f"Too few command entries ({len(commands)}), min {MIN_COMMAND_ENTRIES}")
        for i, cmd in enumerate(commands):
            if isinstance(cmd, dict):
                exit_code = cmd.get("exit_code")
                if exit_code is None:
                    errors.append(f"commands[{i}] missing 'exit_code'")
                elif exit_code != 0:
                    errors.append(f"commands[{i}] has non-zero exit code ({exit_code})")
            elif isinstance(cmd, str):
                errors.append(f"commands[{i}] is a string, expected dict with exit_code")

    # 4. Test-count validation
    actual_test_count = _scan_test_count()
    if actual_test_count < MIN_TEST_COUNT:
        errors.append(f"Test count too low ({actual_test_count}), minimum {MIN_TEST_COUNT}")

    # 5. Proof-of-evidence: referenced paths must exist
    for list_field in ["artifacts", "schemas", "evidence", "event_logs", "replay_reports", "final_claims"]:
        value = data.get(list_field, [])
        if isinstance(value, list):
            found_valid = 0
            for item in value:
                if isinstance(item, str) and item.startswith((".", "/")):
                    if os.path.exists(item):
                        found_valid += 1
                elif isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str) and (v.startswith(".") or v.startswith("/")):
                            if os.path.exists(v):
                                found_valid += 1
            if list_field in ("evidence", "artifacts") and found_valid < MIN_EVIDENCE_PATHS:
                errors.append(f"'{list_field}' has no existing paths (need >= {MIN_EVIDENCE_PATHS})")

    # 6. forbidden_claim_scan_path must exist
    scan_path = data.get("forbidden_claim_scan_path", "")
    if scan_path and not os.path.exists(scan_path):
        errors.append(f"forbidden_claim_scan_path '{scan_path}' does not exist")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    print(f"PASS: run manifest '{RUN_MANIFEST_FILE}' validates — {len(commands)} commands OK, "
          f"{actual_test_count} tests found, verdict: {final_verdict[:60]}")
    sys.exit(0)


if __name__ == "__main__":
    main()
