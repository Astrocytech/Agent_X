import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerContextPackage,
)
from agentx_evolve.workers.llm_implementation_worker.prompt_builder import (
    build_prompt_package,
    build_output_schema_instruction,
    hash_prompt_package,
    FORBIDDEN_ACTIONS,
)


class TestPromptBuilder:
    def test_creates_schema_instruction(self):
        instruction = build_output_schema_instruction(
            "llm_worker_model_output.schema.json"
        )
        assert "implementation_summary" in instruction

    def test_includes_forbidden_actions(self):
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
        pkg = build_prompt_package(task, ctx, "llm_worker_model_output.schema.json")
        assert len(pkg.forbidden_actions) > 0
        assert "direct source write" in pkg.forbidden_actions

    def test_prompt_hash_is_stable(self):
        task = LLMWorkerTask(
            task_id="t-002",
            implementation_goal="test",
            target_component_id="test",
        )
        ctx = LLMWorkerContextPackage(
            context_package_id="cp-002",
            task_id="t-002",
            included_files=[],
            context_summary="test",
        )
        pkg1 = build_prompt_package(task, ctx, "llm_worker_model_output.schema.json")
        pkg2 = build_prompt_package(task, ctx, "llm_worker_model_output.schema.json")
        assert pkg1.prompt_hash == pkg2.prompt_hash

    def test_hash_prompt_package(self):
        pkg = type("Pkg", (), {
            "system_contract": "sys",
            "developer_contract": "dev",
            "task_prompt": "task",
            "output_schema_instruction": "schema",
            "forbidden_actions": ["a"],
            "required_output_sections": ["b"],
        })()
        h = hash_prompt_package(pkg)
        assert isinstance(h, str)
        assert len(h) == 64
