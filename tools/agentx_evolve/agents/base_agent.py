from __future__ import annotations


class MvpBaseAgent:
    def __init__(self, agent_id: str, role: str, capabilities: list[str]) -> None:
        self._agent_id = agent_id
        self._role = role
        self._capabilities = capabilities

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def role(self) -> str:
        return self._role

    @property
    def capabilities(self) -> list[str]:
        return self._capabilities

    def can_perform(self, capability: str) -> bool:
        return capability in self._capabilities

    def __repr__(self) -> str:
        return f"MvpBaseAgent(agent_id={self._agent_id!r}, role={self._role!r}, capabilities={self._capabilities!r})"
