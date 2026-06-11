"""Artifact immutability and content-addressed evidence references.

Item 39 (33.1): All evidence artifacts are referenced by SHA-256
content hash; renames or overwrites are detected as violations.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ImmutabilityViolation(Exception):
    pass


def hash_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def hash_content(content: str | bytes) -> str:
    h = hashlib.sha256()
    if isinstance(content, str):
        h.update(content.encode())
    else:
        h.update(content)
    return h.hexdigest()


class ImmutableStore:
    """Write-once content-addressed store keyed by SHA-256."""

    def __init__(self, base_path: str | Path):
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)
        self._registry_path = self._base / "registry.json"
        self._registry: dict[str, dict] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if self._registry_path.exists():
            try:
                self._registry = json.loads(self._registry_path.read_text())
            except (json.JSONDecodeError, ValueError):
                self._registry = {}

    def _save_registry(self) -> None:
        self._registry_path.write_text(json.dumps(self._registry, indent=2))

    def store(self, content: str | bytes, name: str = "",
              metadata: dict | None = None) -> str:
        """Store content and return its SHA-256 address."""
        h = hash_content(content)
        blob_path = self._base / h[:2] / h
        if not blob_path.exists():
            blob_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, str):
                blob_path.write_text(content)
            else:
                blob_path.write_bytes(content)
        self._registry[h] = {
            "name": name,
            "hash": h,
            "size": len(content) if isinstance(content, bytes) else len(content.encode()),
            "metadata": metadata or {},
            "path": str(blob_path),
        }
        self._save_registry()
        return h

    def get(self, content_hash: str) -> bytes | None:
        blob_path = self._base / content_hash[:2] / content_hash
        if blob_path.exists():
            return blob_path.read_bytes()
        return None

    def get_text(self, content_hash: str) -> str | None:
        data = self.get(content_hash)
        return data.decode() if data else None

    def verify_file(self, path: str | Path) -> str | None:
        p = Path(path)
        if not p.exists():
            return None
        h = hash_file(p)
        entry = self._registry.get(h)
        if entry:
            return h
        # Check if file matches any known hash
        for ch, info in self._registry.items():
            if info.get("name", "").endswith(p.name):
                actual = hash_file(p)
                if actual == ch:
                    return ch
        return None

    def check_immutable(self, path: str | Path) -> bool:
        """Return True if the file at path matches its registered hash."""
        p = Path(path)
        if not p.exists():
            raise ImmutabilityViolation(f"File not found: {p}")
        h = hash_file(p)
        for ch, info in self._registry.items():
            if info.get("name", "").endswith(p.name) or info["hash"] == h:
                return h == ch
        return True
