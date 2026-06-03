from __future__ import annotations

from pathlib import Path

import pytest

from agentx_evolve.git.git_models import (
    GitOperation,
    GitResult,
    GitMutationRequest,
    GitAuditEvent,
    GS_SUCCESS,
    GS_BLOCKED,
    GIT_OP_STATUS,
    new_id,
    utc_now_iso,
    to_dict,
)
from agentx_evolve.git.git_evidence import (
    append_git_operation,
    append_git_result,
    append_git_blocked,
    append_git_mutation_request,
)


class TestGitAudit:
    def test_append_operation(self, tmp_path: Path):
        op = GitOperation(
            op_id=new_id("op"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            repo_path=str(tmp_path),
        )
        result = append_git_operation(op, repo_root=str(tmp_path))
        assert result == op.op_id
        history_path = tmp_path / ".agentx-init" / "git" / "git_operation_history.jsonl"
        assert history_path.exists()

    def test_append_result(self, tmp_path: Path):
        result = GitResult(
            result_id=new_id("res"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            status=GS_SUCCESS,
        )
        res_id = append_git_result(result, repo_root=str(tmp_path))
        assert res_id == result.result_id

    def test_append_blocked(self, tmp_path: Path):
        op = GitOperation(
            op_id=new_id("op"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            repo_path=str(tmp_path),
        )
        result = GitResult(
            result_id=new_id("res"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            status=GS_BLOCKED,
            message="Blocked by policy",
        )
        res_id = append_git_blocked(op, result, repo_root=str(tmp_path))
        assert res_id == result.result_id

    def test_append_mutation_request(self, tmp_path: Path):
        req = GitMutationRequest(
            request_id=new_id("mreq"),
            operation="STAGE",
            repo_path=str(tmp_path),
            target="test.txt",
        )
        req_id = append_git_mutation_request(req, repo_root=str(tmp_path))
        assert req_id == req.request_id

    def test_audit_creates_jsonl(self, tmp_path: Path):
        op = GitOperation(
            op_id=new_id("op"),
            timestamp=utc_now_iso(),
            operation=GIT_OP_STATUS,
            repo_path=str(tmp_path),
        )
        append_git_operation(op, repo_root=str(tmp_path))
        history_path = tmp_path / ".agentx-init" / "git" / "git_operation_history.jsonl"
        assert history_path.stat().st_size > 0
