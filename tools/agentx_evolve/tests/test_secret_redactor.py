import pytest
from pathlib import Path
from agentx_evolve.security.secret_redactor import redact_secrets
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


@pytest.fixture
def policy(temp_repo):
    return default_sandbox_policy(temp_repo)


def test_api_key_like_value_redacted(temp_repo, policy):
    text = 'OPENAI_API_KEY="sk-1234567890abcdef1234567890abcdef"'
    result = redact_secrets(text, policy)
    assert result.redaction_count > 0, f"No redactions in: {result.redacted_text}"
    assert "[REDACTED_API_KEY]" in result.redacted_text, result.redacted_text


def test_env_secret_name_redacted(temp_repo, policy):
    text = "GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef123456"
    result = redact_secrets(text, policy)
    assert result.redaction_count > 0, f"No redactions in: {result.redacted_text}"
    assert "[REDACTED_TOKEN]" in result.redacted_text, result.redacted_text


def test_generic_long_token_redacted(temp_repo, policy):
    text = "sk-abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklm"
    result = redact_secrets(text, policy)
    assert result.redaction_count > 0, f"No redactions in: {result.redacted_text}"
    assert "[REDACTED_TOKEN]" in result.redacted_text or "[REDACTED_SECRET]" in result.redacted_text


def test_no_secret_does_not_alter_text(temp_repo, policy):
    text = "this is plain text with no secrets"
    result = redact_secrets(text, policy)
    assert result.redaction_count == 0
    assert result.redacted_text == text


def test_redaction_count_recorded(temp_repo, policy):
    text = 'OPENAI_API_KEY="sk-key1" and GITHUB_TOKEN="ghp-token2"'
    result = redact_secrets(text, policy)
    assert result.redaction_count > 0
    assert result.redaction_types


def test_empty_text_returns_success(temp_repo, policy):
    result = redact_secrets("", policy)
    assert result.status == "SUCCESS"
    assert result.redaction_count == 0


def test_custom_pattern_from_policy(temp_repo, policy):
    policy.redact_secret_patterns = [r"MY_CUSTOM_KEY=\w+"]
    text = "MY_CUSTOM_KEY=super_secret_value"
    result = redact_secrets(text, policy)
    assert result.redaction_count > 0
    assert "[REDACTED_SECRET]" in result.redacted_text


def test_redact_secrets_with_none_policy_uses_defaults():
    text = 'OPENAI_API_KEY="sk-1234567890abcdef1234567890abcdef"'
    result = redact_secrets(text, None)
    assert result.redaction_count > 0
    assert "[REDACTED_API_KEY]" in result.redacted_text


def test_no_secret_with_none_policy_preserves_text():
    text = "safe text with no credentials"
    result = redact_secrets(text, None)
    assert result.redaction_count == 0
    assert result.redacted_text == text
