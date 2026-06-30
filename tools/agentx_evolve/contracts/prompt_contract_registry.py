from __future__ import annotations

from agentx_evolve.contracts.prompt_contract import PromptContract


class PromptContractRegistry:
    def __init__(self) -> None:
        self._contracts: dict[str, PromptContract] = {}

    def register(self, contract: PromptContract) -> None:
        self._contracts[contract.contract_id] = contract

    def resolve(self, contract_id: str, version: str | None = None) -> PromptContract | None:
        contract = self._contracts.get(contract_id)
        if not contract:
            return None
        if version and contract.version != version:
            return None
        return contract

    def list_contracts(self) -> list[PromptContract]:
        return list(self._contracts.values())


_default_registry = PromptContractRegistry()


def register_contract(contract: PromptContract) -> None:
    _default_registry.register(contract)


def get_contract(contract_id: str) -> PromptContract | None:
    return _default_registry.resolve(contract_id)
