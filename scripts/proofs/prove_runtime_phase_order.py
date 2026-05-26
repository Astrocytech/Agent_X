"""Prove runtime phase order — one turn must emit phases in correct order."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "CODE"))
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    from core_kernel.public.kernel_service import KernelService
    from core_kernel.models.kernel_requests import KernelTurnRequest

    svc = KernelService()
    resp = svc.run_turn(KernelTurnRequest(
        user_input="phase order test",
        session_id="phase-prove",
    ))

    events = resp.metadata.get("events", [])
    actual_phases = [e.get("phase") for e in events if e.get("phase")]

    expected_order = [
        "input_received",
        "goal_normalized",
        "profile_loaded",
        "task_created",
        "policy_computed",
        "capability_selected",
        "planner_decision_made",
        "governance_checked",
        "approval_continuation_resolved",
        "tool_requested",
        "trace_write_completed",
        "evaluation_completed",
        "memory_written_or_skipped_with_reason",
        "checkpoint_write_completed",
        "output_returned",
    ]

    errors: list[str] = []
    filtered = [p for p in actual_phases if p in expected_order]
    expected_idx = 0
    for phase in filtered:
        if expected_idx >= len(expected_order):
            break
        if phase == expected_order[expected_idx]:
            expected_idx += 1

    if expected_idx != len(expected_order):
        errors.append(
            f"Phase order mismatch: expected subsequence of {len(expected_order)} "
            f"phases, matched {expected_idx}"
        )
        errors.append(f"Expected order: {expected_order}")
        errors.append(f"Actual filtered: {filtered}")

    # Additional governance ordering invariants
    gov_idx = actual_phases.index("governance_checked") if "governance_checked" in actual_phases else -1
    gw_idx = actual_phases.index("tool_gateway_called") if "tool_gateway_called" in actual_phases else -1
    planner_idx = actual_phases.index("planner_decision_made") if "planner_decision_made" in actual_phases else -1

    if gov_idx == -1:
        errors.append("governance_checked phase not found")
    if gw_idx == -1:
        errors.append("tool_gateway_called phase not found")
    if planner_idx == -1:
        errors.append("planner_decision_made phase not found")

    if planner_idx >= 0 and gov_idx >= 0 and planner_idx >= gov_idx:
        errors.append("planner_decision_made must be before governance_checked")
    if gov_idx >= 0 and gw_idx >= 0 and gov_idx >= gw_idx:
        errors.append("governance_checked must be before tool_gateway_called")

    if errors:
        print("RUNTIME PHASE ORDER PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RUNTIME PHASE ORDER PROOF: OK")
    print(f"- phases emitted: {len(actual_phases)}")
    print(f"- required order maintained: {len(expected_order)} phases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
