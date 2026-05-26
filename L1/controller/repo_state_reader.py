from __future__ import annotations

import dataclasses
import hashlib as _hashlib
import pathlib as _pathlib
import typing as _typing

__all__ = [
    "DEFAULT_MAX_FILE_BYTES",
    "RepoFileInfo",
    "RepoStateReader",
    "RepoStateError",
    "RepoStatePathError",
    "RepoStateReadError",
    "get_repo_file_info",
    "list_repo_files",
    "read_text_file",
]

DEFAULT_MAX_FILE_BYTES: int = 1048576


class RepoStateError(Exception):
    pass


class RepoStatePathError(RepoStateError):
    pass


class RepoStateReadError(RepoStateError):
    pass


@dataclasses.dataclass(frozen=True)
class RepoFileInfo:
    path: str
    relative_path: str
    size_bytes: int
    sha256: str
    is_dir: bool


_StrOrPath = _typing.Union[str, _pathlib.Path]


class RepoStateReader:
    def __init__(self, root: _StrOrPath = "."):
        self._root = _resolve_root(root)

    @property
    def root(self) -> str:
        return str(self._root)

    def list_files(self, glob_pattern: str) -> list[str]:
        if not isinstance(glob_pattern, str):
            raise RepoStatePathError("glob_pattern must be a string")
        if not glob_pattern:
            raise RepoStatePathError("glob_pattern must not be empty")
        results: list[str] = []
        for p in sorted(self._root.rglob(glob_pattern)):
            try:
                rel = p.relative_to(self._root)
            except ValueError:
                continue
            results.append(rel.as_posix())
        return results

    def get_file_info(self, path: str) -> RepoFileInfo:
        target = _resolve_path(path, self._root)
        _reject_directory(target)
        raw = target.read_bytes()
        sha256 = _compute_sha256(raw)
        rel = _to_relative(target, self._root)
        return RepoFileInfo(
            path=str(target),
            relative_path=rel,
            size_bytes=len(raw),
            sha256=sha256,
            is_dir=False,
        )

    def read_text_file(self, path: str) -> str:
        target = _resolve_path(path, self._root)
        _reject_directory(target)
        raw = target.read_bytes()
        if len(raw) > DEFAULT_MAX_FILE_BYTES:
            raise RepoStateReadError("file exceeds maximum allowed size")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            raise RepoStateReadError("file is not valid UTF-8")


def _resolve_root(root: _StrOrPath) -> _pathlib.Path:
    if isinstance(root, _pathlib.Path):
        r = root
    elif isinstance(root, str):
        if not root:
            raise RepoStatePathError("root must not be empty")
        r = _pathlib.Path(root)
    else:
        raise RepoStatePathError("root must be str or pathlib.Path")

    try:
        resolved = r.resolve(strict=False)
    except (OSError, ValueError):
        resolved = r.absolute()

    if not resolved.exists():
        raise RepoStatePathError("root does not exist")
    if not resolved.is_dir():
        raise RepoStatePathError("root is not a directory")
    return resolved


def _resolve_path(path: str, root: _pathlib.Path) -> _pathlib.Path:
    if not isinstance(path, str):
        raise RepoStatePathError("path must be a string")
    if not path:
        raise RepoStatePathError("path must not be empty")

    p = _pathlib.Path(path)
    if p.is_absolute():
        raise RepoStatePathError("path must be relative")

    target = root / p

    try:
        target.relative_to(root)
    except ValueError:
        raise RepoStatePathError("path escapes root")

    real = target.resolve(strict=False)
    if real != target:
        try:
            real.relative_to(root.resolve(strict=True))
        except ValueError:
            raise RepoStatePathError("path escapes root after symlink resolution")

    if not target.exists():
        raise RepoStatePathError("path does not exist")

    return target


def _reject_directory(target: _pathlib.Path) -> None:
    if target.is_dir():
        raise RepoStatePathError("path is a directory")

def _compute_sha256(raw: bytes) -> str:
    return _hashlib.sha256(raw).hexdigest()


def _to_relative(target: _pathlib.Path, root: _pathlib.Path) -> str:
    return str(target.relative_to(root).as_posix())


def get_repo_file_info(path: str, *, root: _StrOrPath = ".") -> RepoFileInfo:
    return RepoStateReader(root).get_file_info(path)


def list_repo_files(glob_pattern: str, *, root: _StrOrPath = ".") -> list[str]:
    return RepoStateReader(root).list_files(glob_pattern)


def read_text_file(path: str, *, root: _StrOrPath = ".") -> str:
    return RepoStateReader(root).read_text_file(path)
