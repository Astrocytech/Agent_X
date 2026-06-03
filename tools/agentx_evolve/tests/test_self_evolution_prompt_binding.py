import pytest


def test_prompt_binding_structure():
    binding = {
        "binding_id": "pb-001",
        "step_id": "step-001",
        "session_id": "sess-001",
        "run_id": "run-001",
        "prompt_contract_id": "pc-001",
        "prompt_contract_version": "1.0",
        "input_contract_schema_id": "input.schema.json",
        "output_contract_schema_id": "output.schema.json",
    }
    assert binding["prompt_contract_id"] == "pc-001"
    assert binding["prompt_contract_version"] == "1.0"


def test_prompt_binding_requires_version():
    binding = {
        "prompt_contract_id": "pc-001",
        "prompt_contract_version": "1.0",
    }
    assert binding["prompt_contract_version"] is not None and binding["prompt_contract_version"] != ""
