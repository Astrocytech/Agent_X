from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpSecurityEnvelope:
    run_id: str = ""
    action_id: str = ""
    agent_identity: str = ""
    workspace_id: str = ""
    runtime_profile_id: str = ""
    capabilities: list[str] = field(default_factory=list)
    policy_decisions: list[dict[str, str]] = field(default_factory=list)
    budget_reservation: str | None = None
    transaction_id: str = ""
    evidence_target: str = ""
    allowed_effects: list[str] = field(default_factory=list)
    forbidden_effects: list[str] = field(default_factory=list)
    _sealed: bool = False

    def seal(self) -> None:
        self._sealed = True

    def is_sealed(self) -> bool:
        return self._sealed

    def validate(self) -> list[str]:
        issues = []
        if not self.run_id:
            issues.append("run_id required")
        if not self.action_id:
            issues.append("action_id required")
        if not self.agent_identity:
            issues.append("agent_identity required")
        if not self.workspace_id:
            issues.append("workspace_id required")
        if not self.runtime_profile_id:
            issues.append("runtime_profile_id required")
        if not self.evidence_target:
            issues.append("evidence_target required")
        return issues

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "action_id": self.action_id,
            "agent_identity": self.agent_identity,
            "workspace_id": self.workspace_id,
            "runtime_profile_id": self.runtime_profile_id,
            "capabilities": list(self.capabilities),
            "policy_decisions": list(self.policy_decisions),
            "budget_reservation": self.budget_reservation,
            "transaction_id": self.transaction_id,
            "evidence_target": self.evidence_target,
            "allowed_effects": list(self.allowed_effects),
            "forbidden_effects": list(self.forbidden_effects),
            "sealed": self._sealed,
        }


class MvpEnvelopeBuilder:
    def __init__(self) -> None:
        self._envelope = MvpSecurityEnvelope()

    def with_run(self, run_id: str) -> MvpEnvelopeBuilder:
        self._envelope.run_id = run_id
        return self

    def with_action(self, action_id: str) -> MvpEnvelopeBuilder:
        self._envelope.action_id = action_id
        return self

    def with_agent(self, identity: str) -> MvpEnvelopeBuilder:
        self._envelope.agent_identity = identity
        return self

    def with_workspace(self, workspace_id: str) -> MvpEnvelopeBuilder:
        self._envelope.workspace_id = workspace_id
        return self

    def with_profile(self, profile_id: str) -> MvpEnvelopeBuilder:
        self._envelope.runtime_profile_id = profile_id
        return self

    def with_capabilities(self, caps: list[str]) -> MvpEnvelopeBuilder:
        self._envelope.capabilities = list(caps)
        return self

    def with_policy_decisions(self, decisions: list[dict[str, str]]) -> MvpEnvelopeBuilder:
        self._envelope.policy_decisions = list(decisions)
        return self

    def with_transaction(self, txn_id: str) -> MvpEnvelopeBuilder:
        self._envelope.transaction_id = txn_id
        return self

    def with_evidence_target(self, target: str) -> MvpEnvelopeBuilder:
        self._envelope.evidence_target = target
        return self

    def with_allowed_effects(self, effects: list[str]) -> MvpEnvelopeBuilder:
        self._envelope.allowed_effects = list(effects)
        return self

    def with_forbidden_effects(self, effects: list[str]) -> MvpEnvelopeBuilder:
        self._envelope.forbidden_effects = list(effects)
        return self

    def build(self) -> MvpSecurityEnvelope:
        if not self._envelope.is_valid():
            raise ValueError(f"Invalid envelope: {self._envelope.validate()}")
        return self._envelope


class MvpEnvelopeValidator:
    @staticmethod
    def validate_envelope(envelope: MvpSecurityEnvelope, context: dict) -> list[str]:
        issues = []
        if not envelope.is_sealed():
            issues.append("Envelope not sealed")
        if context.get("agent_id") and envelope.agent_identity != context["agent_id"]:
            issues.append("Agent mismatch")
        if context.get("action_id") and envelope.action_id != context["action_id"]:
            issues.append("Action mismatch")
        return issues
