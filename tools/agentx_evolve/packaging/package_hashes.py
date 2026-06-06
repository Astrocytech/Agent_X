from __future__ import annotations

import hashlib
from pathlib import Path

__all__ = [
    "hash_file",
    "hash_directory",
    "verify_hash",
]


def hash_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_directory(path: str | Path) -> dict[str, str]:
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    result: dict[str, str] = {}
    for entry in sorted(root.rglob("*")):
        if entry.is_file():
            rel = str(entry.relative_to(root))
            result[rel] = hash_file(entry)
    return result


def verify_hash(path: str | Path, expected: str) -> bool:
    actual = hash_file(path)
    return actual == expected
