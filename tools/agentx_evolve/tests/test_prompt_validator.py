import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptContract, PromptVersion, PromptRegistry, PromptInputContract,
    PromptOutputContract, PromptRuntimeBinding,
    PROMPT_STATUS_DRAFT, PROMPT_STATUS_BLOCKED, PROMPT_STATUS_RETIRED,
    PROMPT_TYPE_TASK, PROMPT_TYPE_SYSTEM,
    sha256_text,
)
from agentx_evolve.prompts.prompt_validator import (
    validate_prompt_contract, validate_prompt_version,
    validate_prompt_registry, validate_prompt_input,
    validate_prompt_output, validate_runtime_binding,
)


class TestValidatePromptContract:
    def test_valid_contract_passes(self):
        c = PromptContract(
            prompt_contract_id="pc-001",
            prompt_name="test",
            owner_component="Test",
            prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["developer"],
            input_contract_id="ic-001",
            output_contract_id="oc-001",
            status=PROMPT_STATUS_DRAFT,
        )
        errors = validate_prompt_contract(c)
        assert errors == []

    def test_missing_contract_id_fails(self):
        c = PromptContract(prompt_name="test")
        errors = validate_prompt_contract(c)
        assert any("prompt_contract_id" in e for e in errors)

    def test_invalid_prompt_type_fails(self):
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="Test", prompt_type="INVALID",
            allowed_roles=["dev"], input_contract_id="ic-001",
            output_contract_id="oc-001",
        )
        errors = validate_prompt_contract(c)
        assert any("prompt_type" in e for e in errors)

    def test_empty_allowed_roles_fails(self):
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="Test", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=[], input_contract_id="ic-001",
            output_contract_id="oc-001",
        )
        errors = validate_prompt_contract(c)
        assert any("allowed_roles" in e for e in errors)


class TestValidatePromptVersion:
    def test_valid_version_passes(self):
        body = "test body"
        v = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0.0",
            prompt_body=body,
            prompt_body_sha256=sha256_text(body),
            change_summary="test",
            status=PROMPT_STATUS_DRAFT,
        )
        errors = validate_prompt_version(v)
        assert errors == []

    def test_missing_version_id_fails(self):
        v = PromptVersion(prompt_body="test", prompt_body_sha256="abc")
        errors = validate_prompt_version(v)
        assert any("prompt_version_id" in e for e in errors)

    def test_empty_prompt_body_fails(self):
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="", prompt_body_sha256="abc",
            change_summary="test",
        )
        errors = validate_prompt_version(v)
        assert any("prompt_body" in e for e in errors)

    def test_hash_mismatch_fails(self):
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="actual body",
            prompt_body_sha256="wrong_hash", change_summary="test",
        )
        errors = validate_prompt_version(v)
        assert any("sha256" in e for e in errors)


class TestValidatePromptRegistry:
    def test_empty_registry_passes(self):
        r = PromptRegistry(registry_id="pr-001")
        errors = validate_prompt_registry(r)
        assert errors == []

    def test_duplicate_contract_id_fails(self):
        c1 = PromptContract(prompt_contract_id="pc-001", prompt_name="a",
                            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
                            allowed_roles=["dev"], input_contract_id="ic-001",
                            output_contract_id="oc-001")
        c2 = PromptContract(prompt_contract_id="pc-001", prompt_name="b",
                            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
                            allowed_roles=["dev"], input_contract_id="ic-001",
                            output_contract_id="oc-001")
        r = PromptRegistry(registry_id="pr-001", contracts=[c1, c2])
        errors = validate_prompt_registry(r)
        assert any("duplicate" in e for e in errors)

    def test_duplicate_version_id_fails(self):
        v1 = PromptVersion(prompt_version_id="pv-001", prompt_contract_id="pc-001",
                           version="1", prompt_body="a", prompt_body_sha256="h1",
                           change_summary="a")
        v2 = PromptVersion(prompt_version_id="pv-001", prompt_contract_id="pc-001",
                           version="2", prompt_body="b", prompt_body_sha256="h2",
                           change_summary="b")
        r = PromptRegistry(registry_id="pr-001", versions=[v1, v2])
        errors = validate_prompt_registry(r)
        assert any("duplicate" in e for e in errors)


class TestValidatePromptInput:
    def test_valid_input_passes(self):
        ic = PromptInputContract(
            input_contract_id="ic-001",
            required_fields=["task"],
            max_input_chars=10000,
        )
        data = {"task": "fix bug"}
        errors = validate_prompt_input(data, ic)
        assert errors == []

    def test_missing_required_field_fails(self):
        ic = PromptInputContract(
            input_contract_id="ic-001",
            required_fields=["task", "context"],
            max_input_chars=10000,
        )
        data = {"task": "fix bug"}
        errors = validate_prompt_input(data, ic)
        assert any("context" in e for e in errors)

    def test_exceeds_max_chars_fails(self):
        ic = PromptInputContract(
            input_contract_id="ic-001",
            required_fields=["task"],
            max_input_chars=10,
        )
        data = {"task": "x" * 20}
        errors = validate_prompt_input(data, ic)
        assert any("max_input_chars" in e for e in errors)


class TestValidatePromptOutput:
    def test_valid_output_passes(self):
        oc = PromptOutputContract(
            output_contract_id="oc-001",
            required_format="json",
            required_fields=["summary"],
        )
        data = {"summary": "done", "extra": "field"}
        errors = validate_prompt_output(data, oc)
        assert errors == []

    def test_missing_required_field_fails(self):
        oc = PromptOutputContract(
            output_contract_id="oc-001",
            required_format="json",
            required_fields=["summary", "files"],
        )
        data = {"summary": "done"}
        errors = validate_prompt_output(data, oc)
        assert any("files" in e for e in errors)

    def test_forbidden_field_present_fails(self):
        oc = PromptOutputContract(
            output_contract_id="oc-001",
            required_format="json",
            required_fields=["summary"],
            forbidden_fields=["secret"],
        )
        data = {"summary": "done", "secret": "leak"}
        errors = validate_prompt_output(data, oc)
        assert any("secret" in e for e in errors)
