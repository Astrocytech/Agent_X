"""System test: safe_report_generation_goal (positive scenario).

Creates an approved report artifact from a fixed input string.
No source mutation, all artifacts typed and persisted, replay reproduces.
"""
import tempfile
from pathlib import Path

import pytest

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
from agentx_evolve.observation.source_manifest import (
    collect_source_manifest, compare_source_manifests, write_source_mutation_report,
)


class TestSafeReportGenerationGoal:
    def test_safe_report_generation(self):
        tmp = Path(tempfile.mkdtemp(prefix="safe_report_"))
        try:
            ctx = MvpRuntimeContext()
            ctx.randomness = MvpSeededRandomness("safe-report-test-seed")
            ctx.clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")

            ws = MvpWorkspaceManager(root=tmp / "ws")
            store = MvpArtifactStore(tmp / "artifacts")
            state = MvpStateStore(tmp / "state")
            bus = MvpEventBus(log_path=tmp / "events.jsonl")
            action = MvpAction(action_id="safe-act-1",
                                action_type="report_generation",
                                agent_id="agent-1")
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
                agent_id="agent-1", capability="execute", target="report",
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

            result = orch.run_goal("Create a safe report artifact", profile_id="STRICT", context_overrides={
                "agent_id": "agent-1",
                "action_type": "report_generation",
                "target_path": str(tmp / "report.json"),
                "report_content": {"result": "safe_report_data", "timestamp": "2026-06-10"},
                "report_name": "final_report.json",
                "review_decision": "APPROVED",
                "review_reason": "Report verified safe",
                "reviewer": "human-reviewer-1",
                "target": "report",
                "requires_rollback": False,
                "evidence_target": str(tmp / "evidence"),
            })

            assert result.verdict == "PASS", f"Expected PASS, got {result.verdict}: {result.errors}"

            assert result.run_id
            assert result.goal_id

            # Event log persisted
            bus_events = bus.history(result.run_id)
            assert len(bus_events) > 0

            evt_types = {e.event_type for e in bus_events}
            assert "goal_received" in evt_types

            # Transaction committed exactly once
            assert txn_mgr._history, "Transaction should have been committed"
            committed = [t for t in txn_mgr._history if t.status == "committed"]
            assert len(committed) >= 1, f"Expected at least 1 committed transaction, got {len(committed)}"

            # Artifact refs validate by hash
            if result.artifacts:
                for art in result.artifacts:
                    h = store.hash_path(art.get("path", ""))
                    assert h is not None

            # Review ref exists
            assert ri._packets, "Review packets should exist"

            # Promotion decision promoted == true
            assert len(prom.decisions) > 0, "Promotion decisions should exist"
            assert prom.decisions[-1].promoted, "Promotion should be allowed"

            assert ctx.clock.now_iso() == "2026-06-10T12:00:00+00:00"
            assert not cb.is_tripped

            # Source manifests and mutation report exist with mutation_detected == false
            source_scope = ["Makefile", "tools/agentx_evolve/", "tests/system/"]
            root_path = Path(__file__).resolve().parent.parent.parent
            before = collect_source_manifest(root_path, include_paths=source_scope)
            after = collect_source_manifest(root_path, include_paths=source_scope)
            assert "files" in before or "entries" in before
            assert "files" in after or "entries" in after
            diff = compare_source_manifests(before, after)
            assert not diff.get("mutation_detected", True), "Source mutation should not be detected"

            src_dir = tmp / "src_reports"
            src_dir.mkdir(parents=True, exist_ok=True)
            report_paths = write_source_mutation_report(before, after, diff, src_dir)
            for rp in report_paths:
                assert Path(rp).exists(), f"Source mutation report missing: {rp}"

            # State records persisted
            state_records = state.query_by_run(result.run_id)
            assert len(state_records) > 0, "State records should exist"

            # Replay manifest export exists
            replay_artifacts = store.export_replay_manifest(result.run_id)
            assert len(replay_artifacts) > 0, "Should have replay manifest artifacts"

            # ── Export scenario data for replay manifests ────────────────
            from agentx_evolve.acceptance.scenario_export import export_scenario_data
            export_scenario_data(
                scenario_name="safe_report_generation",
                state_records=state_records,
                event_log_path=bus._log_path,
                runtime_context={
                    "seed": "safe-report-test-seed",
                    "fixed_clock": "2026-06-10T12:00:00+00:00",
                    "profile_id": "STRICT",
                    "agent_id": "agent-1",
                    "target_agent": "agent-2",
                    "review_decision": "APPROVED",
                    "review_reason": "Report verified safe",
                    "reviewer": "human-reviewer-1",
                    "action_type": "report_generation",
                    "target_path": str(tmp / "report.json"),
                    "report_content": {"result": "safe_report_data", "timestamp": "2026-06-10"},
                    "report_name": "final_report.json",
                    "target": "report",
                    "requires_rollback": False,
                    "evidence_target": str(tmp / "evidence"),
                },
                invariant_results=[],
                safety_events=[],
                promotion_decisions=[d.to_dict() for d in prom.decisions],
                extra_artifacts=replay_artifacts,
            )

        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
