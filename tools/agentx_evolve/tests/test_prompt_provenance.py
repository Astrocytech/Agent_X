import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import PromptProvenance, sha256_text
from agentx_evolve.prompts.prompt_provenance import (
    create_prompt_provenance, validate_prompt_provenance,
)


class TestCreatePromptProvenance:
    def test_hash_matches_prompt_body(self):
        body = "This is the prompt body"
        p = create_prompt_provenance(
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            prompt_body=body,
            created_by="developer",
        )
        assert p.prompt_body_sha256 == sha256_text(body)

    def test_creates_with_all_fields(self):
        p = create_prompt_provenance(
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            prompt_body="test",
            created_by="developer",
            source_documents=["spec-v3.md"],
            basis_contracts=["EQC"],
            review_refs=["review-001"],
            approval_refs=["approval-001"],
        )
        assert p.provenance_id.startswith("pp-")
        assert p.source_documents == ["spec-v3.md"]
        assert p.basis_contracts == ["EQC"]

    def test_created_at_is_set(self):
        p = create_prompt_provenance(
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            prompt_body="test",
            created_by="developer",
        )
        assert p.created_at != ""


class TestValidatePromptProvenance:
    def test_valid_provenance_passes(self):
        p = PromptProvenance(
            provenance_id="pp-001",
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            created_by="developer",
            prompt_body_sha256="abc123",
        )
        errors = validate_prompt_provenance(p)
        assert errors == []

    def test_missing_provenance_id_fails(self):
        p = PromptProvenance(
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            created_by="developer",
            prompt_body_sha256="abc",
        )
        errors = validate_prompt_provenance(p)
        assert any("provenance_id" in e for e in errors)

    def test_missing_body_sha256_fails(self):
        p = PromptProvenance(
            provenance_id="pp-001",
            prompt_contract_id="pc-001",
            prompt_version_id="pv-001",
            created_by="developer",
        )
        errors = validate_prompt_provenance(p)
        assert any("prompt_body_sha256" in e for e in errors)
