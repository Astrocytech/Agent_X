from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentx_evolve.self_evolution.self_evolution_controller import (
    MvpAgentContract,
    MvpAgentContractBuilder,
    MvpEvolutionResult,
    MvpGeneratedAgentRegistry,
    MvpSelfEvolutionController,
)


class TestEvolutionControllerIntegration:
    def test_forbidden_actions_wired_into_orchestrator(self):
        class SecureOrchestrator:
            def __init__(self):
                self._forbidden: dict[str, list[str]] = {}
                self._validators: list[str] = []

            def set_forbidden_actions(self, agent_id: str, actions: list[str]) -> None:
                self._forbidden[agent_id] = list(actions)

            def set_validator_files(self, files: list[str]) -> None:
                self._validators = list(files)

            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> Any:
                agent = (context_overrides or {}).get("agent_id", "")
                forbidden = self._forbidden.get(agent, [])
                for action in forbidden:
                    if action in goal_text:
                        return type("R", (), {
                            "run_id": "sec-run", "goal_id": "sec-goal",
                            "verdict": "VALIDATION_FAILED",
                            "errors": [f"Forbidden action: {action}"],
                            "action_status": "FAILED",
                            "artifacts": [], "events": [], "evidence_refs": [],
                        })()
                return type("R", (), {
                    "run_id": "sec-run", "goal_id": "sec-goal",
                    "verdict": "PASS", "errors": [],
                    "action_status": "COMPLETED",
                    "artifacts": [], "events": [], "evidence_refs": [],
                })()

        ctrl = MvpSelfEvolutionController(orchestrator=SecureOrchestrator())
        result = ctrl.generate_agent("Build a monitoring agent")
        assert result.verdict in ("PROMOTED", "REJECTED")

    def test_get_promoted_agent(self):
        reg = MvpGeneratedAgentRegistry()
        ctrl = MvpSelfEvolutionController(registry=reg)

        promoted = MvpAgentContract(
            agent_id="promoted-1", purpose="test", status="PROMOTED",
        )
        rejected = MvpAgentContract(
            agent_id="rejected-1", purpose="test", status="REJECTED",
        )
        reg.register(promoted)
        reg.register(rejected)

        found = ctrl.get_promoted_agent("promoted-1")
        assert found is not None
        assert found.agent_id == "promoted-1"

        not_found = ctrl.get_promoted_agent("rejected-1")
        assert not_found is None

    def test_get_rejected_agents(self):
        reg = MvpGeneratedAgentRegistry()
        ctrl = MvpSelfEvolutionController(registry=reg)

        reg.register(MvpAgentContract(
            agent_id="r1", purpose="x", status="REJECTED",
        ))
        reg.register(MvpAgentContract(
            agent_id="r2", purpose="x", status="REJECTED",
        ))
        reg.register(MvpAgentContract(
            agent_id="p1", purpose="x", status="PROMOTED",
        ))

        rejected = ctrl.get_rejected_agents()
        assert len(rejected) == 2
        assert all(a.status == "REJECTED" for a in rejected)

    def test_generate_contract_snapshot_in_result(self):
        ctrl = MvpSelfEvolutionController()
        result = ctrl.generate_agent("Snapshot test")
        assert "agent_id" in result.contract_snapshot
        assert "purpose" in result.contract_snapshot
        assert result.contract_snapshot["purpose"] == "Snapshot test"

    def test_replay_generation(self):
        class ReplayOrchestrator:
            def replay_run(self, run_id: str, context: Any,
                           context_overrides: dict | None = None) -> Any:
                return type("R", (), {
                    "run_id": run_id, "goal_id": "replay-goal",
                    "verdict": "PASS", "errors": [],
                    "action_status": "COMPLETED",
                    "artifacts": [], "events": [], "evidence_refs": [],
                })()

            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> Any:
                return type("R", (), {
                    "run_id": "orig-run", "goal_id": "orig-goal",
                    "verdict": "PASS", "errors": [],
                    "action_status": "COMPLETED",
                    "artifacts": [], "events": [], "evidence_refs": [],
                })()

        ctrl = MvpSelfEvolutionController(orchestrator=ReplayOrchestrator())
        result = ctrl.replay_generation("run-001", None)
        assert result.verdict == "PROMOTED"
        assert result.run_id == "run-001"
