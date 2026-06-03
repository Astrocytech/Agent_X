import pytest
from pathlib import Path
from agentx_evolve.security.safe_file_ops import (
    safe_read_file, safe_write_file, safe_exact_edit, safe_patch_precheck,
)
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "L0").mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "allowed.txt").write_text("hello world")
    (repo / ".agentx-init").mkdir()
    (repo / ".agentx-init" / "memory").mkdir()
    return repo


@pytest.fixture
def policy(temp_repo):
    return default_sandbox_policy(temp_repo)


def test_safe_read_existing_file(temp_repo, policy):
    result = safe_read_file("src/allowed.txt", temp_repo, policy)
    assert result.status == "SUCCESS", result.errors
    assert result.content == "hello world"


def test_safe_read_missing_file_fails_cleanly(temp_repo, policy):
    result = safe_read_file("src/nonexistent.txt", temp_repo, policy)
    assert result.status != "SUCCESS"


def test_safe_read_large_file_blocks(temp_repo, policy):
    path = temp_repo / "large.txt"
    path.write_text("x" * (policy.max_file_size_bytes + 1))
    result = safe_read_file(str(path), temp_repo, policy)
    assert result.status != "SUCCESS"


def test_safe_write_blocks_when_source_write_disabled(temp_repo, policy):
    result = safe_write_file("src/new.txt", "content", temp_repo, policy)
    assert result.status != "SUCCESS"


def test_safe_write_allows_runtime_artifact(temp_repo, policy):
    result = safe_write_file(
        ".agentx-init/test.txt", "runtime data", temp_repo, policy,
    )
    assert result.status == "SUCCESS", result.errors
    assert (temp_repo / ".agentx-init" / "test.txt").exists()


def test_safe_write_requires_governance_for_source_write(temp_repo, policy):
    policy.source_write_allowed = True
    result = safe_write_file(
        "src/new.txt", "content", temp_repo, policy,
    )
    assert result.status != "SUCCESS"


def test_safe_write_requires_session_for_source_write(temp_repo, policy):
    policy.source_write_allowed = True
    result = safe_write_file(
        "src/new.txt", "content", temp_repo, policy,
        governance_decision_id="gov-123",
    )
    assert result.status != "SUCCESS"


def test_safe_write_source_blocked_without_rollback(temp_repo, policy):
    policy.source_write_allowed = True
    result = safe_write_file(
        "src/new.txt", "content", temp_repo, policy,
        implementation_session_id="sess-1",
        governance_decision_id="gov-123",
    )
    assert result.status != "SUCCESS"
    assert result.errors is not None and any("rollback" in (e or "").lower() for e in result.errors)


def test_safe_write_source_with_all_ids_explicit_rollback_disabled(temp_repo, policy):
    policy.source_write_allowed = True
    policy.require_rollback_for_source_write = False
    result = safe_write_file(
        "src/new.txt", "content", temp_repo, policy,
        implementation_session_id="sess-1",
        governance_decision_id="gov-123",
    )
    assert result.status == "SUCCESS", result.errors
    assert (temp_repo / "src" / "new.txt").exists()
    assert (temp_repo / "src" / "new.txt").read_text() == "content"


def test_safe_exact_edit_single_match_succeeds(temp_repo, policy):
    path = ".agentx-init/edit_test.txt"
    safe_write_file(path, "hello world", temp_repo, policy)
    result = safe_exact_edit(path, "hello", "hi", temp_repo, policy)
    assert result.status == "SUCCESS", result.errors


def test_safe_exact_edit_no_match_blocks(temp_repo, policy):
    path = ".agentx-init/edit_test.txt"
    safe_write_file(path, "hello world", temp_repo, policy)
    result = safe_exact_edit(path, "notfound", "hi", temp_repo, policy)
    assert result.status != "SUCCESS"


def test_safe_exact_edit_multiple_matches_blocks(temp_repo, policy):
    path = ".agentx-init/multi.txt"
    safe_write_file(path, "abc abc abc", temp_repo, policy)
    result = safe_exact_edit(
        path, "abc", "xyz", temp_repo, policy,
    )
    assert result.status != "SUCCESS"


def test_safe_exact_edit_dry_run_changes_nothing(temp_repo, policy):
    path = ".agentx-init/edit_test.txt"
    safe_write_file(path, "hello world", temp_repo, policy)
    original = (temp_repo / ".agentx-init" / "edit_test.txt").read_text()
    result = safe_exact_edit(
        path, "hello", "hi", temp_repo, policy, dry_run=True,
    )
    assert result.status == "DRY_RUN", result.errors
    assert (temp_repo / ".agentx-init" / "edit_test.txt").read_text() == original


def test_patch_precheck_blocks_forbidden_target(temp_repo, policy):
    result = safe_patch_precheck(
        ["src/allowed.txt", "L0/protected.py"], temp_repo, policy,
    )
    assert result.decision == "BLOCK", result.reason
