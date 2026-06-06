from __future__ import annotations
from pathlib import Path
import os

from agentx_evolve.evaluation.evaluation_errors import EVAL_UNTRUSTED_INPUT


def resolve_inside_root(path: Path, root: Path) -> Path:
    resolved = (root / path).resolve()
    root_resolved = root.resolve()
    if not str(resolved).startswith(str(root_resolved)):
        raise ValueError(f"Path {path} escapes root {root}")
    return resolved


def ensure_inside_root(path: Path, root: Path) -> None:
    resolve_inside_root(path, root)


def reject_path_traversal(path_text: str) -> None:
    if ".." in path_text.split(os.sep):
        raise ValueError(f"{EVAL_UNTRUSTED_INPUT}: Path traversal detected: {path_text}")
    p = Path(path_text)
    if ".." in str(p):
        raise ValueError(f"{EVAL_UNTRUSTED_INPUT}: Path traversal detected: {path_text}")


def safe_relative_ref(path: Path, root: Path) -> str:
    resolved = resolve_inside_root(path, root)
    return str(resolved.relative_to(root.resolve()))
