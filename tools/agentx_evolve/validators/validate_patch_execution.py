#!/usr/bin/env python3
import sys, os, subprocess

PATCH_EXEC_DIR = "tools/agentx_evolve/patch_execution"
ROLLBACK_TEST = os.path.join("tests", "release", "test_failure_rollback_flow.py")
SEED_L0_DIR = os.path.join("L0", "tests", "seed_l0")

def count_test_functions(path):
    count = 0
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("def test_") and stripped.endswith(":"):
                count += 1
    return count

def main():
    errors = []

    if not os.path.isdir(PATCH_EXEC_DIR):
        errors.append(f"Patch execution directory '{PATCH_EXEC_DIR}' does not exist")
    else:
        expected_patch_files = [
            "patch_models.py", "patch_applier.py", "patch_policy.py",
            "patch_session.py", "patch_evidence.py", "rollback_manager.py",
            "implementation_validation_gate.py", "patch_execution_service.py"
        ]
        for fname in expected_patch_files:
            if not os.path.isfile(os.path.join(PATCH_EXEC_DIR, fname)):
                errors.append(f"Expected patch execution file '{fname}' missing in {PATCH_EXEC_DIR}")

    if not os.path.isfile(ROLLBACK_TEST):
        errors.append(f"Rollback test file '{ROLLBACK_TEST}' not found")
    else:
        n = count_test_functions(ROLLBACK_TEST)
        if n < 1:
            errors.append(f"'{ROLLBACK_TEST}' has no test functions")
        else:
            print(f"  INFO: {ROLLBACK_TEST} has {n} test function(s)")

    if not os.path.isdir(SEED_L0_DIR):
        errors.append(f"Seed L0 test dir '{SEED_L0_DIR}' does not exist")
    else:
        seed_tests = [f for f in os.listdir(SEED_L0_DIR) if f.startswith("test_") and f.endswith(".py")]
        if not seed_tests:
            errors.append(f"No seed L0 tests found in '{SEED_L0_DIR}'")
        else:
            print(f"  INFO: {len(seed_tests)} seed L0 test files found in {SEED_L0_DIR}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: patch execution foundation validated")
    sys.exit(0)

if __name__ == "__main__":
    main()
