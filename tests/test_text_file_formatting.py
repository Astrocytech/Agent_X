"""Format guard tests — prevent collapsed single-line source files.

Checks:
- Python validator/test files meet minimum line counts
- Selected YAML files are expanded multiline YAML
- No semicolon-compressed or collapsed patterns in critical files
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PYTHON_FILES_MIN_LINES: dict[str, int] = {
    "L1/validators/validate_target_taxonomy.py": 25,
    "L1/validators/validate_framework_manifest.py": 25,
    "L1/validators/validate_all.py": 25,
    "L2/validators/validate_target_profiles.py": 25,
    "L2/validators/bootstrap_validate_l2_scaffold.py": 25,
    "tests/test_text_file_formatting.py": 40,
}

YAML_FILES_MIN_LINES: dict[str, int] = {
    "L1/target_taxonomy.yaml": 40,
    "L2/profiles/framework_seed.yaml": 80,
}

FILES_EXPECTED_MULTILINE: list[str] = [
    "Makefile",
    "README.md",
    "L1/README.md",
    "L2/README.md",
    "L1/target_taxonomy.yaml",
    "L1/schemas/framework_package_manifest.schema.yaml",
    "L2/profiles/framework_seed.yaml",
    "L1/tests/test_l1_framework_target.py",
    "L2/tests/test_l2_framework_target.py",
    "L1/validators/validate_target_taxonomy.py",
    "L1/validators/validate_framework_manifest.py",
    "L1/validators/validate_all.py",
    "L2/validators/validate_target_profiles.py",
    "L2/validators/bootstrap_validate_l2_scaffold.py",
    "tests/test_text_file_formatting.py",
]


def test_python_validator_files_meet_minimum_line_count():
    for rel_path, min_lines in PYTHON_FILES_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        assert path.exists(), f"Missing expected Python file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= min_lines, (
            f"{rel_path} has {len(lines)} lines, expected >= {min_lines}"
        )


def test_yaml_files_meet_minimum_line_count():
    for rel_path, min_lines in YAML_FILES_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        assert path.exists(), f"Missing expected YAML file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= min_lines, (
            f"{rel_path} has {len(lines)} lines, expected >= {min_lines}"
        )


def test_selected_text_files_are_not_collapsed():
    for name in FILES_EXPECTED_MULTILINE:
        path = REPO_ROOT / name
        assert path.exists(), f"Missing expected text file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 5, (
            f"{name} appears collapsed or too short ({len(lines)} lines)"
        )


def test_python_files_no_collapse_patterns():
    for rel_path in PYTHON_FILES_MIN_LINES:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        if "test_text_file_formatting" in rel_path:
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for ln in lines:
            stripped = ln.strip()
            if stripped.startswith("def ") and stripped.count("def ") > 1:
                assert False, (
                    f"{rel_path}: multiple defs on one line: {ln}"
                )
            if stripped.startswith("class ") and stripped.count("class ") > 1:
                assert False, (
                    f"{rel_path}: multiple classes on one line: {ln}"
                )
        assert " import " not in text or "\ndef " in text or "\nclass " in text or path.stat().st_size < 500


def test_yaml_expanded_format():
    for rel_path in YAML_FILES_MIN_LINES:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) >= 40, f"{rel_path}: too few lines for expanded YAML"
        if "target_kinds:" in text:
            found_framework = False
            for ln in lines:
                if ln.rstrip() == "  framework:" or ln.strip() == "framework:":
                    found_framework = True
                    break
            assert found_framework, (
                f"{rel_path}: framework not found as expanded key under target_kinds"
            )
        if "framework_rules:" in text:
            found_required = False
            for ln in lines:
                if "required_capabilities:" in ln:
                    found_required = True
                    break
            assert found_required, (
                f"{rel_path}: framework_rules keys not expanded across lines"
            )


def test_makefile_recipes_not_collapsed():
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ["prove-all:", "prove-l1:", "prove-l2:", "prove-seed:"]:
        line = next(
            (ln for ln in text.splitlines() if ln.startswith(target)), ""
        )
        assert ";" not in line, (
            f"{target} recipe should not be collapsed onto target line"
        )


def test_yaml_files_parse():
    import yaml
    for pattern in ["L1/**/*.yaml", "L2/**/*.yaml"]:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file() or path.stat().st_size == 0:
                continue
            if "generated" in path.parts:
                continue
            with path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert data is not None or path.stat().st_size < 10, (
                f"Failed to parse YAML: {path}"
            )
