from __future__ import annotations

import dataclasses
import hashlib as _hashlib
import pathlib as _pathlib
import typing as _typing

__all__ = [
    "DEFAULT_MAX_DOCUMENT_BYTES",
    "DocumentRecord",
    "DocumentLoaderError",
    "DocumentRootError",
    "DocumentPathError",
    "DocumentLoadError",
    "load_document",
    "load_documents",
]

DEFAULT_MAX_DOCUMENT_BYTES: int = 1048576


class DocumentLoaderError(Exception):
    pass


class DocumentRootError(DocumentLoaderError):
    pass


class DocumentPathError(DocumentLoaderError):
    pass


class DocumentLoadError(DocumentLoaderError):
    pass


@dataclasses.dataclass(frozen=True)
class DocumentRecord:
    path: str
    content: str
    size_bytes: int
    sha256: str
    exists: bool = True


_StrOrPath = _typing.Union[str, _pathlib.Path]


def _resolve_root(root: _StrOrPath) -> _pathlib.Path:
    if isinstance(root, _pathlib.Path):
        r = root
    elif isinstance(root, str):
        if not root:
            raise DocumentRootError("root must not be empty")
        r = _pathlib.Path(root)
    else:
        raise DocumentRootError("root must be str or pathlib.Path")

    try:
        resolved = r.resolve(strict=False)
    except (OSError, ValueError):
        resolved = r.absolute()

    if not resolved.exists():
        raise DocumentRootError("root does not exist")
    if not resolved.is_dir():
        raise DocumentRootError("root is not a directory")
    return resolved


def _validate_max_bytes(max_bytes: int) -> int:
    if isinstance(max_bytes, bool):
        raise DocumentLoadError("max_bytes must not be bool")
    if not isinstance(max_bytes, int):
        raise DocumentLoadError("max_bytes must be an integer")
    if max_bytes < 0:
        raise DocumentLoadError("max_bytes must not be negative")
    return max_bytes


def _validate_path(path: object) -> str:
    if not isinstance(path, str):
        raise DocumentPathError("path must be a string")
    if not path:
        raise DocumentPathError("path must not be empty")
    return path


def _reject_absolute(path: str, resolved_root: _pathlib.Path) -> None:
    p = _pathlib.Path(path)
    if p.is_absolute():
        raise DocumentPathError("path must be relative")


def _reject_traversal(path: str, resolved_root: _pathlib.Path) -> _pathlib.Path:
    target = (resolved_root / path).resolve(strict=False)

    try:
        target.relative_to(resolved_root)
    except ValueError:
        raise DocumentPathError("path escapes root")

    if target.exists():
        try:
            real_target = target.resolve(strict=True)
            real_root = resolved_root.resolve(strict=True)
        except OSError:
            raise DocumentPathError("path cannot be resolved")

        try:
            real_target.relative_to(real_root)
        except ValueError:
            raise DocumentPathError("path escapes root after symlink resolution")

    return target


def _read_file(target: _pathlib.Path, max_bytes: int) -> bytes:
    if not target.exists():
        raise DocumentLoadError("path does not exist")
    if not target.is_file():
        raise DocumentLoadError("path is not a regular file")

    raw = target.read_bytes()
    if len(raw) > max_bytes:
        raise DocumentLoadError("file exceeds maximum allowed size")
    return raw


def _compute_sha256(raw: bytes) -> str:
    return _hashlib.sha256(raw).hexdigest()


def _decode_utf8(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        raise DocumentLoadError("file is not valid UTF-8")


def _normalize_relative(path: _pathlib.Path, resolved_root: _pathlib.Path) -> str:
    return str(path.relative_to(resolved_root).as_posix())


def load_document(
    path: str,
    *,
    root: _StrOrPath,
    max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES,
) -> DocumentRecord:
    resolved_root = _resolve_root(root)
    _validate_max_bytes(max_bytes)
    path_str = _validate_path(path)
    _reject_absolute(path_str, resolved_root)
    target = _reject_traversal(path_str, resolved_root)
    raw = _read_file(target, max_bytes)
    content = _decode_utf8(raw)
    sha256 = _compute_sha256(raw)
    normalized_path = _normalize_relative(target, resolved_root)
    return DocumentRecord(
        path=normalized_path,
        content=content,
        size_bytes=len(raw),
        sha256=sha256,
        exists=True,
    )


def load_documents(
    paths: list[str],
    *,
    root: _StrOrPath,
    max_bytes: int = DEFAULT_MAX_DOCUMENT_BYTES,
) -> list[DocumentRecord]:
    if not isinstance(paths, list):
        raise DocumentPathError("paths must be a list")
    records: list[DocumentRecord] = []
    for p in paths:
        records.append(load_document(p, root=root, max_bytes=max_bytes))
    return records
