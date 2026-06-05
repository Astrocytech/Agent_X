from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewAuditEvent, HumanReviewEvidenceManifest,
    HumanReviewCompletionRecord,
    new_id, utc_now_iso, sha256_file, sha256_dict,
    atomic_write_json, append_jsonl, human_review_runs_dir,
    SOURCE_COMPONENT,
)


def write_audit_event(
    event_type: str,
    request_id: str | None = None,
    decision_id: str | None = None,
    status: str = "",
    message: str = "",
    repo_root: Path | None = None,
) -> HumanReviewAuditEvent:
    event = HumanReviewAuditEvent(
        audit_id=new_id("aud"),
        timestamp=utc_now_iso(),
        event_type=event_type,
        request_id=request_id,
        decision_id=decision_id,
        status=status,
        message=message,
    )
    if repo_root:
        append_jsonl(human_review_runs_dir(repo_root) / "human_review_audit.jsonl", event.to_dict())
    return event


def write_evidence_manifest(
    repo_root: Path,
    validated_commit: str | None = None,
    commands: list[dict] | None = None,
) -> HumanReviewEvidenceManifest:
    manifest = HumanReviewEvidenceManifest(
        validated_commit=validated_commit,
        created_at=utc_now_iso(),
        commands=commands or [],
    )
    evidence_dir = human_review_runs_dir(repo_root)
    if evidence_dir.exists():
        for f in sorted(evidence_dir.iterdir()):
            if f.is_file() and f.suffix in (".json", ".jsonl"):
                manifest.evidence_files.append({"path": str(f.relative_to(repo_root))})
                manifest.evidence_file_hashes.append({"path": str(f.relative_to(repo_root)), "sha256": sha256_file(f)})
    path = evidence_dir / "human_review_evidence_manifest.json"
    atomic_write_json(path, manifest.to_dict())
    return manifest


def write_review_report(
    repo_root: Path,
    reviewed_commit: str = "",
    reviewer: str = "",
    coverage_statuses: dict | None = None,
) -> dict:
    report = {
        "schema_version": "1.0",
        "schema_id": "human_review_review_report.schema.json",
        "component_id": "AGENTX_HUMAN_REVIEW_APPROVAL",
        "reviewed_commit": reviewed_commit,
        "reviewed_at": utc_now_iso(),
        "reviewer": reviewer,
        "coverage_statuses": coverage_statuses or {},
        "blockers": [],
        "high_issues": [],
        "non_blocking_followups": [],
        "deviation_register": [],
        "final_verdict": "DONE",
    }
    path = human_review_runs_dir(repo_root) / "human_review_review_report.json"
    atomic_write_json(path, report)
    return report


def write_completion_record(
    repo_root: Path,
    validated_commit: str = "",
    final_decision: str = "",
    files_created: list[str] | None = None,
    schemas_created: list[str] | None = None,
    tests_created: list[str] | None = None,
) -> HumanReviewCompletionRecord:
    record = HumanReviewCompletionRecord(
        status=final_decision or "DONE",
        validated_commit=validated_commit,
        validated_at=utc_now_iso(),
        files_created_or_changed=files_created or [],
        schemas_created_or_changed=schemas_created or [],
        tests_created_or_changed=tests_created or [],
        final_decision=final_decision or "DONE",
    )
    path = human_review_runs_dir(repo_root) / "human_review_completion_record.json"
    atomic_write_json(path, record.to_dict())
    record.completion_record_sha256 = sha256_file(path)
    atomic_write_json(path, record.to_dict())
    return record


def write_integrity_record(
    prior_record_hash: str,
    payload_hash: str,
    record_type: str,
    repo_root: Path,
) -> dict:
    record = {
        "record_id": new_id("int"),
        "prior_record_hash": prior_record_hash,
        "payload_hash": payload_hash,
        "record_hash": "",
        "timestamp": utc_now_iso(),
        "record_type": record_type,
    }
    payload = {k: v for k, v in record.items() if k != "record_hash"}
    import json, hashlib
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    record["record_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    append_jsonl(human_review_runs_dir(repo_root) / "record_integrity_chain.jsonl", record)
    return record
