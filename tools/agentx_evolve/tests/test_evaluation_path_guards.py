import pytest
from pathlib import Path
from agentx_evolve.evaluation.path_guards import (
    resolve_inside_root, ensure_inside_root, reject_path_traversal, safe_relative_ref,
)


def test_resolve_inside_root_valid(tmp_path):
    inner = tmp_path / "subdir" / "file.txt"
    inner.parent.mkdir(parents=True)
    inner.write_text("data")
    resolved = resolve_inside_root(Path("subdir/file.txt"), tmp_path)
    assert resolved == inner


def test_resolve_inside_root_raises_on_escape(tmp_path):
    with pytest.raises(ValueError, match="escapes root"):
        resolve_inside_root(Path(".."), tmp_path)


def test_resolve_inside_root_absolute_path(tmp_path):
    with pytest.raises(ValueError, match="escapes root"):
        resolve_inside_root(Path("/etc/passwd"), tmp_path)


def test_ensure_inside_root_valid(tmp_path):
    inner = tmp_path / "file.txt"
    inner.write_text("data")
    ensure_inside_root(Path("file.txt"), tmp_path)


def test_ensure_inside_root_raises(tmp_path):
    with pytest.raises(ValueError, match="escapes root"):
        ensure_inside_root(Path("../outside"), tmp_path)


def test_reject_path_traversal_clean():
    reject_path_traversal("subdir/file.txt")


def test_reject_path_traversal_double_dot():
    with pytest.raises(ValueError, match="Path traversal"):
        reject_path_traversal("../etc/passwd")


def test_reject_path_traversal_nested():
    with pytest.raises(ValueError, match="Path traversal"):
        reject_path_traversal("subdir/../../etc")


def test_reject_path_traversal_with_os_sep():
    with pytest.raises(ValueError, match="Path traversal"):
        reject_path_traversal("a/../b")


def test_reject_path_traversal_empty():
    reject_path_traversal("")


def test_reject_path_traversal_normal_path():
    reject_path_traversal("normal/path/file.json")


def test_safe_relative_ref(tmp_path):
    inner = tmp_path / "subdir" / "file.txt"
    inner.parent.mkdir(parents=True)
    inner.write_text("data")
    ref = safe_relative_ref(inner, tmp_path)
    assert ref == "subdir/file.txt" or ref.endswith("subdir/file.txt")


def test_safe_relative_ref_root(tmp_path):
    ref = safe_relative_ref(tmp_path, tmp_path)
    assert ref == "."


def test_safe_relative_ref_nested(tmp_path):
    inner = tmp_path / "a" / "b" / "c.txt"
    inner.parent.mkdir(parents=True)
    inner.write_text("data")
    ref = safe_relative_ref(inner, tmp_path)
    assert ref == "a/b/c.txt" or ref.endswith("a/b/c.txt")


def test_safe_relative_ref_outside_raises(tmp_path):
    with pytest.raises(ValueError, match="escapes root"):
        safe_relative_ref(Path("/etc"), tmp_path)


def test_resolve_inside_root_symlink(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target)
    inner = link / "file.txt"
    inner.write_text("data")
    resolved = resolve_inside_root(Path("link/file.txt"), tmp_path)
    assert resolved.exists()
