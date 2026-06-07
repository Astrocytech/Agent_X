from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ALLOWED_ROOTS: list[Path] = []
BLOCKED_PATTERNS: list[str] = []


def configure_path_boundaries(
    allowed_roots: list[str] | None = None,
    blocked_patterns: list[str] | None = None,
) -> None:
    global ALLOWED_ROOTS, BLOCKED_PATTERNS
    if allowed_roots is not None:
        ALLOWED_ROOTS = [Path(r).resolve() for r in allowed_roots]
    if blocked_patterns is not None:
        BLOCKED_PATTERNS = blocked_patterns


def is_path_allowed(target: Path | str) -> bool:
    target_path = Path(target).resolve()
    if not ALLOWED_ROOTS:
        return True
    for root in ALLOWED_ROOTS:
        try:
            target_path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def is_path_blocked(target: Path | str) -> bool:
    target_str = str(target)
    for pattern in BLOCKED_PATTERNS:
        if pattern in target_str:
            return True
    return False


def check_path_safety(target: Path | str) -> dict[str, Any]:
    target_path = Path(target)
    resolved = target_path.resolve()
    result = {
        "original": str(target_path),
        "resolved": str(resolved),
        "exists": resolved.exists(),
        "is_file": resolved.is_file(),
        "is_dir": resolved.is_dir(),
        "is_symlink": resolved.is_symlink(),
        "allowed": True,
        "blocked": False,
        "inside_agentx_init": ".agentx-init" in str(resolved),
        "reasons": [],
    }
    if not is_path_allowed(resolved):
        result["allowed"] = False
        result["reasons"].append("Path outside allowed roots")
    if is_path_blocked(resolved):
        result["blocked"] = True
        result["reasons"].append("Path matches blocked pattern")
    return result
