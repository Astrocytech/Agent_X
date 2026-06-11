#!/usr/bin/env python3
import sys, os, subprocess

RUNTIME_ARTIFACTS_DIR = os.path.join("tools", "agentx_evolve", "runtime_artifacts")
RUNTIME_PATTERNS = [".coverage", ".mypy_cache", ".ruff_cache", "__pycache__"]
RUNTIME_FILE_EXTENSIONS = [".pyc", ".pyo"]
KNOWN_RUNTIME_GIT_PATTERNS = ["__pycache__", ".coverage", ".mypy_cache", ".ruff_cache", ".pytest_cache"]
SOURCE_DIRS = [
    "tools/agentx_evolve",
    "L0",
    "L1",
    "L2",
    "tests",
    "benchmarks",
    "reports",
    "schemas",
    "examples",
    "umbrella_agent",
    "docs",
]

def check_init_py():
    init = os.path.join(RUNTIME_ARTIFACTS_DIR, "__init__.py")
    if not os.path.isfile(init):
        return [f"'{init}' not found"]
    return []

def check_source_dirs_for_artifacts():
    errors = []
    for sdir in SOURCE_DIRS:
        if not os.path.isdir(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__",)]
            # Skip evidence and bootstrap dirs (log files are expected there)
            if "/evidence/" in root or "/bootstrap/" in root or root.endswith("/evidence") or root.endswith("/bootstrap"):
                continue
            for pattern in RUNTIME_PATTERNS:
                if os.path.basename(root) == pattern:
                    rel = os.path.relpath(root)
                    errors.append(f"Runtime artifact directory '{rel}' found in source tree")
                for f in files:
                    if f == pattern:
                        rel = os.path.relpath(os.path.join(root, f))
                        errors.append(f"Runtime artifact file '{rel}' found in source tree")
                    # Check runtime file extensions
                    if any(f.endswith(ext) for ext in RUNTIME_FILE_EXTENSIONS):
                        rel = os.path.relpath(os.path.join(root, f))
                        errors.append(f"Runtime artifact file '{rel}' found in source tree")
    return errors

def check_git_tracked_runtime():
    errors = []
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, timeout=30, check=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            for pattern in KNOWN_RUNTIME_GIT_PATTERNS:
                if pattern in line and "__init__" not in line:
                    errors.append(f"Runtime artifact '{line}' is tracked in git")
    except (subprocess.SubprocessError, FileNotFoundError):
        errors.append("Could not run git ls-files (not a git repo?)")
    return errors

def check_temp_generated_files():
    errors = []
    for sdir in SOURCE_DIRS:
        if not os.path.isdir(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__",)]
            # Skip evidence and bootstrap dirs (log files are expected there)
            if "/evidence/" in root or "/bootstrap/" in root or root.endswith("/evidence") or root.endswith("/bootstrap"):
                continue
            for f in files:
                if f.endswith(".pyc") or f.endswith(".pyo") or f.endswith(".tmp") or f.endswith(".log"):
                    rel = os.path.relpath(os.path.join(root, f))
                    errors.append(f"Generated/temp file '{rel}' found in source tree")
    return errors

def main():
    errors = []

    if not os.path.isdir(RUNTIME_ARTIFACTS_DIR):
        errors.append(f"Runtime artifacts directory '{RUNTIME_ARTIFACTS_DIR}' does not exist")
    else:
        errors.extend(check_init_py())

    errors.extend(check_source_dirs_for_artifacts())
    errors.extend(check_git_tracked_runtime())
    errors.extend(check_temp_generated_files())

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: runtime artifact boundary validated")
    sys.exit(0)

if __name__ == "__main__":
    main()
