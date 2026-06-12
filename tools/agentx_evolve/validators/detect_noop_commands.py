"""Detect no-op commands in a transcript.

Item 14.1: Strengthened detection for commands that only simulate success.
"""
import json, sys, os, re

NOOP_PATTERNS = [
    "echo ok", "echo passed", "echo success", "echo done",
    "exit 0", "true", ":", "# noop",
    "python3 -c \"pass\"", "python3 -c 'pass'",
]

NOOP_REGEXES = [
    re.compile(r'echo\s+.*PASS', re.IGNORECASE),
    re.compile(r'make\s+\S+\s*[|&;>]'),
    re.compile(r'^(exit\s+0|true|:)\s*$'),
    re.compile(r'python3\s+-c\s+["\']pass["\']'),
    re.compile(r'pytest.*--collect-only'),  # collecting without running
]


def detect(path):
    issues = []
    with open(path) as f:
        data = json.load(f) if path.endswith(".json") else []
    if isinstance(data, dict):
        data = [data]
    for i, entry in enumerate(data):
        cmd = entry.get("command", "")
        exit_code = entry.get("exit_code", -1)
        stdout = entry.get("stdout", "")
        stderr = entry.get("stderr", "")

        for pat in NOOP_PATTERNS:
            if pat in cmd.lower():
                issues.append(f"Entry {i}: possible no-op command: {cmd}")
                break
        else:
            for regex in NOOP_REGEXES:
                if regex.search(cmd):
                    issues.append(f"Entry {i}: regex-matched no-op command: {cmd}")
                    break

        # Detect commands that always return zero without evidence of real work
        if exit_code == 0 and not stdout.strip() and not stderr.strip():
            if "copy" not in cmd and "mv" not in cmd and "compileall" not in cmd:
                issues.append(f"Entry {i}: exit_code=0 with empty output: {cmd}")

    return issues


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/baseline/baseline_command_transcript.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found — command transcript is a mandatory proof artifact"); sys.exit(1)
    issues = detect(path)
    if issues:
        print(f"ISSUES: {len(issues)} no-op command(s):"); [print(f"  - {i}") for i in issues]
    else:
        print(f"PASS: no no-op commands in {path}")


if __name__ == "__main__":
    main()
