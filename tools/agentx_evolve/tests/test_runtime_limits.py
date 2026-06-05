import pytest
from agentx_evolve.models.runtime_limits import (
    estimate_token_count,
    check_context_budget,
    truncate_for_evidence,
)
from agentx_evolve.models.model_models import ModelRequest, ModelProfile
from agentx_evolve.model_runtime.runtime_models import RuntimeProfile, LocalRuntimeProfile


class TestEstimateTokenCount:
    def test_empty_string(self):
        assert estimate_token_count("") == 0

    def test_simple_text(self):
        count = estimate_token_count("hello world")
        assert count > 0

    def test_longer_text(self):
        short = estimate_token_count("short")
        long_ = estimate_token_count("a " * 1000)
        assert long_ > short


class TestCheckContextBudget:
    def test_within_budget(self):
        req = ModelRequest(prompt="hello world")
        profile = ModelProfile(context_window=4096)
        runtime = LocalRuntimeProfile(max_context_tokens=8192)
        errors = check_context_budget(req, profile, runtime)
        assert errors == []

    def test_exceeds_budget(self):
        req = ModelRequest(prompt="x" * 50000)
        profile = ModelProfile(context_window=100)
        runtime = LocalRuntimeProfile(max_context_tokens=200)
        errors = check_context_budget(req, profile, runtime)
        assert len(errors) >= 1

    def test_output_tokens_exceed(self):
        req = ModelRequest(prompt="hello", max_output_tokens=9999)
        profile = ModelProfile(max_output_tokens=100)
        runtime = LocalRuntimeProfile(max_context_tokens=8192)
        errors = check_context_budget(req, profile, runtime)
        assert len(errors) >= 1


class TestTruncateForEvidence:
    def test_short_text_not_truncated(self):
        result = truncate_for_evidence("hello world")
        assert result == "hello world"

    def test_long_text_truncated(self):
        text = "hello world " * 500
        result = truncate_for_evidence(text, max_chars=50)
        assert len(result) < len(text)
        assert "(truncated" in result
