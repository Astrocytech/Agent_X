from __future__ import annotations

import logging
from pathlib import Path

from agentx_evolve.packaging.packaging_models import (
    REJECTION_SECRET,
    SEVERITY_BLOCKER,
    PackageFileRecord,
    PackageRejection,
    has_secret_like_content,
    is_secret_file,
    new_id,
    utc_now_iso,
)

logger = logging.getLogger(__name__)


def scan_secrets_in_files(
    files: list[PackageFileRecord],
    repo_root: Path,
) -> list[PackageRejection]:
    rejections: list[PackageRejection] = []
    for rec in files:
        if is_secret_file(rec.relative_path):
            rejections.append(_make_secret_rejection(rec, "Filename matches secret pattern"))
            continue
        abs_path = Path(rec.absolute_path) if rec.absolute_path else repo_root / rec.relative_path
        if abs_path.is_file():
            try:
                text = abs_path.read_text(errors="replace")
                if has_secret_like_content(text):
                    rejections.append(_make_secret_rejection(rec, "Content matches secret detection patterns"))
            except (OSError, UnicodeDecodeError, PermissionError):
                pass
    return rejections


def verify_no_secrets(
    files: list[PackageFileRecord],
    repo_root: Path,
) -> bool:
    rejections = scan_secrets_in_files(files, repo_root)
    if rejections:
        logger.warning("Secret exclusion found %d issue(s)", len(rejections))
        return False
    return True


def _make_secret_rejection(rec: PackageFileRecord, reason_detail: str) -> PackageRejection:
    return PackageRejection(
        rejection_id=new_id("rej"),
        created_at=utc_now_iso(),
        relative_path=rec.relative_path,
        reason_code=REJECTION_SECRET,
        reason="Secret-like content excluded from package",
        severity=SEVERITY_BLOCKER,
        safe_detail=reason_detail,
    )
