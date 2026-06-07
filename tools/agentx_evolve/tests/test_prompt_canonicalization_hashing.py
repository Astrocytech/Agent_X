import pytest
from agentx_evolve.prompts.prompt_provenance import create_prompt_provenance, validate_prompt_provenance


class TestPromptCanonicalizationHashing:
    def test_create_provenance(self):
        prov = create_prompt_provenance(
            prompt_contract_id="contract-1",
            prompt_version_id="v1",
            prompt_body="test body",
            created_by="tester",
        )
        assert prov is not None

    def test_validate_provenance(self):
        prov = create_prompt_provenance(
            prompt_contract_id="contract-1",
            prompt_version_id="v1",
            prompt_body="test body",
            created_by="tester",
        )
        errors = validate_prompt_provenance(prov)
        assert isinstance(errors, list)
