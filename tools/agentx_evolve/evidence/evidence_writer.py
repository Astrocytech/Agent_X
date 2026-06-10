"""Evidence writer for umbrella agent milestone artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_evidence(
    artifact_name: str,
    data: dict[str, Any],
    repo_root: Path,
    subdir: str = "umbrella_agent",
) -> dict[str, Any]:
    """Write an evidence artifact to .agentx-init/evidence/{subdir}/."""
    ev_dir = repo_root / ".agentx-init" / "evidence" / subdir
    ev_dir.mkdir(parents=True, exist_ok=True)
    path = ev_dir / f"{artifact_name}.json"
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)
    return {"status": "written", "path": str(path)}


def write_latest(name: str, data: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    """Write the latest version of an artifact to reports/umbrella_agent/."""
    report_dir = repo_root / "reports" / "umbrella_agent"
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{name}.json"
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)
    return {"status": "written", "path": str(path)}
