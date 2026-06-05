import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerPromptPackage,
)
from agentx_evolve.workers.llm_implementation_worker.model_boundary import (
    build_model_request,
    call_model_adapter,
)


class TestModelBoundary:
    def test_builds_model_request(self):
        task = LLMWorkerTask(task_id="t-001", max_model_output_chars=16000)
        pp = LLMWorkerPromptPackage(prompt_package_id="pp-001")
        req = build_model_request(task, pp, "claude-sonnet", {})
        assert req.model_profile_id == "claude-sonnet"
        assert req.max_output_chars == 16000
        assert req.model_request_hash != ""

    def test_blocks_without_model_adapter(self):
        task = LLMWorkerTask(task_id="t-002")
        pp = LLMWorkerPromptPackage(prompt_package_id="pp-002")
        req = build_model_request(task, pp, "default", {})
        resp = call_model_adapter(req, pp, {"status": "MISSING"})
        assert resp.status == "BLOCKED"
        assert "adapter is missing" in resp.safe_summary.lower()

    def test_rejects_invalid_model_response(self):
        task = LLMWorkerTask(task_id="t-003")
        pp = LLMWorkerPromptPackage(prompt_package_id="pp-003")
        req = build_model_request(task, pp, "default", {})
        resp = call_model_adapter(req, pp, {"status": "AVAILABLE"})
        assert resp.status == "INVALID"

    def test_does_not_import_provider_clients(self):
        import sys as _sys
        mod_names = [
            "openai", "anthropic", "google.generativeai",
            "transformers", "torch",
        ]
        for m in mod_names:
            assert m not in _sys.modules, f"{m} should not be imported"
