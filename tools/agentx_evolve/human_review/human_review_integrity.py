from __future__ import annotations
from pathlib import Path
from agentx_evolve.human_review.review_models import (
    HumanReviewValidationResult,
    new_id, utc_now_iso, sha256_dict, append_jsonl, human_review_runs_dir,
    VALIDATION_VALID, VALIDATION_STALE, VALIDATION_FORGED_OR_UNTRUSTED,
)
import json


def compute_record_chain_hash(
    previous_hash: str | None,
    event_payload: dict,
) -> str:
    payload = dict(event_payload)
    payload.pop("record_hash", None)
    payload["prior_record_hash"] = previous_hash if previous_hash is not None else ""
    return sha256_dict(payload)


def append_integrity_record(
    event_type: str,
    artifact_path: str,
    artifact_sha256: str,
    repo_root: Path,
) -> dict:
    runs_dir = human_review_runs_dir(repo_root)
    chain_path = runs_dir / "record_integrity_chain.jsonl"
    queue_path = runs_dir / "review_queue.json"

    prior_hash = ""
    if chain_path.exists():
        with open(chain_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line)
                    prior_hash = last.get("record_hash", "")

    event_payload = {
        "event_id": new_id("int"),
        "event_type": event_type,
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_sha256,
        "timestamp": utc_now_iso(),
    }

    record_hash = compute_record_chain_hash(prior_hash if prior_hash else None, event_payload)

    record = {
        **event_payload,
        "prior_record_hash": prior_hash,
        "record_hash": record_hash,
    }

    append_jsonl(chain_path, record)

    if queue_path.exists():
        with open(queue_path) as qf:
            queue = json.load(qf)
        integrity_records = queue.setdefault("integrity_records", [])
        integrity_records.append(record)
        with open(queue_path, "w") as qf:
            json.dump(queue, qf, indent=2, sort_keys=True)

    return record


def verify_human_review_integrity_chain(repo_root: Path) -> HumanReviewValidationResult:
    chain_path = human_review_runs_dir(repo_root) / "record_integrity_chain.jsonl"

    if not chain_path.exists():
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            status=VALIDATION_STALE,
            reason="Integrity chain file not found",
            allowed=False,
        )

    records = []
    with open(chain_path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    if not records:
        return HumanReviewValidationResult(
            validation_id=new_id("val"),
            validated_at=utc_now_iso(),
            status=VALIDATION_STALE,
            reason="Integrity chain is empty",
            allowed=False,
        )

    expected_prior = ""
    for i, record in enumerate(records):
        stored_prior = record.get("prior_record_hash", "")
        if stored_prior != expected_prior:
            return HumanReviewValidationResult(
                validation_id=new_id("val"),
                validated_at=utc_now_iso(),
                status=VALIDATION_FORGED_OR_UNTRUSTED,
                reason=f"Chain broken at record {i}: prior_record_hash mismatch",
                allowed=False,
            )
        record_copy = dict(record)
        record_copy.pop("record_hash", None)
        computed = sha256_dict(record_copy)
        if computed != record.get("record_hash", ""):
            return HumanReviewValidationResult(
                validation_id=new_id("val"),
                validated_at=utc_now_iso(),
                status=VALIDATION_FORGED_OR_UNTRUSTED,
                reason=f"Chain broken at record {i}: record_hash mismatch",
                allowed=False,
            )
        expected_prior = record.get("record_hash", "")

    return HumanReviewValidationResult(
        validation_id=new_id("val"),
        validated_at=utc_now_iso(),
        status=VALIDATION_VALID,
        matched_scope=True,
        allowed=True,
    )
