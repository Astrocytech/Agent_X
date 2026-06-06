import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.model_binding import (
    invoke_model_for_step,
    create_prompt_binding_for_step,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep


def _make_step(step_id="s-1", run_id="r-1", step_name="test_model", assigned_role="model_agent"):
    return ExecutionStep(step_id=step_id, run_id=run_id, step_name=step_name, assigned_role=assigned_role)


def test_invoke_model_for_step_success():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "SUCCESS", "output": "generated"}

    binding, result = invoke_model_for_step(step, "default", "prompt text", adapter_fn, {})
    assert binding.status == "COMPLETED"
    assert result["status"] == "SUCCESS"


def test_invoke_model_for_step_disallowed_profile():
    step = _make_step()
    binding, result = invoke_model_for_step(step, "bogus", "prompt text", None, {})
    assert binding.status == "BLOCKED"
    assert "not allowed" in binding.errors[-1]


def test_invoke_model_for_step_no_adapter():
    step = _make_step()
    binding, result = invoke_model_for_step(step, "default", "prompt text", None, {})
    assert binding.status == "BLOCKED"
    assert "unavailable" in binding.errors[-1]


def test_invoke_model_for_step_adapter_exception():
    step = _make_step()

    def adapter_fn(**kwargs):
        raise RuntimeError("Adapter failure")

    binding, result = invoke_model_for_step(step, "default", "prompt text", adapter_fn, {})
    assert binding.status == "FAILED"
    assert "Adapter failure" in binding.errors[-1]


def test_invoke_model_for_step_adapter_returns_failure():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "FAILED", "error": "Model error"}

    binding, result = invoke_model_for_step(step, "default", "prompt text", adapter_fn, {})
    assert binding.status == "FAILED"


def test_create_prompt_binding_for_step():
    step = _make_step()
    binding = create_prompt_binding_for_step(step, "contract-1", "input-schema", "output-schema")
    assert binding.step_id == "s-1"
    assert binding.run_id == "r-1"
    assert binding.prompt_contract_id == "contract-1"
    assert binding.prompt_contract_version == "1.0"
    assert binding.input_contract_schema_id == "input-schema"
    assert binding.output_contract_schema_id == "output-schema"
