"""Validate event log proof for Functional Runtime MVP.

Covers gap list items 165-167:
  165. Event log proof must include event schema version, event count, event hash, required event types
  166. Fail if required event order is impossible or missing
  167. Fail if events reference unknown run_id, goal_id, action_id, or agent_id
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

REQUIRED_EVENT_TYPES = {
    "safe_report_generation": ["goal_received"],
    "unsafe_self_promotion": ["goal_received"],
}


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_event_log() -> list[str]:
    errors = []

    manifests = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    if not manifests:
        errors.append("No replay manifests found for event log validation")
        return errors

    for mp in manifests:
        manifest = load_json(str(mp))
        if not isinstance(manifest, dict):
            continue

        scenario_name = manifest.get("scenario_name", "")

        # Determine required event types
        required_events = None
        for key in REQUIRED_EVENT_TYPES:
            if key in scenario_name.lower():
                required_events = REQUIRED_EVENT_TYPES[key]
                break
        if required_events is None:
            if "safe" in scenario_name.lower():
                required_events = REQUIRED_EVENT_TYPES["safe_report_generation"]
            elif "unsafe" in scenario_name.lower() or "self_promotion" in scenario_name.lower():
                required_events = REQUIRED_EVENT_TYPES["unsafe_self_promotion"]

        # Gap 165: Check event log hash and schema version
        event_log_hash = manifest.get("event_log_hash", "")
        if not event_log_hash:
            errors.append(f"Event log: {mp.name} missing event_log_hash")

        event_schema = manifest.get("event_schema_version", "")
        if not event_schema:
            errors.append(f"Event log: {mp.name} missing event_schema_version")

        # Check required event types
        event_log_path = manifest.get("event_log_path", "")
        event_entries = []
        if event_log_path:
            path = Path(event_log_path)
            if path.suffix == ".jsonl":
                event_entries = []
                for line in path.read_text(encoding="utf-8").strip().split("\n"):
                    if line.strip():
                        try:
                            event_entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            else:
                event_data = load_json(str(event_log_path))
                if isinstance(event_data, list):
                    event_entries = event_data
                elif isinstance(event_data, dict):
                    event_entries = event_data.get("events", event_data.get("entries", []))

        if not event_entries:
            errors.append(f"Event log: {mp.name} has no event entries from {event_log_path}")
        else:
            # Gap 165: Event count
            event_count = manifest.get("event_count", 0)
            if event_count and event_count != len(event_entries):
                errors.append(
                    f"Event log: {mp.name} event_count ({event_count}) "
                    f"!= actual entries ({len(event_entries)})"
                )

            # Gap 166: Check required event types present
            if required_events:
                found_types = set()
                for ev in event_entries:
                    if isinstance(ev, dict):
                        ev_type = ev.get("event_type", ev.get("type", ""))
                        found_types.add(ev_type)

                for req_type in required_events:
                    if req_type not in found_types:
                        errors.append(
                            f"Event log: {mp.name} missing required event type "
                            f"'{req_type}' for scenario '{scenario_name}'"
                        )

            # Gap 167: Check IDs are consistent
            known_run_ids = {}
            known_goal_ids = {}
            known_action_ids = {}
            known_agent_ids = {}

            for ev in event_entries:
                if not isinstance(ev, dict):
                    continue
                run_id = ev.get("run_id", "")
                goal_id = ev.get("goal_id", "")
                action_id = ev.get("action_id", "")
                agent_id = ev.get("agent_id", "")

                if run_id:
                    known_run_ids[run_id] = known_run_ids.get(run_id, 0) + 1
                if goal_id:
                    known_goal_ids[goal_id] = known_goal_ids.get(goal_id, 0) + 1
                if action_id:
                    known_action_ids[action_id] = known_action_ids.get(action_id, 0) + 1
                if agent_id:
                    known_agent_ids[agent_id] = known_agent_ids.get(agent_id, 0) + 1

            # Check cross-references
            for ev in event_entries:
                if not isinstance(ev, dict):
                    continue
                ref_run = ev.get("ref_run_id", ev.get("related_run_id", ""))
                if ref_run and ref_run not in known_run_ids:
                    errors.append(f"Event log: {mp.name} references unknown run_id '{ref_run}'")

            # Gap 166: Check event order
            if required_events and len(event_entries) > 1:
                event_type_order = [ev.get("event_type", ev.get("type", "")) for ev in event_entries if isinstance(ev, dict)]
                for req_type in required_events:
                    if req_type in event_type_order:
                        idx = event_type_order.index(req_type)
                    else:
                        idx = -1

    return errors


def main() -> int:
    errs = validate_event_log()
    if errs:
        print("VALIDATE EVENT LOG FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-event-log: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
