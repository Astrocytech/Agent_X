#!/usr/bin/env python3
"""Validate CI evidence: run binding, artifact hashes, raw logs, pinning."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")


def validate() -> list[str]:
    errors: list[str] = []
    path = REPORT_DIR / "ci_evidence_report.json"
    if not path.exists():
        errors.append(f"ci_evidence_report.json not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append("ci_evidence_report.json must be a JSON object")
        return errors

    commit_sha = data.get("commit_sha", "")
    if commit_sha == "UNKNOWN":
        errors.append("commit_sha is UNKNOWN")

    is_ci_run = data.get("is_ci_run", False)
    workflow_run_id = data.get("workflow_run_id")
    conclusion = data.get("workflow_conclusion", "")

    if conclusion in ("success", "PASSED", "PASSED_WITH_RUN_ID"):
        if not workflow_run_id:
            errors.append("CI success claimed without workflow run ID")
        if not data.get("artifact_ids"):
            errors.append("CI success claimed without artifact_ids")
        artifact_hashes = data.get("artifact_hashes", {})
        if not artifact_hashes:
            errors.append("CI success claimed without artifact_hashes")

    if is_ci_run:
        if not data.get("actions_pinned_by_sha"):
            errors.append("CI run but GitHub Actions are not pinned by commit SHA")
        if not data.get("raw_logs_uploaded"):
            errors.append("CI run but raw_logs_uploaded is falsy")
        if not data.get("raw_logs_hash_bound"):
            errors.append("CI run but raw_logs_hash_bound is falsy")

    if conclusion in ("success", "PASSED", "PASSED_WITH_RUN_ID"):
        artifact_hashes = data.get("artifact_hashes", {})
        if artifact_hashes:
            import hashlib
            for artifact_name, artifact_hash in artifact_hashes.items():
                artifact_path = REPORT_DIR / artifact_name
                if artifact_path.exists():
                    actual_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                    if actual_hash != artifact_hash:
                        errors.append(f"CI evidence artifact_hashes mismatch for '{artifact_name}': report says {artifact_hash}, actual is {actual_hash}")

    required_jobs = data.get("required_jobs", [])
    if not required_jobs:
        errors.append("No required jobs listed in CI evidence")

    matrix_python = data.get("matrix_python_versions", "")
    if is_ci_run and not matrix_python:
        errors.append("CI run but matrix_python_versions is empty")

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_ci_evidence",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_ci_evidence.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE CI EVIDENCE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-ci-evidence: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
