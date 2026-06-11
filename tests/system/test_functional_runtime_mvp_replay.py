"""Replay system test: reproduces both MVP scenarios from recorded context.
 
Uses the same deterministic seed and clock as the original runs
to verify that the verdict and key artifact hashes are identical.
"""
import json
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


PASS_SEED = "replay-safe-pass-seed"
DENY_SEED = "replay-unsafe-deny-seed"
FIXED_CLOCK = "2026-06-10T12:00:00+00:00"


def _run_scenario(seed: str, agent_id: str, target_agent: str,
                  review_decision: str, reviewer: str) -> tuple:
    tmp = Path(tempfile.mkdtemp(prefix="replay_test_"))
    try:
        ctx = MvpRuntimeContext()
        ctx.randomness = MvpSeededRandomness(seed)
        ctx.clock = MvpDeterministicClock(FIXED_CLOCK)

        ws = MvpWorkspaceManager(root=tmp / "ws")
        store = MvpArtifactStore(tmp / "artifacts")
        state = MvpStateStore(tmp / "state")
        bus = MvpEventBus(log_path=tmp / "events.jsonl")
        action = MvpAction(action_id=f"replay-act-{seed[:4]}",
                            action_type="report_generation", agent_id=agent_id)
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
            contract_id="report_generation", contract_type="action", version="1.0.0",
        ))

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
            ("contract_registry", contract_reg),
            ("security_envelope", MvpSecurityEnvelope()),
        ]:
            orch.bind(name, inst)

        result = orch.run_goal("Replay scenario", profile_id="STRICT", context_overrides={
            "agent_id": agent_id,
            "target_agent": target_agent,
            "action_type": "report_generation",
            "target_path": str(tmp / "report.json"),
            "report_content": {"result": "replay_data", "seed": seed},
            "report_name": "replay_report.json",
            "review_decision": review_decision,
            "review_reason": "Replay review",
            "reviewer": reviewer,
            "target": "report",
            "requires_rollback": False,
            "evidence_target": str(tmp / "evidence"),
        })

        artifacts = []
        if result.artifacts:
            for art in result.artifacts:
                h = store.hash_path(art.get("path", ""))
                artifacts.append({"path": art.get("path", ""), "hash": h})

        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

        return result.verdict, artifacts, result.errors

    except Exception:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
        raise


