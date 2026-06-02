from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from agentx_initiator.core.config_model import ConfigRecord, ConfigValidationReport
from agentx_initiator.core.path_registry import get_path


DEFAULT_CONFIG = {
    "agentx_init": {
        "version": "1.0.0",
        "state_dir": ".agentx-init",
        "log_level": "info",
        "allowlisted_commands": [
            "python -m compileall -q",
            "python -m pytest --co -q",
            "make prove-seed",
            "make prove-l1",
            "make prove-l2",
        ],
        "protected_paths": [
            "L0/CODE/core_kernel",
            "L0/CODE/governance",
            "L0/CODE/kernel_composition",
        ],
        "blocked_paths": [
            "L0/CODE",
            ".agentx-init",
        ],
        "risk_levels": {
            "R0": "read-only or tool-owned output",
            "R1": "planning, proposals, allowlisted validation",
            "R2": "future docs/tests/schema/profile modifications",
            "R3": "future governance or L1 behavior changes",
            "R4": "L0, promotion, permission behavior, self-modification, governance bypass",
        },
        "max_risk_allowed": "R1",
    }
}


_SPEC_DEFAULT = ConfigRecord().to_dict()


class AgentXInitConfig(BaseModel):
    version: str
    state_dir: str
    log_level: str
    allowlisted_commands: list[str]
    protected_paths: list[str]
    blocked_paths: list[str]
    risk_levels: dict[str, str]
    max_risk_allowed: str


def load_config(config_path: Optional[Path] = None) -> AgentXInitConfig:
    if config_path and config_path.exists():
        raw = json.loads(config_path.read_text())
    elif get_path("config_file").exists():
        raw = json.loads(get_path("config_file").read_text())
    else:
        raw = DEFAULT_CONFIG
    data = raw.get("agentx_init", raw)
    if "version" not in data:
        data["version"] = "1.0.0"
    return AgentXInitConfig(**data)


def load_config_record(config_path: Optional[Path] = None) -> ConfigRecord:
    if config_path and config_path.exists():
        raw = json.loads(config_path.read_text())
    elif get_path("config_file").exists():
        raw = json.loads(get_path("config_file").read_text())
    else:
        raw = _SPEC_DEFAULT

    if "agentx_init" in raw:
        data = raw["agentx_init"]
        return ConfigRecord(
            config_version=data.get("version", "1.0.0"),
            runtime_root=data.get("state_dir", ".agentx-init"),
        )

    if "schema_version" not in raw:
        return ConfigRecord()

    return ConfigRecord(
        schema_version=raw.get("schema_version", "1.0"),
        config_version=raw.get("config_version", "1.0.0"),
        default_mode=raw.get("default_mode", "read_only"),
        runtime_root=raw.get("runtime_root", ".agentx-init"),
        scan=raw.get("scan", ConfigRecord().scan),
        feature_flags=raw.get("feature_flags", ConfigRecord().feature_flags),
    )


def validate_config(record: ConfigRecord) -> ConfigValidationReport:
    report = ConfigValidationReport()
    if not record.schema_version:
        report.errors.append("Missing schema_version")
    if not record.config_version:
        report.errors.append("Missing config_version")
    if record.default_mode not in ("read_only",):
        report.warnings.append(f"Unexpected default_mode: {record.default_mode}")
    if ".." in str(record.runtime_root):
        report.errors.append("Unsafe runtime_root")
    if report.errors:
        report.status = "INVALID"
    elif report.warnings:
        report.status = "PARTIAL"
    return report
