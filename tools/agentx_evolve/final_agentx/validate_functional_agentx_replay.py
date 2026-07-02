#!/usr/bin/env python3
"""Validate final replay: enforce stage-specific equality fields.

For each mandatory stage, requires the fields specified in
REQUIRED_FIELDS_BY_STAGE. Rejects replay reports that lack
stage-appropriate behavioral equality fields.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_BASE = Path(".agentx-init/reports/functional-agentx")

REQUIRED_FIELDS_BY_STAGE: dict[str, list[str]] = {
    "FRMVP": [
        "original_run_id", "replay_run_id", "live_provider_used",
    ],
    "AdapterMVP": [
        "original_run_id", "replay_run_id", "live_provider_used",
    ],
    "Alpha": [
        "original_run_id", "replay_run_id",
        "agent_identity_hash", "contract_hash", "goal_hash",
        "artifact_hashes", "live_provider_used",
    ],
    "Beta": [
        "original_run_id", "replay_run_id",
        "agent_identity_hash", "contract_hash", "goal_hash",
        "artifact_hashes", "live_provider_used",
    ],
    "Governed": [
        "original_run_id", "replay_run_id",
        "agent_identity_hash", "contract_hash", "goal_hash",
        "review_packet_hash", "capability_grants",
        "input_output_schemas",
        "artifact_hashes", "live_provider_used",
    ],
    "RepoMemory": [
        "original_run_id", "replay_run_id",
        "memory_corpus_hash", "memory_index_hash",
        "artifact_hashes", "live_provider_used",
    ],
    "GitPromotion": [
        "original_run_id", "replay_run_id",
        "git_patch_hash", "promotion_decision", "diff_hash",
        "artifact_hashes", "live_provider_used",
    ],
}


def validate_stage_replay(stage: str, path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        errors.append(f"{stage} replay report not found at {path}")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{stage} replay report invalid JSON: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"{stage} replay report must be a JSON object")
        return errors

    status = data.get("status", data.get("verdict", ""))
    if status == "FAIL":
        errors.append(f"{stage} replay report status is FAIL")

    # Live provider should not be used for replay
    if data.get("live_provider_used") is True:
        errors.append(f"{stage} replay used live provider")

    # Check required fields for this stage
    required = REQUIRED_FIELDS_BY_STAGE.get(stage, [])
    for field in required:
        if not data.get(field):
            errors.append(f"{stage} replay report missing required field: {field}")

    # Check artifact_hashes has required entries
    artifact_hashes = data.get("artifact_hashes", {})
    if artifact_hashes:
        for expected in ("acceptance_matrix.json", "final_verdict.json"):
            if expected not in artifact_hashes:
                errors.append(f"{stage} replay report missing hash for {expected}")

    # Check non-FRMVP/non-Adapter stages have run IDs
    if stage not in ("FRMVP", "AdapterMVP"):
        if not data.get("original_run_id") and not data.get("replay_run_id"):
            errors.append(f"{stage} replay report missing both original_run_id and replay_run_id")

    # Reject equality fields that are present but stale
    if data.get("goal_hash") and len(data.get("goal_hash", "")) != 64:
        errors.append(f"{stage} goal_hash is not a valid SHA-256 (len={len(data.get('goal_hash',''))})")
    if data.get("contract_hash") and len(data.get("contract_hash", "")) != 64:
        errors.append(f"{stage} contract_hash is not a valid SHA-256 (len={len(data.get('contract_hash',''))})")
    if data.get("agent_identity_hash") and len(data.get("agent_identity_hash", "")) != 64:
        errors.append(f"{stage} agent_identity_hash is not a valid SHA-256 (len={len(data.get('agent_identity_hash',''))})")

    return errors


def validate() -> list[str]:
    errors: list[str] = []

    stages = [
        ("FRMVP", Path(".agentx-init/reports/functional_runtime_mvp_replay_report.json")),
        ("AdapterMVP", Path(".agentx-init/reports/adapter-mvp/replay_report.json")),
        ("Alpha", Path(".agentx-init/reports/agent-evolution-alpha/replay_report.json")),
        ("Beta", Path(".agentx-init/reports/agent-evolution-beta/replay_report.json")),
        ("Governed", Path(".agentx-init/reports/governed-self-evolution/replay_report.json")),
        ("RepoMemory", Path(".agentx-init/reports/repo-memory-mvp/replay_report.json")),
        ("GitPromotion", Path(".agentx-init/reports/generated-agent-git-promotion/replay_report.json")),
    ]

    for stage, path in stages:
        errors.extend(validate_stage_replay(stage, path))

    return errors


def main() -> int:
    errs = validate()

    result = {
        "validator": "validate_functional_agentx_replay",
        "passed": len(errs) == 0,
        "errors": errs,
        "summary": "PASS" if len(errs) == 0 else "FAIL",
    }
    out_path = REPORT_BASE / "validate_replay.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if errs:
        print("VALIDATE FINAL REPLAY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-replay: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
