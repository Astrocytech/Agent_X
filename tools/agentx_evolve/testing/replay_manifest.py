from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_KEYS = [
    "schema_version", "scenario_name", "run_id", "runtime_context",
    "state_records_path", "state_records_hash",
    "event_log_path", "event_log_hash",
]


def create_replay_manifest(
    scenario_name: str,
    run_id: str,
    goal_id: str = "",
    runtime_context: dict | None = None,
    state_records_path: str = "",
    state_records_hash: str = "",
    event_log_path: str = "",
    event_log_hash: str = "",
    artifact_refs: list[dict[str, str]] | None = None,
    gate_decisions: list[dict] | None = None,
    invariant_results: list[dict] | None = None,
    review_decisions: list[dict] | None = None,
    promotion_decisions: list[dict] | None = None,
    safety_events: list[dict] | None = None,
    final_verdict: str = "UNKNOWN",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "scenario_name": scenario_name,
        "run_id": run_id,
        "goal_id": goal_id,
        "runtime_context": runtime_context or {},
        "state_records_path": state_records_path,
        "state_records_hash": state_records_hash,
        "event_log_path": event_log_path,
        "event_log_hash": event_log_hash,
        "artifact_refs": artifact_refs or [],
        "gate_decisions": gate_decisions or [],
        "invariant_results": invariant_results or [],
        "review_decisions": review_decisions or [],
        "promotion_decisions": promotion_decisions or [],
        "safety_events": safety_events or [],
        "final_verdict": final_verdict,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_manifest(manifest: dict) -> list[str]:
    errors = []
    for key in REQUIRED_KEYS:
        if key not in manifest:
            errors.append(f"Missing required key: {key}")
    if "artifact_refs" in manifest:
        for i, ref in enumerate(manifest["artifact_refs"]):
            if "path" not in ref:
                errors.append(f"artifact_refs[{i}] missing path")
            if "hash" not in ref:
                errors.append(f"artifact_refs[{i}] missing hash")
    return errors


def write_replay_manifest(manifest: dict, output_dir: Path, scenario_name: str) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = scenario_name.replace(" ", "_").replace("/", "_")
    path = output_dir / f"functional_runtime_mvp_replay_manifest_{safe_name}.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return str(path)
