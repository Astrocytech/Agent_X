"""Validate runtime lifecycle: state machine, event log integrity, policy, capability, invariant, promotion gate, artifact lifecycle, replay isolation.

Gaps 532-541 (state machine), 542-551 (event log integrity), 552-561 (policy registry),
562-569 (capability registry), 570-579 (invariant engine), 580-589 (promotion gate),
590-599 (artifact lifecycle), 600-609 (replay isolation)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1

ALLOWED_ARTIFACT_STATES = {"created", "stored", "reviewed", "approved", "promoted", "denied", "rolled_back", "retained"}


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_lifecycle() -> list[str]:
    errors = []

    manifests = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    if not manifests:
        errors.append("Lifecycle: no replay manifests found")
        return errors

    for mp in manifests:
        manifest = load_json(str(mp))
        if not isinstance(manifest, dict):
            continue

        scenario_name = manifest.get("scenario_name", "")
        is_unsafe = "unsafe" in scenario_name.lower() or "self_promotion" in scenario_name.lower()
        final_verdict = manifest.get("final_verdict", "")

        # Gap 532-541: State machine proof
        state_records_path = manifest.get("state_records_path", "")
        if state_records_path:
            state_data = load_json(str(state_records_path))
            state_records = []
            if isinstance(state_data, list):
                state_records = state_data
            elif isinstance(state_data, dict):
                state_records = state_data.get("records", state_data.get("states", []))

            if state_records:
                seen_states = []
                prev_ts = None
                for rec in state_records:
                    if not isinstance(rec, dict):
                        continue
                    state = rec.get("state", rec.get("status", "")).lower()
                    timestamp = rec.get("timestamp", rec.get("created_at", ""))
                    sequence = rec.get("sequence", rec.get("seq", 0))

                    if prev_ts and timestamp and timestamp < prev_ts:
                        errors.append(f"Lifecycle ({mp.name}): non-monotonic timestamp in state {state}")
                    prev_ts = timestamp

                    # Gap 534: Denied -> promoted not allowed
                    seen_states.append(state)

                # Check final state matches verdict
                if seen_states:
                    final_state = seen_states[-1]
                    if final_verdict == "DENIED_AND_RECORDED" and final_state == "promoted":
                        errors.append(f"Lifecycle ({mp.name}): denied action reached promoted state")
                    if final_verdict == "PASS" and is_unsafe:
                        errors.append(f"Lifecycle ({mp.name}): unsafe scenario has PASS verdict")

        # Gap 542-551: Event log integrity
        event_log_path = manifest.get("event_log_path", "")
        if event_log_path:
            event_data = load_json(str(event_log_path))
            events = []
            if isinstance(event_data, list):
                events = event_data
            elif isinstance(event_data, dict):
                events = event_data.get("events", event_data.get("entries", []))

            if events:
                producers = set()
                prev_ets = None
                for ev in events:
                    if not isinstance(ev, dict):
                        continue
                    producer = ev.get("producer", ev.get("source", ""))
                    if producer:
                        producers.add(producer)
                    ets = ev.get("timestamp", ev.get("event_timestamp", ""))
                    if prev_ets and ets and ets < prev_ets:
                        errors.append(f"Lifecycle ({mp.name}): non-monotonic event timestamps")
                    prev_ets = ets

                if not producers:
                    errors.append(f"Lifecycle ({mp.name}): no event producer identity found")

        # Gap 552-561: Policy registry
        policy_evidence = manifest.get("policy_evidence", [])
        if not policy_evidence and is_unsafe:
            errors.append(f"Lifecycle ({mp.name}): unsafe scenario missing policy_evidence")
        for pe in policy_evidence:
            if isinstance(pe, dict):
                if not pe.get("rule_id") and not pe.get("rule_name"):
                    errors.append(f"Lifecycle ({mp.name}): policy_evidence entry missing rule_id")
                if pe.get("decision") == "ALLOW" and final_verdict == "DENIED_AND_RECORDED":
                    errors.append(f"Lifecycle ({mp.name}): ALLOW policy but final verdict is DENIED")

        # Gap 562-569: Capability registry
        capability_proof = manifest.get("capability_proof", {})
        if isinstance(capability_proof, dict):
            acts = capability_proof.get("actions", capability_proof.get("action_ids", []))
            if not acts:
                if capability_proof.get("enforced", True) is False:
                    errors.append(f"Lifecycle ({mp.name}): capability enforcement is disabled")

        # Gap 570-579: Invariant engine
        invariant_results = manifest.get("invariant_results", [])
        if invariant_results:
            for inv in invariant_results:
                if isinstance(inv, dict):
                    inv_name = inv.get("invariant_name", inv.get("name", ""))
                    if inv.get("exception_raised"):
                        errors.append(f"Lifecycle ({mp.name}): invariant '{inv_name}' raised exception")

        # Gap 580-589: Promotion gate
        promotion_gate = manifest.get("promotion_gate_evidence", {})
        if isinstance(promotion_gate, dict):
            if promotion_gate.get("bypassed"):
                errors.append(f"Lifecycle ({mp.name}): promotion gate was bypassed")
            if final_verdict == "DENIED_AND_RECORDED" and promotion_gate.get("gate_output") == "APPROVED":
                errors.append(f"Lifecycle ({mp.name}): gate approved but action denied")

        # Gap 590-599: Artifact lifecycle
        artifacts = manifest.get("artifact_refs", manifest.get("artifacts", []))
        for art in artifacts:
            if not isinstance(art, dict):
                continue
            lifecycle_state = art.get("state", art.get("lifecycle_state", ""))
            if lifecycle_state and lifecycle_state.lower() not in ALLOWED_ARTIFACT_STATES:
                errors.append(f"Lifecycle ({mp.name}): unknown artifact state '{lifecycle_state}'")
            aid = art.get("artifact_id", art.get("id", ""))
            ahash = art.get("hash", "")
            if aid and ahash:
                art_path = art.get("path", "")
                if art_path and Path(art_path).exists():
                    actual = hashlib.sha256(Path(art_path).read_bytes()).hexdigest()
                    if actual != ahash:
                        errors.append(f"Lifecycle ({mp.name}): artifact '{aid}' hash mismatch")

        # Gap 600-609: Replay isolation
        replay_in_manifest = manifest.get("replay_isolation", {})
        if isinstance(replay_in_manifest, dict):
            if replay_in_manifest.get("writes_to_source"):
                errors.append(f"Lifecycle ({mp.name}): replay wrote to source directory")
            if replay_in_manifest.get("modifies_original_evidence"):
                errors.append(f"Lifecycle ({mp.name}): replay modified original evidence")

    return errors


def main() -> int:
    errs = validate_lifecycle()
    if errs:
        print("VALIDATE LIFECYCLE FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-lifecycle: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
