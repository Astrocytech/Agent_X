from __future__ import annotations
from pathlib import Path
import hashlib
import json

from agentx_evolve.evaluation.evaluation_errors import EVAL_SOURCE_MUTATION_DETECTED


def capture_source_state(repo_root: Path) -> dict:
    state = {"files": {}, "git_status": None, "errors": []}
    git_dir = repo_root / ".git"
    if git_dir.exists():
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(repo_root),
                capture_output=True, text=True, timeout=10,
            )
            state["git_status"] = result.stdout.strip()
        except Exception as e:
            state["errors"].append(str(e))
    source_dirs = ["tools/agentx_evolve"]
    for sd in source_dirs:
        src = repo_root / sd
        if src.exists():
            for f in sorted(src.rglob("*.py")):
                try:
                    state["files"][str(f.relative_to(repo_root))] = hashlib.sha256(f.read_bytes()).hexdigest()
                except Exception as e:
                    state["errors"].append(f"Failed to hash {f}: {e}")
    return state


def compare_source_state(before: dict, after: dict, allowed_runtime_root: Path) -> dict:
    changes = []
    for fpath, before_hash in before.get("files", {}).items():
        full_path = allowed_runtime_root.parent / fpath
        after_hash = after.get("files", {}).get(fpath)
        if after_hash is None:
            changes.append({"file": fpath, "change": "DELETED", "before": before_hash})
        elif after_hash != before_hash:
            changes.append({"file": fpath, "change": "MODIFIED", "before": before_hash, "after": after_hash})
    for fpath in after.get("files", {}):
        if fpath not in before.get("files", {}):
            changes.append({"file": fpath, "change": "CREATED"})
    return {
        "changes": changes,
        "source_mutated": len(changes) > 0,
        "git_status_before": before.get("git_status"),
        "git_status_after": after.get("git_status"),
    }


def assert_no_source_mutation(before: dict, after: dict, allowed_runtime_root: Path) -> None:
    result = compare_source_state(before, after, allowed_runtime_root)
    if result["source_mutated"]:
        raise RuntimeError(f"{EVAL_SOURCE_MUTATION_DETECTED}: {result['changes']}")
