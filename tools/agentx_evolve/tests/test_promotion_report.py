import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.promotion.promotion_report import (
    create_promotion_evidence_manifest, write_promotion_review_report,
    write_promotion_completion_record, revalidate_promotion_evidence,
)
from agentx_evolve.promotion.promotion_models import (
    ReleaseCandidate, PromotionGateDecision,
    PC_BLOCKED, PC_APPROVED,
)
from agentx_evolve.promotion.release_candidate import promotion_runs_dir


class TestCreateEvidenceManifest:
    def test_create_evidence_manifest_builds_valid_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            decision = PromotionGateDecision(
                decision_id="gd-001",
                gate_decision_hash="b" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
                status=PC_APPROVED,
            )
            evidence_files = []
            manifest = create_promotion_evidence_manifest(candidate, decision, evidence_files, repo_root)
            assert manifest["manifest_id"].startswith("manifest-")
            assert manifest["candidate_id"] == "rc-001"
            assert manifest["source_commit"] == "abc123"
            assert manifest["final_decision"] == PC_APPROVED


class TestWriteReviewReportCreatesFile:
    def test_write_review_report_creates_file(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            decision = PromotionGateDecision(
                decision_id="gd-001",
                gate_decision_hash="b" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
                status="APPROVED",
                decision="PROMOTE",
            )
            path = write_promotion_review_report(candidate, decision, repo_root)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["candidate_id"] == "rc-001"
            assert data["final_verdict"] == "APPROVED"


class TestWriteCompletionRecordOnlyWhenApproved:
    def test_write_completion_record_only_when_approved(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            candidate = ReleaseCandidate(
                candidate_id="rc-001",
                candidate_hash="a" * 64,
                source_commit="abc123",
                component_id="comp-1",
                component_name="test",
                roadmap_layer="layer-1",
                schema_id="promotion_release_candidate.schema.json",
            )
            decision = PromotionGateDecision(
                decision_id="gd-001",
                gate_decision_hash="b" * 64,
                idempotency_key="ik-001",
                component_id="comp-1",
                candidate_id="rc-001",
                source_commit="abc123",
                status=PC_BLOCKED,
                decision="BLOCK",
            )
            output_dir = promotion_runs_dir(repo_root)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = write_promotion_completion_record(candidate, decision, repo_root)
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["decision_status"] == PC_BLOCKED


class TestRevalidateEvidence:
    def test_revalidate_evidence_returns_errors_on_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            output_dir = promotion_runs_dir(repo_root)
            output_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = output_dir / "promotion_evidence_manifest.json"
            manifest_path.write_text(json.dumps({
                "evidence_file_hashes": [
                    {"path": ".agentx-init/promotion/nonexistent.json", "sha256": "abc123"},
                ],
            }))
            completion_record_path = output_dir / "promotion_completion_record.json"
            completion_record_path.write_text(json.dumps({
                "completion_record_id": "cr-001",
                "evidence_manifest_path": str(manifest_path.relative_to(repo_root)),
                "review_report_path": "",
            }))
            from agentx_evolve.promotion.promotion_models import PromotionCompletionRecord, from_dict
            import json as _json
            data = _json.loads(completion_record_path.read_text())
            record = from_dict(PromotionCompletionRecord, data)
            errors = revalidate_promotion_evidence(record, repo_root)
            assert len(errors) > 0
