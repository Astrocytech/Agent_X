from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator


class TestMvpFunctionalOrchestrator:
    def test_run_without_context_returns_manual(self):
        orch = MvpFunctionalOrchestrator()
        result = orch.run_goal("test goal", profile_id="STRICT")
        assert result.run_id == "manual_run"

    def test_run_with_full_bindings(self):
        from agentx_evolve.runtime.runtime_context import MvpRuntimeContext, MvpSeededRandomness, MvpDeterministicClock
        from agentx_evolve.workspace.workspace_manager import MvpWorkspaceManager
        from agentx_evolve.artifacts.artifact_store import MvpArtifactStore
        from agentx_evolve.state.state_store import MvpStateStore
        from agentx_evolve.bus.event_bus import MvpEventBus
        from agentx_evolve.lifecycle.action import MvpAction
        from agentx_evolve.gates.decision_gate import MvpDecisionGate
        from agentx_evolve.simulation.simulation_engine import MvpSimulationEngine
        from agentx_evolve.promotion.promotion_gate import MvpPromotionGate
        from agentx_evolve.security.security_envelope import MvpEnvelopeBuilder, MvpSecurityEnvelope

        import tempfile
        tmp = tempfile.mkdtemp(prefix="test_orch_")

        ctx = MvpRuntimeContext()
        ctx.randomness = MvpSeededRandomness("orch-test-seed")
        ctx.clock = MvpDeterministicClock("2026-06-10T12:00:00+00:00")

        from pathlib import Path
        ws = MvpWorkspaceManager(root=Path(tmp))
        store = MvpArtifactStore(Path(tmp) / "artifacts")
        state = MvpStateStore(Path(tmp) / "state")
        bus = MvpEventBus(log_path=Path(tmp) / "events.jsonl")
        action = MvpAction(action_id="orch-act-1")
        gate = MvpDecisionGate()
        sim = MvpSimulationEngine()
        prom = MvpPromotionGate()

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
        orch.bind("security_envelope", MvpSecurityEnvelope())

        import shutil
        result = orch.run_goal("test report goal", profile_id="STRICT", context_overrides={
            "agent_id": "agent-1",
            "action_type": "report_generation",
            "target_path": "/tmp/report.json",
            "report_content": {"result": "test"},
            "report_name": "test_report.json",
            "review_decision": "APPROVED",
            "review_reason": "Auto-approved",
            "reviewer": "orchestrator-test",
        })
        assert result.verdict in ("PASS", "DENIED_AND_RECORDED", "FAILED")
        assert result.run_id != "manual_run"
        shutil.rmtree(tmp, ignore_errors=True)
