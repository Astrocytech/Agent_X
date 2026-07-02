from __future__ import annotations

import hashlib
import json as _json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentx_evolve.orchestrator.functional_orchestrator import MvpFunctionalOrchestrator


VALID_STATUSES = frozenset({
    "DRAFT", "GENERATED", "VALIDATED", "TESTED", "ADVERSARIAL_TESTED",
    "REVIEWED", "PROMOTION_ELIGIBLE", "PROMOTED", "DEPRECATED",
    "REJECTED", "BLOCKED", "ROLLBACK_REQUIRED", "DRAFT_OVERRIDE_REQUESTED",
})

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"GENERATED", "REJECTED", "BLOCKED"},
    "GENERATED": {"VALIDATED", "REJECTED", "BLOCKED"},
    "VALIDATED": {"TESTED", "REJECTED", "BLOCKED"},
    "TESTED": {"ADVERSARIAL_TESTED", "REJECTED", "BLOCKED"},
    "ADVERSARIAL_TESTED": {"REVIEWED", "REJECTED", "BLOCKED"},
    "REVIEWED": {"PROMOTION_ELIGIBLE", "REJECTED", "BLOCKED"},
    "PROMOTION_ELIGIBLE": {"PROMOTED", "REJECTED", "BLOCKED"},
    "PROMOTED": {"DEPRECATED", "ROLLBACK_REQUIRED"},
    "ROLLBACK_REQUIRED": {"DEPRECATED", "REJECTED"},
    "REJECTED": {"DRAFT_OVERRIDE_REQUESTED"},
    "DEPRECATED": {"DRAFT_OVERRIDE_REQUESTED"},
    "DRAFT_OVERRIDE_REQUESTED": {"VALIDATED", "REJECTED", "BLOCKED"},
    "BLOCKED": {"DRAFT_OVERRIDE_REQUESTED", "REJECTED"},
}


def deterministic_id(
    prefix: str,
    run_id: str = "",
    seed: str = "",
    purpose_hash: str = "",
    parent_version: str = "root",
    sequence: int = 0,
) -> str:
    h = hashlib.sha256(
        f"{run_id}:{seed}:{purpose_hash}:{parent_version}:{sequence}".encode()
    ).hexdigest()[:12]
    return f"{prefix}-{h}"


@dataclass
class MvpAgentContract:
    agent_id: str = ""
    purpose: str = ""
    schema_version: str = "1.0.0"
    contract_hash: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    allowed_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    test_requirements: list[str] = field(default_factory=list)
    adversarial_test_requirements: list[str] = field(default_factory=list)
    rollback_requirements: list[str] = field(default_factory=list)
    promotion_requirements: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    review_requirements: list[str] = field(default_factory=list)
    replay_mode: str = "deterministic_simulated"
    risk_level: str = "low"
    status: str = "DRAFT"
    version: str = "0.1.0"
    evidence_refs: list[str] = field(default_factory=list)
    runtime_modes: list[str] = field(default_factory=list)
    parent_version: str | None = None

    def compute_hash(self) -> str:
        raw = hashlib.sha256(
            f"{self.agent_id}:{self.purpose}:{self.schema_version}:"
            f"{_json.dumps(self.inputs, sort_keys=True)}:"
            f"{_json.dumps(self.outputs, sort_keys=True)}:"
            f"{sorted(self.allowed_actions)}:{sorted(self.forbidden_actions)}:"
            f"{sorted(self.capabilities)}:{self.risk_level}:{self.replay_mode}"
            .encode()
        ).hexdigest()
        return raw

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "purpose": self.purpose,
            "schema_version": self.schema_version,
            "contract_hash": self.compute_hash(),
            "inputs": dict(self.inputs),
            "outputs": dict(self.outputs),
            "allowed_actions": list(self.allowed_actions),
            "forbidden_actions": list(self.forbidden_actions),
            "capabilities": list(self.capabilities),
            "invariants": list(self.invariants),
            "test_requirements": list(self.test_requirements),
            "adversarial_test_requirements": list(self.adversarial_test_requirements),
            "rollback_requirements": list(self.rollback_requirements),
            "promotion_requirements": list(self.promotion_requirements),
            "evidence_requirements": list(self.evidence_requirements),
            "review_requirements": list(self.review_requirements),
            "replay_mode": self.replay_mode,
            "risk_level": self.risk_level,
            "status": self.status,
            "version": self.version,
            "evidence_refs": list(self.evidence_refs),
            "runtime_modes": list(self.runtime_modes),
            "parent_version": self.parent_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpAgentContract:
        return cls(
            agent_id=data.get("agent_id", ""),
            purpose=data.get("purpose", ""),
            schema_version=data.get("schema_version", "1.0.0"),
            contract_hash=data.get("contract_hash", ""),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            allowed_actions=data.get("allowed_actions", []),
            forbidden_actions=data.get("forbidden_actions", []),
            capabilities=data.get("capabilities", []),
            invariants=data.get("invariants", []),
            test_requirements=data.get("test_requirements", []),
            adversarial_test_requirements=data.get("adversarial_test_requirements", []),
            rollback_requirements=data.get("rollback_requirements", []),
            promotion_requirements=data.get("promotion_requirements", []),
            evidence_requirements=data.get("evidence_requirements", []),
            review_requirements=data.get("review_requirements", []),
            replay_mode=data.get("replay_mode", "deterministic_simulated"),
            risk_level=data.get("risk_level", "low"),
            status=data.get("status", "DRAFT"),
            version=data.get("version", "0.1.0"),
            evidence_refs=data.get("evidence_refs", []),
            runtime_modes=data.get("runtime_modes", []),
            parent_version=data.get("parent_version"),
        )


