#!/usr/bin/env python3
"""Validate evidence manifest: SHA-256 verification, run_id/commit binding,
path containment, namespace correctness, and alias-or-canonical metadata."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import (
    REPORT_BASE, get_canonical_artifact_map, get_git_commit, get_run_id,
)

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")
REPO_ROOT = Path.cwd().resolve()


def _current_run_id() -> str:
    return get_run_id()


def _current_git_commit() -> str:
    return get_git_commit()


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "evidence_manifest.json"
    if not path.exists():
        errors.append(f"evidence_manifest.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("evidence_manifest.json must be a JSON object")
        return errors

    if data.get("schema_version") not in ("1.0", "1.1"):
        errors.append(f"schema_version expected '1.0' or '1.1', got {data.get('schema_version')}")

    if data.get("artifact_type") != "evidence_manifest":
        errors.append("artifact_type must be 'evidence_manifest'")

    # Check run_id and git_commit match current run
    manifest_run_id = data.get("run_id", "")
    manifest_commit = data.get("git_commit", "")
    current_run_id = _current_run_id()
    current_commit = _current_git_commit()
    if manifest_run_id and manifest_run_id != current_run_id:
        errors.append(f"Manifest run_id '{manifest_run_id}' does not match current '{current_run_id}'")
    if manifest_commit and manifest_commit != current_commit:
        errors.append(f"Manifest git_commit '{manifest_commit}' does not match current '{current_commit}'")

    refs = data.get("evidence_refs", [])
    if not refs:
        errors.append("evidence_manifest has no evidence refs")
        return errors

    # Check every ref has namespace, producer, validation_status, canonical_or_alias
    for ref in refs:
        namespace = ref.get("namespace", "")
        if not namespace:
            errors.append(f"Evidence ref {ref.get('name', '?')} missing namespace field")

        if not ref.get("producer"):
            errors.append(f"Evidence ref {ref.get('name', '?')} missing producer field")

        vs = ref.get("validation_status", "")
        if vs not in ("VALIDATED", "UNVALIDATED", "PENDING", "MISSING"):
            errors.append(f"Evidence ref {ref.get('name', '?')} has unknown validation_status '{vs}'")

        canonical_flag = ref.get("canonical_or_alias", "")
        if canonical_flag not in ("canonical", "alias"):
            errors.append(f"Evidence ref {ref.get('name', '?')} has unknown canonical_or_alias '{canonical_flag}'")

        path_str = ref.get("path", "")
        if path_str:
            p = Path(path_str).resolve()
            # Check path containment under repo root
            try:
                p.relative_to(REPO_ROOT)
            except ValueError:
                errors.append(f"Evidence ref {ref.get('name', '?')} path '{path_str}' is outside repo root")

            # Recompute SHA-256 from actual file bytes and compare
            if p.exists():
                actual_sha = hashlib.sha256(p.read_bytes()).hexdigest()
                manifest_sha = ref.get("sha256", "")
                if manifest_sha:
                    if actual_sha != manifest_sha:
                        errors.append(
                            f"Evidence ref {ref.get('name', '?')} SHA-256 mismatch: "
                            f"manifest says {manifest_sha}, actual file is {actual_sha}"
                        )
                else:
                    errors.append(f"Artifact {path_str} exists but has no sha256 in manifest")
            elif ref.get("required") is True:
                errors.append(f"Required evidence ref {ref.get('name', '?')} path '{path_str}' does not exist")
        else:
            errors.append(f"Evidence ref {ref.get('name', '?')} missing path field")

    # Check alias refs do NOT satisfy canonical requirements by path coincidence
    canonical_map = get_canonical_artifact_map()
    ref_namespaces = set(ref.get("namespace", "") for ref in refs)
    for expected_ns in canonical_map:
        if expected_ns not in ref_namespaces:
            errors.append(f"Canonical namespace '{expected_ns}' not found in evidence manifest")

    for ns, expected_files in canonical_map.items():
        canonical_refs = [ref for ref in refs if ref.get("namespace") == ns and ref.get("canonical_or_alias") == "canonical"]
        alias_refs = [ref for ref in refs if ref.get("namespace") == ns and ref.get("canonical_or_alias") == "alias"]
        for expected_file in expected_files:
            found_canonical = any(
                ref.get("name", "").endswith(expected_file) or ref.get("path", "").endswith(expected_file)
                for ref in canonical_refs
            )
            if not found_canonical:
                # Check if only an alias provides this file
                found_alias_only = any(
                    ref.get("name", "").endswith(expected_file) or ref.get("path", "").endswith(expected_file)
                    for ref in alias_refs
                )
                if found_alias_only:
                    errors.append(
                        f"File '{expected_file}' in namespace '{ns}' only present as alias, "
                        f"not canonical — cannot satisfy canonical requirement"
                    )

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_evidence_manifest",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_BASE / "validate_evidence_manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE EVIDENCE MANIFEST FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-evidence-manifest: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
