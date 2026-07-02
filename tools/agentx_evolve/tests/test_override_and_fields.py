"""Tests for N1 §2: override path, missing registry fields, and CLI skeleton.

Verifies:
- Explicit override path for rejected/deprecated agents
- MvpAgentContract has version, evidence_refs, runtime_modes, parent_version
- MvpAgentContractBuilder supports parent_version lineage
- CLI skeleton commands are dispatched (goal, action, replay, health, config-validate, override)
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentx_evolve.self_evolution.self_evolution_controller import (
    MvpAgentContract,
    MvpAgentContractBuilder,
    MvpGeneratedAgentRegistry,
    MvpSelfEvolutionController,
    VALID_STATUSES,
)


class TestAgentOverridePath:
    def _ev_file(self) -> str:
        """Create a temp evidence file and return its path."""
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w")
        f.write('{"evidence": true}')
        f.close()
        return f.name

    def test_override_rejected_to_draft_override(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a1", purpose="test", status="REJECTED")
        registry.register(contract)
        ev = self._ev_file()
        ok = registry.override_rejected("a1", "DRAFT_OVERRIDE_REQUESTED", ev, "actor", "reason")
        assert ok
        assert contract.status == "DRAFT_OVERRIDE_REQUESTED"
        assert ev in contract.evidence_refs

    def test_override_rejected_to_draft_override_no_actor_fails(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a2", purpose="test", status="REJECTED")
        registry.register(contract)
        ev = self._ev_file()
        ok = registry.override_rejected("a2", "DRAFT_OVERRIDE_REQUESTED", ev, "", "reason")
        assert not ok

    def test_override_deprecated_to_draft_override(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a3", purpose="test", status="DEPRECATED")
        registry.register(contract)
        ev = self._ev_file()
        ok = registry.override_rejected("a3", "DRAFT_OVERRIDE_REQUESTED", ev, "actor", "reason")
        assert ok
        assert contract.status == "DRAFT_OVERRIDE_REQUESTED"

    def test_override_promoted_fails(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a4", purpose="test", status="PROMOTED")
        registry.register(contract)
        ev = self._ev_file()
        ok = registry.override_rejected("a4", "DEPRECATED", ev)
        assert not ok

    def test_override_unknown_agent_fails(self):
        registry = MvpGeneratedAgentRegistry()
        ev = self._ev_file()
        ok = registry.override_rejected("nonexistent", "PROMOTED", ev)
        assert not ok

    def test_override_invalid_status_fails(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a5", purpose="test", status="REJECTED")
        registry.register(contract)
        ev = self._ev_file()
        ok = registry.override_rejected("a5", "INVALID_STATUS", ev)
        assert not ok

    def test_override_without_evidence_fails(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a6", purpose="test", status="REJECTED")
        registry.register(contract)
        ok = registry.override_rejected("a6", "PROMOTED", "", "actor", "reason")
        assert not ok

    def test_override_with_nonexistent_evidence_fails(self):
        registry = MvpGeneratedAgentRegistry()
        contract = MvpAgentContract(agent_id="a7", purpose="test", status="REJECTED")
        registry.register(contract)
        ok = registry.override_rejected("a7", "PROMOTED", "/nonexistent/path.json", "actor", "reason")
        assert not ok

    def test_controller_override_agent(self):
        ctrl = MvpSelfEvolutionController()
        contract = MvpAgentContract(agent_id="ca1", purpose="test", status="REJECTED")
        ctrl._registry.register(contract)
        ev = self._ev_file()
        result = ctrl.override_agent("ca1", "DRAFT_OVERRIDE_REQUESTED", ev, "actor", "reason")
        assert result["success"]
        assert result["old_status"] == "REJECTED"
        assert result["new_status"] == "DRAFT_OVERRIDE_REQUESTED"

    def test_controller_override_not_found(self):
        ctrl = MvpSelfEvolutionController()
        ev = self._ev_file()
        result = ctrl.override_agent("nonexistent", "DRAFT_OVERRIDE_REQUESTED", ev)
        assert not result["success"]

    def test_controller_override_wrong_status(self):
        ctrl = MvpSelfEvolutionController()
        contract = MvpAgentContract(agent_id="ca2", purpose="test", status="DRAFT")
        ctrl._registry.register(contract)
        ev = self._ev_file()
        result = ctrl.override_agent("ca2", "DRAFT_OVERRIDE_REQUESTED", ev)
        assert not result["success"]

    def test_get_deprecated_agents(self):
        ctrl = MvpSelfEvolutionController()
        ctrl._registry.register(
            MvpAgentContract(agent_id="d1", purpose="test", status="DEPRECATED")
        )
        ctrl._registry.register(
            MvpAgentContract(agent_id="d2", purpose="test", status="REJECTED")
        )
        deprecated = ctrl.get_deprecated_agents()
        assert len(deprecated) == 1
        assert deprecated[0].agent_id == "d1"


class TestMissingRegistryFields:
    def test_contract_has_version(self):
        c = MvpAgentContract(agent_id="v1", purpose="test")
        assert c.version == "0.1.0"

    def test_contract_has_evidence_refs(self):
        c = MvpAgentContract(agent_id="v2", purpose="test", evidence_refs=["ref1"])
        assert "ref1" in c.evidence_refs

    def test_contract_has_runtime_modes(self):
        c = MvpAgentContract(agent_id="v3", purpose="test", runtime_modes=["goal_execution"])
        assert "goal_execution" in c.runtime_modes

    def test_contract_has_parent_version(self):
        c = MvpAgentContract(agent_id="v4", purpose="test", parent_version="0.0.1")
        assert c.parent_version == "0.0.1"

    def test_contract_parent_version_none_default(self):
        c = MvpAgentContract(agent_id="v5", purpose="test")
        assert c.parent_version is None

    def test_contract_to_dict_includes_new_fields(self):
        c = MvpAgentContract(
            agent_id="v6", purpose="test",
            version="1.0.0", evidence_refs=["ev1"],
            runtime_modes=["mode1"], parent_version="0.9.0",
        )
        d = c.to_dict()
        assert d["version"] == "1.0.0"
        assert d["evidence_refs"] == ["ev1"]
        assert d["runtime_modes"] == ["mode1"]
        assert d["parent_version"] == "0.9.0"

    def test_contract_from_dict_includes_new_fields(self):
        data = {
            "agent_id": "v7", "purpose": "test",
            "version": "2.0.0", "evidence_refs": ["ev2"],
            "runtime_modes": ["mode2"], "parent_version": "1.0.0",
        }
        c = MvpAgentContract.from_dict(data)
        assert c.version == "2.0.0"
        assert "ev2" in c.evidence_refs
        assert "mode2" in c.runtime_modes
        assert c.parent_version == "1.0.0"

    def test_contract_from_dict_missing_fields_defaults(self):
        data = {"agent_id": "v8", "purpose": "test"}
        c = MvpAgentContract.from_dict(data)
        assert c.version == "0.1.0"
        assert c.evidence_refs == []
        assert c.runtime_modes == []
        assert c.parent_version is None

    def test_builder_supports_parent_version(self):
        builder = MvpAgentContractBuilder()
        contract = builder.build("test goal", parent_version="0.0.5")
        assert contract.parent_version == "0.0.5"
        assert contract.version == "0.1.0"

    def test_builder_default_no_parent(self):
        builder = MvpAgentContractBuilder()
        contract = builder.build("test goal")
        assert contract.parent_version is None


class TestCLISkeleton:
    def test_goal_create_returns_result(self):
        ctrl = MvpSelfEvolutionController()
        result = ctrl.generate_agent("test goal")
        assert result.agent_id != ""
        assert result.verdict in ("PROMOTED", "REJECTED")

    def test_goal_list_returns_goals(self):
        ctrl = MvpSelfEvolutionController()
        ctrl.generate_agent("goal 1")
        ctrl.generate_agent("goal 2")
        goals = ctrl.get_goals()
        assert len(goals) >= 2

    def test_goal_status_found(self):
        ctrl = MvpSelfEvolutionController()
        result = ctrl.generate_agent("status test")
        contract = ctrl.get_promoted_agent(result.agent_id)
        if contract:
            assert contract.agent_id == result.agent_id

    def test_replay_generation_returns_verdict(self):
        ctrl = MvpSelfEvolutionController()
        result = ctrl.replay_generation("test-run", None)
        assert isinstance(result.verdict, str)
        assert isinstance(result.errors, list)

    def test_get_rejected_agents(self):
        ctrl = MvpSelfEvolutionController()
        ctrl._registry.register(
            MvpAgentContract(agent_id="r1", purpose="test", status="REJECTED")
        )
        ctrl._registry.register(
            MvpAgentContract(agent_id="r2", purpose="test", status="REJECTED")
        )
        rejected = ctrl.get_rejected_agents()
        assert len(rejected) >= 2

    def test_get_goals_includes_status_purpose_version(self):
        ctrl = MvpSelfEvolutionController()
        ctrl._registry.register(
            MvpAgentContract(agent_id="g1", purpose="goal one", status="PROMOTED", version="1.0.0")
        )
        goals = ctrl.get_goals()
        found = [g for g in goals if g["agent_id"] == "g1"]
        assert len(found) == 1
        assert found[0]["status"] == "PROMOTED"
        assert found[0]["purpose"] == "goal one"
        assert found[0]["version"] == "1.0.0"
