"""Evidence manifest builder and validator for umbrella agent milestone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def build_evidence_manifest(
    milestone: str,
    commit_before: str,
    commit_after: str,
    artifacts: list[dict[str, Any]],
    validation_commands: list[dict[str, Any]],
    source_boundary: dict[str, Any],
    final_verdict: str,
) -> dict[str, Any]:
    """Build a structured evidence manifest."""
    return {
        "milestone": milestone,
        "status": "PASS" if final_verdict == "ACCEPTED" else "FAIL",
        "repository_commit_before": commit_before,
        "repository_commit_after": commit_after,
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "artifacts": artifacts,
        "validation_commands": validation_commands,
        "source_boundary": source_boundary,
        "final_verdict": final_verdict,
    }


def hash_file(path: Path) -> str:
    """Compute SHA256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    """Validate evidence manifest against required rules."""
    errors = []

    if not manifest.get("milestone"):
        errors.append("Missing milestone field")

    if not manifest.get("repository_commit_before"):
        errors.append("Missing repository_commit_before")

    if not manifest.get("artifacts"):
        errors.append("Missing artifacts list")
    else:
        for i, art in enumerate(manifest["artifacts"]):
            path_str = art.get("path", "")
            if not path_str:
                errors.append(f"Artifact {i}: missing path")
                continue
            resolved = (repo_root / path_str).resolve()
            if not resolved.exists():
                errors.append(f"Artifact {i}: referenced path '{path_str}' does not exist")
            if art.get("sha256") and resolved.exists():
                actual = hash_file(resolved)
                if actual != art["sha256"]:
                    errors.append(f"Artifact {i}: hash mismatch for '{path_str}'")
            if art.get("required") and not art.get("exists"):
                errors.append(f"Artifact {i}: required artifact '{path_str}' marked as missing")
            if "persistence" not in art:
                errors.append(f"Artifact {i}: missing persistence field")

    if not manifest.get("validation_commands"):
        errors.append("Missing validation_commands")
    else:
        for i, cmd in enumerate(manifest["validation_commands"]):
            if cmd.get("exit_code") is None:
                errors.append(f"Command {i}: missing exit_code")
            if not cmd.get("result"):
                errors.append(f"Command {i}: missing result")

    sb = manifest.get("source_boundary", {})
    if sb.get("l0_modified"):
        errors.append("L0/ was modified")

    if manifest.get("final_verdict") not in ("ACCEPTED", "REJECTED"):
        errors.append(f"Invalid final_verdict: {manifest.get('final_verdict')}")

    return errors
