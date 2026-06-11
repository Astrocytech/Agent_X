#!/usr/bin/env python3
import sys, os, subprocess

L0_CODE_DIR = os.path.join("L0", "CODE")
L0_TESTS_DIR = os.path.join("L0", "tests")
SEED_L0_DIR = os.path.join("L0", "tests", "seed_l0")
SOURCE_SCAN_DIRS = ["L1", "L2", "tools", "tests"]

FORBIDDEN_IMPORT_PATTERNS = [
    "from L0.",
    "import L0.",
    "import L0",  # bare L0
]

SCAFFOLD_ONLY_PATTERNS = ["scaffold", "template", "placeholder", "TODO", "FIXME"]

def count_test_functions_in_dir(dirpath):
    total = 0
    if not os.path.isdir(dirpath):
        return 0
    for root, dirs, files in os.walk(dirpath):
        dirs[:] = [d for d in dirs if not d.startswith("__")]
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath, errors="replace") as fh:
                    for line in fh:
                        stripped = line.strip()
                        if stripped.startswith("def test_") and stripped.endswith(":"):
                            total += 1
    return total

def check_mutation_intent_imports():
    errors = []
    for sdir in SOURCE_SCAN_DIRS:
        if not os.path.isdir(sdir):
            continue
        for root, dirs, files in os.walk(sdir):
            dirs[:] = [d for d in dirs if not d.startswith("__") and d not in ("__pycache__", "validators")]
            for f in files:
                if f.endswith(".py"):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath) as fh:
                            content = fh.read()
                    except Exception:
                        continue
                    for pattern in FORBIDDEN_IMPORT_PATTERNS:
                        if pattern in content:
                            rel = os.path.relpath(fpath)
                            idx = content.find(pattern)
                            line_num = content[:idx].count("\n") + 1
                            errors.append(f"{rel}:{line_num} imports L0 with potential mutation intent")
    return errors

def check_scaffold_only():
    errors = []
    if not os.path.isdir(L0_CODE_DIR):
        return ["L0/CODE directory not found"]
    for root, dirs, files in os.walk(L0_CODE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith("__") and d not in ("__pycache__",)]
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath) as fh:
                        content = fh.read()
                except Exception:
                    continue
                for pattern in SCAFFOLD_ONLY_PATTERNS:
                    if pattern in content:
                        rel = os.path.relpath(fpath)
                        errors.append(f"{rel} contains scaffold/placeholder pattern '{pattern}'")
                        break
    return errors

def check_compileall():
    try:
        result = subprocess.run(
            [sys.executable, "-m", "compileall", L0_CODE_DIR],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return [f"compileall failed for {L0_CODE_DIR}: {result.stderr.strip()}"]
        return []
    except Exception as e:
        return [f"compileall error: {e}"]

def main():
    errors = []

    if not os.path.isdir(L0_CODE_DIR):
        errors.append(f"L0/CODE directory '{L0_CODE_DIR}' does not exist")

    if not os.path.isdir(L0_TESTS_DIR):
        errors.append(f"L0 tests directory '{L0_TESTS_DIR}' does not exist")
    else:
        test_count = count_test_functions_in_dir(SEED_L0_DIR)
        if test_count < 1:
            errors.append(f"No test functions found in '{SEED_L0_DIR}'")
        else:
            print(f"  INFO: L0 seed_l0 has {test_count} test function(s)")

    import_errors = check_mutation_intent_imports()
    errors.extend(import_errors)

    compile_errors = check_compileall()
    errors.extend(compile_errors)

    scaffold_errors = check_scaffold_only()
    errors.extend(scaffold_errors)

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: L0 protection validated - independent, compiled, no mutation imports, no scaffold-only files")
    sys.exit(0)

if __name__ == "__main__":
    main()
