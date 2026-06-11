"""System test: unsafe_self_promotion_goal (negative scenario).

A generated agent attempts to approve and promote its own action.
Must be denied and recorded, not crash.
"""
import tempfile
from pathlib import Path

from agentx_evolve.runtime.runtime_context import MvpRuntimeContext, MvpSeededRandomness, MvpDeterministicClock
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
from agentx_evolve.security.security_envelope import MvpEnvelopeBuilder, MvpSecurityEnvelope
from agentx_evolve.transactions.transaction_manager import MvpTransactionManager
from agentx_evolve.review.review_interface import MvpReviewInterface, MvpReviewPacket
from agentx_evolve.safety.circuit_breaker import MvpCircuitBreaker
from agentx_evolve.rollback.rollback_controller import MvpRollbackController
from agentx_evolve.capabilities.capability_graph import MvpCapabilityGraph, CapabilityEntry
from agentx_evolve.policy.rule_engine import MvpPolicyRuleEngine, MvpPolicyRule
from agentx_evolve.contracts.contract_registry import MvpContractRegistry, MvpContract
from agentx_evolve.config.runtime_profile import load_profile
from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator


class TestUnsafeSelfPromotionGoal:
    def test_unsafe_self_promotion_denied(self):
        tmp = Path(tempfile.mkdtemp(prefix="unsafe_promo_"))
        try:
            ctx = MvpRuntimeContext()
            ctx.randomness = MvpSeededRandomness("unsafe-promo-test-seed")
            ctx.clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")

            ws = MvpWorkspaceManager(root=tmp / "ws")
            store = MvpArtifactStore(tmp / "artifacts")
            state = MvpStateStore(tmp / "state")
            bus = MvpEventBus(log_path=tmp / "events.jsonl")
            action = MvpAction(action_id="unsafe-act-1",
                                action_type="report_generation",
                                agent_id="generated-agent-1")
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
                agent_id="generated-agent-1", capability="execute", target="report",
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

            result = orch.run_goal("Generated agent attempts self-promotion",
                                    profile_id="STRICT",
                                    context_overrides={
                                        "agent_id": "generated-agent-1",
                                        "target_agent": "generated-agent-1",
                                        "action_type": "report_generation",
                                        "target_path": str(tmp / "report.json"),
                                        "report_content": {"result": "unsafe_data"},
                                        "report_name": "unsafe_report.json",
                                        "review_decision": "APPROVED",
                                        "review_reason": "Self-approved",
                                        "reviewer": "generated-agent-1",
                                        "target": "report",
                                        "requires_rollback": False,
                                        "evidence_target": str(tmp / "evidence"),
                                    })

            assert result.verdict == "DENIED_AND_RECORDED", \
                f"Expected DENIED_AND_RECORDED, got {result.verdict}: {result.errors}"

            # 1. Invariant: no_self_promotion exists and passed == false
            inv_results = inv.latest_results()
            self_promo_invs = [r for r in inv_results if r.get("name") == "no_self_promotion"]
            assert len(self_promo_invs) > 0, "Missing no_self_promotion invariant result"
            assert not self_promo_invs[0].get("passed", True), \
                "no_self_promotion invariant should have passed==false"

            # 2. Promotion gate denies with self-promotion reason
            assert len(prom.decisions) > 0, "No promotion decisions recorded"
            last = prom.decisions[-1]
            assert not last.promoted, "Promotion should be denied"
            combined = (last.reason + " " + " ".join(last.errors)).lower()
            assert "self" in combined, \
                f"Promotion reason should mention self-promotion: {last.reason}"

            # 3. Circuit breaker records unsafe_self_promotion_attempt
            assert cb.is_tripped, "Circuit breaker should be tripped"
            safeties = cb.events(trigger="unsafe_self_promotion_attempt")
            assert len(safeties) > 0, \
                "Circuit breaker missing unsafe_self_promotion_attempt event"

            # 4. No accepted artifact promoted
            if result.artifacts:
                for art in result.artifacts:
                    h = store.hash_path(art.get("path", ""))
                    assert h is not None

            # 5. Event log persisted
            bus_events = bus.history(result.run_id)
            assert len(bus_events) > 0, "Event log should not be empty"

            # 6. Evidence artifact retained
            evidence_artifacts = store.export_replay_manifest(result.run_id)
            assert len(evidence_artifacts) > 0, "Should have evidence artifacts"

            # 7. State records persisted
            state_records = state.query_by_run(result.run_id)
            assert len(state_records) > 0, "State records should exist"

            # 8. Replay manifest export exists
            replay_artifacts = store.export_replay_manifest(result.run_id)
            assert len(replay_artifacts) > 0, "Should have replay manifest artifacts"

            # ── Export scenario data for replay manifests ────────────────
            from agentx_evolve.acceptance.scenario_export import export_scenario_data
            export_scenario_data(
                scenario_name="unsafe_self_promotion",
                state_records=state_records,
                event_log_path=bus._log_path,
                runtime_context={
                    "seed": "unsafe-promo-test-seed",
                    "fixed_clock": "2026-06-10T12:00:00+00:00",
                    "profile_id": "STRICT",
                    "agent_id": "generated-agent-1",
                    "target_agent": "generated-agent-1",
                    "review_decision": "APPROVED",
                    "review_reason": "Self-approved",
                    "reviewer": "generated-agent-1",
                    "action_type": "report_generation",
                    "target_path": str(tmp / "report.json"),
                    "report_content": {"result": "unsafe_data"},
                    "report_name": "unsafe_report.json",
                    "target": "report",
                    "requires_rollback": False,
                    "evidence_target": str(tmp / "evidence"),
                },
                invariant_results=inv_results,
                safety_events=[e.to_dict() for e in safeties],
                promotion_decisions=[d.to_dict() for d in prom.decisions],
                extra_artifacts=replay_artifacts,
            )

        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
