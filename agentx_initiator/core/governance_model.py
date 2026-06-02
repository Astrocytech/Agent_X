from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


GOVERNANCE_ACTIONS = [
    "READ_FILE", "WRITE_FILE", "CREATE_FILE", "DELETE_FILE", "MODIFY_FILE",
    "WRITE_ARTIFACT", "RUN_VALIDATION", "GENERATE_REPORT", "GENERATE_PLAN",
    "GENERATE_PROPOSAL", "QUERY_MEMORY", "READ_AUDIT", "UNKNOWN",
]

GOVERNANCE_DECISIONS = ["ALLOW", "WARN", "BLOCK"]


@dataclass
class GovernanceRequest:
    schema_version: str = "1.0"
    request_id: str = ""
    timestamp: str = ""
    source_component: str = ""
    action_type: str = "UNKNOWN"
    reason: str = ""
    requested_effect: str = ""
    target_path: Optional[str] = None
    target_resource: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernanceContext:
    repo_root: Path = Path(".")
    runtime_root: Path = Path(".agentx-init")
    protected_path_map: dict = field(default_factory=dict)
    path_registry: Optional[object] = None
    config: Optional[object] = None

    def to_dict(self) -> dict:
        return {
            "repo_root": str(self.repo_root),
            "runtime_root": str(self.runtime_root),
        }


@dataclass
class GovernanceEvidence:
    schema_version: str = "1.0"
    evidence_id: str = ""
    request_id: str = ""
    rule_id: str = ""
    source: str = ""
    source_path: str = ""
    claim: str = ""
    confidence: str = "HIGH"
    supports_decision: str = "BLOCK"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernanceViolation:
    schema_version: str = "1.0"
    violation_id: str = ""
    request_id: str = ""
    rule_id: str = ""
    violation_type: str = ""
    target: str = ""
    severity: str = "HIGH"
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernanceDecision:
    schema_version: str = "1.0"
    decision_id: str = ""
    request_id: str = ""
    timestamp: str = ""
    decision: str = "BLOCK"
    decision_reason: str = ""
    applied_rule_ids: list = field(default_factory=list)
    evidence_ids: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    required_approvals: list = field(default_factory=list)
    source_component: str = "GovernanceEngine"
    status: str = "PASS"

    def to_dict(self) -> dict:
        return asdict(self)
