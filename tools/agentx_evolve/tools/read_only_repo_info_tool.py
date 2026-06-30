from __future__ import annotations

from pathlib import Path
from typing import Any


class ReadOnlyRepoInfoTool:
    def __init__(self, repo_root: str | None = None):
        self._repo_root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()

    def get_info(self, path: str = ".") -> dict[str, Any]:
        target = (self._repo_root / path).resolve()
        try:
            target.relative_to(self._repo_root)
        except ValueError:
            return {"error": "path traversal blocked", "status": "DENIED"}

        if not target.exists():
            return {"error": "path not found", "status": "DENIED"}

        info: dict[str, Any] = {
            "path": str(target.relative_to(self._repo_root)),
            "exists": True,
            "is_dir": target.is_dir(),
            "name": target.name,
        }

        if target.is_dir():
            try:
                entries = sorted(target.iterdir())[:100]
                info["entries"] = [e.name for e in entries]
            except PermissionError:
                info["entries"] = []
                info["error"] = "permission denied"

        return info
