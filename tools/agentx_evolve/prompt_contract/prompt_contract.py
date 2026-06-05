from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from agentx_evolve.model.model_models import new_id, to_dict

PC_SCHEMA_VERSION = "1.0"
PC_ACTIVE = "ACTIVE"
PC_DEPRECATED = "DEPRECATED"
PC_RETIRED = "RETIRED"
ALL_PROMPT_CONTRACT_STATUSES = [PC_ACTIVE, PC_DEPRECATED, PC_RETIRED]


@dataclass
class PromptContract:
    schema_version: str = PC_SCHEMA_VERSION
    prompt_id: str = ""
    prompt_version: str = "1.0.0"
    status: str = PC_ACTIVE
    task_type: str = ""
    input_schema: str = ""
    output_schema: str = ""
    allowed_tools: list[str] = field(default_factory=list)
    forbidden_behavior: list[str] = field(default_factory=list)
    model_profiles: list[str] = field(default_factory=list)
    template: str = ""
    test_cases: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


@dataclass
class PromptVersionRecord:
    schema_version: str = PC_SCHEMA_VERSION
    version_id: str = ""
    prompt_id: str = ""
    old_version: str = ""
    new_version: str = ""
    status: str = PC_ACTIVE
    change_description: str = ""
    changed_by: str = ""
    timestamp: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class PromptContractRegistry:
    def __init__(self):
        self._contracts: dict[str, PromptContract] = {}
        self._version_history: dict[str, list[PromptVersionRecord]] = {}

    def register(self, contract: PromptContract) -> None:
        if not contract.prompt_id:
            contract.prompt_id = new_id("pc")
        if not contract.created_at:
            contract.created_at = datetime.now(timezone.utc).isoformat()
        contract.updated_at = datetime.now(timezone.utc).isoformat()
        self._contracts[contract.prompt_id] = contract

    def get(self, prompt_id: str) -> PromptContract | None:
        return self._contracts.get(prompt_id)

    def get_by_task(self, task_type: str) -> list[PromptContract]:
        return [c for c in self._contracts.values() if c.task_type == task_type]

    def list_all(self) -> list[PromptContract]:
        return list(self._contracts.values())

    def update_version(self, prompt_id: str, new_version: str,
                       change_description: str = "", changed_by: str = "") -> PromptVersionRecord | None:
        contract = self._contracts.get(prompt_id)
        if not contract:
            return None
        old_version = contract.prompt_version
        contract.prompt_version = new_version
        contract.updated_at = datetime.now(timezone.utc).isoformat()
        record = PromptVersionRecord(
            version_id=new_id("pvr"),
            prompt_id=prompt_id,
            old_version=old_version,
            new_version=new_version,
            change_description=change_description,
            changed_by=changed_by,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if prompt_id not in self._version_history:
            self._version_history[prompt_id] = []
        self._version_history[prompt_id].append(record)
        return record

    def get_version_history(self, prompt_id: str) -> list[PromptVersionRecord]:
        return list(self._version_history.get(prompt_id, []))

    def deprecate(self, prompt_id: str) -> bool:
        contract = self._contracts.get(prompt_id)
        if not contract:
            return False
        contract.status = PC_DEPRECATED
        contract.updated_at = datetime.now(timezone.utc).isoformat()
        return True

    def retire(self, prompt_id: str) -> bool:
        contract = self._contracts.get(prompt_id)
        if not contract:
            return False
        contract.status = PC_RETIRED
        contract.updated_at = datetime.now(timezone.utc).isoformat()
        return True

    def remove(self, prompt_id: str) -> bool:
        if prompt_id in self._contracts:
            del self._contracts[prompt_id]
            return True
        return False

    def clear(self) -> None:
        self._contracts.clear()
        self._version_history.clear()

    def validate_contract(self, contract: PromptContract) -> list[str]:
        errors = []
        if not contract.prompt_id:
            errors.append("prompt_id is required")
        if not contract.task_type:
            errors.append("task_type is required")
        if not contract.template:
            errors.append("template is required")
        if not contract.output_schema:
            errors.append("output_schema is required")
        if contract.status not in ALL_PROMPT_CONTRACT_STATUSES:
            errors.append(f"invalid status: {contract.status}")
        return errors
