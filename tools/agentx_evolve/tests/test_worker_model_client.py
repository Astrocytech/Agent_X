import pytest
from agentx_evolve.worker.model_client import ModelClient


class TestModelClient:
    def test_invoke_model(self):
        client = ModelClient()
        result = client.invoke_model("hello", "gpt-4")
        assert result["model"] == "gpt-4"
        assert result["prompt_length"] == 5
        assert result["status"] == "simulated"
