from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

CLI_RESULT_SCHEMA = "agentx.cli_result.v1"
FINAL_VERDICT_SCHEMA = "agentx.final_verdict.v1"
EVIDENCE_MANIFEST_SCHEMA = "agentx.evidence_manifest.v1"
IMPLEMENTATION_LEDGER_SCHEMA = "agentx.implementation_ledger.v1"

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_BLOCKED = 2
EXIT_INVALID_CLI = 3
EXIT_PROVIDER_ERROR = 4
EXIT_VALIDATION_FAIL = 5
EXIT_ARTIFACT_FAIL = 6

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_BLOCKED = "BLOCKED"

STATUS_MAP = {
    EXIT_PASS: STATUS_PASS,
    EXIT_FAIL: STATUS_FAIL,
    EXIT_BLOCKED: STATUS_BLOCKED,
    EXIT_INVALID_CLI: STATUS_BLOCKED,
    EXIT_PROVIDER_ERROR: STATUS_FAIL,
    EXIT_VALIDATION_FAIL: STATUS_FAIL,
    EXIT_ARTIFACT_FAIL: STATUS_FAIL,
}


@dataclass
class CLIResult:
    command: str = ""
    status: str = STATUS_PASS
    exit_code: int = EXIT_PASS
    run_id: str = ""
    run_dir: str = ""
    message: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": CLI_RESULT_SCHEMA,
            "command": self.command,
            "status": self.status,
            "exit_code": self.exit_code,
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "message": self.message,
            "artifacts": dict(self.artifacts),
            **self.extra,
        }


@dataclass
class FinalVerdict:
    command: str = ""
    status: str = STATUS_PASS
    exit_code: int = EXIT_PASS
    run_id: str = ""
    summary: str = ""
    failures: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    validation_status: str = STATUS_PASS

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": FINAL_VERDICT_SCHEMA,
            "command": self.command,
            "status": self.status,
            "exit_code": self.exit_code,
            "run_id": self.run_id,
            "summary": self.summary,
            "failures": list(self.failures),
            "blocked_reasons": list(self.blocked_reasons),
            "validation_status": self.validation_status,
        }


@dataclass
class EvidenceManifest:
    run_id: str = ""
    command: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    source_mutation_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EVIDENCE_MANIFEST_SCHEMA,
            "run_id": self.run_id,
            "command": self.command,
            "artifacts": list(self.artifacts),
            "commands_run": list(self.commands_run),
            "source_mutation_detected": self.source_mutation_detected,
        }


@dataclass
class ImplementationLedger:
    run_id: str = ""
    repo_drift_notes: list[str] = field(default_factory=list)
    compatibility_shims_used: list[str] = field(default_factory=list)
    deviations_from_brief: list[str] = field(default_factory=list)
    files_changed_by_command: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": IMPLEMENTATION_LEDGER_SCHEMA,
            "run_id": self.run_id,
            "repo_drift_notes": list(self.repo_drift_notes),
            "compatibility_shims_used": list(self.compatibility_shims_used),
            "deviations_from_brief": list(self.deviations_from_brief),
            "files_changed_by_command": list(self.files_changed_by_command),
        }
