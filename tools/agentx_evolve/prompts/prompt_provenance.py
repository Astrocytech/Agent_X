from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptProvenance,
    sha256_text,
    utc_now_iso,
    new_id,
)


def create_prompt_provenance(
    prompt_contract_id: str,
    prompt_version_id: str,
    prompt_body: str,
    created_by: str,
    source_documents: list[str] | None = None,
    basis_contracts: list[str] | None = None,
    review_refs: list[str] | None = None,
    approval_refs: list[str] | None = None,
) -> PromptProvenance:
    return PromptProvenance(
        provenance_id=new_id("pp"),
        prompt_contract_id=prompt_contract_id,
        prompt_version_id=prompt_version_id,
        created_at=utc_now_iso(),
        created_by=created_by,
        source_documents=source_documents or [],
        basis_contracts=basis_contracts or [],
        review_refs=review_refs or [],
        approval_refs=approval_refs or [],
        prompt_body_sha256=sha256_text(prompt_body),
    )


def validate_prompt_provenance(provenance: PromptProvenance) -> list[str]:
    errors = []
    if not provenance.provenance_id:
        errors.append("provenance_id is required")
    if not provenance.prompt_contract_id:
        errors.append("prompt_contract_id is required")
    if not provenance.prompt_version_id:
        errors.append("prompt_version_id is required")
    if not provenance.created_by:
        errors.append("created_by is required")
    if not provenance.prompt_body_sha256:
        errors.append("prompt_body_sha256 is required")
    return errors
