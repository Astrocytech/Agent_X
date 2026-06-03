from __future__ import annotations

import os
import tarfile
import zipfile
from pathlib import Path
from typing import Any

__all__ = [
    "inspect_archive",
]


def inspect_archive(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else 0,
        "format": None,
        "files": [],
        "warnings": [],
        "errors": [],
    }
    if not result["exists"]:
        result["errors"].append(f"Path does not exist: {path}")
        return result

    suffix = path.suffix.lower()
    name = path.name.lower()

    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        result["format"] = "tar.gz"
    elif suffix == ".zip":
        result["format"] = "zip"
    elif suffix == ".tar":
        result["format"] = "tar"
    elif suffix == ".gz" and not name.endswith(".tar.gz"):
        result["format"] = "gzip"
    elif suffix == ".bz2":
        result["format"] = "bzip2"
    else:
        result["warnings"].append(f"Unknown archive format: {suffix}")

    try:
        if result["format"] in ("tar.gz", "tar", "gzip"):
            _inspect_tar(path, result)
        elif result["format"] == "zip":
            _inspect_zip(path, result)
    except Exception as exc:
        result["errors"].append(f"Inspection failed: {exc}")

    return result


def _inspect_tar(path: Path, result: dict[str, Any]) -> None:
    with tarfile.open(path, "r:*") as tar:
        for member in tar.getmembers():
            result["files"].append({
                "name": member.name,
                "size": member.size,
                "type": "directory" if member.isdir() else "file" if member.isfile() else "other",
            })


def _inspect_zip(path: Path, result: dict[str, Any]) -> None:
    with zipfile.ZipFile(path, "r") as zf:
        for info in zf.infolist():
            result["files"].append({
                "name": info.filename,
                "size": info.file_size,
                "type": "directory" if info.filename.endswith("/") else "file",
            })
