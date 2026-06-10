from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def _makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def _target_header(text: str, target: str) -> str:
    prefix = f"{target}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    raise AssertionError(f"Missing Makefile target: {target}")


def _target_block(text: str, target: str) -> str:
    prefix = f"{target}:"
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            start = index
            break
    if start is None:
        raise AssertionError(f"Missing Makefile target: {target}")

    block = [lines[start]]
    for line in lines[start + 1 :]:
        if line and not line.startswith(("\t", " ")) and ":" in line:
            break
        block.append(line)
    return "\n".join(block)


def test_prove_all_depends_on_prove_format():
    text = _makefile_text()
    target_line = _target_header(text, "prove-all")
    assert "prove-format" in target_line


def test_prove_format_runs_top_level_format_guard_directly():
    text = _makefile_text()
    prove_format_block = _target_block(text, "prove-format")
    assert "tests/regression/test_text_file_formatting.py" in prove_format_block


def test_prove_format_runs_makefile_wiring_guard_directly():
    text = _makefile_text()
    prove_format_block = _target_block(text, "prove-format")
    assert "tests/regression/test_makefile_proof_wiring.py" in prove_format_block


def test_prove_format_does_not_depend_on_keyword_selection_only():
    text = _makefile_text()
    prove_format_block = _target_block(text, "prove-format")
    assert "-k \"formatting or text_file\"" not in prove_format_block
    assert "-k 'formatting or text_file'" not in prove_format_block
