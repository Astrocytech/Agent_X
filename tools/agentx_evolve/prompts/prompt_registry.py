from __future__ import annotations

from pathlib import Path
from agentx_evolve.prompts.prompt_models import (
    PromptRegistry,
    PromptContract,
    PromptVersion,
    PromptRegistrySnapshot,
    PROMPT_STATUS_ACTIVE,
    PROMPT_STATUS_BLOCKED,
    PROMPT_STATUS_RETIRED,
    sha256_dict,
    utc_now_iso,
    new_id,
    to_dict,
)
from agentx_evolve.prompts.prompt_validator import (
    validate_prompt_contract,
    validate_prompt_version,
    validate_prompt_registry,
)


def load_prompt_registry(repo_root: Path) -> PromptRegistry:
    registry = create_empty_prompt_registry()
    contracts_dir = repo_root / ".agentx-init" / "prompts" / "contracts"
    if contracts_dir.exists():
        import json
        for cfile in sorted(contracts_dir.iterdir()):
            if cfile.suffix == ".json":
                data = json.loads(cfile.read_text())
                c = PromptContract(**data)
                registry.contracts.append(c)
    return registry


def create_empty_prompt_registry() -> PromptRegistry:
    return PromptRegistry(
        registry_id=new_id("pr"),
        created_at=utc_now_iso(),
    )


def register_prompt_contract(
    registry: PromptRegistry, contract: PromptContract
) -> PromptRegistry:
    errs = validate_prompt_contract(contract)
    if errs:
        registry.errors.extend(errs)
        return registry
    for existing in registry.contracts:
        if existing.prompt_contract_id == contract.prompt_contract_id:
            registry.errors.append(
                f"duplicate prompt_contract_id: {contract.prompt_contract_id}"
            )
            return registry
    registry.contracts.append(contract)
    registry.registry_sha256 = compute_registry_hash(registry)
    return registry


def register_prompt_version(
    registry: PromptRegistry, version: PromptVersion
) -> PromptRegistry:
    errs = validate_prompt_version(version)
    if errs:
        registry.errors.extend(errs)
        return registry
    contract = None
    for c in registry.contracts:
        if c.prompt_contract_id == version.prompt_contract_id:
            contract = c
            break
    if contract is None:
        registry.errors.append(
            f"contract not found for version: {version.prompt_contract_id}"
        )
        return registry
    for existing in registry.versions:
        if existing.prompt_version_id == version.prompt_version_id:
            registry.errors.append(
                f"duplicate prompt_version_id: {version.prompt_version_id}"
            )
            return registry
    registry.versions.append(version)
    registry.registry_sha256 = compute_registry_hash(registry)
    return registry


def get_prompt_contract(
    registry: PromptRegistry, prompt_contract_id: str
) -> PromptContract | None:
    for c in registry.contracts:
        if c.prompt_contract_id == prompt_contract_id:
            return c
    return None


def get_prompt_version(
    registry: PromptRegistry, prompt_version_id: str
) -> PromptVersion | None:
    for v in registry.versions:
        if v.prompt_version_id == prompt_version_id:
            return v
    return None


def get_active_prompt_version(
    registry: PromptRegistry, prompt_contract_id: str
) -> PromptVersion | None:
    contract = get_prompt_contract(registry, prompt_contract_id)
    if contract is None or not contract.active_version_id:
        return None
    return get_prompt_version(registry, contract.active_version_id)


def set_active_prompt_version(
    registry: PromptRegistry,
    prompt_contract_id: str,
    prompt_version_id: str,
) -> PromptRegistry:
    contract = get_prompt_contract(registry, prompt_contract_id)
    if contract is None:
        registry.errors.append(f"contract not found: {prompt_contract_id}")
        return registry
    version = get_prompt_version(registry, prompt_version_id)
    if version is None:
        registry.errors.append(f"version not found: {prompt_version_id}")
        return registry
    if version.prompt_contract_id != prompt_contract_id:
        registry.errors.append(
            "version does not belong to contract"
        )
        return registry
    if version.status in (PROMPT_STATUS_BLOCKED, PROMPT_STATUS_RETIRED):
        registry.errors.append(
            f"cannot activate version with status: {version.status}"
        )
        return registry
    contract.active_version_id = prompt_version_id
    registry.active_bindings[prompt_contract_id] = prompt_version_id
    registry.registry_sha256 = compute_registry_hash(registry)
    return registry


def compute_registry_hash(registry: PromptRegistry) -> str:
    data = {
        "registry_id": registry.registry_id,
        "registry_version": registry.registry_version,
        "contracts": [
            {"id": c.prompt_contract_id, "name": c.prompt_name, "status": c.status, "active_version_id": c.active_version_id}
            for c in registry.contracts
        ],
        "versions": [
            {"id": v.prompt_version_id, "contract_id": v.prompt_contract_id, "version": v.version, "status": v.status, "sha256": v.prompt_body_sha256}
            for v in registry.versions
        ],
        "active_bindings": dict(registry.active_bindings),
    }
    return sha256_dict(data)


def create_registry_snapshot(registry: PromptRegistry) -> PromptRegistrySnapshot:
    contract_ids = [c.prompt_contract_id for c in registry.contracts]
    version_ids = [v.prompt_version_id for v in registry.versions]
    sha256 = compute_registry_hash(registry)
    return PromptRegistrySnapshot(
        snapshot_id=new_id("prs"),
        registry_id=registry.registry_id,
        registry_version=registry.registry_version,
        created_at=utc_now_iso(),
        prompt_contract_ids=contract_ids,
        prompt_version_ids=version_ids,
        active_bindings=dict(registry.active_bindings),
        registry_sha256=sha256,
    )
