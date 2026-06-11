#!/usr/bin/env python3
import os, re, sys

CRITICAL_SCRIPTS = [
    "scripts/prove-umbrella-agent.sh",
    "scripts/prove-post-umbrella.sh",
    "scripts/prove-inverse-science.sh",
    "scripts/prove-scriptor-benchmark.sh",
    "tools/agentx_evolve/final_acceptance/generate_artifacts.py",
    "tools/agentx_evolve/inverse_science/cli.py",
    "tools/agentx_evolve/umbrella/run_stage_b.py",
    "tools/agentx_evolve/umbrella/validate_stage_b.py",
    "Makefile",
]

MIN_LOGICAL_LINES = 50
MIN_FUNCTIONS = 1


def logical_lines(path: str) -> int:
    count = 0
    with open(path, errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
                count += 1
    return count


FUNCTION_REGEXES = [
    re.compile(r'^def\s+\w+\s*\('),          # Python: def func(
    re.compile(r'^class\s+\w+'),              # Python: class ClassName
    re.compile(r'^function\s+\w+'),           # Bash: function name
    re.compile(r'^\w[\w-]*\s*\(\s*\)\s*\{'), # Bash: name() {
    re.compile(r'^[\w-]+:'),                   # Makefile: target:
]


def function_count(path: str) -> int:
    count = 0
    with open(path, errors="replace") as f:
        for line in f:
            stripped = line.strip()
            for regex in FUNCTION_REGEXES:
                if regex.match(stripped):
                    count += 1
                    break
    return count


def has_real_logic(path: str) -> bool:
    with open(path, errors="replace") as f:
        content = f.read()
    indicators = ["assert ", "exit ", "test ", "pytest", "sys.exit", "raise ", "PASS", "FAIL"]
    return any(ind in content for ind in indicators)


def main() -> None:
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    errors = []
    for rel_path in CRITICAL_SCRIPTS:
        full = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full):
            errors.append(f"MISSING: {rel_path}")
            continue
        ll = logical_lines(full)
        if ll < MIN_LOGICAL_LINES:
            errors.append(f"{rel_path}: only {ll} logical lines (min {MIN_LOGICAL_LINES})")
        fc = function_count(full)
        if fc < MIN_FUNCTIONS:
            errors.append(f"{rel_path}: only {fc} function/class definitions (min {MIN_FUNCTIONS})")
        if not has_real_logic(full):
            errors.append(f"{rel_path}: no real logic indicators (assert/exit/test/PASS/FAIL)")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print(f"PASS: All {len(CRITICAL_SCRIPTS)} critical scripts are substantial ({MIN_LOGICAL_LINES}+ logical lines, {MIN_FUNCTIONS}+ definitions, real logic)")
    sys.exit(0)


if __name__ == "__main__":
    main()
