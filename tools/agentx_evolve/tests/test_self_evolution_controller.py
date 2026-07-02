from __future__ import annotations

import json as _json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.self_evolution.self_evolution_controller import (
    MvpAgentContract,
    MvpAgentContractBuilder,
    MvpEvolutionResult,
    MvpGeneratedAgentRegistry,
    MvpSelfEvolutionController,
    ALLOWED_TRANSITIONS,
)


class TestMvpAgentContractBuilder:
    def test_contract_builder_creates_valid_contract(self) -> None:
        builder = MvpAgentContractBuilder()
        contract = builder.build("Generate a report from system logs")
        assert contract.agent_id.startswith("agent-")
        assert contract.purpose == "Generate a report from system logs"
        assert contract.status == "DRAFT"
        assert len(contract.allowed_actions) > 0
        assert len(contract.forbidden_actions) > 0
        issues = builder.validate(contract)
        assert len(issues) == 0

    def test_contract_builder_validates_required_fields(self) -> None:
        builder = MvpAgentContractBuilder()
        empty = MvpAgentContract()
        issues = builder.validate(empty)
        assert len(issues) > 0
        no_purpose = MvpAgentContract(agent_id="agent-1")
        issues = builder.validate(no_purpose)
        assert len(issues) > 0
        no_id = MvpAgentContract(purpose="do something")
        issues = builder.validate(no_id)
        assert len(issues) > 0
        invalid_status = MvpAgentContract(agent_id="a", purpose="p", status="INVALID")
        issues = builder.validate(invalid_status)
        assert len(issues) > 0


