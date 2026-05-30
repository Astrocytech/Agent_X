"""Format guard tests — prevent collapsed single-line source files.

Checks:
- Python validator/test files meet minimum line counts
- Selected YAML files are expanded multiline YAML
- No semicolon-compressed or collapsed patterns in critical files
"""

import ast
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CRITICAL_PYTHON_MIN_LINES: dict[str, int] = {
    "L1/validators/validate_target_taxonomy.py": 80,
    "L1/validators/validate_framework_manifest.py": 120,
    "L1/validators/validate_all.py": 100,
    "L1/tests/test_l1_framework_target.py": 150,
    "L2/validators/validate_target_profiles.py": 120,
    "L2/validators/bootstrap_validate_l2_scaffold.py": 80,
    "L2/tests/test_l2_framework_target.py": 120,
    "tests/test_text_file_formatting.py": 80,
}

CRITICAL_YAML_MIN_LINES: dict[str, int] = {
    "L1/target_taxonomy.yaml": 80,
}

CRITICAL_FILES: list[str] = [
    "L1/target_taxonomy.yaml",
    "L1/validators/validate_target_taxonomy.py",
    "L1/validators/validate_framework_manifest.py",
    "L1/validators/validate_all.py",
    "L1/tests/test_l1_framework_target.py",
    "L2/validators/validate_target_profiles.py",
    "L2/validators/bootstrap_validate_l2_scaffold.py",
    "L2/tests/test_l2_framework_target.py",
    "tests/test_text_file_formatting.py",
    "Makefile",
    "README.md",
    "L1/README.md",
    "L2/README.md",
]


def test_critical_python_files_meet_minimum_line_count():
    for rel_path, min_lines in CRITICAL_PYTHON_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        assert path.exists(), f"Missing expected Python file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= min_lines, (
            f"{rel_path} has {len(lines)} lines, "
            f"expected >= {min_lines}"
        )


def test_critical_yaml_files_meet_minimum_line_count():
    for rel_path, min_lines in CRITICAL_YAML_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        assert path.exists(), f"Missing expected YAML file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= min_lines, (
            f"{rel_path} has {len(lines)} lines, "
            f"expected >= {min_lines}"
        )


def test_critical_files_are_not_collapsed():
    for name in CRITICAL_FILES:
        path = REPO_ROOT / name
        assert path.exists(), f"Missing expected file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 5, (
            f"{name} appears collapsed "
            f"({len(lines)} lines, expected >= 5)"
        )


def test_no_multiple_def_on_same_line():
    for rel_path, _min_lines in CRITICAL_PYTHON_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        for i, ln in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            stripped = ln.strip()
            if stripped.startswith("def ") and stripped.count("def ") > 1:
                assert False, (
                    f"{rel_path}:{i}: multiple defs on one line: {ln}"
                )
            if stripped.startswith("class ") and stripped.count("class ") > 1:
                assert False, (
                    f"{rel_path}:{i}: multiple classes on one line: {ln}"
                )


def test_no_collapse_patterns_in_critical_python():
    patterns = [
        ') def ',
        ': def ',
        '; def ',
        '; class ',
    ]
    for rel_path, _min_lines in CRITICAL_PYTHON_MIN_LINES.items():
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, ln in enumerate(
            text.splitlines(), start=1
        ):
            stripped = ln.strip()
            if stripped.startswith("'") and stripped.endswith(","):
                continue
            if stripped.startswith('"') and stripped.endswith(","):
                continue
            for pat in patterns:
                if pat in ln:
                    assert False, (
                        f"{rel_path}:{i}: "
                        f"contains collapse pattern '{pat}': {ln}"
                    )


def test_no_docstring_and_import_on_same_line():
    critical = [
        "L1/validators/validate_target_taxonomy.py",
        "L1/validators/validate_framework_manifest.py",
        "L1/validators/validate_all.py",
        "L2/validators/validate_target_profiles.py",
        "L2/validators/bootstrap_validate_l2_scaffold.py",
        "L1/tests/test_l1_framework_target.py",
        "L2/tests/test_l2_framework_target.py",
        "tests/test_text_file_formatting.py",
    ]
    for rel_path in critical:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for i, ln in enumerate(text.splitlines(), start=1):
            if '"""' in ln and '""" ' in ln:
                docstring_open = ln.find('"""')
                rest = ln[docstring_open + 3:]
                if 'from ' in rest or 'import ' in rest:
                    assert False, (
                        f"{rel_path}:{i}: docstring and import "
                        f"on same line: {ln}"
                    )


def test_makefile_recipes_not_collapsed():
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    for target in [
        "prove-all:",
        "prove-l1:",
        "prove-l2:",
        "prove-seed:",
    ]:
        line = next(
            (ln for ln in text.splitlines()
             if ln.startswith(target)),
            ""
        )
        assert ";" not in line, (
            f"{target} recipe should not be "
            f"collapsed onto target line"
        )


def test_taxonomy_has_expanded_framework_rules():
    path = REPO_ROOT / "L1" / "target_taxonomy.yaml"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) >= 80, (
        f"taxonomy has {len(lines)} lines, "
        f"expected >= 80"
    )
    assert "target_kinds:" in text, (
        "taxonomy missing target_kinds"
    )
    framework_under_kinds = False
    for ln in lines:
        stripped = ln.rstrip()
        if stripped == "  framework:":
            framework_under_kinds = True
    assert framework_under_kinds, (
        "taxonomy: framework not expanded under target_kinds"
    )
    assert "framework_rules:" in text, (
        "taxonomy missing framework_rules"
    )
    required_under_rules = False
    for ln in lines:
        if "required_capabilities:" in ln:
            required_under_rules = True
    assert required_under_rules, (
        "taxonomy: framework_rules keys not expanded"
    )


def test_critical_files_are_expanded_yaml():
    yaml_critical = [
        "L1/target_taxonomy.yaml",
    ]
    for rel_path in yaml_critical:
        path = REPO_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) >= 80, (
            f"{rel_path}: {len(lines)} lines < 80"
        )


def test_format_guard_itself_is_not_collapsed():
    path = REPO_ROOT / "tests" / "test_text_file_formatting.py"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) >= 80, (
        f"format guard has {len(lines)} lines, expected >= 80"
    )
    test_defs = [ln for ln in lines if "def test_" in ln]
    assert len(test_defs) >= 5, (
        f"format guard has {len(test_defs)} test functions, "
        f"expected >= 5"
    )


def test_yaml_files_parse():
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


def test_python_files_parse_with_ast():
    for rel_path in CRITICAL_PYTHON_MIN_LINES:
        full = REPO_ROOT / rel_path
        if not full.is_file():
            continue
        source = full.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=rel_path)
        except SyntaxError as e:
            assert False, f"{rel_path}: AST parse error: {e}"


def test_no_escaped_newline_inflation():
    for rel_path in CRITICAL_PYTHON_MIN_LINES:
        full = REPO_ROOT / rel_path
        if not full.is_file():
            continue
        raw = full.read_bytes()
        phys_lines = raw.count(b"\n")
        lit_esc = raw.count(b"\\n")
        if lit_esc > 0 and lit_esc >= phys_lines * 0.5:
            assert False, (
                f"{rel_path}: {lit_esc} literal \\n sequences "
                f"({phys_lines} physical lines) — possible collapse"
            )
