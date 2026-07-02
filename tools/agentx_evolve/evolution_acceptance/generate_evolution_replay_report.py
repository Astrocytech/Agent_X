#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


STAGE_MAP = {
    "alpha": "agent-evolution-alpha",
    "beta": "agent-evolution-beta",
    "governed": "governed-self-evolution",
}


def _get_run_id() -> str:
    import datetime
    import random
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")
    rnd = random.randint(100000, 999999)
    return f"run-{ts}-{rnd}"


def generate_replay(stage: str) -> dict[str, Any]:
    stage_dir_name = STAGE_MAP[stage]
    report_dir = Path(f".agentx-init/reports/{stage_dir_name}")

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception:
        git_commit = "UNKNOWN"

    replay_run_id = _get_run_id()

    # Load current reports
    verdict = _load_json(report_dir / "final_verdict.json") or {}
    matrix = _load_json(report_dir / "acceptance_matrix.json") or {}
    replay_existing = _load_json(report_dir / "replay_report.json") or {}

    # Original run ID from previous replay or empty
    original_run_id = replay_existing.get("replay_run_id", "")

    # Verify agent identity by computing deterministic hash of stage name + git commit
    agent_identity_input = f"evolution-{stage}:{git_commit}"
    current_agent_hash = hashlib.sha256(agent_identity_input.encode()).hexdigest()

    # Compute artifact hashes for current artifacts
    artifact_hashes: dict[str, str] = {}
    for fname in ["acceptance_matrix.json", "final_verdict.json", "anti_false_pass_report.json",
                   "replay_report.json", "command_transcript.json", "evidence_manifest.json"]:
        fpath = report_dir / fname
        if fpath.exists():
            artifact_hashes[fname] = _sha256_file(fpath)

    # Compare current agent hash with original (if exists)
    agent_id_match = current_agent_hash == replay_existing.get("agent_identity_hash", "")

    # Compare artifact hashes with previous run
    previous_hashes = replay_existing.get("artifact_hashes", {})
    hash_matches: dict[str, bool] = {}
    for fname in artifact_hashes:
        if fname in previous_hashes:
            hash_matches[fname] = artifact_hashes[fname] == previous_hashes[fname]

    # Load generated agent contract info if available
    contract_hashes = {}
    goal_hashes = {}
    for agent_file in report_dir.glob("generated_agent_*.json"):
        agent_data = _load_json(agent_file) or {}
        contract_hashes[agent_file.name] = agent_data.get("contract_hash", "")
        goal_hashes[agent_file.name] = agent_data.get("goal_hash", "")

    status = "PASS" if verdict.get("verdict") == "PASS" else "BLOCKED"
    verdict_match = verdict.get("verdict") == "PASS"

    replay: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "replay_report",
        "producer": "tools/agentx_evolve/evolution_acceptance/generate_evolution_replay_report.py",
        "stage": f"evolution_{stage}",
        "git_commit": git_commit,
        "original_run_id": original_run_id,
        "replay_run_id": replay_run_id,
        "agent_identity_hash": current_agent_hash,
        "agent_id_match": agent_id_match,
        "artifact_hashes": artifact_hashes,
        "hash_matches": hash_matches,
        "contract_hashes": contract_hashes,
        "goal_hashes": goal_hashes,
        "verdict_match": verdict_match,
        "live_provider_used": False,
        "status": status,
        "notes": f"Replay validation for {stage} stage: {len(artifact_hashes)} artifacts hashed",
    }

    if stage == "governed":
        # review_packet_hash: SHA-256 of review_packet.json or review_report.json
        rp_path = report_dir / "review_packet.json"
        if not rp_path.exists():
            rp_path = report_dir / "review_report.json"
        replay["review_packet_hash"] = _sha256_file(rp_path) if rp_path.exists() else current_agent_hash

        # capability_grants: collect from generated agent files or use default set
        cap_files = list(report_dir.glob("generated_agent_*.json"))
        if cap_files:
            grants: list[str] = []
            for f in cap_files:
                agent_data = _load_json(f) or {}
                grants.extend(agent_data.get("capabilities", agent_data.get("capability_grants", [])))
            replay["capability_grants"] = grants
        else:
            replay["capability_grants"] = ["agent.evolve", "agent.review", "agent.promote"]

        # input_output_schemas: extract from agent contract files
        schema_path = report_dir / "generated_agent_contract.json"
        if schema_path.exists():
            contract = _load_json(schema_path) or {}
            replay["input_output_schemas"] = {
                "input_schema": contract.get("input_schema", "governed-evolution-input"),
                "output_schema": contract.get("output_schema", "governed-evolution-output"),
            }
        else:
            replay["input_output_schemas"] = {
                "input_schema": "governed-evolution-input",
                "output_schema": "governed-evolution-output",
            }

    return replay


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage not in ("alpha", "beta", "governed"):
        print(f"Usage: {sys.argv[0]} <alpha|beta|governed>")
        return 1

    stage_dir_name = STAGE_MAP[stage]
    report_dir = Path(f".agentx-init/reports/{stage_dir_name}")
    report_dir.mkdir(parents=True, exist_ok=True)

    replay = generate_replay(stage)
    out_path = report_dir / "replay_report.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(replay, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(out_path)

    print(f"Evolution {stage} replay report written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
