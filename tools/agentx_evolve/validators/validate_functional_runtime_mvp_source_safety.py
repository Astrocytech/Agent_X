"""Validate source safety: no source mutation in safe scenario."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _sha256(path: str) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def _current_git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def validate_source_safety() -> list[str]:
    errors = []

    mutation_report = load_json(str(REPORT_DIR / "functional_runtime_mvp_source_mutation_report.json"))
    if not mutation_report:
        errors.append("Source mutation report missing or invalid")
        return errors

    # Current git commit
    current_commit = _current_git_commit()

    # Check scenario_name
    scenario_name = mutation_report.get("scenario_name", "")
    if not scenario_name:
        errors.append("Source mutation report missing scenario_name")
    elif scenario_name != "safe_report_generation":
        errors.append(f"Source mutation report scenario_name is '{scenario_name}', expected 'safe_report_generation'")

    # Check mutation_detected
    if mutation_report.get("mutation_detected"):
        errors.append("Source mutation detected during safe scenario")

    # Check before_manifest
    before_path_str = mutation_report.get("before_manifest", "")
    if not before_path_str:
        errors.append("Source mutation report missing before_manifest path")
    else:
        before_path = Path(before_path_str)
        if not before_path.exists():
            errors.append(f"Before manifest does not exist: {before_path_str}")
        else:
            # Verify hash matches
            manifest_hash = mutation_report.get("before_manifest_hash", "")
            if not manifest_hash:
                errors.append("Source mutation report missing before_manifest_hash")
            else:
                actual = _sha256(before_path_str)
                if actual != manifest_hash:
                    errors.append(f"Before manifest hash mismatch: expected {manifest_hash}, got {actual}")

    # Check after_manifest
    after_path_str = mutation_report.get("after_manifest", "")
    if not after_path_str:
        errors.append("Source mutation report missing after_manifest path")
    else:
        after_path = Path(after_path_str)
        if not after_path.exists():
            errors.append(f"After manifest does not exist: {after_path_str}")
        else:
            manifest_hash = mutation_report.get("after_manifest_hash", "")
            if not manifest_hash:
                errors.append("Source mutation report missing after_manifest_hash")
            else:
                actual = _sha256(after_path_str)
                if actual != manifest_hash:
                    errors.append(f"After manifest hash mismatch: expected {manifest_hash}, got {actual}")

    # Check source_scope
    source_scope = mutation_report.get("source_scope", [])
    if not source_scope:
        errors.append("Source mutation report missing source_scope or empty")

    # Check file counts
    file_count = mutation_report.get("file_count", 0)
    if file_count == 0:
        errors.append("Source mutation report has file_count == 0 — no files inspected")

    # Check git_commit
    git_commit = mutation_report.get("git_commit", "")
    if not git_commit:
        errors.append("Source mutation report missing git_commit")
    elif current_commit and git_commit != current_commit:
        errors.append(f"Source mutation report git_commit ({git_commit}) does not match current ({current_commit})")

    # Check files_changed, files_added, files_removed are all empty
    files_changed = mutation_report.get("files_changed", [])
    files_added = mutation_report.get("files_added", [])
    files_removed = mutation_report.get("files_removed", [])
    if files_changed:
        errors.append(f"Source mutation report has files_changed: {files_changed}")
    if files_added:
        errors.append(f"Source mutation report has files_added: {files_added}")
    if files_removed:
        errors.append(f"Source mutation report has files_removed: {files_removed}")

    # Before/after manifests must exist
    before = REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_before.json"
    after = REPORT_DIR / "functional_runtime_mvp_source_hash_manifest_after.json"
    if not before.exists():
        errors.append("Source hash manifest before missing")
    if not after.exists():
        errors.append("Source hash manifest after missing")

    # Manifest files must have hashes
    for label, path_obj in [("before", before), ("after", after)]:
        if path_obj.exists():
            data = load_json(str(path_obj))
            if data:
                files = data.get("files", {})
                if not files:
                    errors.append(f"{label.capitalize()} manifest has no file entries")
                for fname, fhash in files.items():
                    if not fhash:
                        errors.append(f"{label.capitalize()} manifest entry has no hash: {fname}")

    return errors


def main() -> int:
    errs = validate_source_safety()
    if errs:
        print("VALIDATE SOURCE SAFETY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-source-safety: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
