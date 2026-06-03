import pytest
from pathlib import Path
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


@pytest.fixture
def policy(temp_repo):
    return default_sandbox_policy(temp_repo)


def test_network_blocks_by_default(temp_repo, policy):
    result = check_network_allowed("https://example.com", policy)
    assert result.status == "BLOCKED", result.reason


def test_network_requires_explicit_policy(temp_repo, policy):
    policy.network_allowed = True
    result = check_network_allowed(None, policy)
    assert result.status == "FAILED", result.reason


def test_network_target_not_allowlisted_blocks(temp_repo, policy):
    policy.network_allowed = True
    result = check_network_allowed("https://example.com", policy)
    assert result.status == "BLOCKED", result.reason


def test_network_result_schema_fields(temp_repo, policy):
    result = check_network_allowed("https://example.com", policy)
    assert result.result_id
    assert result.timestamp
    assert result.status == "BLOCKED"
    assert result.reason
