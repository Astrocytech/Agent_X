from __future__ import annotations
from dataclasses import dataclass, field, asdict


VALID_STATUSES = ["PENDING", "PASS", "FAIL", "TIMEOUT", "ERROR"]


@dataclass
class ValidationAllowlistEntry:
    schema_version: str = "1.0"
    entry_id: str = ""
    command_pattern: str = ""
    source: str = ""
    category: str = "allowlisted"
    max_timeout: int = 60
    allow_exit_codes: list = field(default_factory=lambda: [0])

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationRun:
    schema_version: str = "1.0"
    run_id: str = ""
    command: str = ""
    status: str = "PENDING"
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    entry_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationManifest:
    schema_version: str = "1.0"
    manifest_id: str = ""
    report_id: str = ""
    run_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    created_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationAudit:
    schema_version: str = "1.0"
    audit_id: str = ""
    event_type: str = ""
    report_id: str = ""
    timestamp: str = ""
    source_component: str = "ValidationRunner"
    status: str = "INITIATED"
    artifacts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
