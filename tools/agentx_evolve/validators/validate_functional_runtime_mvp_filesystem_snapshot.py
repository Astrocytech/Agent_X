"""Validate filesystem snapshot matches evidence manifest.

Gaps 163-170: snapshot consistency, no hidden-file dependency, manifest alignment.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_filesystem_snapshot() -> list[str]:
    errors = []

    # Item 167: Check for final filesystem snapshot
    snapshot_path = REPORT_DIR / "functional_runtime_mvp_filesystem_snapshot.json"
    if not snapshot_path.exists():
        errors.append("Filesystem-snapshot: 167 - final filesystem snapshot missing (expected functional_runtime_mvp_filesystem_snapshot.json)")
        return errors

    snapshot = load_json(str(snapshot_path))
    if not isinstance(snapshot, dict):
        errors.append("Filesystem-snapshot: 167 - filesystem snapshot does not parse as dict")
        return errors

    snapshot_files = snapshot.get("files", snapshot.get("entries", {}))
    if not snapshot_files or not isinstance(snapshot_files, dict):
        errors.append("Filesystem-snapshot: 167 - snapshot missing 'files' or 'entries' dict")
        return errors

    # Item 168: Validate that final filesystem snapshot matches the evidence manifest
    evidence_manifest = load_json(str(REPORT_DIR / "functional_runtime_mvp_evidence_manifest.json"))
    if not isinstance(evidence_manifest, dict):
        errors.append("Filesystem-snapshot: 168 - evidence manifest missing or invalid")
    else:
        evidence_list = evidence_manifest.get("evidence", [])
        evidence_paths = set()
        for entry in evidence_list:
            if isinstance(entry, dict):
                ev_path = entry.get("file", entry.get("path", ""))
                if ev_path:
                    evidence_paths.add(Path(ev_path).name)

        snapshot_paths = set(snapshot_files.keys())
        for ev_path in evidence_paths:
            snapshot_keys = [k for k in snapshot_files if Path(k).name == Path(ev_path).name or k == ev_path]
            if not snapshot_keys:
                if ev_path not in snapshot_paths:
                    errors.append(f"Filesystem-snapshot: 168 - evidence manifest references '{ev_path}' but not in filesystem snapshot")

    # Item 169: Validate no hidden/debug-only file is required for proof success
    snapshot_paths = list(snapshot_files.keys())
    hidden_or_debug = [p for p in snapshot_paths if
                       Path(p).name.startswith(".") or
                       "debug" in Path(p).name.lower() or
                       "tmp" in Path(p).name.lower() or
                       "temp" in Path(p).name.lower()]

    # Check which reports validators depend on hidden files
    if isinstance(evidence_manifest, dict):
        evidence_list = evidence_manifest.get("evidence", [])
        for entry in evidence_list:
            if isinstance(entry, dict):
                ev_path = entry.get("file", entry.get("path", ""))
                ev_name = Path(ev_path).name
                if ev_name.startswith(".") or "debug" in ev_name.lower():
                    errors.append(f"Filesystem-snapshot: 169 - evidence manifest references hidden/debug file: {ev_path}")

    # Item 170: Check that validators don't depend on record_command_debug.ndjson
    # (the file is intentionally excluded from the evidence manifest by the pipeline)
    debug_path = REPORT_DIR / "record_command_debug.ndjson"
    if debug_path.exists():
        # Check that validators don't depend on debug file
        for validator_py in sorted((REPORT_DIR.parent / "validators").glob("validate_*.py")):
            try:
                text = validator_py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "record_command_debug" in text:
                errors.append(
                    f"Filesystem-snapshot: 170 - validator {validator_py.name} references "
                    f"record_command_debug.ndjson — debug-only dependency"
                )

    # Verify snapshot hash integrity
    for fpath, meta in snapshot_files.items():
        if isinstance(meta, dict):
            expected_hash = meta.get("hash", "")
            if expected_hash:
                full_path = REPORT_DIR / Path(fpath).name
                if full_path.exists():
                    actual = hashlib.sha256(full_path.read_bytes()).hexdigest()
                    if actual != expected_hash:
                        errors.append(f"Filesystem-snapshot: hash mismatch for {fpath}")
                else:
                    full_path_abs = Path(fpath)
                    if full_path_abs.exists():
                        actual = hashlib.sha256(full_path_abs.read_bytes()).hexdigest()
                        if actual != expected_hash:
                            errors.append(f"Filesystem-snapshot: hash mismatch for {fpath}")

    return errors


def main() -> int:
    errs = validate_filesystem_snapshot()
    if errs:
        print("VALIDATE FILESYSTEM SNAPSHOT FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-filesystem-snapshot: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
