from __future__ import annotations

from pathlib import Path
from typing import Any

from agentx_evolve.policy.initiator_policy_compat import (
    InitiatorPolicyCompat,
    get_policy_registry,
)
from agentx_evolve.policy.policy_registry import PolicyRegistry
from agentx_evolve.policy.policy_models import PolicyDecision


class SandboxPolicyCompat:
    def __init__(self, repo_root: Path | None = None) -> None:
        self._initiator_compat = InitiatorPolicyCompat(repo_root)

    def get_repo_root(self) -> Path:
        return self._initiator_compat.get_repo_root()

    def get_policy_runtime_root(self) -> Path:
        return self._initiator_compat.get_policy_runtime_root()

    def validate_schema(self, artifact: dict, schema_id: str) -> dict:
        return self._initiator_compat.validate_schema(artifact, schema_id)

    def write_json_atomic(self, path: Path, artifact: dict) -> dict:
        return self._initiator_compat.write_json_atomic(path, artifact)

    def append_audit_event(self, event: dict) -> dict:
        return self._initiator_compat.append_audit_event(event)

    def append_policy_decision(self, decision: PolicyDecision) -> dict:
        return self._initiator_compat.append_policy_decision(decision)

    def write_latest_policy_decision(self, decision: PolicyDecision) -> dict:
        return self._initiator_compat.write_latest_policy_decision(decision)

    def get_policy_registry(self, *args: Any, **kwargs: Any) -> PolicyRegistry | None:
        return get_policy_registry(*args, **kwargs)


__all__ = [
    "SandboxPolicyCompat",
]
