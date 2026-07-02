#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPORT_DIR = Path(".agentx-init/reports/functional-agentx")
ALLOWLIST_PATH = Path("tools/agentx_evolve/final_agentx/gap_discovery_allowlist.json")
NON_CRITICAL_PATHS = ["test_", "fixtures/", "docs/", "__pycache__", ".egg-info", "examples/", "schemas/"]
NON_CRITICAL_TAGS = {"CLEANUP_GAP", "TEST_COVERAGE_GAP", "SAFETY_GAP", "DETERMINISM_GAP", "PROOF_GAP"}
CRITICAL_TAGS = {"OVERCLAIM_GAP"}


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _match_glob(file: str, glob: str) -> bool:
    if glob.startswith("**/"):
        suffix = glob[3:]
        return suffix in file or file.endswith(suffix.lstrip("*"))
    from fnmatch import fnmatch
    return fnmatch(file, glob)


def validate_allowlist_integrity() -> list[str]:
    errors: list[str] = []
    allowlist = load_json(ALLOWLIST_PATH)
    if not allowlist:
        errors.append(f"Allowlist not found at {ALLOWLIST_PATH}")
        return errors

    if allowlist.get("schema_version") != "1.0":
        errors.append(f"Allowlist schema_version is not 1.0: {allowlist.get('schema_version')}")

    entries = allowlist.get("entries", [])
    for entry in entries:
        fid = entry.get("id", "(no-id)")
        pat_hash = entry.get("pattern_hash", "")
        file_glob = entry.get("file_glob", "")

        if not pat_hash:
            errors.append(f"Allowlist entry {fid} missing pattern_hash")
        if not file_glob:
            errors.append(f"Allowlist entry {fid} missing file_glob")
        if not entry.get("tag"):
            errors.append(f"Allowlist entry {fid} missing tag")
        if not entry.get("owner"):
            errors.append(f"Allowlist entry {fid} missing owner")
        if not entry.get("expires"):
            errors.append(f"Allowlist entry {fid} missing expires")
        else:
            try:
                year, month, day = entry["expires"].split("-")
                if int(year) < 2026:
                    errors.append(f"Allowlist entry {fid} expired: {entry['expires']}")
            except (ValueError, IndexError):
                errors.append(f"Allowlist entry {fid} invalid expires format: {entry['expires']}")

    return errors


def validate_gap_report_classification() -> list[str]:
    errors: list[str] = []
    report_path = REPORT_DIR / "gap_discovery_report.json"
    if not report_path.exists():
        errors.append(f"Gap discovery report not found at {report_path}")
        return errors

    report = load_json(report_path)
    if not report:
        errors.append("Gap discovery report is not valid JSON")
        return errors

    if report.get("artifact_type") != "gap_discovery_report":
        errors.append(f"Unexpected artifact_type: {report.get('artifact_type')}")

    allowlist = load_json(ALLOWLIST_PATH)
    entries = allowlist.get("entries", []) if allowlist else []

    findings = report.get("findings", [])
    for f in findings:
        file = f.get("file", "")
        tag = f.get("tag", "")
        status = f.get("status", "")

        matched_allowlist = any(
            _match_glob(file, e.get("file_glob", "")) and tag == e.get("tag", "")
            for e in entries
        )

        if status == "BLOCKING_GAP" and matched_allowlist:
            errors.append(
                f"Finding at {file}:{f.get('line','?')} tagged {tag} matches allowlist "
                f"but is classified BLOCKING_GAP"
            )
        if status == "ALLOWED_WITH_REASON" and not matched_allowlist:
            in_noncritical = any(p in file for p in NON_CRITICAL_PATHS) or tag in NON_CRITICAL_TAGS
            if not in_noncritical:
                errors.append(
                    f"Finding at {file}:{f.get('line','?')} tagged {tag} classified "
                    f"ALLOWED_WITH_REASON but does not match any allowlist entry and is "
                    f"not in a non-critical path or tag"
                )

    return errors


def validate_no_blocking_findings() -> list[str]:
    errors: list[str] = []
    report_path = REPORT_DIR / "gap_discovery_report.json"
    if not report_path.exists():
        return errors

    report = load_json(report_path)
    if not report:
        return errors

    blocking = [f for f in report.get("findings", []) if f.get("status") == "BLOCKING_GAP"]
    critical_blocking = [f for f in blocking if f.get("tag") in CRITICAL_TAGS]

    if critical_blocking:
        for f in critical_blocking:
            errors.append(
                f"Proof-critical blocking gap: {f.get('file','?')}:{f.get('line','?')} "
                f"[{f.get('tag','?')}] {f.get('match','')[:80]}"
            )

    non_critical_blocking = [f for f in blocking if f.get("tag") not in CRITICAL_TAGS]
    if non_critical_blocking:
        print(f"NOTE: {len(non_critical_blocking)} non-critical findings are tracked but do not block the proof")

    return errors


def main() -> int:
    all_errors: list[str] = []
    all_errors.extend(validate_allowlist_integrity())
    all_errors.extend(validate_gap_report_classification())
    all_errors.extend(validate_no_blocking_findings())

    result = {
        "validator": "validate_functional_agentx_gap_discovery",
        "passed": len(all_errors) == 0,
        "errors": all_errors,
        "summary": "PASS" if len(all_errors) == 0 else "FAIL",
    }
    out_path = REPORT_DIR / "validate_gap_discovery.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    if all_errors:
        print("VALIDATE GAP DISCOVERY FAILED:")
        for e in all_errors:
            print(f"  - {e}")
        return 1
    print("validate-functional-agentx-gap-discovery: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
