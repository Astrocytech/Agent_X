import pytest
from pathlib import Path
from agentx_evolve.security.path_boundary import check_path_boundary
from agentx_evolve.security.safe_file_ops import safe_read_file, safe_write_file
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "L0").mkdir()
    (repo / "L0" / "protected.py").write_text("")
    (repo / "src").mkdir()
    (repo / "src" / "allowed.txt").write_text("hello")
    (repo / ".agentx-init").mkdir()
    return repo


@pytest.fixture
def policy(temp_repo):
    return default_sandbox_policy(temp_repo)


def test_attempted_symlink_escape_never_allows(temp_repo, policy):
    escape_target = temp_repo.parent / "secret.txt"
    escape_target.write_text("secret")
    link = temp_repo / "innocent_link"
    link.symlink_to(escape_target, target_is_directory=False)
    for op in ["READ", "WRITE", "EDIT"]:
        decision = check_path_boundary(str(link), temp_repo, op, policy)
        assert decision.decision == "BLOCK", f"Symlink escape should block for {op}"
    escape_target.unlink()
    link.unlink()


def test_attempted_l0_write_never_allows(temp_repo, policy):
    for op in ["WRITE", "EDIT", "PATCH_PRECHECK"]:
        decision = check_path_boundary("L0/protected.py", temp_repo, op, policy)
        assert decision.decision == "BLOCK", f"L0 should block for {op}: {decision.reason}"


def test_attempted_path_escape_never_allows(temp_repo, policy):
    for op in ["READ", "WRITE", "EDIT"]:
        decision = check_path_boundary("../outside.txt", temp_repo, op, policy)
        assert decision.decision == "BLOCK", f"Escape should block for {op}"


def test_attempted_raw_shell_never_allows(temp_repo, policy):
    result = check_subprocess_allowed(["bash", "-c", "echo hi"], policy)
    assert result.status == "BLOCK", result.reason


def test_attempted_network_never_allows_by_default(temp_repo, policy):
    result = check_network_allowed("https://example.com", policy)
    assert result.status == "BLOCK", result.reason


def test_opencode_style_patch_cannot_bypass_agentx_governance(temp_repo, policy):
    decision = check_path_boundary("L0/protected.py", temp_repo, "EDIT", policy)
    assert decision.decision == "BLOCK", "L0 edit must block"


def test_plugin_like_tool_cannot_bypass_capability_policy(temp_repo, policy):
    result = check_subprocess_allowed(["plugin_tool", "--execute"], policy)
    assert result.status == "BLOCK", "Unallowlisted tool must block"


def test_absolute_outside_repo_read_blocks(temp_repo, policy):
    outside = temp_repo.parent / "outside.txt"
    outside.write_text("data")
    result = safe_read_file(str(outside), temp_repo, policy)
    assert result.status != "SUCCESS"
    outside.unlink()


def test_rm_rf_root_always_blocks(temp_repo, policy):
    policy.shell_allowed = True
    result = check_subprocess_allowed(["rm", "-rf", "/"], policy)
    assert result.status == "BLOCK"

    policy.shell_allowed = True
    result = check_subprocess_allowed(["rm", "-rf", "."], policy)
    assert result.status == "BLOCK"


def test_write_outside_agentx_init_blocks_by_default(temp_repo, policy):
    result = safe_write_file("src/new.txt", "data", temp_repo, policy)
    assert result.status != "SUCCESS"
