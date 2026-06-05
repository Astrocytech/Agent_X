import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry, PromptContract, PromptVersion,
    PROMPT_STATUS_ACTIVE, PROMPT_STATUS_DRAFT, PROMPT_TYPE_TASK,
    sha256_text,
)
from agentx_evolve.prompts.prompt_registry import (
    create_empty_prompt_registry, register_prompt_contract,
    register_prompt_version, set_active_prompt_version,
    compute_registry_hash,
)
from agentx_evolve.prompts.prompt_diff import create_prompt_diff, hash_prompt_diff

CONTRACT_ARGS = {
    "owner_component": "T",
    "prompt_type": PROMPT_TYPE_TASK,
    "allowed_roles": ["dev"],
    "input_contract_id": "ic-001",
    "output_contract_id": "oc-001",
}


class TestLockingIdempotency:
    def test_duplicate_registration_blocked(self):
        r = create_empty_prompt_registry()
        c1 = PromptContract(prompt_contract_id="pc-001", prompt_name="a", **CONTRACT_ARGS)
        c2 = PromptContract(prompt_contract_id="pc-001", prompt_name="b", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c1)
        assert "duplicate" not in " ".join(r.errors).lower()
        r = register_prompt_contract(r, c2)
        assert any("duplicate" in e for e in r.errors)

    def test_repeated_validation_stable(self):
        from agentx_evolve.prompts.prompt_validator import validate_prompt_contract
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        e1 = validate_prompt_contract(c)
        e2 = validate_prompt_contract(c)
        assert e1 == e2

    def test_repeated_binding_same_hash(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body",
            prompt_body_sha256=sha256_text("body"),
            change_summary="init", status=PROMPT_STATUS_ACTIVE,
            provenance_id="pp-001",
        )
        r = register_prompt_version(r, v)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        from agentx_evolve.prompts.prompt_runtime_binding import bind_prompt_for_runtime
        b1 = bind_prompt_for_runtime(r, "pc-001", "dev", "TASK", None, None, [], {})
        b2 = bind_prompt_for_runtime(r, "pc-001", "dev", "TASK", None, None, [], {})
        assert b1.registry_snapshot_sha256 == b2.registry_snapshot_sha256
        assert b1.prompt_body_sha256 == b2.prompt_body_sha256

    def test_active_version_lock(self):
        r = create_empty_prompt_registry()
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test", **CONTRACT_ARGS)
        r = register_prompt_contract(r, c)
        v1 = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body1",
            prompt_body_sha256=sha256_text("body1"),
            change_summary="v1", status=PROMPT_STATUS_ACTIVE,
            provenance_id="pp-001",
        )
        v2 = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="2.0", prompt_body="body2",
            prompt_body_sha256=sha256_text("body2"),
            change_summary="v2", status=PROMPT_STATUS_ACTIVE,
            provenance_id="pp-002",
        )
        r = register_prompt_version(r, v1)
        r = register_prompt_version(r, v2)
        r = set_active_prompt_version(r, "pc-001", "pv-001")
        active = None
        for x in r.versions:
            if x.status == PROMPT_STATUS_ACTIVE and x.prompt_contract_id == "pc-001":
                active = x
                break
        assert active is not None

    def test_same_body_same_sha256(self):
        h1 = sha256_text("same prompt body")
        h2 = sha256_text("same prompt body")
        assert h1 == h2

    def test_same_diff_same_hash(self):
        old = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="old",
            prompt_body_sha256="abc", change_summary="old",
        )
        new = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="2.0", prompt_body="new",
            prompt_body_sha256="def", change_summary="new",
        )
        d1 = create_prompt_diff(old, new)
        d2 = create_prompt_diff(old, new)
        assert hash_prompt_diff(d1) == hash_prompt_diff(d2)
