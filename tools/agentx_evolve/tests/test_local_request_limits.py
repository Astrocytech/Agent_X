import pytest
from pathlib import Path
from agentx_evolve.model_runtime.profile_loader import load_request_limits
from agentx_evolve.model_runtime.profile_validator import validate_request_limits
from agentx_evolve.model_runtime.runtime_models import LocalRuntimeRequestLimits

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "model_runtime"


def test_valid_limits_load():
    l = load_request_limits(FIXTURES / "valid_request_limits_small_context.json")
    assert l.max_prompt_tokens == 2048


def test_request_limits_reject_zero_or_negative():
    l = LocalRuntimeRequestLimits(max_prompt_tokens=0, max_response_tokens=0, max_total_context_tokens=0)
    result = validate_request_limits(l)
    assert result["valid"] is False

    l2 = LocalRuntimeRequestLimits(max_prompt_tokens=-1, max_response_tokens=2048, max_total_context_tokens=4096)
    result2 = validate_request_limits(l2)
    assert result2["valid"] is False
