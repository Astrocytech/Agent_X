import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.human_review import (
    write_audit_event,
    write_evidence_manifest,
    write_integrity_record,
    write_completion_record,
    collect_human_review_evidence_files,
    hash_human_review_evidence,
)


class TestWriteAuditEvent:
    def test_write_audit_event_creates_event_with_correct_type(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            event = write_audit_event(
                event_type="REVIEW_STARTED",
                request_id="r-001",
                status="OK",
                message="Review initiated",
                repo_root=repo_root,
            )
            assert event.audit_id.startswith("aud-")
            assert event.event_type == "REVIEW_STARTED"
            assert event.status == "OK"


class TestWriteEvidenceManifest:
    def test_write_evidence_manifest_creates_manifest_with_files(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            manifest = write_evidence_manifest(repo_root, validated_commit="abc123")
            assert manifest.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"
            manifest_path = repo_root / ".agentx-init" / "human_review" / "human_review_evidence_manifest.json"
            assert manifest_path.exists()


class TestCollectHumanReviewEvidenceFiles:
    def test_collect_human_review_evidence_files_returns_list(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            files = collect_human_review_evidence_files(repo_root)
            assert isinstance(files, list)


class TestHashHumanReviewEvidence:
    def test_hash_human_review_evidence_returns_hash_entries(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            hashes = hash_human_review_evidence(repo_root)
            assert isinstance(hashes, list)


class TestWriteIntegrityRecord:
    def test_write_integrity_record_creates_record_with_hash_chain(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = write_integrity_record(
                prior_record_hash="",
                payload_hash="payload-abc",
                record_type="REQUEST",
                repo_root=repo_root,
            )
            assert record["record_id"].startswith("int-")
            assert record["record_hash"] != ""
            assert record["prior_record_hash"] == ""
            assert record["payload_hash"] == "payload-abc"
            assert record["record_type"] == "REQUEST"

    def test_write_integrity_record_chains_correctly(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            r1 = write_integrity_record(
                prior_record_hash="",
                payload_hash="first",
                record_type="REQUEST",
                repo_root=repo_root,
            )
            r2 = write_integrity_record(
                prior_record_hash=r1["record_hash"],
                payload_hash="second",
                record_type="DECISION",
                repo_root=repo_root,
            )
            assert r2["prior_record_hash"] == r1["record_hash"]


class TestWriteCompletionRecord:
    def test_write_completion_record_creates_record_with_sha256(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            record = write_completion_record(
                repo_root=repo_root,
                validated_commit="abc123",
                final_decision="DONE",
                files_created=["test_file.py"],
                schemas_created=["test.schema.json"],
                tests_created=["test_test.py"],
            )
            assert record.component_id == "AGENTX_HUMAN_REVIEW_APPROVAL"
            assert record.status == "DONE"
            assert record.final_decision == "DONE"
            assert record.completion_record_sha256 != ""
            assert "test_file.py" in record.files_created_or_changed
