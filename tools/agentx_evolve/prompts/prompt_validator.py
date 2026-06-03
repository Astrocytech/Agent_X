from __future__ import annotations

from agentx_evolve.prompts.prompt_models import (
    PromptContract,
    PromptVersion,
    PromptRegistry,
    PromptInputContract,
    PromptOutputContract,
    PromptRuntimeBinding,
    ALL_PROMPT_STATUSES,
    ALL_PROMPT_TYPES,
    PROMPT_STATUS_ACTIVE,
    PROMPT_STATUS_BLOCKED,
    PROMPT_STATUS_RETIRED,
    PROMPT_TYPE_TOOL_USE,
    PROMPT_TYPE_REPAIR,
    PROMPT_TYPE_TASK,
    sha256_text,
)


def validate_prompt_contract(contract: PromptContract) -> list[str]:
    errors = []
    if not contract.prompt_contract_id:
        errors.append("prompt_contract_id is required")
    if not contract.prompt_name:
        errors.append("prompt_name is required")
    if not contract.owner_component:
        errors.append("owner_component is required")
    if not contract.prompt_type:
        errors.append("prompt_type is required")
    elif contract.prompt_type not in ALL_PROMPT_TYPES:
        errors.append(f"invalid prompt_type: {contract.prompt_type}")
    if not contract.allowed_roles:
        errors.append("allowed_roles cannot be empty")
    if not contract.input_contract_id:
        errors.append("input_contract_id is required")
    if not contract.output_contract_id:
        errors.append("output_contract_id is required")
    if contract.status not in ALL_PROMPT_STATUSES:
        errors.append(f"invalid status: {contract.status}")
    if contract.active_version_id and not any(
        v.prompt_version_id == contract.active_version_id
        for v in getattr(contract, "_versions", [])
    ):
        pass
    return errors


def validate_prompt_version(
    version: PromptVersion, contract: PromptContract | None = None
) -> list[str]:
    errors = []
    if not version.prompt_version_id:
        errors.append("prompt_version_id is required")
    if not version.prompt_contract_id:
        errors.append("prompt_contract_id is required")
    if contract and version.prompt_contract_id != contract.prompt_contract_id:
        errors.append("version prompt_contract_id does not match contract")
    if not version.version:
        errors.append("version string is required")
    if not version.prompt_body:
        errors.append("prompt_body cannot be empty")
    if version.prompt_body_sha256:
        expected = sha256_text(version.prompt_body)
        if version.prompt_body_sha256 != expected:
            errors.append("prompt_body_sha256 does not match prompt_body")
    elif version.prompt_body:
        errors.append("prompt_body_sha256 is required when prompt_body is set")
    if version.status not in ALL_PROMPT_STATUSES:
        errors.append(f"invalid status: {version.status}")
    return errors


def validate_prompt_registry(registry: PromptRegistry) -> list[str]:
    errors = []
    if not registry.registry_id:
        errors.append("registry_id is required")
    contract_ids = set()
    version_ids = set()
    active_versions: dict[str, str] = {}
    for c in registry.contracts:
        if c.prompt_contract_id in contract_ids:
            errors.append(
                f"duplicate contract_id: {c.prompt_contract_id}"
            )
        contract_ids.add(c.prompt_contract_id)
        if c.active_version_id:
            if c.prompt_contract_id in active_versions:
                errors.append(
                    f"multiple active versions for contract: {c.prompt_contract_id}"
                )
            active_versions[c.prompt_contract_id] = c.active_version_id
    for v in registry.versions:
        if v.prompt_version_id in version_ids:
            errors.append(f"duplicate version_id: {v.prompt_version_id}")
        version_ids.add(v.prompt_version_id)
        if v.status in (PROMPT_STATUS_BLOCKED, PROMPT_STATUS_RETIRED):
            for c in registry.contracts:
                if c.active_version_id == v.prompt_version_id:
                    errors.append(
                        f"active version {v.prompt_version_id} is {v.status}"
                    )
    for c in registry.contracts:
        if c.active_version_id:
            found = any(
                v.prompt_version_id == c.active_version_id
                and v.prompt_contract_id == c.prompt_contract_id
                for v in registry.versions
            )
            if not found:
                errors.append(
                    f"active version {c.active_version_id} not found for contract {c.prompt_contract_id}"
                )
    return errors


def validate_prompt_input(
    input_data: dict, input_contract: PromptInputContract
) -> list[str]:
    errors = []
    for field in input_contract.required_fields:
        if field not in input_data:
            errors.append(f"missing required input field: {field}")
    total_chars = sum(len(str(v)) for v in input_data.values())
    if input_contract.max_input_chars > 0 and total_chars > input_contract.max_input_chars:
        errors.append(
            f"input exceeds max_input_chars: {total_chars} > {input_contract.max_input_chars}"
        )
    return errors


def validate_prompt_output(
    output_data: dict | str, output_contract: PromptOutputContract
) -> list[str]:
    errors = []
    if isinstance(output_data, dict):
        for field in output_contract.required_fields:
            if field not in output_data:
                errors.append(f"missing required output field: {field}")
        for field in output_contract.forbidden_fields:
            if field in output_data:
                errors.append(f"forbidden output field present: {field}")
        if output_contract.requires_json:
            pass
    if output_contract.max_output_chars > 0:
        size = len(str(output_data))
        if size > output_contract.max_output_chars:
            errors.append(
                f"output exceeds max_output_chars: {size} > {output_contract.max_output_chars}"
            )
    return errors


def validate_runtime_binding(
    binding: PromptRuntimeBinding, registry: PromptRegistry
) -> list[str]:
    errors = []
    if not binding.prompt_contract_id:
        errors.append("prompt_contract_id is required")
    if not binding.prompt_version_id:
        errors.append("prompt_version_id is required")
    if not binding.bound_by_component:
        errors.append("bound_by_component is required")
    if not binding.caller_role:
        errors.append("caller_role is required")
    if not binding.task_type:
        errors.append("task_type is required")
    contract = None
    for c in registry.contracts:
        if c.prompt_contract_id == binding.prompt_contract_id:
            contract = c
            break
    if contract is None:
        errors.append(
            f"contract not found: {binding.prompt_contract_id}"
        )
    version = None
    for v in registry.versions:
        if v.prompt_version_id == binding.prompt_version_id:
            version = v
            break
    if version is None:
        errors.append(f"version not found: {binding.prompt_version_id}")
    if contract and version:
        if version.prompt_contract_id != contract.prompt_contract_id:
            errors.append("version does not belong to contract")
    if binding.prompt_body_sha256 and version:
        if version.prompt_body_sha256 != binding.prompt_body_sha256:
            errors.append("binding prompt_body_sha256 does not match version")
    return errors
