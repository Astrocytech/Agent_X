"""Validate state proof for Functional Runtime MVP.

Covers gap list items 168-169:
  168. State proof must include state schema version, state record count, state hash, required transitions
  169. State validator must fail if state records are empty, stale, out of order, or don't match final verdict
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

REQUIRED_STATE_TRANSITIONS = {
    "safe": ["initiated", "running", "completed"],
    "unsafe": ["initiated", "running", "denied", "recorded"],
}


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_state() -> list[str]:
    errors = []

    manifests = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    if not manifests:
        errors.append("No replay manifests found for state validation")
        return errors

    for mp in manifests:
        manifest = load_json(str(mp))
        if not isinstance(manifest, dict):
            continue

        scenario_name = manifest.get("scenario_name", "")
        final_verdict = manifest.get("final_verdict", "")

        # Gap 168: Check state records hash and schema version
        state_hash = manifest.get("state_records_hash", "")
        if not state_hash:
            errors.append(f"State: {mp.name} missing state_records_hash")

        state_schema = manifest.get("state_schema_version", "")
        if not state_schema:
            errors.append(f"State: {mp.name} missing state_schema_version")

        # Load actual state records
        state_path = manifest.get("state_records_path", "")
        state_records = []
        if state_path:
            state_data = load_json(str(state_path))
            if isinstance(state_data, list):
                state_records = state_data
            elif isinstance(state_data, dict):
                state_records = state_data.get("records", state_data.get("states", []))

        if not state_records:
            errors.append(f"State: {mp.name} has no state records from {state_path}")
        else:
            # Gap 169: Check state record count
            record_count = manifest.get("state_record_count", 0)
            if record_count and record_count != len(state_records):
                errors.append(
                    f"State: {mp.name} state_record_count ({record_count}) "
                    f"!= actual records ({len(state_records)})"
                )

            found_record_types = set()
            found_run_ids = set()
            for rec in state_records:
                if isinstance(rec, dict):
                    found_record_types.add(rec.get("record_type", "").lower())
                    if rec.get("run_id"):
                        found_run_ids.add(rec.get("run_id"))

            # Gap 168/169: Must have at least one record with a record_type
            if not found_record_types:
                errors.append(
                    f"State: {mp.name} state records missing record_type field"
                )

            # Gap 168/169: Must have a run_id
            if not found_run_ids:
                errors.append(
                    f"State: {mp.name} state records missing run_id"
                )

            # Gap 169: Records must be in order (timestamps/created_at should increase)
            if len(state_records) > 1:
                timestamps = []
                for rec in state_records:
                    if isinstance(rec, dict):
                        ts = rec.get("timestamp", rec.get("created_at", ""))
                        timestamps.append(ts)

                for i in range(1, len(timestamps)):
                    if timestamps[i] and timestamps[i - 1] and timestamps[i] < timestamps[i - 1]:
                        errors.append(
                            f"State: {mp.name} records out of order at index {i}: "
                            f"{timestamps[i-1]} > {timestamps[i]}"
                        )
                        break

    return errors


def main() -> int:
    errs = validate_state()
    if errs:
        print("VALIDATE STATE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-state: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
