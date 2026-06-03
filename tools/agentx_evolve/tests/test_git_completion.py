from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentx_evolve.git.git_models import (
    GitCompletionRecord,
    GitEvidenceManifest,
    GitReviewReport,
    new_id,
    utc_now_iso,
    to_dict,
)
from agentx_evolve.git.git_evidence import (
    write_git_completion_record,
    write_git_evidence_manifest,
    write_git_review_report,
)


class TestGitCompletion:
    def test_write_completion_record(self, tmp_path: Path):
        record = write_git_completion_record(repo_root=str(tmp_path), status="VALIDATED")
        assert isinstance(record, GitCompletionRecord)
        assert record.status == "VALIDATED"
        record_path = tmp_path / ".agentx-init" / "git" / "git_integration_completion_record.json"
        assert record_path.exists()

    def test_write_evidence_manifest(self, tmp_path: Path):
        manifest = write_git_evidence_manifest(repo_root=str(tmp_path), validated_commit="abc123")
        assert isinstance(manifest, GitEvidenceManifest)
        assert manifest.validated_commit == "abc123"
        manifest_path = tmp_path / ".agentx-init" / "git" / "git_evidence_manifest.json"
        assert manifest_path.exists()

    def test_write_review_report(self, tmp_path: Path):
        report = write_git_review_report(
            repo_root=str(tmp_path),
            commit_hash="def456",
            reviewer="TestAgent",
            status="DONE",
        )
        assert isinstance(report, GitReviewReport)
        assert report.commit_hash == "def456"
        report_path = tmp_path / ".agentx-init" / "git" / "git_implementation_review_report.json"
        assert report_path.exists()

    def test_completion_record_has_hash(self, tmp_path: Path):
        record = write_git_completion_record(repo_root=str(tmp_path), status="VALIDATED")
        assert record.hash != ""
        assert len(record.hash) == 64

    def test_completion_json_valid(self, tmp_path: Path):
        write_git_completion_record(repo_root=str(tmp_path), status="VALIDATED")
        path = tmp_path / ".agentx-init" / "git" / "git_integration_completion_record.json"
        data = json.loads(path.read_text())
        assert data["status"] == "VALIDATED"
