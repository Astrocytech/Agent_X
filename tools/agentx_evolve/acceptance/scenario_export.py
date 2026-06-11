"""Export scenario data for replay manifests.

Scenario tests call export_scenario_data() before cleanup when
AGENTX_MVP_SCENARIO_EXPORT_DIR is set.  generate_mvp_reports.py reads
the marker file to get real state/event/log paths for replay manifests.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def export_scenario_data(
    scenario_name: str,
    state_records: list[dict],
    event_log_path: str | Path | None = None,
    runtime_context: dict | None = None,
    invariant_results: list[dict] | None = None,
    safety_events: list[dict] | None = None,
    promotion_decisions: list[dict] | None = None,
    extra_artifacts: list[dict] | None = None,
) -> dict:
    export_dir_env = os.environ.get("AGENTX_MVP_SCENARIO_EXPORT_DIR")
    if not export_dir_env:
        return {}

    export_dir = Path(export_dir_env)
    scenario_dir = export_dir / scenario_name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    # Write state records
    state_path = scenario_dir / "state_records.json"
    state_path.write_text(json.dumps(state_records, indent=2))
    state_hash = hashlib.sha256(state_path.read_bytes()).hexdigest()

    # Copy event log if it exists
    event_dest = scenario_dir / "event_log.jsonl"
    event_hash = ""
    if event_log_path:
        src = Path(event_log_path)
        if src.exists():
            event_dest.write_bytes(src.read_bytes())
            event_hash = hashlib.sha256(event_dest.read_bytes()).hexdigest()

    # Write promotion decisions
    prom_path = scenario_dir / "promotion_decisions.json"
    prom_path.write_text(json.dumps(promotion_decisions or [], indent=2))

    # Write invariant results
    inv_path = scenario_dir / "invariant_results.json"
    inv_path.write_text(json.dumps(invariant_results or [], indent=2))

    # Write safety events
    safety_path = scenario_dir / "safety_events.json"
    safety_path.write_text(json.dumps(safety_events or [], indent=2))

    # Collect artifact refs — copy extra artifact files into the export dir
    artifact_refs = []
    for ap in [state_path, event_dest, prom_path, inv_path, safety_path]:
        if ap.exists() and ap.stat().st_size > 0:
            artifact_refs.append({
                "path": str(ap),
                "hash": hashlib.sha256(ap.read_bytes()).hexdigest(),
            })
    for idx, ea in enumerate(extra_artifacts or []):
        src = Path(ea["path"])
        if src.exists():
            dest = scenario_dir / f"artifact_{idx}_{src.name}"
            dest.write_bytes(src.read_bytes())
            artifact_refs.append({
                "path": str(dest),
                "hash": hashlib.sha256(dest.read_bytes()).hexdigest(),
            })

    marker = {
        "scenario_name": scenario_name,
        "state_records_path": str(state_path),
        "state_records_hash": state_hash,
        "event_log_path": str(event_dest) if event_hash else "",
        "event_log_hash": event_hash,
        "runtime_context": runtime_context or {},
        "artifact_refs": artifact_refs,
        "invariant_results": invariant_results or [],
        "safety_events": safety_events or [],
        "promotion_decisions": promotion_decisions or [],
    }

    # Write marker to export-dir parent (REPORT_DIR)
    marker_path = export_dir.parent / f".scenario-{scenario_name}-paths.json"
    marker_path.write_text(json.dumps(marker, indent=2))

    return marker