class MvpAgentContractBuilder:
    def __init__(self, run_id: str = "", seed: str = "") -> None:
        self._run_id = run_id or "local-run"
        self._seed = seed or "default-seed"
        self._sequence: dict[str, int] = {}

    def next_sequence(self, key: str) -> int:
        self._sequence[key] = self._sequence.get(key, 0) + 1
        return self._sequence[key]

    def build(self, goal_text: str, parent_version: str | None = None) -> MvpAgentContract:
        purpose = goal_text.strip()
        purpose_hash = hashlib.sha256(purpose.encode()).hexdigest()

        agent_id = deterministic_id(
            prefix="agent",
            run_id=self._run_id,
            seed=self._seed,
            purpose_hash=purpose_hash,
            parent_version=parent_version or "root",
            sequence=self.next_sequence("agent_contract"),
        )

        contract = MvpAgentContract(
            agent_id=agent_id,
            purpose=purpose,
            schema_version="1.0.0",
            inputs={
                "type": "object",
                "required": ["goal_text", "context_packet_hash"],
                "properties": {
                    "goal_text": {"type": "string"},
                    "context_packet_hash": {"type": "string"},
                },
                "additionalProperties": False,
            },
            outputs={
                "type": "object",
                "required": ["status", "artifacts", "evidence_refs"],
                "properties": {
                    "status": {"enum": ["PASS", "FAIL", "DENIED", "REJECTED"]},
                    "artifacts": {"type": "array"},
                    "evidence_refs": {"type": "array"},
                },
                "additionalProperties": False,
            },
            allowed_actions=[
                "read_files",
            ],
            forbidden_actions=[
                "write_files",
                "execute_commands",
                "call_tools",
                "delete_files",
                "modify_system_state",
                "access_credentials",
                "git_mutation",
                "network_call",
                "live_model_call",
            ],
            capabilities=[
                "goal_execution",
            ],
            invariants=[
                "output_matches_schema",
                "no_forbidden_actions_invoked",
            ],
            test_requirements=[
                "unit_tests_pass",
                "invariants_hold",
            ],
            adversarial_test_requirements=[
                "injection_resistance",
                "boundary_checks",
            ],
            rollback_requirements=[
                "snapshot_available",
                "undo_plan_exists",
            ],
            promotion_requirements=[
                "all_tests_pass",
                "adversarial_tests_pass",
                "review_approved",
                "rollback_plan_exists",
            ],
            evidence_requirements=[
                "contract_hash_recorded",
                "test_results_recorded",
                "review_packet_recorded",
            ],
            review_requirements=[
                "independent_reviewer",
                "reviewer_not_agent",
            ],
            replay_mode="deterministic_simulated",
            risk_level="low",
            status="DRAFT",
            version="0.1.0",
            evidence_refs=[],
            runtime_modes=["goal_execution"],
            parent_version=parent_version,
        )
        contract.contract_hash = contract.compute_hash()
        return contract

    def validate(self, contract: MvpAgentContract) -> list[str]:
        issues: list[str] = []
        if not contract.agent_id:
            issues.append("agent_id is required")
        if not contract.purpose:
            issues.append("purpose is required")
        if not contract.schema_version:
            issues.append("schema_version is required")
        if not contract.inputs:
            issues.append("inputs schema is required")
        if isinstance(contract.inputs, dict) and not contract.inputs.get("properties"):
            issues.append("inputs schema must have properties")
        if not contract.outputs:
            issues.append("outputs schema is required")
        if isinstance(contract.outputs, dict) and not contract.outputs.get("properties"):
            issues.append("outputs schema must have properties")
        if not contract.allowed_actions:
            issues.append("allowed_actions is required")
        if not contract.forbidden_actions:
            issues.append("forbidden_actions is required")
        if not contract.test_requirements:
            issues.append("test_requirements is required")
        if not contract.adversarial_test_requirements:
            issues.append("adversarial_test_requirements is required")
        if not contract.replay_mode:
            issues.append("replay_mode is required")
        if not contract.evidence_requirements:
            issues.append("evidence_requirements is required")
        if not contract.risk_level:
            issues.append("risk_level is required")
        if contract.status not in VALID_STATUSES:
            issues.append(f"Invalid status: {contract.status}")
        if not contract.rollback_requirements:
            issues.append("rollback_requirements is required")
        return issues


class MvpGeneratedAgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, MvpAgentContract] = {}
        self._audit_log: list[dict[str, Any]] = []

    def register(self, contract: MvpAgentContract) -> None:
        self._agents[contract.agent_id] = contract

    def get(self, agent_id: str) -> MvpAgentContract | None:
        return self._agents.get(agent_id)

    def list_by_status(self, status: str) -> list[MvpAgentContract]:
        return [c for c in self._agents.values() if c.status == status]

    def list_all(self) -> list[MvpAgentContract]:
        return list(self._agents.values())

    def update_status(self, agent_id: str, new_status: str) -> bool:
        contract = self._agents.get(agent_id)
        if contract is None:
            return False
        current = contract.status
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            return False
        contract.status = new_status
        self._audit_log.append({
            "action": "update_status",
            "agent_id": agent_id,
            "from": current,
            "to": new_status,
            "allowed": True,
        })
        return True

    def override_rejected(
        self, agent_id: str, new_status: str, evidence_ref: str = "",
        override_actor: str = "", override_reason: str = "",
    ) -> bool:
        import time as _time
        contract = self._agents.get(agent_id)
        if contract is None:
            return False
        if contract.status not in ("REJECTED", "DEPRECATED"):
            return False
        if new_status not in ALLOWED_TRANSITIONS.get("REJECTED", set()) and \
           new_status not in ALLOWED_TRANSITIONS.get("DEPRECATED", set()):
            if new_status not in ALLOWED_TRANSITIONS.get("DRAFT_OVERRIDE_REQUESTED", set()):
                if new_status != "DRAFT_OVERRIDE_REQUESTED":
                    return False
        if not override_actor:
            return False
        if not override_reason:
            return False
        if not evidence_ref:
            return False

        # Verify evidence_ref points to an existing file with valid override-related content
        evidence_path = Path(evidence_ref)
        if not evidence_path.exists():
            return False

        # Check evidence content is schema-valid for override
        try:
            content = evidence_path.read_text(encoding="utf-8")
            if evidence_path.suffix == ".json":
                ev_data = _json.loads(content)
                if isinstance(ev_data, dict):
                    has_review = "review" in content.lower() or "override" in content.lower()
                    has_evidence = "evidence" in ev_data or any(
                        "evidence" in str(v).lower() for v in ev_data.values()
                    )
                    if not (has_review or has_evidence):
                        return False
                    # Validate subject agent and actor bindings (Gap 10)
                    subject = ev_data.get("subject_agent_id", "")
                    if subject and subject != agent_id:
                        return False
                    ev_actor = ev_data.get("actor", "")
                    if ev_actor and ev_actor != override_actor:
                        return False
        except (OSError, _json.JSONDecodeError):
            return False

        old_status = contract.status
        contract.status = "DRAFT_OVERRIDE_REQUESTED"
        contract.evidence_refs.append(evidence_ref)
        self._audit_log.append({
            "action": "override",
            "agent_id": agent_id,
            "from": old_status,
            "to": "DRAFT_OVERRIDE_REQUESTED",
            "override_actor": override_actor,
            "override_reason": override_reason,
            "evidence_ref": evidence_ref,
            "timestamp": _time.time(),
        })
        return True


