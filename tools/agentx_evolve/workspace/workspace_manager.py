from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any


class MvpWorkspaceManager:
    def __init__(self, root: str | Path | None = None):
        self._root = Path(root) if root else Path(tempfile.mkdtemp(prefix="mvp_ws_"))
        self._run_workspace: Path | None = None
        self._temp_workspace: Path | None = None
        self._artifact_workspace: Path | None = None

    @property
    def root(self) -> Path:
        return self._root

    @property
    def run_dir(self) -> Path | None:
        return self._run_workspace

    @property
    def temp_dir(self) -> Path | None:
        return self._temp_workspace

    @property
    def artifact_dir(self) -> Path | None:
        return self._artifact_workspace

    def create_run_workspace(self, run_id: str) -> Path:
        ws = self._root / run_id
        ws.mkdir(parents=True, exist_ok=True)
        self._run_workspace = ws
        return ws

    def create_temp_workspace(self, run_id: str) -> Path:
        tw = self._root / f"{run_id}_tmp"
        tw.mkdir(parents=True, exist_ok=True)
        self._temp_workspace = tw
        return tw

    def create_artifact_workspace(self, run_id: str) -> Path:
        aw = self._root / f"{run_id}_artifacts"
        aw.mkdir(parents=True, exist_ok=True)
        self._artifact_workspace = aw
        return aw

    def validate_path(self, path: str | Path) -> bool:
        resolved = Path(path).resolve()
        return self._root in resolved.parents or resolved == self._root

    def block_path_traversal(self, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        if not self.validate_path(resolved):
            msg = f"Path traversal blocked: {resolved} is outside workspace root {self._root}"
            raise PermissionError(msg)
        return resolved

    def block_source_pollution(self, source_dirs: list[str | Path]) -> list[Path]:
        blocked = []
        for sd in source_dirs:
            p = Path(sd).resolve()
            if self._root in p.parents:
                blocked.append(p)
        if blocked:
            raise PermissionError(f"Source pollution blocked: {blocked}")
        return blocked

    def block_evidence_overwrite(self, path: str | Path, dry_run: bool = False) -> bool:
        p = Path(path).resolve()
        if self.validate_path(p) and p.exists():
            if not dry_run:
                msg = f"Evidence overwrite blocked: {p} already exists"
                raise PermissionError(msg)
            return False
        return True

    def clean_temp(self) -> None:
        if self._temp_workspace and self._temp_workspace.exists():
            shutil.rmtree(self._temp_workspace)
            self._temp_workspace = None

    def clean_all(self) -> None:
        if self._root.exists():
            shutil.rmtree(self._root)
        self._run_workspace = None
        self._temp_workspace = None
        self._artifact_workspace = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self._root),
            "run_workspace": str(self._run_workspace) if self._run_workspace else None,
            "temp_workspace": str(self._temp_workspace) if self._temp_workspace else None,
            "artifact_workspace": str(self._artifact_workspace) if self._artifact_workspace else None,
        }
