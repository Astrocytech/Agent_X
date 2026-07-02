#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import REPORT_BASE, compute_sha256, load_json

CANONICAL_DIR = REPORT_BASE
ALIAS_DIR = Path(".agentx-init/reports")

ALIAS_MAP: dict[str, str] = {
    "functional_agentx_acceptance_matrix.json": "functional-agentx/acceptance_matrix.json",
    "FUNCTIONAL_AGENTX_ACCEPTANCE_REVIEW.md": "functional-agentx/ACCEPTANCE_REVIEW.md",
    "functional_agentx_final_verdict.json": "functional-agentx/final_verdict.json",
    "functional_agentx_command_transcript.json": "functional-agentx/command_transcript.json",
    "FUNCTIONAL_AGENTX_COMMAND_TRANSCRIPT.md": "functional-agentx/COMMAND_TRANSCRIPT.md",
    "functional_agentx_evidence_manifest.json": "functional-agentx/evidence_manifest.json",
    "functional_agentx_replay_report.json": "functional-agentx/replay_report.json",
    "functional_agentx_anti_false_pass_report.json": "functional-agentx/anti_false_pass_report.json",
}


def generate_aliases() -> list[dict]:
    aliases: list[dict] = []
    for alias_name, canonical_rel in ALIAS_MAP.items():
        canonical_path = CANONICAL_DIR / canonical_rel.split("/", 1)[1] if "/" in canonical_rel else CANONICAL_DIR / canonical_rel
        alias_path = ALIAS_DIR / alias_name

        if not canonical_path.exists():
            aliases.append({
                "alias": str(alias_path),
                "canonical": str(canonical_path),
                "exists": False,
                "hash_match": None,
                "status": "CANONICAL_MISSING",
            })
            continue

        canonical_data = load_json(canonical_path) if canonical_path.suffix == ".json" else None

        alias_path.parent.mkdir(parents=True, exist_ok=True)
        if canonical_data is not None and isinstance(canonical_data, dict):
            alias_entry = dict(canonical_data)
            alias_entry["alias_of"] = str(canonical_path)
            alias_path.write_text(json.dumps(alias_entry, indent=2, sort_keys=True), encoding="utf-8")
        elif canonical_path.suffix == ".md":
            alias_path.write_text(canonical_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            alias_path.write_bytes(canonical_path.read_bytes())

        canonical_hash = compute_sha256(canonical_path)
        alias_hash = compute_sha256(alias_path)
        hash_match = canonical_hash == alias_hash

        if not hash_match and canonical_data is not None:
            aliases.append({
                "alias": str(alias_path),
                "canonical": str(canonical_path),
                "exists": True,
                "hash_match": False,
                "alias_of_metadata": str(canonical_path),
                "canonical_hash": canonical_hash,
                "alias_hash": alias_hash,
                "status": "PASS_WITH_METADATA",
            })
        else:
            aliases.append({
                "alias": str(alias_path),
                "canonical": str(canonical_path),
                "exists": alias_path.exists(),
                "hash_match": hash_match,
                "status": "PASS" if hash_match else "HASH_MISMATCH",
            })
    return aliases


def main() -> int:
    aliases = generate_aliases()
    report = {
        "schema_version": "1.0",
        "artifact_type": "alias_report",
        "producer": "tools/agentx_evolve/final_agentx/generate_functional_agentx_aliases.py",
        "total_aliases": len(aliases),
        "pass": sum(1 for a in aliases if a["status"] in ("PASS", "PASS_WITH_METADATA")),
        "failures": sum(1 for a in aliases if a["status"] not in ("PASS", "PASS_WITH_METADATA")),
        "aliases": aliases,
    }

    out_path = REPORT_BASE / "alias_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Alias report written to {out_path}")
    for a in aliases:
        print(f"  {a['alias']} -> {a['canonical']}: {a['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
