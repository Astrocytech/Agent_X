import json
import hashlib
from pathlib import Path
from agentx_evolve.git.git_models import (
    GitOperation, GitResult, GitOperationResult, GitMutationRequest,
    GitCommitEvidence, GitEvidenceManifest, GitReviewReport, GitCompletionRecord,
    GS_SUCCESS, GS_BLOCKED, GS_FAILED, GS_PENDING,
    new_id, utc_now_iso, to_dict,
)


def _jsonl_path(repo_root: str, name: str) -> Path:
    return Path(repo_root) / ".agentx-init" / "git" / f"{name}.jsonl"


def _artifact_dir(repo_root: str) -> Path:
    return Path(repo_root) / ".agentx-init" / "git"


def _write_json_atomic(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str))
    tmp.rename(path)


def _append_jsonl(record: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if path.exists():
        lines = path.read_text().splitlines()
    lines.append(json.dumps(record, default=str))
    path.write_text("\n".join(lines) + "\n")


def append_git_operation(op: GitOperation, repo_root: str) -> str:
    record = to_dict(op)
    record["event"] = "operation"
    path = _jsonl_path(repo_root, "git_operation_history")
    _append_jsonl(record, path)
    return op.op_id


def append_git_result(result: GitResult, repo_root: str) -> str:
    record = to_dict(result)
    record["event"] = "result"
    path = _jsonl_path(repo_root, "git_result_history")
    _append_jsonl(record, path)
    return result.result_id


def append_git_blocked(op: GitOperation, result: GitResult, repo_root: str) -> str:
    record = {
        "event": "blocked",
        "operation": to_dict(op),
        "result": to_dict(result),
        "timestamp": utc_now_iso(),
    }
    path = _jsonl_path(repo_root, "git_blocked_history")
    _append_jsonl(record, path)
    return result.result_id


def append_git_mutation_request(req: GitMutationRequest, repo_root: str) -> str:
    record = to_dict(req)
    record["event"] = "mutation_request"
    path = _jsonl_path(repo_root, "git_mutation_request_history")
    _append_jsonl(record, path)
    return req.request_id


def append_git_commit_evidence(evidence: GitCommitEvidence, repo_root: str) -> str:
    record = to_dict(evidence)
    record["event"] = "commit_evidence"
    path = _jsonl_path(repo_root, "git_commit_evidence_history")
    _append_jsonl(record, path)
    return evidence.commit_id


def write_latest_artifact(artifact: dict, name: str, repo_root: str) -> str:
    art_dir = _artifact_dir(repo_root) / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)
    art_path = art_dir / f"{name}.json"
    _write_json_atomic(artifact, art_path)
    return str(art_path)


def write_latest_operation(op: GitOperation, repo_root: str) -> str:
    art_dir = _artifact_dir(repo_root)
    art_dir.mkdir(parents=True, exist_ok=True)
    path = art_dir / "git_latest_operation.json"
    _write_json_atomic(to_dict(op), path)
    return str(path)


def write_latest_result(result: GitResult, repo_root: str) -> str:
    art_dir = _artifact_dir(repo_root)
    art_dir.mkdir(parents=True, exist_ok=True)
    path = art_dir / "git_latest_result.json"
    _write_json_atomic(to_dict(result), path)
    return str(path)


def write_git_evidence_manifest(repo_root: str, validated_commit: str = "") -> GitEvidenceManifest:
    manifest_id = new_id("gem")
    timestamp = utc_now_iso()
    art_dir = _artifact_dir(repo_root) / "artifacts"
    artifacts: dict[str, str] = {}
    if art_dir.exists():
        for f in sorted(art_dir.iterdir()):
            if f.suffix == ".json":
                artifacts[f.stem] = str(f)
    manifest = GitEvidenceManifest(
        manifest_id=manifest_id,
        validated_commit=validated_commit,
        timestamp=timestamp,
        artifacts=artifacts,
    )
    raw = json.dumps(to_dict(manifest), default=str)
    manifest.hash = hashlib.sha256(raw.encode()).hexdigest()
    manifest_path = _artifact_dir(repo_root) / "git_evidence_manifest.json"
    _write_json_atomic(to_dict(manifest), manifest_path)
    return manifest


def write_git_review_report(repo_root: str, commit_hash: str = "", reviewer: str = "AGENTX_GIT_INTEGRATION_LAYER", status: str = "DONE") -> GitReviewReport:
    report = GitReviewReport(
        report_id=new_id("grr"),
        commit_hash=commit_hash,
        reviewer=reviewer,
        status=status,
        findings=[],
        timestamp=utc_now_iso(),
    )
    path = _artifact_dir(repo_root) / "git_implementation_review_report.json"
    _write_json_atomic(to_dict(report), path)
    return report


def write_git_completion_record(repo_root: str, status: str = "VALIDATED") -> GitCompletionRecord:
    record = GitCompletionRecord(
        record_id=new_id("gcr"),
        timestamp=utc_now_iso(),
        repo_root=repo_root,
        status=status,
        summary=f"Git completion record created with status {status}",
    )
    raw = json.dumps(to_dict(record), default=str)
    record.hash = hashlib.sha256(raw.encode()).hexdigest()
    path = _artifact_dir(repo_root) / "git_integration_completion_record.json"
    _write_json_atomic(to_dict(record), path)
    return record
