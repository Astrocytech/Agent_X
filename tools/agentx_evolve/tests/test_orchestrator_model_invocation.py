import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.model_invocation import (
    invoke_model_for_step,
    create_prompt_binding_for_step,
    ALLOWED_MODEL_PROFILES,
    REQUIRED_PROMPT_CONTRACT_VERSION,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep


def test_allowed_model_profiles():
    assert "default" in ALLOWED_MODEL_PROFILES
    assert "fast" in ALLOWED_MODEL_PROFILES
    assert "precise" in ALLOWED_MODEL_PROFILES
    assert len(ALLOWED_MODEL_PROFILES) == 3


def test_required_prompt_contract_version():
    assert REQUIRED_PROMPT_CONTRACT_VERSION == "1.0"


def _make_step(step_id="s-1", run_id="r-1", step_name="test_model", assigned_role="model_agent"):
    return ExecutionStep(step_id=step_id, run_id=run_id, step_name=step_name, assigned_role=assigned_role)


def test_invoke_model_for_step_success():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "SUCCESS", "output": "generated"}

    binding, result = invoke_model_for_step(step, "default", "prompt text", adapter_fn, {})
    assert binding.status == "COMPLETED"
    assert result["status"] == "SUCCESS"
    assert binding.model_profile_id == "default"


def test_invoke_model_for_step_disallowed_profile():
    step = _make_step()
    binding, result = invoke_model_for_step(step, "bogus_profile", "text", None, {})
    assert binding.status == "BLOCKED"
    assert "not allowed" in binding.errors[-1]


def test_invoke_model_for_step_null_adapter():
    step = _make_step()
    binding, result = invoke_model_for_step(step, "default", "text", None, {})
    assert binding.status == "BLOCKED"
    assert "unavailable" in binding.errors[-1]


def test_invoke_model_for_step_adapter_throws():
    step = _make_step()

    def broken(**kwargs):
        raise ValueError("Broken adapter")

    binding, result = invoke_model_for_step(step, "default", "text", broken, {})
    assert binding.status == "FAILED"
    assert "Broken adapter" in binding.errors[-1]


def test_invoke_model_for_step_sets_idempotency():
    step = _make_step(step_id="s-model-1")

    def adapter_fn(**kwargs):
        return {"status": "SUCCESS"}

    binding, _ = invoke_model_for_step(step, "precise", "text", adapter_fn, {})
    assert "s-model-1" in binding.idempotency_key
    assert "precise" in binding.idempotency_key


def test_create_prompt_binding_for_step_full():
    step = _make_step(step_id="s-pb-1", run_id="r-pb-1")
    binding = create_prompt_binding_for_step(step, "pc-1", "in-schema", "out-schema")
    assert binding.binding_id.startswith("pb-")
    assert binding.step_id == "s-pb-1"
    assert binding.run_id == "r-pb-1"
    assert binding.prompt_contract_id == "pc-1"
    assert binding.prompt_contract_version == "1.0"
    assert binding.input_contract_schema_id == "in-schema"
    assert binding.output_contract_schema_id == "out-schema"
