import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.evidence_manifest import (
    create_evidence_manifest,
    write_evidence_manifest,
    create_review_report,
    write_review_report,
    create_completion_record,
    write_completion_record,
)
from agentx_evolve.orchestrator.orchestrator_config import RUNTIME_ARTIFACT_ROOT


def test_create_evidence_manifest():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    assert manifest.run_id == "run-1"
    assert manifest.session_id == "sess-1"
    assert manifest.manifest_id.startswith("em-")


def test_create_evidence_manifest_has_hash():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    assert manifest.evidence_manifest_sha256 != ""
    assert len(manifest.evidence_manifest_sha256) == 64


def test_write_evidence_manifest_writes_file(tmp_path):
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    result = write_evidence_manifest(manifest, tmp_path)
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()
    assert result["sha256"] == manifest.evidence_manifest_sha256


def test_create_review_report():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    assert report.review_report_id.startswith("rr-")
    assert report.evidence_manifest_sha256 == manifest.evidence_manifest_sha256


def test_create_review_report_has_hash():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    assert report.review_report_sha256 != ""
    assert len(report.review_report_sha256) == 64


def test_write_review_report_writes_file(tmp_path):
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    result = write_review_report(report, tmp_path, "run-1")
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()
    assert result["sha256"] == report.review_report_sha256


def test_create_completion_record():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report, status="DONE")
    assert record.completion_record_id.startswith("cr-")
    assert record.status == "DONE"


def test_create_completion_record_has_hash():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report, status="DONE")
    assert record.completion_record_sha256 != ""
    assert len(record.completion_record_sha256) == 64


def test_write_completion_record_writes_file(tmp_path):
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report)
    result = write_completion_record(record, tmp_path, "run-1")
    assert "path" in result
    assert "sha256" in result
    p = Path(result["path"])
    assert p.exists()
    assert result["sha256"] == record.completion_record_sha256


def test_completion_record_references_manifest_and_report_hashes():
    manifest = create_evidence_manifest(run_id="run-1", session_id="sess-1")
    report = create_review_report(manifest)
    record = create_completion_record(manifest, report, status="DONE")
    assert record.evidence_manifest_sha256 == manifest.evidence_manifest_sha256
    assert record.review_report_sha256 == report.review_report_sha256
