"""Format guard tests — prevent collapsed single-line source files."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FILES_EXPECTED_MULTILINE = [
    "Makefile",
    "README.md",
    "L1/README.md",
    "L2/README.md",
    "L1/target_taxonomy.yaml",
    "L1/schemas/framework_package_manifest.schema.yaml",
    "L2/profiles/framework_seed.yaml",
    "L1/tests/test_l1_framework_target.py",
    "L2/tests/test_l2_framework_target.py",
]


def test_selected_text_files_are_not_collapsed():
    for name in FILES_EXPECTED_MULTILINE:
        path = REPO_ROOT / name
        assert path.exists(), f"Missing expected text file: {path}"
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 5, f"{name} appears collapsed or too short ({len(lines)} lines)"


def test_python_files_no_collapse_patterns():
    for base_dir in ["L1", "L2"]:
        for path in sorted((REPO_ROOT / base_dir).rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            assert ": def " not in text, f"{path} appears to contain collapsed class/function code"
            assert ": class " not in text, f"{path} appears to contain collapsed class definition"
            assert " import " not in text or "\ndef " in text or "\nclass " in text or path.stat().st_size < 500


def test_makefile_recipes_not_collapsed():
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ["prove-all:", "prove-l1:", "prove-l2:", "prove-seed:"]:
        line = next((ln for ln in text.splitlines() if ln.startswith(target)), "")
        assert ";" not in line, f"{target} recipe should not be collapsed onto target line"


def test_yaml_files_parse():
    for pattern in ["L1/**/*.yaml", "L2/**/*.yaml"]:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file() or path.stat().st_size == 0:
                continue
            if "generated" in path.parts:
                continue
            import yaml
            with path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            assert data is not None or path.stat().st_size < 10, f"Failed to parse YAML: {path}"
