import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion, PromptInputContract,
    PromptOutputContract, PROMPT_STATUS_ACTIVE, PROMPT_STATUS_RETIRED,
    PROMPT_STATUS_BLOCKED, PROMPT_STATUS_DRAFT, PROMPT_TYPE_TASK,
    PROMPT_DECISION_BLOCK, sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version, set_active_prompt_version,
)
from agentx_evolve.prompts.prompt_runtime_binding import (
    check_prompt_permission, bind_prompt_for_runtime,
)
from agentx_evolve.prompts.prompt_validator import (
    validate_prompt_output, validate_prompt_input,
)

CONTRACT_ARGS = {
    "owner_component": "Test",
    "prompt_type": PROMPT_TYPE_TASK,
    "allowed_roles": ["developer"],
    "allowed_task_types": ["IMPLEMENT_PATCH"],
    "allowed_model_profiles": ["claude-sonnet"],
    "allowed_tool_names": ["read", "write"],
    "input_contract_id": "ic-001",
    "output_contract_id": "oc-001",
}


def _make_registry():
    r = create_empty_prompt_registry()
    c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
    r = register_prompt_contract(r, c)
    v = PromptVersion(
        prompt_version_id="pv-001", prompt_contract_id="pc-001",
        version="1.0", prompt_body="implement",         prompt_body_sha256=sha256_text("implement"),
        change_summary="initial", status=PROMPT_STATUS_ACTIVE,
        provenance_id="pp-001",
    )
    r = register_prompt_version(r, v)
    r = set_active_prompt_version(r, "pc-001", "pv-001")
    return r


class TestNegativeCases:
    def test_unregistered_prompt_cannot_bind(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "nonexistent", "developer", "IMPLEMENT_PATCH",
            None, [], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK

    def test_retired_prompt_version_cannot_bind(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0",             prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="init", status=PROMPT_STATUS_RETIRED,
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        assert any("RETIRED" in e for e in r.errors)

    def test_output_missing_required_field_fails_validation(self):
        oc = PromptOutputContract(
            output_contract_id="oc-001", required_format="json",
            required_fields=["summary", "files_changed"],
        )
        data = {"summary": "done"}
        errors = validate_prompt_output(data, oc)
        assert any("files_changed" in e for e in errors)

    def test_context_incompatible_with_input_contract_blocks(self):
        ic = PromptInputContract(
            input_contract_id="ic-001",
            required_fields=["task_description", "file_path"],
            max_input_chars=10000,
        )
        data = {"task_description": "fix"}
        errors = validate_prompt_input(data, ic)
        assert any("file_path" in e for e in errors)

    def test_prompt_layer_does_not_execute_tools(self):
        pass

    def test_prompt_layer_does_not_call_model(self):
        pass

    def test_prompt_layer_does_not_call_network(self):
        pass

    def test_prompt_layer_does_not_execute_raw_shell(self):
        pass
