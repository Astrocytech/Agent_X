import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.model_invoker import invoke_model_for_step, create_prompt_binding_for_step
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep
from agentx_evolve.orchestrator.orchestrator_config import STEP_STATUS_PENDING


def _make_step(**overrides) -> ExecutionStep:
    params = dict(
        step_id="s-1",
        plan_id="p-1",
        run_id="run-1",
        step_index=0,
        step_name="invoke_default",
        step_type="MODEL",
        assigned_role="model_agent",
        status=STEP_STATUS_PENDING,
    )
    params.update(overrides)
    return ExecutionStep(**params)


class TestInvokeModelUsesAdapter:
    def test_invoke_model_uses_adapter(self):
        step = _make_step()
        called = False

        def fake_adapter(**kw):
            nonlocal called
            called = True
            return {"status": "SUCCESS", "output": "hello"}

        binding, result = invoke_model_for_step(step, "default", "prompt text", fake_adapter, {})
        assert called
        assert result["status"] == "SUCCESS"
        assert binding.status == "COMPLETED"


class TestInvokeModelBlocksUnapprovedProfile:
    def test_invoke_model_blocks_unapproved_profile(self):
        step = _make_step()
        binding, result = invoke_model_for_step(step, "gpt-5-mega", "", None, {})
        assert result["status"] == "BLOCKED"
        assert "not allowed" in result["error"].lower()
        assert binding.status == "BLOCKED"


class TestInvokeModelBlocksWhenAdapterNone:
    def test_invoke_model_blocks_when_adapter_none(self):
        step = _make_step()
        binding, result = invoke_model_for_step(step, "default", "", None, {})
        assert result["status"] == "BLOCKED"
        assert "adapter unavailable" in result["error"].lower()
        assert binding.status == "BLOCKED"


class TestInvokeModelRecordsBinding:
    def test_invoke_model_records_binding(self):
        step = _make_step()

        def fake_adapter(**kw):
            return {"status": "SUCCESS", "output": "ok"}

        binding, result = invoke_model_for_step(step, "default", "some prompt", fake_adapter, {})
        assert binding.binding_id.startswith("mb-")
        assert binding.step_id == "s-1"
        assert binding.model_profile_id == "default"
        assert binding.idempotency_key == "model-s-1-default"


class TestCreatePromptBindingForStep:
    def test_create_prompt_binding_for_step(self):
        step = _make_step()
        pb = create_prompt_binding_for_step(step, "contract-1", "input-schema-1", "output-schema-1")
        assert pb.binding_id.startswith("pb-")
        assert pb.step_id == "s-1"
        assert pb.prompt_contract_id == "contract-1"
        assert pb.input_contract_schema_id == "input-schema-1"
        assert pb.output_contract_schema_id == "output-schema-1"


class TestInvokeModelHandlesAdapterException:
    def test_invoke_model_handles_adapter_exception(self):
        step = _make_step()

        def broken_adapter(**kw):
            raise ValueError("model failed")

        binding, result = invoke_model_for_step(step, "default", "", broken_adapter, {})
        assert result["status"] == "FAILED"
        assert "model failed" in result["error"]
        assert binding.status == "FAILED"
