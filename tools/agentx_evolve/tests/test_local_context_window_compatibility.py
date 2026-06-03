import pytest
from agentx_evolve.model_runtime.compatibility_checker import check_context_window_compatibility
from agentx_evolve.model_runtime.runtime_models import LocalModelProfile


def test_context_fits():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=4096,
    )
    result = check_context_window_compatibility(model, 2048)
    assert result["compatible"] is True


def test_context_exceeded():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=1024,
    )
    result = check_context_window_compatibility(model, 2048)
    assert result["compatible"] is False


def test_no_declared_context_blocks():
    model = LocalModelProfile(
        model_id="m1", model_family="test", model_format="gguf",
        quantization="Q4", max_context_tokens=0,
    )
    result = check_context_window_compatibility(model, 100)
    assert result["compatible"] is False
