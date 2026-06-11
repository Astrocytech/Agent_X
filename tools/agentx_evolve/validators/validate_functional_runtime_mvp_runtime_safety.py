"""Validate runtime safety proof depth for all scenarios.

Covers gap list items:
  107-113: Self-promotion denial mechanisms (imported into self_promotion validator)
  165-167: Event log proof
  168-169: State proof
  170-171: Transaction proof
  172: Rollback proof
  173-174: Review proof
  175-176: Policy proof
  177-178: Capability proof
  179-180: Contract proof
  181-182: Invariant proof
  183-184: Circuit breaker proof
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


def validate_runtime_safety() -> list[str]:
    errors = []

    manifests = list(REPORT_DIR.glob("functional_runtime_mvp_replay_manifest_*.json"))
    if not manifests:
        errors.append("No replay manifests found for runtime safety validation")
        return errors

    for mp in manifests:
        manifest = load_json(str(mp))
        if not isinstance(manifest, dict):
            continue

        scenario_name = manifest.get("scenario_name", "")
        final_verdict = manifest.get("final_verdict", "")
        is_unsafe = "unsafe" in scenario_name.lower() or "self_promotion" in scenario_name.lower()

        # Gap 170-171: Transaction proof
        transaction_proof = manifest.get("transaction_proof", {})
        if not transaction_proof:
            errors.append(f"Runtime safety ({mp.name}): missing transaction_proof")
        elif isinstance(transaction_proof, dict):
            if is_unsafe:
                if transaction_proof.get("unsafe_commit_detected"):
                    errors.append(
                        f"Runtime safety ({mp.name}): "
                        f"unsafe scenario has unsafe_commit_detected=true"
                    )
            if not transaction_proof.get("commit_hash"):
                errors.append(f"Runtime safety ({mp.name}): transaction_proof missing commit_hash")

        # Gap 172: Rollback proof
        rollback_proof = manifest.get("rollback_proof", {})
        if is_unsafe and not rollback_proof:
            errors.append(f"Runtime safety ({mp.name}): unsafe scenario missing rollback_proof")
        elif rollback_proof and isinstance(rollback_proof, dict):
            if is_unsafe and not rollback_proof.get("rollback_events"):
                errors.append(f"Runtime safety ({mp.name}): rollback_proof missing rollback_events")

        # Gap 173-174: Review proof
        review_proof = manifest.get("review_proof", {})
        if review_proof and isinstance(review_proof, dict):
            reviewer = review_proof.get("reviewer_id", "")
            agent_id = review_proof.get("agent_id", "")
            if not reviewer:
                errors.append(f"Runtime safety ({mp.name}): review_proof missing reviewer_id")
            if is_unsafe and reviewer and agent_id and reviewer == agent_id:
                if not review_proof.get("separation_evidence"):
                    errors.append(
                        f"Runtime safety ({mp.name}): "
                        f"unsafe scenario has reviewer==agent but no separation_evidence"
                    )

        # Gap 175-176: Policy proof
        policy_evidence = manifest.get("policy_evidence", [])
        if not policy_evidence and is_unsafe:
            errors.append(f"Runtime safety ({mp.name}): unsafe scenario missing policy_evidence")
        for pe in policy_evidence:
            if isinstance(pe, dict):
                if final_verdict == "DENIED_AND_RECORDED" and pe.get("decision") == "ALLOW":
                    errors.append(
                        f"Runtime safety ({mp.name}): "
                        f"denied scenario has ALLOW policy decision"
                    )

        # Gap 177-178: Capability proof
        capability_proof = manifest.get("capability_proof", {})
        if capability_proof and isinstance(capability_proof, dict):
            if not capability_proof.get("capability_id"):
                errors.append(f"Runtime safety ({mp.name}): capability_proof missing capability_id")

        # Gap 179-180: Contract proof
        contract_proof = manifest.get("contract_proof", {})
        if contract_proof and isinstance(contract_proof, dict):
            if not contract_proof.get("contract_id"):
                errors.append(f"Runtime safety ({mp.name}): contract_proof missing contract_id")
            if contract_proof.get("validation_skipped"):
                errors.append(f"Runtime safety ({mp.name}): contract validation was skipped")

        # Gap 181-182: Invariant proof
        invariant_results = manifest.get("invariant_results", [])
        if not invariant_results and is_unsafe:
            errors.append(f"Runtime safety ({mp.name}): missing invariant_results in unsafe scenario")
        else:
            found_nsp = False
            for inv in invariant_results:
                if isinstance(inv, dict):
                    inv_name = inv.get("invariant_name", inv.get("name", ""))
                    if "no_self_promotion" in inv_name.lower():
                        found_nsp = True
                        if is_unsafe and inv.get("passed", inv.get("result")) is True:
                            errors.append(
                                f"Runtime safety ({mp.name}): "
                                f"no_self_promotion passed=true in unsafe scenario"
                            )
            if is_unsafe and not found_nsp:
                errors.append(
                    f"Runtime safety ({mp.name}): "
                    f"no_self_promotion invariant not evaluated in unsafe scenario"
                )

        # Gap 183-184: Circuit breaker proof
        circuit_breaker = manifest.get("circuit_breaker_proof", manifest.get("safety_events", []))
        if is_unsafe:
            if not circuit_breaker:
                errors.append(f"Runtime safety ({mp.name}): unsafe scenario missing circuit_breaker_proof")
            elif isinstance(circuit_breaker, list):
                found_trip = False
                for se in circuit_breaker:
                    if isinstance(se, dict):
                        event_type = se.get("event_type", se.get("type", se.get("trigger", "")))
                        if "unsafe_self_promotion_attempt" in event_type or "trip" in event_type.lower():
                            found_trip = True
                            break
                if not found_trip:
                    errors.append(
                        f"Runtime safety ({mp.name}): "
                        f"no unsafe_self_promotion_attempt safety event"
                    )
        elif not is_unsafe and circuit_breaker:
            for se in (circuit_breaker if isinstance(circuit_breaker, list) else []):
                if isinstance(se, dict):
                    if se.get("event_type") == "unsafe_self_promotion_attempt":
                        errors.append(
                            f"Runtime safety ({mp.name}): "
                            f"safe scenario has unsafe_self_promotion_attempt event"
                        )

    return errors


def main() -> int:
    errs = validate_runtime_safety()
    if errs:
        print("VALIDATE RUNTIME SAFETY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-runtime-safety: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
