from __future__ import annotations

import logging
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    REJECTION_RUNTIME_ARTIFACT,
    SEVERITY_BLOCKER,
    PackageFileRecord,
    PackageRejection,
    is_runtime_artifact,
    new_id,
    utc_now_iso,
)

logger = logging.getLogger(__name__)


def scan_runtime_artifacts(
    files: list[PackageFileRecord],
) -> list[PackageRejection]:
    rejections: list[PackageRejection] = []
    for rec in files:
        if is_runtime_artifact(rec.relative_path):
            rejection = PackageRejection(
                rejection_id=new_id("rej"),
                created_at=utc_now_iso(),
                relative_path=rec.relative_path,
                reason_code=REJECTION_RUNTIME_ARTIFACT,
                reason="Runtime artifact excluded from package",
                severity=SEVERITY_BLOCKER,
                safe_detail=f"Path under runtime artifact root: {rec.relative_path}",
            )
            rejections.append(rejection)
            logger.info("Excluded runtime artifact: %s", rec.relative_path)
    return rejections


def verify_no_runtime_artifacts(files: list[PackageFileRecord]) -> bool:
    for rec in files:
        if is_runtime_artifact(rec.relative_path):
            logger.warning("Runtime artifact found: %s", rec.relative_path)
            return False
    return True


def allowed_paths_only(
    files: list[PackageFileRecord],
    allowed_roots: list[str],
) -> list[PackageRejection]:
    rejections: list[PackageRejection] = []
    for rec in files:
        allowed = False
        for root in allowed_roots:
            norm_root = root.rstrip("/")
            if rec.relative_path == norm_root or rec.relative_path.startswith(norm_root + "/"):
                allowed = True
                break
        if not allowed:
            rejections.append(
                PackageRejection(
                    rejection_id=new_id("rej"),
                    created_at=utc_now_iso(),
                    relative_path=rec.relative_path,
                    reason_code=REJECTION_RUNTIME_ARTIFACT,
                    reason="Path not in allowed roots",
                    severity=SEVERITY_BLOCKER,
                    safe_detail=f"Path outside allowed roots: {rec.relative_path}",
                )
            )
    return rejections
