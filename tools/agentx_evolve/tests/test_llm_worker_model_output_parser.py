import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerModelResponse,
)
from agentx_evolve.workers.llm_implementation_worker.model_output_parser import (
    parse_model_output,
    validate_parsed_model_output,
    REJECTION_PATTERNS,
    DIRECT_EXECUTION_PATTERNS,
)


class TestModelOutputParser:
    def test_accepts_required_shape(self):
        resp = LLMWorkerModelResponse(
            task_id="t-001",
            model_request_id="mr-001",
            status="SUCCESS",
            raw_response_ref='{"implementation_summary":"test","implementation_plan":{"steps":[]}}',
        )
        parsed = parse_model_output(resp)
        assert parsed.implementation_summary == "test"
        assert parsed.parsed_output_hash != ""

    def test_rejects_claimed_execution(self):
        resp = LLMWorkerModelResponse(
            task_id="t-002",
            model_request_id="mr-002",
            status="SUCCESS",
            raw_response_ref='{"implementation_summary":"tests already pass","implementation_plan":{}}',
        )
        parsed = parse_model_output(resp)
        assert any("tests passed" in str(r) or "prohibited claim" in str(r).lower() or "rejected" in str(r) for r in parsed.rejected_content)

    def test_rejects_direct_shell_instruction(self):
        resp = LLMWorkerModelResponse(
            task_id="t-003",
            model_request_id="mr-003",
            status="SUCCESS",
            raw_response_ref='{"implementation_summary":"use subprocess.run","implementation_plan":{}}',
        )
        parsed = parse_model_output(resp)
        assert len(parsed.rejected_content) > 0

    def test_rejection_patterns_defined(self):
        assert len(REJECTION_PATTERNS) > 0
        assert "tests passed" in REJECTION_PATTERNS

    def test_direct_execution_patterns_defined(self):
        assert len(DIRECT_EXECUTION_PATTERNS) > 0
        assert "subprocess.run" in DIRECT_EXECUTION_PATTERNS

    def test_validate_parsed_output(self):
        task = LLMWorkerTask(task_id="t-001", worker_mode="PLAN_ONLY")
        resp = LLMWorkerModelResponse(
            task_id="t-001",
            model_request_id="mr-001",
            status="SUCCESS",
            raw_response_ref='{"implementation_summary":"","implementation_plan":{}}',
        )
        parsed = parse_model_output(resp)
        result = validate_parsed_model_output(parsed, task)
        assert result is not None
        assert "implementation_summary" in str(result.errors)
