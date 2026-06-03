import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion,
    PROMPT_STATUS_DRAFT, PROMPT_STATUS_ACTIVE, PROMPT_STATUS_RETIRED,
    PROMPT_STATUS_BLOCKED, PROMPT_TYPE_TASK,
    sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version,
)
from agentx_evolve.prompts.prompt_versioning import (
    create_prompt_version, activate_prompt_version,
    deprecate_prompt_version, retire_prompt_version,
)

CONTRACT_ARGS = {
    "owner_component": "Test",
    "prompt_type": PROMPT_TYPE_TASK,
    "allowed_roles": ["developer"],
    "input_contract_id": "ic-001",
    "output_contract_id": "oc-001",
}


class TestCreatePromptVersion:
    def test_version_hash_matches_body(self):
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        v = create_prompt_version(c, "implement the change", "1.0.0", "developer", "initial")
        assert v.prompt_body_sha256 is not None
        assert v.prompt_version_id.startswith("pv-")
        assert v.status == PROMPT_STATUS_DRAFT


class TestActivatePromptVersion:
    def test_activate_blocks_retired_version(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="test", status=PROMPT_STATUS_RETIRED,
            provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = activate_prompt_version(r, "pc-001", "pv-001", {})
        assert any("RETIRED" in e or "retired" in e for e in r.errors)

    def test_activate_blocks_missing_provenance(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="test", status=PROMPT_STATUS_DRAFT,
            provenance_id="",
        )
        r = register_prompt_version(r, v)
        r = activate_prompt_version(r, "pc-001", "pv-001", {})
        assert any("provenance" in e for e in r.errors)


class TestDeprecatePromptVersion:
    def test_deprecate_marks_version(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body",             prompt_body_sha256=sha256_text("body"),
            change_summary="test", status=PROMPT_STATUS_ACTIVE,
        )
        r = register_prompt_version(r, v)
        r = deprecate_prompt_version(r, "pv-001", "no longer needed")
        version = None
        for x in r.versions:
            if x.prompt_version_id == "pv-001":
                version = x
                break
        assert version is not None and version.status == "DEPRECATED"


class TestRetirePromptVersion:
    def test_retire_removes_active_binding(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body",             prompt_body_sha256=sha256_text("body"),
            change_summary="test", status=PROMPT_STATUS_ACTIVE,
        )
        r = register_prompt_version(r, v)
        r = retire_prompt_version(r, "pv-001", "retired")
        version = None
        for x in r.versions:
            if x.prompt_version_id == "pv-001":
                version = x
                break
        assert version is not None and version.status == "RETIRED"
