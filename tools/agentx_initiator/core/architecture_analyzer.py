from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4
from agentx_initiator.core.repo_model import (
    RepositoryScanResult, ArchitectureReport, LayerEntry,
)
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.layer_mapper import build_layer_map
from agentx_initiator.core.path_registry import get_path, _detect_repo_root


@dataclass
class ArchitectureFinding:
    finding_id: str = ""
    category: str = "INFO"
    title: str = ""
    description: str = ""
    affected_paths: list[str] = field(default_factory=list)
    affected_layers: list[str] = field(default_factory=list)
    confidence: str = "MEDIUM"
    evidence_ids: list[str] = field(default_factory=list)
    source: str = ""
    recommendation_scope: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ArchitectureEvidence:
    evidence_id: str = ""
    source_scan_id: str = ""
    source_path: str = ""
    source_artifact: str = "file"
    detection_rule: str = ""
    supports: str = ""
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ArchitectureRelationship:
    relationship_id: str = ""
    source: str = ""
    target: str = ""
    relationship_type: str = "unknown"
    confidence: str = "MEDIUM"
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ArchitectureReportResult:
    schema_version: str = "1.0"
    report_id: str = ""
    timestamp: str = ""
    status: str = "PASS"
    layer_summary: dict = field(default_factory=dict)
    protected_count: int = 0
    total_files: int = 0
    findings: list[ArchitectureFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence: list[ArchitectureEvidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_architecture() -> ArchitectureReport:
    """Backward-compat: scan repo and return old ArchitectureReport."""
    scan = scan_repo()
    mapping = build_layer_map()
    layers = scan.layers
    l0_independent = True
    l1_separated = True
    l2_runtime = False
    risks = []

    for name, info in mapping.items():
        if isinstance(info, dict):
            for v in info.get("violations", []):
                if name == "L2" and "runtime" in v.lower():
                    l2_runtime = True
                risks.append({
                    "layer": name,
                    "concern": v,
                    "severity": "medium",
                })

    if not risks:
        for entry in layers:
            if entry.layer == "unknown" and entry.file_count > 0:
                risks.append({
                    "layer": "unknown",
                    "concern": f"{entry.file_count} file(s) unclassified",
                    "severity": "low",
                })

    return ArchitectureReport(
        layers=layers,
        layer_count=len(layers),
        valid_layer_structure=all(l.has_readme for l in layers),
        l0_independent=l0_independent,
        l1_separated=l1_separated,
        l2_contains_active_runtime=l2_runtime,
        risks=risks,
    )


def analyze_scan(scan_result: RepositoryScanResult) -> ArchitectureReportResult:
    report_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    findings: list[ArchitectureFinding] = []
    evidence_list: list[ArchitectureEvidence] = []
    warnings: list[str] = []
    errors: list[str] = []

    layer_summary: dict[str, int] = {}
    protected_count = 0

    for f in scan_result.files:
        layer_summary[f.detected_layer] = layer_summary.get(f.detected_layer, 0) + 1
        if f.is_protected:
            protected_count += 1

    for layer, count in sorted(layer_summary.items()):
        if layer == "unknown" and count > 0:
            ev = ArchitectureEvidence(
                evidence_id=str(uuid4()),
                source_scan_id=scan_result.scan_id,
                source_path="",
                source_artifact="summary",
                supports=f"{count} files in unknown layer",
                confidence="MEDIUM",
            )
            evidence_list.append(ev)
            findings.append(ArchitectureFinding(
                finding_id=str(uuid4()),
                category="WARNING",
                title="Files in unknown layer",
                description=f"{count} file(s) could not be classified into L0/L1/L2",
                affected_layers=["unknown"],
                confidence="MEDIUM",
                evidence_ids=[ev.evidence_id],
                source="architecture_analyzer",
            ))
            warnings.append(f"{count} file(s) in unknown layer")

    for f in scan_result.files:
        if f.is_protected and f.trust_level != "HIGH":
            findings.append(ArchitectureFinding(
                finding_id=str(uuid4()),
                category="INFO",
                title="Protected file with non-HIGH trust level",
                description=f"{f.relative_path} is protected but trust is {f.trust_level}",
                affected_paths=[f.path],
                affected_layers=[f.detected_layer],
                confidence="HIGH",
                source="architecture_analyzer",
            ))

    if scan_result.warnings:
        for w in scan_result.warnings:
            findings.append(ArchitectureFinding(
                finding_id=str(uuid4()),
                category="WARNING",
                title="Scanner warning",
                description=w,
                confidence="HIGH",
                source="architecture_analyzer",
            ))

    status = "PASS"
    if scan_result.errors:
        status = "FAIL"
        errors.extend(scan_result.errors)
    elif findings:
        status = "PARTIAL"

    return ArchitectureReportResult(
        report_id=report_id,
        timestamp=timestamp,
        status=status,
        layer_summary=layer_summary,
        protected_count=protected_count,
        total_files=scan_result.total_files,
        findings=findings,
        warnings=warnings,
        errors=errors,
        evidence=evidence_list,
    )
