"""Dependency-change review enforcement.

Item 24 (19.2): Dependency files must not change silently; require
justification, alternatives, security note, and approval.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEPENDENCY_PATTERNS = [
    "requirements/*.txt",
    "requirements/*.in",
    "Pipfile*",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "poetry.lock",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "Makefile",
]


@dataclass
class DependencyChangeRequest:
    change_id: str
    file_path: str
    old_hash: str
    new_hash: str
    justification: str = ""
    alternatives_considered: str = ""
    security_notes: str = ""
    affected_commands: list[str] = field(default_factory=list)
    requires_reviewer_approval: bool = True
    rollback_plan: str = ""
    status: str = "pending"  # pending | approved | rejected
    reviewed_by: str = ""
    reviewed_at: str = ""


def detect_changes(repo_root: str | Path) -> list[dict[str, Any]]:
    """Detect dependency files that changed since last committed state."""
    import subprocess
    root = Path(repo_root)
    changes = []

    for pattern in DEPENDENCY_PATTERNS:
        for f in root.glob(pattern):
            rel = str(f.relative_to(root))
            # Current file hash
            h = hashlib.sha256()
            try:
                h.update(f.read_bytes())
                current = h.hexdigest()
            except FileNotFoundError:
                continue

            # Committed hash
            try:
                result = subprocess.run(
                    ["git", "show", f"HEAD:{rel}"],
                    capture_output=True, text=True, cwd=str(root), timeout=30,
                )
                if result.returncode == 0:
                    committed = hashlib.sha256(result.stdout.encode()).hexdigest()
                else:
                    continue
            except Exception:
                continue

            if current != committed:
                changes.append({
                    "file": rel,
                    "old_hash": committed,
                    "new_hash": current,
                    "requires_review": True,
                })

    return changes


def create_change_request(file_path: str, old_hash: str, new_hash: str,
                           justification: str = "",
                           alternatives: str = "",
                           security: str = "") -> dict[str, Any]:
    change = DependencyChangeRequest(
        change_id=f"DEP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        file_path=file_path,
        old_hash=old_hash,
        new_hash=new_hash,
        justification=justification,
        alternatives_considered=alternatives,
        security_notes=security,
    )
    return asdict(change)


def review_change(change: dict[str, Any], approved: bool,
                   reviewer: str = "") -> dict[str, Any]:
    change["status"] = "approved" if approved else "rejected"
    change["reviewed_by"] = reviewer or "automated-policy"
    change["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return change
