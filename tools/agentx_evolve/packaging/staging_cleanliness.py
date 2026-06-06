from __future__ import annotations

import os
import shutil
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    StagingCleanlinessReport,
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_FAIL,
    staging_dir,
    dist_dir,
    utc_now_iso,
    new_id,
    to_dict,
    write_json_atomic,
)


def check_staging_cleanliness(
    repo_root: Path,
    expected_staging_id: str | None = None,
) -> StagingCleanlinessReport:
    stage = staging_dir(repo_root)
    dist = dist_dir(repo_root)

    stale_staging_entries: list[str] = []
    stale_dist_entries: list[str] = []
    issues: list[str] = []

    if not stage.exists():
        issues.append("staging directory does not exist (fresh state)")
    else:
        for entry in sorted(stage.iterdir()):
            if expected_staging_id and entry.name == expected_staging_id:
                continue
            rel = str(entry.relative_to(repo_root))
            stale_staging_entries.append(rel)
            issues.append(f"stale staging entry: {entry.name}")

    if dist.exists():
        for entry in sorted(dist.iterdir()):
            rel = str(entry.relative_to(repo_root))
            stale_dist_entries.append(rel)
            issues.append(f"pre-existing dist entry: {entry.name}")

    status = VALIDATION_STATUS_FAIL if (stale_staging_entries or stale_dist_entries) else VALIDATION_STATUS_PASS

    report = StagingCleanlinessReport(
        report_id=new_id("stage_clean"),
        created_at=utc_now_iso(),
        staging_dir=str(stage),
        dist_dir=str(dist),
        expected_staging_id=expected_staging_id or "",
        stale_staging_entries=stale_staging_entries,
        stale_dist_entries=stale_dist_entries,
        issues=issues,
        status=status,
    )

    report_path = stage.parent / "reports" / f"staging_cleanliness_{report.report_id}.json"
    write_json_atomic(report_path, to_dict(report))
    return report


def clean_staging(repo_root: Path) -> None:
    stage = staging_dir(repo_root)
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True, exist_ok=True)


def verify_clean_staging(
    repo_root: Path,
    expected_staging_id: str | None = None,
    auto_clean: bool = True,
) -> StagingCleanlinessReport:
    report = check_staging_cleanliness(repo_root, expected_staging_id)
    if report.status != VALIDATION_STATUS_PASS and auto_clean:
        clean_staging(repo_root)
        report = check_staging_cleanliness(repo_root, expected_staging_id)
        if report.status == VALIDATION_STATUS_PASS:
            report.issues.append("staging was auto-cleaned (not a real issue)")
    return report
