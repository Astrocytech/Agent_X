#!/usr/bin/env python3
import json, sys, os, subprocess

DEPENDENCY_REPORT = os.path.join(".agentx-init", "reports", "final_project_dependency_change_report.json")
DEPENDENCY_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
]

def get_untracked_and_modified():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=30, check=True
        )
        changed = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            status = line[:2]
            filepath = line[3:]
            for dep_file in DEPENDENCY_FILES:
                if filepath.rstrip("/") == dep_file or filepath.endswith("/" + dep_file):
                    if status != "??":
                        changed.append(filepath)
        return changed
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return [f"git error: {e}"]

def main():
    if not os.path.isfile(DEPENDENCY_REPORT):
        print(f"FAIL: Dependency change report '{DEPENDENCY_REPORT}' not found")
        sys.exit(1)

    try:
        with open(DEPENDENCY_REPORT) as f:
            data = json.load(f)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"FAIL: '{DEPENDENCY_REPORT}' invalid JSON: {e}")
        sys.exit(1)

    verdict = data.get("verdict", data.get("dependency_verdict", ""))
    if verdict == "NO_DEPENDENCY_CHANGES":
        print(f"PASS: Report declares NO_DEPENDENCY_CHANGES")
        sys.exit(0)

    changed = get_untracked_and_modified()
    if isinstance(changed, list) and all(isinstance(x, str) for x in changed):
        if changed:
            for c in changed:
                print(f"FAIL: Dependency file '{c}' has uncommitted changes")
            sys.exit(1)

    print(f"PASS: '{DEPENDENCY_REPORT}' validates, no dependency changes detected")
    sys.exit(0)

if __name__ == "__main__":
    main()
