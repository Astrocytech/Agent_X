from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RuntimePaths:
    runtime_root: Path
    config_dir: Path
    logs_dir: Path
    memory_dir: Path
    reports_dir: Path
    cache_dir: Path
    snapshots_dir: Path


@dataclass
class ConfigRecord:
    schema_version: str = "1.0"
    config_version: str = "1.0.0"
    default_mode: str = "read_only"
    runtime_root: str = ".agentx-init"
    scan: dict = field(default_factory=lambda: {
        "include_hidden": False,
        "max_file_size_mb": 5,
        "ignore_dirs": [".git", "__pycache__", ".venv", "node_modules", ".agentx-init"],
    })
    feature_flags: dict = field(default_factory=lambda: {
        "governance_engine_active": False,
        "risk_engine_active": False,
        "planner_active": False,
        "proposal_generator_active": False,
        "validation_runner_active": False,
        "knowledge_graph_active": False,
    })

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "config_version": self.config_version,
            "default_mode": self.default_mode,
            "runtime_root": self.runtime_root,
            "scan": dict(self.scan),
            "feature_flags": dict(self.feature_flags),
        }


@dataclass
class ConfigValidationReport:
    status: str = "VALID"
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    failure_class: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "schema_version": "1.0",
            "report_id": "",
            "timestamp": "",
            "status": self.status,
            "config_ref": "",
            "validated_paths": [],
            "warnings": self.warnings,
            "errors": self.errors,
            "failure_class": self.failure_class,
        }