class TestMvpGeneratedAgentRegistry:
    def test_registry_register_and_get(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="agent-1", purpose="test")
        reg.register(c)
        assert reg.get("agent-1") is c
        assert reg.get("nonexistent") is None

    def test_registry_status_transition(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="agent-2", purpose="test")
        reg.register(c)
        assert c.status == "DRAFT"
        assert reg.update_status("agent-2", "GENERATED")
        assert reg.get("agent-2").status == "GENERATED"
        assert reg.update_status("agent-2", "VALIDATED")
        assert reg.get("agent-2").status == "VALIDATED"
        assert reg.update_status("agent-2", "TESTED")
        assert reg.get("agent-2").status == "TESTED"
        assert reg.update_status("agent-2", "ADVERSARIAL_TESTED")
        assert reg.get("agent-2").status == "ADVERSARIAL_TESTED"
        assert reg.update_status("agent-2", "REVIEWED")
        assert reg.get("agent-2").status == "REVIEWED"
        assert reg.update_status("agent-2", "PROMOTION_ELIGIBLE")
        assert reg.get("agent-2").status == "PROMOTION_ELIGIBLE"
        assert reg.update_status("agent-2", "PROMOTED")
        assert reg.get("agent-2").status == "PROMOTED"

    def test_registry_skipping_steps_rejected(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="agent-skip", purpose="test")
        reg.register(c)
        assert reg.update_status("agent-skip", "GENERATED")
        assert not reg.update_status("agent-skip", "PROMOTED")
        assert reg.get("agent-skip").status == "GENERATED"

    def test_registry_rejected_agent_cannot_be_used(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="rejected-1", purpose="test", status="REJECTED")
        reg.register(c)
        assert reg.get("rejected-1") is not None
        assert reg.get("rejected-1").status == "REJECTED"
        promoted = reg.list_by_status("PROMOTED")
        assert all(a.status == "PROMOTED" for a in promoted)
        assert len(promoted) == 0

    def test_update_status_invalid_skips_allowed(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="agent-3", purpose="test")
        reg.register(c)
        assert not reg.update_status("agent-3", "BOGUS")
        assert not reg.update_status("nonexistent", "PROMOTED")

    def test_list_by_status(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        for i in range(3):
            reg.register(MvpAgentContract(agent_id=f"draft-{i}", purpose="x", status="DRAFT"))
        for i in range(2):
            reg.register(MvpAgentContract(agent_id=f"promoted-{i}", purpose="x", status="PROMOTED"))
        drafts = reg.list_by_status("DRAFT")
        assert len(drafts) == 3
        promoted = reg.list_by_status("PROMOTED")
        assert len(promoted) == 2

    def test_override_rejected_requires_actor_and_reason(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="rej-1", purpose="test", status="REJECTED")
        reg.register(c)
        assert not reg.override_rejected("rej-1", "VALIDATED")
        assert not reg.override_rejected("rej-1", "VALIDATED", override_actor="admin")
        assert not reg.override_rejected("rej-1", "VALIDATED", override_reason="because")
        # Create valid evidence file for the successful call
        with tempfile.TemporaryDirectory() as td:
            ev_path = Path(td) / "override_evidence.json"
            ev_path.write_text(
                _json.dumps({
                    "review": "manual review override",
                    "subject_agent_id": "rej-1",
                    "actor": "admin",
                }),
            )
            assert reg.override_rejected(
                "rej-1", "DRAFT_OVERRIDE_REQUESTED",
                evidence_ref=str(ev_path),
                override_actor="admin", override_reason="manual review pass",
            )
            assert reg.get("rej-1").status == "DRAFT_OVERRIDE_REQUESTED"

    def test_override_from_promoted_rejected(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(agent_id="prom-1", purpose="test", status="PROMOTED")
        reg.register(c)
        assert not reg.override_rejected(
            "prom-1", "DRAFT_OVERRIDE_REQUESTED",
            override_actor="admin", override_reason="should not work",
        )


class TestMvpSelfEvolutionController:
    def test_self_evolution_controller_generate_agent(self) -> None:
        @dataclass
        class FakeResult:
            run_id: str = "run-001"
            goal_id: str = "goal-001"
            verdict: str = "PASS"
            errors: list[str] = field(default_factory=list)
            action_status: str = "COMPLETED"
            artifacts: list[dict] = field(default_factory=list)
            events: list[dict] = field(default_factory=list)
            evidence_refs: list[dict] = field(default_factory=list)

        class FakeOrchestrator:
            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> FakeResult:
                return FakeResult()

        ctrl = MvpSelfEvolutionController(
            orchestrator=FakeOrchestrator(),
        )
        result = ctrl.generate_agent("Build a monitoring agent")
        assert result.verdict == "PROMOTED"
        assert result.run_id == "run-001"
        assert result.goal_id == "goal-001"
        assert result.agent_id.startswith("agent-")
        assert len(result.errors) == 0

    def test_generate_agent_rejected(self) -> None:
        class FailingOrchestrator:
            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> Any:
                return type("FakeResult", (), {
                    "run_id": "run-002",
                    "goal_id": "goal-002",
                    "verdict": "VALIDATION_FAILED",
                    "errors": ["Invalid action type"],
                    "action_status": "FAILED",
                    "artifacts": [],
                    "events": [],
                    "evidence_refs": [],
                })()

        ctrl = MvpSelfEvolutionController(
            orchestrator=FailingOrchestrator(),
        )
        result = ctrl.generate_agent("Bad goal that will fail")
        assert result.verdict == "REJECTED"
        assert "Invalid action type" in result.errors

    def test_generate_agent_invalid_contract(self) -> None:
        class BrokenBuilder(MvpAgentContractBuilder):
            def build(self, goal_text: str) -> MvpAgentContract:
                return MvpAgentContract()

        ctrl = MvpSelfEvolutionController(
            contract_builder=BrokenBuilder(),
        )
        result = ctrl.generate_agent("some goal")
        assert result.verdict == "FAILED"
        assert any("Contract validation failed" in e for e in result.errors)

    def test_override_promoted_agent_rejected(self) -> None:
        @dataclass
        class FakeResult:
            run_id: str = "run-003"
            goal_id: str = "goal-003"
            verdict: str = "PASS"
            errors: list[str] = field(default_factory=list)
            action_status: str = "COMPLETED"
            artifacts: list[dict] = field(default_factory=list)
            events: list[dict] = field(default_factory=list)
            evidence_refs: list[dict] = field(default_factory=list)

        class FakeOrchestrator:
            def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                         context_overrides: dict | None = None) -> FakeResult:
                return FakeResult()

        ctrl = MvpSelfEvolutionController(
            orchestrator=FakeOrchestrator(),
        )
        result = ctrl.generate_agent("Test agent for override")
        assert result.verdict == "PROMOTED"
        r = ctrl.override_agent(
            result.agent_id, "PROMOTED",
            override_actor="admin", override_reason="test override",
        )
        assert not r["success"]
        assert "must be REJECTED or DEPRECATED" in r["error"]

    def test_override_rejected_agent_succeeds(self) -> None:
        reg = MvpGeneratedAgentRegistry()
        c = MvpAgentContract(
            agent_id="rej-override", purpose="test", status="REJECTED",
            allowed_actions=["read_files"],
            forbidden_actions=["write_files"],
            test_requirements=["unit_tests_pass"],
            adversarial_test_requirements=["injection_resistance"],
            evidence_requirements=["contract_hash_recorded"],
            rollback_requirements=["snapshot_available"],
            inputs={"type": "object", "properties": {"x": {"type": "string"}}},
            outputs={"type": "object", "properties": {"y": {"type": "string"}}},
        )
        reg.register(c)
        ctrl = MvpSelfEvolutionController(registry=reg)
        with tempfile.TemporaryDirectory() as td:
            ev_path = Path(td) / "override_evidence.json"
            ev_path.write_text(
                _json.dumps({
                    "review": "manual override",
                    "subject_agent_id": "rej-override",
                    "actor": "admin",
                }),
            )
            r = ctrl.override_agent(
                "rej-override", "VALIDATED",
                evidence_ref=str(ev_path),
                override_actor="admin", override_reason="manual override for retry",
            )
            assert r["success"]
            assert r["old_status"] == "REJECTED"
            assert r["new_status"] == "DRAFT_OVERRIDE_REQUESTED"
            assert reg.get("rej-override").status == "DRAFT_OVERRIDE_REQUESTED"


class TestMvpEvolutionResult:
    def test_evolution_result_format(self) -> None:
        result = MvpEvolutionResult(
            run_id="run-001",
            goal_id="goal-001",
            agent_id="agent-abc",
            verdict="PROMOTED",
            errors=[],
        )
        d = result.to_dict()
        assert d["run_id"] == "run-001"
        assert d["goal_id"] == "goal-001"
        assert d["agent_id"] == "agent-abc"
        assert d["verdict"] == "PROMOTED"
        assert d["errors"] == []

    def test_evolution_result_defaults(self) -> None:
        result = MvpEvolutionResult()
        assert result.verdict == "FAILED"
        assert result.errors == []

    def test_evolution_result_with_errors(self) -> None:
        result = MvpEvolutionResult(
            run_id="run-002",
            goal_id="goal-002",
            agent_id="agent-xyz",
            verdict="REJECTED",
            errors=["capability denied", "policy violation"],
        )
        d = result.to_dict()
        assert len(d["errors"]) == 2
        assert "capability denied" in d["errors"]


class TestAllowedTransitions:
    def test_all_transition_steps_covered(self) -> None:
        assert "DRAFT" in ALLOWED_TRANSITIONS
        assert "GENERATED" in ALLOWED_TRANSITIONS
        assert "VALIDATED" in ALLOWED_TRANSITIONS
        assert "TESTED" in ALLOWED_TRANSITIONS
        assert "ADVERSARIAL_TESTED" in ALLOWED_TRANSITIONS
        assert "REVIEWED" in ALLOWED_TRANSITIONS
        assert "PROMOTION_ELIGIBLE" in ALLOWED_TRANSITIONS
        assert "PROMOTED" in ALLOWED_TRANSITIONS
        assert "REJECTED" in ALLOWED_TRANSITIONS
        assert "BLOCKED" in ALLOWED_TRANSITIONS
        assert "DRAFT_OVERRIDE_REQUESTED" in ALLOWED_TRANSITIONS

    def test_no_shortcut_to_promoted(self) -> None:
        for status, next_states in ALLOWED_TRANSITIONS.items():
            if status != "PROMOTION_ELIGIBLE":
                assert "PROMOTED" not in next_states, f"{status} can shortcut to PROMOTED"

    def test_deprecated_and_rejected_to_override(self) -> None:
        assert "DRAFT_OVERRIDE_REQUESTED" in ALLOWED_TRANSITIONS["REJECTED"]
        assert "DRAFT_OVERRIDE_REQUESTED" in ALLOWED_TRANSITIONS["DEPRECATED"]