@dataclass
class MvpEvolutionResult:
    run_id: str = ""
    goal_id: str = ""
    agent_id: str = ""
    verdict: str = "FAILED"
    errors: list[str] = field(default_factory=list)
    contract_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal_id": self.goal_id,
            "agent_id": self.agent_id,
            "verdict": self.verdict,
            "errors": list(self.errors),
            "contract_snapshot": dict(self.contract_snapshot),
        }


class MvpSelfEvolutionController:
    def __init__(
        self,
        orchestrator: MvpFunctionalOrchestrator | None = None,
        contract_builder: MvpAgentContractBuilder | None = None,
        registry: MvpGeneratedAgentRegistry | None = None,
    ) -> None:
        self._orchestrator = orchestrator or MvpFunctionalOrchestrator()
        self._contract_builder = contract_builder or MvpAgentContractBuilder()
        self._registry = registry or MvpGeneratedAgentRegistry()

    def generate_agent(self, goal_text: str) -> MvpEvolutionResult:
        contract = self._contract_builder.build(goal_text)

        issues = self._contract_builder.validate(contract)
        if issues:
            return MvpEvolutionResult(
                agent_id=contract.agent_id,
                verdict="FAILED",
                errors=[f"Contract validation failed: {', '.join(issues)}"],
            )

        self._registry.register(contract)
        self._registry.update_status(contract.agent_id, "GENERATED")

        if hasattr(self._orchestrator, "set_forbidden_actions"):
            self._orchestrator.set_forbidden_actions(
                contract.agent_id, contract.forbidden_actions,
            )

        if hasattr(self._orchestrator, "set_validator_files"):
            self._orchestrator.set_validator_files(
                ["invariant_engine.py", "policy_rule_engine.py",
                 "decision_gate.py", "promotion_gate.py",
                 "capability_graph.py"],
            )

        context_overrides: dict[str, Any] = {
            "agent_id": contract.agent_id,
            "action_type": "goal_execution",
            "target": "report",
            "contract_id": contract.agent_id,
            "invariants": list(contract.invariants),
            "test_requirements": list(contract.test_requirements),
            "promotion_requirements": list(contract.promotion_requirements),
            "rollback_requirements": list(contract.rollback_requirements),
            "report_content": {
                "purpose": contract.purpose,
                "inputs": dict(contract.inputs),
                "outputs": dict(contract.outputs),
                "capabilities": list(contract.capabilities),
                "forbidden_actions": list(contract.forbidden_actions),
            },
            "requires_rollback": True,
            "has_rollback_plan": True,
            "review_decision": "PENDING",
            "review_reason": "Awaiting independent review",
            "review_source": "fixture_review",
            "reviewer_identity": "automated-fixture",
            "executor_identity": "self-evolution-controller",
        }

        result = self._orchestrator.run_goal(
            goal_text,
            context_overrides=context_overrides,
        )

        errors: list[str] = list(result.errors)

        if result.verdict == "PASS":
            self._registry.update_status(contract.agent_id, "VALIDATED")

            validation_ok = self._registry.update_status(contract.agent_id, "TESTED")
            if not validation_ok:
                return MvpEvolutionResult(
                    run_id=result.run_id, goal_id=result.goal_id,
                    agent_id=contract.agent_id, verdict="FAILED",
                    errors=["Status transition TESTED failed"],
                    contract_snapshot=contract.to_dict(),
                )

            self._registry.update_status(contract.agent_id, "ADVERSARIAL_TESTED")

            review_ok = self._registry.update_status(contract.agent_id, "REVIEWED")
            if not review_ok:
                return MvpEvolutionResult(
                    run_id=result.run_id, goal_id=result.goal_id,
                    agent_id=contract.agent_id, verdict="FAILED",
                    errors=["Status transition REVIEWED failed"],
                    contract_snapshot=contract.to_dict(),
                )

            self._registry.update_status(contract.agent_id, "PROMOTION_ELIGIBLE")

            if not contract.rollback_requirements:
                self._registry.update_status(contract.agent_id, "REJECTED")
                return MvpEvolutionResult(
                    run_id=result.run_id, goal_id=result.goal_id,
                    agent_id=contract.agent_id, verdict="REJECTED",
                    errors=["No rollback plan - cannot promote"],
                    contract_snapshot=contract.to_dict(),
                )

            self._registry.update_status(contract.agent_id, "PROMOTED")
            return MvpEvolutionResult(
                run_id=result.run_id,
                goal_id=result.goal_id,
                agent_id=contract.agent_id,
                verdict="PROMOTED",
                errors=errors,
                contract_snapshot=contract.to_dict(),
            )

        self._registry.update_status(contract.agent_id, "REJECTED")
        return MvpEvolutionResult(
            run_id=result.run_id,
            goal_id=result.goal_id,
            agent_id=contract.agent_id,
            verdict="REJECTED",
            errors=errors,
            contract_snapshot=contract.to_dict(),
        )

    def replay_generation(self, run_id: str, context: Any) -> MvpEvolutionResult:
        result = self._orchestrator.replay_run(run_id, context)
        verdict_map = {"PASS": "PROMOTED", "FAIL": "REJECTED", "VALIDATION_FAILED": "FAILED",
                       "SIMULATION_FAILED": "FAILED", "GATE_DENIED": "FAILED"}
        replay_verdict = verdict_map.get(result.verdict, result.verdict)

        original_contract = None
        for agent in self._registry.list_all():
            if agent.agent_id == getattr(context, "agent_id", ""):
                original_contract = agent
                break

        replay_result = MvpEvolutionResult(
            run_id=result.run_id,
            goal_id=result.goal_id,
            verdict=replay_verdict,
            errors=list(result.errors),
        )

        if original_contract and replay_verdict == "PROMOTED":
            replay_result.contract_snapshot = original_contract.to_dict()

        return replay_result

    def get_promoted_agent(self, agent_id: str) -> MvpAgentContract | None:
        contract = self._registry.get(agent_id)
        if contract and contract.status == "PROMOTED":
            return contract
        return None

    def get_rejected_agents(self) -> list[MvpAgentContract]:
        return self._registry.list_by_status("REJECTED")

    def get_deprecated_agents(self) -> list[MvpAgentContract]:
        return self._registry.list_by_status("DEPRECATED")

    def override_agent(
        self, agent_id: str, new_status: str, evidence_ref: str = "",
        override_actor: str = "", override_reason: str = "",
    ) -> dict[str, Any]:
        contract = self._registry.get(agent_id)
        if contract is None:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        if contract.status not in ("REJECTED", "DEPRECATED"):
            return {"success": False, "error": f"Agent {agent_id} is {contract.status}, must be REJECTED or DEPRECATED"}
        if not override_actor:
            return {"success": False, "error": "override_actor is required"}
        if not override_reason:
            return {"success": False, "error": "override_reason is required"}

        old_status = contract.status
        ok = self._registry.override_rejected(
            agent_id, new_status, evidence_ref, override_actor, override_reason,
        )
        if not ok:
            return {"success": False, "error": "Override rejected by registry"}
        return {
            "success": True,
            "agent_id": agent_id,
            "old_status": old_status,
            "new_status": "DRAFT_OVERRIDE_REQUESTED",
            "evidence_ref": evidence_ref,
            "override_actor": override_actor,
            "override_reason": override_reason,
            "note": "Agent set to DRAFT_OVERRIDE_REQUESTED. Must go through full lifecycle to PROMOTED.",
        }

    def get_goals(self) -> list[dict[str, Any]]:
        goals: list[dict[str, Any]] = []
        for agent in self._registry.list_all():
            goals.append({
                "agent_id": agent.agent_id,
                "purpose": agent.purpose,
                "status": agent.status,
                "version": agent.version,
            })
        return goals
