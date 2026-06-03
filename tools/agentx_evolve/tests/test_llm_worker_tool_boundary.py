import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
)
from agentx_evolve.workers.llm_implementation_worker.tool_boundary import (
    build_tool_request,
    request_tool_via_adapter,
    block_direct_tool_bypass,
    DIRECT_MUTATION_BYPASS_REASONS,
)


class TestToolBoundary:
    def test_blocks_direct_tool_bypass(self):
        result = block_direct_tool_bypass("direct shell execution")
        assert result.status == "BLOCKED"
        assert "Direct tool bypass blocked" in result.message

    def test_uses_tool_adapter_only(self):
        task = LLMWorkerTask(task_id="t-001")
        treq = build_tool_request(task, "read_file", {"path": "test.txt"}, "read")
        assert treq["tool_name"] == "read_file"
        assert treq["source_component"] == "LLMImplementationWorker"

    def test_blocks_without_tool_adapter(self):
        task = LLMWorkerTask(task_id="t-002")
        treq = build_tool_request(task, "validate", {}, "validate")
        result = request_tool_via_adapter(treq, {"status": "MISSING"})
        assert result["status"] == "BLOCKED"

    def test_bypass_reasons_listed(self):
        assert "direct shell execution" in DIRECT_MUTATION_BYPASS_REASONS
        assert "direct Git write" in DIRECT_MUTATION_BYPASS_REASONS
