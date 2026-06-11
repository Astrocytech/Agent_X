from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpContract:
    contract_id: str = ""
    contract_type: str = ""
    version: str = "1.0.0"
    scope: str = ""
    schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "version": self.version,
            "scope": self.scope,
            "schema": self.schema,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MvpContract:
        return cls(
            contract_id=data.get("contract_id", ""),
            contract_type=data.get("contract_type", ""),
            version=data.get("version", "1.0.0"),
            scope=data.get("scope", ""),
            schema=data.get("schema", {}),
            metadata=data.get("metadata", {}),
        )


class MvpContractRegistry:
    def __init__(self) -> None:
        self._contracts: dict[str, MvpContract] = {}

    def register(self, contract: MvpContract) -> None:
        if contract.contract_id in self._contracts:
            existing = self._contracts[contract.contract_id]
            if existing.version != contract.version:
                raise ValueError(
                    f"Incompatible version for {contract.contract_id}: "
                    f"existing={existing.version}, new={contract.version}"
                )
        self._contracts[contract.contract_id] = contract

    def validate(self, contract: MvpContract) -> list[str]:
        issues = []
        if not contract.contract_id:
            issues.append("contract_id required")
        if not contract.contract_type:
            issues.append("contract_type required")
        if contract.contract_id in self._contracts:
            existing = self._contracts[contract.contract_id]
            if existing.version != contract.version:
                issues.append(
                    f"Version mismatch: existing={existing.version}, provided={contract.version}"
                )
        return issues

    def resolve(self, contract_id: str) -> MvpContract | None:
        return self._contracts.get(contract_id)

    def resolve_required(self, contract_id: str) -> MvpContract:
        c = self.resolve(contract_id)
        if c is None:
            raise KeyError(f"Unknown contract: {contract_id}")
        return c

    def list_by_type(self, contract_type: str) -> list[MvpContract]:
        return [c for c in self._contracts.values() if c.contract_type == contract_type]

    def use_as_evidence(self, contract_id: str) -> dict[str, str] | None:
        c = self.resolve(contract_id)
        if c is None:
            return None
        return {"contract_id": c.contract_id, "version": c.version, "type": c.contract_type}
