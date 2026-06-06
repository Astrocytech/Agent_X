from __future__ import annotations
from pathlib import Path
from agentx_evolve.packaging.packaging_models import (
    LicenseNoticeReport,
    PackageInventory,
    PackageManifest,
    VALIDATION_STATUS_BLOCKED,
    VALIDATION_STATUS_PASS,
    new_id,
    utc_now_iso,
)


def validate_license_notice_files(
    repo_root: Path,
    manifest: PackageManifest,
    inventory: PackageInventory,
) -> LicenseNoticeReport:
    required_names = ["README.md", "LICENSE", "NOTICE"]
    found_names: set[str] = set()
    for record in inventory.files:
        name = Path(record.relative_path).name
        if name in required_names:
            found_names.add(name)

    required = [r for r in required_names if r in manifest.required_files]
    if not required:
        required = required_names

    missing = [r for r in required if r not in found_names]

    notice_files = []
    for record in inventory.files:
        name = Path(record.relative_path).name
        if "notice" in name.lower() or "license" in name.lower():
            if record.relative_path not in notice_files:
                notice_files.append(record.relative_path)

    found_list = sorted(
        record.relative_path
        for record in inventory.files
        if Path(record.relative_path).name in required
    )

    report = LicenseNoticeReport(
        report_id=new_id("lnr"),
        created_at=utc_now_iso(),
        required_license_files=required,
        found_license_files=found_list,
        missing_license_files=missing,
        notice_files=notice_files,
        status=VALIDATION_STATUS_PASS,
    )

    if missing:
        report.status = VALIDATION_STATUS_BLOCKED

    return report
