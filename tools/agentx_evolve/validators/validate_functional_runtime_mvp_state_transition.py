"""Validate action/state-machine transition proof and external I/O boundaries.

Gaps 395-403: legal state transitions, I/O boundary model, command-injection resistance.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

LEGAL_TRANSITIONS: dict[str, list[str]] = {
    "goal_received": ["action_proposed", "goal_rejected"],
    "action_proposed": ["action_validated", "action_rejected"],
    "action_validated": ["execution_started", "validation_failed"],
    "execution_started": ["execution_completed", "execution_failed", "execution_timed_out"],
    "execution_completed": ["review_pending", "promotion_pending"],
    "review_pending": ["review_approved", "review_denied"],
    "review_approved": ["promotion_pending", "promoted", "promotion_denied"],
    "promotion_pending": ["promoted", "promotion_denied"],
    "promoted": ["goal_completed", "archived"],
    "execution_failed": ["rollback_started", "goal_failed"],
    "rollback_started": ["rollback_completed", "rollback_failed"],
    "rollback_completed": ["goal_failed"],
    "circuit_breaker_tripped": ["circuit_breaker_reset", "goal_failed"],
    "circuit_breaker_reset": ["goal_received"],
}

TERMINAL_STATES = {"goal_completed", "goal_failed", "goal_rejected", "archived"}

SHELL_DANGEROUS_PATTERNS = [
    re.compile(r"shell\s*=\s*True"),
    re.compile(r"os\.system\("),
    re.compile(r"subprocess\.run\([^)]*shell\s*=\s*True"),
    re.compile(r"subprocess\.Popen\([^)]*shell\s*=\s*True"),
    re.compile(r"eval\s*\("),
    re.compile(r"exec\s*\("),
    re.compile(r"\$\{"),
    re.compile(r"`[^`]+`"),
]


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_state_transition() -> list[str]:
    errors = []

    # Items 395-398: Action/state-machine transition proof
    event_log = load_json(str(REPORT_DIR / "functional_runtime_mvp_event_log.json"))
    if isinstance(event_log, dict):
        events = event_log.get("events", event_log.get("entries", []))
        prev_state = None
        for event in events:
            if not isinstance(event, dict):
                continue
            event_type = event.get("event_type", event.get("type", event.get("state", "")))
            if not event_type:
                continue
            if prev_state is not None:
                legal_next = LEGAL_TRANSITIONS.get(prev_state, [])
                if event_type not in legal_next and event_type not in TERMINAL_STATES:
                    errors.append(
                        f"State-transition: 396 - illegal transition '{prev_state}' -> '{event_type}'"
                    )
                if event_type in TERMINAL_STATES and prev_state in TERMINAL_STATES:
                    errors.append(
                        f"State-transition: 396 - duplicate terminal state '{event_type}' after '{prev_state}'"
                    )
            prev_state = event_type

    # Check action lifecycle for illegal transitions
    state = load_json(str(REPORT_DIR / "functional_runtime_mvp_state.json"))
    if isinstance(state, dict):
        state_records = state.get("records", state.get("states", []))
        for rec in state_records:
            if isinstance(rec, dict):
                rec_state = rec.get("state", rec.get("status", ""))
                rec_prev = rec.get("previous_state", rec.get("prev_state", ""))
                if rec_prev and rec_state:
                    legal_next = LEGAL_TRANSITIONS.get(rec_prev, [])
                    if rec_state not in legal_next:
                        errors.append(
                            f"State-transition: 396 - illegal state transition in state record: "
                            f"'{rec_prev}' -> '{rec_state}'"
                        )

    # Item 398: Terminal verdict from state-machine, not free text
    if isinstance(state, dict):
        final_state = state.get("final_state", state.get("terminal_state", ""))
        final_verdict = state.get("final_verdict", "")
        if final_state and final_verdict:
            if final_state not in TERMINAL_STATES:
                errors.append(f"State-transition: 398 - final state '{final_state}' is not a terminal state")
    else:
        errors.append("State-transition: 398 - state file missing, cannot verify terminal verdict derivation")

    # Items 399-402: External I/O boundary model
    proof_bundle = load_json(str(REPORT_DIR / "functional_runtime_mvp_proof_bundle.json"))
    if isinstance(proof_bundle, dict):
        io_boundary = proof_bundle.get("io_boundary", proof_bundle.get("external_io", {}))
        if not io_boundary:
            errors.append("State-transition: 399 - proof bundle missing io_boundary/external_io declaration")
        elif isinstance(io_boundary, dict):
            network_allowed = io_boundary.get("network", io_boundary.get("network_allowed", None))
            subprocess_allowed = io_boundary.get("subprocess", io_boundary.get("subprocess_allowed", None))
            if network_allowed is None:
                errors.append("State-transition: 399 - io_boundary missing 'network' declaration")
            if subprocess_allowed is None:
                errors.append("State-transition: 399 - io_boundary missing 'subprocess' declaration")

    # Item 403: Network-boundary test (offline mode)
    if isinstance(proof_bundle, dict):
        offline_mode = proof_bundle.get("offline_mode", proof_bundle.get("offline", None))
        if offline_mode is None:
            errors.append("State-transition: 403 - proof bundle missing offline_mode declaration")

    # Check transcript for shell injection risks
    transcript = load_json(str(REPORT_DIR / "functional_runtime_mvp_command_transcript.json"))
    if isinstance(transcript, list):
        for cmd_idx, cmd in enumerate(transcript):
            if isinstance(cmd, dict):
                cmd_str = cmd.get("command", "")
                for pattern in SHELL_DANGEROUS_PATTERNS:
                    if pattern.search(cmd_str):
                        errors.append(
                            f"State-transition: 400 - dangerous shell pattern in command {cmd_idx}: "
                            f"'{cmd_str[:80]}'"
                        )

    return errors


def main() -> int:
    errs = validate_state_transition()
    if errs:
        print("VALIDATE STATE TRANSITION FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-state-transition: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