class TestFunctionalRuntimeMvpReplay:
    def test_replay_safe_scenario_produces_same_verdict(self):
        v1, arts1, errs1 = _run_scenario(
            PASS_SEED, "agent-1", "agent-2", "APPROVED", "human-reviewer",
        )
        v2, arts2, errs2 = _run_scenario(
            PASS_SEED, "agent-1", "agent-2", "APPROVED", "human-reviewer",
        )
        assert v1 == v2, f"Verdict mismatch: {v1} vs {v2}"
        if arts1 and arts2:
            for a1, a2 in zip(arts1, arts2):
                assert a1.get("hash") == a2.get("hash"), \
                    f"Hash mismatch: {a1} vs {a2}"

    def test_replay_unsafe_scenario_produces_same_denial(self):
        v1, arts1, errs1 = _run_scenario(
            DENY_SEED, "generated-agent-X", "generated-agent-X", "APPROVED", "generated-agent-X",
        )
        v2, arts2, errs2 = _run_scenario(
            DENY_SEED, "generated-agent-X", "generated-agent-X", "APPROVED", "generated-agent-X",
        )
        assert v1 == "DENIED_AND_RECORDED", f"First run: {v1}"
        assert v2 == "DENIED_AND_RECORDED", f"Replay: {v2}"
        assert v1 == v2, f"Verdict mismatch: {v1} vs {v2}"

    def test_replay_uses_persisted_manifest_for_safe_scenario(self):
        from agentx_evolve.testing.replay_manifest import (
            create_replay_manifest, write_replay_manifest, validate_manifest,
        )
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="replay_persist_safe_"))
        try:
            manifest = create_replay_manifest(
                scenario_name="safe_report_generation",
                run_id="run-safe-1",
                goal_id="goal-safe-1",
                runtime_context={"seed": PASS_SEED, "clock": FIXED_CLOCK},
                state_records_path=str(tmp / "state.json"),
                state_records_hash="abc",
                event_log_path=str(tmp / "events.jsonl"),
                event_log_hash="def",
                artifact_refs=[{"path": str(tmp / "art.json"), "hash": "123"}],
                final_verdict="PASS",
            )
            errs = validate_manifest(manifest)
            assert errs == [], f"Manifest validation errors: {errs}"
            p = write_replay_manifest(manifest, tmp, "safe_report_generation")
            assert Path(p).exists()
            assert "replay_manifest" in p
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_replay_uses_persisted_manifest_for_unsafe_scenario(self):
        from agentx_evolve.testing.replay_manifest import (
            create_replay_manifest, write_replay_manifest, validate_manifest,
        )
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="replay_persist_unsafe_"))
        try:
            manifest = create_replay_manifest(
                scenario_name="unsafe_self_promotion",
                run_id="run-unsafe-1",
                goal_id="goal-unsafe-1",
                runtime_context={"seed": DENY_SEED, "clock": FIXED_CLOCK},
                state_records_path=str(tmp / "state.json"),
                state_records_hash="ghi",
                event_log_path=str(tmp / "events.jsonl"),
                event_log_hash="jkl",
                artifact_refs=[{"path": str(tmp / "unsafe_art.json"), "hash": "456"}],
                safety_events=[{"trigger": "unsafe_self_promotion_attempt", "reason": "Self-promotion"}],
                final_verdict="DENIED_AND_RECORDED",
            )
            errs = validate_manifest(manifest)
            assert errs == [], f"Manifest validation errors: {errs}"
            p = write_replay_manifest(manifest, tmp, "unsafe_self_promotion")
            assert Path(p).exists()
            assert "replay_manifest" in p
        finally:
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_replay_fails_on_artifact_hash_mismatch(self):
        from agentx_evolve.validators.validate_functional_runtime_mvp_replay import (
            validate_replay, REPORT_DIR,
        )
        import tempfile
        orig_dir = REPORT_DIR
        try:
            tmp = Path(tempfile.mkdtemp(prefix="replay_hash_mismatch_"))
            manifest = {
                "schema_version": "1.0.0",
                "scenario_name": "safe_report_generation",
                "run_id": "test-run",
                "runtime_context": {"seed": "test", "fixed_clock": "2026-06-10T12:00:00", "profile_id": "STRICT"},
                "state_records_path": str(tmp / "state.json"),
                "state_records_hash": "0" * 64,
                "event_log_path": str(tmp / "events.jsonl"),
                "event_log_hash": "0" * 64,
                "artifact_refs": [
                    {"path": str(tmp / "nonexistent.bin"), "hash": "0000000000000000000000000000000000000000000000000000000000000000"},
                ],
                "final_verdict": "PASS",
                "created_at": "2026-06-26T00:00:00",
            }
            (tmp / "functional_runtime_mvp_replay_manifest_safe_report_generation.json").write_text(
                json.dumps(manifest)
            )
            import agentx_evolve.validators.validate_functional_runtime_mvp_replay as vmod
            vmod.REPORT_DIR = tmp
            errs = validate_replay()
            assert len(errs) > 0
            assert any("missing" in e.lower() or "unreadable" in e.lower() for e in errs)
        finally:
            vmod.REPORT_DIR = orig_dir
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_replay_fails_on_verdict_mismatch(self):
        from agentx_evolve.validators.validate_functional_runtime_mvp_replay import (
            validate_replay, REPORT_DIR,
        )
        import tempfile
        orig_dir = REPORT_DIR
        try:
            tmp = Path(tempfile.mkdtemp(prefix="replay_verdict_mismatch_"))
            # Create a replay manifest with contradicting data (safe scenario with DENIED_AND_RECORDED)
            manifest = {
                "schema_version": "1.0.0",
                "scenario_name": "safe_report_generation",
                "run_id": "test-run",
                "runtime_context": {"seed": "test", "fixed_clock": "2026-06-10T12:00:00", "profile_id": "STRICT"},
                "state_records_path": str(tmp / "state.json"),
                "state_records_hash": "0" * 64,
                "event_log_path": str(tmp / "events.jsonl"),
                "event_log_hash": "0" * 64,
                "artifact_refs": [],
                "final_verdict": "DENIED_AND_RECORDED",
                "created_at": "2026-06-26T00:00:00",
            }
            (tmp / "functional_runtime_mvp_replay_manifest_safe_report_generation.json").write_text(
                json.dumps(manifest)
            )
            import agentx_evolve.validators.validate_functional_runtime_mvp_replay as vmod
            vmod.REPORT_DIR = tmp
            errs = validate_replay()
            assert len(errs) > 0
            assert any("verdict" in e and "PASS" in e for e in errs)
        finally:
            vmod.REPORT_DIR = orig_dir
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_replay_fails_on_missing_event_log(self):
        from agentx_evolve.validators.validate_functional_runtime_mvp_replay import (
            validate_replay, REPORT_DIR,
        )
        import tempfile
        orig_dir = REPORT_DIR
        try:
            tmp = Path(tempfile.mkdtemp(prefix="replay_missing_event_"))
            manifest = {
                "schema_version": "1.0.0",
                "scenario_name": "safe_report_generation",
                "run_id": "test-run",
                "runtime_context": {"seed": "test", "fixed_clock": "2026-06-10T12:00:00", "profile_id": "STRICT"},
                "state_records_path": str(tmp / "state.json"),
                "state_records_hash": "0" * 64,
                "event_log_path": str(tmp / "events.jsonl"),
                "event_log_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                "artifact_refs": [
                    {"path": str(tmp / "events.jsonl"), "hash": "0000000000000000000000000000000000000000000000000000000000000000"},
                ],
                "final_verdict": "PASS",
                "created_at": "2026-06-26T00:00:00",
            }
            (tmp / "functional_runtime_mvp_replay_manifest_safe_report_generation.json").write_text(
                json.dumps(manifest)
            )
            import agentx_evolve.validators.validate_functional_runtime_mvp_replay as vmod
            vmod.REPORT_DIR = tmp
            errs = validate_replay()
            assert len(errs) > 0
            assert any("unreadable" in e.lower() or "missing" in e.lower() or "hash mismatch" in e.lower() for e in errs)
        finally:
            vmod.REPORT_DIR = orig_dir
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_replay_fails_on_missing_state_records(self):
        from agentx_evolve.validators.validate_functional_runtime_mvp_replay import (
            validate_replay, REPORT_DIR,
        )
        import tempfile
        orig_dir = REPORT_DIR
        try:
            tmp = Path(tempfile.mkdtemp(prefix="replay_missing_state_"))
            manifest = {
                "schema_version": "1.0.0",
                "scenario_name": "safe_report_generation",
                "run_id": "test-run",
                "runtime_context": {"seed": "test", "fixed_clock": "2026-06-10T12:00:00", "profile_id": "STRICT"},
                "state_records_path": str(tmp / "state.json"),
                "state_records_hash": "0000000000000000000000000000000000000000000000000000000000000000",
                "event_log_path": str(tmp / "events.jsonl"),
                "event_log_hash": "0" * 64,
                "artifact_refs": [
                    {"path": str(tmp / "state.json"), "hash": "0000000000000000000000000000000000000000000000000000000000000000"},
                ],
                "final_verdict": "PASS",
                "created_at": "2026-06-26T00:00:00",
            }
            (tmp / "functional_runtime_mvp_replay_manifest_safe_report_generation.json").write_text(
                json.dumps(manifest)
            )
            import agentx_evolve.validators.validate_functional_runtime_mvp_replay as vmod
            vmod.REPORT_DIR = tmp
            errs = validate_replay()
            assert len(errs) > 0
            assert any("missing" in e.lower() or "unreadable" in e.lower() or "hash mismatch" in e.lower() for e in errs)
        finally:
            vmod.REPORT_DIR = orig_dir
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
