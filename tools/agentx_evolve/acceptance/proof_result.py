from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


ACCEPTABLE_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED", "UNKNOWN", "OUT_OF_SCOPE"})


@dataclass
class CommandResult:
    command: str = ""
    exit_code: int = -1
    stdout_summary: str = ""
    stderr_summary: str = ""
    timestamp: str = ""
    duration_seconds: float = 0.0
    git_commit: str = ""
    branch: str = ""
    environment: str = ""
    source: str = "subprocess"
    provenance_id: str = ""
    stdout_hash: str = ""
    stderr_hash: str = ""
    stdout_log: str = ""
    stderr_log: str = ""
    cmd_index: int = -1
    working_directory: str = ""
    recorded_by: str = ""
    source_detail: str = ""
    redacted: bool = True
    redaction_applied: bool = True
    failure_code: str = ""
    phase: str = ""
    component: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout_summary": self.stdout_summary,
            "stderr_summary": self.stderr_summary,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "git_commit": self.git_commit,
            "branch": self.branch,
            "environment": self.environment,
            "source": self.source,
            "provenance_id": self.provenance_id,
            "stdout_hash": self.stdout_hash,
            "stderr_hash": self.stderr_hash,
            "stdout_log": self.stdout_log,
            "stderr_log": self.stderr_log,
            "cmd_index": self.cmd_index,
            "working_directory": self.working_directory,
            "recorded_by": self.recorded_by,
            "source_detail": self.source_detail,
            "redacted": self.redacted,
            "redaction_applied": self.redaction_applied,
            "failure_code": self.failure_code,
            "phase": self.phase,
            "component": self.component,
        }

    def validate(self) -> list[str]:
        errors = []
        if self.source in ("static", ""):
            errors.append("source must be subprocess")
        if self.exit_code == -1:
            errors.append("exit_code missing")
        if not self.timestamp:
            errors.append("timestamp missing")
        if not self.git_commit:
            errors.append("git_commit missing")
        if not self.environment:
            errors.append("environment missing")
        return errors


@dataclass
class ScenarioProof:
    scenario_name: str = ""
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class ReplayProof:
    scenario_name: str = ""
    original_verdict: str = ""
    replay_verdict: str = ""
    verdict_match: bool = False
    artifact_hashes_match: bool = False
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "original_verdict": self.original_verdict,
            "replay_verdict": self.replay_verdict,
            "verdict_match": self.verdict_match,
            "artifact_hashes_match": self.artifact_hashes_match,
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class SourceMutationProof:
    before_manifest_path: str = ""
    after_manifest_path: str = ""
    mutation_detected: bool = False
    mutation_report_path: str = ""
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "before_manifest_path": self.before_manifest_path,
            "after_manifest_path": self.after_manifest_path,
            "mutation_detected": self.mutation_detected,
            "mutation_report_path": self.mutation_report_path,
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class ArtifactSafetyProof:
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class CompatibilityProof:
    verdict: str = "UNKNOWN"
    checks: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "checks": self.checks,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class ReuseMapProof:
    status: str = "UNKNOWN"
    regenerated: bool = False
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "regenerated": self.regenerated,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class RequirementTraceProof:
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class GapDiscoveryProof:
    status: str = "UNKNOWN"
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class AntiFalsePassProof:
    status: str = "UNKNOWN"
    attacks_tested: int = 0
    attacks_rejected: int = 0
    attacks_accepted: list[str] = field(default_factory=list)
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    created_at: str = ""
    git_commit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "attacks_tested": self.attacks_tested,
            "attacks_rejected": self.attacks_rejected,
            "attacks_accepted": self.attacks_accepted,
            "evidence_refs": self.evidence_refs,
            "errors": self.errors,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "git_commit": self.git_commit,
        }


@dataclass
class AcceptanceRowProof:
    component: str = ""
    status: str = "UNKNOWN"
    details: str = ""
    evidence_refs: list[dict[str, str]] = field(default_factory=list)
    proof_type: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "details": self.details,
            "evidence_refs": self.evidence_refs,
            "proof_type": self.proof_type,
        }


