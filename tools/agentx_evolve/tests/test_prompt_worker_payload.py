import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


class TestPromptWorkerPayload:
    def test_schema_accepts_valid_payload(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_worker_payload.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_worker_payload.schema.json",
            "payload_id": "pwp-001",
            "binding_id": "rb-001",
            "prompt_contract_id": "pc-001",
            "prompt_version_id": "pv-001",
            "prompt_body": "implement the change",
            "prompt_body_sha256": "abc123",
            "input_data": {"task": "fix"},
            "input_contract_id": "ic-001",
            "output_contract_id": "oc-001",
            "allowed_tool_names": ["read", "write"],
            "registry_snapshot_sha256": "def456",
        }
        jsonschema.validate(data, schema)

    def test_records_binding_and_hash(self):
        from agentx_evolve.prompts.prompt_models import (
            PromptRegistry, PromptWorkerPayload,
        )
        from agentx_evolve.prompts.prompt_runtime_binding import (
            bind_prompt_for_runtime, render_prompt_for_worker,
        )
        from agentx_evolve.prompts.prompt_registry import (
            create_empty_prompt_registry, register_prompt_contract,
            register_prompt_version, set_active_prompt_version,
        )
        from agentx_evolve.prompts.prompt_models import (
            PromptContract, PromptVersion, PROMPT_STATUS_ACTIVE, PROMPT_TYPE_TASK,
        )
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="Test", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], allowed_task_types=["TASK"],
            input_contract_id="ic-001", output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="do it", prompt_body_sha256="abc",
            change_summary="init", status=PROMPT_STATUS_ACTIVE,
            provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        binding = bind_prompt_for_runtime(
            r, "pc-001", "dev", "TASK", None, None, [], {},
        )
        payload = render_prompt_for_worker(r, binding, {"input": "data"})
        assert payload.binding_id == binding.binding_id
        assert payload.prompt_body_sha256 is not None
        assert payload.prompt_contract_id == "pc-001"
