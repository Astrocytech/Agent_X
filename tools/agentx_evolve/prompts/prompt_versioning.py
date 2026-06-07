from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptRegistry,
    PromptContract,
    PromptVersion,
    PromptAuditEvent,
    PROMPT_STATUS_DRAFT,
    PROMPT_STATUS_ACTIVE,
    PROMPT_STATUS_DEPRECATED,
    PROMPT_STATUS_RETIRED,
    PROMPT_STATUS_BLOCKED,
    P_PROMPT_EVENT_TYPE_VERSION_CREATED,
    P_PROMPT_EVENT_TYPE_VERSION_ACTIVATED,
    P_PROMPT_EVENT_TYPE_VERSION_DEPRECATED,
    P_PROMPT_EVENT_TYPE_VERSION_RETIRED,
    P_PROMPT_EVENT_TYPE_ACTIVATION_FAILED,
    sha256_text,
    utc_now_iso,
    new_id,
)
from agentx_evolve.prompts.prompt_compatibility import (
    check_prompt_compatibility,
    requires_migration,
)
from agentx_evolve.prompts.prompt_registry import (
    get_prompt_contract,
    get_prompt_version,
    set_active_prompt_version,
)


def create_prompt_version(
    contract: PromptContract,
    prompt_body: str,
    version: str,
    created_by: str,
    change_summary: str,
    supersedes_version_id: str | None = None,
) -> PromptVersion:
    prompt_body_sha256 = sha256_text(prompt_body)
    return PromptVersion(
        prompt_version_id=new_id("pv"),
        prompt_contract_id=contract.prompt_contract_id,
        version=version,
        created_at=utc_now_iso(),
        created_by=created_by,
        status=PROMPT_STATUS_DRAFT,
        prompt_body=prompt_body,
        prompt_body_sha256=prompt_body_sha256,
        change_summary=change_summary,
        supersedes_version_id=supersedes_version_id,
    )


def activate_prompt_version(
    registry: PromptRegistry,
    prompt_contract_id: str,
    prompt_version_id: str,
    approval_context: dict,
) -> PromptRegistry:
    contract = get_prompt_contract(registry, prompt_contract_id)
    if contract is None:
        registry.errors.append(f"contract not found: {prompt_contract_id}")
        _record_activation_failure(registry, prompt_contract_id, prompt_version_id, "contract not found")
        return registry
    version = get_prompt_version(registry, prompt_version_id)
    if version is None:
        registry.errors.append(f"version not found: {prompt_version_id}")
        _record_activation_failure(registry, prompt_contract_id, prompt_version_id, "version not found")
        return registry
    if version.prompt_contract_id != prompt_contract_id:
        registry.errors.append("version does not belong to contract")
        _record_activation_failure(registry, prompt_contract_id, prompt_version_id, "version contract mismatch")
        return registry
    if version.status in (PROMPT_STATUS_RETIRED, PROMPT_STATUS_BLOCKED):
        registry.errors.append(f"cannot activate {version.status} version")
        _record_activation_failure(registry, prompt_contract_id, prompt_version_id, f"version is {version.status}")
        return registry
    if not version.provenance_id:
        registry.errors.append("cannot activate version without provenance")
        _record_activation_failure(registry, prompt_contract_id, prompt_version_id, "missing provenance")
        return registry
    old_active = None
    for v in registry.versions:
        if (
            v.prompt_contract_id == prompt_contract_id
            and v.status == PROMPT_STATUS_ACTIVE
        ):
            old_active = v
            break
    if old_active:
        diff = check_prompt_compatibility(old_active, version, contract)
        if requires_migration(diff) and not version.migration_id:
            registry.errors.append(
                "breaking change requires migration before activation"
            )
            _record_activation_failure(
                registry, prompt_contract_id, prompt_version_id,
                "breaking change without migration"
            )
            return registry
    version.status = PROMPT_STATUS_ACTIVE
    result = set_active_prompt_version(registry, prompt_contract_id, prompt_version_id)
    if result.errors:
        return result
    if old_active:
        old_active.status = PROMPT_STATUS_DEPRECATED
    return registry


def _record_activation_failure(
    registry: PromptRegistry,
    contract_id: str,
    version_id: str,
    reason: str,
) -> None:
    import logging
    logging.getLogger(__name__).warning(
        "Prompt activation failed: contract=%s version=%s reason=%s",
        contract_id, version_id, reason,
    )


def deprecate_prompt_version(
    registry: PromptRegistry,
    prompt_version_id: str,
    reason: str,
) -> PromptRegistry:
    version = get_prompt_version(registry, prompt_version_id)
    if version is None:
        registry.errors.append(f"version not found: {prompt_version_id}")
        return registry
    version.status = PROMPT_STATUS_DEPRECATED
    for c in registry.contracts:
        if c.active_version_id == prompt_version_id:
            c.active_version_id = None
    registry.registry_sha256 = None
    return registry


def retire_prompt_version(
    registry: PromptRegistry,
    prompt_version_id: str,
    reason: str,
) -> PromptRegistry:
    version = get_prompt_version(registry, prompt_version_id)
    if version is None:
        registry.errors.append(f"version not found: {prompt_version_id}")
        return registry
    version.status = PROMPT_STATUS_RETIRED
    for c in registry.contracts:
        if c.active_version_id == prompt_version_id:
            c.active_version_id = None
            if prompt_version_id in registry.active_bindings:
                del registry.active_bindings[
                    c.prompt_contract_id
                ]
    registry.registry_sha256 = None
    return registry
