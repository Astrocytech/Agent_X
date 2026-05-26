from __future__ import annotations

import dataclasses
import hashlib
import os
import pathlib
import sys
import tempfile
from unittest.mock import patch

import pytest

from L1.controller.document_loader import (
    DEFAULT_MAX_DOCUMENT_BYTES,
    DocumentLoadError,
    DocumentLoaderError,
    DocumentPathError,
    DocumentRecord,
    DocumentRootError,
    load_document,
    load_documents,
)


def test_loads_a_valid_utf8_document(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "hello.txt"
    doc.write_text("Hello, world!", encoding="utf-8")
    record = load_document("hello.txt", root=tmp_path)
    assert record.exists is True
    assert record.content == "Hello, world!"
    assert record.size_bytes == 13


def test_loads_an_empty_utf8_document(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "empty.txt"
    doc.write_text("", encoding="utf-8")
    record = load_document("empty.txt", root=tmp_path)
    assert record.content == ""
    assert record.size_bytes == 0


def test_computes_sha256_from_raw_bytes(tmp_path: pathlib.Path) -> None:
    content = "Hello, world!"
    doc = tmp_path / "hello.txt"
    doc.write_text(content, encoding="utf-8")
    record = load_document("hello.txt", root=tmp_path)
    expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert record.sha256 == expected


def test_document_record_is_frozen(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    record = load_document("test.txt", root=tmp_path)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.content = "changed"
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.path = "changed"


def test_preserves_input_order_for_multiple_documents(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "c.txt").write_text("c", encoding="utf-8")
    records = load_documents(["a.txt", "b.txt", "c.txt"], root=tmp_path)
    assert [r.path for r in records] == ["a.txt", "b.txt", "c.txt"]
    assert [r.content for r in records] == ["a", "b", "c"]


def test_rejects_non_list_paths_input(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError):
        load_documents("single_path", root=tmp_path)  # type: ignore[arg-type]


def test_rejects_non_string_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError):
        load_document(123, root=tmp_path)  # type: ignore[arg-type]


def test_rejects_empty_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError):
        load_document("", root=tmp_path)


def test_rejects_absolute_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError):
        load_document("/etc/passwd", root=tmp_path)


def test_rejects_path_traversal_outside_root(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError):
        load_document("../../etc/passwd", root=tmp_path)


def test_rejects_symlink_escape_outside_root(tmp_path: pathlib.Path) -> None:
    outside = tempfile.mkdtemp()
    outside_file = pathlib.Path(outside) / "secret.txt"
    outside_file.write_text("secret", encoding="utf-8")
    link = tmp_path / "escape_link"
    try:
        link.symlink_to(outside_file)
    except OSError:
        pytest.skip("platform does not support symlinks")
    with pytest.raises(DocumentPathError):
        load_document("escape_link", root=tmp_path)


def test_rejects_missing_root(tmp_path: pathlib.Path) -> None:
    missing = tmp_path / "does_not_exist"
    with pytest.raises(DocumentRootError):
        load_document("test.txt", root=missing)


