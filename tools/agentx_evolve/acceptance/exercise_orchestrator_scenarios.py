"""Exercise a fully-wired orchestrator to produce runtime artifacts needed by
runtime proof validators (state records, event log, review, promotion).

Creates:
  .agentx-init/reports/state/run_{run_id}.jsonl
  .agentx-init/reports/events/{event_id}.json
  .agentx-init/reports/review/{review_id}.json
  .agentx-init/reports/promotion/{promotion_id}.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports")


def _write_review_packet(packet: dict, run_id: str) -> None:
    review_dir = REPORT_DIR / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    path = review_dir / f"{packet.get('review_id', 'review')}_{run_id}.json"
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


def _write_promotion_decision(decision: dict, run_id: str) -> None:
    prom_dir = REPORT_DIR / "promotion"
    prom_dir.mkdir(parents=True, exist_ok=True)
    path = prom_dir / f"decision_{run_id}.json"
    path.write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")


def _write_event_log(event: dict, run_id: str) -> None:
    events_dir = REPORT_DIR / "events"
    events_dir.mkdir(parents=True, exist_ok=True)
    path = events_dir / f"{event.get('message_id', 'event')}.json"
    path.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    from agentx_evolve.runtime.runtime_context import MvpRuntimeContext, MvpSeededRandomness, MvpDeterministicClock
    from agentx_evolve.workspace.workspace_manager import MvpWorkspaceManager
    from agentx_evolve.artifacts.artifact_store import MvpArtifactStore
    from agentx_evolve.state.state_store import MvpStateStore
    from agentx_evolve.bus.event_bus import MvpEventBus, MvpEvent
    from agentx_evolve.lifecycle.action import MvpAction
    from agentx_evolve.gates.decision_gate import MvpDecisionGate
    from agentx_evolve.simulation.simulation_engine import MvpSimulationEngine
    from agentx_evolve.promotion.promotion_gate import MvpPromotionGate
    from agentx_evolve.security.security_envelope import MvpSecurityEnvelope
    from agentx_evolve.review.review_interface import MvpReviewInterface, MvpReviewPacket
    from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator

    state_dir = REPORT_DIR / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    events_dir = REPORT_DIR / "events"
    events_dir.mkdir(parents=True, exist_ok=True)

    ws_root = REPORT_DIR / "workspace"
    ws_root.mkdir(parents=True, exist_ok=True)

    artifact_root = REPORT_DIR / "artifacts"
    artifact_root.mkdir(parents=True, exist_ok=True)

    ctx = MvpRuntimeContext()
    ctx.randomness = MvpSeededRandomness("exercise-scenario-seed")
    ctx.clock = MvpDeterministicClock("2026-06-28T12:00:00+00:00")

    ws = MvpWorkspaceManager(root=ws_root)
    store = MvpArtifactStore(artifact_root)
    state = MvpStateStore(state_dir)
    bus = MvpEventBus(log_path=events_dir / "events.jsonl")
    action = MvpAction(action_id="exercise-act-1")
    gate = MvpDecisionGate()
    sim = MvpSimulationEngine()
    prom = MvpPromotionGate()
    review = MvpReviewInterface()

    orch = MvpFunctionalOrchestrator()
    orch.bind("context", ctx)
    orch.bind("workspace", ws)
    orch.bind("artifact_store", store)
    orch.bind("state_store", state)
    orch.bind("event_bus", bus)
    orch.bind("action", action)
    orch.bind("decision_gate", gate)
    orch.bind("simulation_engine", sim)
    orch.bind("promotion_gate", prom)
    orch.bind("review_interface", review)
    orch.bind("security_envelope", MvpSecurityEnvelope())

    result = orch.run_goal("exercise full mvp scenario", profile_id="STRICT", context_overrides={
        "agent_id": "agent-exercise-1",
        "action_type": "report_generation",
        "target_path": str(REPORT_DIR / "exercise_report.json"),
        "report_content": {"result": "exercise"},
        "report_name": "exercise_report.json",
        "review_decision": "APPROVED",
        "review_reason": "Auto-approved",
        "reviewer": "orchestrator-exercise",
    })

    run_id = result.run_id
    print(f"Exercise orchestrator: run_id={run_id}, verdict={result.verdict}")

    # Persist review packets
    for pid, packet in review._packets.items():
        _write_review_packet(packet.to_dict(), run_id)

    # Persist promotion decisions
    for decision in prom.decisions:
        _write_promotion_decision(decision.to_dict(), run_id)

    # Persist event bus history as individual files
    for event in bus.history():
        _write_event_log(event.to_dict(), run_id)

    # Verify all required artifacts exist
    state_jsonl = state_dir / f"run_{run_id}.jsonl"
    has_state = state_jsonl.exists() and state_jsonl.stat().st_size > 0
    has_events = any(events_dir.iterdir())
    has_review = any((REPORT_DIR / "review").iterdir())
    has_promotion = any((REPORT_DIR / "promotion").iterdir())

    print(f"  state records: {'PASS' if has_state else 'FAIL'} ({state_jsonl})")
    print(f"  event log:     {'PASS' if has_events else 'FAIL'} ({events_dir})")
    print(f"  review:        {'PASS' if has_review else 'FAIL'} ({REPORT_DIR / 'review'})")
    print(f"  promotion:     {'PASS' if has_promotion else 'FAIL'} ({REPORT_DIR / 'promotion'})")

    if not (has_state and has_events and has_review and has_promotion):
        print("FAIL: one or more required runtime artifacts missing", file=sys.stderr)
        return 1

    print("Exercise orchestrator: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
