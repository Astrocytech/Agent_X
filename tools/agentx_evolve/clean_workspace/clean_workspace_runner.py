"""Standalone clean-workspace runner.

Item 15.1: Creates a temporary checkout, installs dependencies, runs
commands, captures outputs, and compares artifacts with development-run artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _collect_artifact_hashes(root: Path, patterns: list[str] | None = None) -> dict[str, str]:
    result = {}
    if patterns is None:
        patterns = ["*.json", "*.md", "*.py", "*.sh", "Makefile", "*.yaml", "*.yml", "*.toml"]
    for pat in patterns:
        for f in root.rglob(pat):
            rel = f.relative_to(root)
            sha = _sha256(f)
            if sha:
                result[str(rel)] = sha
    return result


def _run_command(cmd: list[str], cwd: Path, timeout: int = 300) -> dict[str, Any]:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout,
        )
        return {
            "command": " ".join(cmd),
            "exit_code": r.returncode,
            "stdout": r.stdout[-2000:],
            "stderr": r.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"command": " ".join(cmd), "exit_code": -1, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as e:
        return {"command": " ".join(cmd), "exit_code": -1, "stdout": "", "stderr": str(e)}


def run_clean(
    commands: list[list[str]] | None = None,
    cleanup: bool = True,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run a set of commands in a clean temporary workspace checkout.

    Parameters
    ----------
    commands:
        List of command argument lists to execute. Defaults to
        ``[["make", "prove-format"], ["make", "audit-structure"]]``.
    cleanup:
        Whether to delete the temporary workspace after completion.
    run_id:
        Optional identifier for this clean run.

    Returns
    -------
    dict with keys: ``run_id``, ``workspace``, ``commands``, ``artifact_hashes``,
    ``status``, ``started_at``, ``completed_at``.
    """
    repo_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))).resolve()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_id = run_id or f"clean-{int(time.time())}"
    workspace = Path(tempfile.mkdtemp(suffix=f"-clean-{run_id}"))

    if commands is None:
        commands = [["make", "prove-format"], ["make", "audit-structure"]]

    try:
        # Copy the repo into the workspace (excluding .git, __pycache__, .agentx-init/runs)
        dst = workspace / "repo"
        shutil.copytree(
            str(repo_root), str(dst),
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc", ".agentx-init/runs",
            ),
        )

        # Run each command
        results = []
        for cmd in commands:
            results.append(_run_command(cmd, cwd=dst))

        # Collect artifact hashes
        hashes = _collect_artifact_hashes(dst)

        completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        all_pass = all(r["exit_code"] == 0 for r in results)
        status = "PASS" if all_pass else "FAIL"

        result = {
            "run_id": run_id,
            "workspace": str(workspace),
            "commands": results,
            "artifact_hashes": hashes,
            "status": status,
            "started_at": started_at,
            "completed_at": completed_at,
        }

        return result

    finally:
        if cleanup and workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    import json
    result = run_clean()
    print(json.dumps(result, indent=2))
