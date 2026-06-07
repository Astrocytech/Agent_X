from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from agentx_evolve.monitoring.monitoring_utils import write_json_atomic
from agentx_evolve.models.model_models import utc_now_iso

logger = logging.getLogger(__name__)

RR_SCHEMA_VERSION = "1.0"
RR_SCHEMA_ID = "monitoring_review_report.schema.json"


def write_monitoring_review_report(
    repo_root: Path,
    reviewed_commit: str = "",
    reviewer: str = "automated",
    coverage_statuses: dict | None = None,
    blockers: list[str] | None = None,
    high_issues: list[str] | None = None,
    final_verdict: str = "PENDING",
) -> dict:
    report = {
        "schema_version": RR_SCHEMA_VERSION,
        "schema_id": RR_SCHEMA_ID,
        "component_id": "AGENTX_MONITORING",
        "component_name": "Monitoring Layer",
        "reviewed_commit": reviewed_commit,
        "reviewed_at": utc_now_iso(),
        "reviewer": reviewer,
        "coverage_statuses": coverage_statuses or {},
        "blockers": blockers or [],
        "high_issues": high_issues or [],
        "non_blocking_followups": [],
        "deviation_register": [],
        "final_verdict": final_verdict,
    }
    dest = repo_root / ".agentx-init/monitoring" / "review_report.json"
    write_json_atomic(dest, report)
    return report


def load_monitoring_review_report(repo_root: Path) -> dict | None:
    dest = repo_root / ".agentx-init/monitoring" / "review_report.json"
    if not dest.exists():
        return None
    import json
    return json.loads(dest.read_text())
