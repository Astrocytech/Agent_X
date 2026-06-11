"""Validate gap discovery report completeness."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.validators.common import parse_report_dir

REPORT_DIR = parse_report_dir()
STATUS_OK = 0
STATUS_FAIL = 1


def load_json(path: str) -> dict | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def validate_gap_discovery() -> list[str]:
    errors = []

    gap_json = REPORT_DIR / "functional_runtime_mvp_gap_discovery_report.json"
    gap_md = REPORT_DIR / "functional_runtime_mvp_gap_discovery_report.md"

    if not gap_json.exists():
        errors.append("Gap discovery report (JSON) missing")
    if not gap_md.exists():
        errors.append("Gap discovery report (MD) missing")

    gap = load_json(str(gap_json))
    if not gap or not isinstance(gap, dict):
        errors.append("Gap discovery report does not parse")
        return errors

    # Search scope
    search_scope = gap.get("search_scope", [])
    if not search_scope:
        errors.append("Search scope missing — no source paths were scanned")
    else:
        required_scope = {"Makefile", "docs/", "tools/agentx_evolve/", "tests/"}
        missing_scope = required_scope - set(search_scope)
        if missing_scope:
            errors.append(f"Search scope missing required paths: {missing_scope}")

    # Search patterns
    search_patterns = gap.get("search_patterns", [])
    if not search_patterns:
        errors.append("Search patterns missing")

    # Source files inspected
    source_files = gap.get("source_files_inspected", [])
    if not source_files:
        errors.append("No source files inspected")

    # Documents inspected
    documents = gap.get("documents_inspected", [])
    if not documents:
        errors.append("No documents inspected")

    # Matches
    matches = gap.get("matches", {})
    if not matches:
        errors.append("No matches found — search may have failed")

    # Known gaps
    if not gap.get("known_gaps_confirmed"):
        errors.append("No known gaps confirmed in report")

    # Classification context for finding validation
    pre_class = gap.get("final_pre_implementation_classification", "")
    post_class = gap.get("final_post_implementation_classification", "")
    if not pre_class:
        errors.append("Final pre-implementation classification missing")
    if not post_class:
        errors.append("Final post-implementation classification missing")

    # Findings — every finding must have evidence and classification
    findings = gap.get("findings", [])
    if not findings:
        errors.append("No findings — gap discovery must produce scan-derived findings")
    for f in findings:
        if isinstance(f, dict):
            f_class = f.get("classification", "")
            if not f_class:
                errors.append(f"Finding {f.get('finding_id', '?')} missing classification")
            # MVP_BLOCKER / NEEDS_REVIEW is only rejectable when FUNCTIONAL_RUNTIME_MVP is claimed
            if f_class in ("MVP_BLOCKER", "NEEDS_REVIEW") and post_class == "FUNCTIONAL_RUNTIME_MVP":
                errors.append(
                    f"Finding {f.get('finding_id', '?')} ({f.get('pattern', '')}) "
                    f"is {f_class} — unacceptable for {post_class}"
                )
            if not f.get("evidence_refs"):
                errors.append(f"Finding {f.get('finding_id', '?')} lacks evidence_refs")
            if f_class == "FIXED" and not f.get("closure_evidence"):
                errors.append(f"Finding {f.get('finding_id', '?')} is FIXED but lacks closure_evidence")

    # New gaps
    new_gaps = gap.get("new_gaps_discovered", [])
    if not new_gaps:
        errors.append("No new gaps discovered in report")

    for ng in new_gaps:
        if isinstance(ng, dict):
            resolution = ng.get("resolution", "")
            if not resolution:
                errors.append(f"New gap {ng.get('id', '?')} lacks resolution")

    # Suspected gaps
    for sg in gap.get("suspected_gaps", []):
        if isinstance(sg, dict):
            status = sg.get("status", "")
            if status == "CLOSED" and not sg.get("evidence_ref"):
                errors.append(f"Suspected gap {sg.get('id', '?')} is CLOSED but lacks evidence_ref")

    # Out of scope items must have rationale
    out_of_scope = gap.get("out_of_scope", [])
    if not out_of_scope:
        errors.append("No out-of-scope items listed")

    # Classification consistency check
    has_blocker_or_review = any(
        f.get("classification") in ("MVP_BLOCKER", "NEEDS_REVIEW")
        for f in findings if isinstance(f, dict)
    )
    if has_blocker_or_review and post_class == "FUNCTIONAL_RUNTIME_MVP":
        errors.append(
            "final_post_implementation_classification is FUNCTIONAL_RUNTIME_MVP "
            "but findings include MVP_BLOCKER or NEEDS_REVIEW"
        )

    return errors


def main() -> int:
    errs = validate_gap_discovery()
    if errs:
        print("VALIDATE GAP DISCOVERY FAILED:")
        for e in errs:
            print(f"  - {e}")
        return STATUS_FAIL
    print("validate-functional-runtime-mvp-gap-discovery: PASS")
    return STATUS_OK


if __name__ == "__main__":
    sys.exit(main())
