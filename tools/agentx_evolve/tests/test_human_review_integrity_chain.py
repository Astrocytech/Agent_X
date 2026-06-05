import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    append_integrity_record,
    verify_human_review_integrity_chain,
    compute_record_chain_hash,
    VALIDATION_STALE,
    VALIDATION_VALID,
)


class TestHumanReviewIntegrityChain:
    def test_append_integrity_record_creates_record(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = append_integrity_record(
                event_type="REQUEST",
                artifact_path=".agentx-init/human_review/review_request_history.jsonl",
                artifact_sha256="abc123",
                repo_root=repo_root,
            )
            assert record["event_id"].startswith("int-")
            assert record["event_type"] == "REQUEST"
            assert record["artifact_sha256"] == "abc123"
            assert record["record_hash"] != ""

    def test_verify_human_review_integrity_chain_valid_for_empty(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            result = verify_human_review_integrity_chain(repo_root)
            assert result.status == VALIDATION_STALE
            assert result.allowed is False

    def test_compute_record_chain_hash_is_deterministic(self):
        payload = {"event_id": "int-001", "event_type": "REQUEST", "data": "test"}
        h1 = compute_record_chain_hash(None, payload)
        h2 = compute_record_chain_hash(None, payload)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64

    def test_append_integrity_record_links_to_prior_hash(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            r1 = append_integrity_record(
                event_type="REQUEST",
                artifact_path="req.jsonl",
                artifact_sha256="aaa",
                repo_root=repo_root,
            )
            r2 = append_integrity_record(
                event_type="DECISION",
                artifact_path="dec.jsonl",
                artifact_sha256="bbb",
                repo_root=repo_root,
            )
            assert r1["prior_record_hash"] == ""
            assert r2["prior_record_hash"] == r1["record_hash"]
