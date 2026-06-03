import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion,
    PROMPT_STATUS_ACTIVE, PROMPT_TYPE_TASK,
    PROMPT_DECISION_ALLOW, PROMPT_DECISION_BLOCK,
    sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version, set_active_prompt_version,
)
from agentx_evolve.prompts.prompt_runtime_binding import (
    check_prompt_permission, bind_prompt_for_runtime,
    resolve_prompt_body, render_prompt_for_worker,
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


class TestCheckPromptPermission:
    def test_allows_valid_request(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            "claude-sonnet", ["read"], {},
        )
        assert perm.decision == PROMPT_DECISION_ALLOW

    def test_blocks_unknown_contract(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "unknown", "developer", "IMPLEMENT_PATCH",
            None, [], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK

    def test_blocks_disallowed_role(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "pc-001", "admin", "IMPLEMENT_PATCH",
            None, [], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK

    def test_blocks_disallowed_task_type(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "pc-001", "developer", "REVIEW",
            None, [], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK

    def test_blocks_disallowed_model_profile(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            "gpt-4", [], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK

    def test_blocks_disallowed_requested_tool(self):
        r = _make_registry()
        perm = check_prompt_permission(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            None, ["execute"], {},
        )
        assert perm.decision == PROMPT_DECISION_BLOCK


class TestBindPromptForRuntime:
    def test_bind_records_registry_snapshot_hash(self):
        r = _make_registry()
        binding = bind_prompt_for_runtime(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            None, None, ["read"], {},
        )
        assert binding.registry_snapshot_sha256 is not None
        assert binding.prompt_version_id == "pv-001"
        assert binding.prompt_body_sha256 is not None

    def test_bind_blocks_unknown_contract(self):
        r = _make_registry()
        binding = bind_prompt_for_runtime(
            r, "unknown", "developer", "IMPLEMENT_PATCH",
            None, None, [], {},
        )
        assert len(binding.errors) > 0

    def test_resolve_prompt_body_returns_body(self):
        r = _make_registry()
        binding = bind_prompt_for_runtime(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            None, None, ["read"], {},
        )
        body = resolve_prompt_body(r, binding)
        assert body == "implement"

    def test_render_prompt_for_worker_returns_payload(self):
        r = _make_registry()
        binding = bind_prompt_for_runtime(
            r, "pc-001", "developer", "IMPLEMENT_PATCH",
            None, None, ["read"], {},
        )
        payload = render_prompt_for_worker(r, binding, {"task": "fix"})
        assert payload.prompt_body == "implement"
        assert payload.binding_id == binding.binding_id
        assert payload.registry_snapshot_sha256 is not None
