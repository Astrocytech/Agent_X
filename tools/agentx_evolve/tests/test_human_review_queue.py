import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    HumanReviewRequest,
    load_queue,
    enqueue_request,
    resolve_request,
    REQ_PENDING,
    RISK_LEVEL_LOW,
)


class TestHumanReviewQueue:
    def test_load_queue_creates_new_queue_if_missing(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            queue = load_queue(repo_root)
            assert queue.queue_id.startswith("q-")
            assert len(queue.pending_requests) == 0
            assert len(queue.resolved_requests) == 0

    def test_enqueue_request_adds_to_pending(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            req = HumanReviewRequest(
                request_id="q-enq-001",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=RISK_LEVEL_LOW,
                reason="queue enqueue test",
                status=REQ_PENDING,
            )
            enqueue_request(req, repo_root)
            queue = load_queue(repo_root)
            ids = [r.request_id for r in queue.pending_requests]
            assert "q-enq-001" in ids

    def test_enqueue_multiple_requests(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            for i in range(3):
                req = HumanReviewRequest(
                    request_id=f"q-multi-{i:03d}",
                    requested_by="user-1",
                    requested_action="apply_patch",
                    requested_effect="modify",
                    risk_level=RISK_LEVEL_LOW,
                    reason=f"request {i}",
                    status=REQ_PENDING,
                )
                enqueue_request(req, repo_root)
            queue = load_queue(repo_root)
            ids = [r.request_id for r in queue.pending_requests]
            for i in range(3):
                assert f"q-multi-{i:03d}" in ids
            assert len(ids) >= 3

    def test_resolve_request_moves_from_pending_to_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            req = HumanReviewRequest(
                request_id="q-res-001",
                requested_by="user-1",
                requested_action="apply_patch",
                requested_effect="modify",
                risk_level=RISK_LEVEL_LOW,
                reason="queue resolve test",
                status=REQ_PENDING,
            )
            enqueue_request(req, repo_root)
            resolve_request("q-res-001", repo_root)
            queue = load_queue(repo_root)
            ids = [r.request_id for r in queue.pending_requests]
            assert "q-res-001" not in ids
            assert "q-res-001" in queue.resolved_requests

    def test_resolve_nonexistent_request_does_not_error(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            resolve_request("nonexistent-req", repo_root)
            queue = load_queue(repo_root)
            assert "nonexistent-req" in queue.resolved_requests
