import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerContextPackage,
)
from agentx_evolve.workers.llm_implementation_worker.context_builder import (
    build_context_package,
)
from agentx_evolve.workers.llm_implementation_worker.prompt_builder import (
    build_prompt_package,
    hash_prompt_package,
)


class TestIdempotency:
    def test_same_input_produces_same_context_hash(self, tmp_path):
        task = LLMWorkerTask(
            task_id="t-001",
            max_context_chars=100000,
        )
        ctx_sources = {"spec": {"path": "src/test.py", "content": "def test(): pass"}}
        policy = {"allowed_source_dirs": ["src"]}
        pkg1 = build_context_package(task, ctx_sources, policy, tmp_path)
        pkg2 = build_context_package(task, ctx_sources, policy, tmp_path)
        assert pkg1.context_hash == pkg2.context_hash

    def test_same_prompt_produces_same_hash(self):
        task = LLMWorkerTask(
            task_id="t-001",
            implementation_goal="test",
            target_component_id="test",
        )
        ctx = LLMWorkerContextPackage(
            context_package_id="cp-001",
            task_id="t-001",
            included_files=[],
            context_summary="test",
        )
        pkg1 = build_prompt_package(task, ctx, "llm_worker_model_output.schema.json")
        pkg2 = build_prompt_package(task, ctx, "llm_worker_model_output.schema.json")
        assert pkg1.prompt_hash == pkg2.prompt_hash
