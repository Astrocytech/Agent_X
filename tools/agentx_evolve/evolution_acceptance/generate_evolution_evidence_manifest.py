#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def generate_manifest(stage: str) -> dict[str, Any]:
    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        git_commit = "UNKNOWN"

    evidence_refs: list[dict] = []
    artifact_names = [
        "acceptance_matrix.json",
        "replay_report.json",
        "anti_false_pass_report.json",
        "final_verdict.json",
    ]

    for name in artifact_names:
        path = report_dir / name
        entry: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "exists": path.exists(),
            "required": True,
            "sha256": None,
        }
        if path.exists():
            entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        evidence_refs.append(entry)

    manifest = {
        "schema_version": "1.0",
        "artifact_type": "evidence_manifest",
        "stage": stage,
        "producer": "tools/agentx_evolve/evolution_acceptance/generate_evolution_evidence_manifest.py",
        "git_commit": git_commit,
        "evidence_refs": evidence_refs,
    }
    return manifest


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    stage_map = {"alpha": "agent-evolution-alpha", "beta": "agent-evolution-beta", "governed": "governed-self-evolution"}
    report_dir = Path(f".agentx-init/reports/{stage_map[stage]}")
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = generate_manifest(stage)
    out_path = report_dir / "evidence_manifest.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evolution {stage} evidence manifest written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