def test_rejects_root_that_is_a_file(tmp_path: pathlib.Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("data", encoding="utf-8")
    with pytest.raises(DocumentRootError):
        load_document("test.txt", root=f)


def test_rejects_missing_document(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentLoadError):
        load_document("nonexistent.txt", root=tmp_path)


def test_rejects_directory_document_path(tmp_path: pathlib.Path) -> None:
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    with pytest.raises(DocumentLoadError):
        load_document("subdir", root=tmp_path)


def test_rejects_file_larger_than_max_bytes(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "big.txt"
    doc.write_text("x" * 100, encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_document("big.txt", root=tmp_path, max_bytes=50)


def test_rejects_invalid_max_bytes(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_document("test.txt", root=tmp_path, max_bytes=-1)


def test_does_not_write_files(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    load_document("test.txt", root=tmp_path)
    assert list(tmp_path.iterdir()) == [doc]


def test_does_not_use_forbidden_imports() -> None:
    import L1.controller.document_loader as mod

    source = pathlib.Path(mod.__file__).read_text()
    forbidden = ["import os", "from os", "import subprocess", "from subprocess", "import requests", "import urllib", "import socket", "import http"]
    for imp in forbidden:
        assert imp not in source, f"forbidden import found: {imp}"


def test_all_matches_declared_module_exports() -> None:
    import L1.controller.document_loader as mod

    expected = {
        "DEFAULT_MAX_DOCUMENT_BYTES",
        "DocumentRecord",
        "DocumentLoaderError",
        "DocumentRootError",
        "DocumentPathError",
        "DocumentLoadError",
        "load_document",
        "load_documents",
    }
    assert set(mod.__all__) == expected


def test_duplicate_paths_preserve_multiplicity_and_order(tmp_path: pathlib.Path) -> None:
    (tmp_path / "a.txt").write_text("content", encoding="utf-8")
    records = load_documents(["a.txt", "a.txt", "a.txt"], root=tmp_path)
    assert len(records) == 3
    assert records[0].path == records[1].path == records[2].path == "a.txt"


def test_bool_max_bytes_is_rejected(tmp_path: pathlib.Path) -> None:
    (tmp_path / "test.txt").write_text("data", encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_document("test.txt", root=tmp_path, max_bytes=True)  # type: ignore[arg-type]


def test_returned_path_is_normalized_posix_style_relative_path(tmp_path: pathlib.Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    doc = sub / "test.txt"
    doc.write_text("data", encoding="utf-8")
    record = load_document("sub/test.txt", root=tmp_path)
    assert record.path == "sub/test.txt"
    assert "\\" not in record.path


def test_error_messages_do_not_expose_document_content_or_paths(tmp_path: pathlib.Path) -> None:
    with pytest.raises(DocumentPathError) as exc:
        load_document("../../etc/passwd", root=tmp_path)
    msg = str(exc.value)
    assert "passwd" not in msg


def test_non_declared_imported_helper_names_do_not_leak_through_all(tmp_path: pathlib.Path) -> None:
    import L1.controller.document_loader as mod

    for name in mod.__all__:
        assert not name.startswith("_")
    assert "_hashlib" not in mod.__all__
    assert "_pathlib" not in mod.__all__


def test_max_bytes_zero_allows_empty_file_and_rejects_non_empty(tmp_path: pathlib.Path) -> None:
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    record = load_document("empty.txt", root=tmp_path, max_bytes=0)
    assert record.content == ""
    assert record.size_bytes == 0

    nonempty = tmp_path / "nonempty.txt"
    nonempty.write_text("x", encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_document("nonempty.txt", root=tmp_path, max_bytes=0)


def test_path_like_root_is_accepted(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    record = load_document("test.txt", root=tmp_path)
    assert record.exists is True


def test_root_symlink_to_directory_is_allowed(tmp_path: pathlib.Path) -> None:
    real_dir = tmp_path / "realdir"
    real_dir.mkdir()
    (real_dir / "doc.txt").write_text("data", encoding="utf-8")
    link = tmp_path / "linkdir"
    try:
        link.symlink_to(real_dir, target_is_directory=True)
    except OSError:
        pytest.skip("platform does not support symlinks")
    record = load_document("doc.txt", root=link)
    assert record.content == "data"
    assert record.path == "doc.txt"


def test_rejects_invalid_utf8_bytes(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "bad.txt"
    doc.write_bytes(b"\xff\xfe\x00\x01")
    with pytest.raises(DocumentLoadError):
        load_document("bad.txt", root=tmp_path)


def test_load_documents_fails_on_one_bad_path_without_partial_return(tmp_path: pathlib.Path) -> None:
    (tmp_path / "good.txt").write_text("ok", encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_documents(["good.txt", "missing.txt", "good.txt"], root=tmp_path)


def test_sha256_is_lowercase_hex(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    record = load_document("test.txt", root=tmp_path)
    assert record.sha256 == record.sha256.lower()
    assert len(record.sha256) == 64


def test_default_max_document_bytes_is_positive_int() -> None:
    assert isinstance(DEFAULT_MAX_DOCUMENT_BYTES, int)
    assert DEFAULT_MAX_DOCUMENT_BYTES > 0


def test_document_loader_error_is_base_exception() -> None:
    assert issubclass(DocumentRootError, DocumentLoaderError)
    assert issubclass(DocumentPathError, DocumentLoaderError)
    assert issubclass(DocumentLoadError, DocumentLoaderError)


def test_document_record_value_equality(tmp_path: pathlib.Path) -> None:
    doc = tmp_path / "test.txt"
    doc.write_text("data", encoding="utf-8")
    r1 = load_document("test.txt", root=tmp_path)
    r2 = load_document("test.txt", root=tmp_path)
    assert r1 == r2
