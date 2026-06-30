from __future__ import annotations

from typing import Any

from agentx_evolve.adapters import AdapterRegistry
from agentx_evolve.evidence.evidence_bridge import EvidenceBridge, EvidencePacket
from agentx_evolve.adapters.adapter_failures import FailureClass, ADAPTER_FAILURE_CLASSES, failure_outcome
from agentx_evolve.adapters.replay_policy import ReplayPolicy, ReplayMode


class AdapterConformance:
    @staticmethod
    def check_schema_validation(adapter_id: str, schemas: list[str]) -> list[str]:
        issues: list[str] = []
        if not schemas:
            issues.append(f"{adapter_id}: no schemas declared")
        return issues

    @staticmethod
    def check_capability_declaration(adapter_id: str, capabilities: list[str]) -> list[str]:
        issues: list[str] = []
        if not capabilities:
            issues.append(f"{adapter_id}: no capabilities declared")
        return issues

    @staticmethod
    def check_security_envelope(adapter_id: str, requires_envelope: bool) -> list[str]:
        if not requires_envelope:
            return [f"{adapter_id}: must require security envelope"]
        return []

    @staticmethod
    def check_failure_taxonomy(failure_class: str) -> list[str]:
        if failure_class not in ADAPTER_FAILURE_CLASSES:
            return [f"{failure_class}: unknown failure class"]
        outcome = failure_outcome(failure_class)
        if outcome == "PASS":
            return [f"{failure_class}: failure cannot map to PASS"]
        return []

    @staticmethod
    def check_replay_mode(adapter_id: str, mode: ReplayMode) -> list[str]:
        if mode == ReplayMode.LIVE_NON_REPLAYABLE:
            return [f"{adapter_id}: live_non_replayable adapters must have recorded_replay fallback"]
        return []

    @staticmethod
    def run_all(adapter_id: str, capabilities: list[str], schemas: list[str],
                requires_envelope: bool, mode: ReplayMode) -> list[str]:
        issues: list[str] = []
        issues.extend(AdapterConformance.check_schema_validation(adapter_id, schemas))
        issues.extend(AdapterConformance.check_capability_declaration(adapter_id, capabilities))
        issues.extend(AdapterConformance.check_security_envelope(adapter_id, requires_envelope))
        issues.extend(AdapterConformance.check_replay_mode(adapter_id, mode))
        return issues
