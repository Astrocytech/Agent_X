from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional


SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
CONFIDENCES = ["LOW", "MEDIUM", "HIGH"]
CATEGORIES = [
    "ARCHITECTURE_RISK", "GOVERNANCE_RISK", "IMPLEMENTATION_RISK",
    "TESTING_RISK", "SCHEMA_RISK", "DEPENDENCY_RISK", "BOUNDARY_RISK",
    "EVIDENCE_RISK", "UNKNOWN_RISK",
]
MITIGATION_TYPES = [
    "ADD_TESTS", "ADD_VALIDATION", "ADD_SCHEMA", "ADD_EVIDENCE",
    "REQUEST_REVIEW", "DEFER", "BLOCK_FOR_GOVERNANCE_REVIEW",
]


@dataclass
class RiskSignal:
    signal_type: str = ""
    source: str = ""
    source_path: str = ""
    claim: str = ""
    severity: str = "LOW"
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskContext:
    architecture_report: Optional[dict] = None
    repository_scan_summary: Optional[dict] = None
    governance_decision: Optional[dict] = None
    evolution_plan: Optional[dict] = None
    patch_proposal: Optional[dict] = None
    validation_report: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskEvidence:
    schema_version: str = "1.0"
    evidence_id: str = ""
    source_artifact: str = ""
    source_id: str = ""
    source_path: str = ""
    claim: str = ""
    supports: str = ""
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskMitigation:
    schema_version: str = "1.0"
    mitigation_id: str = ""
    risk_ids: list = field(default_factory=list)
    mitigation_type: str = ""
    description: str = ""
    execution_authority: str = "none"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskItem:
    schema_version: str = "1.0"
    risk_id: str = ""
    category: str = "UNKNOWN_RISK"
    severity: str = "LOW"
    confidence: str = "MEDIUM"
    title: str = ""
    description: str = ""
    source_refs: list = field(default_factory=list)
    evidence_ids: list = field(default_factory=list)
    mitigation_ids: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskAssessment:
    schema_version: str = "1.0"
    assessment_id: str = ""
    timestamp: str = ""
    source_component: str = "RiskEngine"
    status: str = "PASS"
    overall_risk: str = "LOW"
    input_refs: list = field(default_factory=list)
    risk_items: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    mitigations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
