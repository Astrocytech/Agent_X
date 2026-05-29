from pathlib import Path


def test_python_files_are_not_collapsed_to_one_line():
    for path in sorted(Path("L1").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if not text:
            continue  # empty __init__.py is valid
        assert "\n" in text, f"{path} appears collapsed into one line"


def test_makefile_has_real_targets_and_recipe_lines():
    path = Path("Makefile")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "\nprove-l1:" in text, "Makefile missing prove-l1 target"
    assert "\n\t" in text, "Makefile missing tab-indented recipe lines"


def test_yaml_files_are_not_collapsed_block_yaml():
    for path in sorted(Path("L1").rglob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        assert "\n" in text, f"{path} appears collapsed into one line"


def test_json_files_are_not_collapsed():
    for path in sorted(Path("L1").rglob("*.json")):
        text = path.read_text(encoding="utf-8")
        assert "\n" in text, f"{path} appears collapsed into one line"
