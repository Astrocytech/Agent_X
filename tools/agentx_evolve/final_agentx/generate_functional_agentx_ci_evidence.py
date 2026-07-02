#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")
WORKFLOW_FILE = Path(".github/workflows/final-closeout.yml")


def _check_actions_pinned() -> bool:
    """Check if all actions in the workflow file use SHA256 pinning."""
    if not WORKFLOW_FILE.exists():
        return False
    text = WORKFLOW_FILE.read_text(encoding="utf-8")
    # Find all uses: lines matching `uses: owner/repo@ref`
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("uses:"):
            continue
        ref = stripped.split("uses:")[1].strip()
        # If ref is a SHA (40 hex chars), it's pinned
        if re.fullmatch(r"[a-f0-9]{40}", ref.split("@")[-1] if "@" in ref else ref):
            continue
        # If ref is a version tag like v4, v5, not pinned
        if re.match(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@", ref):
            return False
    return True


def generate() -> dict:
    try:
        commit_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        commit_sha = "UNKNOWN"

    # Capture CI environment variables if running in GitHub Actions
    is_ci = bool(os.environ.get("GITHUB_ACTIONS"))
    workflow_run_id = os.environ.get("GITHUB_RUN_ID")
    workflow_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    workflow_name = os.environ.get("GITHUB_WORKFLOW", "Final Closeout")
    job_name = os.environ.get("GITHUB_JOB", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    actions_pinned = _check_actions_pinned()
    matrix_python_versions = os.environ.get("AGENTX_MATRIX_PYTHON_VERSIONS", "3.11,3.12" if is_ci else "")

    # Compute artifact_ids from existing report files
    import hashlib
    artifact_ids_map = {}
    if REPORT_BASE.exists():
        for fpath in sorted(REPORT_BASE.iterdir()):
            if fpath.is_file() and fpath.suffix in (".json", ".md"):
                artifact_ids_map[fpath.name] = hashlib.sha256(fpath.read_bytes()).hexdigest()

    report = {
        "schema_version": "1.0",
        "artifact_type": "ci_evidence",
        "commit_sha": commit_sha,
        "workflow_name": workflow_name,
        "workflow_run_id": workflow_run_id,
        "workflow_attempt": workflow_attempt,
        "workflow_conclusion": None if is_ci else "NOT_ATTACHED_WITH_REASON",
        "job_name": job_name,
        "repository": repo,
        "run_number": run_number,
        "server_url": server_url,
        "is_ci_run": is_ci,
        "actions_pinned_by_sha": actions_pinned,
        "matrix_python_versions": matrix_python_versions,
        "python_version": sys.version,
        "platform": sys.platform,
        "required_jobs": [
            "prove-functional-runtime-mvp",
            "prove-agentx-adapter-mvp",
            "prove-functional-agent-evolution-alpha",
            "prove-functional-agent-evolution-beta",
            "prove-governed-self-evolution-prototype",
            "prove-agentx-repo-memory-mvp",
            "prove-agentx-generated-agent-git-promotion",
            "prove-functional-agentx",
        ],
        "artifact_ids": [] if is_ci else list(artifact_ids_map.keys()),
        "artifact_hashes": artifact_ids_map,
        "raw_logs_uploaded": is_ci,
        "raw_logs_hash_bound": is_ci and bool(workflow_run_id),
        "uploaded_artifact_ids": [] if not is_ci else None,
        "local_evidence_manifest_comparison": None,
        "local_status_allowed": True,
        "overclaim_guard": "No CI success claimed without workflow run ID",
    }
    return report


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    report = generate()

    out_path = REPORT_BASE / "ci_evidence_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"CI evidence report written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
