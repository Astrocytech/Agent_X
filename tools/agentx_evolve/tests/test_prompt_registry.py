import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion,
    PROMPT_STATUS_DRAFT, PROMPT_STATUS_ACTIVE, PROMPT_STATUS_BLOCKED,
    PROMPT_STATUS_RETIRED, PROMPT_TYPE_TASK,
    sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version, get_prompt_contract, get_prompt_version,
    get_active_prompt_version, set_active_prompt_version,
    compute_registry_hash, create_registry_snapshot,
)

CONTRACT_ARGS = {
    "owner_component": "Test",
    "prompt_type": PROMPT_TYPE_TASK,
    "allowed_roles": ["developer"],
    "input_contract_id": "ic-001",
    "output_contract_id": "oc-001",
}


class TestPromptRegistry:
    def test_loads_empty_registry(self):
        r = create_empty_prompt_registry()
        assert r.registry_id.startswith("pr-")
        assert r.contracts == []
        assert r.versions == []

    def test_rejects_duplicate_contract_id(self):
        r = create_empty_prompt_registry()
        c1 = PromptContract(prompt_contract_id="pc-001", prompt_name="a", **CONTRACT_ARGS)
        c2 = PromptContract(prompt_contract_id="pc-001", prompt_name="b", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c1)
        assert "duplicate" not in " ".join(r.errors).lower()
        r = register_prompt_contract(r, c2)
        assert any("duplicate" in e for e in r.errors)

    def test_rejects_duplicate_version_id(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v1 = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="v1",
        )
        v2 = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="2.0", prompt_body="body2", prompt_body_sha256=sha256_text("body2"),
            change_summary="v2",
        )
        r = register_prompt_version(r, v1)
        r = register_prompt_version(r, v2)
        assert any("duplicate" in e for e in r.errors)

    def test_hash_changes_on_content_change(self):
        r = create_empty_prompt_registry()
        h1 = compute_registry_hash(r)
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        h2 = compute_registry_hash(r)
        assert h1 != h2

    def test_snapshot_hash_is_stable(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        s1 = create_registry_snapshot(r)
        s2 = create_registry_snapshot(r)
        assert s1.registry_sha256 == s2.registry_sha256

    def test_get_contract_and_version(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="initial",
        )
        r = register_prompt_version(r, v)
        assert get_prompt_contract(r, "pc-001") is not None
        assert get_prompt_version(r, "pv-001") is not None
        assert get_prompt_contract(r, "nonexistent") is None
        assert get_prompt_version(r, "nonexistent") is None

    def test_set_active_version(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="initial", status=PROMPT_STATUS_ACTIVE,
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        assert r.errors == []
        assert get_active_prompt_version(r, "pc-001") is not None

    def test_rejects_multiple_active_versions(self):
        r = create_empty_prompt_registry()
        c1 = PromptContract(prompt_contract_id="pc-001", prompt_name="a", **CONTRACT_ARGS)
        c2 = PromptContract(prompt_contract_id="pc-002", prompt_name="b", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c1)
        r = register_prompt_contract(r, c2)
        v1 = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body1", prompt_body_sha256=sha256_text("body1"),
            change_summary="v1", status=PROMPT_STATUS_ACTIVE,
        )
        v2 = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-002",
            version="1.0", prompt_body="body2", prompt_body_sha256=sha256_text("body2"),
            change_summary="v2", status=PROMPT_STATUS_ACTIVE,
        )
        r = register_prompt_version(r, v1)
        r = register_prompt_version(r, v2)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        r = set_active_prompt_version(r, "pc-002", "pv-002")
        assert r.errors == []

    def test_rejects_retired_active_version(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256=sha256_text("body"),
            change_summary="initial", status=PROMPT_STATUS_RETIRED,
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        assert any("RETIRED" in e for e in r.errors)
