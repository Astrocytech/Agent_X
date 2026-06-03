import json
import os
import tempfile
from pathlib import Path


def runtime_root(repo_root: Path) -> Path:
    return repo_root / ".agentx-init" / "final_acceptance"


def ensure_runtime_root(repo_root: Path) -> Path:
    root = runtime_root(repo_root)
    root.mkdir(parents=True, exist_ok=True)
    return root


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp." + os.urandom(8).hex())
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


def write_json_artifact(repo_root: Path, artifact_name: str, data: dict) -> Path:
    root = ensure_runtime_root(repo_root)
    path = root / artifact_name
    atomic_write_json(path, data)
    return path


def is_within_runtime_root(repo_root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
        rt_root = runtime_root(repo_root).resolve()
        return rt_root in resolved.parents or resolved == rt_root
    except (OSError, ValueError):
        return False


def reject_path_traversal(repo_root: Path, path: Path) -> None:
    try:
        resolved = path.resolve()
        rt_root = runtime_root(repo_root).resolve()
        if rt_root not in resolved.parents and resolved != rt_root:
            raise ValueError(
                f"Path {path} is outside runtime root {rt_root}"
            )
    except (OSError, ValueError) as e:
        raise ValueError(
            f"Path traversal rejected: {e}"
        )
