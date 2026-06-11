from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_SOURCE_SCOPE = [
    "Makefile",
    "docs/plans/AGENT_X_FUNCTIONAL_RUNTIME_MVP_IMPLEMENTATION_PROMPT.md",
    "tools/agentx_evolve/",
    "tests/system/",
]


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _sha256(path_str: str) -> str:
    try:
        return hashlib.sha256(Path(path_str).read_bytes()).hexdigest()
    except OSError:
        return ""


def collect_source_manifest(
    root: Path,
    include_paths: list[str] | None = None,
) -> dict[str, Any]:
    if include_paths is None:
        include_paths = list(DEFAULT_SOURCE_SCOPE)

    manifest: dict[str, str] = {}
    errors: list[str] = []

    root = root.resolve()

    def _should_skip(p: Path) -> bool:
        return any(part.startswith(".") or part == "__pycache__" for part in p.parts)

    for pattern in include_paths:
        full_path = root / pattern
        if not full_path.exists():
            errors.append(f"Path does not exist: {pattern}")
            continue
        if full_path.is_file():
            rel = str(full_path.relative_to(root))
            try:
                manifest[rel] = hash_file(full_path)
            except OSError as e:
                errors.append(f"Cannot hash {rel}: {e}")
        elif full_path.is_dir():
            for f in sorted(full_path.rglob("*")):
                if f.is_file() and not f.name.startswith(".") and not _should_skip(f):
                    try:
                        rel = str(f.relative_to(root))
                        manifest[rel] = hash_file(f)
                    except OSError as e:
                        errors.append(f"Cannot hash {rel}: {e}")
                    except ValueError:
                        errors.append(f"Path outside root: {f}")

    return {
        "root": str(root),
        "source_scope": sorted(include_paths),
        "files": dict(sorted(manifest.items())),
        "file_count": len(manifest),
        "errors": errors,
    }


def compare_source_manifests(before: dict, after: dict) -> dict[str, Any]:
    before_files = before.get("files", {})
    after_files = after.get("files", {})

    all_keys = sorted(set(before_files.keys()) | set(after_files.keys()))
    changed: list[dict[str, Any]] = []
    added: list[str] = []
    removed: list[str] = []

    for key in all_keys:
        b_hash = before_files.get(key)
        a_hash = after_files.get(key)
        if b_hash is None and a_hash is not None:
            added.append(key)
        elif b_hash is not None and a_hash is None:
            removed.append(key)
        elif b_hash != a_hash:
            changed.append({"file": key, "before": b_hash, "after": a_hash})

    mutation_detected = bool(changed or added or removed)

    return {
        "mutation_detected": mutation_detected,
        "files_changed": changed,
        "files_added": added,
        "files_removed": removed,
        "before_file_count": before.get("file_count", 0),
        "after_file_count": after.get("file_count", 0),
    }


def write_source_mutation_report(
    before: dict,
    after: dict,
    diff: dict,
    output_dir: Path,
    scenario_name: str = "safe_report_generation",
) -> tuple[str, str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    before_path = output_dir / "functional_runtime_mvp_source_hash_manifest_before.json"
    after_path = output_dir / "functional_runtime_mvp_source_hash_manifest_after.json"
    report_path = output_dir / "functional_runtime_mvp_source_mutation_report.json"

    before_path.write_text(json.dumps(before, indent=2), encoding="utf-8")
    after_path.write_text(json.dumps(after, indent=2), encoding="utf-8")

    before_str = str(before_path)
    after_str = str(after_path)

    report = {
        "scenario_name": scenario_name,
        "mutation_detected": diff["mutation_detected"],
        "before_manifest": before_str,
        "before_manifest_hash": _sha256(before_str),
        "after_manifest": after_str,
        "after_manifest_hash": _sha256(after_str),
        "source_scope": before.get("source_scope", []),
        "file_count": diff.get("before_file_count", 0),
        "files_changed": diff["files_changed"],
        "files_added": diff["files_added"],
        "files_removed": diff["files_removed"],
        "before_file_count": diff["before_file_count"],
        "after_file_count": diff["after_file_count"],
        "git_commit": _git_commit(),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return str(before_path), str(after_path), str(report_path)
