import pytest
from agentx_evolve.worker.context_builder_client import ContextBuilderClient


class TestContextBuilderClient:
    def test_build_context(self):
        client = ContextBuilderClient()
        result = client.build_context({"task_pack_id": "tp-001", "summary": "test"})
        assert result["task_pack_id"] == "tp-001"
        assert result["summary"] == "test"
        assert result["status"] == "built"