@dataclass
class FunctionalMvpProofBundle:
    git_commit: str = ""
    tree_hash: str = ""
    parent_commit: str = ""
    branch: str = ""
    remote_url: str = ""
    detached: bool = False
    proof_run_id: str = ""
    created_at: str = ""
    command_proofs: list[CommandResult] = field(default_factory=list)
    scenario_proofs: list[ScenarioProof] = field(default_factory=list)
    replay_proofs: list[ReplayProof] = field(default_factory=list)
    source_mutation_proof: SourceMutationProof | None = None
    artifact_safety_proof: ArtifactSafetyProof | None = None
    compatibility_proof: CompatibilityProof | None = None
    reuse_map_proof: ReuseMapProof | None = None
    requirement_trace_proof: RequirementTraceProof | None = None
    gap_discovery_proof: GapDiscoveryProof | None = None
    anti_false_pass_proof: AntiFalsePassProof | None = None
    acceptance_rows: list[AcceptanceRowProof] = field(default_factory=list)
    invariant_results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    report_hashes: dict[str, str] = field(default_factory=dict)
    proof_config: dict[str, str] = field(default_factory=dict)
    source_tree: dict[str, str] = field(default_factory=dict)
    toolchain_hashes: dict[str, str] = field(default_factory=dict)
    generator_proofs: list[dict[str, Any]] = field(default_factory=list)
    final_verifier: dict[str, str] = field(default_factory=dict)
    classification_rules: dict[str, Any] = field(default_factory=dict)
    cleanup_performed: str = ""
    environment: dict[str, str] = field(default_factory=dict)
    parallelism: str = ""
    generator_metadata: dict[str, str] = field(default_factory=dict)
    dependency_graph: list[dict[str, str]] = field(default_factory=list)
    corrective_list: dict[str, str] = field(default_factory=dict)
    schema_version: str = ""
    makefile_hash: str = ""
    io_boundary: dict[str, Any] = field(default_factory=lambda: {"network": False, "subprocess": True})
    offline_mode: bool = False
    redaction_proof: dict[str, Any] = field(default_factory=dict)
    allowed_side_effects: dict[str, Any] = field(default_factory=dict)
    proof_run_lock: str = "serial_executor_guard (single-run, no concurrent executions)"
    platform: dict[str, str] = field(default_factory=dict)
    resources: dict[str, str] = field(default_factory=dict)
    container: dict[str, str] = field(default_factory=dict)
    locale: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "git_commit": self.git_commit,
            "tree_hash": self.tree_hash,
            "parent_commit": self.parent_commit,
            "branch": self.branch,
            "remote_url": self.remote_url,
            "detached": self.detached,
            "proof_run_id": self.proof_run_id,
            "created_at": self.created_at,
            "command_proofs": [c.to_dict() for c in self.command_proofs],
            "scenario_proofs": [s.to_dict() for s in self.scenario_proofs],
            "replay_proofs": [r.to_dict() for r in self.replay_proofs],
            "source_mutation_proof": self.source_mutation_proof.to_dict() if self.source_mutation_proof else None,
            "artifact_safety_proof": self.artifact_safety_proof.to_dict() if self.artifact_safety_proof else None,
            "compatibility_proof": self.compatibility_proof.to_dict() if self.compatibility_proof else None,
            "reuse_map_proof": self.reuse_map_proof.to_dict() if self.reuse_map_proof else None,
            "requirement_trace_proof": self.requirement_trace_proof.to_dict() if self.requirement_trace_proof else None,
            "gap_discovery_proof": self.gap_discovery_proof.to_dict() if self.gap_discovery_proof else None,
            "anti_false_pass_proof": self.anti_false_pass_proof.to_dict() if self.anti_false_pass_proof else None,
            "acceptance_rows": [r.to_dict() for r in self.acceptance_rows],
            "invariant_results": self.invariant_results,
            "errors": self.errors,
            "report_hashes": self.report_hashes,
            "proof_config": self.proof_config,
            "source_tree": self.source_tree,
            "toolchain_hashes": self.toolchain_hashes,
            "generator_proofs": self.generator_proofs,
            "final_verifier": self.final_verifier,
            "classification_rules": self.classification_rules,
            "cleanup_performed": self.cleanup_performed,
            "environment": self.environment,
            "parallelism": self.parallelism,
            "generator_metadata": self.generator_metadata,
            "dependency_graph": self.dependency_graph,
            "corrective_list": self.corrective_list,
            "schema_version": self.schema_version,
            "makefile_hash": self.makefile_hash,
            "io_boundary": self.io_boundary,
            "offline_mode": self.offline_mode,
            "redaction_proof": self.redaction_proof,
            "allowed_side_effects": self.allowed_side_effects,
            "proof_run_lock": self.proof_run_lock,
            "platform": self.platform,
            "resources": self.resources,
            "container": self.container,
            "locale": self.locale,
        }
        return d

    def hash_report(self, path: str) -> str:
        try:
            import hashlib
            return hashlib.sha256(open(path, "rb").read()).hexdigest()
        except OSError:
            return ""

    def set_report_hash(self, path: str) -> None:
        self.report_hashes[path] = self.hash_report(path)


def create_proof_bundle(git_commit: str, proof_run_id: str = "") -> FunctionalMvpProofBundle:
    now = datetime.now(timezone.utc).isoformat()
    return FunctionalMvpProofBundle(
        git_commit=git_commit,
        proof_run_id=proof_run_id,
        created_at=now,
    )
