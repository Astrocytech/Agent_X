"""Validate replay manifests and compare verdicts.
Requires persisted replay manifests with actual re-execution. Fails if
no manifests exist or any replayed verdict differs from the original."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
ROOT = Path(__file__).resolve().parent.parent.parent.parent
STATUS_OK = 0
STATUS_FAIL = 1
REPLAY_EXECUTE = ROOT / "tools" / "agentx_evolve" / "acceptance" / "replay_execute.py"


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def run_replay(manifest_path: Path) -> dict | None:
    """Execute the scenario from its persisted manifest and return the replay result."""
    if not REPLAY_EXECUTE.exists():
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(REPLAY_EXECUTE), str(manifest_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def validate_replay() -> list[str]:
    errors = []

    manifest_patterns = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    if not manifest_patterns:
        errors.append("No replay manifests found — persisted replay required")
        return errors

    for mp in manifest_patterns:
        manifest = load_json(str(mp))
        if not manifest or not isinstance(manifest, dict):
            errors.append(f"Invalid replay manifest: {mp}")
            continue

        # Schema validation
        schema_version = manifest.get("schema_version", "")
        if not schema_version:
            errors.append(f"Replay manifest {mp.name} missing schema_version")

        scenario_name = manifest.get("scenario_name", "")
        if not scenario_name:
            errors.append(f"Replay manifest {mp.name} missing scenario_name")

        # Reject report-only replay: state_records_path must differ from event_log_path
        state_path = manifest.get("state_records_path", "")
        event_path = manifest.get("event_log_path", "")
        if state_path and event_path and state_path == event_path:
            errors.append(f"Replay manifest {mp.name} uses same file for state_records and event_log — report-only replay is not sufficient")

        # State records validation
        state_hash = manifest.get("state_records_hash", "")
        if not state_hash:
            errors.append(f"Replay manifest {mp.name} missing state_records_hash")
        if state_path:
            if not Path(state_path).exists():
                errors.append(f"State records path missing: {state_path}")
            if state_path and state_hash and Path(state_path).exists():
                try:
                    actual = hashlib.sha256(Path(state_path).read_bytes()).hexdigest()
                    if actual != state_hash:
                        errors.append(f"State records hash mismatch: {state_path}")
                except OSError:
                    errors.append(f"State records unreadable: {state_path}")

        # Event log validation
        event_hash = manifest.get("event_log_hash", "")
        if not event_hash:
            errors.append(f"Replay manifest {mp.name} missing event_log_hash")
        if event_path:
            if not Path(event_path).exists():
                errors.append(f"Event log path missing: {event_path}")
            if event_path and event_hash and Path(event_path).exists():
                try:
                    actual = hashlib.sha256(Path(event_path).read_bytes()).hexdigest()
                    if actual != event_hash:
                        errors.append(f"Event log hash mismatch: {event_path}")
                except OSError:
                    errors.append(f"Event log unreadable: {event_path}")

        # Artifact refs validation
        for ref in manifest.get("artifact_refs", []):
            ref_path = ref.get("path", "")
            ref_hash = ref.get("hash", "")
            if ref_path and not Path(ref_path).exists():
                errors.append(f"Replay artifact missing: {ref_path}")
            if ref_path and ref_hash and Path(ref_path).exists():
                try:
                    actual = hashlib.sha256(Path(ref_path).read_bytes()).hexdigest()
                    if actual != ref_hash:
                        errors.append(f"Replay artifact hash mismatch: {ref_path}")
                except OSError:
                    errors.append(f"Replay artifact unreadable: {ref_path}")

        # Verdict validation
        final_verdict = manifest.get("final_verdict", "")
        if scenario_name and scenario_name.startswith("safe_") and final_verdict != "PASS":
            errors.append(f"Safe scenario {scenario_name} verdict not PASS: {final_verdict}")
        if scenario_name and scenario_name.startswith("unsafe_") and final_verdict != "DENIED_AND_RECORDED":
            errors.append(f"Unsafe scenario {scenario_name} verdict not DENIED_AND_RECORDED: {final_verdict}")

        # Safety events for unsafe scenarios
        if scenario_name and scenario_name.startswith("unsafe_"):
            safety_events = manifest.get("safety_events", [])
            if not safety_events:
                errors.append(f"Unsafe scenario {scenario_name} missing safety_events")

        # Invariant results for unsafe scenarios
        if scenario_name and scenario_name.startswith("unsafe_"):
            invariant_results = manifest.get("invariant_results", [])
            if not invariant_results:
                errors.append(f"Unsafe scenario {scenario_name} missing invariant_results")

        # ── Real replay execution ──────────────────────────────────────
        replay_result = run_replay(mp)
        if replay_result is None:
            errors.append(f"Replay execution failed for {mp.name} — replay_execute.py not available or errored")
        elif not replay_result.get("match", False):
            errors.append(
                f"Replay verdict mismatch for {scenario_name}: "
                f"replayed={replay_result.get('replayed_verdict')} "
                f"expected={replay_result.get('expected_verdict')}"
            )

    # Also validate replay report JSON (verdicts must match expected)
    report_path = REPORT_DIR / "functional_runtime_mvp_replay_report.json"
    if report_path.exists():
        try:
            report_data = json.loads(report_path.read_text(encoding="utf-8"))
            rows = report_data if isinstance(report_data, list) else report_data.get("rows", [])
            found_safe = False
            found_unsafe = False
            for item in rows:
                scenario = item.get("scenario", "")
                rv = item.get("replay_verdict", "")
                ov = item.get("original_verdict", "")
                if scenario.startswith("safe_") or scenario == "safe":
                    found_safe = True
                    if rv != "PASS":
                        errors.append(f"Replay report: safe scenario {scenario} replay_verdict not PASS: {rv}")
                if scenario.startswith("unsafe_") or "self_promotion" in scenario.lower():
                    found_unsafe = True
                    if rv != "DENIED_AND_RECORDED":
                        errors.append(f"Replay report: unsafe scenario {scenario} replay_verdict not DENIED_AND_RECORDED: {rv}")
            if not found_safe:
                errors.append("Replay report missing safe scenario row")
            if not found_unsafe:
                errors.append("Replay report missing unsafe scenario row")
            # Also check event_log_hash and state_records_hash in the report
            if isinstance(report_data, dict):
                if not report_data.get("event_log_hash"):
                    errors.append("Replay report missing event_log_hash")
                if not report_data.get("state_records_hash"):
                    errors.append("Replay report missing state_records_hash")
        except (OSError, json.JSONDecodeError):
            errors.append("Replay report JSON is corrupt or unreadable")

    return errors


def main() -> int:
    errs = validate_replay()
    if errs:
        print("VALIDATE REPLAY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-replay: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
