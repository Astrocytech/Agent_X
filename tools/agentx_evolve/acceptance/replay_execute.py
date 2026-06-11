"""Replay a Functional Runtime MVP scenario from its persisted replay manifest.

The manifest is the sole-authoritative source of runtime parameters.
No hardcoded fallback SCENARIO_PARAMS are used — every replay must be
fully determined by the manifest content.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REQUIRED_RUNTIME_FIELDS = [
    "seed",
    "fixed_clock",
    "agent_id",
    "target_agent",
    "review_decision",
    "reviewer",
    "action_type",
]


def replay_scenario(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenario_name = manifest.get("scenario_name", "")
    runtime_ctx = manifest.get("runtime_context", {})

    missing = [f for f in REQUIRED_RUNTIME_FIELDS if f not in runtime_ctx]
    if missing:
        return {
            "scenario_name": scenario_name,
            "manifest_path": str(manifest_path),
            "replayed_verdict": "MISSING_FIELDS",
            "expected_verdict": manifest.get("final_verdict", "UNKNOWN"),
            "match": False,
            "errors": [f"Replay-abort: manifest runtime_context missing required fields: {missing}"],
        }

    seed = runtime_ctx["seed"]
    clock_str = runtime_ctx["fixed_clock"]
    agent_id = runtime_ctx["agent_id"]
    target_agent = runtime_ctx["target_agent"]
    review_decision = runtime_ctx["review_decision"]
    reviewer = runtime_ctx["reviewer"]

    tmp = Path(tempfile.mkdtemp(prefix=f"replay_{scenario_name}_"))
    try:
        from agentx_evolve.runtime.runtime_context import (
            MvpRuntimeContext, MvpSeededRandomness, MvpDeterministicClock,
        )
        from agentx_evolve.workspace.workspace_manager import MvpWorkspaceManager
        from agentx_evolve.artifacts.artifact_store import MvpArtifactStore
        from agentx_evolve.state.state_store import MvpStateStore
        from agentx_evolve.bus.event_bus import MvpEventBus
        from agentx_evolve.lifecycle.action import MvpAction
        from agentx_evolve.gates.decision_gate import MvpDecisionGate
        from agentx_evolve.simulation.simulation_engine import MvpSimulationEngine
        from agentx_evolve.promotion.promotion_gate import MvpPromotionGate
        from agentx_evolve.invariants.invariant_engine import MvpInvariantEngine
        from agentx_evolve.executors.report_generation_executor import MvpReportGenerationExecutor
        from agentx_evolve.observation.observer import MvpObserver
        from agentx_evolve.security.security_envelope import MvpSecurityEnvelope
        from agentx_evolve.transactions.transaction_manager import MvpTransactionManager
        from agentx_evolve.review.review_interface import MvpReviewInterface
        from agentx_evolve.safety.circuit_breaker import MvpCircuitBreaker
        from agentx_evolve.rollback.rollback_controller import MvpRollbackController
        from agentx_evolve.capabilities.capability_graph import MvpCapabilityGraph, CapabilityEntry
        from agentx_evolve.policy.rule_engine import MvpPolicyRuleEngine, MvpPolicyRule
        from agentx_evolve.contracts.contract_registry import MvpContractRegistry, MvpContract
        from agentx_evolve.config.runtime_profile import load_profile
        from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator

        ctx = MvpRuntimeContext()
        ctx.randomness = MvpSeededRandomness(seed)
        ctx.clock = MvpDeterministicClock(clock_str)

        ws = MvpWorkspaceManager(root=tmp / "ws")
        store = MvpArtifactStore(tmp / "artifacts")
        state = MvpStateStore(tmp / "state")
        bus = MvpEventBus(log_path=tmp / "events.jsonl")
        action = MvpAction(
            action_id=f"replay-act-{scenario_name[:4]}",
            action_type="report_generation",
            agent_id=agent_id,
        )
        gate = MvpDecisionGate()
        sim = MvpSimulationEngine()
        prom = MvpPromotionGate()
        inv = MvpInvariantEngine()
        executor = MvpReportGenerationExecutor(store)
        observer = MvpObserver(store, source_dirs=["L0/CODE"])
        ri = MvpReviewInterface()
        cb = MvpCircuitBreaker()
        rb = MvpRollbackController()
        txn_mgr = MvpTransactionManager()
        cap_graph = MvpCapabilityGraph()
        cap_graph.register(CapabilityEntry(
            agent_id=agent_id, capability="execute", target="report",
            validator_required="schema", evidence_required="evidence_log",
        ))
        policy = MvpPolicyRuleEngine()
        policy.add_rule(MvpPolicyRule(
            rule_id="allow-report", scope="action",
            conditions={"action_type": "report_generation"},
            decision="ALLOW", reason="Report generation allowed",
        ))
        contract_reg = MvpContractRegistry()
        contract_reg.register(MvpContract(
            contract_id="report_generation", contract_type="action",
            version="1.0.0",
        ))
        profile = load_profile("STRICT")

        orch = MvpFunctionalOrchestrator()
        for name, inst in [
            ("context", ctx), ("workspace", ws), ("artifact_store", store),
            ("state_store", state), ("event_bus", bus), ("action", action),
            ("decision_gate", gate), ("simulation_engine", sim),
            ("promotion_gate", prom), ("invariant_engine", inv),
            ("executor", executor), ("observer", observer),
            ("review_interface", ri), ("circuit_breaker", cb),
            ("rollback_controller", rb), ("transaction_manager", txn_mgr),
            ("capability_graph", cap_graph), ("policy_engine", policy),
            ("contract_registry", contract_reg), ("runtime_profile", profile),
            ("security_envelope", MvpSecurityEnvelope()),
        ]:
            orch.bind(name, inst)

        context_overrides = dict(runtime_ctx)
        context_overrides.setdefault("target_path", str(tmp / "report.json"))
        context_overrides.setdefault("report_content", {"result": f"replay_{scenario_name}"})
        context_overrides.setdefault("report_name", f"{scenario_name}.json")
        context_overrides.setdefault("requires_rollback", False)
        context_overrides.setdefault("evidence_target", str(tmp / "evidence"))

        result = orch.run_goal(
            f"Replay: {scenario_name}",
            profile_id="STRICT",
            context_overrides=context_overrides,
        )

        return {
            "scenario_name": scenario_name,
            "manifest_path": str(manifest_path),
            "replayed_verdict": result.verdict,
            "expected_verdict": manifest.get("final_verdict", "UNKNOWN"),
            "match": result.verdict == manifest.get("final_verdict", ""),
            "errors": result.errors,
        }
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: replay_execute.py <replay_manifest.json> [--verbose]", file=sys.stderr)
        return 1
    manifest_path = Path(sys.argv[1])
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    result = replay_scenario(manifest_path)
    print(json.dumps(result, indent=2))
    return 0 if result.get("match") else 1


if __name__ == "__main__":
    sys.exit(main())
