import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion,
    PromptRuntimeBinding, PromptWorkerPayload,
    PROMPT_STATUS_ACTIVE, PROMPT_TYPE_TASK,
    PROMPT_DECISION_ALLOW, PROMPT_DECISION_BLOCK,
    sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version, set_active_prompt_version,
    compute_registry_hash,
)
from agentx_evolve.prompts.prompt_runtime_binding import (
    bind_prompt_for_runtime, render_prompt_for_worker,
)
from agentx_evolve.prompts.prompt_audit_logger import (
    write_latest_prompt_binding,
)


class TestIntegrationBoundaries:
    def test_prompt_worker_payload_contains_binding_info(self):
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], allowed_task_types=["TASK"],
            input_contract_id="ic-001", output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="execute task",
            prompt_body_sha256=sha256_text("execute task"),
            change_summary="init", status=PROMPT_STATUS_ACTIVE,
            provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        binding = bind_prompt_for_runtime(
            r, "pc-001", "dev", "TASK", None, None, [], {},
        )
        payload = render_prompt_for_worker(r, binding, {"input": "data"})
        assert isinstance(payload, PromptWorkerPayload)
        assert payload.prompt_body == "execute task"
        assert payload.prompt_body_sha256 == sha256_text("execute task")

    def test_schema_invalid_binding_does_not_replace_latest(self, tmp_path):
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], allowed_task_types=["TASK"],
            input_contract_id="ic-001", output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body",
            prompt_body_sha256=sha256_text("body"), change_summary="init",
            status=PROMPT_STATUS_ACTIVE, provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        binding = bind_prompt_for_runtime(
            r, "pc-001", "dev", "TASK", None, None, [], {},
        )
        result = write_latest_prompt_binding(binding, tmp_path)
        assert result["binding_id"] == binding.binding_id

    def test_registry_hash_in_binding(self):
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], allowed_task_types=["TASK"],
            input_contract_id="ic-001", output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body",
            prompt_body_sha256=sha256_text("body"), change_summary="init",
            status=PROMPT_STATUS_ACTIVE, provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        registry_hash = compute_registry_hash(r)
        binding = bind_prompt_for_runtime(
            r, "pc-001", "dev", "TASK", None, None, [], {},
        )
        assert binding.registry_snapshot_sha256 == registry_hash
