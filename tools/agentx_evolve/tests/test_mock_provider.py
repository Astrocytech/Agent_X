from agentx_evolve.providers.mock_provider import MockProvider


class TestMockProvider:
    def setup_method(self):
        self.provider = MockProvider()

    def test_ready_response(self):
        messages = [
            {"role": "system", "content": "You are Agent_X."},
            {"role": "user", "content": "Say READY"},
        ]
        response = self.provider.complete(messages)
        assert response["role"] == "assistant"
        assert "READY" in response["content"]
        assert response["finish_reason"] == "stop"
        assert response["tool_calls"] == []

    def test_case_insensitive_match(self):
        messages = [{"role": "user", "content": "Please Say READY now"}]
        response = self.provider.complete(messages)
        assert "READY" in response["content"]

    def test_unknown_message(self):
        messages = [{"role": "user", "content": "what is the weather"}]
        response = self.provider.complete(messages)
        assert response["role"] == "assistant"
        assert "Mock response" in response["content"]

    def test_structured_plan_for_ready(self):
        messages = [{"role": "user", "content": "Say READY"}]
        response = self.provider.complete_structured(messages)
        assert response["schema_version"] == "agentx.structured_plan.v1"
        assert response["summary"] == "mock plan for testing"
        assert len(response["actions"]) > 0

    def test_empty_messages(self):
        response = self.provider.complete([])
        assert response["role"] == "assistant"

    def test_model_property(self):
        p = MockProvider(model="mock/custom")
        assert p.model == "mock/custom"

    def test_deterministic_output(self):
        messages = [{"role": "user", "content": "Say READY"}]
        r1 = self.provider.complete(messages)
        r2 = self.provider.complete(messages)
        assert r1["content"] == r2["content"]
