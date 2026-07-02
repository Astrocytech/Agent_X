#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import (
    get_canonical_artifact_map,
    get_git_commit,
    get_run_id,
    REPORT_BASE,
)

STAGE_NAMESPACE_DIRS: dict[str, Path] = {
    "functional-agentx": REPORT_BASE,
    "agent-evolution-alpha": Path(".agentx-init/reports/agent-evolution-alpha"),
    "agent-evolution-beta": Path(".agentx-init/reports/agent-evolution-beta"),
    "governed-self-evolution": Path(".agentx-init/reports/governed-self-evolution"),
    "repo-memory-mvp": Path(".agentx-init/reports/repo-memory-mvp"),
    "generated-agent-git-promotion": Path(".agentx-init/reports/generated-agent-git-promotion"),
}


def _resolve_stage_path(namespace: str, filename: str) -> Path:
    """Resolve the path for a canonical artifact within a namespace."""
    stage_dir = STAGE_NAMESPACE_DIRS.get(namespace)
    if stage_dir:
        return stage_dir / filename
    return REPORT_BASE / filename


def collect_evidence() -> dict:
    git_commit = get_git_commit()
    run_id = get_run_id()

    evidence_refs: list[dict] = []

    canonical_map = get_canonical_artifact_map()

    for namespace, filenames in canonical_map.items():
        for filename in filenames:
            path = _resolve_stage_path(namespace, filename)

            entry: dict = {
                "namespace": namespace,
                "name": f"{namespace}:{filename}",
                "path": str(path),
                "exists": path.exists(),
                "required": True,
                "sha256": None,
                "git_commit": git_commit,
                "run_id": run_id,
                "producer": None,
                "canonical_or_alias": "canonical",
                "validation_status": "PENDING",
            }

            if path.exists():
                entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
                if path.suffix == ".json":
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                        if isinstance(data, dict):
                            vs_raw = data.get(
                                "verdict", data.get("status", "")
                            )
                            entry["validation_status"] = "VALIDATED" if vs_raw in ("PASS", "VALIDATED", "DONE") else "UNVALIDATED"
                            entry["producer"] = data.get("producer", "unknown")
                        else:
                            entry["validation_status"] = "VALIDATED"
                    except Exception:
                        entry["validation_status"] = "UNVALIDATED"
            else:
                entry["validation_status"] = "MISSING"

            evidence_refs.append(entry)

    manifest = {
        "schema_version": "1.0",
        "artifact_type": "evidence_manifest",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_evidence_manifest.py",
        "run_id": run_id,
        "git_commit": git_commit,
        "evidence_refs": evidence_refs,
        "total_refs": len(evidence_refs),
        "present": sum(1 for r in evidence_refs if r["exists"]),
        "missing": sum(1 for r in evidence_refs if not r["exists"] and r["required"]),
        "canonical_namespaces": list(canonical_map.keys()),
    }
    return manifest


def main() -> int:
    REPORT_BASE.mkdir(parents=True, exist_ok=True)
    manifest = collect_evidence()

    out_path = REPORT_BASE / "evidence_manifest.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evidence manifest written to {out_path}")
    print(f"  Total refs: {manifest['total_refs']}")
    print(f"  Present: {manifest['present']}")
    print(f"  Required missing: {manifest['missing']}")
    print(f"  Namespaces: {manifest['canonical_namespaces']}")

    if manifest["missing"] > 0:
        print("WARNING: Some required evidence refs are missing")
        for r in manifest["evidence_refs"]:
            if not r["exists"] and r["required"]:
                print(f"  MISSING: {r['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
