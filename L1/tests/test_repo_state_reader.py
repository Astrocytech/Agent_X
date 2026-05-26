from __future__ import annotations

import dataclasses
import hashlib
import pathlib
import sys

import pytest

from L1.controller.repo_state_reader import (
    DEFAULT_MAX_FILE_BYTES,
    RepoFileInfo,
    RepoStateReader,
    RepoStateError,
    RepoStatePathError,
    RepoStateReadError,
    get_repo_file_info,
    list_repo_files,
    read_text_file,
)


def test_get_file_info_returns_correct_metadata(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "info.txt"
    doc.write_text("metadata", encoding="utf-8")
    info = get_repo_file_info("info.txt", root=tmp_path)
    assert info.relative_path == "info.txt"
    assert info.size_bytes == 8
    assert info.is_dir is False


def test_get_file_info_computes_sha256(tmp_path: pathlib.Path) -> None:
    content = "sha256-check"
    doc = tmp_path / "check.txt"
    doc.write_text(content, encoding="utf-8")
    info = get_repo_file_info("check.txt", root=tmp_path)
    expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert info.sha256 == expected


def test_get_file_info_rejects_directory(tmp_path: pathlib.Path) -> None:
    (tmp_path / "sub").mkdir()
    with pytest.raises(RepoStatePathError, match="directory"):
        get_repo_file_info("sub", root=tmp_path)


def test_get_file_info_rejects_missing_file(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RepoStatePathError, match="does not exist"):
        get_repo_file_info("nonexistent.txt", root=tmp_path)


def test_get_file_info_rejects_absolute_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RepoStatePathError, match="must be relative"):
        get_repo_file_info(str(tmp_path / "whatever"), root=tmp_path)


def test_get_file_info_rejects_empty_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RepoStatePathError, match="must not be empty"):
        get_repo_file_info("", root=tmp_path)


def test_get_file_info_rejects_non_string_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RepoStatePathError, match="must be a string"):
        get_repo_file_info(123, root=tmp_path)  # type: ignore[arg-type]


def test_get_file_info_rejects_traversal(tmp_path: pathlib.Path) -> None:
    with pytest.raises(RepoStatePathError, match="escapes root"):
        get_repo_file_info("../outside.txt", root=tmp_path)


def test_get_file_info_rejects_symlink_escape(tmp_path: pathlib.Path) -> None:
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("escape", encoding="utf-8")
    link = tmp_path / "evil_link.txt"
    link.symlink_to(outside)
    with pytest.raises(RepoStatePathError, match="escapes root"):
        get_repo_file_info("evil_link.txt", root=tmp_path)


def test_list_files_matches_glob(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.py").write_text("a", encoding="utf-8")
    (tmp_path / "b.py").write_text("b", encoding="utf-8")
    (tmp_path / "c.txt").write_text("c", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "d.py").write_text("d", encoding="utf-8")

    py_files = list_repo_files("*.py", root=tmp_path)
    assert "a.py" in py_files
    assert "b.py" in py_files
    assert "sub/d.py" in py_files
    assert "c.txt" not in py_files


def test_list_files_returns_empty_for_no_match(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    assert list_repo_files("*.md", root=tmp_path) == []


def test_list_files_includes_hidden_files(tmp_path: pathlib.Path) -> None:
    (tmp_path / ".hidden").write_text("secret", encoding="utf-8")
    all_files = list_repo_files("*", root=tmp_path)
    assert ".hidden" in all_files


def test_read_text_file_returns_content(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "hello.txt"
    doc.write_text("Hello, world!", encoding="utf-8")
    content = read_text_file("hello.txt", root=tmp_path)
    assert content == "Hello, world!"


def test_read_text_file_rejects_non_utf8(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "binary.bin"
    doc.write_bytes(b"\xff\xfe\x00\x01")
    with pytest.raises(RepoStateReadError, match="UTF-8"):
        read_text_file("binary.bin", root=tmp_path)


def test_read_text_file_rejects_oversized(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "big.txt"
    doc.write_bytes(b"x" * (DEFAULT_MAX_FILE_BYTES + 1))
    with pytest.raises(RepoStateReadError, match="exceeds maximum"):
        read_text_file("big.txt", root=tmp_path)


def test_read_text_file_rejects_directory(tmp_path: pathlib.Path) -> None:
    (tmp_path / "sub").mkdir()
    with pytest.raises(RepoStatePathError, match="directory"):
        read_text_file("sub", root=tmp_path)


def test_repo_state_reader_init_rejects_non_existent_root() -> None:
    with pytest.raises(RepoStatePathError, match="does not exist"):
        RepoStateReader("/nonexistent/path/12345")


def test_repo_state_reader_init_rejects_file_root(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "file.txt"
    doc.write_text("", encoding="utf-8")
    with pytest.raises(RepoStatePathError, match="not a directory"):
        RepoStateReader(str(doc))


def test_repo_file_info_is_frozen(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "frozen.txt"
    doc.write_text("data", encoding="utf-8")
    info = get_repo_file_info("frozen.txt", root=tmp_path)
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.path = "changed"
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.relative_path = "changed"
    with pytest.raises(dataclasses.FrozenInstanceError):
        info.sha256 = "changed"


def test_repo_state_reader_no_forbidden_imports() -> None:
    source = pathlib.Path("L1/controller/repo_state_reader.py").read_text(
        encoding="utf-8"
    )
    forbidden = [
        "import os",
        "from os",
        "import subprocess",
        "from subprocess",
        "import requests",
        "import urllib",
        "import socket",
        "import http",
    ]
    for imp in forbidden:
        assert imp not in source, f"forbidden import found: {imp}"


def test_read_text_file_returns_sha256(tmp_path: pathlib.Path) -> None:
    content = "sha256-content"
    doc = tmp_path / "sha.txt"
    doc.write_text(content, encoding="utf-8")
    reader = RepoStateReader(tmp_path)
    info = reader.get_file_info("sha.txt")
    assert info.sha256 == hashlib.sha256(content.encode("utf-8")).hexdigest()


def test_independent_reader_instances(tmp_path: pathlib.Path) -> None:
    (tmp_path / "alpha.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "beta.txt").write_text("beta", encoding="utf-8")

    reader_a = RepoStateReader(tmp_path)
    reader_b = RepoStateReader(tmp_path)

    info_a = reader_a.get_file_info("alpha.txt")
    info_b = reader_b.get_file_info("sub/beta.txt")

    assert info_a.relative_path == "alpha.txt"
    assert info_b.relative_path == "sub/beta.txt"
    assert info_a.size_bytes != info_b.size_bytes


def test_list_files_rejects_non_string_glob(tmp_path: pathlib.Path) -> None:
    reader = RepoStateReader(tmp_path)
    with pytest.raises(RepoStatePathError, match="must be a string"):
        reader.list_files(123)  # type: ignore[arg-type]


def test_list_files_rejects_empty_glob(tmp_path: pathlib.Path) -> None:
    reader = RepoStateReader(tmp_path)
    with pytest.raises(RepoStatePathError, match="must not be empty"):
        reader.list_files("")



def test_reader_root_property(tmp_path: pathlib.Path) -> None:
    reader = RepoStateReader(tmp_path)
    assert reader.root == str(tmp_path.resolve())
