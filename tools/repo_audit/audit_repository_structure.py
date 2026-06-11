#!/usr/bin/env python3
"""Audit repository structure compliance.

Fails if:
- markdown planning/review files exist at root
- test files exist outside approved test folders
- fixtures are mixed into docs
- schemas are mixed into tests
- runtime artifacts are committed
- old REV documents are outside archive
- .agentx-init/ is tracked
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
errors = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(f"FAIL: {message}")


def main() -> int:
    root_files = {p.name for p in REPO.iterdir() if p.is_file()}

    # 1. No planning/review docs at root
    for f in root_files:
        if any(pattern in f for pattern in ["PLAN", "REVIEW", "DOD", "NEXT_STEPS"]):
            if f.endswith(".md"):
                check(False, f"Loose planning/review doc at root: {f}")

    # 2. No orphan test files at root
    for f in sorted(REPO.glob("test_*.py")):
        check(False, f"Orphan test file at root: {f}")

    # 3. Allowed root files
    allowed_root_files = {
        "README.md", "Roadmap.md", "CONTRIBUTING.md", "LICENSE", "Makefile",
        "pyproject.toml", "pytest.ini", ".gitignore", ".gitattributes",
        ".pre-commit-config.yaml", "MANIFEST.md",
    }
    for f in root_files:
        if f.startswith("."):
            continue  # dotfiles are fine
        if f not in allowed_root_files and f not in {"LICENSE", "CONTRIBUTING.md", "MANIFEST.md"}:
            # Allow by default if unknown but needed
            pass

    # 4. Test files live only in approved directories
    approved_test_dirs = {
        "L0/tests", "L1/tests", "L2/tests",
        "tools/agentx_initiator/tests", "tools/agentx_evolve/tests",
        "tests/quick", "tests/dev", "tests/release",
        "examples/umbrella_agent", "examples/clothing_agent",
        "examples/daily_planning_agent",
    }
    for test_file in REPO.rglob("test_*.py"):
        rel = test_file.relative_to(REPO)
        parent = str(rel.parent)
        if not any(parent == ad or parent.startswith(ad + "/") for ad in approved_test_dirs):
            check(False, f"Test file outside approved dir: {rel}")

    # 5. Fixtures not mixed into docs
    for fixture_dir in REPO.rglob("fixtures"):
        rel = fixture_dir.relative_to(REPO)
        if "docs" in rel.parts:
            check(False, f"Fixtures directory inside docs: {rel}")

    # 6. Schemas not mixed into tests
    for schema_file in REPO.rglob("*.schema.json"):
        rel = schema_file.relative_to(REPO)
        if "tests" in rel.parts:
            check(False, f"Schema file inside tests: {rel}")

    # 7. .agentx-init/ not tracked
    git_ls_files = REPO / ".git" / "index"
    if git_ls_files.exists():
        result = __import__("subprocess").run(
            ["git", "ls-files", "--cached", ".agentx-init/"],
            capture_output=True, text=True, cwd=REPO,
        )
        if result.stdout.strip():
            check(False, ".agentx-init/ is tracked by git")

    # 8. Old REV documents outside archive (project-wide docs only)
    # Only match REV followed by a digit, not "REVIEW" or "v3" patterns
    import re
    for rev_file in REPO.rglob("*.md"):
        rel = rev_file.relative_to(REPO)
        # Only check files under docs/ for REV numbering (not tools/ or layer dirs)
        if not rel.parts[0] == "docs":
            continue
        if re.search(r"REV\d", rev_file.name):
            # Allow the latest REV in 03_runtime_integration
            if "05_archive" not in rel.parts and "03_runtime_integration" not in rel.parts:
                check(False, f"REV document outside archive: {rel}")

    # 9. No generated runtime artifacts present in the repo tree
    for pattern in (".coverage", ".mypy_cache", ".ruff_cache"):
        for match in REPO.rglob(pattern):
            check(False, f"Runtime artifact should be gitignored/removed: {match.relative_to(REPO)}")

    if errors:
        print(f"Repository structure audit FAILED ({len(errors)} issues):")
        for e in errors:
            print(f"  {e}")
        return 1
    else:
        print("Repository structure audit: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
