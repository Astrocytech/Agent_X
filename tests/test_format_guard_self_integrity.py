"""Self-integrity test for the formatting guard.

Ensures the formatting guard itself cannot be collapsed and that it
covers all critical files.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_format_guard_has_minimum_lines():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    assert path.exists()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 80, (
        f"format guard has {len(lines)} lines, expected >= 80"
    )


def test_format_guard_has_minimum_test_functions():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    text = path.read_text(encoding="utf-8")
    test_defs = [
        ln for ln in text.splitlines()
        if "def test_" in ln
    ]
    assert len(test_defs) >= 5, (
        f"format guard has {len(test_defs)} test functions, "
        f"expected >= 5"
    )


def test_format_guard_no_multiple_def_per_line():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    text = path.read_text(encoding="utf-8")
    for i, ln in enumerate(text.splitlines(), start=1):
        stripped = ln.strip()
        if stripped.startswith("def test_") and stripped.count("def ") > 1:
            assert False, (
                f"format guard line {i}: "
                f"multiple defs on one line: {ln}"
            )


def test_format_guard_includes_itself():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    text = path.read_text(encoding="utf-8")
    assert "test_text_file_formatting.py" in text, (
        "format guard must include itself in critical file list"
    )


def test_format_guard_includes_taxonomy():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    text = path.read_text(encoding="utf-8")
    assert "L1/target_taxonomy.yaml" in text, (
        "format guard must include L1/target_taxonomy.yaml"
    )


def test_format_guard_includes_production_validators():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    text = path.read_text(encoding="utf-8")
    validators = [
        "validate_target_taxonomy.py",
        "validate_framework_manifest.py",
        "validate_all.py",
        "validate_target_profiles.py",
        "bootstrap_validate_l2_scaffold.py",
    ]
    for v in validators:
        assert v in text, (
            f"format guard must include {v}"
        )
