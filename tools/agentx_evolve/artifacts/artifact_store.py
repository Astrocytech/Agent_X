from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any


class ArtifactOverwriteError(Exception):
    pass


class ArtifactPathTraversalError(Exception):
    pass


class ArtifactEscapeError(Exception):
    pass


class MvpArtifactStore:
    def __init__(self, root: str | Path):
        self._root = Path(root).resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def _validate_name(self, name: str) -> None:
        if ".." in name or name.startswith("/") or "~" in name:
            raise ArtifactPathTraversalError(
                f"Artifact name rejected (path traversal): {name}"
            )

    def _validate_path(self, resolved: Path) -> None:
        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise ArtifactEscapeError(
                f"Artifact path escapes workspace root: {resolved}"
            )
        if resolved.is_symlink():
            real = resolved.resolve()
            try:
                real.relative_to(self._root)
            except ValueError:
                raise ArtifactEscapeError(
                    f"Artifact symlink escape detected: {resolved} -> {real}"
                )

    def write(self, run_id: str, action_id: str, name: str, data: Any,
              artifact_type: str = "report", agent_id: str = "",
              overwrite_policy: str = "deny") -> dict:
        self._validate_name(name)
        artifact_dir = (self._root / run_id / action_id).resolve()
        self._validate_path(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        path = (artifact_dir / name).resolve()
        self._validate_path(path)

        valid_policies = {"deny", "version", "content_addressed"}
        if overwrite_policy not in valid_policies:
            raise ValueError(
                f"Unknown overwrite_policy={overwrite_policy!r}; "
                f"expected one of {sorted(valid_policies)}"
            )
        if path.exists():
            if overwrite_policy == "deny":
                raise ArtifactOverwriteError(
                    f"Artifact already exists and overwrite_policy=deny: {path}"
                )
            elif overwrite_policy == "version":
                stem = path.stem
                ext = path.suffix
                idx = 1
                while True:
                    versioned = path.parent / f"{stem}.v{idx}{ext}"
                    if not versioned.exists():
                        path = versioned
                        break
                    idx += 1
            elif overwrite_policy == "content_addressed":
                raw = json.dumps(data, indent=2) if not isinstance(data, str) else data
                h = hashlib.sha256(raw.encode()).hexdigest()[:16]
                content_path = path.parent / f"{h}_{path.name}"
                if content_path.exists():
                    existing_content = content_path.read_text(encoding="utf-8")
                    if existing_content != (raw if isinstance(data, str) else json.dumps(data, indent=2)):
                        raise ArtifactOverwriteError(
                            f"Content-addressed artifact collision at {content_path}: "
                            f"existing content differs from new content"
                        )
                path = content_path

        content = json.dumps(data, indent=2) if not isinstance(data, str) else data
        path.write_text(content, encoding="utf-8")
        h = hashlib.sha256(content.encode()).hexdigest()
        record = {
            "path": str(path),
            "name": path.name,
            "type": artifact_type,
            "run_id": run_id,
            "action_id": action_id,
            "agent_id": agent_id,
            "hash": h,
            "size": len(content),
            "overwrite_policy": overwrite_policy,
        }
        meta_path = path.with_suffix(path.suffix + ".meta.json")
        meta_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def read(self, path: str | Path) -> str | None:
        p = Path(path)
        if not p.exists():
            return None
        return p.read_text(encoding="utf-8")

    def hash_path(self, path: str | Path) -> str | None:
        p = Path(path)
        if not p.exists():
            return None
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def classify(self, path: str | Path) -> str:
        p = Path(path)
        meta = p.with_suffix(p.suffix + ".meta.json")
        if meta.exists():
            try:
                rec = json.loads(meta.read_text(encoding="utf-8"))
                return rec.get("type", "unknown")
            except (json.JSONDecodeError, OSError):
                pass
        return "unknown"

    def link_to_run(self, path: str | Path, run_id: str, action_id: str = "") -> bool:
        p = Path(path)
        meta = p.with_suffix(p.suffix + ".meta.json")
        if meta.exists():
            try:
                rec = json.loads(meta.read_text(encoding="utf-8"))
                rec["run_id"] = run_id
                if action_id:
                    rec["action_id"] = action_id
                meta.write_text(json.dumps(rec, indent=2), encoding="utf-8")
                return True
            except (json.JSONDecodeError, OSError):
                pass
        return False

    def prevent_overwrite(self, path: str | Path) -> bool:
        p = Path(path)
        if p.exists():
            name = p.stem
            ext = p.suffix
            idx = 1
            while True:
                backup = p.parent / f"{name}.v{idx}{ext}"
                if not backup.exists():
                    shutil.copy2(p, backup)
                    return True
                idx += 1

    def retain_failed(self, run_id: str, action_id: str, name: str, data: Any) -> dict:
        return self.write(run_id, f"{action_id}_failed", f"failed_{name}", data)

    def validate_ref(self, ref: dict) -> bool:
        path = ref.get("path", "")
        expected_hash = ref.get("hash", "")
        if not path or not Path(path).exists():
            return False
        actual = self.hash_path(path)
        return actual == expected_hash

    def export_replay_manifest(self, run_id: str) -> list[dict]:
        artifacts = []
        run_dir = self._root / run_id
        if not run_dir.exists():
            return artifacts
        for meta_file in run_dir.rglob("*.meta.json"):
            try:
                rec = json.loads(meta_file.read_text(encoding="utf-8"))
                artifacts.append(rec)
            except (json.JSONDecodeError, OSError):
                pass
        return artifacts

    def list_run_artifacts(self, run_id: str) -> list[dict]:
        return self.export_replay_manifest(run_id)
