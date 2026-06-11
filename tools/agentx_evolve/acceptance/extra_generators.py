"""Offline evidence bundle + proofs index generator.

Produces:
  1. offline_evidence_bundle.tar.gz — tarball of all reports, proof, manifests
  2. proofs_index.json — map of all proof types to their artifact paths

Usage:
    python3 extra_generators.py [--report-dir PATH]
"""
from __future__ import annotations

import json
import os
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

REPORT_DIR = Path(os.environ.get("AGENTX_REPORT_DIR", ".agentx-init/reports"))


def _collect_artifacts() -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {}
    for p in REPORT_DIR.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(REPORT_DIR).as_posix()
        ext = p.suffix.lower()
        if ext in (".json",):
            categories.setdefault("json_reports", []).append(rel)
        elif ext in (".md",):
            categories.setdefault("markdown_reports", []).append(rel)
        elif ext in (".txt",):
            categories.setdefault("text_reports", []).append(rel)
        elif ext in (".tar", ".gz", ".zip"):
            categories.setdefault("archives", []).append(rel)
        else:
            categories.setdefault("other", []).append(rel)
    return categories


def generate_proofs_index() -> dict:
    artifacts = _collect_artifacts()
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_dir": str(REPORT_DIR),
        "artifact_categories": artifacts,
        "proof_artifacts": {
            "proof_bundle": "functional_runtime_mvp_proof_bundle.json",
            "scope_map": "functional_runtime_mvp_scope_map.json",
            "final_verdict": "functional_runtime_mvp_final_verdict.json",
            "command_transcript": "functional_runtime_mvp_command_transcript.json",
            "evidence_manifest": "functional_runtime_mvp_evidence_manifest.json",
        },
    }
    idx_path = REPORT_DIR / "proofs_index.json"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    idx_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return index


def build_offline_bundle() -> str:
    bundle_path = REPORT_DIR / "offline_evidence_bundle.tar.gz"
    with tarfile.open(bundle_path, "w:gz") as tar:
        for p in REPORT_DIR.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix in (".tar", ".gz") and "offline_evidence_bundle" in p.name:
                continue
            arcname = str(p.relative_to(REPORT_DIR.parent))
            tar.add(p, arcname=arcname)
    return str(bundle_path)


def main() -> int:
    try:
        index = generate_proofs_index()
        print(f"Proofs index: {len(index['artifact_categories'])} categories")
        bundle = build_offline_bundle()
        size = os.path.getsize(bundle)
        print(f"Offline bundle: {bundle} ({size} bytes)")
        return 0
    except OSError as e:
        print(f"FATAL: extra_generators failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
