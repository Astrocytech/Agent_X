from __future__ import annotations

from pathlib import Path

import pytest

from agentx_evolve.git.git_models import (
    GitMutationRequest,
    GitLockRecord,
    GIT_LOCK_ACQUIRED,
    GIT_LOCK_RELEASED,
    GIT_LOCK_BLOCKED,
    new_id,
    utc_now_iso,
)
from agentx_evolve.git.git_mutation_gate import MutationGate
from agentx_evolve.git.git_locks import acquire_git_lock, release_git_lock


class TestGitMutation:
    def test_mutation_request_creation(self):
        req = GitMutationRequest(
            request_id=new_id("mreq"),
            operation="COMMIT",
            repo_path="/tmp/repo",
            target="test.py",
        )
        assert req.operation == "COMMIT"
        assert req.target == "test.py"
