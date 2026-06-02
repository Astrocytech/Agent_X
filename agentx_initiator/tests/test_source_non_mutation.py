import hashlib
from pathlib import Path
from agentx_initiator.core.repo_scanner import scan_repository
from agentx_initiator.cli.main import main


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _hash_source_tree(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".agentx-init" not in path.parts:
            try:
                content = path.read_bytes()
                h.update(content)
            except (OSError, PermissionError):
                continue
    return h.hexdigest()


def _get_source_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".agentx-init" not in str(path):
            files.append(path)
    return files


def test_source_non_mutation_after_scan():
    root = PROJECT_ROOT
    before = _hash_source_tree(root)
    scan_repository(root, ignore_dirs={
        ".git", "__pycache__", ".venv", "node_modules", ".agentx-init"
    })
    after = _hash_source_tree(root)
    assert before == after, "Source files changed after scan"


def test_source_non_mutation_after_scan_status():
    root = PROJECT_ROOT
    before_files = _get_source_files(root)
    scan_repository(root, ignore_dirs={
        ".git", "__pycache__", ".venv", "node_modules", ".agentx-init"
    })
    from agentx_initiator.core.repo_scanner import scan_repo
    scan_repo(root)
    after_files = _get_source_files(root)
    assert len(before_files) == len(after_files)
    for bf, af in zip(before_files, after_files):
        assert bf.read_bytes() == af.read_bytes(), f"File changed: {bf}"
