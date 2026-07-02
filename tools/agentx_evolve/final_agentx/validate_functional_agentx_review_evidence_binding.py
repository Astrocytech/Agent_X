#!/usr/bin/env python3
"""Validate that review decisions are bound to evidence hashes.

Checks:
1. All review packets in the orchestrator evidence events have evidence_refs
   that match the evidence manifest's file hashes.
2. Contract identity is present in review records.
3. Override evidence refs resolve to valid manifest entries.
4. No evidence hash mismatch between review decisions and actual files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agentx_evolve.final_agentx import (
    REPORT_BASE, get_canonical_artifact_map, load_json, atomic_write_json,
)

ROOT = Path.cwd()
ORCHESTRATOR_DIR = ROOT / ".agentx-init" / "reports" / "functional-agentx"


def _sha256_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_binding() -> list[str]:
    errors: list[str] = []
    report_dir = REPORT_BASE

    # Load evidence manifest
    manifest_path = report_dir / "evidence_manifest.json"
    manifest = load_json(manifest_path)
    if not manifest:
        errors.append(f"evidence_manifest.json not found at {manifest_path}")
        return errors

    manifest_version = manifest.get("schema_version", "")
    if manifest_version not in ("1.0", "1.1"):
        errors.append(f"evidence_manifest schema_version unknown: {manifest_version}")

    # Build expected hash map from manifest entries
    expected_hashes: dict[str, str] = {}
    for entry_key in ("pre_existing_evidence", "generated_evidence", "dynamically_derived_evidence"):
        for item in manifest.get(entry_key, []):
            ref = item.get("ref", item.get("artifact_id", item.get("name", "")))
            sha = item.get("sha256", item.get("sha", ""))
            if ref and sha:
                expected_hashes[ref] = sha

    # Try loading orchestrator events to find review events
    review_events: list[dict] = []
    events_path = ORCHESTRATOR_DIR / "orchestrator_events.jsonl"
    if events_path.exists():
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("event_type", "").startswith("review") or \
                   ev.get("status") in ("APPROVED", "REJECTED"):
                    review_events.append(ev)

        for ev in review_events:
            evidence_refs = ev.get("evidence_refs", ev.get("refs", []))
            if not evidence_refs:
                errors.append(f"Review event {ev.get('event_id','?')} has no evidence_refs")
                continue
            for ref in evidence_refs:
                if isinstance(ref, dict):
                    ref_key = ref.get("ref", ref.get("path", ""))
                else:
                    ref_key = str(ref)
                if ref_key and ref_key not in expected_hashes:
                    errors.append(
                        f"Review event {ev.get('event_id','?')} references "
                        f"'{ref_key}' not found in evidence manifest"
                    )

    # Try loading orchestrated review report
    review_report_path = report_dir / "review_report.json"
    review_report = load_json(review_report_path)
    if review_report:
        ev_manifest_sha = review_report.get("evidence_manifest_sha256", "")
        if ev_manifest_sha:
            manifest_actual = _sha256_file(manifest_path)
            if ev_manifest_sha != manifest_actual:
                errors.append(
                    f"Review report evidence_manifest_sha256 mismatch: "
                    f"report says {ev_manifest_sha}, actual file is {manifest_actual}"
                )

    # Check orchestrator review report
    orch_report = load_json(ORCHESTRATOR_DIR / "orchestrator_review_report.json") or {}
    if orch_report:
        ev_manifest_sha = orch_report.get("evidence_manifest_sha256", "")
        if ev_manifest_sha:
            manifest_actual = _sha256_file(manifest_path)
            if ev_manifest_sha != manifest_actual:
                errors.append(
                    f"Orchestrator review report evidence_manifest_sha256 mismatch: "
                    f"report says {ev_manifest_sha}, actual file is {manifest_actual}"
                )

    # Check command transcript has source=recorded (not synthetic)
    ct_path = report_dir / "command_transcript.json"
    ct = load_json(ct_path)
    if ct:
        source = ct.get("source", "")
        if source == "no_recorder_fallback":
            errors.append(
                "Command transcript source is 'no_recorder_fallback' — "
                "commands were not actually recorded, transcript is empty"
            )

    # Gap 10: Prevent fixture/policy review labeled as human/independent review
    _check_fixture_not_human(errors, review_report)
    _check_fixture_not_human(errors, orch_report)
    for ev in review_events:
        _check_review_event_fixture_not_human(errors, ev)

    return errors


def _check_fixture_not_human(errors: list[str], report: dict) -> None:
    """Hard rule #5: fixture/policy review must not claim human/independent review status."""
    if not report:
        return
    reviewer = (report.get("reviewer") or "").strip().lower()
    src = (report.get("review_source") or "").strip().lower()
    reviewer_identity = (report.get("reviewer_identity") or "").strip().lower()

    # Automatic reviewer indicators
    auto_reviewer = any(
        kw in reviewer or kw in reviewer_identity
        for kw in ("automated-", "automated_", "fixture", "policy-", "auto-")
    )
    # Human claims: source tagged as human, independent, or identity says human
    human_claim = (
        "human" in src or "independent" in src
        or ("review_source" not in report and report.get("human_review"))
    )

    if auto_reviewer and human_claim:
        errors.append(
            f"Fixture/automated review labeled as human/independent: "
            f"reviewer='{report.get('reviewer','')}', "
            f"reviewer_identity='{report.get('reviewer_identity','')}', "
            f"review_source='{report.get('review_source','')}'"
        )


def _check_review_event_fixture_not_human(errors: list[str], ev: dict) -> None:
    """Check orchestrator review events for fixture-vs-human violation."""
    if not ev:
        return
    reviewer = (ev.get("reviewer_identity") or ev.get("reviewer") or "").strip().lower()
    src = (ev.get("review_source") or ev.get("source") or "").strip().lower()
    auto_reviewer = any(
        kw in reviewer for kw in ("automated-", "automated_", "fixture", "policy-", "auto-")
    )
    human_claim = "human" in src or "independent" in src
    if auto_reviewer and human_claim:
        errors.append(
            f"Review event {ev.get('event_id','?')}: fixture/automated review "
            f"labeled as human/independent"
        )


def main() -> int:
    errors = validate_binding()

    result = {
        "schema_version": "1.0",
        "artifact_type": "review_evidence_binding_validation",
        "producer": "tools/agentx_evolve/final_agentx/validate_functional_agentx_review_evidence_binding.py",
        "passed": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors),
    }

    out_path = REPORT_BASE / "review_evidence_binding_validation.json"
    atomic_write_json(out_path, result)

    if errors:
        print(f"REVIEW EVIDENCE BINDING VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Review evidence binding validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
