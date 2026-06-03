from __future__ import annotations
from pathlib import Path
import os
import json
import time
from agentx_evolve.human_review.review_models import (
    HumanReviewQueue, HumanReviewRequest, HumanReviewAuditEvent,
    new_id, utc_now_iso, sha256_dict, canonical_hash_payload,
    atomic_write_json, append_jsonl, human_review_runs_dir,
    SOURCE_COMPONENT, SCHEMA_VERSION,
)


def load_queue(repo_root: Path) -> HumanReviewQueue:
    path = human_review_runs_dir(repo_root) / "review_queue.json"
    if not path.exists():
        q = HumanReviewQueue(
            queue_id=new_id("q"),
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
        )
        q.queue_hash = sha256_dict(canonical_hash_payload(q.to_dict()))
        atomic_write_json(path, q.to_dict())
        return q
    with open(path) as f:
        data = json.load(f)
    return _queue_from_dict(data)


def _queue_from_dict(data: dict) -> HumanReviewQueue:
    q = HumanReviewQueue(
        queue_id=data.get("queue_id", new_id("q")),
        created_at=data.get("created_at", utc_now_iso()),
        updated_at=data.get("updated_at", utc_now_iso()),
        queue_version=data.get("queue_version", 1),
        queue_hash=data.get("queue_hash"),
        warnings=data.get("warnings", []),
        errors=data.get("errors", []),
        resolved_requests=data.get("resolved_requests", []),
        deferred_requests=data.get("deferred_requests", []),
        clarification_requests=data.get("clarification_requests", []),
    )
    for r in data.get("pending_requests", []):
        req = HumanReviewRequest(
            request_id=r.get("request_id", ""),
            created_at=r.get("created_at", ""),
            source_component=r.get("source_component", SOURCE_COMPONENT),
            requested_by=r.get("requested_by", ""),
            requested_action=r.get("requested_action", ""),
            requested_effect=r.get("requested_effect", ""),
            risk_level=r.get("risk_level", "LOW"),
            reason=r.get("reason", ""),
            status=r.get("status", "PENDING"),
            request_hash=r.get("request_hash"),
            artifact_refs=r.get("artifact_refs", []),
            evidence_refs=r.get("evidence_refs", []),
            warnings=r.get("warnings", []),
            errors=r.get("errors", []),
        )
        q.pending_requests.append(req)
    return q


def save_queue(queue: HumanReviewQueue, repo_root: Path) -> dict:
    path = human_review_runs_dir(repo_root) / "review_queue.json"
    queue.updated_at = utc_now_iso()
    queue.queue_version += 1
    queue.queue_hash = sha256_dict(canonical_hash_payload(queue.to_dict()))
    return atomic_write_json(path, queue.to_dict())


def acquire_queue_lock(repo_root: Path, timeout: float = 5.0) -> bool:
    lock_dir = human_review_runs_dir(repo_root)
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / ".queue.lock"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.05)
    return False


def release_queue_lock(repo_root: Path) -> None:
    lock_path = human_review_runs_dir(repo_root) / ".queue.lock"
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def enqueue_request(request: HumanReviewRequest, repo_root: Path) -> dict:
    queue = load_queue(repo_root)
    queue.pending_requests.append(request)
    append_jsonl(
        human_review_runs_dir(repo_root) / "review_request_history.jsonl",
        request.to_dict(),
    )
    atomic_write_json(
        human_review_runs_dir(repo_root) / "latest_review_request.json",
        request.to_dict(),
    )
    return save_queue(queue, repo_root)


def resolve_request(request_id: str, repo_root: Path) -> dict:
    queue = load_queue(repo_root)
    queue.pending_requests = [r for r in queue.pending_requests if r.request_id != request_id]
    if request_id not in queue.resolved_requests:
        queue.resolved_requests.append(request_id)
    return save_queue(queue, repo_root)
