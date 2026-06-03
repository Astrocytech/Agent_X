import pytest
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


class TestPromptRegistrySnapshotSchema:
    def test_schema_accepts_valid_snapshot(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_registry_snapshot.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_registry_snapshot.schema.json",
            "snapshot_id": "prs-001",
            "registry_id": "pr-001",
            "registry_version": "1.0",
            "created_at": "2026-06-05T00:00:00",
            "prompt_contract_ids": ["pc-001"],
            "prompt_version_ids": ["pv-001"],
            "active_bindings": {"pc-001": "pv-001"},
            "registry_sha256": "abc123",
        }
        jsonschema.validate(data, schema)

    def test_rejects_missing_sha256(self):
        import jsonschema
        path = os.path.join(SCHEMA_DIR, "prompt_registry_snapshot.schema.json")
        with open(path) as f:
            schema = json.load(f)
        data = {
            "schema_version": "1.0",
            "schema_id": "prompt_registry_snapshot.schema.json",
            "snapshot_id": "prs-002",
            "registry_id": "pr-001",
            "registry_version": "1.0",
            "created_at": "2026-06-05T00:00:00",
            "prompt_contract_ids": [],
            "prompt_version_ids": [],
            "active_bindings": {},
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(data, schema)


class TestRegistrySnapshot:
    def test_snapshot_hash_is_stable(self):
        from agentx_evolve.prompts.prompt_models import (
            PromptRegistry, PromptContract, PromptVersion,
            PROMPT_TYPE_TASK, sha256_text,
        )
        from agentx_evolve.prompts.prompt_registry import (
            create_empty_prompt_registry, register_prompt_contract,
            register_prompt_version, create_registry_snapshot,
        )
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], input_contract_id="ic-001",
            output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        s1 = create_registry_snapshot(r)
        s2 = create_registry_snapshot(r)
        assert s1.registry_sha256 == s2.registry_sha256

    def test_snapshot_includes_all_ids(self):
        from agentx_evolve.prompts.prompt_models import (
            PromptContract, PromptVersion, PROMPT_TYPE_TASK, sha256_text,
        )
        from agentx_evolve.prompts.prompt_registry import (
            create_empty_prompt_registry, register_prompt_contract,
            register_prompt_version, create_registry_snapshot,
        )
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], input_contract_id="ic-001",
            output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="b", prompt_body_sha256=sha256_text("b"),
            change_summary="c",
        )
        from agentx_evolve.prompts.prompt_registry import (
            create_empty_prompt_registry, register_prompt_contract,
            register_prompt_version, create_registry_snapshot,
        )
        r = create_empty_prompt_registry()
        c = PromptContract(
            prompt_contract_id="pc-001", prompt_name="test",
            owner_component="T", prompt_type=PROMPT_TYPE_TASK,
            allowed_roles=["dev"], input_contract_id="ic-001",
            output_contract_id="oc-001",
        )
        r = register_prompt_contract(r, c)
        v = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="b",         prompt_body_sha256=sha256_text("b"),
            change_summary="c",
        )
        r = register_prompt_version(r, v)
        snap = create_registry_snapshot(r)
        assert "pc-001" in snap.prompt_contract_ids
        assert "pv-001" in snap.prompt_version_ids
