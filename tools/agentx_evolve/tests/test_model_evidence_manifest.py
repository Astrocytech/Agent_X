import pytest
from agentx_evolve.models.model_models import ModelEvidenceManifest, ModelCompletionRecord


class TestModelEvidenceManifest:
    def test_manifest_records_evidence(self):
        manifest = ModelEvidenceManifest(manifest_id="m-001")
        record = ModelCompletionRecord(
            record_id="r-001",
            model_request_id="req-001",
            model_response_id="resp-001",
            status="SUCCESS",
            summary="completed",
        )
        manifest.add_record(record)
        assert len(manifest.completion_records) == 1
        assert manifest.completion_records[0].record_id == "r-001"

    def test_manifest_empty_by_default(self):
        manifest = ModelEvidenceManifest()
        assert manifest.completion_records == []
        assert manifest.evidence_refs == []

    def test_completion_record_serializes(self):
        record = ModelCompletionRecord(
            record_id="r-002",
            model_request_id="req-002",
            model_response_id="resp-002",
            timestamp="2026-01-01T00:00:00",
            status="FAILED",
            summary="timeout",
        )
        d = record.to_dict()
        assert d["record_id"] == "r-002"
        assert d["status"] == "FAILED"
        assert d["summary"] == "timeout"

    def test_manifest_serializes(self):
        manifest = ModelEvidenceManifest(manifest_id="m-002")
        record = ModelCompletionRecord(
            record_id="r-003", status="SUCCESS", summary="ok",
        )
        manifest.add_record(record)
        d = manifest.to_dict()
        assert d["manifest_id"] == "m-002"
        assert len(d["completion_records"]) == 1

    def test_manifest_add_multiple_records(self):
        manifest = ModelEvidenceManifest(manifest_id="m-003")
        for i in range(3):
            record = ModelCompletionRecord(record_id=f"r-{i}", status="SUCCESS")
            manifest.add_record(record)
        assert len(manifest.completion_records) == 3
