import json
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitMutationRequest, GitCommitEvidence,
    GS_SUCCESS, GS_BLOCKED,
    new_id, utc_now_iso, GIT_OP_STATUS,
)
from agentx_evolve.git.git_evidence import (
    append_git_operation, append_git_result, append_git_blocked,
    append_git_mutation_request, append_git_commit_evidence,
    write_latest_artifact, write_latest_operation, write_latest_result,
    write_git_evidence_manifest, write_git_review_report, write_git_completion_record,
)


class TestAppendGitOperation:
    def test_appends_to_jsonl(self, tmp_path):
        op = GitOperation(op_id="go-test-1", timestamp=utc_now_iso(), operation=GIT_OP_STATUS)
        result_id = append_git_operation(op, str(tmp_path))
        assert result_id == "go-test-1"
        log_path = tmp_path / ".agentx-init" / "git" / "git_operation_history.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "operation"
        assert record["operation"] == GIT_OP_STATUS

    def test_appends_multiple_operations(self, tmp_path):
        op1 = GitOperation(op_id="go-1", operation=GIT_OP_STATUS)
        op2 = GitOperation(op_id="go-2", operation="DIFF")
        append_git_operation(op1, str(tmp_path))
        append_git_operation(op2, str(tmp_path))
        log_path = tmp_path / ".agentx-init" / "git" / "git_operation_history.jsonl"
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2


class TestAppendGitResult:
    def test_appends_to_jsonl(self, tmp_path):
        result = GitResult(result_id="gr-test-1", status=GS_SUCCESS)
        result_id = append_git_result(result, str(tmp_path))
        assert result_id == "gr-test-1"
        log_path = tmp_path / ".agentx-init" / "git" / "git_result_history.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "result"

    def test_appends_multiple_results(self, tmp_path):
        r1 = GitResult(result_id="gr-1", status=GS_SUCCESS)
        r2 = GitResult(result_id="gr-2", status=GS_BLOCKED)
        append_git_result(r1, str(tmp_path))
        append_git_result(r2, str(tmp_path))
        log_path = tmp_path / ".agentx-init" / "git" / "git_result_history.jsonl"
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2


class TestAppendGitBlocked:
    def test_appends_to_jsonl(self, tmp_path):
        op = GitOperation(op_id="go-test-1", operation=GIT_OP_STATUS)
        result = GitResult(result_id="gr-test-1", status=GS_BLOCKED)
        result_id = append_git_blocked(op, result, str(tmp_path))
        assert result_id == "gr-test-1"
        log_path = tmp_path / ".agentx-init" / "git" / "git_blocked_history.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "blocked"
        assert "operation" in record
        assert "result" in record


class TestAppendGitMutationRequest:
    def test_appends_to_jsonl(self, tmp_path):
        req = GitMutationRequest(request_id="mr-test-1", operation="STAGE", repo_path=str(tmp_path))
        result_id = append_git_mutation_request(req, str(tmp_path))
        assert result_id == "mr-test-1"
        log_path = tmp_path / ".agentx-init" / "git" / "git_mutation_request_history.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "mutation_request"


class TestAppendGitCommitEvidence:
    def test_appends_to_jsonl(self, tmp_path):
        evidence = GitCommitEvidence(commit_id="ce-test-1", message="test commit")
        result_id = append_git_commit_evidence(evidence, str(tmp_path))
        assert result_id == "ce-test-1"
        log_path = tmp_path / ".agentx-init" / "git" / "git_commit_evidence_history.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "commit_evidence"


class TestWriteLatestArtifact:
    def test_writes_artifact(self, tmp_path):
        artifact = {"key": "value", "nested": {"a": 1}}
        art_path = write_latest_artifact(artifact, "test_artifact", str(tmp_path))
        assert Path(art_path).exists()
        data = json.loads(Path(art_path).read_text())
        assert data["key"] == "value"
        assert data["nested"]["a"] == 1

    def test_overwrites_existing_artifact(self, tmp_path):
        write_latest_artifact({"v": 1}, "test", str(tmp_path))
        write_latest_artifact({"v": 2}, "test", str(tmp_path))
        data = json.loads(Path(tmp_path / ".agentx-init" / "git" / "artifacts" / "test.json").read_text())
        assert data["v"] == 2


class TestWriteLatestOperation:
    def test_writes_operation(self, tmp_path):
        op = GitOperation(op_id="go-1", operation=GIT_OP_STATUS)
        path = write_latest_operation(op, str(tmp_path))
        assert Path(path).exists()
        data = json.loads(Path(path).read_text())
        assert data["op_id"] == "go-1"


class TestWriteLatestResult:
    def test_writes_result(self, tmp_path):
        result = GitResult(result_id="gr-1", status=GS_SUCCESS)
        path = write_latest_result(result, str(tmp_path))
        assert Path(path).exists()
        data = json.loads(Path(path).read_text())
        assert data["result_id"] == "gr-1"


class TestWriteGitEvidenceManifest:
    def test_creates_manifest(self, tmp_path):
        manifest = write_git_evidence_manifest(str(tmp_path), validated_commit="abc123")
        assert manifest.validated_commit == "abc123"
        assert manifest.manifest_id.startswith("gem-")
        manifest_path = tmp_path / ".agentx-init" / "git" / "git_evidence_manifest.json"
        assert manifest_path.exists()
        data = json.loads(manifest_path.read_text())
        assert data["validated_commit"] == "abc123"

    def test_includes_artifacts(self, tmp_path):
        write_latest_artifact({"k": "v"}, "test_artifact", str(tmp_path))
        manifest = write_git_evidence_manifest(str(tmp_path))
        assert len(manifest.artifacts) >= 1
        assert "test_artifact" in manifest.artifacts

    def test_has_hash(self, tmp_path):
        manifest = write_git_evidence_manifest(str(tmp_path))
        assert len(manifest.hash) == 64

    def test_has_timestamp(self, tmp_path):
        manifest = write_git_evidence_manifest(str(tmp_path))
        assert "T" in manifest.timestamp


class TestWriteGitReviewReport:
    def test_creates_report(self, tmp_path):
        report = write_git_review_report(str(tmp_path), commit_hash="abc123", status="DONE")
        assert report.report_id.startswith("grr-")
        assert report.status == "DONE"
        report_path = tmp_path / ".agentx-init" / "git" / "git_implementation_review_report.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert data["commit_hash"] == "abc123"

    def test_defaults(self, tmp_path):
        report = write_git_review_report(str(tmp_path))
        assert report.reviewer == "AGENTX_GIT_INTEGRATION_LAYER"

    def test_has_timestamp(self, tmp_path):
        report = write_git_review_report(str(tmp_path))
        assert "T" in report.timestamp


class TestWriteGitCompletionRecord:
    def test_creates_record(self, tmp_path):
        record = write_git_completion_record(str(tmp_path), status="VALIDATED")
        assert record.status == "VALIDATED"
        assert record.record_id.startswith("gcr-")
        record_path = tmp_path / ".agentx-init" / "git" / "git_integration_completion_record.json"
        assert record_path.exists()
        data = json.loads(record_path.read_text())
        assert data["status"] == "VALIDATED"

    def test_default_status(self, tmp_path):
        record = write_git_completion_record(str(tmp_path))
        assert record.status == "VALIDATED"

    def test_sets_repo_root(self, tmp_path):
        record = write_git_completion_record(str(tmp_path))
        assert record.repo_root == str(tmp_path)

    def test_has_hash(self, tmp_path):
        record = write_git_completion_record(str(tmp_path))
        assert len(record.hash) == 64
