import pytest
from pathlib import Path
from agentx_evolve.security.path_boundary import normalize_repo_path, check_path_boundary
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "L0").mkdir()
    (repo / "L0" / "protected.py").write_text("")
    (repo / "src").mkdir()
    (repo / "src" / "allowed.txt").write_text("hello")
    (repo / "core").mkdir()
    (repo / "core" / "protected_core.py").write_text("")
    (repo / ".agentx-init").mkdir()
    (repo / ".agentx-init" / "memory").mkdir()
    return repo


@pytest.fixture
def policy(temp_repo):
    return default_sandbox_policy(temp_repo)


def test_relative_path_inside_repo_allows_read(temp_repo, policy):
    decision = check_path_boundary("src/allowed.txt", temp_repo, "READ", policy)
    assert decision.decision == "ALLOW", decision.reason


def test_absolute_path_inside_repo_allows_read(temp_repo, policy):
    path = str(temp_repo / "src" / "allowed.txt")
    decision = check_path_boundary(path, temp_repo, "READ", policy)
    assert decision.decision == "ALLOW", decision.reason


def test_path_traversal_blocks(temp_repo, policy):
    decision = check_path_boundary("../outside.txt", temp_repo, "READ", policy)
    assert decision.decision == "BLOCK", decision.reason


def test_absolute_path_outside_repo_blocks(temp_repo, policy):
    decision = check_path_boundary("/etc/passwd", temp_repo, "READ", policy)
    assert decision.decision == "BLOCK", decision.reason


def test_symlink_escape_blocks(temp_repo, policy):
    escape_target = temp_repo.parent / "outside.txt"
    escape_target.write_text("secret")
    link = temp_repo / "escape_link"
    link.symlink_to(escape_target, target_is_directory=False)
    decision = check_path_boundary(str(link), temp_repo, "READ", policy)
    assert decision.decision == "BLOCK", decision.reason
    escape_target.unlink()


def test_l0_write_blocks(temp_repo, policy):
    decision = check_path_boundary("L0/protected.py", temp_repo, "WRITE", policy)
    assert decision.decision == "BLOCK", decision.reason


def test_l0_edit_blocks(temp_repo, policy):
    decision = check_path_boundary("L0/protected.py", temp_repo, "EDIT", policy)
    assert decision.decision == "BLOCK", decision.reason


def test_protected_path_write_blocks(temp_repo, policy):
    decision = check_path_boundary("core/protected_core.py", temp_repo, "WRITE", policy)
    assert decision.decision == "BLOCK", decision.reason


def test_runtime_write_under_agentx_init_allows(temp_repo, policy):
    decision = check_path_boundary(".agentx-init/test.txt", temp_repo, "WRITE", policy)
    assert decision.decision == "ALLOW", decision.reason


def test_normalize_repo_path_outside(temp_repo, policy):
    result = normalize_repo_path("/etc/passwd", temp_repo)
    assert result.inside_repo is False


def test_normalize_repo_path_inside(temp_repo, policy):
    result = normalize_repo_path("src/allowed.txt", temp_repo)
    assert result.inside_repo is True
