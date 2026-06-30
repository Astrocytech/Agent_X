"""Generate adapter-mvp evidence manifest.

Scans .agentx-init/reports/adapter-mvp/ for all proof artifacts,
computes SHA-256 hashes, and writes the evidence manifest.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports") / "adapter-mvp"
MANIFEST_PATH = REPORT_DIR / "adapter_evidence_manifest.json"

SKIP_NAMES = {
    "adapter_evidence_manifest.json",
    "adapter_proof_bundle.json",
    "logs",
}


def _git_commit() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _working_tree_status() -> str:
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10,
        )
        return "dirty" if r.stdout.strip() else "clean"
    except Exception:
        return "unknown"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    evidence_files = sorted(REPORT_DIR.glob("*"))
    evidence_list = []
    for f in evidence_files:
        if f.is_file() and not f.name.startswith(".") and f.name not in SKIP_NAMES:
            h = _sha256(f)
            evidence_list.append({
                "file": f.name,
                "hash": h,
                "type": f.stem,
            })

    wt = _working_tree_status()
    commit = _git_commit()
    manifest = {
        "schema_version": "agentx.evidence_manifest.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "working_tree": wt,
        "claim": "AGENTX_ADAPTER_MVP",
        "ci_workflow_evidence": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit": commit,
            "working_tree_status": wt,
            "environment": "clean_checkout" if wt == "clean" else "modified_checkout",
            "note": "CI integration: verify this commit on a CI runner with `make prove-agentx-adapter-mvp` exiting 0.",
        },
        "evidence": evidence_list,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence manifest: {MANIFEST_PATH} ({len(evidence_list)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
