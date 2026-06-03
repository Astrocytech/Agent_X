from __future__ import annotations
from pathlib import Path
from agentx_evolve.models.model_models import new_id, utc_now_iso
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, PromotionGateDecision, PromotionEvidenceManifest,
    PromotionReviewReport, PromotionCompletionRecord,
    canonical_json, sha256_dict, sha256_file, from_dict, to_dict,
    write_json_atomic, append_jsonl,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


def create_promotion_evidence_manifest(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    evidence_files: list[Path],
    repo_root: Path,
) -> dict:
    manifest_id = new_id("manifest-")
    now = utc_now_iso()
    evidence_list = []
    evidence_hashes = []
    for f in evidence_files:
        rel = str(f.relative_to(repo_root))
        evidence_list.append({"path": rel})
        evidence_hashes.append({"path": rel, "sha256": sha256_file(f)})

    manifest = PromotionEvidenceManifest(
        manifest_id=manifest_id,
        created_at=now,
        component_id=candidate.component_id,
        candidate_id=candidate.candidate_id,
        source_commit=candidate.source_commit,
        decision_id=decision.decision_id,
        gate_decision_hash=decision.gate_decision_hash,
        idempotency_key=decision.idempotency_key,
        runtime_artifact_root=str(promotion_runs_dir(repo_root).relative_to(repo_root)),
        evidence_files=evidence_list,
        evidence_file_hashes=evidence_hashes,
        final_decision=decision.status,
    )
    payload = {k: v for k, v in to_dict(manifest).items() if k != "manifest_hash"}
    manifest.manifest_hash = sha256_dict(payload)
    path = promotion_runs_dir(repo_root) / "promotion_evidence_manifest.json"
    write_json_atomic(path, to_dict(manifest))
    return to_dict(manifest)


def write_promotion_review_report(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path:
    report = PromotionReviewReport(
        review_report_id=new_id("review-report-"),
        created_at=utc_now_iso(),
        component_id=candidate.component_id,
        candidate_id=candidate.candidate_id,
        source_commit=candidate.source_commit,
        decision_id=decision.decision_id,
        reviewed_commit=candidate.source_commit,
        blockers=decision.blocking_failures,
        high_issues=decision.high_issues,
        non_blocking_followups=decision.non_blocking_followups,
        final_verdict=decision.status,
    )
    payload = {k: v for k, v in to_dict(report).items() if k != "review_report_hash"}
    report.review_report_hash = sha256_dict(payload)
    path = promotion_runs_dir(repo_root) / "promotion_review_report.json"
    write_json_atomic(path, to_dict(report))
    return path


def write_promotion_completion_record(
    candidate: ReleaseCandidate,
    decision: PromotionGateDecision,
    repo_root: Path,
) -> Path:
    record = PromotionCompletionRecord(
        completion_record_id=new_id("completion-"),
        created_at=utc_now_iso(),
        component_id=candidate.component_id,
        component_name=candidate.component_name,
        candidate_id=candidate.candidate_id,
        source_commit=candidate.source_commit,
        decision_id=decision.decision_id,
        decision_status=decision.status,
        decision=decision.decision,
        approved_at=utc_now_iso() if decision.decision == "PROMOTE" else "",
        release_scope=candidate.release_scope,
    )
    payload = {k: v for k, v in to_dict(record).items() if k != "completion_record_hash"}
    record.completion_record_hash = sha256_dict(payload)
    path = promotion_runs_dir(repo_root) / "promotion_completion_record.json"
    write_json_atomic(path, to_dict(record))
    return path


def revalidate_promotion_evidence(
    completion_record: PromotionCompletionRecord,
    repo_root: Path,
) -> list[str]:
    errors: list[str] = []
    manifest_path = completion_record.evidence_manifest_path
    if manifest_path:
        full_path = repo_root / manifest_path
        if not full_path.exists():
            errors.append(f"Evidence manifest not found: {manifest_path}")
        else:
            import json
            manifest_data = json.loads(full_path.read_text())
            for entry in manifest_data.get("evidence_file_hashes", []):
                epath = entry.get("path", "")
                ehash = entry.get("sha256", "")
                if not epath or not ehash:
                    errors.append(f"Incomplete hash entry in manifest: {entry}")
                    continue
                full_epath = repo_root / epath
                if not full_epath.exists():
                    errors.append(f"Evidence file missing: {epath}")
                    continue
                actual_hash = sha256_file(full_epath)
                if actual_hash != ehash:
                    errors.append(f"Hash mismatch for {epath}: expected {ehash}, got {actual_hash}")

    report_path = completion_record.review_report_path
    if report_path:
        full_rpath = repo_root / report_path
        if not full_rpath.exists():
            errors.append(f"Review report not found: {report_path}")

    return errors
