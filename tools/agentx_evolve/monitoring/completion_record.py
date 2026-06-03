from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_utils import write_json_atomic
from agentx_evolve.models.model_models import utc_now_iso

logger = logging.getLogger(__name__)

CR_SCHEMA_VERSION = "1.0"
CR_SCHEMA_ID = "monitoring_completion_record.schema.json"


def write_monitoring_completion_record(
    repo_root: Path,
    status: str = "DONE",
    validated_commit: str = "",
    commands_run: list[dict] | None = None,
    files_created: list[str] | None = None,
    schemas_created: list[str] | None = None,
    tests_created: list[str] | None = None,
) -> dict:
    record = {
        "schema_version": CR_SCHEMA_VERSION,
        "schema_id": CR_SCHEMA_ID,
        "component_id": "AGENTX_MONITORING",
        "component_name": "Monitoring Layer",
        "status": status,
        "validated_commit": validated_commit,
        "validated_at": utc_now_iso(),
        "canonical_subdirectory": "tools/agentx_evolve/monitoring/",
        "runtime_artifact_root": ".agentx-init/monitoring/",
        "commands_run": commands_run or [],
        "files_created_or_changed": files_created or [],
        "schemas_created_or_changed": schemas_created or [],
        "tests_created_or_changed": tests_created or [],
        "final_decision": status,
    }
    dest = repo_root / ".agentx-init/monitoring" / "completion_record.json"
    write_json_atomic(dest, record)
    return record


def load_monitoring_completion_record(repo_root: Path) -> dict | None:
    dest = repo_root / ".agentx-init/monitoring" / "completion_record.json"
    if not dest.exists():
        return None
    import json
    return json.loads(dest.read_text())
